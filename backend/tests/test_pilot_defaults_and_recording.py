"""Pilot-safe defaults and the recorded-run builder. Fakes only: no live model call."""
import json
import pytest
from fastapi.testclient import TestClient

from app.adapters import registry
from app.adapters.mock import MockAdapter
from app.db import Database, DEFAULT_SETTINGS, PILOT_DEFAULTS
from app import recording
from app.main import create_app
from tests.test_pipeline import CORPUS, factors_json


@pytest.mark.real_defaults
def test_production_defaults_are_sized_to_the_budget():
    assert PILOT_DEFAULTS == {"daily_cap": 3, "rate_limit_per_hour": 3, "max_judgments": 15}
    s = Database(":memory:").settings()
    assert (s["daily_cap"], s["rate_limit_per_hour"], s["max_judgments"]) == (3, 3, 15)


@pytest.mark.real_defaults
def test_fourth_run_in_an_hour_is_refused_with_production_defaults(monkeypatch):
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: MockAdapter([factors_json()]))
    app = create_app(":memory:", lister=lambda *a, **k: [dict(o) for o in CORPUS],
                     detailer=lambda ids, **k: ([dict(o) for o in CORPUS if o["source_record_id"] in [str(i) for i in ids]], []))
    c = TestClient(app)
    body = {"input_type": "pi_name", "input_text": "x", "profile": {"career_stage": "e", "lanes": ["photochemistry and flavin biology"]}}
    assert [c.post("/api/runs", json=body).status_code for _ in range(4)] == [200, 200, 200, 429]


def test_tests_keep_their_generous_fixtures():
    assert DEFAULT_SETTINGS["daily_cap"] == 200 and DEFAULT_SETTINGS["max_judgments"] == 25


# ---- recorded run -------------------------------------------------------------------------------------------
def make_db_with_store():
    """A database holding two stored opportunities, so the recorder reads text exactly as production would."""
    db = Database(":memory:")
    from app import store
    docs = [{k: v for k, v in o.items() if k != "open_date"} for o in CORPUS[:2]]    # real detail records carry no open_date
    store.ingest(db, lister=lambda *a, **k: [dict(o) for o in CORPUS[:2]],
                 detailer=lambda ids, **k: ([dict(o) for o in docs if o["source_record_id"] in [str(i) for i in ids]], []))
    return db


def profile_for_test():
    return dict(recording.FICTIONAL_PROFILE, lanes=["photochemistry and flavin biology"])


def test_recorded_run_has_the_page_shape_and_a_clean_quote_check():
    db = make_db_with_store()
    rec = recording.record(db, MockAdapter([factors_json()]), db.settings(), profile=profile_for_test(), max_judgments=15)
    assert {"profile", "settings", "retrieved_at", "counters", "results", "excluded", "source_failures", "recorded_run"} <= set(rec)
    r = rec["recorded_run"]
    assert r["researcher_is_fictional"] is True and "fictional researcher" in r["label"]
    q = r["quote_check"]; assert q["quotes_checked"] > 0 and q["quotes_failed"] == 0 and q["quotes_supported"] == q["quotes_checked"]
    assert rec["results"] and rec["results"][0]["citations"]
    assert rec["counters"]["cost_usd"] is None and r["cost_note"] == "prices not set"
    js = recording.to_js(rec)
    assert js.startswith("/* RECORDED RUN") and "window.MOCK = " in js
    assert json.loads(js.split("window.MOCK = ", 1)[1].rstrip().rstrip(";"))["results"] == json.loads(json.dumps(rec["results"]))


def test_recorder_refuses_to_write_when_a_quote_is_not_in_its_source(monkeypatch):
    db = make_db_with_store()
    monkeypatch.setattr(recording, "source_text_for", lambda db, url: "completely different text")
    with pytest.raises(RuntimeError, match="not found in their source"):
        recording.record(db, MockAdapter([factors_json()]), db.settings(), profile=profile_for_test())


def test_recorder_refuses_when_nothing_could_be_rated():
    db = make_db_with_store()
    with pytest.raises(RuntimeError, match="nothing could be rated"):
        recording.record(db, MockAdapter(["{not json"]), db.settings(), profile=profile_for_test())


def test_recorder_cost_uses_prices_when_given():
    db = make_db_with_store()
    rec = recording.record(db, MockAdapter([factors_json()]), db.settings(), profile=profile_for_test(),
                           prices={"price_per_mtok_input": 4.0, "price_per_mtok_output": 20.0})
    assert rec["counters"]["cost_usd"] > 0 and "estimate" in rec["recorded_run"]["cost_note"]


def test_script_refuses_to_spend_without_the_flag(tmp_path):
    import subprocess, sys
    db = tmp_path / "x.db"; Database(str(db))
    r = subprocess.run([sys.executable, "scripts/record_run.py", "--db", str(db), "--out", str(tmp_path / "o.js")],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "--yes-spend-money" in (r.stdout + r.stderr) and not (tmp_path / "o.js").exists()


def test_fictional_profile_has_no_real_names():
    p = recording.FICTIONAL_PROFILE
    assert "fictional" in p["investigator"].lower() and "fictional" in p["institution"].lower()


# ---- application budget stop ----------------------------------------------------------------------------------
def _app(monkeypatch):
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: MockAdapter([factors_json()]))
    monkeypatch.setenv("ADMIN_TOKEN", "t")
    return create_app(":memory:", lister=lambda *a, **k: [dict(o) for o in CORPUS],
                      detailer=lambda ids, **k: ([dict(o) for o in CORPUS if o["source_record_id"] in [str(i) for i in ids]], []))


BODY = {"input_type": "pi_name", "input_text": "x", "profile": {"career_stage": "e", "lanes": ["photochemistry and flavin biology"]}}


def test_budget_stop_is_inactive_without_prices_and_says_so(monkeypatch):
    app = _app(monkeypatch); c = TestClient(app)
    j = c.get("/api/admin/environment", headers={"X-Admin-Token": "t"}).json()
    assert j["budget_stop"]["state"] == "inactive: prices not set"
    assert c.post("/api/runs", json=BODY).status_code == 200          # nothing stops a run while cost is unknown


def test_budget_stop_refuses_live_runs_once_the_recorded_estimate_reaches_the_limit(monkeypatch):
    app = _app(monkeypatch); c = TestClient(app); db = app.state.db
    for k, v in {"price_per_mtok_input": 1000.0, "price_per_mtok_output": 1000.0, "pilot_budget_usd": 0.0001}.items():
        db.set_setting(k, v)
    assert c.post("/api/runs", json=BODY).status_code == 200           # first run records a cost above the tiny limit
    r = c.post("/api/runs", json=BODY)
    assert r.status_code == 503 and r.json()["detail"]["code"] == "budget_reached" and "recorded example run" in r.json()["detail"]["message"]
    assert c.get("/api/admin/environment", headers={"X-Admin-Token": "t"}).json()["budget_stop"]["state"] == "reached"
    db.set_setting("pilot_budget_usd", 1e9)                            # raising the limit reopens runs
    assert c.post("/api/runs", json=BODY).status_code == 200


def test_budget_stop_reads_the_database_so_it_survives_a_restart(tmp_path, monkeypatch):
    path = str(tmp_path / "b.db")
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: MockAdapter([factors_json()]))
    a1 = create_app(path, lister=lambda *a, **k: [dict(o) for o in CORPUS],
                    detailer=lambda ids, **k: ([dict(o) for o in CORPUS if o["source_record_id"] in [str(i) for i in ids]], []))
    for k, v in {"price_per_mtok_input": 1000.0, "price_per_mtok_output": 1000.0, "pilot_budget_usd": 0.0001}.items():
        a1.state.db.set_setting(k, v)
    TestClient(a1).post("/api/runs", json=BODY)
    a2 = create_app(path, lister=lambda *a, **k: [], detailer=lambda *a, **k: ([], []))          # "restart"
    assert TestClient(a2).post("/api/runs", json=BODY).status_code == 503


@pytest.mark.parametrize("args", [["bench_judging.py", "--db", "x.db"], ["repeatability.py", "--db", "x.db", "--lane", "a"],
                                  ["model_check.py"], ["record_run.py", "--db", "x.db", "--out", "o.js"]])
def test_every_spending_script_prints_a_plan_and_refuses_without_the_flag(args, tmp_path):
    import subprocess, sys, os
    env = {k: v for k, v in os.environ.items() if k not in ("FORGE_API_KEY", "FORGE_MODEL_KEY", "SIGNAL_MODEL_KEY", "ANTHROPIC_API_KEY")}
    r = subprocess.run([sys.executable, "scripts/" + args[0]] + args[1:], capture_output=True, text=True, cwd=".", env=env)
    out = r.stdout + r.stderr
    assert r.returncode != 0 and "live model calls" in out and "cost" in out and "nothing was spent" in out


def test_model_check_dry_runs_still_need_no_flag():
    import subprocess, sys
    r = subprocess.run([sys.executable, "scripts/model_check.py", "--mock"], capture_output=True, text=True, cwd=".")
    assert r.returncode == 0 and "schema-valid" in r.stdout


def test_recorded_run_meets_the_integrity_rules_and_detects_edits():
    db = make_db_with_store()
    rec = recording.record(db, MockAdapter([factors_json()]), db.settings(), profile=profile_for_test())
    checks = recording.integrity_checks(rec)
    assert all(ok for _, ok in checks), [r for r, ok in checks if not ok]
    r = rec["recorded_run"]
    assert r["run_id"] and r["rubric_version"] and r["redactions"] == [] and r["input_sent"]["question"] and r["as_of_date"]
    assert recording.verify_file(recording.to_js(rec)) == checks
    edited = json.loads(json.dumps(rec)); edited["results"][0]["rationale"] = "edited by hand"
    assert not all(ok for _, ok in recording.integrity_checks(edited))
    assert not all(ok for _, ok in recording.verify_file(recording.to_js(edited)))


def test_recording_carries_real_provenance_and_an_exported_run_detail():
    db = make_db_with_store(); sink = []
    rec = recording.record(db, MockAdapter([factors_json()]), db.settings(), profile=profile_for_test(), detail_sink=sink)
    r = rec["recorded_run"]
    assert r["rubric_version"] not in ("", "recorded", None) and r["deadline_flags_as_of"] == r["as_of_date"] and r["code_commit"]
    row = db.q("SELECT rubric_version FROM runs WHERE id=?", (r["run_id"],), one=True)
    assert row["rubric_version"] == r["rubric_version"]                    # the run row carries the real hash too
    import hashlib
    assert len(sink) == 1 and hashlib.sha256(sink[0].encode()).hexdigest() == r["run_detail"]["sha256"]
    ok = recording.verify_file(recording.to_js(rec), sink[0]); assert all(v for _, v in ok)
    bad = recording.verify_file(recording.to_js(rec), sink[0] + " ")
    assert not all(v for _, v in bad) and bad[-1][0].startswith("exported run detail")


def test_record_run_needs_prices_so_cost_is_never_blank():
    import subprocess, sys, os
    env = {k: v for k, v in os.environ.items() if k not in ("FORGE_API_KEY", "FORGE_MODEL_KEY", "SIGNAL_MODEL_KEY", "ANTHROPIC_API_KEY")}
    r = subprocess.run([sys.executable, "scripts/record_run.py", "--db", "x.db", "--out", "o.js", "--yes-spend-money"],
                       capture_output=True, text=True, env=env)
    assert r.returncode != 0 and "--price-in" in (r.stdout + r.stderr) and "at most about 30" in r.stdout
