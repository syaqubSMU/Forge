"""Live-pull pipeline. Source functions are injected fakes: no test touches the network."""
import json
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.adapters import registry
from app.adapters.mock import MockAdapter
from app.main import create_app

H = {"X-Admin-Token": "secret-token"}
TODAY = date.today()


def opp(i, days=30, title="Photoreceptor mechanisms in plants",
        desc="This program supports photochemistry and flavin biology in plant systems.",
        elig="Accredited U.S. institutions of higher education may apply.", flags=None, related=None):
    return {"source_system": "Grants.gov", "source_record_id": str(i), "number": f"OPP-{i}", "title": title,
            "sponsor": "National Science Foundation", "agency_code": "NSF", "status": "posted",
            "open_date": TODAY, "close_date": TODAY + timedelta(days=days), "cfda": [],
            "url": f"https://www.grants.gov/search-results-detail/{i}",
            "description": desc, "eligibility_text": elig, "applicant_types": ["Others"],
            "posting_date": TODAY, "archive_date": None, "last_updated": TODAY,
            "award_floor": 1000, "award_ceiling": 500000, "cost_sharing": False,
            "related_opportunity_ids": related or [], "currency_flags": flags or []}


CORPUS = [
    opp(1, days=30),
    opp(2, days=10, title="Battery materials discovery", desc="Supports energy storage characterization.",
        elig="Universities and national laboratories may apply."),
    opp(3, days=400),                                   # beyond the horizon
    opp(4, days=-5),                                    # already closed
]


def factors_json(centrality="central", repositioning="none", lead="yes", elig="Eligible",
                 quote="supports photochemistry and flavin biology", src="https://www.grants.gov/search-results-detail/1",
                 elig_quote="Accredited U.S. institutions of higher education may apply."):
    return json.dumps({
        "factors": {
            "centrality": {"value": centrality, "citations": [{"quote": quote, "source_id": src}]},
            "repositioning": {"value": repositioning, "citations": [{"quote": quote, "source_id": src}]},
            "pi_can_lead": {"value": lead, "citations": [{"quote": "Established research areas", "source_id": "researcher-profile"}]},
            "career_stage_excluded": {"value": "no", "citations": []},
            "positioning_violation": {"value": "no", "citations": []}},
        "eligibility": elig,
        "eligibility_citations": [{"quote": elig_quote, "source_id": src}] if elig_quote else [],
        "rationale": "Topic matches the stated research areas."})


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: MockAdapter([factors_json()]))
    calls = {"list": 0, "detail": 0}

    def lister(statuses, timeout=30.0, cache_ttl_minutes=15):
        calls["list"] += 1
        return [dict(o) for o in CORPUS]

    def detailer(ids, timeout=30.0, concurrency=8):
        calls["detail"] += 1
        ids = [str(i) for i in ids]
        return [dict(o) for o in CORPUS if o["source_record_id"] in ids], []

    app = create_app(":memory:", lister=lister, detailer=detailer)
    c = TestClient(app); c.calls = calls
    return c


def live(c, **kw):
    body = {"input_type": "pi_name", "input_text": "Dr. Sample A",
            "profile": {"career_stage": "established", "lanes": ["photochemistry and flavin biology"]}}
    body.update(kw)
    return c.post("/api/runs", json=body)


def test_live_run_returns_cited_results_within_the_horizon(client):
    r = live(client); assert r.status_code == 200, r.text
    j = r.json()
    ids = [x["url"].rsplit("/", 1)[-1] for x in j["results"]]
    assert "3" not in ids and "4" not in ids           # horizon and closed filtered in code
    assert j["counters"]["opportunities_listed"] == 4 and j["counters"]["in_horizon"] == 2
    top = j["results"][0]
    assert top["fit"] == "High" and top["tier"] == "Direct" and top["citations"]
    assert top["how_calculated"]["rules_fired"] == ["R5"]
    assert "retrieved_at" in j and "logged" in j["notice"]


def test_fit_comes_from_the_rubric_not_the_model(client, monkeypatch):
    monkeypatch.setitem(registry.PROVIDERS, "mock",
                        lambda: MockAdapter([factors_json(centrality="adjacent")]))
    top = live(client).json()["results"][0]
    assert top["tier"] == "Conditional" and top["fit"] == "Low"
    assert any("adjacent" in x for x in top["how_calculated"]["reasons"])


def test_unsupported_quote_falls_back_to_the_conservative_value(client, monkeypatch):
    monkeypatch.setitem(registry.PROVIDERS, "mock",
                        lambda: MockAdapter([factors_json(quote="this sentence is not in any source")]))
    j = live(client).json()
    assert j["results"] == []                           # centrality -> none -> Excluded -> hidden
    rid = j["run_id"]
    detail = client.get(f"/api/admin/runs/{rid}", headers=H).json()
    assert any(c["validated"] == 0 for c in detail["citations"])
    logged = detail["matches"][0]
    assert logged["tier"] == "Excluded"
    assert any("conservative value" in a for a in logged["how_calculated"]["adjustments"])


def test_eligibility_without_a_supported_quote_stays_needs_verification(client, monkeypatch):
    monkeypatch.setitem(registry.PROVIDERS, "mock",
                        lambda: MockAdapter([factors_json(elig="Eligible", elig_quote=None)]))
    assert live(client).json()["results"][0]["eligibility"] == "Needs verification"


def test_invalid_model_output_skips_that_opportunity_and_is_logged(client, monkeypatch):
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: MockAdapter(["not json"]))
    j = live(client).json()
    assert j["results"] == []
    failures = client.get(f"/api/admin/runs/{j['run_id']}", headers=H).json()["source_failures"]
    assert any("model output invalid" in f["error"] for f in failures)


def test_judgment_cap_is_respected_and_reported(client):
    client.put("/api/admin/settings", json={"max_judgments": 1}, headers=H)
    both = {"career_stage": "established", "lanes": ["photochemistry and flavin biology", "battery energy storage"]}
    c = live(client, profile=both).json()["counters"]
    assert c["judged"] == 1 and c["not_judged_due_to_cap"] == 1


def test_records_sharing_no_term_with_the_research_areas_are_not_sent_to_the_model(client):
    c = live(client).json()["counters"]                 # the battery record shares nothing with this profile
    assert c["judged"] == 1 and c["no_term_overlap"] == 1 and c["not_judged_due_to_cap"] == 0


def test_run_log_records_sources_tokens_and_counters(client):
    rid = live(client).json()["run_id"]
    d = client.get(f"/api/admin/runs/{rid}", headers=H).json()
    assert d["opportunities_listed"] == 4 and d["details_fetched"] == 2
    assert d["input_tokens"] > 0 and d["output_tokens"] > 0
    assert {s["url"] for s in d["sources"]} and all(s["retrieved_at"] for s in d["sources"])


def test_currency_flags_reach_the_result(client, monkeypatch):
    flagged = [dict(o) for o in CORPUS]
    flagged[0] = opp(1, days=30, flags=["Archived on the sponsor site"], related=["99"])
    app = create_app(":memory:", lister=lambda *a, **k: flagged,
                     detailer=lambda ids, **k: ([o for o in flagged if o["source_record_id"] in [str(i) for i in ids]], []))
    c = TestClient(app)
    top = [r for r in live(c).json()["results"] if r["url"].endswith("/1")][0]
    assert "Archived on the sponsor site" in top["currency_flags"] and top["related_opportunity_ids"] == ["99"]


def test_source_outage_is_reported_not_faked(client):
    from app.sources.grants_gov import SourceError
    app = create_app(":memory:", lister=lambda *a, **k: (_ for _ in ()).throw(SourceError("search2: HTTP 503")),
                     detailer=lambda ids, **k: ([], []))
    r = live(TestClient(app))
    assert r.status_code == 503 and "could not be read" in r.json()["detail"]


# ---------------------------------------------------------------- calendar endpoints (FR-12, FR-13)
def test_calendar_json_groups_and_computes_internal_deadlines(client):
    rid = live(client).json()["run_id"]
    cal = client.get(f"/api/runs/{rid}/calendar").json()
    assert cal["lead_days"] == 14
    fixed = cal["groups"]["Fixed"]
    assert fixed and all(r["internal_deadline"] for r in fixed)
    from datetime import date as _d, timedelta as _t
    for r in fixed:
        assert _d.fromisoformat(r["internal_deadline"]) == _d.fromisoformat(r["close_date"]) - _t(days=14)
    assert all("how_calculated" not in r for r in fixed)      # evidence stays on the results page


def test_calendar_downloads_are_real_files(client):
    rid = live(client).json()["run_id"]
    ics = client.get(f"/api/runs/{rid}/calendar.ics")
    assert ics.status_code == 200 and ics.content.startswith(b"BEGIN:VCALENDAR")
    assert "attachment" in ics.headers["content-disposition"] and ics.headers["content-disposition"].endswith('.ics"')
    xl = client.get(f"/api/runs/{rid}/calendar.xlsx")
    assert xl.status_code == 200 and xl.content[:2] == b"PK"   # a real zip-based workbook
    import io, openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(xl.content))
    assert "Fixed deadlines" in wb.sheetnames


def test_calendar_is_scoped_to_the_visitor_who_ran_it(client):
    live(client)
    assert client.get("/api/runs/does-not-exist/calendar").status_code == 404
    assert client.get("/api/runs/does-not-exist/calendar.ics").status_code == 404


def test_lead_time_setting_changes_the_internal_deadline(client):
    client.put("/api/admin/settings", json={"lead_time_days": 30}, headers=H)
    rid = live(client).json()["run_id"]
    cal = client.get(f"/api/runs/{rid}/calendar").json()
    from datetime import date as _d, timedelta as _t
    r = cal["groups"]["Fixed"][0]
    assert _d.fromisoformat(r["internal_deadline"]) == _d.fromisoformat(r["close_date"]) - _t(days=30)


# ---------------------------------------------------------------- pages wired to the API
def test_per_run_options_change_this_run_only(client):
    a = live(client, options={"horizon_months": 14, "lead_time_days": 30}).json()
    assert a["counters"]["in_horizon"] == 3            # the 400-day opportunity is inside 14 months
    cal = client.get(f"/api/runs/{a['run_id']}/calendar").json()
    assert cal["lead_days"] == 30                      # lead time travels with the run
    b = live(client).json()                            # the next run is back to the saved settings
    assert b["counters"]["in_horizon"] == 2
    assert client.get(f"/api/runs/{b['run_id']}/calendar").json()["lead_days"] == 14


@pytest.mark.parametrize("bad", [{"daily_cap": 9999}, {"rate_limit_per_hour": 9999}, {"horizon_months": 0},
                                 {"horizon_months": 99}, {"horizon_months": True}, {"lead_time_days": -1},
                                 {"lead_time_days": 2.5}])
def test_options_cannot_override_limits_or_go_out_of_range(client, bad):
    assert live(client, options=bad).status_code == 400


def test_every_run_says_where_its_data_came_from(client):
    src = live(client).json()["source"]
    assert src["system"] == "Grants.gov" and "public" in src["api"] and src["mode"] == "live pull"


def test_config_js_tells_the_pages_the_api_is_live(client):
    r = client.get("/config.js")
    assert r.status_code == 200 and "live: true" in r.text and r.headers["cache-control"] == "no-store"


def test_pages_are_served_and_the_api_still_wins(client):
    assert client.get("/api/health").json()["status"] == "ok"
    home = client.get("/")
    assert home.status_code == 200 and "FORGE" in home.text
    assert client.get("/results.html").status_code == 200


def test_sponsor_comes_from_the_search_list_not_a_contact_name_in_the_detail(monkeypatch):
    """Grants.gov detail records sometimes carry a contact person (or nothing) in the agency field."""
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: MockAdapter([factors_json()]))
    lister = lambda statuses, timeout=30.0, cache_ttl_minutes=15: [dict(CORPUS[0])]
    detailer = lambda ids, timeout=30.0, concurrency=8: ([{**CORPUS[0], "sponsor": "Mary A Johnson\nContract Specialist"}], [])
    c = TestClient(create_app(":memory:", lister=lister, detailer=detailer))
    assert live(c).json()["results"][0]["sponsor"] == "National Science Foundation"
    detailer2 = lambda ids, timeout=30.0, concurrency=8: ([{**CORPUS[0], "sponsor": "From The Detail"}], [])
    lister2 = lambda statuses, timeout=30.0, cache_ttl_minutes=15: [{**CORPUS[0], "sponsor": ""}]
    c2 = TestClient(create_app(":memory:", lister=lister2, detailer=detailer2))
    assert live(c2).json()["results"][0]["sponsor"] == "From The Detail"       # fallback when the list has none
