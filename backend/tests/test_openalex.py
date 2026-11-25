"""OpenAlex lookup with a fake HTTP client: no test touches the network."""
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.sources import openalex as oa


def author(i, name="Pat Example", works=40, insts=("Example University",), topics=("Plant Photobiology", "Flavoproteins"),
           years=((2022, 3), (2025, 2)), affs=()):
    return {"id": f"https://openalex.org/A{i}", "display_name": name, "works_count": works, "cited_by_count": 900,
            "last_known_institutions": [{"display_name": x} for x in insts],
            "affiliations": [{"institution": {"display_name": x}} for x in affs],
            "topics": [{"display_name": t} for t in topics],
            "counts_by_year": [{"year": y, "works_count": n} for y, n in years]}


def work(i, topics, kws=()):
    return {"id": f"https://openalex.org/W{i}", "title": f"Paper {i}", "publication_year": 2024, "doi": f"https://doi.org/10.1/{i}",
            "topics": [{"display_name": t} for t in topics], "keywords": [{"display_name": k} for k in kws]}


WORKS = {"results": [work(1, ["Plant Photobiology", "Science"], ["blue light"]), work(2, ["Plant Photobiology"]),
                     work(3, ["Flavoproteins"], ["blue light"])]}


class Resp:
    def __init__(self, data, code=200): self.data, self.status_code = data, code
    def json(self):
        if self.data is None: raise ValueError("bad json")
        return self.data


class FakeClient:
    def __init__(self, authors=None, code=200, works=WORKS, exc=None):
        self.calls, self.code, self.exc, self.works = [], code, exc, works
        self.authors = authors if authors is not None else {"results": [author(111111), author(222222, works=2, insts=(), affs=("Other College",), years=())]}
    def get(self, url, params=None):
        self.calls.append((url, params))
        if self.exc: raise self.exc
        return Resp(self.authors if url.endswith("/authors") else self.works, self.code)


def lookup(**kw): return oa.Lookup(client=FakeClient(**kw))


def test_search_returns_rich_candidates_and_flags_same_name_records():
    r = lookup().search("Pat Example")
    c = r["candidates"]
    assert [x["openalex_id"] for x in c] == ["A111111", "A222222"] and r["status"] == "ambiguous" and "not merged" in r["note"]
    assert c[0]["institutions"] == ["Example University"] and c[1]["institutions"] == ["Other College"]
    assert c[0]["last_active_year"] == 2025 and c[1]["last_active_year"] is None and c[0]["works_count"] == 40


def test_no_match_is_said_plainly():
    r = lookup(authors={"results": []}).search("Zzzz Qqqq")
    assert r["status"] == "no_match" and r["candidates"] == [] and "no researcher matching" in r["note"]


def test_researcher_with_very_few_works():
    r = lookup(authors={"results": [author(333333, works=1, years=((2025, 1),))]}).search("New Student")
    assert r["status"] == "single" and r["candidates"][0]["works_count"] == 1
    e = lookup(works={"results": []}).expertise("A333333")
    assert e["status"] == "no_works" and e["terms"] == [] and "No works" in e["note"]
    e = lookup(works={"results": [work(9, ["Soil Chemistry"])]}).expertise("A333333")
    assert [t["term"] for t in e["terms"]] == ["Soil Chemistry"] and e["terms"][0]["proposed"] is True


@pytest.mark.parametrize("name", ["李明", "Müller-Ñandú", "Ольга Иванова", "محمد علي", "O'Brien, Seán"])
def test_non_english_names_are_accepted_and_sent_intact(name):
    fc = FakeClient(); oa.Lookup(client=fc).search(name)
    assert fc.calls[0][1]["search"] == name


def test_name_cleaning_and_limits():
    assert oa.clean_name("  Pat \x00\x07 Example​ \n ") == "Pat Example"
    with pytest.raises(oa.OpenAlexError) as e: oa.clean_name("a")
    assert e.value.code == "name_too_short"
    with pytest.raises(oa.OpenAlexError) as e: oa.clean_name("x" * 121)
    assert e.value.code == "name_too_long"
    assert oa.clean_name("李明") == "李明"                      # two-character names are real names in some scripts


def test_expertise_terms_carry_their_source_works_and_skip_generic_terms():
    e = lookup().expertise("A111111")
    terms = {t["term"]: t for t in e["terms"]}
    assert e["works_considered"] == 3 and "Science" not in terms
    assert terms["Plant Photobiology"]["work_count"] == 2 and terms["blue light"]["work_count"] == 2
    assert terms["Plant Photobiology"]["works"][0]["url"].startswith("https://doi.org/")


def test_requests_send_no_personal_details_and_a_generic_agent():
    fc = FakeClient(); lk = oa.Lookup(client=fc); lk.search("Pat Example"); lk.expertise("A111111")
    blob = str(fc.calls).lower()
    assert "mailto" not in blob and "@" not in blob and oa.USER_AGENT == "forge-signal"


@pytest.mark.parametrize("bad", ["", "A1", "A111111; DROP", "../x", "W123456"])
def test_bad_author_ids_are_refused_before_any_request(bad):
    fc = FakeClient()
    with pytest.raises(oa.OpenAlexError) as e: oa.Lookup(client=fc).expertise(bad)
    assert e.value.code == "bad_author_id" and fc.calls == []


@pytest.mark.parametrize("kw,code,status", [
    (dict(code=429), "upstream_rate_limited", 503), (dict(code=500), "upstream_unavailable", 502),
    (dict(exc=httpx.ReadTimeout("slow")), "upstream_timeout", 504), (dict(exc=httpx.ConnectError("down")), "upstream_unavailable", 502),
    (dict(authors=None, code=200, works=None), None, None)])
def test_each_upstream_failure_has_its_own_code_and_text(kw, code, status):
    if code is None:                                                     # unreadable JSON
        class Bad(FakeClient):
            def get(self, url, params=None): return Resp(None)
        with pytest.raises(oa.OpenAlexError) as e: oa.Lookup(client=Bad()).search("Pat Example")
        assert e.value.code == "upstream_bad_response"; return
    with pytest.raises(oa.OpenAlexError) as e: lookup(**kw).search("Pat Example")
    assert (e.value.code, e.value.status) == (code, status) and e.value.message == oa.ERRORS[code][1]


def test_answers_are_cached_briefly_and_only_real_calls_are_logged():
    fc, log = FakeClient(), []
    lk = oa.Lookup(client=fc, log=lambda *a: log.append(a), ttl_s=600)
    lk.search("Pat Example"); lk.search("Pat Example")
    assert len(fc.calls) == 1 and len(log) == 1
    lk2 = oa.Lookup(client=fc, ttl_s=0); lk2.search("Pat Example"); lk2.search("Pat Example")
    assert len(fc.calls) == 3


@pytest.fixture
def api():
    return TestClient(create_app(":memory:", lister=lambda *a, **k: [], detailer=lambda *a, **k: ([], []), openalex_client=FakeClient()))


def test_endpoints_and_call_log_keep_the_name_out(api):
    name = "Pat Example"
    r = api.post("/api/pi/search", json={"name": name}); assert r.status_code == 200 and r.json()["status"] == "ambiguous"
    assert api.get("/api/pi/search", params={"name": name}).status_code in (404, 405, 422)   # no name in a URL
    e = api.get("/api/pi/A111111/expertise"); assert e.status_code == 200 and e.json()["terms"]
    rows = api.app.state.db.q("SELECT source, endpoint, params, ok, http_status, latency_ms FROM api_calls WHERE source='OpenAlex'")
    assert len(rows) == 2 and all(r["ok"] == 1 and r["http_status"] == 200 for r in rows)
    logged = " ".join(str(dict(r)) for r in rows).lower()
    assert "pat" not in logged and "example" not in logged and "name_length" in logged and "name_sha256_16" in logged


def test_error_bodies_carry_code_and_message(api):
    r = api.post("/api/pi/search", json={"name": "a"})
    assert r.status_code == 400 and r.json()["detail"] == {"code": "name_too_short", "message": oa.ERRORS["name_too_short"][1]}
    r = api.get("/api/pi/not-an-id/expertise"); assert r.status_code == 400 and r.json()["detail"]["code"] == "bad_author_id"
    assert api.post("/api/pi/search", json={"name": "x" * 600}).status_code == 422


def test_hourly_and_daily_limits(api):
    db = api.app.state.db; db.set_setting("pi_lookups_per_hour", 2)
    codes = [api.post("/api/pi/search", json={"name": "Pat Example"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
    assert api.post("/api/pi/search", json={"name": "Pat Example"}).json()["detail"]["code"] == "hourly_limit"
    db.set_setting("pi_lookups_per_hour", 100); db.set_setting("pi_lookups_per_day", 2)
    assert api.post("/api/pi/search", json={"name": "Pat Example"}).json()["detail"]["code"] == "daily_limit"


def test_invalid_names_do_not_use_up_the_limit(api):
    api.app.state.db.set_setting("pi_lookups_per_hour", 1)
    for _ in range(3): assert api.post("/api/pi/search", json={"name": "a"}).status_code == 400
    assert api.post("/api/pi/search", json={"name": "Pat Example"}).status_code == 200
