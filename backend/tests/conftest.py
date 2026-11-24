"""Optional: run the whole suite against a real Postgres.
  FORGE_TEST_PG_URL=postgresql://user@localhost:5432/forge_test python3 -m pytest
Each test that asks for ':memory:' gets a freshly emptied Postgres schema instead. Without the variable
nothing changes and the suite runs on in-memory SQLite."""
import os
import pytest


@pytest.fixture(autouse=True)
def _postgres_for_memory_tests(monkeypatch):
    url = os.environ.get("FORGE_TEST_PG_URL")
    if not url:
        yield; return
    import app.main as main
    import app.db as dbmod
    real = dbmod.Database

    class PgDatabase(real):
        def __init__(self, path=":memory:"):
            if path == ":memory:":
                import psycopg
                with psycopg.connect(url, autocommit=True) as c:
                    c.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
                path = url
            super().__init__(path)

    monkeypatch.setattr(main, "Database", PgDatabase)
    yield
