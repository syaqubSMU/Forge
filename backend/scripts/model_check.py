"""Model check on the gold set (PRD section 9 measures).
  python scripts/model_check.py --mock                    dry run, no model
  python scripts/model_check.py --responses FILE.json     score saved model outputs {case_id: raw JSON string or object}
  ANTHROPIC_API_KEY=... python scripts/model_check.py --yes-spend-money     live Claude (costs money)
Reports: schema-valid, citation pass rate, silent-eligibility handling, and agreement with the
customer's expected labels (only for cases where she has filled them in)."""
import json, sys, os
sys.path.insert(0, ".")
from app.adapters.base import ModelAdapter, SchemaError
from app.validator import validate

GOLD = os.path.join(os.path.dirname(__file__), "..", "evals", "gold_set.json")


class PerCase(ModelAdapter):
    name = "saved-responses"
    def __init__(self, table): self.table, self.case = table, None
    def complete(self, system, prompt):
        r = self.table[self.case]
        return r if isinstance(r, str) else json.dumps(r)


def main():
    cases = json.load(open(GOLD))["cases"]
    if "--responses" in sys.argv:
        a = PerCase(json.load(open(sys.argv[sys.argv.index("--responses") + 1])))
    elif "--mock" in sys.argv:
        a = PerCase({c["id"]: {"fit": "Low", "eligibility": "Needs verification", "rationale": "mock",
                               "fit_citations": [], "eligibility_citations": []} for c in cases})
    else:
        sys.path.insert(0, os.path.dirname(__file__))
        from _spend_guard import guard
        guard("--yes-spend-money" in sys.argv, len(cases), "model_check (live)")
        from app.adapters.claude import ClaudeAdapter
        a = ClaudeAdapter()
    n = schema_ok = silent_n = silent_ok = cites = bad = lab = fit_agree = el_agree = 0
    rows = []
    for c in cases:
        n += 1
        if isinstance(a, PerCase): a.case = c["id"]
        try:
            j = a.judge(c["sources"], c["question"]); schema_ok += 1
        except (SchemaError, KeyError) as e:
            rows.append((c["id"], "SCHEMA FAIL", "", "", str(e)[:50])); continue
        r = validate(j, c["sources"])
        cites += len(j.fit_citations) + len(j.eligibility_citations); bad += len(r["failed_citations"])
        if c["eligibility_silent"]:
            silent_n += 1; silent_ok += r["eligibility"] == "Needs verification"
        agree = ""
        if c["expected_fit"] and c["expected_eligibility"]:
            lab += 1; f = r["fit"] == c["expected_fit"]; e = r["eligibility"] == c["expected_eligibility"]
            fit_agree += f; el_agree += e; agree = f"fit {'ok' if f else 'DIFF'}, elig {'ok' if e else 'DIFF'}"
        rows.append((c["id"], r["fit"], r["eligibility"], f"{r['citation_pass_rate']:.0%}", agree or "(no expected label yet)"))
    print(f"{'case':5} {'fit':7} {'eligibility':20} {'cites':6} agreement")
    for x in rows: print(f"{x[0]:5} {x[1]:7} {x[2]:20} {x[3]:6} {x[4]}")
    print(f"\nschema-valid: {schema_ok}/{n}")
    print(f"citations supported: {cites - bad}/{cites}" + (f" ({(cites-bad)/cites:.0%})" if cites else ""))
    print(f"silent-eligibility cases answered 'Needs verification': {silent_ok}/{silent_n}")
    print(f"agreement with expected labels: " + (f"fit {fit_agree}/{lab}, eligibility {el_agree}/{lab}" if lab else "not scored (labels blank)"))

main()
