import json
import pytest
from fastapi.testclient import TestClient

from app.adapters import registry
from app.adapters.mock import MockAdapter
from app.fit import DEFAULT_RUBRIC
from app.main import create_app
from app.template_xlsx import write_template

SRC = {"https://sponsor.example/nofo": "Applicants must be U.S. institutions of higher education. Proposals are due March 15, 2027."}
GOOD = json.dumps({"fit": "High", "eligibility": "Eligible", "rationale": "ok",
                   "fit_citations": [{"quote": "Proposals are due March 15, 2027.", "source_id": "https://sponsor.example/nofo"}],
                   "eligibility_citations": [{"quote": "Applicants must be U.S. institutions of higher education", "source_id": "https://sponsor.example/nofo"}]})
BAD_QUOTE = GOOD.replace("Applicants must be U.S. institutions of higher education", "Open to everyone worldwide")
H = {"X-Admin-Token": "secret-token"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "secret-token")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: MockAdapter([GOOD]))
    return TestClient(create_app(":memory:"))


def run(c, **kw):
    body = {"input_type": "pi_name", "input_text": "Dr. Sample A", "sources": SRC}; body.update(kw)
    return c.post("/api/runs", json=body)


def test_run_is_logged_and_result_has_citations(client):
    r = run(client); assert r.status_code == 200
    j = r.json(); assert j["result"]["fit"] == "High" and "logged" in j["notice"] and len(j["result"]["citations"]) == 2
    d = client.get(f"/api/admin/runs/{j['run_id']}", headers=H).json()
    assert d["status"] == "ok" and d["model"] == "mock" and len(d["sources"]) == 1 and d["citations"] and d["rubric_version"]


def test_public_response_returns_only_quotes_not_whole_sources(client):
    j = run(client).json()
    assert set(j.keys()) == {"run_id", "result", "notice"}
    assert all(c["quote"] in SRC["https://sponsor.example/nofo"] for c in j["result"]["citations"])
    assert "sk-" not in run(client).text


def test_fabricated_quote_is_logged_as_failed(client, monkeypatch):
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: MockAdapter([BAD_QUOTE]))
    j = run(client).json(); assert j["result"]["failed_citation_count"] == 1 and j["result"]["eligibility"] == "Needs verification"
    cites = client.get(f"/api/admin/runs/{j['run_id']}", headers=H).json()["citations"]
    assert any(c["validated"] == 0 for c in cites)


def test_invalid_model_output_returns_502_and_logs_failure(client, monkeypatch):
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: MockAdapter(["not json"]))
    assert run(client).status_code == 502
    runs = client.get("/api/admin/runs", headers=H).json(); assert runs[0]["status"] == "failed"


def test_input_validation(client):
    assert run(client, input_type="nope").status_code == 400
    assert run(client, sources={}, input_text=" ").status_code == 422   # live mode needs a profile


def test_admin_requires_token(client, monkeypatch):
    assert client.get("/api/admin/settings").status_code == 401
    assert client.get("/api/admin/settings", headers={"X-Admin-Token": "wrong"}).status_code == 401
    monkeypatch.delenv("ADMIN_TOKEN"); assert client.get("/api/admin/settings", headers=H).status_code == 503


def test_rate_limit_and_daily_cap(client):
    client.put("/api/admin/settings", json={"rate_limit_per_hour": 2}, headers=H)
    assert run(client).status_code == 200 and run(client).status_code == 200 and run(client).status_code == 429
    client.put("/api/admin/settings", json={"rate_limit_per_hour": 100, "daily_cap": 2}, headers=H)
    assert run(client).status_code == 503


def test_settings_validation_and_audit_of_model_switch(client):
    assert client.put("/api/admin/settings", json={"bogus": 1}, headers=H).status_code == 400
    assert client.put("/api/admin/settings", json={"horizon_months": "three"}, headers=H).status_code == 400
    assert client.put("/api/admin/settings", json={"active_model": "nope"}, headers=H).status_code == 400
    assert client.put("/api/admin/settings", json={"active_model": "claude"}, headers=H).status_code == 200
    a = client.get("/api/admin/audit", headers=H).json()[0]
    assert a["action"] == "setting_changed" and '"active_model"' in a["detail"]
    s = client.get("/api/admin/settings", headers=H).json()["settings"]
    assert s["active_model"] == "claude" and not any("key" in k.lower() for k in s)


def test_email_requires_confirmation_and_is_logged_dummy(client):
    rid = run(client).json()["run_id"]
    body = {"draft": "DRAFT alert", "recipient": "pi@example.edu", "confirmed": False}
    assert client.post(f"/api/runs/{rid}/email", json=body).status_code == 400
    body["confirmed"] = True
    r = client.post(f"/api/runs/{rid}/email", json=body); assert r.status_code == 200 and r.json()["mode"] == "dummy"
    assert client.get(f"/api/admin/runs/{rid}", headers=H).json()["emails"][0]["recipient"] == "pi@example.edu"
    assert client.post(f"/api/runs/{rid}/email", json={**body, "recipient": "bad"}).status_code == 400
    assert client.post("/api/runs/unknown/email", json=body).status_code == 404


def test_annotations_csv_and_formula_injection_guard(client):
    rid = run(client, input_text="=HYPERLINK(\"http://x\")").json()["run_id"]
    assert client.post(f"/api/admin/runs/{rid}/annotations", json={"label": "agree", "note": "good"}, headers=H).status_code == 200
    assert client.get(f"/api/admin/runs/{rid}", headers=H).json()["annotations"][0]["label"] == "agree"
    csv_text = client.get("/api/admin/runs.csv", headers=H).text
    assert "'=HYPERLINK" in csv_text


def test_retention_archives_old_runs(client):
    rid = run(client).json()["run_id"]
    client.app.state.db.q("UPDATE runs SET created_at='2020-01-01T00:00:00+00:00' WHERE id=?", (rid,), write=True)
    assert client.post("/api/admin/retention/run", headers=H).json()["archived"] == 1
    assert client.get("/api/admin/runs", headers=H).json() == []
    assert len(client.get("/api/admin/runs?archived=true", headers=H).json()) == 1


def test_rubric_preview_and_publish_gate(client, tmp_path):
    p = tmp_path / "t.xlsx"; write_template(p, DEFAULT_RUBRIC)
    pv = client.post("/api/admin/rubric/preview", files={"file": open(p, "rb")}, headers=H).json()
    assert pv["publishable"] and pv["diff"] == []
    import openpyxl
    wb = openpyxl.load_workbook(p); wb["Examples"]["C2"].value = "Strong"; wb.save(p)       # wrong worked example
    assert client.post("/api/admin/rubric/publish", files={"file": open(p, "rb")}, headers=H).status_code == 400
    write_template(p, DEFAULT_RUBRIC)
    assert client.post("/api/admin/rubric/publish?note=first", files={"file": open(p, "rb")}, headers=H).status_code == 200
    assert client.get("/api/admin/rubric", headers=H).json()["versions"][0]["status"] == "published"
