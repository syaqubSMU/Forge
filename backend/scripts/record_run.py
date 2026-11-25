"""Record ONE real run (live model, costs money) for the public pages, from the stored public Grants.gov copy.
  python scripts/record_run.py --db forge.db --out ../public/signal/recorded-run.js --yes-spend [--price-in 4.0 --price-out 20.0]
Prints the expected cost first and refuses to call the model without --yes-spend. Uses a COPY of a SQLite database, so
the original is untouched. Fictional researcher only (see app/recording.py). Writes nothing unless every quote is
found in its source. Never run it without the approvals the project requires."""
import argparse, json, os, shutil, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.db import Database
from app.recording import record, to_js, FICTIONAL_PROFILE

ap = argparse.ArgumentParser()
ap.add_argument("--db", default=os.environ.get("FORGE_DB", "forge.db"))
ap.add_argument("--out", required=True)
ap.add_argument("--max-judgments", type=int, default=15)
ap.add_argument("--effort"); ap.add_argument("--price-in", type=float); ap.add_argument("--price-out", type=float)
ap.add_argument("--yes-spend", action="store_true", help="required to call the live model")
a = ap.parse_args()
if a.db.startswith(("postgres://", "postgresql://")) or a.db == ":memory:":
    sys.exit("use a SQLite file holding the stored copy; it is copied, never written to")
if not 1 <= a.max_judgments <= 25:
    sys.exit("max-judgments must be 1 to 25")
est = a.max_judgments * 0.03
print(f"Fictional researcher: {FICTIONAL_PROFILE['investigator']}; areas: {FICTIONAL_PROFILE['lanes']}")
print(f"Expected live calls: up to {a.max_judgments + 2}; expected cost about ${est:.2f} (list prices, estimate)")
if not a.yes_spend:
    sys.exit("not run: add --yes-spend to call the live model")
from app.adapters.claude import ClaudeAdapter
tmp = os.path.join(tempfile.mkdtemp(), "copy.db"); shutil.copy(a.db, tmp)
db = Database(tmp)
prices = {"price_per_mtok_input": a.price_in or 0, "price_per_mtok_output": a.price_out or 0}
rec = record(db, ClaudeAdapter(effort=a.effort), db.settings(), max_judgments=a.max_judgments, effort=a.effort, prices=prices)
open(a.out, "w", encoding="utf-8").write(to_js(rec))
c, q = rec["counters"], rec["recorded_run"]["quote_check"]
print(f"wrote {a.out}: {len(rec['results'])} results, judged {c['judged']}, tokens {c['input_tokens']}/{c['output_tokens']}, cost {c['cost_usd']}")
print(f"quote check: {q['quotes_supported']}/{q['quotes_checked']} supported, {q['quotes_failed']} failed")
