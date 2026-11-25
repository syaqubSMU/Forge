"""Record ONE real run (live model, costs money) for the public pages, from the stored public Grants.gov copy.
  python scripts/record_run.py --db forge.db --out ../public/signal/recorded-run.js --yes-spend-money [--price-in 4.0 --price-out 20.0]
Prints the planned calls and estimated cost first and refuses to call the model without --yes-spend-money. Uses a COPY of a SQLite database, so
the original is untouched. Fictional researcher only (see app/recording.py). Writes nothing unless every quote is
found in its stored source text, and exports the run's logged detail next to the file (its sha256 is recorded in the file). Never run it without the approvals the project requires."""
import argparse, json, os, shutil, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.db import Database
from app.recording import record, to_js, FICTIONAL_PROFILE, integrity_checks, verify_file
sys.path.insert(0, os.path.dirname(__file__))
from _spend_guard import guard

ap = argparse.ArgumentParser()
ap.add_argument("--db", default=os.environ.get("FORGE_DB", "forge.db"))
ap.add_argument("--out", required=True)
ap.add_argument("--max-judgments", type=int, default=15)
ap.add_argument("--effort"); ap.add_argument("--price-in", type=float); ap.add_argument("--price-out", type=float)
ap.add_argument("--yes-spend-money", action="store_true", help="required to call the live model")
ap.add_argument("--verify", action="store_true", help="only re-check an existing file at --out (no model, no cost)")
a = ap.parse_args()
if a.verify:
    detail_path = os.path.splitext(a.out)[0] + ".run-detail.json"
    detail = open(detail_path, encoding="utf-8").read() if os.path.exists(detail_path) else None
    res = verify_file(open(a.out, encoding="utf-8").read(), detail)
    for rule, ok in res: print(("PASS " if ok else "FAIL ") + rule)
    sys.exit(0 if all(ok for _, ok in res) else 1)
if a.db.startswith(("postgres://", "postgresql://")) or a.db == ":memory:":
    sys.exit("use a SQLite file holding the stored copy; it is copied, never written to")
if not 1 <= a.max_judgments <= 25:
    sys.exit("max-judgments must be 1 to 25")
print(f"Fictional researcher: {FICTIONAL_PROFILE['investigator']}; areas: {FICTIONAL_PROFILE['lanes']}")
guard(a.yes_spend_money, a.max_judgments, "record_run", max_calls=30)
if a.yes_spend_money and not (a.price_in and a.price_out):
    sys.exit("pass --price-in and --price-out (USD per million tokens) so the cost estimate is recorded; nothing was spent")
from app.adapters.claude import ClaudeAdapter
tmp = os.path.join(tempfile.mkdtemp(), "copy.db"); shutil.copy(a.db, tmp)
db = Database(tmp)
prices = {"price_per_mtok_input": a.price_in or 0, "price_per_mtok_output": a.price_out or 0}
sink = []
rec = record(db, ClaudeAdapter(effort=a.effort), db.settings(), max_judgments=a.max_judgments, effort=a.effort, prices=prices, detail_sink=sink)
checks = integrity_checks(rec)
for rule, ok in checks: print(("PASS " if ok else "FAIL ") + rule)
if not all(ok for _, ok in checks):
    sys.exit("integrity check failed: no file written")
detail_path = os.path.splitext(a.out)[0] + ".run-detail.json"
open(a.out, "w", encoding="utf-8").write(to_js(rec))
open(detail_path, "w", encoding="utf-8").write(sink[0])
print(f"run detail exported to {detail_path} (sha256 {rec['recorded_run']['run_detail']['sha256']}); code commit {rec['recorded_run']['code_commit']}")
c, q = rec["counters"], rec["recorded_run"]["quote_check"]
print(f"wrote {a.out}: {len(rec['results'])} results, judged {c['judged']}, tokens {c['input_tokens']}/{c['output_tokens']}, cost {c['cost_usd']}")
print(f"quote check: {q['quotes_supported']}/{q['quotes_checked']} supported, {q['quotes_failed']} failed")
