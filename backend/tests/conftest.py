"""Optional: run the whole suite against a real Postgres.
  FORGE_TEST_PG_URL=postgresql://user@localhost:5432/forge_test python3 -m pytest
Each test that asks for ':memory:' gets a freshly emptied Postgres schema instead. Without the variable
nothing changes and the suite runs on in-memory SQLite."""
import os
import pytest


@pytest.fixture(autouse=True)
def _generous_limits_for_tests(request, monkeypatch):
    """Production defaults are sized to the pilot budget (6 runs a day, 3 an hour per visitor, 15 judgments). Tests
    that make many runs keep their own fixtures: the earlier generous numbers. Mark a test `real_defaults` to see the
    production defaults."""
    if request.node.get_closest_marker("real_defaults"):
        yield; return
    import app.db as dbmod
    import app.main as mainmod
    monkeypatch.setattr(mainmod, "MIN_HOSTED_ADMIN_TOKEN", 0)          # tests use short admin tokens, also against Postgres
    for k, v in {"daily_cap": 200, "rate_limit_per_hour": 20, "max_judgments": 25, "require_access_code": False, "public_daily_cap": 200, "pi_lookups_per_hour": 60, "pi_lookups_per_day": 1000}.items():
        monkeypatch.setitem(dbmod.DEFAULT_SETTINGS, k, v)
    yield


@pytest.fixture(autouse=True)
def _postgres_for_memory_tests(monkeypatch):
    url = os.environ.get("FORGE_TEST_PG_URL")
    if not url:
        yield; return
    import app.main as main
    import app.db as dbmod
    real = dbmod.Database
    opened = []

    class PgDatabase(real):
        def __init__(self, path=":memory:"):
            if path == ":memory:":
                import psycopg
                with psycopg.connect(url, autocommit=True) as c:
                    c.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
                path = url
            super().__init__(path)
            opened.append(self)                     # closed after the test: the suite makes more databases than the server allows connections

    import sys
    for mod in list(sys.modules.values()):          # every module that imported Database by name (tests included)
        if getattr(mod, "Database", None) is real:
            monkeypatch.setattr(mod, "Database", PgDatabase)
    yield
    for d in opened:
        try: d.conn.close()
        except Exception: pass
