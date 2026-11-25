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
    assert PILOT_DEFAULTS == {"daily_cap": 6, "rate_limit_per_hour": 3, "max_judgments": 15}
    s = Database(":memory:").settings()
    assert (s["daily_cap"], s["rate_limit_per_hour"], s["max_judgments"]) == (6, 3, 15)


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
    assert r.returncode != 0 and "--yes-spend" in (r.stdout + r.stderr) and not (tmp_path / "o.js").exists()


def test_fictional_profile_has_no_real_names():
    p = recording.FICTIONAL_PROFILE
    assert "fictional" in p["investigator"].lower() and "fictional" in p["institution"].lower()
