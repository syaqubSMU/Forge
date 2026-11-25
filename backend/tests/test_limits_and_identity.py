"""Request size limits and client identity behind a proxy. Fakes only."""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app, MAX_SOURCE_CHARS


@pytest.fixture
def c():
    return TestClient(create_app(":memory:", lister=lambda *a, **k: [], detailer=lambda *a, **k: ([], [])))


def run(c, **kw):
    body = {"input_type": "pi_name", "input_text": "x", "profile": {"career_stage": "e", "lanes": ["plants"]}}
    body.update(kw)
    return c.post("/api/runs", json=body, **kw.pop("req", {}))


@pytest.mark.parametrize("patch", [
    {"question": "q" * 1001},
    {"profile": {"lanes": ["x" * 301]}}, {"profile": {"lanes": ["a"] * 41}},
    {"profile": {"positioning_rules": ["x" * 601]}}, {"profile": {"career_stage": "x" * 201}},
    {"sources": {str(i): "t" for i in range(6)}},
    {"sources": {"a": "x" * (MAX_SOURCE_CHARS + 1)}},
    {"options": {str(i): 1 for i in range(11)}}])
def test_oversized_fields_are_refused(c, patch):
    assert run(c, **patch).status_code == 422


def test_body_cap_returns_413_before_parsing(c):
    r = c.post("/api/runs", content=b"{" + b" " * 450000 + b"}", headers={"content-type": "application/json"})
    assert r.status_code == 413


def test_pasted_source_at_the_limit_is_accepted(c):
    r = run(c, sources={"s": "x" * MAX_SOURCE_CHARS})
    assert r.status_code != 422 and r.status_code != 413


def test_forwarded_header_is_ignored_by_default(c, monkeypatch):
    monkeypatch.delenv("FORGE_TRUSTED_PROXY_HOPS", raising=False)
    monkeypatch.setenv("FORGE_SALT", "s")
    c.app.state.db.set_setting("rate_limit_per_hour", 1)
    a = c.post("/api/runs", json={"input_type": "pi_name", "input_text": "x", "profile": {"lanes": ["p"]}}, headers={"x-forwarded-for": "1.1.1.1"})
    b = c.post("/api/runs", json={"input_type": "pi_name", "input_text": "x", "profile": {"lanes": ["p"]}}, headers={"x-forwarded-for": "2.2.2.2"})
    assert a.status_code == 200 and b.status_code == 429          # a client cannot dodge the limit by forging the header


def test_trusted_proxy_hops_use_the_rightmost_entries(c, monkeypatch):
    monkeypatch.setenv("FORGE_TRUSTED_PROXY_HOPS", "1")
    c.app.state.db.set_setting("rate_limit_per_hour", 1)
    post = lambda xff: c.post("/api/runs", json={"input_type": "pi_name", "input_text": "x", "profile": {"lanes": ["p"]}}, headers={"x-forwarded-for": xff})
    assert post("9.9.9.9, 1.1.1.1").status_code == 200             # real client 1.1.1.1 (left entry is client-supplied)
    assert post("8.8.8.8, 1.1.1.1").status_code == 429             # same client again, whatever it forged on the left
    assert post("1.1.1.1, 2.2.2.2").status_code == 200             # a different client is counted separately


def test_new_runs_get_32_hex_ids_and_old_12_character_ids_still_work(c, monkeypatch):
    import re
    monkeypatch.setenv("ADMIN_TOKEN", "t")
    rid = c.post("/api/runs", json={"input_type": "pi_name", "input_text": "x", "profile": {"lanes": ["p"]}}).json()["run_id"]
    assert re.fullmatch(r"[0-9a-f]{32}", rid)
    db = c.app.state.db
    db.q("UPDATE runs SET id=? WHERE id=?", ("abcdef123456", rid), write=True)        # a run created by the old code
    assert c.get("/api/admin/runs/abcdef123456", headers={"X-Admin-Token": "t"}).status_code == 200
    assert c.get("/api/runs/abcdef123456/calendar").status_code in (200, 404)         # lookup by id still works (owner check may apply)


def test_whoami_is_admin_only_and_reports_the_believed_address(c, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "t"); monkeypatch.setenv("FORGE_TRUSTED_PROXY_HOPS", "1")
    assert c.get("/api/admin/whoami").status_code == 401
    j = c.get("/api/admin/whoami", headers={"X-Admin-Token": "t", "x-forwarded-for": "9.9.9.9, 1.1.1.1"}).json()
    assert j["believed_client_ip"] == "1.1.1.1" and j["trusted_proxy_hops"] == "1"


def test_hosted_database_without_a_salt_logs_a_warning(monkeypatch, caplog):
    import app.main as main
    class FakeDb(main.Database):
        def __init__(self, path=":memory:"):
            super().__init__(":memory:"); self.pg = True
    monkeypatch.setattr(main, "Database", FakeDb); monkeypatch.delenv("FORGE_SALT", raising=False)
    with caplog.at_level("WARNING", logger="uvicorn.error"):
        main.create_app("postgresql://x", lister=lambda *a, **k: [], detailer=lambda *a, **k: ([], []))
    assert "FORGE_SALT is not set" in caplog.text
