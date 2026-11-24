"""Run log (the only database, PRD section 6) plus admin settings, audit trail and rubric versions.
SQLite for the pilot; the same schema ports to Postgres. No opportunity, faculty or profile tables (hard rule 1)."""
import json, sqlite3, threading, uuid
from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, created_at TEXT, visitor_hash TEXT, input_type TEXT, input_text TEXT,
  scope_snapshot TEXT, settings_snapshot TEXT, rubric_version TEXT, model TEXT, latency_ms INTEGER, status TEXT, error TEXT, archived INTEGER DEFAULT 0,
  input_tokens INTEGER DEFAULT 0, output_tokens INTEGER DEFAULT 0, opportunities_listed INTEGER DEFAULT 0, details_fetched INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS run_source_failures(id INTEGER PRIMARY KEY, run_id TEXT, source_id TEXT, error TEXT);
CREATE TABLE IF NOT EXISTS run_sources(id INTEGER PRIMARY KEY, run_id TEXT, source_id TEXT, url TEXT, retrieved_at TEXT, text_hash TEXT);
CREATE TABLE IF NOT EXISTS run_matches(id INTEGER PRIMARY KEY, run_id TEXT, data TEXT);
CREATE TABLE IF NOT EXISTS run_citations(id INTEGER PRIMARY KEY, run_id TEXT, source_id TEXT, quote TEXT, validated INTEGER, reason TEXT);
CREATE TABLE IF NOT EXISTS email_events(id INTEGER PRIMARY KEY, run_id TEXT, draft TEXT, recipient TEXT, confirmed INTEGER, mode TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS chat_entries(id INTEGER PRIMARY KEY, run_id TEXT, role TEXT, text TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS annotations(id INTEGER PRIMARY KEY, run_id TEXT, label TEXT, note TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS admin_audit(id INTEGER PRIMARY KEY, at TEXT, actor TEXT, action TEXT, detail TEXT);
CREATE TABLE IF NOT EXISTS rubric_versions(version TEXT PRIMARY KEY, body TEXT, status TEXT, created_at TEXT, published_at TEXT, note TEXT);
CREATE INDEX IF NOT EXISTS ix_runs_visitor ON runs(visitor_hash, created_at);
"""

DEFAULT_SETTINGS = {
    "scope_level": "Dedman College", "units": [], "funder_types": ["federal"],
    "horizon_months": 3, "lead_time_days": 14, "min_fit": "Low", "faculty_per_run": 25,
    "max_detail_fetches": 250, "max_judgments": 25, "source_timeout_s": 30, "source_concurrency": 8,
    "cache_ttl_minutes": 15, "include_undated_deadlines": False,
    "price_per_mtok_input": 0.0, "price_per_mtok_output": 0.0,
    "rate_limit_per_hour": 20, "daily_cap": 200, "retention_days": 90,
    "email_mode": "dummy", "test_mailbox": "", "sender_label": "Forge Signal (pilot)", "active_model": "mock",
}
NOTICE = ("Runs, inputs and calendars are logged for the pilot report, kept for 90 days, then archived. "
          "Only the administrator can see them. Do not enter restricted data.")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        with self.lock:
            self.conn.executescript(SCHEMA); self.conn.commit()

    def q(self, sql, args=(), one=False, write=False):
        with self.lock:
            cur = self.conn.execute(sql, args)
            if write: self.conn.commit(); return cur.lastrowid
            rows = cur.fetchall()
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
        rid = uuid.uuid4().hex[:12]
        scope = {k: settings[k] for k in ("scope_level", "units", "funder_types")}
        self.q("INSERT INTO runs(id,created_at,visitor_hash,input_type,input_text,scope_snapshot,settings_snapshot,rubric_version,model,status) VALUES(?,?,?,?,?,?,?,?,?,?)",
               (rid, now(), visitor_hash, input_type, input_text, json.dumps(scope), json.dumps(settings), rubric_version, model, "running"), write=True)
        return rid

    def finish_run(self, rid, status, latency_ms, error=None, input_tokens=0, output_tokens=0,
                   opportunities_listed=0, details_fetched=0):
        self.q("UPDATE runs SET status=?, latency_ms=?, error=?, input_tokens=?, output_tokens=?,"
               " opportunities_listed=?, details_fetched=? WHERE id=?",
               (status, latency_ms, error, input_tokens, output_tokens, opportunities_listed, details_fetched, rid), write=True)

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
                     "input_tokens,output_tokens,opportunities_listed,details_fetched FROM runs WHERE 1=1"), []
        if not include_archived: sql += " AND archived=0"
        if q: sql += " AND input_text LIKE ?"; args.append(f"%{q}%")
        sql += " ORDER BY created_at DESC, id LIMIT ? OFFSET ?"; args += [limit, offset]
        return [dict(r) for r in self.q(sql, args)]

    def count_runs_since(self, visitor_hash, since_iso):
        sql, args = "SELECT COUNT(*) c FROM runs WHERE created_at>=?", [since_iso]
        if visitor_hash: sql += " AND visitor_hash=?"; args.append(visitor_hash)
        return self.q(sql, args, one=True)["c"]

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
        self.q("INSERT OR REPLACE INTO rubric_versions(version,body,status,created_at,published_at,note) VALUES(?,?,?,?,?,?)",
               (version, json.dumps(body), "published", now(), now(), note), write=True)

    def rubric_versions(self):
        return [dict(r) for r in self.q("SELECT version,status,created_at,published_at,note FROM rubric_versions ORDER BY created_at DESC")]
