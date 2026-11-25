"""Record ONE real run for the public pages.

The public pages show a fictional sample (public/signal/mock-data.js). A recorded run replaces it with what the real
pipeline produced for a FICTIONAL researcher against the stored public Grants.gov copy, labelled as a recording, so the
pages can show real behaviour without any visitor spending model money.

Nothing here invents content: results, counters, tokens and timings come from `run_match`. Before anything is written,
every quote is checked again, independently of the pipeline, against the stored source text it claims to come from.
Public Grants.gov data only; the researcher is fictional.
"""
import json
import time

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
    rid = db.create_run("recorded-run", "keywords", "recorded run (fictional researcher)", s, "recorded", adapter.name)
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
    return {
        "profile": {k: profile[k] for k in ("investigator", "institution", "career_stage", "lanes", "positioning_rules")},
        "settings": {"horizon_months": s["horizon_months"], "lead_time_days": s["lead_time_days"],
                     "funder_types": s["funder_types"], "min_fit": s["min_fit"], "scope_level": s["scope_level"],
                     "max_judgments": max_judgments},
        "retrieved_at": store.as_of(db),
        "counters": c, "results": out["results"], "excluded": excluded, "source_failures": failures,
        "recorded_run": {"label": LABEL, "recorded_at": now(), "model": getattr(adapter, "model", adapter.name),
                         "effort": effort, "researcher_is_fictional": True, "source": store.provenance(db),
                         "quote_check": {k: check[k] for k in ("quotes_checked", "quotes_supported", "quotes_failed")},
                         "cost_note": "estimate from reported token usage" if cost is not None else "prices not set"},
    }


def to_js(rec: dict) -> str:
    head = ("/* RECORDED RUN. Real output of the FORGE SIGNAL pipeline for a FICTIONAL researcher against the stored public\n"
            "   Grants.gov copy. Same shape as the API response and as the sample data it replaces. Every quote was\n"
            "   re-checked against its source before this file was written (see recorded_run.quote_check). */\n")
    return head + "window.MOCK = " + json.dumps(rec, ensure_ascii=False, indent=1) + ";\n"
