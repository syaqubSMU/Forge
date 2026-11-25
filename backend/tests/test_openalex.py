"""OpenAlex lookup with a fake HTTP client: no test touches the network."""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.sources import openalex as oa

AUTHORS = {"results": [
    {"id": "https://openalex.org/A111111", "display_name": "Pat Example", "works_count": 40, "cited_by_count": 900,
     "last_known_institutions": [{"display_name": "Example University"}], "affiliations": [],
     "topics": [{"display_name": "Plant Photobiology"}, {"display_name": "Flavoproteins"}]},
    {"id": "https://openalex.org/A222222", "display_name": "Pat Example", "works_count": 2, "cited_by_count": 3,
     "last_known_institutions": [], "affiliations": [{"institution": {"display_name": "Other College"}}], "topics": []}]}


def work(i, topics, kws=()):
    return {"id": f"https://openalex.org/W{i}", "title": f"Paper {i}", "publication_year": 2024, "doi": f"https://doi.org/10.1/{i}",
            "topics": [{"display_name": t} for t in topics], "keywords": [{"display_name": k} for k in kws]}


WORKS = {"results": [work(1, ["Plant Photobiology", "Science"], ["blue light"]), work(2, ["Plant Photobiology"]),
                     work(3, ["Flavoproteins"], ["blue light"])]}


class Resp:
    def __init__(self, data, code=200): self.data, self.status_code = data, code
    def json(self): return self.data


class FakeClient:
    def __init__(self, code=200): self.calls, self.code = [], code
    def get(self, url, params=None):
        self.calls.append((url, params))
        return Resp(AUTHORS if url.endswith("/authors") else WORKS, self.code)


def test_search_returns_candidates_with_institution_fallback():
    c = oa.search_authors("Pat Example", client=FakeClient())
    assert [x["openalex_id"] for x in c] == ["A111111", "A222222"]
    assert c[0]["institution"] == "Example University" and c[1]["institution"] == "Other College"
    assert c[0]["top_topics"] == ["Plant Photobiology", "Flavoproteins"] and c[0]["works_count"] == 40


def test_expertise_terms_carry_their_source_works_and_skip_generic_terms():
    e = oa.expertise("A111111", client=FakeClient())
    terms = {t["term"]: t for t in e["terms"]}
    assert e["works_considered"] == 3 and "Science" not in terms
    assert terms["Plant Photobiology"]["work_count"] == 2 and terms["blue light"]["work_count"] == 2
    assert terms["Plant Photobiology"]["works"][0]["url"].startswith("https://doi.org/")
    assert e["terms"][0]["work_count"] >= e["terms"][-1]["work_count"]


def test_requests_send_no_personal_details_and_a_generic_agent():
    fc = FakeClient(); oa.search_authors("Pat Example", client=fc); oa.expertise("A111111", client=fc)
    blob = str(fc.calls).lower()
    assert "mailto" not in blob and "@" not in blob
    assert oa.USER_AGENT == "forge-signal"


@pytest.mark.parametrize("bad", ["", "A1", "A111111; DROP", "../x", "W123456"])
def test_bad_author_ids_are_refused_before_any_request(bad):
    fc = FakeClient()
    with pytest.raises(oa.OpenAlexError): oa.expertise(bad, client=fc)
    assert fc.calls == []


def test_upstream_errors_become_a_clear_error():
    with pytest.raises(oa.OpenAlexError, match="HTTP 429"): oa.search_authors("Pat Example", client=FakeClient(429))


@pytest.fixture
def api():
    return TestClient(create_app(":memory:", lister=lambda *a, **k: [], detailer=lambda *a, **k: ([], []), openalex_client=FakeClient()))


def test_endpoints(api):
    r = api.get("/api/pi/search", params={"name": "Pat Example"}); assert r.status_code == 200
    assert len(r.json()["candidates"]) == 2 and r.json()["source"]["system"] == "OpenAlex"
    assert api.get("/api/pi/search", params={"name": "ab"}).status_code == 400
    e = api.get("/api/pi/A111111/expertise"); assert e.status_code == 200 and e.json()["terms"]
    assert api.get("/api/pi/not-an-id/expertise").status_code == 400


def test_lookup_rate_limit(api):
    api.app.state.db.set_setting("pi_lookups_per_hour", 2)
    codes = [api.get("/api/pi/search", params={"name": "Pat Example"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]
