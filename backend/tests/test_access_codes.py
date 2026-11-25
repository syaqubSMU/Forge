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


def test_only_failed_attempts_are_counted_and_no_code_is_locked(hosted):
    good = make(hosted)["code"]
    hosted.db.set_setting("access_failures_per_hour", 2)
    for _ in range(5): assert err(run(hosted))["code"] == "missing"                      # a missing code is not a failed attempt
    assert run(hosted, good).status_code == 200 and run(hosted, good).status_code == 200  # valid use is not counted
    assert err(run(hosted, "fsa_a"))["code"] == "invalid" and err(run(hosted, "fsa_b"))["code"] == "invalid"
    r = run(hosted, "fsa_c"); assert r.status_code == 429 and err(r)["code"] == "too_many_attempts" and "recorded_example" not in err(r)
    assert hosted.db.q("SELECT revoked_at FROM access_codes", one=True)["revoked_at"] is None    # the address is throttled, the code is not locked
    assert err(hosted.get("/api/access/check", headers={"X-Access-Code": "fsa_d"}))["code"] == "too_many_attempts"


def test_failed_attempts_are_not_logged_or_stored(hosted, caplog):
    with caplog.at_level(logging.DEBUG):
        run(hosted, "fsa_guess-one"); run(hosted, "fsa_guess-two")
    assert "guess" not in caplog.text and "access code" not in caplog.text.lower()
    assert hosted.db.q("SELECT COUNT(*) c FROM admin_audit WHERE action IN ('access_code_created', 'access_code_revoked', 'access_code_failed')", one=True)["c"] == 0


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
    assert (j["required"], j["salt_set"], j["usable_codes"]) == (True, True, 1) and j["budget_reservation"]["outstanding_runs"] == 3


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


# ---- one run in flight per code ------------------------------------------------------------------------------------
def test_a_second_concurrent_run_from_the_same_code_is_refused_then_allowed_after(hosted, monkeypatch):
    started, release = threading.Event(), threading.Event()

    class Slow(PricedMock):
        def complete(self, system, prompt):
            started.set(); release.wait(10)
            return super().complete(system, prompt)
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: Slow([factors_json()]))
    out = make(hosted); box = []
    t = threading.Thread(target=lambda: box.append(run(hosted, out["code"]))); t.start()
    assert started.wait(10)
    r = run(hosted, out["code"])
    assert r.status_code == 429 and err(r)["code"] == "run_in_progress" and "still running" in err(r)["message"]
    assert hosted.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 1      # the refused request took nothing
    other = make(hosted, "tester 2")                                                            # another code is not blocked by this one
    release.set(); t.join(30)
    assert box[0].status_code == 200 and run(hosted, other["code"]).status_code == 200
    assert run(hosted, out["code"]).status_code == 200                                         # released after the first finished


def test_the_in_flight_slot_is_released_when_a_run_fails(hosted, monkeypatch):
    class Boom(ModelAdapter):
        name = "boom"
        def complete(self, system, prompt): raise RuntimeError("down")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: Boom())
    out = make(hosted)
    assert run(hosted, out["code"]).status_code == 502
    r = run(hosted, out["code"])
    assert r.status_code == 502 and "run_in_progress" not in r.text                  # reached the model again: the slot was free


# ---- budget reservation at creation --------------------------------------------------------------------------------
def test_creating_a_code_is_refused_when_outstanding_allowances_would_exceed_the_budget(hosted):
    assert hosted.db.settings()["pilot_budget_usd"] == 9.0 and hosted.db.settings()["estimated_run_cost_usd"] == 0.44
    for i in range(6): make(hosted, f"tester {i + 1}", 3)                       # 18 runs, about $7.92
    make(hosted, "owner", 2)                                                     # 20 runs, $8.80: fits
    r = hosted.post("/api/admin/access-codes", json={"label": "owner extra", "allowance": 1}, headers=ADMIN)
    assert r.status_code == 409 and err(r)["code"] == "budget_would_be_exceeded" and "exceed the pilot budget" in err(r)["message"]
    assert hosted.db.q("SELECT COUNT(*) c FROM access_codes", one=True)["c"] == 7


def test_an_owner_code_of_three_is_refused_after_six_testers_of_three(hosted):
    for i in range(6): make(hosted, f"tester {i + 1}", 3)
    assert hosted.post("/api/admin/access-codes", json={"label": "owner", "allowance": 3}, headers=ADMIN).status_code == 409


def test_revoking_or_using_runs_frees_budget_and_a_raised_limit_allows_more(hosted):
    ids = [make(hosted, f"tester {i + 1}", 3) for i in range(6)]
    make(hosted, "owner", 2)
    assert hosted.post("/api/admin/access-codes", json={"label": "x", "allowance": 3}, headers=ADMIN).status_code == 409
    hosted.post(f"/api/admin/access-codes/{ids[0]['id']}/revoke", headers=ADMIN)       # frees 3 runs
    assert hosted.post("/api/admin/access-codes", json={"label": "x", "allowance": 3}, headers=ADMIN).status_code == 201
    assert hosted.post("/api/admin/access-codes", json={"label": "y", "allowance": 1}, headers=ADMIN).status_code == 409
    hosted.db.set_setting("pilot_budget_usd", 20.0)                                    # deliberate
    assert hosted.post("/api/admin/access-codes", json={"label": "y", "allowance": 1}, headers=ADMIN).status_code == 201


def test_recorded_spend_counts_against_the_reservation(hosted):
    out = make(hosted, "tester 1", 1)
    assert run(hosted, out["code"]).status_code == 200
    hosted.db.q("UPDATE runs SET cost_usd=8.9", write=True)                            # spend already recorded in this database
    assert hosted.post("/api/admin/access-codes", json={"label": "z", "allowance": 1}, headers=ADMIN).status_code == 409


def test_out_of_range_allowance_still_says_400_not_a_budget_message(hosted):
    assert hosted.post("/api/admin/access-codes", json={"label": "x", "allowance": 21}, headers=ADMIN).status_code == 400


# ---- the researcher lookup also needs a code ---------------------------------------------------------------------
def test_pi_lookup_needs_a_valid_code_and_does_not_spend_an_allowance(monkeypatch):
    from tests.test_openalex import FakeClient
    monkeypatch.setenv("ADMIN_TOKEN", "admin-secret-token-for-tests-1234567890"); monkeypatch.setenv("FORGE_SALT", "s")
    app = create_app(":memory:", lister=lambda *a, **k: [], detailer=detailer, openalex_client=FakeClient())
    app.state.db.set_setting("require_access_code", True)
    c = TestClient(app); c.db = app.state.db
    out = make(c)
    assert err(c.post("/api/pi/search", json={"name": "Pat Example"}))["code"] == "missing"
    assert err(c.get("/api/pi/A111111/expertise"))["code"] == "missing"
    assert err(c.post("/api/pi/search", json={"name": "Pat Example"}, headers={"X-Access-Code": "fsa_nope"}))["code"] == "invalid"
    h = {"X-Access-Code": out["code"]}
    assert c.post("/api/pi/search", json={"name": "Pat Example"}, headers=h).status_code == 200
    assert c.get("/api/pi/A111111/expertise", headers=h).status_code == 200
    assert c.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 0
    c.db.set_setting("require_access_code", False)
    assert c.post("/api/pi/search", json={"name": "Pat Example"}).status_code == 200


# ---- admin API on a hosted database ----------------------------------------------------------------------------
@pytest.mark.real_defaults
def test_a_short_admin_token_disables_the_admin_api_on_a_hosted_database(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "short-token")
    app = create_app(":memory:", lister=lambda *a, **k: [], detailer=detailer)
    c = TestClient(app)
    app.state.db.pg = False                                                                                   # behave as a local database
    assert c.get("/api/admin/settings", headers={"X-Admin-Token": "short-token"}).status_code == 200      # local database: fine
    app.state.db.pg = True                                                                                    # behave as hosted Postgres
    r = c.get("/api/admin/settings", headers={"X-Admin-Token": "short-token"})
    assert r.status_code == 503 and "at least 32 characters" in r.text and "short-token" not in r.text
    monkeypatch.setenv("ADMIN_TOKEN", "x" * 40)
    app.state.db.pg = False                                                                                   # settings are read through the real engine below
    assert c.get("/api/admin/settings", headers={"X-Admin-Token": "x" * 40}).status_code == 200


# ---- follow-up: CORS header, committed estimate, unexpected errors -------------------------------------------------
def test_cors_allows_the_access_code_header_when_pages_are_on_another_host(monkeypatch):
    monkeypatch.setenv("FORGE_CORS_ORIGINS", "https://pages.example.org")
    app = create_app(":memory:", lister=lambda *a, **k: [], detailer=detailer)
    r = TestClient(app).options("/api/runs", headers={"Origin": "https://pages.example.org", "Access-Control-Request-Method": "POST",
                                                      "Access-Control-Request-Headers": "X-Access-Code"})
    assert r.status_code == 200 and "x-access-code" in r.headers["access-control-allow-headers"].lower()


def test_environment_report_shows_the_committed_estimate(hosted):
    make(hosted, "tester 1", 3); make(hosted, "tester 2", 2)
    j = hosted.get("/api/admin/environment", headers=ADMIN).json()["access_codes"]["budget_reservation"]
    assert j == {"outstanding_runs": 5, "estimated_run_cost_usd": 0.44, "committed_estimate_usd": 2.2,
                 "recorded_spend_estimate_usd": 0.0, "total_usd": 2.2, "pilot_budget_usd": 9.0}


def test_an_unexpected_error_marks_the_run_failed_and_refunds_when_nothing_was_billed(monkeypatch):
    monkeypatch.setenv("ADMIN_TOKEN", "admin-secret-token-for-tests-1234567890"); monkeypatch.setenv("FORGE_SALT", "s")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: PricedMock([factors_json()]))
    def broken(*a, **k): raise ValueError("secret detail sk-ant-LEAK")
    app = create_app(":memory:", lister=broken, detailer=detailer); app.state.db.set_setting("require_access_code", True)
    c = TestClient(app, raise_server_exceptions=False); c.db = app.state.db
    out = make(c)
    r = run(c, out["code"])
    assert r.status_code == 500
    row = c.db.q("SELECT status, error FROM runs", one=True)
    assert row["status"] == "failed" and row["error"] == "unexpected error: ValueError" and "LEAK" not in row["error"]
    assert c.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 0
    assert run(c, out["code"]).status_code == 500                              # the in-flight slot was released too
