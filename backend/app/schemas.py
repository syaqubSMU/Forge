"""Fixed output schema for fit/eligibility judgments (PRD FR-8, FR-11)."""
from dataclasses import dataclass, field

FIT = ("High", "Medium", "Low")
ELIGIBILITY = ("Eligible", "Not eligible", "Needs verification")
NO_SUPPORT = "No explicit support found in the provided sources."


@dataclass
class Citation:
    quote: str
    source_id: str  # key into the sources dict (URL)


@dataclass
class Judgment:
    fit: str
    eligibility: str
    rationale: str
    fit_citations: list = field(default_factory=list)
    eligibility_citations: list = field(default_factory=list)


class SchemaError(ValueError):
    pass


def parse_judgment(data: dict) -> Judgment:
    """Strictly parse model output. Raises SchemaError on any deviation."""
    if not isinstance(data, dict):
        raise SchemaError("output is not an object")
    if data.get("fit") not in FIT:
        raise SchemaError("fit must be High, Medium or Low")
    if data.get("eligibility") not in ELIGIBILITY:
        raise SchemaError("eligibility must be Eligible, Not eligible or Needs verification")
    if not isinstance(data.get("rationale"), str):
        raise SchemaError("rationale must be a string")

    def cites(key):
        out = []
        for c in data.get(key, []):
            if not isinstance(c, dict) or not isinstance(c.get("quote"), str) or not isinstance(c.get("source_id"), str):
                raise SchemaError(f"{key} entries need quote and source_id strings")
            out.append(Citation(c["quote"], c["source_id"]))
        return out

    return Judgment(data["fit"], data["eligibility"], data["rationale"],
                    cites("fit_citations"), cites("eligibility_citations"))
