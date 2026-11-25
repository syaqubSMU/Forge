"""Smoke test of a hosted database. Reads the address from FORGE_DB (never printed). Uses a throwaway run id and
removes what it writes. No model, no Grants.gov, no cost.
  FORGE_DB=postgresql://... python scripts/db_smoke.py
Checks: connect, migrations reach the latest version, write and read back a run, settings round trip,
measured round-trip latency, batched read of stored opportunities (if any are ingested), and recovery after the
connection is dropped (as an idle serverless database does)."""
import os, sys, time, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.db import Database
from app.migrations import MIGRATIONS
from app import store

url = os.environ.get("FORGE_DB", "")
if not url.startswith(("postgres://", "postgresql://")):
    print("FORGE_DB must be a postgresql:// URL in the environment"); sys.exit(2)
ok = True
def check(name, cond, extra=""):
    global ok; ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name + (f"  {extra}" if extra else ""))

try:
    t = time.time(); db = Database(url); check("connect and migrate", True, f"{time.time()-t:.2f}s")
except Exception as e:                                   # the address may hold a password: print the type only
    print("FAIL connect:", type(e).__name__); sys.exit(1)
check("schema at latest version", db.schema_version() == MIGRATIONS[-1][0], f"v{db.schema_version()}")
rid = "smoke" + uuid.uuid4().hex[:8]
s = db.settings()
db.q("INSERT INTO runs(id,created_at,status,input_text) VALUES(?,?,?,?)", (rid, "now", "smoke", "x"), write=True)
check("write and read a run", db.q("SELECT status FROM runs WHERE id=?", (rid,), one=True)["status"] == "smoke")
db.set_setting("smoke_probe", 1); check("settings round trip", db.settings().get("smoke_probe") == 1)
lat = []
for _ in range(20):
    t = time.time(); db.q("SELECT 1 AS x", one=True); lat.append(time.time() - t)
lat.sort(); check("round trip latency", True, f"median {lat[10]*1000:.0f} ms, worst {lat[-1]*1000:.0f} ms (20 reads)")
n = db.q("SELECT COUNT(*) c FROM opportunities WHERE detail IS NOT NULL", one=True)["c"]
if n:
    ids = [r["source_record_id"] for r in db.q("SELECT source_record_id FROM opportunities WHERE detail IS NOT NULL LIMIT 250")]
    t = time.time(); det, fail = store.stored_detailer(db)(ids); el = time.time() - t
    check("batched read of stored details", len(det) == len(ids) and not fail, f"{len(det)} records in {el:.2f}s")
else:
    print("SKIP batched read: no opportunities ingested yet (run scripts/ingest.py first)")
db.conn.close()                                          # simulate a dropped connection
try:
    check("recovers after the connection is dropped", db.q("SELECT 1 AS x", one=True)["x"] == 1)
except Exception as e:
    check("recovers after the connection is dropped", False, type(e).__name__)
db.q("DELETE FROM runs WHERE id=?", (rid,), write=True); db.q("DELETE FROM settings WHERE key='smoke_probe'", write=True)
print("RESULT:", "all checks passed" if ok else "SOME CHECKS FAILED"); sys.exit(0 if ok else 1)
