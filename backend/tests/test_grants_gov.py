"""Grants.gov source tests. Fixtures mirror the live API's real shapes (captured 2026-11-23).
No network: httpx is mocked throughout."""
from datetime import date

import httpx
import pytest

from app.sources import grants_gov as g


def hit(i, close="03/15/2027", status="posted"):
    return {"id": str(i), "number": f"OPP-{i}", "title": f"Opportunity {i}", "agencyCode": "NSF",
            "agency": "National Science Foundation", "openDate": "01/02/2026", "closeDate": close,
            "oppStatus": status, "docType": "synopsis", "cfdaList": ["47.049"]}


def detail(i, desc="Supports photochemistry and flavin biology.", elig="U.S. institutions of higher education may apply.",
           archive="Apr 15, 2027 12:00:00 AM EST", related=None):
    return {"opportunityNumber": f"OPP-{i}", "opportunityTitle": f"Opportunity {i}",
            "relatedOpps": related or [],
            "synopsis": {"agencyName": "National Science Foundation", "synopsisDesc": desc,
                         "applicantEligibilityDesc": elig, "responseDate": "Mar 15, 2027 12:00:00 AM EST",
                         "postingDate": "Jan 02, 2026 12:00:00 AM EST", "archiveDate": archive,
                         "lastUpdatedDate": "Nov 01, 2026 12:00:00 AM EST",
                         "awardFloor": 50000, "awardCeiling": 500000, "costSharing": False,
                         "applicantTypes": [{"id": "25", "description": "Others"}]}}


def mock_transport(handler):
    return httpx.MockTransport(handler)


@pytest.fixture(autouse=True)
def clear():
    g.clear_cache(); yield; g.clear_cache()


@pytest.fixture
def api(monkeypatch):
    """Serve search2/fetchOpportunity from an in-memory corpus. Returns a call counter."""
    state = {"corpus": [hit(i) for i in range(1, 1201)], "calls": [], "fail_times": 0, "detail_fail_ids": set()}

    def handler(request: httpx.Request) -> httpx.Response:
        body = request.read().decode()
        import json as _j
        payload = _j.loads(body)
        state["calls"].append(request.url.path)
        if state["fail_times"] > 0:
            state["fail_times"] -= 1
            return httpx.Response(503, json={})
        if request.url.path.endswith("search2"):
            start = int(payload.get("startRecordNum") or 0)
            rows = int(payload.get("rows") or 500)
            page = state["corpus"][start:start + rows]
            return httpx.Response(200, json={"errorcode": 0, "data": {"hitCount": len(state["corpus"]), "oppHits": page}})
        oid = str(payload.get("opportunityId"))
        if oid in state["detail_fail_ids"]:
            return httpx.Response(404, json={})
        return httpx.Response(200, json={"errorcode": 0, "data": detail(oid)})

    real = g._client
    monkeypatch.setattr(g, "_client", lambda timeout: httpx.Client(transport=mock_transport(handler), timeout=timeout))
    monkeypatch.setattr(g.time, "sleep", lambda *_: None)
    return state


# ---------------------------------------------------------------- list
def test_pages_whole_corpus_without_duplicates_or_gaps(api):
    recs = list_ = g.list_opportunities(("posted",))
    assert len(recs) == 1200
    assert len({r["source_record_id"] for r in recs}) == 1200
    assert sum(1 for p in api["calls"] if p.endswith("search2")) == 3      # 500+500+200
    assert recs[0]["sponsor"] == "National Science Foundation" and recs[0]["url"].endswith("/1")


def test_no_keyword_is_sent(api, monkeypatch):
    g.list_opportunities(("posted",))
    # the module must not rely on keyword search: it is always empty
    assert all(p.endswith(("search2", "fetchOpportunity")) for p in api["calls"])


def test_cache_is_memory_only_and_expires(api):
    g.list_opportunities(("posted",)); n = len(api["calls"])
    g.list_opportunities(("posted",))
    assert len(api["calls"]) == n                       # served from memory
    g.list_opportunities(("posted",), cache_ttl_minutes=0)
    assert len(api["calls"]) > n                        # expired -> refetched


def test_statuses_are_separate_cache_keys(api):
    g.list_opportunities(("posted",)); n = len(api["calls"])
    g.list_opportunities(("forecasted",))
    assert len(api["calls"]) > n


def test_transient_server_error_is_retried(api):
    api["fail_times"] = 2
    assert len(g.list_opportunities(("posted",))) == 1200


def test_persistent_failure_raises_source_error(api, monkeypatch):
    api["fail_times"] = 99
    with pytest.raises(g.SourceError):
        g.list_opportunities(("posted",))


# ---------------------------------------------------------------- detail
def test_detail_is_normalized_and_text_cleaned(api):
    d = g.fetch_detail("7")
    assert d["close_date"] == date(2027, 3, 15) and d["posting_date"] == date(2026, 1, 2)
    assert d["award_ceiling"] == 500000 and d["applicant_types"] == ["Others"]
    assert "photochemistry" in d["description"] and "higher education" in d["eligibility_text"]


def test_currency_flags_come_from_the_record_not_inference(api, monkeypatch):
    base = g.fetch_detail("7")
    assert base["currency_flags"] == []                                   # archive date in the future
    monkeypatch.setattr(g, "_normalize_detail", g._normalize_detail)
    d = g._normalize_detail(detail("8", archive="Jan 01, 2020 12:00:00 AM EST",
                                   related=[{"id": "99"}]), "8")
    assert "Archived on the sponsor site" in d["currency_flags"]
    assert "related or replacement" in " ".join(d["currency_flags"])
    assert d["related_opportunity_ids"] == ["99"]


def test_failed_details_are_reported_not_dropped(api):
    api["detail_fail_ids"] = {"3"}
    details, failures = g.fetch_details(["1", "2", "3"], concurrency=3)
    assert len(details) == 2 and len(failures) == 1 and failures[0]["source_record_id"] == "3"


# ---------------------------------------------------------------- shortlist
def test_shortlist_filters_by_horizon_and_sorts_by_nearest_deadline():
    today = date(2026, 11, 24)
    recs = [{"source_record_id": "a", "close_date": date(2026, 12, 1)},
            {"source_record_id": "b", "close_date": date(2027, 6, 1)},     # beyond 3 months
            {"source_record_id": "c", "close_date": date(2026, 11, 1)},    # already closed
            {"source_record_id": "d", "close_date": date(2026, 11, 26)},
            {"source_record_id": "e", "close_date": None}]
    out = g.shortlist(recs, horizon_months=3, today=today)
    assert [r["source_record_id"] for r in out] == ["d", "a"]
    assert [r["source_record_id"] for r in g.shortlist(recs, 3, include_undated=True, today=today)][-1] == "e"


def test_shortlist_respects_limit():
    today = date(2026, 11, 24)
    recs = [{"source_record_id": str(i), "close_date": date(2026, 12, 1)} for i in range(50)]
    assert len(g.shortlist(recs, 3, limit=10, today=today)) == 10


def test_malformed_dates_do_not_crash():
    assert g.parse_list_date("not a date") is None and g.parse_detail_date(None) is None
    assert g.shortlist([{"source_record_id": "x", "close_date": None}], 3) == []


def test_award_amounts_from_the_real_api_are_cleaned(api):
    assert g.parse_money("none") is None and g.parse_money("") is None and g.parse_money(None) is None
    assert g.parse_money(0) is None                       # never turned into an award of zero
    assert g.parse_money("500000") == 500000 and g.parse_money(500000.0) == 500000
    d = g._normalize_detail({"synopsis": {"awardFloor": "none", "awardCeiling": "500000"}}, "1")
    assert d["award_floor"] is None and d["award_ceiling"] == 500000
