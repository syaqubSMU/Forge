"""Show or apply schema migrations.  python scripts/migrate.py [--db URL_OR_PATH] [--status]
Servers apply pending migrations on start; use this to apply them ahead of a deploy."""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.db import Database
from app.migrations import MIGRATIONS

ap = argparse.ArgumentParser(); ap.add_argument("--db", default=os.environ.get("FORGE_DB", "forge.db")); ap.add_argument("--status", action="store_true")
a = ap.parse_args()
try:
    db = Database(a.db)                       # opening applies pending migrations
except Exception as e:
    print(f"could not open the database ({type(e).__name__})"); sys.exit(2)
print(f"schema version {db.schema_version()} of {MIGRATIONS[-1][0]}")
for v, name, _ in MIGRATIONS: print(f"  {v}: {name}")
