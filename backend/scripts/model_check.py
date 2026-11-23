"""Live model check: does the model return schema-valid JSON whose quotes the validator accepts?
Usage: ANTHROPIC_API_KEY=... python scripts/model_check.py   (add --mock to dry-run)
Cases are FICTIONAL. Replace/extend with real announcements for the gold set."""
import json, sys
sys.path.insert(0, ".")
from app.adapters.base import SchemaError
from app.validator import validate

CASES = [
 {"q": "Researcher: studies machine learning for rural health access. Fit and eligibility?",
  "sources": {"opp": "Sample NOFO. Supports data-driven methods that improve access to care in rural communities. Proposals are due March 15, 2027.",
              "pi": "Sample PI A develops machine learning methods for rural health access."}},
 {"q": "Researcher: studies battery materials. Fit and eligibility?",
  "sources": {"opp": "Sample NOFO. Supports digitization of cultural collections. Applicant eligibility is described in Section III.",
              "pi": "Sample PI C studies battery materials discovery."}},
]

def main():
    if "--mock" in sys.argv:
        from app.adapters.mock import MockAdapter
        a = MockAdapter([json.dumps({"fit": "Low", "eligibility": "Needs verification", "rationale": "x", "fit_citations": [], "eligibility_citations": []})])
    else:
        from app.adapters.claude import ClaudeAdapter
        a = ClaudeAdapter()
    ok = 0
    for i, c in enumerate(CASES, 1):
        try:
            r = validate(a.judge(c["sources"], c["q"]), c["sources"])
            ok += 1
            print(i, r["fit"], r["eligibility"], "pass-rate", r["citation_pass_rate"], "failed:", len(r["failed_citations"]))
        except SchemaError as e:
            print(i, "SCHEMA FAIL", e)
    print(f"{ok}/{len(CASES)} schema-valid")
main()
