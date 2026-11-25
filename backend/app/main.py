"""FORGE SIGNAL API skeleton: public run endpoint, dummy email, admin dashboard API, run log.
Hard rules enforced here: keys only from the server environment and never returned; human confirmation
before any email; per-visitor rate limit and daily cap; no raw source text returned to the public."""
import csv, hashlib, hmac, io, os, pathlib, re, tempfile, time
from datetime import date, datetime, timedelta, timezone

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import rubric as R
from . import store
from .adapters.registry import available, get_adapter
from .db import DEFAULT_SETTINGS, NOTICE, Database, run_cost
from .fit import DEFAULT_RUBRIC
from .calendar import build_calendar
from .exports import to_ics, to_xlsx
from .pipeline import run_match
from .schemas import FIT, SchemaError
from .sources.grants_gov import SourceError
from .sources import openalex
from .template_xlsx import preview
from .validator import validate

INPUT_TYPES = ("pi_name", "project", "keywords", "opportunity_unit")


class Profile(BaseModel):
    """Researcher evidence for ONE run. Never stored outside that run's log (hard rule 1)."""
    career_stage: str = Field(default="", max_length=200)
    lanes: list[str] = Field(default_factory=list, max_length=40)
    positioning_rules: list[str] = Field(default_factory=list, max_length=20)


class RunIn(BaseModel):
    input_type: str
    input_text: str = Field(min_length=1, max_length=4000)
    question: str = "Does this researcher fit this opportunity, and is the researcher's institution eligible?"
    profile: Profile = Field(default_factory=Profile)
    sources: dict[str, str] = {}      # pasted evidence; omit it to pull live from Grants.gov (FR-5)
    options: dict = Field(default_factory=dict)   # per-run overrides: horizon_months, lead_time_days (never saved as settings)


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


def create_app(db_path: str = None, lister=None, detailer=None, openalex_client=None) -> FastAPI:
    """lister/detailer override the live source functions; tests inject fakes so no test hits the network."""
    app = FastAPI(title="FORGE SIGNAL API", version="0.2-skeleton", docs_url=None, redoc_url=None)
    origins = [o.strip() for o in os.environ.get("FORGE_CORS_ORIGINS", "").split(",") if o.strip()]
    if origins:                                   # only when the pages are hosted on a different address than the API
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST", "PUT"],
                           allow_headers=["Content-Type", "X-Admin-Token"])
    db = Database(db_path or os.environ.get("FORGE_DB", "forge.db"))
    app.state.db = db
    if lister is None and detailer is None:                    # not under test: use the stored copy once it exists
        lister, detailer = store.sources(db)

    def visitor(request: Request) -> str:
        ip = request.client.host if request.client else "unknown"
        return hashlib.sha256((ip + os.environ.get("FORGE_SALT", "dev-salt")).encode()).hexdigest()[:16]

    def admin(x_admin_token: str = Header(default="")):
        expected = os.environ.get("ADMIN_TOKEN", "")
        if not expected: raise HTTPException(503, "admin is disabled: ADMIN_TOKEN is not set on the server")
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

    # ---------------------------------------------------------------- public run
    @app.post("/api/runs")
    def create_run(body: RunIn, request: Request):
        if body.input_type not in INPUT_TYPES: raise HTTPException(400, f"input_type must be one of {INPUT_TYPES}")
        live = not body.sources
        if live and not (body.profile.lanes or body.input_text.strip()):
            raise HTTPException(422, "Describe the researcher's established research areas before running a live match.")
        s, vh = db.settings(), visitor(request)
        hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(timespec="seconds")
        day_start = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00")
        if db.count_runs_since(vh, hour_ago) >= s["rate_limit_per_hour"]: raise HTTPException(429, "Too many runs from this visitor. Try again later.")
        if db.count_runs_since(None, day_start) >= s["daily_cap"]: raise HTTPException(503, "The daily run limit has been reached. Please try again tomorrow.")
        for k, v in body.options.items():            # per-run only; rate limits and caps can never be overridden here
            num = isinstance(v, (int, float)) and not isinstance(v, bool)
            if k == "horizon_months" and num and 0 < v <= 36: s[k] = v
            elif k == "lead_time_days" and isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= 365: s[k] = v
            else: raise HTTPException(400, f"option '{k}' is not allowed or is out of range")
        try:
            adapter = get_adapter(s)
        except (ValueError, RuntimeError) as e:
            raise HTTPException(503, f"model not available: {e}")        # message never contains a key
        rid = db.create_run(vh, body.input_type, body.input_text, s, R.version(current_rubric()), adapter.name)
        t0 = time.time()

        if live:
            profile = body.profile.model_dump()
            if not profile["lanes"]:
                profile["lanes"] = [body.input_text.strip()]
            try:
                out = run_match(db, rid, adapter, s, profile, body.question, lister=lister, detailer=detailer)
            except SourceError as e:
                db.finish_run(rid, "failed", int((time.time() - t0) * 1000), f"source unavailable: {e}")
                raise HTTPException(503, "The funding source could not be read right now. The attempt was logged.")
            c = out["counters"]
            c["cost_usd"] = run_cost(s, c["input_tokens"], c["output_tokens"])
            db.finish_run(rid, "ok", c["latency_ms"], None, c["input_tokens"], c["output_tokens"],
                          c["opportunities_listed"], c["details_fetched"], c["cost_usd"])
            return {"run_id": rid, "results": out["results"], "counters": c,
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
                      cost_usd=run_cost(s, u.get("input_tokens", 0), u.get("output_tokens", 0)))
        return {"run_id": rid, "result": result, "notice": NOTICE}

    # ---------------------------------------------------------------- researcher lookup (OpenAlex)
    pi_hits = {}                                   # visitor hash -> request times in the last hour (in memory only)

    def pi_limit(request: Request):
        vh, t = visitor(request), time.time()
        recent = [x for x in pi_hits.get(vh, []) if t - x < 3600]
        if len(recent) >= db.settings()["pi_lookups_per_hour"]:
            raise HTTPException(429, "Too many lookups from this visitor. Try again later.")
        pi_hits[vh] = recent + [t]

    @app.get("/api/pi/search")
    def pi_search(name: str, request: Request):
        pi_limit(request)
        try:
            return {"candidates": openalex.search_authors(name, client=openalex_client),
                    "source": {"system": "OpenAlex", "api": openalex.BASE},
                    "note": "OpenAlex sometimes splits one person into several records. Pick the one that matches, then confirm the terms before anything is screened."}
        except openalex.OpenAlexError as e:
            raise HTTPException(400 if "enter a name" in str(e) else 503, str(e))

    @app.get("/api/pi/{author_id}/expertise")
    def pi_expertise(author_id: str, request: Request):
        pi_limit(request)
        try:
            return openalex.expertise(author_id, client=openalex_client)
        except openalex.OpenAlexError as e:
            raise HTTPException(400 if "not an OpenAlex" in str(e) else 503, str(e))

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
    @app.get("/api/admin/settings")
    def get_settings(_=Depends(admin)):
        return {"settings": db.settings(), "available_models": available()}

    @app.put("/api/admin/settings")
    def put_settings(changes: dict, actor=Depends(admin)):
        old = db.settings()
        for k, v in changes.items():
            if k not in DEFAULT_SETTINGS: raise HTTPException(400, f"unknown setting '{k}'")
            d = DEFAULT_SETTINGS[k]
            if isinstance(d, bool) or isinstance(v, bool) != isinstance(d, bool) or not isinstance(v, type(d)):
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
        cols = ["id", "created_at", "input_type", "input_text", "model", "status", "latency_ms", "rubric_version", "archived"]
        w.writerow(cols)
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
