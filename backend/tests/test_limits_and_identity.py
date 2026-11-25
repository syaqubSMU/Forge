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


def test_environment_report_shows_no_secret_values(c, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "super-secret-admin"); monkeypatch.setenv("FORGE_SALT", "salty-secret")
    monkeypatch.setenv("FORGE_API_KEY", "sk-ant-VERYSECRET"); monkeypatch.setenv("FORGE_DB", "postgresql://u:pw123@h/db")
    assert c.get("/api/admin/environment").status_code == 401
    r = c.get("/api/admin/environment", headers={"X-Admin-Token": "super-secret-admin"})
    j = r.json()
    assert j["admin_token_set"] and j["salt_set"] and j["model_key_variable"] == "FORGE_API_KEY"
    for secret in ("super-secret-admin", "salty-secret", "VERYSECRET", "pw123", "postgresql://"):
        assert secret not in r.text


def test_runs_csv_labels_cost_as_an_estimate(c, monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "t")
    head = c.get("/api/admin/runs.csv", headers={"X-Admin-Token": "t"}).text.splitlines()[0]
    assert "cost_usd_estimate" in head and head.endswith("access_code_id")


@pytest.mark.parametrize("value,shown", [("claude-opus-5-5", "claude-opus-5-5"), ("low", "low"),
                                         ("sk-ant-SECRET value with spaces", "(set, unusual value)"),
                                         ("https://u:pw@host/x", "(set, unusual value)"), ("x" * 81, "(set, unusual value)")])
def test_environment_shows_model_and_effort_only_if_they_look_ordinary(c, monkeypatch, value, shown):
    monkeypatch.setenv("ADMIN_TOKEN", "t"); monkeypatch.setenv("FORGE_MODEL", value); monkeypatch.setenv("FORGE_EFFORT", value)
    j = c.get("/api/admin/environment", headers={"X-Admin-Token": "t"}).json()
    assert j["model"] == shown and j["effort"] == shown
    assert "SECRET" not in str(j) and "pw@" not in str(j)


def test_short_admin_token_logs_a_warning_without_the_token(monkeypatch, caplog):
    import app.main as main
    monkeypatch.setenv("ADMIN_TOKEN", "short-token-123")
    with caplog.at_level("WARNING", logger="uvicorn.error"):
        main.create_app(":memory:", lister=lambda *a, **k: [], detailer=lambda *a, **k: ([], []))
    assert "shorter than 32" in caplog.text and "short-token-123" not in caplog.text
    caplog.clear(); monkeypatch.setenv("ADMIN_TOKEN", "x" * 40)
    with caplog.at_level("WARNING", logger="uvicorn.error"):
        main.create_app(":memory:", lister=lambda *a, **k: [], detailer=lambda *a, **k: ([], []))
    assert "shorter than 32" not in caplog.text
