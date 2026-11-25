"""Fill or refresh the stored Grants.gov copy from a command line or a scheduled job (no web request involved).
  python scripts/ingest.py [--db URL_OR_PATH] [--statuses posted,forecasted] [--window-months 12]
The database defaults to FORGE_DB. Applies pending schema migrations first. Prints one JSON summary line.
Exit code 0 = finished with every detail stored; 1 = finished but some details failed; 2 = could not run.
Needs only api.grants.gov and the database; no model key. About 70 s for 1,400 records against local SQLite."""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.db import Database
from app import store
from app.sources.grants_gov import SourceError


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.environ.get("FORGE_DB", "forge.db"))
    ap.add_argument("--statuses", default="posted,forecasted")
    ap.add_argument("--window-months", type=int, default=12)
    a = ap.parse_args(argv)
    try:
        db = Database(a.db)
        out = store.ingest(db, statuses=tuple(x.strip() for x in a.statuses.split(",") if x.strip()),
                           detail_window_months=a.window_months)
    except SourceError as e:
        print(json.dumps({"ok": False, "error": f"source unavailable: {e}"})); return 2
    except Exception as e:                                   # never print the database address: it may hold a password
        print(json.dumps({"ok": False, "error": f"{type(e).__name__}"})); return 2
    out.update(ok=out["details_failed"] == 0, schema_version=db.schema_version())
    print(json.dumps(out))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
