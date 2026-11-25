"""FORGE SIGNAL API skeleton: public run endpoint, dummy email, admin dashboard API, run log.
Hard rules enforced here: keys only from the server environment and never returned; human confirmation
before any email; per-visitor rate limit and daily cap; no raw source text returned to the public."""
import contextlib, csv, hashlib, json, hmac, io, os, pathlib, re, tempfile, threading, time
from datetime import date, datetime, timedelta, timezone

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator

from . import rubric as R
from . import access
from . import store
from .adapters.registry import available, get_adapter
from .db import DEFAULT_SETTINGS, NOTICE, Database, now, run_cost
from .fit import DEFAULT_RUBRIC
from .calendar import build_calendar
from .exports import to_ics, to_xlsx
from .adapters.claude import KEY_VARS
from .pipeline import run_match, MODEL_MAX_CONCURRENT
from .schemas import FIT, SchemaError
from .sources.grants_gov import SourceError
from .sources import openalex
from .template_xlsx import preview
from .validator import validate

MAX_SOURCES, MAX_SOURCE_CHARS = 3, 20000        # pasted evidence goes straight to the model: bound the cost of one request
MAX_BODY_BYTES = int(os.environ.get("FORGE_MAX_BODY_BYTES", "400000"))   # public POST bodies; admin uploads are exempt
MIN_HOSTED_ADMIN_TOKEN = 32                      # on a hosted (Postgres) database a shorter ADMIN_TOKEN disables the admin API
INPUT_TYPES = ("pi_name", "project", "keywords", "opportunity_unit")


class Profile(BaseModel):
    """Researcher evidence for ONE run. Never stored outside that run's log (hard rule 1)."""
    career_stage: str = Field(default="", max_length=200)
    lanes: list[Annotated[str, StringConstraints(max_length=300)]] = Field(default_factory=list, max_length=40)
    positioning_rules: list[Annotated[str, StringConstraints(max_length=600)]] = Field(default_factory=list, max_length=20)


class RunIn(BaseModel):
    input_type: str
    input_text: str = Field(min_length=1, max_length=4000)
    question: str = Field(default="Does this researcher fit this opportunity, and is the researcher's institution eligible?", max_length=1000)
    profile: Profile = Field(default_factory=Profile)
    sources: dict[str, str] = {}      # pasted evidence; omit it to pull live from Grants.gov (FR-5)
    options: dict = Field(default_factory=dict)   # per-run overrides: horizon_months, lead_time_days (never saved as settings)

    @field_validator("sources")
    @classmethod
    def _sources_bounded(cls, v):
        if len(v) > MAX_SOURCES: raise ValueError(f"at most {MAX_SOURCES} pasted sources")
        for k, t in v.items():
            if len(k) > 500 or len(t) > MAX_SOURCE_CHARS: raise ValueError(f"each pasted source must be at most {MAX_SOURCE_CHARS} characters")
        return v

    @field_validator("options")
    @classmethod
    def _options_bounded(cls, v):
        if len(v) > 10: raise ValueError("too many options")
        return v


class EmailIn(BaseModel):
    draft: str = Field(min_length=1, max_length=10000)
    recipient: str
    confirmed: bool = False


class AnnotationIn(BaseModel):
    label: str = Field(max_length=40)
    note: str = Field(default="", max_length=2000)


def _csv_safe(v):
    s = "" if v is None else str(v)
    return "'" + s if s[:1] in ("=", "+", "-", "@") else s    # block spreadsheet formula injection


PLAIN_SETTING = re.compile(r"[A-Za-z0-9._:-]{1,80}")


def estimated_run_cost(st) -> float:
    """What one full run is assumed to cost: judgments per run times an estimated cost per judgment (about 3 cents, measured at
    claude-opus-5-5 list prices). Derived from max_judgments so that raising it can never make the budget reservation undercount."""
    return round(st["max_judgments"] * st["estimated_cost_per_judgment_usd"], 4)


def cost_of(adapter, settings, input_tokens, output_tokens):
    """Cost estimate for a run. The mock model makes no paid call, so its runs cost nothing and never count toward the
    budget (its token figures are only character counts, used by tests)."""
    return None if getattr(adapter, "name", "") == "mock" else run_cost(settings, input_tokens, output_tokens)


def plain_setting(v):
    """Echo a setting only if it looks like an ordinary identifier; anything else (a pasted key, a URL, a sentence)
    is reported as set but never shown."""
    if v is None:
        return None
    return v if PLAIN_SETTING.fullmatch(v) else "(set, unusual value)"


def create_app(db_path: str = None, lister=None, detailer=None, openalex_client=None) -> FastAPI:
    """lister/detailer override the live source functions; tests inject fakes so no test hits the network."""
    app = FastAPI(title="FORGE SIGNAL API", version="0.2-skeleton", docs_url=None, redoc_url=None)
    origins = [o.strip() for o in os.environ.get("FORGE_CORS_ORIGINS", "").split(",") if o.strip()]
    if origins:                                   # only when the pages are hosted on a different address than the API
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST", "PUT"],
                           allow_headers=["Content-Type", "X-Admin-Token", "X-Access-Code"])
    db = Database(db_path or os.environ.get("FORGE_DB", "forge.db"))
    app.state.db = db
    admin_token = os.environ.get("ADMIN_TOKEN", "")
    if admin_token and len(admin_token) < 32:
        import logging
        logging.getLogger("uvicorn.error").warning("ADMIN_TOKEN is shorter than 32 characters. Use a long random string.")
    if db.pg and not os.environ.get("FORGE_SALT"):
        import logging
        logging.getLogger("uvicorn.error").warning("FORGE_SALT is not set: visitor hashes use a public default salt. Set it in every hosted environment.")
    if lister is None and detailer is None:                    # not under test: use the stored copy once it exists
        lister, detailer = store.sources(db)

    @app.middleware("http")
    async def cap_body(request: Request, call_next):
        if request.method in ("POST", "PUT") and not request.url.path.startswith("/api/admin"):
            n = request.headers.get("content-length")
            if n is None or not n.isdigit() or int(n) > MAX_BODY_BYTES:
                return Response("request too large or missing its length", status_code=413 if n else 411)
        return await call_next(request)

    def client_ip(request: Request) -> str:
        """The socket peer, unless the server sits behind N trusted proxies (FORGE_TRUSTED_PROXY_HOPS=N). Then the
        address the outermost trusted proxy saw is the Nth entry from the RIGHT of X-Forwarded-For: entries further
        left were supplied by the client and can be forged. Unset or 0 ignores the header entirely (safe default)."""
        peer = request.client.host if request.client else "unknown"
        try:
            hops = int(os.environ.get("FORGE_TRUSTED_PROXY_HOPS", "0"))
        except ValueError:
            hops = 0
        if hops > 0:
            parts = [x.strip() for x in request.headers.get("x-forwarded-for", "").split(",") if x.strip()]
            if len(parts) >= hops:
                return parts[-hops]
        return peer

    def visitor(request: Request) -> str:
        ip = client_ip(request)
        return hashlib.sha256((ip + os.environ.get("FORGE_SALT", "dev-salt")).encode()).hexdigest()[:16]

    def admin(x_admin_token: str = Header(default="")):
        expected = os.environ.get("ADMIN_TOKEN", "")
        if not expected: raise HTTPException(503, "admin is disabled: ADMIN_TOKEN is not set on the server")
        if db.pg and len(expected) < MIN_HOSTED_ADMIN_TOKEN:
            raise HTTPException(503, f"The admin API is disabled: on a hosted database ADMIN_TOKEN must be at least {MIN_HOSTED_ADMIN_TOKEN} characters. Set a longer one and restart.")
        if not hmac.compare_digest(x_admin_token, expected): raise HTTPException(401, "admin sign-in required")
        return "admin"

    def current_rubric():
        return db.published_rubric() or DEFAULT_RUBRIC

    @app.get("/api/health")
    def health():
        return {"status": "ok", "time": datetime.now(timezone.utc).isoformat(timespec="seconds")}

    @app.get("/api/notice")
    def notice():
        return {"notice": NOTICE}

    # ---------------------------------------------------------------- tester access codes
    access_fails = {}                              # visitor hash -> times of FAILED code attempts in the last hour; per process, in memory only
    busy_codes = set()                             # access code ids with a run in flight; per process
    busy_lock = threading.Lock()

    @contextlib.contextmanager
    def in_flight(code_id):
        """One live run at a time per code: a second concurrent run from the same code is refused, never queued."""
        with busy_lock:
            if code_id in busy_codes:
                raise HTTPException(429, {"code": "run_in_progress", "message": "Another search with this access code is still running. Please wait for it to finish, then try again."})
            busy_codes.add(code_id)
        try:
            yield
        finally:
            with busy_lock:
                busy_codes.discard(code_id)

    def access_gate(st, vh, code):
        """Validate the X-Access-Code header. Only FAILED attempts are counted, per visitor address, in memory (about 20 an
        hour, then 429): a throttle on guessing, never a lock on any code. Failures are not logged or stored."""
        if not code:
            raise HTTPException(403, access.AccessError("missing").detail())
        t = time.time()
        for k in [k for k, v in access_fails.items() if not v or t - v[-1] >= 3600]: del access_fails[k]
        recent = [x for x in access_fails.get(vh, []) if t - x < 3600]
        if len(recent) >= st["access_failures_per_hour"]:
            raise HTTPException(429, access.AccessError("too_many_attempts").detail())
        try:
            return access.check(db, code)
        except access.NoSalt:
            raise HTTPException(503, "Access codes are not configured on this server.")
        except access.AccessError as e:
            if e.code == "invalid":
                access_fails[vh] = recent + [t]
            raise HTTPException(e.status, e.detail())

    @app.get("/api/access/check")
    def access_check(request: Request, x_access_code: str = Header(default="")):
        """Validate a code without spending anything, so the page can accept or refuse it before a search is filled in."""
        st = db.settings()
        if not st["require_access_code"]:
            return {"required": False, "valid": True}
        row = access_gate(st, visitor(request), x_access_code)
        return {"required": True, "valid": True, "remaining": access.remaining(db, row["id"]), "expires_at": row["expires_at"]}

    class AccessCodeIn(BaseModel):
        label: str = Field(max_length=100)
        allowance: int = 3
        expires_at: str | None = None                # omitted: the default expiry setting; "none": no expiry

    @app.post("/api/admin/access-codes")
    def create_access_code(body: AccessCodeIn, actor=Depends(admin)):
        st = db.settings(); limit, est = st["pilot_budget_usd"], estimated_run_cost(st)
        if limit and est and isinstance(body.allowance, int) and not isinstance(body.allowance, bool) and 1 <= body.allowance <= 20:
            # BUDGET RESERVATION: recorded spend + every run still allowed to usable codes + this code's runs must fit the pilot budget
            outstanding = sum(c["remaining"] for c in access.listing(db)
                              if not c["revoked"] and not (c["expires_at"] and c["expires_at"] <= now()))
            spent = db.spent_usd()
            if spent + (outstanding + body.allowance) * est > limit + 1e-9:
                raise HTTPException(409, {"code": "budget_would_be_exceeded",
                    "message": (f"Creating this code would exceed the pilot budget: ${spent:.2f} is already recorded, {outstanding} runs are already "
                                f"allowed to other codes and this code adds {body.allowance}, at about ${est:.2f} a run, against a budget of ${limit:.2f}. "
                                "Lower the allowance, revoke an unused code, or raise pilot_budget_usd on purpose after checking the provider console.")})
        try:
            exp = access.iso_expiry(body.expires_at, db.settings()["access_code_default_expiry"])
            out = access.create(db, body.label, body.allowance, exp, actor)
        except access.NoSalt as e:
            raise HTTPException(503, str(e))
        except ValueError as e:
            raise HTTPException(400, str(e))
        db.audit(actor, "access_code_created", {"id": out["id"], "label": out["label"], "allowance": out["allowance"], "expires_at": out["expires_at"]})
        out["created_at"] = now()
        return JSONResponse(out, status_code=201, headers={"Cache-Control": "no-store"})     # the only time the code is shown

    @app.get("/api/admin/access-codes")
    def list_access_codes(_=Depends(admin)):
        return JSONResponse(access.listing(db), headers={"Cache-Control": "no-store"})

    @app.post("/api/admin/access-codes/{code_id}/revoke")
    def revoke_access_code(code_id: str, actor=Depends(admin)):
        at = access.revoke(db, code_id)
        if at is None: raise HTTPException(404, "access code not found")
        db.audit(actor, "access_code_revoked", {"id": code_id})
        return {"id": code_id, "revoked_at": at}

    # ---------------------------------------------------------------- public run
    @app.post("/api/runs")
    def create_run(body: RunIn, request: Request, x_access_code: str = Header(default="")):
        if body.input_type not in INPUT_TYPES: raise HTTPException(400, f"input_type must be one of {INPUT_TYPES}")
        live = not body.sources
        if live and not (body.profile.lanes or body.input_text.strip()):
            raise HTTPException(422, "Describe the researcher's established research areas before running a live match.")
        s, vh = db.settings(), visitor(request)
        code_row = access_gate(s, vh, x_access_code) if s["require_access_code"] else None      # tester code, before any other gate
        hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(timespec="seconds")
        day_start = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00")
        if db.count_runs_since(vh, hour_ago) >= s["rate_limit_per_hour"]: raise HTTPException(429, "Too many runs from this visitor. Try again later.")
        if db.count_runs_since(None, day_start) >= s["daily_cap"]: raise HTTPException(503, "The daily run limit has been reached. Please try again tomorrow.")
        if budget_state(s)["state"] == "reached":
            raise HTTPException(503, {"code": "budget_reached", "message": "The pilot's AI budget has been used up, so live runs are paused. You can look at the recorded example run instead."})
        for k, v in body.options.items():            # per-run only; rate limits and caps can never be overridden here
            num = isinstance(v, (int, float)) and not isinstance(v, bool)
            if k == "horizon_months" and num and 0 < v <= 36: s[k] = v
            elif k == "lead_time_days" and isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 365: s[k] = v
            else: raise HTTPException(400, f"option '{k}' is not allowed or is out of range")
        try:
            adapter = get_adapter(s)
        except (ValueError, RuntimeError) as e:
            raise HTTPException(503, f"model not available: {e}")        # message never contains a key
        if code_row is None:
            return _execute(body, s, vh, live, adapter, None)
        with in_flight(code_row["id"]):
            return _execute(body, s, vh, live, adapter, code_row)

    def _execute(body, s, vh, live, adapter, code_row):
        ctx = {"claimed": False, "rid": None}
        try:
            return _execute_inner(body, s, vh, live, adapter, code_row, ctx)
        except HTTPException:
            raise
        except Exception as e:
            # an unexpected error after the allowance was taken: mark the run failed (not left 'running'), refund if nothing
            # was billed, and let the error surface. The exception text is never stored (it could hold a secret).
            if ctx["rid"]:
                u = getattr(adapter, "total_usage", {}) or {}
                db.finish_run(ctx["rid"], "failed", 0, f"unexpected error: {type(e).__name__}", u.get("input_tokens", 0), u.get("output_tokens", 0),
                              cost_usd=cost_of(adapter, s, u.get("input_tokens", 0), u.get("output_tokens", 0)))
            if ctx["claimed"] and code_row is not None and not (getattr(adapter, "total_usage", {}) or {}).get("input_tokens"):
                access.refund(db, code_row["id"])
            raise

    def _execute_inner(body, s, vh, live, adapter, code_row, ctx):
        if code_row is not None and not access.claim(db, code_row):          # atomic: two simultaneous requests cannot both take the last run
            fresh = db.q("SELECT * FROM access_codes WHERE id=?", (code_row["id"],), one=True)
            raise HTTPException(403, access.AccessError(access.state(fresh) or "allowance_used").detail())
        ctx["claimed"] = code_row is not None
        rid = db.create_run(vh, body.input_type, body.input_text, s, R.version(current_rubric()), adapter.name)
        ctx["rid"] = rid
        if code_row is not None:
            db.q("UPDATE runs SET access_code_id=? WHERE id=?", (code_row["id"], rid), write=True)
        t0 = time.time()
        access_info = lambda: {"remaining": access.remaining(db, code_row["id"])} if code_row is not None else None
        refund = lambda: access.refund(db, code_row["id"]) if code_row is not None else None

        if live:
            profile = body.profile.model_dump()
            if not profile["lanes"]:
                profile["lanes"] = [body.input_text.strip()]
            try:
                out = run_match(db, rid, adapter, s, profile, body.question, lister=lister, detailer=detailer)
            except SourceError as e:
                db.finish_run(rid, "failed", int((time.time() - t0) * 1000), f"source unavailable: {e}")
                refund()                                    # nothing was spent: do not charge the tester's allowance
                raise HTTPException(503, "The funding source could not be read right now. The attempt was logged.")
            c = out["counters"]
            if c["judged"] == 0 and c["model_failures"] > 0:
                # nothing could be rated because of the model side, whatever the cause: a failed run, not an empty result list
                unreachable = c["model_call_failures"] > 0
                reason = (f"model unavailable: all {c['model_failures']} calls failed" if unreachable
                          else f"model answers unreadable: all {c['model_failures']} answers were invalid")
                # a failed run still spent tokens (unreadable answers cost output): keep its cost so the budget sum is not understated
                db.finish_run(rid, "failed", c["latency_ms"], reason, c["input_tokens"], c["output_tokens"],
                              c["opportunities_listed"], c["details_fetched"], cost_of(adapter, s, c["input_tokens"], c["output_tokens"]))
                if not c["input_tokens"]:
                    refund()                                # no model call succeeded, nothing spent; unreadable answers did spend, so they count
                raise HTTPException(502, "The model could not be reached, so nothing was rated. The attempt was logged; please try again later."
                                    if unreachable else
                                    "The model's answers could not be read, so nothing was rated. The attempt was logged; please try again later.")
            c["cost_usd"] = cost_of(adapter, s, c["input_tokens"], c["output_tokens"])
            c["cost_basis"] = "estimate from reported token usage; needs both prices set; excludes calls abandoned or failed"
            db.finish_run(rid, "ok", c["latency_ms"], None, c["input_tokens"], c["output_tokens"],
                          c["opportunities_listed"], c["details_fetched"], c["cost_usd"])
            return {"run_id": rid, "results": out["results"], "counters": c, **({"access": access_info()} if code_row is not None else {}),
                    "retrieved_at": store.as_of(db) if store.status(db)["with_full_text"] else datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "source": store.provenance(db), "notice": NOTICE}

        for sid, text in body.sources.items():
            db.add_source(rid, sid, sid if sid.startswith("http") else "", hashlib.sha256(text.encode()).hexdigest()[:16])
        try:
            j = adapter.judge(body.sources, body.question)
        except SchemaError as e:
            db.finish_run(rid, "failed", int((time.time() - t0) * 1000), f"model output invalid: {e}")
            raise HTTPException(502, "The model did not return a valid answer. The attempt was logged.")
        except Exception as e:
            db.finish_run(rid, "failed", int((time.time() - t0) * 1000), type(e).__name__)
            refund()
            raise HTTPException(502, "The model call failed. The attempt was logged.")
        r = validate(j, body.sources)
        for c in r["fit_citations"] + r["eligibility_citations"]: db.add_citation(rid, c.source_id, c.quote, True)
        for f in r["failed_citations"]: db.add_citation(rid, f["source_id"], f["quote"], False, "quote not found in source")
        result = {"fit": r["fit"], "eligibility": r["eligibility"], "rationale": r["rationale"],
                  "citations": [{"source_id": c.source_id, "quote": c.quote} for c in r["fit_citations"] + r["eligibility_citations"]],
                  "failed_citation_count": len(r["failed_citations"])}
        db.add_match(rid, result)
        u = adapter.total_usage
        db.finish_run(rid, "ok", int((time.time() - t0) * 1000), None, u.get("input_tokens", 0), u.get("output_tokens", 0),
                      cost_usd=cost_of(adapter, s, u.get("input_tokens", 0), u.get("output_tokens", 0)))
        return {"run_id": rid, "result": result, "notice": NOTICE, **({"access": access_info()} if code_row is not None else {})}

    # ---------------------------------------------------------------- researcher lookup (OpenAlex)
    pi_hits = {}                                   # visitor hash -> request times in the last hour; per process, resets on restart
    pi_day = {"date": None, "n": 0}                # global daily count; per process

    def pi_log(endpoint, params, ok, status, ms, error):
        db.q("INSERT INTO api_calls(at,source,endpoint,params,ok,http_status,latency_ms,error,ingest_id) VALUES(?,?,?,?,?,?,?,?,?)",
             (now(), "OpenAlex", endpoint, json.dumps(params), int(ok), status, ms, error, None), write=True)

    lookup = openalex.Lookup(client=openalex_client, log=pi_log)

    def pi_limit(request: Request):
        st = db.settings(); vh, t = visitor(request), time.time()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if pi_day["date"] != today: pi_day.update(date=today, n=0)
        for k in [k for k, v in pi_hits.items() if not v or t - v[-1] >= 3600]: del pi_hits[k]      # prune idle visitors
        if pi_day["n"] >= st["pi_lookups_per_day"]: raise openalex.OpenAlexError("daily_limit")
        recent = [x for x in pi_hits.get(vh, []) if t - x < 3600]
        if len(recent) >= st["pi_lookups_per_hour"]: raise openalex.OpenAlexError("hourly_limit")
        pi_hits[vh] = recent + [t]; pi_day["n"] += 1

    def pi_error(e: "openalex.OpenAlexError"):
        return HTTPException(e.status, {"code": e.code, "message": e.message})

    def pi_access(request, code):
        """The researcher lookup calls a third party, so it needs a valid access code too (checked, never consuming an allowance)."""
        st = db.settings()
        if st["require_access_code"]:
            access_gate(st, visitor(request), code)

    class PiSearchIn(BaseModel):
        name: str = Field(max_length=500)           # real limits (3 to 120 characters, after cleaning) are checked with clear messages

    @app.post("/api/pi/search")                       # POST so the name never appears in a URL or access log
    def pi_search(body: PiSearchIn, request: Request, x_access_code: str = Header(default="")):
        pi_access(request, x_access_code)
        try:
            openalex.clean_name(body.name)            # refuse before spending a lookup
            pi_limit(request)
            return lookup.search(body.name)
        except openalex.OpenAlexError as e:
            raise pi_error(e)

    @app.get("/api/pi/{author_id}/expertise")
    def pi_expertise(author_id: str, request: Request, x_access_code: str = Header(default="")):
        pi_access(request, x_access_code)
        try:
            if not openalex.ID_RE.fullmatch(author_id): raise openalex.OpenAlexError("bad_author_id")
            pi_limit(request)
            return lookup.expertise(author_id)
        except openalex.OpenAlexError as e:
            raise pi_error(e)

    @app.post("/api/runs/{rid}/email")
    def send_email(rid: str, body: EmailIn, request: Request):
        run = db.get_run(rid)
        if run is None or run["visitor_hash"] != visitor(request): raise HTTPException(404, "run not found")
        if not body.confirmed: raise HTTPException(400, "A person must review the draft and tick the confirmation before it can be sent.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", body.recipient): raise HTTPException(400, "enter a valid recipient address")
        mode = db.settings()["email_mode"]
        db.add_email(rid, body.draft, body.recipient, True, mode)
        return {"status": "logged", "mode": mode, "message": "Dummy mode: the alert was logged and no email was sent." if mode == "dummy" else "Test mode."}

    # ---------------------------------------------------------------- calendar (FR-12, FR-13)
    def _calendar_for(rid, request):
        run = db.get_run(rid)
        if run is None or run["visitor_hash"] != visitor(request):
            raise HTTPException(404, "run not found")
        rows = []
        for m in run["matches"]:
            if not m.get("fit"):
                continue
            r = dict(m)
            r["close_date"] = date.fromisoformat(m["close_date"]) if m.get("close_date") else None
            rows.append(r)
        lead = run["settings_snapshot"].get("lead_time_days", 14)
        return run, build_calendar(rows, lead_days=lead)

    def _slug(run):
        return "forge-signal-" + (run["created_at"][:10] if run.get("created_at") else "calendar")

    @app.get("/api/runs/{rid}/calendar")
    def calendar_json(rid: str, request: Request):
        run, cal = _calendar_for(rid, request)
        def out(r):
            return {k: (v.isoformat() if isinstance(v, date) else v)
                    for k, v in r.items() if k not in ("how_calculated", "citations")}
        return {"run_id": rid, "lead_days": cal["lead_days"], "today": cal["today"].isoformat(),
                "groups": {g: [out(r) for r in rows] for g, rows in cal["groups"].items()},
                "decide_now": [out(r) for r in cal["decide_now"]],
                "needs_action": [out(r) for r in cal["needs_action"]],
                "top": [out(r) for r in cal["top"]], "watch": [out(r) for r in cal["watch"]]}

    @app.get("/api/runs/{rid}/calendar.ics")
    def calendar_ics(rid: str, request: Request):
        run, cal = _calendar_for(rid, request)
        return Response(to_ics(cal), media_type="text/calendar; charset=utf-8",
                        headers={"Content-Disposition": f'attachment; filename="{_slug(run)}.ics"'})

    @app.get("/api/runs/{rid}/calendar.xlsx")
    def calendar_xlsx(rid: str, request: Request):
        run, cal = _calendar_for(rid, request)
        data = to_xlsx(cal, {"investigator": run.get("input_text")})
        return Response(data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f'attachment; filename="{_slug(run)}.xlsx"'})

    # ---------------------------------------------------------------- admin
    def budget_state(st) -> dict:
        """The application-level budget stop: refuses new live runs once the recorded estimate reaches pilot_budget_usd.
        Inactive when no prices are set (cost is then unknown) or the limit is 0. It undercounts (failed or abandoned
        calls, and spend made outside this database), so it must be set below the provider limit, which stays the real guard."""
        limit = st.get("pilot_budget_usd") or 0
        if not st.get("price_per_mtok_input") or not st.get("price_per_mtok_output"):
            return {"state": "inactive: prices not set", "pilot_budget_usd": limit, "recorded_spend_estimate_usd": None, "prices_in_use": None}
        if not limit:
            return {"state": "inactive: pilot_budget_usd is 0", "pilot_budget_usd": 0, "recorded_spend_estimate_usd": round(db.spent_usd(), 4), "prices_in_use": None}
        spent = round(db.spent_usd(), 4)
        return {"state": "reached" if spent >= limit else "active", "pilot_budget_usd": limit, "recorded_spend_estimate_usd": spent,
                "prices_in_use": {"input_usd_per_million": st["price_per_mtok_input"], "output_usd_per_million": st["price_per_mtok_output"],
                                  "basis": "estimate: list prices for claude-opus-5-5 (cached 2026-11-03); the owner confirms them in the provider console"},
                "counts": "only runs in this database; not the roughly $7 of earlier engineering spend"}

    def reservation(st) -> dict:
        """The money already spoken for: recorded spend plus every run still allowed to usable codes at the estimated run cost."""
        outstanding = sum(c["remaining"] for c in access.listing(db)
                          if not c["revoked"] and not (c["expires_at"] and c["expires_at"] <= now()))
        est, spent = estimated_run_cost(st), round(db.spent_usd(), 4)
        return {"outstanding_runs": outstanding, "estimated_run_cost_usd": est, "derived_from": f"{st['max_judgments']} judgments x ${st['estimated_cost_per_judgment_usd']} each",
                "committed_estimate_usd": round(outstanding * est, 2),
                "recorded_spend_estimate_usd": spent, "total_usd": round(spent + outstanding * est, 2), "pilot_budget_usd": st["pilot_budget_usd"]}

    @app.get("/api/admin/environment")
    def environment(_=Depends(admin)):
        """Which settings are in effect, WITHOUT any secret value: yes/no for secrets, the kind of database (never its
        address), and plain values only for non-secret settings."""
        key_var = next((n for n in KEY_VARS if (os.environ.get(n) or "").strip()), None)
        static_dir = pathlib.Path(os.environ.get("FORGE_STATIC") or pathlib.Path(__file__).resolve().parents[2] / "public" / "signal")
        return {"database": "postgres" if db.pg else ("memory" if db.target == ":memory:" else "sqlite file"),
                "schema_version": db.schema_version(),
                "admin_token_set": bool(os.environ.get("ADMIN_TOKEN")), "salt_set": bool(os.environ.get("FORGE_SALT")),
                "model_key_variable": key_var,                      # the variable's NAME, never its value
                "active_model": db.settings()["active_model"],
                "model": plain_setting(os.environ.get("FORGE_MODEL", "claude-opus-5-5")),
                "effort": plain_setting(os.environ.get("FORGE_EFFORT") or None),
                "trusted_proxy_hops": os.environ.get("FORGE_TRUSTED_PROXY_HOPS", "0"),
                "cors_origins": origins, "model_max_concurrent": MODEL_MAX_CONCURRENT,
                "judge_concurrency": db.settings()["judge_concurrency"],
                "static_dir_found": static_dir.is_dir(), "max_body_bytes": MAX_BODY_BYTES,
                "budget_stop": budget_state(db.settings()),
                "access_codes": {"required": db.settings()["require_access_code"], "salt_set": bool(os.environ.get("FORGE_SALT")),
                                 "budget_reservation": reservation(db.settings()),
                                 "usable_codes": sum(1 for c in access.listing(db) if not c["revoked"] and c["remaining"] > 0
                                                     and not (c["expires_at"] and c["expires_at"] <= now()))},
                "daily_cap": db.settings()["daily_cap"], "rate_limit_per_hour": db.settings()["rate_limit_per_hour"],
                "max_judgments": db.settings()["max_judgments"]}

    @app.get("/api/admin/whoami")
    def whoami(request: Request, _=Depends(admin)):
        """What address the server believes this request came from, for setting FORGE_TRUSTED_PROXY_HOPS. Admin only;
        the address is never shown to the public and the visitor hash is the only form that is stored."""
        return {"believed_client_ip": client_ip(request), "socket_peer": request.client.host if request.client else None,
                "x_forwarded_for": request.headers.get("x-forwarded-for"),
                "trusted_proxy_hops": os.environ.get("FORGE_TRUSTED_PROXY_HOPS", "0")}

    @app.get("/api/admin/settings")
    def get_settings(_=Depends(admin)):
        return {"settings": db.settings(), "available_models": available()}

    @app.put("/api/admin/settings")
    def put_settings(changes: dict, actor=Depends(admin)):
        old = db.settings()
        for k, v in changes.items():
            if k not in DEFAULT_SETTINGS: raise HTTPException(400, f"unknown setting '{k}'")
            d = DEFAULT_SETTINGS[k]
            if isinstance(v, bool) != isinstance(d, bool) or not isinstance(v, type(d)):
                raise HTTPException(400, f"setting '{k}' must be {type(d).__name__}")
            if isinstance(v, int) and v < 0: raise HTTPException(400, f"setting '{k}' must not be negative")
        if "active_model" in changes and changes["active_model"] not in available(): raise HTTPException(400, f"active_model must be one of {available()}")
        if "email_mode" in changes and changes["email_mode"] not in ("dummy", "test"): raise HTTPException(400, "email_mode must be dummy or test")
        if "min_fit" in changes and changes["min_fit"] not in FIT: raise HTTPException(400, f"min_fit must be one of {FIT}")
        for k, v in changes.items():
            db.set_setting(k, v)
            db.audit(actor, "setting_changed", {"key": k, "from": old[k], "to": v})   # model switches land here too (FR-19)
        return {"settings": db.settings()}

    @app.get("/api/admin/audit")
    def audit(limit: int = 100, _=Depends(admin)):
        return [dict(r) for r in db.q("SELECT at,actor,action,detail FROM admin_audit ORDER BY id DESC LIMIT ?", (min(limit, 500),))]

    @app.get("/api/admin/runs")
    def runs(limit: int = 50, offset: int = 0, q: str = None, archived: bool = False, _=Depends(admin)):
        return db.list_runs(min(limit, 200), offset, q, archived)

    @app.get("/api/admin/runs.csv")
    def runs_csv(_=Depends(admin)):
        out = io.StringIO(); w = csv.writer(out)
        cols = ["id", "created_at", "input_type", "input_text", "model", "status", "latency_ms", "rubric_version", "archived", "cost_usd", "access_code_id"]
        w.writerow([c + "_estimate" if c == "cost_usd" else c for c in cols])      # runs.cost_usd is an estimate from reported usage
        for r in db.list_runs(10000, 0, None, True): w.writerow([_csv_safe(r[c]) for c in cols])
        return Response(out.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=forge-signal-runs.csv"})

    @app.get("/api/admin/runs/{rid}")
    def run_detail(rid: str, _=Depends(admin)):
        r = db.get_run(rid)
        if r is None: raise HTTPException(404, "run not found")
        return r

    @app.post("/api/admin/runs/{rid}/annotations")
    def annotate(rid: str, body: AnnotationIn, actor=Depends(admin)):
        if db.get_run(rid) is None: raise HTTPException(404, "run not found")
        db.add_annotation(rid, body.label, body.note); db.audit(actor, "annotation", {"run": rid, "label": body.label})
        return {"ok": True}

    @app.post("/api/admin/ingest")
    def run_ingest(actor=Depends(admin)):
        try:
            out = store.ingest(db)
        except SourceError as e:
            raise HTTPException(503, f"Grants.gov could not be read: {e}")
        db.audit(actor, "ingest", out)
        return out

    @app.get("/api/admin/ingest/status")
    def ingest_status(_=Depends(admin)):
        return store.status(db)

    @app.get("/api/admin/api-calls")
    def api_calls(limit: int = 100, _=Depends(admin)):
        return {"calls": [dict(r) for r in db.q("SELECT at,source,endpoint,params,ok,http_status,latency_ms,error,ingest_id FROM api_calls ORDER BY id DESC LIMIT ?", (min(max(limit, 1), 500),))]}

    @app.post("/api/admin/retention/run")
    def retention(actor=Depends(admin)):
        n = db.archive_older_than(db.settings()["retention_days"]); db.audit(actor, "retention", {"archived": n})
        return {"archived": n}

    @app.get("/api/admin/rubric")
    def get_rubric(_=Depends(admin)):
        rb = current_rubric()
        return {"version": R.version(rb), "rubric": rb, "versions": db.rubric_versions()}

    async def _upload_preview(file: UploadFile):
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            tmp.write(await file.read()); tmp.flush()
            return preview(tmp.name, current_rubric())

    @app.post("/api/admin/rubric/preview")
    async def rubric_preview(file: UploadFile = File(...), _=Depends(admin)):
        return await _upload_preview(file)

    @app.post("/api/admin/rubric/publish")
    async def rubric_publish(note: str = "", file: UploadFile = File(...), actor=Depends(admin)):
        from .template_xlsx import parse_template
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            tmp.write(await file.read()); tmp.flush()
            rub, _profile, errors = parse_template(tmp.name)
        if errors or rub is None: raise HTTPException(400, {"parse_errors": errors})
        ok, problems = R.publishable(rub)                 # FR-48 publish gate
        if not ok: raise HTTPException(400, {"problems": problems})
        old = R.version(current_rubric()); new = R.version(rub)
        db.publish_rubric(new, rub, note)
        db.audit(actor, "rubric_published", {"from": old, "to": new, "diff": R.diff(current_rubric() if False else DEFAULT_RUBRIC, rub), "note": note})
        return {"version": new}

    # ---------------------------------------------------------------- the pages (one address for pages and API)
    @app.get("/config.js", include_in_schema=False)
    def config_js():
        """Tells the pages they are talking to a live API at this same address."""
        return PlainTextResponse('window.SIGNAL = {live: true, api: ""};\n', media_type="application/javascript",
                                 headers={"Cache-Control": "no-store"})

    static = pathlib.Path(os.environ.get("FORGE_STATIC") or pathlib.Path(__file__).resolve().parents[2] / "public" / "signal")
    if static.is_dir():                           # mounted last, so every /api route above wins
        app.mount("/", StaticFiles(directory=str(static), html=True), name="pages")
    return app
