"""One run, end to end (PRD FR-1 to FR-12): live pull -> shortlist -> screen -> cited judgment.

Division of labour, per the hard rules:
  * plain code  : paging, dates, the deadline window, the prefilter, the tier calculation
  * the model   : factor values and eligibility, each with an exact quote
  * the validator: rejects any quote not found in its source
Nothing about an opportunity is stored outside the run log.
"""
import re
import time
from concurrent.futures import ThreadPoolExecutor

from . import rubric as R
from .adapters.base import judge_fit
from .schemas import SchemaError
from .sources import grants_gov as gg
from .validator import validate_factors

STOP = set("a an and are as at be by for from in into of on or that the their to with within using use via "
           "data new based study research approach approaches method methods program programs project projects "
           "support supports supporting include includes including section sec will may must".split())


def terms(texts) -> set:
    """Crude stem set, used ONLY to rank which opportunities are worth paying to screen.
    It is a cost control, never a fit judgment: the tier comes from the rubric."""
    out = set()
    for w in re.sub(r"[^a-z0-9 ]", " ", " ".join(texts).lower()).split():
        if len(w) >= 4 and w not in STOP:
            out.add(re.sub(r"(ing|ed|ies|es|s|ion|al|ity)$", "", w))
    return out


def profile_text(profile: dict) -> str:
    """The researcher evidence the model must quote. Supplied per run; never stored (hard rule 1)."""
    parts = []
    if profile.get("career_stage"):
        parts.append(f"Career stage: {profile['career_stage']}.")
    if profile.get("lanes"):
        parts.append("Established research areas: " + "; ".join(profile["lanes"]) + ".")
    for rule in profile.get("positioning_rules") or []:
        parts.append(f"Positioning rule: {rule}")
    return "\n".join(parts)


def rank_candidates(details, profile, limit):
    """Order by shared terms with the profile, then by nearest deadline. Returns (ranked, skipped)."""
    pt = terms([profile_text(profile)])
    scored = []
    for d in details:
        shared = pt & terms([d.get("title", ""), d.get("description", "")])
        scored.append((-len(shared), d.get("close_date") or gg.date.max, d.get("source_record_id", ""), d, sorted(shared)))
    scored.sort(key=lambda x: (x[0], x[1], x[2]))
    ranked = [(d, sh) for _, _, _, d, sh in scored[:limit]]
    return ranked, max(0, len(details) - len(ranked))


def run_match(db, run_id, adapter, settings, profile, question, lister=None, detailer=None) -> dict:
    """Execute one run. Source and model failures are recorded, never silently dropped."""
    lister = lister or gg.list_opportunities
    detailer = detailer or gg.fetch_details
    t0 = time.time()
    rubric = db.published_rubric() or R.load(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "rubrics", "default.json"))

    statuses = tuple(settings.get("opportunity_statuses") or ("posted",))
    listed = lister(statuses, timeout=settings["source_timeout_s"], cache_ttl_minutes=settings["cache_ttl_minutes"])
    short = gg.shortlist(listed, horizon_months=settings["horizon_months"],
                         include_undated=settings["include_undated_deadlines"],
                         limit=settings["max_detail_fetches"])
    details, failures = detailer([r["source_record_id"] for r in short],
                                 timeout=settings["source_timeout_s"], concurrency=settings["source_concurrency"])
    source_status = {r["source_record_id"]: r.get("status") for r in short}
    list_sponsor = {r["source_record_id"]: (r.get("sponsor") or "").strip() for r in short}
    for d in details:
        d.setdefault("source_status", source_status.get(d.get("source_record_id")))
        # The search list names the agency. The detail record's agency field is sometimes a contact person's
        # name or empty, so the list's name wins and the detail's is only the fallback.
        d["sponsor"] = list_sponsor.get(d.get("source_record_id")) or d.get("sponsor", "")
    for f in failures:
        db.add_source_failure(run_id, f.get("source_record_id", ""), f.get("error", ""))

    ranked, skipped = rank_candidates(details, profile, settings["max_judgments"])
    prof_text = profile_text(profile)
    results = []
    prepared = []
    t_start_judging = time.time()
    for d, shared in ranked:
        opp_id = d["url"]
        sources = {opp_id: "\n\n".join(x for x in (d.get("description"), d.get("eligibility_text")) if x),
                   "researcher-profile": prof_text}
        db.add_source(run_id, opp_id, d["url"], R.version({"t": sources[opp_id]}))
        prepared.append((d, shared, opp_id, sources))

    # Model calls run in a bounded thread pool; the database is only touched from this thread, in ranked order,
    # so the log and the result order do not depend on which call finishes first.
    def call(item):
        try:
            return judge_fit(adapter, item[3], question, rubric), None
        except SchemaError as e:
            return None, f"model output invalid: {e}"
        except Exception as e:                       # rate limit after retries, timeout, refusal: never a key in the text
            return None, f"model call failed: {type(e).__name__}"

    workers = max(1, min(int(settings.get("judge_concurrency") or 1), 16, len(prepared) or 1))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        outcomes = list(pool.map(call, prepared))
    t_judged = time.time()
    model_failures = 0
    for (d, shared, opp_id, sources), (fj, err) in zip(prepared, outcomes):
        if err:
            model_failures += 1
            db.add_source_failure(run_id, opp_id, err)
            continue
        checked = validate_factors(fj, sources, rubric)
        tier = R.evaluate(rubric, checked["factors"])
        for name, cites in checked["factor_citations"].items():
            for c in cites:
                db.add_citation(run_id, c.source_id, c.quote, True, f"factor:{name}")
        for c in checked["eligibility_citations"]:
            db.add_citation(run_id, c.source_id, c.quote, True, "eligibility")
        for f in checked["failed_citations"]:
            db.add_citation(run_id, f["source_id"], f["quote"], False, "quote not found in source")
        row = {
            "title": d["title"], "sponsor": d["sponsor"], "number": d["number"], "url": d["url"],
            "close_date": d["close_date"].isoformat() if d.get("close_date") else None,
            "source_status": d.get("source_status"),
            "cost_sharing": d.get("cost_sharing"),
            "days_to_deadline": gg.days_until(d.get("close_date")),
            "award_floor": d.get("award_floor"), "award_ceiling": d.get("award_ceiling"),
            "currency_flags": d.get("currency_flags", []),
            "related_opportunity_ids": d.get("related_opportunity_ids", []),
            "tier": tier.tier, "fit": tier.word, "eligibility": checked["eligibility"],
            "rationale": checked["rationale"],
            "how_calculated": {"factors": checked["factors"], "rules_fired": tier.rule_ids,
                               "reasons": tier.rules, "adjustments": checked["adjustments"]},
            "citations": [{"source_id": c.source_id, "quote": c.quote, "for": name}
                          for name, cs in checked["factor_citations"].items() for c in cs]
                         + [{"source_id": c.source_id, "quote": c.quote, "for": "eligibility"}
                            for c in checked["eligibility_citations"]],
            "failed_citation_count": len(checked["failed_citations"]),
            "prefilter_shared_terms": shared,
        }
        if tier.word is not None:                      # Excluded stays in the log, not in results
            results.append(row)
        db.add_match(run_id, row)
    results.sort(key=lambda r: ({"High": 0, "Medium": 1, "Low": 2}.get(r["fit"], 3),
                                r["days_to_deadline"] if r["days_to_deadline"] is not None else 10 ** 6))
    return {"results": results, "counters": {
        "opportunities_listed": len(listed), "in_horizon": len(short), "details_fetched": len(details),
        "judged": len(ranked) - model_failures, "model_failures": model_failures, "not_judged_due_to_cap": skipped, "source_failures": len(failures),
        "latency_ms": int((time.time() - t0) * 1000),
        "judging_ms": int((t_judged - t_start_judging) * 1000), "judge_concurrency": workers,
        "input_tokens": adapter.total_usage.get("input_tokens", 0),
        "output_tokens": adapter.total_usage.get("output_tokens", 0)}}
