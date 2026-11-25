"""Time the judging step on the stored corpus with the live model. COSTS MONEY: keep --n small (3 to 5).
  python scripts/bench_judging.py --db forge.db --n 5 --workers 5 [--effort low|medium|high] [--model ID]
Same profile and same shortlist every time, so runs are comparable. Prints seconds, tokens and one line per call."""
import argparse, json, os, sys, time
sys.path.insert(0, ".")
from app.db import Database
from app import store
from app.pipeline import run_match
from app.adapters.claude import ClaudeAdapter

PROFILE = {"career_stage": "established",
           "lanes": ["plant photobiology and flavin photochemistry", "photoreceptor signalling in algae and plants"],
           "positioning_rules": []}
Q = "Does this opportunity fit this researcher?"

ap = argparse.ArgumentParser()
ap.add_argument("--db", required=True); ap.add_argument("--n", type=int, default=3)
ap.add_argument("--workers", type=int, default=1); ap.add_argument("--effort"); ap.add_argument("--model")
ap.add_argument("--lane", action="append"); ap.add_argument("--max-tokens", type=int, default=3000)
a = ap.parse_args()
if a.lane: PROFILE = dict(PROFILE, lanes=a.lane)
db = Database(a.db)
s = db.settings(); s.update(max_judgments=a.n, judge_concurrency=a.workers)
lister, detailer = store.sources(db)
ad = ClaudeAdapter(model=a.model, effort=a.effort, max_tokens=a.max_tokens)
rid = db.create_run("bench", "pi_name", "bench", s, "bench", ad.name)
t = time.time()
out = run_match(db, rid, ad, s, PROFILE, Q, lister=lister, detailer=detailer)
wall = time.time() - t
c = out["counters"]
print(f"model={ad.model} effort={ad.effort} workers={c['judge_concurrency']} n={c['judged']} failures={c['model_failures']}")
print(f"wall {wall:.1f}s (judging {c['judging_ms']/1000:.1f}s)  calls={len(ad.call_log)}  in={c['input_tokens']} out={c['output_tokens']}")
for x in ad.call_log: print("  call", x)
rows = [json.loads(r["data"]) for r in db.q("SELECT data FROM run_matches WHERE run_id=?", (rid,))]
print("all judged (number: tier / centrality):")
for r in sorted(rows, key=lambda r: r["number"]):
    print(f"  {r['number']}: {r['tier']} / {r['how_calculated']['factors'].get('centrality')}")
