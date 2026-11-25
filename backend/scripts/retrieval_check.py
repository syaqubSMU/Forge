"""Compare candidate rankings on a frozen, labelled snapshot. No model, no network, no cost.
  python scripts/retrieval_check.py [--k 10]
Data: evals/retrieval_corpus.json.gz (787 posted Grants.gov records, retrieved 2026-11-25),
      evals/retrieval_labels.json (research-area queries and the records judged relevant).
Reports per query and overall: recall@k (share of relevant records in the top k), and MRR (1 / rank of the first
relevant record). Deadlines are ignored here because the snapshot's dates will go stale."""
import argparse, gzip, json, os, sys
sys.path.insert(0, ".")
from app.pipeline import rank_candidates, rank_candidates_overlap

HERE = os.path.join(os.path.dirname(__file__), "..", "evals")


def load():
    corpus = json.load(gzip.open(os.path.join(HERE, "retrieval_corpus.json.gz"), "rt", encoding="utf-8"))["records"]
    details = [{"source_record_id": r["id"], "title": r["title"], "description": r["text"], "close_date": None} for r in corpus]
    return details, json.load(open(os.path.join(HERE, "retrieval_labels.json")))["queries"]


def evaluate(rank, details, queries, k):
    rows = []
    for q in queries:
        profile = {"career_stage": "established", "lanes": q["lanes"], "positioning_rules": []}
        ranked = rank(details, profile, len(details))[0]
        ids = [d["source_record_id"] for d, _ in ranked]
        rel = set(q["relevant"])
        hit = len(rel & set(ids[:k]))
        first = next((i + 1 for i, x in enumerate(ids) if x in rel), None)
        rows.append({"id": q["id"], "recall": hit / len(rel), "mrr": (1 / first) if first else 0.0, "first": first,
                     "considered": len(ids)})
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--k", type=int, default=10); a = ap.parse_args()
    details, queries = load()
    out = {}
    for name, fn in (("word overlap (old)", rank_candidates_overlap), ("BM25", rank_candidates)):
        out[name] = evaluate(fn, details, queries, a.k)
    print(f"{'query':9}" + "".join(f"| {n:>26} " for n in out))
    for i, q in enumerate(queries):
        print(f"{q['id']:9}" + "".join(f"| recall@{a.k} {r[i]['recall']:.2f} first@{str(r[i]['first']):>4} " for r in out.values()))
    for n, r in out.items():
        print(f"{n:20} mean recall@{a.k} {sum(x['recall'] for x in r)/len(r):.2f}   MRR {sum(x['mrr'] for x in r)/len(r):.2f}")
    return out


if __name__ == "__main__":
    main()
