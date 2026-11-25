"""Run the same input several times and report how much the result varies. COSTS MONEY: runs x n live calls.
  python scripts/repeatability.py --db forge.db --runs 4 --n 8 [--effort low] [--lane "..."]
The candidate set is fixed (ranking is deterministic), so any difference comes from the model.
Reports, per item, how many runs agreed on the tier, and how similar the visible result lists were."""
import argparse, collections, itertools, json, os, sys, time
sys.path.insert(0, ".")
from app.db import Database
from app import store
from app.pipeline import run_match
from app.adapters.claude import ClaudeAdapter

ap = argparse.ArgumentParser()
ap.add_argument("--db", required=True); ap.add_argument("--runs", type=int, default=4); ap.add_argument("--n", type=int, default=8)
ap.add_argument("--workers", type=int, default=8); ap.add_argument("--effort"); ap.add_argument("--lane", action="append", required=True); ap.add_argument("--yes-spend-money", action="store_true")
a = ap.parse_args()
sys.path.insert(0, os.path.dirname(__file__))
from _spend_guard import guard
guard(a.yes_spend_money, a.runs * a.n, "repeatability")
db = Database(a.db); lister, detailer = store.sources(db)
profile = {"career_stage": "established", "lanes": a.lane, "positioning_rules": []}
tiers = collections.defaultdict(list); lists = []; secs = []; tok = [0, 0]
for i in range(a.runs):
    s = db.settings(); s.update(max_judgments=a.n, judge_concurrency=a.workers)
    ad = ClaudeAdapter(effort=a.effort); rid = db.create_run("repeat", "pi_name", "repeat", s, "repeat", ad.name)
    t = time.time(); out = run_match(db, rid, ad, s, profile, "Does this opportunity fit this researcher?", lister=lister, detailer=detailer)
    secs.append(time.time() - t); tok[0] += ad.total_usage["input_tokens"]; tok[1] += ad.total_usage["output_tokens"]
    for r in db.q("SELECT data FROM run_matches WHERE run_id=?", (rid,)):
        d = json.loads(r["data"]); tiers[d["number"]].append(d["tier"])
    lists.append({r["number"] for r in out["results"]})
same = sum(1 for v in tiers.values() if len(set(v)) == 1)
jac = [len(x & y) / len(x | y) if x | y else 1.0 for x, y in itertools.combinations(lists, 2)]
print(f"effort={a.effort} runs={a.runs} items={len(tiers)} mean wall {sum(secs)/len(secs):.1f}s tokens in/out {tok[0]}/{tok[1]}")
print(f"items with the same tier in every run: {same}/{len(tiers)}")
print(f"visible-list similarity (Jaccard, mean over run pairs): {sum(jac)/len(jac):.2f}; list sizes {[len(x) for x in lists]}")
for k, v in sorted(tiers.items()):
    if len(set(v)) > 1: print("  varies:", k, dict(collections.Counter(v)))
