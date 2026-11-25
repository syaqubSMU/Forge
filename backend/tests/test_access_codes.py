"""Approved-tester access codes. Fakes only: no live model call."""
import json
import threading
import logging
import os

import pytest
from fastapi.testclient import TestClient

import app.access as access
from app.adapters import registry
from app.adapters.base import ModelAdapter
from app.db import Database
from app.main import create_app
from app.sources.grants_gov import SourceError
from tests.test_pipeline import CORPUS, factors_json, PricedMock

ADMIN = {"X-Admin-Token": "admin-secret-token-for-tests-1234567890"}
BODY = {"input_type": "pi_name", "input_text": "x", "profile": {"career_stage": "e", "lanes": ["photochemistry and flavin biology"]}}


def detailer(ids, **k):
    return [dict(o) for o in CORPUS if o["source_record_id"] in [str(i) for i in ids]], []


@pytest.fixture
def hosted(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "admin-secret-token-for-tests-1234567890"); monkeypatch.setenv("FORGE_SALT", "test-salt-value")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: PricedMock([factors_json()]))
    app = create_app(":memory:", lister=lambda *a, **k: [dict(o) for o in CORPUS], detailer=detailer)
    app.state.db.set_setting("require_access_code", True)
    c = TestClient(app); c.db = app.state.db
    return c


def make(c, label="tester 1", allowance=3, **kw):
    r = c.post("/api/admin/access-codes", json={"label": label, "allowance": allowance, **kw}, headers=ADMIN)
    assert r.status_code == 201, r.text
    return r.json()


def run(c, code=None, **kw):
    h = {"X-Access-Code": code} if code else {}
    return c.post("/api/runs", json=BODY, headers=h, **kw)


def err(r):
    return r.json()["detail"]


# ---- creation, storage, secrecy ----------------------------------------------------------------------------------
def test_code_is_shown_once_and_only_its_keyed_hash_is_stored(hosted):
    out = make(hosted)
    assert out["code"].startswith("fsa_") and len(out["code"]) >= 30 and out["allowance"] == 3 and out["expires_at"] == "2026-12-08T00:00:00+00:00"
    row = hosted.db.q("SELECT * FROM access_codes WHERE id=?", (out["id"],), one=True)
    assert out["code"] not in json.dumps(dict(row)) and row["code_hash"] == access.hash_code(out["code"])
    listing = hosted.get("/api/admin/access-codes", headers=ADMIN)
    assert out["code"] not in listing.text and row["code_hash"] not in listing.text and "code_hash" not in listing.text
    assert hosted.post("/api/admin/access-codes", json={"label": "x"}, headers=ADMIN).headers["cache-control"] == "no-store"
    audit = json.dumps([dict(r) for r in hosted.db.q("SELECT detail FROM admin_audit")])
    assert out["code"] not in audit and "access_code_created" in json.dumps([dict(r) for r in hosted.db.q("SELECT action FROM admin_audit")])


def test_hash_depends_on_the_salt_so_a_changed_salt_invalidates_codes(hosted, monkeypatch):
    out = make(hosted)
    monkeypatch.setenv("FORGE_SALT", "a-different-salt")
    assert err(run(hosted, out["code"]))["code"] == "invalid"


def test_creating_a_code_is_refused_without_a_salt(hosted, monkeypatch):
    monkeypatch.delenv("FORGE_SALT")
    r = hosted.post("/api/admin/access-codes", json={"label": "tester 1"}, headers=ADMIN)
    assert r.status_code == 503 and "FORGE_SALT" in r.text


def test_admin_endpoints_need_the_admin_token(hosted):
    assert hosted.post("/api/admin/access-codes", json={"label": "tester 1"}).status_code == 401
    assert hosted.get("/api/admin/access-codes").status_code == 401
    assert hosted.post("/api/admin/access-codes/abc/revoke").status_code == 401


@pytest.mark.parametrize("label", ["", "ann@example.com", "x" * 61, "-starts with dash", "tab\tinside", "<script>"])
def test_labels_must_not_look_like_emails_or_markup(hosted, label):
    assert hosted.post("/api/admin/access-codes", json={"label": label}, headers=ADMIN).status_code in (400, 422)


@pytest.mark.parametrize("allowance", [0, 21, -1])
def test_allowance_range(hosted, allowance):
    assert hosted.post("/api/admin/access-codes", json={"label": "tester 1", "allowance": allowance}, headers=ADMIN).status_code == 400


def test_expiry_defaults_none_and_dates(hosted):
    assert make(hosted, "a", expires_at="none")["expires_at"] is None
    assert make(hosted, "b", expires_at="2026-12-01")["expires_at"] == "2026-12-01T00:00:00+00:00"
    assert make(hosted, "c")["expires_at"] == "2026-12-08T00:00:00+00:00"
    assert hosted.post("/api/admin/access-codes", json={"label": "d", "expires_at": "tomorrow"}, headers=ADMIN).status_code == 400


# ---- the gate ----------------------------------------------------------------------------------------------------
def test_run_without_a_code_is_refused_and_offers_the_recording(hosted):
    r = run(hosted); d = err(r)
    assert r.status_code == 403 and d["code"] == "missing" and d["recorded_example"] is True and "approved testers" in d["message"]
    assert hosted.db.q("SELECT COUNT(*) c FROM runs", one=True)["c"] == 0


def test_each_refusal_has_its_own_code_and_text(hosted):
    ok = make(hosted)["code"]
    assert err(run(hosted, "fsa_not-a-real-code"))["code"] == "invalid"
    expired = make(hosted, "e", expires_at="2020-01-01")["code"]; assert err(run(hosted, expired))["code"] == "expired"
    rv = make(hosted, "r"); hosted.post(f"/api/admin/access-codes/{rv['id']}/revoke", headers=ADMIN)
    assert err(run(hosted, rv["code"]))["code"] == "revoked"
    one = make(hosted, "o", allowance=1)["code"]; assert run(hosted, one).status_code == 200
    d = err(run(hosted, one)); assert d["code"] == "allowance_used" and d["message"] == access.MESSAGES["allowance_used"]
    assert run(hosted, ok).status_code == 200                                       # the other code still works


def test_valid_code_runs_records_usage_and_shows_remaining(hosted):
    out = make(hosted); r = run(hosted, out["code"]); j = r.json()
    assert r.status_code == 200 and j["access"] == {"remaining": 2} and j["results"]
    assert hosted.db.q("SELECT access_code_id FROM runs", one=True)["access_code_id"] == out["id"]
    row = hosted.get("/api/admin/access-codes", headers=ADMIN).json()[0]
    assert (row["runs_used"], row["remaining"], row["runs"]) == (1, 2, 1) and row["cost_usd_estimate"] > 0 and row["last_used_at"]


def test_pasted_evidence_runs_also_need_a_code(hosted):
    body = {"input_type": "project", "input_text": "x", "sources": {"s": "some source text that is long enough to quote"}}
    assert hosted.post("/api/runs", json=body).status_code == 403


def test_codes_not_required_when_the_setting_is_off(hosted):
    hosted.db.set_setting("require_access_code", False)
    assert run(hosted).status_code == 200


def test_bool_settings_can_now_be_changed(hosted):
    r = hosted.put("/api/admin/settings", json={"require_access_code": False}, headers=ADMIN)
    assert r.status_code == 200 and r.json()["settings"]["require_access_code"] is False
    assert hosted.put("/api/admin/settings", json={"require_access_code": "no"}, headers=ADMIN).status_code == 400


# ---- allowance: atomic claim, refunds, other gates ----------------------------------------------------------------
def test_two_simultaneous_claims_on_the_last_run_cannot_both_win(hosted):
    out = make(hosted, allowance=1); row = access.lookup(hosted.db, out["code"]); results = []
    ts = [threading.Thread(target=lambda: results.append(access.claim(hosted.db, row))) for _ in range(8)]
    [t.start() for t in ts]; [t.join() for t in ts]
    assert results.count(True) == 1 and hosted.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 1


def test_no_refund_needed_when_other_gates_refuse(hosted):
    out = make(hosted)
    hosted.db.set_setting("daily_cap", 0); assert run(hosted, out["code"]).status_code == 503
    hosted.db.set_setting("daily_cap", 100); hosted.db.set_setting("rate_limit_per_hour", 0); assert run(hosted, out["code"]).status_code == 429
    hosted.db.set_setting("rate_limit_per_hour", 10); hosted.db.set_setting("pilot_budget_usd", 1e-9)
    run(hosted, out["code"])                                                           # one real run, whose cost passes the tiny budget
    used = hosted.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"]
    assert used == 1 and err(run(hosted, out["code"]))["code"] == "budget_reached"
    assert hosted.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 1


def test_a_bad_code_gets_the_access_message_not_a_capacity_message(hosted):
    hosted.db.set_setting("daily_cap", 0)
    assert err(run(hosted, "fsa_wrong"))["code"] == "invalid"


def test_outage_with_no_model_call_succeeding_is_refunded(hosted, monkeypatch):
    class Boom(ModelAdapter):
        name = "boom"
        def complete(self, system, prompt): raise RuntimeError("down")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: Boom())
    out = make(hosted)
    assert run(hosted, out["code"]).status_code == 502
    assert hosted.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 0


def test_unreadable_answers_spent_tokens_so_they_count(hosted, monkeypatch):
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: PricedMock(["{not json"]))
    out = make(hosted)
    assert run(hosted, out["code"]).status_code == 502
    assert hosted.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 1


def test_source_outage_is_refunded(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "admin-secret-token-for-tests-1234567890"); monkeypatch.setenv("FORGE_SALT", "s")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: PricedMock([factors_json()]))
    def down(*a, **k): raise SourceError("down")
    app = create_app(":memory:", lister=down, detailer=detailer); app.state.db.set_setting("require_access_code", True)
    c = TestClient(app); c.db = app.state.db
    out = make(c)
    assert run(c, out["code"]).status_code == 503
    assert c.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 0


def test_revoking_takes_effect_on_the_next_request_and_is_idempotent(hosted):
    out = make(hosted); assert run(hosted, out["code"]).status_code == 200
    a = hosted.post(f"/api/admin/access-codes/{out['id']}/revoke", headers=ADMIN).json()
    b = hosted.post(f"/api/admin/access-codes/{out['id']}/revoke", headers=ADMIN).json()
    assert a["revoked_at"] == b["revoked_at"] and err(run(hosted, out["code"]))["code"] == "revoked"
    assert hosted.post("/api/admin/access-codes/nope/revoke", headers=ADMIN).status_code == 404


# ---- check endpoint, ceiling, comparison, secrecy -----------------------------------------------------------------
def test_check_endpoint_validates_without_spending(hosted):
    out = make(hosted)
    r = hosted.get("/api/access/check", headers={"X-Access-Code": out["code"]})
    assert r.json() == {"required": True, "valid": True, "remaining": 3, "expires_at": "2026-12-08T00:00:00+00:00"}
    assert hosted.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 0 and hosted.db.q("SELECT COUNT(*) c FROM runs", one=True)["c"] == 0
    assert err(hosted.get("/api/access/check"))["code"] == "missing"
    assert err(hosted.get("/api/access/check", headers={"X-Access-Code": "fsa_x"}))["code"] == "invalid"
    hosted.db.set_setting("require_access_code", False)
    assert hosted.get("/api/access/check").json() == {"required": False, "valid": True}


def test_pages_and_config_need_no_code(hosted):
    assert hosted.get("/api/health").status_code == 200 and hosted.get("/config.js").status_code == 200


def test_per_visitor_attempt_ceiling_counts_real_attempts_only(hosted):
    hosted.db.set_setting("access_checks_per_hour", 2)
    for _ in range(5): assert err(run(hosted))["code"] == "missing"                       # a missing code costs nothing
    assert err(run(hosted, "fsa_a"))["code"] == "invalid" and err(run(hosted, "fsa_b"))["code"] == "invalid"
    r = run(hosted, "fsa_c"); assert r.status_code == 429 and err(r)["code"] == "too_many_attempts"
    assert "recorded_example" not in err(r)


def test_comparison_uses_a_constant_time_function(hosted, monkeypatch):
    out = make(hosted); calls = []
    real = access.hmac.compare_digest
    monkeypatch.setattr(access.hmac, "compare_digest", lambda a, b: (calls.append(1), real(a, b))[1])
    assert run(hosted, out["code"]).status_code == 200 and calls


def test_the_code_never_appears_in_logs_errors_runs_or_the_database(hosted, caplog):
    out = make(hosted); code = out["code"]
    with caplog.at_level(logging.DEBUG):
        responses = [run(hosted, code), run(hosted, code[:-1] + "Z"), hosted.get("/api/access/check", headers={"X-Access-Code": code}),
                     hosted.get("/api/admin/access-codes", headers=ADMIN), hosted.get("/api/admin/runs", headers=ADMIN),
                     hosted.get("/api/admin/runs.csv", headers=ADMIN), hosted.get("/api/admin/environment", headers=ADMIN)]
    assert all(code not in r.text for r in responses) and code not in caplog.text
    dump = json.dumps({t: [dict(x) for x in hosted.db.q(f"SELECT * FROM {t}")] for t in ("runs", "admin_audit", "api_calls", "run_matches", "run_sources")}, default=str)
    assert code not in dump


def test_environment_report_shows_access_code_state(hosted):
    make(hosted); make(hosted, "e", expires_at="2020-01-01")
    j = hosted.get("/api/admin/environment", headers=ADMIN).json()["access_codes"]
    assert j == {"required": True, "salt_set": True, "usable_codes": 1}


# ---- migration -----------------------------------------------------------------------------------------------------
def test_database_at_version_2_upgrades_to_3_with_data_intact(tmp_path, monkeypatch):
    import app.db as dbmod
    if os.environ.get("FORGE_TEST_PG_URL"):
        import psycopg
        target = os.environ["FORGE_TEST_PG_URL"]
        with psycopg.connect(target, autocommit=True) as c: c.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    else:
        target = str(tmp_path / "v2.db")
    full = list(dbmod.MIGRATIONS)
    monkeypatch.setattr(dbmod, "MIGRATIONS", full[:2])
    old = Database(target); assert old.schema_version() == 2
    old.q("INSERT INTO runs(id,created_at,status,input_text,cost_usd) VALUES(?,?,?,?,?)", ("abcdef123456", "now", "ok", "x", 0.5), write=True)
    old.conn.close()
    monkeypatch.setattr(dbmod, "MIGRATIONS", full)
    new = Database(target)
    assert new.schema_version() == 3
    row = new.q("SELECT id, cost_usd, access_code_id FROM runs", one=True)
    assert (row["id"], row["cost_usd"], row["access_code_id"]) == ("abcdef123456", 0.5, None)
    assert new.q("SELECT COUNT(*) c FROM access_codes", one=True)["c"] == 0
