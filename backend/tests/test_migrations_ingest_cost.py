"""Schema versioning, the ingest command line and per-run cost. Fakes only; no network."""
import json, os, sqlite3, sys
import pytest
from app.db import Database, run_cost
from app.migrations import MIGRATIONS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def test_fresh_database_reaches_the_latest_version_and_is_idempotent():
    db = Database(":memory:")
    assert db.schema_version() == MIGRATIONS[-1][0]
    assert db.migrate() == []                                     # nothing pending the second time
    assert [r["version"] for r in db.q("SELECT version FROM schema_migrations ORDER BY version")] == [m[0] for m in MIGRATIONS]
    cols = db.q("SELECT cost_usd FROM runs LIMIT 1")              # migration 2 added the column
    assert cols == []


@pytest.mark.skipif(bool(os.environ.get("FORGE_TEST_PG_URL")), reason="builds a SQLite file by hand")
def test_database_from_before_versioning_is_adopted(tmp_path):
    from app.migrations import BASELINE
    path = str(tmp_path / "old.db")
    c = sqlite3.connect(path); c.executescript(BASELINE.replace("{PK}", "INTEGER PRIMARY KEY"))
    c.execute("INSERT INTO settings VALUES('active_model','\"claude\"')"); c.commit(); c.close()
    db = Database(path)
    assert db.schema_version() == MIGRATIONS[-1][0]
    assert db.settings()["active_model"] == "claude"             # existing data untouched


def test_a_failing_migration_rolls_back_and_is_not_recorded(monkeypatch):
    import app.db as dbmod
    db = Database(":memory:")
    monkeypatch.setattr(dbmod, "MIGRATIONS", MIGRATIONS + [(99, "bad", ["CREATE TABLE t99(x INTEGER)", "THIS IS NOT SQL"])])
    with pytest.raises(Exception):
        with db.lock: db.migrate()
    assert db.schema_version() == MIGRATIONS[-1][0]
    with pytest.raises(Exception):
        db.q("SELECT * FROM t99")


def test_run_cost_needs_prices_and_never_shows_zero_for_unknown():
    assert run_cost({"price_per_mtok_input": 0, "price_per_mtok_output": 0}, 1000, 1000) is None
    assert run_cost({"price_per_mtok_input": 5.0, "price_per_mtok_output": 0}, 1000, 1000) is None   # one price alone would understate
    assert run_cost({"price_per_mtok_input": 5.0, "price_per_mtok_output": 25.0}, 2_000_000, 400_000) == 20.0


def test_cost_is_logged_with_the_run(monkeypatch):
    from fastapi.testclient import TestClient
    from app.adapters import registry
    from tests.test_pipeline import factors_json, PricedMock
    monkeypatch.setitem(registry.PROVIDERS, "mock", lambda: PricedMock([factors_json()]))
    from app.main import create_app
    from tests.test_pipeline import CORPUS
    app = create_app(":memory:", lister=lambda *a, **k: [dict(o) for o in CORPUS],
                     detailer=lambda ids, **k: ([dict(o) for o in CORPUS if o["source_record_id"] in [str(i) for i in ids]], []))
    c = TestClient(app); db = app.state.db
    db.set_setting("price_per_mtok_input", 1000.0); db.set_setting("price_per_mtok_output", 1000.0)
    j = c.post("/api/runs", json={"input_type": "pi_name", "input_text": "x",
                                  "profile": {"career_stage": "e", "lanes": ["photochemistry and flavin biology"]}}).json()
    assert j["counters"]["cost_usd"] > 0
    row = db.q("SELECT cost_usd, input_tokens, output_tokens FROM runs WHERE id=?", (j["run_id"],), one=True)
    assert row["cost_usd"] == pytest.approx((row["input_tokens"] + row["output_tokens"]) / 1e6 * 1000, rel=1e-6)


def test_ingest_cli_reports_a_summary_and_exit_codes(tmp_path, capsys, monkeypatch):
    import ingest
    import app.store as store
    monkeypatch.setattr(store, "ingest", lambda db, **k: {"ingest_id": "x", "listed": 3, "details_requested": 3, "details_stored": 3,
                                                          "details_failed": 0, "seconds": 0.1})
    assert ingest.main(["--db", str(tmp_path / "a.db")]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ok"] and out["schema_version"] == MIGRATIONS[-1][0]
    monkeypatch.setattr(store, "ingest", lambda db, **k: {"listed": 3, "details_requested": 3, "details_stored": 2, "details_failed": 1, "seconds": 0})
    assert ingest.main(["--db", str(tmp_path / "a.db")]) == 1
    capsys.readouterr()
    assert ingest.main(["--db", "postgresql://u:secretpw@127.0.0.1:1/x"]) == 2
    assert "secretpw" not in capsys.readouterr().out


@pytest.mark.skipif(not os.environ.get("FORGE_TEST_PG_URL"), reason="needs FORGE_TEST_PG_URL")
def test_migrations_on_postgres_including_adoption_and_rollback(monkeypatch):
    import psycopg, app.db as dbmod
    from app.migrations import BASELINE
    url = os.environ["FORGE_TEST_PG_URL"]
    with psycopg.connect(url, autocommit=True) as c:
        c.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        for st in BASELINE.replace("{PK}", "BIGSERIAL PRIMARY KEY").split(";"):   # a database from before versioning
            if st.strip(): c.execute(st)
        c.execute("INSERT INTO settings VALUES('active_model','\"claude\"')")
    db = Database(url)
    assert db.pg and db.schema_version() == MIGRATIONS[-1][0] and db.settings()["active_model"] == "claude"
    assert db.migrate() == []
    monkeypatch.setattr(dbmod, "MIGRATIONS", MIGRATIONS + [(99, "bad", ["CREATE TABLE t99(x INTEGER)", "THIS IS NOT SQL"])])
    with pytest.raises(Exception):
        with db.lock: db.migrate()
    assert db.schema_version() == MIGRATIONS[-1][0]
    with pytest.raises(Exception):
        db.q("SELECT * FROM t99")                         # the first statement of the failed migration was rolled back
