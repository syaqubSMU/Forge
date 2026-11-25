"""The open demo window: live searches open to everyone, with protections for code holders and the budget. Fakes only."""
import pytest
from fastapi.testclient import TestClient

from app.adapters import registry
from app.db import DEFAULT_SETTINGS
from app.main import create_app
from tests.test_access_codes import ADMIN, detailer, make, run, err
from tests.test_openalex import FakeClient
from tests.test_pipeline import CORPUS, factors_json, PricedMock


@pytest.fixture
def window(monkeypatch):
    """Codes NOT required, production-like limits: public_daily_cap 4, daily_cap 12, budget 9.0, 15 judgments."""
    monkeypatch.setenv("ADMIN_TOKEN", "admin-secret-token-for-tests-1234567890"); monkeypatch.setenv("FORGE_SALT", "test-salt-value")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: PricedMock([factors_json()]))
    app = create_app(":memory:", lister=lambda *a, **k: [dict(o) for o in CORPUS], detailer=detailer, openalex_client=FakeClient())
    d = app.state.db
    for k, v in {"require_access_code": False, "public_daily_cap": 4, "daily_cap": 12, "max_judgments": 15, "rate_limit_per_hour": 100}.items():
        d.set_setting(k, v)
    c = TestClient(app); c.db = d
    return c


def env(c):
    return c.get("/api/admin/environment", headers=ADMIN).json()


# (a) a code that is sent is honoured even when codes are not required ----------------------------------------------
def test_no_code_is_a_public_run_when_codes_are_not_required(window):
    r = run(window)
    assert r.status_code == 200 and "access" not in r.json()
    assert window.db.q("SELECT access_code_id FROM runs", one=True)["access_code_id"] is None


def test_a_valid_code_is_used_and_claimed_even_when_not_required(window):
    out = make(window); r = run(window, out["code"])
    assert r.status_code == 200 and r.json()["access"] == {"remaining": 2}
    assert window.db.q("SELECT access_code_id FROM runs", one=True)["access_code_id"] == out["id"]
    assert window.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 1


def test_an_invalid_code_is_refused_even_when_not_required(window):
    r = run(window, "fsa_not-real")
    assert r.status_code == 403 and err(r)["code"] == "invalid"
    assert window.db.q("SELECT COUNT(*) c FROM runs", one=True)["c"] == 0           # it did not silently fall back to a public run


def test_expired_revoked_and_used_up_codes_keep_their_messages_in_open_mode(window):
    exp = make(window, "e", expires_at="2020-01-01")["code"]; assert err(run(window, exp))["code"] == "expired"
    one = make(window, "o", allowance=1)["code"]; assert run(window, one).status_code == 200
    assert err(run(window, one))["code"] == "allowance_used"


def test_check_endpoint_in_open_mode(window):
    out = make(window)
    assert window.get("/api/access/check").json() == {"required": False, "valid": True}
    r = window.get("/api/access/check", headers={"X-Access-Code": out["code"]})
    assert r.json()["valid"] is True and r.json()["required"] is False and r.json()["remaining"] == 3
    assert err(window.get("/api/access/check", headers={"X-Access-Code": "fsa_x"}))["code"] == "invalid"


# (b) two limits ------------------------------------------------------------------------------------------------------
def test_public_runs_have_their_own_cap_and_code_holders_are_not_blocked(window):
    out = make(window, allowance=3)
    assert [run(window).status_code for _ in range(4)] == [200, 200, 200, 200]
    r = run(window); d = err(r)
    assert r.status_code == 503 and d["code"] == "public_cap_reached" and d["recorded_example"] is True
    assert "codes still work" in d["message"] and "18:00 Central" in d["message"]
    assert run(window, out["code"]).status_code == 200                                  # the public rush did not block the code holder


def test_the_overall_daily_cap_still_applies_to_everyone(window):
    window.db.set_setting("daily_cap", 2)
    out = make(window)
    assert run(window).status_code == 200 and run(window, out["code"]).status_code == 200
    assert run(window).status_code == 503 and run(window, out["code"]).status_code == 503


# (c) the public cannot eat the budget reserved to code holders -------------------------------------------------
def test_a_public_run_is_refused_when_it_would_eat_reserved_allowances(window):
    for i in range(6): make(window, f"tester {i + 1}", 3)
    make(window, "owner", 2)                                  # 20 runs reserved = $9.00, the whole budget
    r = run(window); d = err(r)
    assert r.status_code == 503 and d["code"] == "budget_reached" and "reserved for approved testers" in d["message"] and "codes still work" in d["message"]


def test_a_code_holder_is_refused_only_once_spend_has_reached_the_limit(window):
    out = make(window, allowance=3)
    window.db.set_setting("pilot_budget_usd", 1.0)
    window.db.set_setting("price_per_mtok_input", 1000.0); window.db.set_setting("price_per_mtok_output", 1000.0)
    assert run(window, out["code"]).status_code == 200        # spend 0 < 1.0: allowed although reserved runs exceed the budget
    assert run(window, out["code"]).status_code == 503        # recorded spend now reached the limit: everyone is stopped
    assert err(run(window, out["code"]))["code"] == "budget_reached"


def test_public_runs_are_allowed_while_there_is_unreserved_budget(window):
    make(window, "tester 1", 3)                               # 3 reserved ($1.35 of $9.00)
    assert run(window).status_code == 200


def test_no_budget_protection_for_public_runs_when_prices_are_off(window):
    window.db.set_setting("price_per_mtok_input", 0.0); window.db.set_setting("price_per_mtok_output", 0.0)
    for i in range(6): make(window, f"tester {i + 1}", 3)
    assert run(window).status_code == 200                      # budget stop inactive: documented, and the environment report says so


# (d) environment report ----------------------------------------------------------------------------------------
def test_environment_report_shows_todays_counts_and_remaining_capacity(window):
    out = make(window)
    run(window); run(window); run(window, out["code"])
    j = env(window)
    t = j["today"]
    assert t["runs_today"] == 3 and t["runs_today_public"] == 2 and t["runs_today_with_code"] == 1
    assert t["public_daily_cap"] == 4 and t["public_capacity_remaining"] == 2 and t["daily_capacity_remaining"] == 9
    assert "18:00 Central" in t["day_resets_at"] and t["utc_date"]
    assert j["access_codes"]["required"] is False and j["access_codes"]["budget_reservation"]["committed_estimate_usd"] == 0.9


# (e) lookups ----------------------------------------------------------------------------------------------------------
def test_lookup_defaults_are_tightened_and_work_without_a_code_in_open_mode(window):
    assert window.post("/api/pi/search", json={"name": "Pat Example"}).status_code == 200
    out = make(window)
    assert window.post("/api/pi/search", json={"name": "Pat Example"}, headers={"X-Access-Code": out["code"]}).status_code == 200
    assert err(window.post("/api/pi/search", json={"name": "Pat Example"}, headers={"X-Access-Code": "fsa_bad"}))["code"] == "invalid"
    assert window.db.q("SELECT runs_used FROM access_codes", one=True)["runs_used"] == 0


@pytest.mark.real_defaults
def test_production_lookup_limits_are_twenty_an_hour_and_two_hundred_a_day():
    assert DEFAULT_SETTINGS["pi_lookups_per_hour"] == 20 and DEFAULT_SETTINGS["pi_lookups_per_day"] == 200
    assert DEFAULT_SETTINGS["public_daily_cap"] == 4 and DEFAULT_SETTINGS["daily_cap"] == 12 and DEFAULT_SETTINGS["require_access_code"] is True


# code-required mode behaves as before ----------------------------------------------------------------------------
def test_code_required_mode_still_refuses_a_public_run(window):
    window.db.set_setting("require_access_code", True)
    assert err(run(window))["code"] == "missing"
