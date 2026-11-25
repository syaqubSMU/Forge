"""Run log plus admin settings, audit trail, rubric versions and the stored public Grants.gov copy (`opportunities`, `api_calls`; customer-approved for the demo, see docs/ARCHITECTURE.md DR-1). No faculty or researcher-profile tables (hard rule 1)."""
import json, sqlite3, threading, uuid
from .migrations import MIGRATIONS
from datetime import datetime, timedelta, timezone


# Pilot-safe defaults for a hosted service (budget: $20 for the whole pilot; a 15-judgment run costs about $0.44).
# The earlier defaults (200 runs a day, 20 an hour per visitor, 25 judgments) could spend about $88 in a day if a
# public link were shared. The provider's spending limit remains the real guard; these only lower the risk.
PILOT_DEFAULTS = {"daily_cap": 3, "rate_limit_per_hour": 3, "max_judgments": 15}

DEFAULT_SETTINGS = {
    "scope_level": "A named organization", "units": [], "funder_types": ["federal"],
    "horizon_months": 3, "lead_time_days": 14, "min_fit": "Low", "faculty_per_run": 25,
    "max_detail_fetches": 250, "max_judgments": PILOT_DEFAULTS["max_judgments"], "judge_concurrency": 8, "judge_deadline_s": 90, "source_timeout_s": 30, "source_concurrency": 8,
    "cache_ttl_minutes": 15, "include_undated_deadlines": False,
    "price_per_mtok_input": 0.0, "price_per_mtok_output": 0.0, "pilot_budget_usd": 11.0,
    "rate_limit_per_hour": PILOT_DEFAULTS["rate_limit_per_hour"], "pi_lookups_per_hour": 60, "pi_lookups_per_day": 1000, "daily_cap": PILOT_DEFAULTS["daily_cap"], "retention_days": 90,
    "email_mode": "dummy", "test_mailbox": "", "sender_label": "Forge Signal (pilot)", "active_model": "mock",
}
NOTICE = ("Runs, inputs and calendars are logged for the pilot report, kept for 90 days, then archived. "
          "Only the administrator can see them. Do not enter restricted data.")


def run_cost(settings, input_tokens, output_tokens):
    """Tokens times the prices set in settings (USD per million tokens). None unless BOTH prices are set, so a
    missing price is never shown as a cost of zero."""
    pi, po = settings.get("price_per_mtok_input") or 0, settings.get("price_per_mtok_output") or 0
    if not pi or not po:                  # one price alone would silently understate the cost
        return None
    return round((input_tokens or 0) / 1e6 * pi + (output_tokens or 0) / 1e6 * po, 6)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def is_postgres(target) -> bool:
    return str(target).startswith(("postgres://", "postgresql://"))


def _clean(v):
    """Postgres text cannot hold NUL characters; SQLite can. Strip them so a stray byte never fails a run."""
    return v.replace("\x00", "") if isinstance(v, str) else v


class Database:
    def __init__(self, path=":memory:"):
        self.pg = is_postgres(path)
        self.target = path
        self.lock = threading.Lock()
        self._connect()
        with self.lock:
            self.migrate()

    # schema versions ------------------------------------------------------
    def schema_version(self) -> int:
        with self.lock:
            try:
                rows = self.conn.execute("SELECT MAX(version) v FROM schema_migrations").fetchall()
            except Exception:
                if self.pg: self.conn.rollback()
                return 0
            if self.pg: self.conn.commit()
            return int((rows[0]["v"] if rows else 0) or 0)

    def migrate(self, target=None) -> list:
        """Apply pending migrations in order, each in its own transaction. Returns the versions applied.
        Caller holds self.lock. On Postgres an advisory lock keeps two starting servers from racing."""
        pk = "BIGSERIAL PRIMARY KEY" if self.pg else "INTEGER PRIMARY KEY"
        applied = []
        if self.pg:
            self.conn.execute("SELECT pg_advisory_lock(727274)")
        try:
            self.conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY, name TEXT, applied_at TEXT)")
            self.conn.commit()
            done = {r["version"] for r in self.conn.execute("SELECT version FROM schema_migrations").fetchall()}
            for version, name, stmts in MIGRATIONS:
                if version in done or (target is not None and version > target):
                    continue
                try:
                    if not self.pg: self.conn.execute("BEGIN")
                    for st in stmts:
                        self.conn.execute(st.replace("{PK}", pk))
                    self.conn.execute(self._ins(), (version, name, now()))
                    self.conn.commit()
                except Exception:
                    self.conn.rollback()
                    raise
                applied.append(version)
        finally:
            if self.pg:
                self.conn.execute("SELECT pg_advisory_unlock(727274)"); self.conn.commit()
        return applied

    def _ins(self):
        return "INSERT INTO schema_migrations(version,name,applied_at) VALUES(" + ("%s,%s,%s" if self.pg else "?,?,?") + ")"

    def _connect(self):
        if self.pg:
            import psycopg                                   # imported lazily: SQLite users do not need it
            from psycopg.rows import dict_row
            self._psycopg = psycopg
            self.conn = psycopg.connect(self.target, row_factory=dict_row, connect_timeout=15)
        else:
            self.conn = sqlite3.connect(self.target, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row

    def _run(self, sql, args):
        if self.pg:
            return self.conn.execute(sql.replace("?", "%s"), tuple(_clean(a) for a in args))
        return self.conn.execute(sql, args)

    def q(self, sql, args=(), one=False, write=False):
        with self.lock:
            for attempt in (1, 2):
                try:
                    cur = self._run(sql, args)
                    if write:
                        self.conn.commit()
                        return None if self.pg else cur.lastrowid
                    rows = cur.fetchall()
                    if self.pg: self.conn.commit()           # end the read transaction
                    break
                except Exception as e:
                    if not self.pg: raise
                    try: self.conn.rollback()
                    except Exception: pass
                    # An idle serverless Postgres drops connections; reconnect once, then give up.
                    if attempt == 1 and isinstance(e, self._psycopg.OperationalError):
                        self._connect(); continue
                    raise
        return (rows[0] if rows else None) if one else rows

    # settings -------------------------------------------------------------
    def settings(self) -> dict:
        s = dict(DEFAULT_SETTINGS)
        for r in self.q("SELECT key,value FROM settings"):
            s[r["key"]] = json.loads(r["value"])
        return s

    def set_setting(self, key, value):
        self.q("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, json.dumps(value)), write=True)

    def audit(self, actor, action, detail):
        self.q("INSERT INTO admin_audit(at,actor,action,detail) VALUES(?,?,?,?)", (now(), actor, action, json.dumps(detail)), write=True)

    # runs -----------------------------------------------------------------
    def create_run(self, visitor_hash, input_type, input_text, settings, rubric_version, model) -> str:
        rid = uuid.uuid4().hex                      # 32 hex characters; runs created before this change keep their 12-character ids
        scope = {k: settings[k] for k in ("scope_level", "units", "funder_types")}
        self.q("INSERT INTO runs(id,created_at,visitor_hash,input_type,input_text,scope_snapshot,settings_snapshot,rubric_version,model,status) VALUES(?,?,?,?,?,?,?,?,?,?)",
               (rid, now(), visitor_hash, input_type, input_text, json.dumps(scope), json.dumps(settings), rubric_version, model, "running"), write=True)
        return rid

    def finish_run(self, rid, status, latency_ms, error=None, input_tokens=0, output_tokens=0,
                   opportunities_listed=0, details_fetched=0, cost_usd=None):
        self.q("UPDATE runs SET status=?, latency_ms=?, error=?, input_tokens=?, output_tokens=?,"
               " opportunities_listed=?, details_fetched=?, cost_usd=? WHERE id=?",
               (status, latency_ms, error, input_tokens, output_tokens, opportunities_listed, details_fetched, cost_usd, rid), write=True)

    def add_source_failure(self, rid, source_id, error):
        self.q("INSERT INTO run_source_failures(run_id,source_id,error) VALUES(?,?,?)", (rid, source_id, str(error)[:300]), write=True)

    def add_source(self, rid, source_id, url, text_hash):
        self.q("INSERT INTO run_sources(run_id,source_id,url,retrieved_at,text_hash) VALUES(?,?,?,?,?)", (rid, source_id, url, now(), text_hash), write=True)

    def add_match(self, rid, data: dict):
        self.q("INSERT INTO run_matches(run_id,data) VALUES(?,?)", (rid, json.dumps(data)), write=True)

    def add_citation(self, rid, source_id, quote, validated, reason=""):
        self.q("INSERT INTO run_citations(run_id,source_id,quote,validated,reason) VALUES(?,?,?,?,?)", (rid, source_id, quote, int(validated), reason), write=True)

    def add_email(self, rid, draft, recipient, confirmed, mode):
        self.q("INSERT INTO email_events(run_id,draft,recipient,confirmed,mode,created_at) VALUES(?,?,?,?,?,?)", (rid, draft, recipient, int(confirmed), mode, now()), write=True)

    def add_annotation(self, rid, label, note):
        self.q("INSERT INTO annotations(run_id,label,note,created_at) VALUES(?,?,?,?)", (rid, label, note, now()), write=True)

    def get_run(self, rid):
        r = self.q("SELECT * FROM runs WHERE id=?", (rid,), one=True)
        if r is None: return None
        out = dict(r)
        for k in ("scope_snapshot", "settings_snapshot"): out[k] = json.loads(out[k])
        out["sources"] = [dict(x) for x in self.q("SELECT source_id,url,retrieved_at,text_hash FROM run_sources WHERE run_id=?", (rid,))]
        out["matches"] = [json.loads(x["data"]) for x in self.q("SELECT data FROM run_matches WHERE run_id=?", (rid,))]
        out["citations"] = [dict(x) for x in self.q("SELECT source_id,quote,validated,reason FROM run_citations WHERE run_id=?", (rid,))]
        out["emails"] = [dict(x) for x in self.q("SELECT draft,recipient,confirmed,mode,created_at FROM email_events WHERE run_id=?", (rid,))]
        out["annotations"] = [dict(x) for x in self.q("SELECT label,note,created_at FROM annotations WHERE run_id=?", (rid,))]
        out["source_failures"] = [dict(x) for x in self.q("SELECT source_id,error FROM run_source_failures WHERE run_id=?", (rid,))]
        return out

    def list_runs(self, limit=50, offset=0, q=None, include_archived=False):
        sql, args = ("SELECT id,created_at,input_type,input_text,model,status,latency_ms,rubric_version,archived,"
                     "input_tokens,output_tokens,opportunities_listed,details_fetched,cost_usd FROM runs WHERE 1=1"), []
        if not include_archived: sql += " AND archived=0"
        if q: sql += " AND LOWER(input_text) LIKE LOWER(?)"; args.append(f"%{q}%")
        sql += " ORDER BY created_at DESC, id LIMIT ? OFFSET ?"; args += [limit, offset]
        return [dict(r) for r in self.q(sql, args)]

    def count_runs_since(self, visitor_hash, since_iso):
        sql, args = "SELECT COUNT(*) c FROM runs WHERE created_at>=?", [since_iso]
        if visitor_hash: sql += " AND visitor_hash=?"; args.append(visitor_hash)
        return self.q(sql, args, one=True)["c"]

    def spent_usd(self) -> float:
        """Sum of the recorded cost estimates of all runs. Read from the database, so it survives restarts. Spend made
        outside this database (engineering tests, other databases) and failed or abandoned calls are not in it."""
        return float(self.q("SELECT COALESCE(SUM(cost_usd), 0) t FROM runs", one=True)["t"] or 0)

    def archive_older_than(self, days) -> int:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat(timespec="seconds")
        n = self.q("SELECT COUNT(*) c FROM runs WHERE created_at<? AND archived=0", (cutoff,), one=True)["c"]
        self.q("UPDATE runs SET archived=1 WHERE created_at<? AND archived=0", (cutoff,), write=True)
        return n

    # rubric versions ------------------------------------------------------
    def published_rubric(self):
        r = self.q("SELECT body FROM rubric_versions WHERE status='published' ORDER BY published_at DESC LIMIT 1", one=True)
        return json.loads(r["body"]) if r else None

    def publish_rubric(self, version, body: dict, note=""):
        self.q("UPDATE rubric_versions SET status='archived' WHERE status='published'", write=True)
        self.q("INSERT INTO rubric_versions(version,body,status,created_at,published_at,note) VALUES(?,?,?,?,?,?)"
               " ON CONFLICT(version) DO UPDATE SET body=excluded.body, status=excluded.status,"
               " created_at=excluded.created_at, published_at=excluded.published_at, note=excluded.note",
               (version, json.dumps(body), "published", now(), now(), note), write=True)

    def rubric_versions(self):
        return [dict(r) for r in self.q("SELECT version,status,created_at,published_at,note FROM rubric_versions ORDER BY created_at DESC")]
