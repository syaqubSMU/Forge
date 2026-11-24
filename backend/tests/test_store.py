from datetime import date, timedelta

from fastapi.testclient import TestClient

from app import store
from app.db import Database
from app.main import create_app
from app.sources import grants_gov as gg

TODAY = date.today()


def rec(i, days, status="posted"):
    return {"source_system": "Grants.gov", "source_record_id": str(i), "number": f"N-{i}", "title": f"Title {i}",
            "sponsor": "Agency", "agency_code": "AG", "status": status, "open_date": TODAY - timedelta(days=5),
            "close_date": TODAY + timedelta(days=days) if days is not None else None, "cfda": [],
            "url": f"https://www.grants.gov/search-results-detail/{i}"}


def det(r, **kw):
    d = {"source_record_id": r["source_record_id"], "number": r["number"], "title": r["title"], "sponsor": "Agency",
         "description": f"Photochemistry program {r['source_record_id']}.", "eligibility_text": "Universities may apply.",
         "applicant_types": [], "close_date": r["close_date"], "posting_date": TODAY, "archive_date": None, "last_updated": TODAY,
         "award_floor": None, "award_ceiling": 5000, "cost_sharing": None, "related_opportunity_ids": [], "currency_flags": [],
         "url": r["url"]}
    d.update(kw); return d


def fakes(records, calls=None):
    def lister(statuses, timeout=30, cache_ttl_minutes=0, **_):
        if gg.call_hook: gg.call_hook("search2", {"rows": 500}, True, 200, 12, None)
        return [r for r in records if r["status"] in statuses]

    def detailer(ids, timeout=30, concurrency=8, **_):
        if calls is not None: calls.extend(ids)
        out = []
        for i in ids:
            r = next(x for x in records if x["source_record_id"] == i)
            if gg.call_hook: gg.call_hook("fetchOpportunity", {"opportunityId": int(i)}, True, 200, 5, None)
            out.append(det(r))
        return out, []
    return lister, detailer


def test_ingest_stores_records_text_and_logs_every_call():
    db = Database(":memory:")
    recs = [rec(1, 10), rec(2, 40), rec(3, None), rec(4, 900), rec(5, 20, "forecasted")]
    lister, detailer = fakes(recs)
    out = store.ingest(db, lister=lister, detailer=detailer)
    assert out["listed"] == 5 and out["details_failed"] == 0
    st = store.status(db)
    assert st["opportunities"] == 5 and st["with_full_text"] == out["details_stored"]
    by = {c["endpoint"]: c for c in st["api_calls"]}
    assert by["search2"]["n"] == 1 and by["fetchOpportunity"]["n"] == out["details_stored"]
    assert gg.call_hook is None                      # the hook is always cleared


def test_second_ingest_only_refetches_records_in_the_window():
    db = Database(":memory:")
    recs = [rec(1, 10), rec(2, 700)]
    calls = []
    lister, detailer = fakes(recs, calls)
    store.ingest(db, lister=lister, detailer=detailer)
    assert sorted(calls) == ["1", "2"]               # first time: everything lacks text
    calls.clear()
    store.ingest(db, lister=lister, detailer=detailer)
    assert calls == ["1"]                            # later: only what closes inside 12 months


def test_stored_sources_round_trip_dates_and_recompute_currency_flags():
    db = Database(":memory:")
    recs = [rec(1, 10)]
    lister, detailer = fakes(recs)
    store.ingest(db, lister=lister, detailer=detailer)
    sl, sd = store.stored_lister(db), store.stored_detailer(db)
    listed = sl(("posted",))
    assert listed[0]["close_date"] == TODAY + timedelta(days=10)
    d, failed = sd(["1", "999"])
    assert d[0]["close_date"] == TODAY + timedelta(days=10) and d[0]["description"].startswith("Photochemistry")
    assert d[0]["retrieved_at"] and failed[0]["source_record_id"] == "999"
    # an archive date that has passed since ingest is flagged now, not at ingest time
    db.q("UPDATE opportunities SET detail=? WHERE source_record_id='1'",
         (__import__("json").dumps({**__import__("json").loads(db.q("SELECT detail FROM opportunities", one=True)["detail"]),
                                    "archive_date": (TODAY - timedelta(days=1)).isoformat()}),), write=True)
    d, _ = sd(["1"])
    assert "Archived on the sponsor site" in d[0]["currency_flags"]


def test_sources_fall_back_to_live_until_the_store_has_text():
    db = Database(":memory:")
    live = []
    lister, detailer = store.sources(db, live_lister=lambda *a, **k: live.append("list") or [],
                                     live_detailer=lambda *a, **k: live.append("detail") or ([], []))
    lister(("posted",)); detailer(["1"])
    assert live == ["list", "detail"]
    fl, fd = fakes([rec(1, 10)])
    store.ingest(db, lister=fl, detailer=fd)
    live.clear(); lister(("posted",)); detailer(["1"])
    assert live == []                                # now served from the store


def test_admin_ingest_endpoints_need_the_token(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "tok")
    c = TestClient(create_app(":memory:"))
    for method, url in (("post", "/api/admin/ingest"), ("get", "/api/admin/ingest/status"), ("get", "/api/admin/api-calls")):
        assert getattr(c, method)(url).status_code == 401
    r = c.get("/api/admin/ingest/status", headers={"x-admin-token": "tok"})
    assert r.status_code == 200 and r.json()["opportunities"] == 0
