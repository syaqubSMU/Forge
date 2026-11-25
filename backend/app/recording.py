"""Record ONE real run for the public pages.

The public pages show a fictional sample (public/signal/mock-data.js). A recorded run replaces it with what the real
pipeline produced for a FICTIONAL researcher against the stored public Grants.gov copy, labelled as a recording, so the
pages can show real behaviour without any visitor spending model money.

Nothing here invents content: results, counters, tokens and timings come from `run_match`. Before anything is written,
every quote is checked again, independently of the pipeline, against the stored source text it claims to come from.
Public Grants.gov data only; the researcher is fictional.
"""
import hashlib
import json
import os
import time
from datetime import date

from . import rubric as R
from . import store
from .db import now, run_cost
from .pipeline import run_match, profile_text
from .validator import quote_supported

# A fictional researcher chosen so the stored corpus contains matching programs (the earlier photobiology profile
# matched nothing). No real person, institution or collaborator.
FICTIONAL_PROFILE = {
    "investigator": "Dr. Sample Researcher (fictional)",
    "institution": "Sample University (fictional)",
    "career_stage": "Established investigator. Exclude programs restricted to early-career investigators.",
    "lanes": ["Cancer early detection and biomarkers",
              "Tumor imaging and image-guided therapy",
              "Artificial intelligence for cancer imaging and pathology"],
    "positioning_rules": ["Clinical trials only where a named clinical collaborator is in place",
                          "Population-science programs only where an imaging or biomarker component is central"],
}
LABEL = "Recorded run: real model output on a fictional researcher, from the stored public Grants.gov copy."
QUESTION = "Does this opportunity fit this researcher?"


def source_text_for(db, url: str) -> str:
    row = db.q("SELECT detail FROM opportunities WHERE url=?", (url,), one=True)
    if not row or not row["detail"]:
        return ""
    d = json.loads(row["detail"])
    return "\n\n".join(x for x in (d.get("description"), d.get("eligibility_text")) if x)


def check_quotes(db, results, profile) -> dict:
    """Independent re-check: every quote must appear in the text it cites. Returns counts and the failures."""
    prof = profile_text(profile)
    checked = bad = 0
    failures = []
    for r in results:
        src = source_text_for(db, r["url"])
        for c in r["citations"]:
            checked += 1
            text = prof if c["source_id"] == "researcher-profile" else (src if c["source_id"] == r["url"] else "")
            if not quote_supported(c["quote"], text):
                bad += 1
                failures.append({"number": r["number"], "source_id": c["source_id"], "quote": c["quote"]})
    return {"quotes_checked": checked, "quotes_supported": checked - bad, "quotes_failed": bad, "failures": failures}


def record(db, adapter, settings, profile=None, max_judgments=15, effort=None, prices=None, lister=None, detailer=None):
    """Run once and return the dict to be written. Raises if any quote fails the independent check."""
    profile = dict(profile or FICTIONAL_PROFILE)
    s = dict(settings)
    s.update(max_judgments=max_judgments)
    if lister is None:
        lister, detailer = store.sources(db)
    rubric = db.published_rubric() or R.load(os.path.join(os.path.dirname(__file__), "..", "rubrics", "default.json"))
    rubric_version = R.version(rubric)
    rid = db.create_run("recorded-run", "keywords", "recorded run (fictional researcher)", s, rubric_version, adapter.name)
    t0 = time.time()
    out = run_match(db, rid, adapter, s, {k: profile[k] for k in ("career_stage", "lanes", "positioning_rules")},
                    QUESTION, lister=lister, detailer=detailer)
    c = out["counters"]
    if c["judged"] == 0 and c["model_failures"] > 0:
        db.finish_run(rid, "failed", c["latency_ms"], "recorded run: nothing could be rated")
        raise RuntimeError("nothing could be rated; no file written")
    cost = run_cost(prices or {}, c["input_tokens"], c["output_tokens"])
    db.finish_run(rid, "ok", c["latency_ms"], None, c["input_tokens"], c["output_tokens"],
                  c["opportunities_listed"], c["details_fetched"], cost)
    check = check_quotes(db, out["results"], profile)
    if check["quotes_failed"]:
        raise RuntimeError(f"{check['quotes_failed']} quote(s) not found in their source; no file written: {check['failures'][:3]}")
    excluded = []
    for r in db.q("SELECT data FROM run_matches WHERE run_id=?", (rid,)):
        m = json.loads(r["data"])
        if m.get("tier") == "Excluded":
            excluded.append({"title": m["title"], "number": m["number"], "url": m["url"],
                             "reasons": m["how_calculated"]["reasons"]})
    failures = [dict(x) for x in db.q("SELECT source_id, error FROM run_source_failures WHERE run_id=?", (rid,))]
    c = dict(c, cost_usd=cost)
    sent = {k: profile[k] for k in ("career_stage", "lanes", "positioning_rules")}
    as_of = date.today().isoformat()
    rec = {
        "profile": {k: profile[k] for k in ("investigator", "institution", "career_stage", "lanes", "positioning_rules")},
        "settings": {"horizon_months": s["horizon_months"], "lead_time_days": s["lead_time_days"],
                     "funder_types": s["funder_types"], "min_fit": s["min_fit"], "scope_level": s["scope_level"],
                     "max_judgments": max_judgments},
        "retrieved_at": store.as_of(db),
        "counters": c, "results": out["results"], "excluded": excluded, "source_failures": failures,
        "recorded_run": {"label": LABEL, "run_id": rid, "recorded_at": now(), "as_of_date": as_of,
                         "model": getattr(adapter, "model", adapter.name), "effort": effort, "rubric_version": rubric_version,
                         "researcher_is_fictional": True, "source": store.provenance(db),
                         "quote_check": {k: check[k] for k in ("quotes_checked", "quotes_supported", "quotes_failed")},
                         "cost_note": "estimate from reported token usage" if cost is not None else "prices not set",
                         "redactions": [],            # nothing was removed or edited; any future redaction must be listed here
                         "input_sent": {"profile": sent, "question": QUESTION, "evidence_text_of_profile": profile_text(sent),
                                        "max_judgments": max_judgments},
                         "deadline_note": (f"days_to_deadline and any 'closing soon' style flag are as of {as_of}, the day this was "
                                           "recorded. Recompute from close_date, and say so, before showing it on a later day; a "
                                           "deadline that has passed since must be shown as passed.")},
    }
    rec["recorded_run"]["integrity"] = {"results_sha256": hashlib.sha256(json.dumps(rec["results"], sort_keys=True).encode()).hexdigest(),
                                        "note": "Hash of the results exactly as produced by the pipeline; recompute to detect edits."}
    return rec


def to_js(rec: dict) -> str:
    head = ("/* RECORDED RUN. Real output of the FORGE SIGNAL pipeline for a FICTIONAL researcher against the stored public\n"
            "   Grants.gov copy. Same shape as the API response and as the sample data it replaces. Every quote was\n"
            "   re-checked against its source before this file was written (see recorded_run.quote_check). */\n")
    return head + "window.MOCK = " + json.dumps(rec, ensure_ascii=False, indent=1) + ";\n"


def integrity_checks(rec: dict) -> list:
    """Checks the project's recorded-run rules. Returns [(rule, passed)]. The script prints these and writes nothing if any fail."""
    r = rec["recorded_run"]
    h = hashlib.sha256(json.dumps(rec["results"], sort_keys=True).encode()).hexdigest()
    return [
        ("run id, model, rubric version, recording date present", all(r.get(k) for k in ("run_id", "model", "rubric_version", "as_of_date", "recorded_at"))),
        ("opportunity retrieval date present", bool(rec.get("retrieved_at"))),
        ("counters present (listed, judged, tokens, latency)", all(k in rec["counters"] for k in ("opportunities_listed", "judged", "input_tokens", "output_tokens", "latency_ms"))),
        ("redactions stated (list present; empty means none)", isinstance(r.get("redactions"), list)),
        ("input stored with it is what produced it (profile, question, limit)", bool(r.get("input_sent", {}).get("profile")) and bool(r["input_sent"].get("question"))),
        ("profile is marked fictional", "fictional" in rec["profile"]["investigator"].lower() and "fictional" in rec["profile"]["institution"].lower()),
        ("every quote found in its source", r["quote_check"]["quotes_failed"] == 0 and r["quote_check"]["quotes_checked"] == r["quote_check"]["quotes_supported"]),
        ("deadline flags carry the recording date and a stale-deadline note", bool(r.get("as_of_date")) and "recorded" in r.get("deadline_note", "")),
        ("results hash matches the results (not edited)", r["integrity"]["results_sha256"] == h),
    ]


def verify_file(text: str) -> list:
    """Re-run the checks on a written file (to detect later edits)."""
    rec = json.loads(text.split("window.MOCK = ", 1)[1].rstrip().rstrip(";"))
    return integrity_checks(rec)
