"""Numbered schema migrations, the same on SQLite and Postgres.

Each migration is (version, name, [SQL statements]). Statements use `{PK}` for an auto-numbered integer key and
must be valid on both engines. Applied versions are recorded in `schema_migrations`; a migration runs once, in order,
inside one transaction. Never edit a migration that has shipped: add a new one.

Version 1 is the schema as it stood before versioning. It is written with IF NOT EXISTS, so a database created by an
earlier release is adopted as version 1 without changes.
"""

BASELINE = """
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, created_at TEXT, visitor_hash TEXT, input_type TEXT, input_text TEXT,
  scope_snapshot TEXT, settings_snapshot TEXT, rubric_version TEXT, model TEXT, latency_ms INTEGER, status TEXT, error TEXT, archived INTEGER DEFAULT 0,
  input_tokens INTEGER DEFAULT 0, output_tokens INTEGER DEFAULT 0, opportunities_listed INTEGER DEFAULT 0, details_fetched INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS run_source_failures(id {PK}, run_id TEXT, source_id TEXT, error TEXT);
CREATE TABLE IF NOT EXISTS run_sources(id {PK}, run_id TEXT, source_id TEXT, url TEXT, retrieved_at TEXT, text_hash TEXT);
CREATE TABLE IF NOT EXISTS run_matches(id {PK}, run_id TEXT, data TEXT);
CREATE TABLE IF NOT EXISTS run_citations(id {PK}, run_id TEXT, source_id TEXT, quote TEXT, validated INTEGER, reason TEXT);
CREATE TABLE IF NOT EXISTS email_events(id {PK}, run_id TEXT, draft TEXT, recipient TEXT, confirmed INTEGER, mode TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS chat_entries(id {PK}, run_id TEXT, role TEXT, text TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS annotations(id {PK}, run_id TEXT, label TEXT, note TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS admin_audit(id {PK}, at TEXT, actor TEXT, action TEXT, detail TEXT);
CREATE TABLE IF NOT EXISTS rubric_versions(version TEXT PRIMARY KEY, body TEXT, status TEXT, created_at TEXT, published_at TEXT, note TEXT);
CREATE TABLE IF NOT EXISTS opportunities(source_record_id TEXT PRIMARY KEY, source_system TEXT, number TEXT, title TEXT, sponsor TEXT,
  agency_code TEXT, status TEXT, open_date TEXT, close_date TEXT, url TEXT, detail TEXT, text_hash TEXT, listed_at TEXT, detail_at TEXT);
CREATE TABLE IF NOT EXISTS api_calls(id {PK}, at TEXT, source TEXT, endpoint TEXT, params TEXT, ok INTEGER,
  http_status INTEGER, latency_ms INTEGER, error TEXT, ingest_id TEXT);
CREATE INDEX IF NOT EXISTS ix_opps_close ON opportunities(close_date);
CREATE INDEX IF NOT EXISTS ix_calls_at ON api_calls(at);
CREATE INDEX IF NOT EXISTS ix_runs_visitor ON runs(visitor_hash, created_at);
"""


def statements(sql: str) -> list:
    return [s.strip() for s in sql.split(";") if s.strip()]


MIGRATIONS = [
    (1, "baseline schema", statements(BASELINE)),
    (2, "cost per run", ["ALTER TABLE runs ADD COLUMN cost_usd REAL"]),
]
