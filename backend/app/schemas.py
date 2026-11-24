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


# ---------------------------------------------------------------- factor extraction (PRD FR-42)
@dataclass
class FactorJudgment:
    """What the MODEL returns: factor values with citations. It never picks the tier."""
    factors: dict
    eligibility: str
    rationale: str
    factor_citations: dict = field(default_factory=dict)      # factor name -> [Citation]
    eligibility_citations: list = field(default_factory=list)


def parse_factor_judgment(data: dict, rubric: dict) -> FactorJudgment:
    """Strict parse against the rubric's own factor list, so admin edits flow through."""
    if not isinstance(data, dict):
        raise SchemaError("output is not an object")
    if data.get("eligibility") not in ELIGIBILITY:
        raise SchemaError(f"eligibility must be one of {ELIGIBILITY}")
    if not isinstance(data.get("rationale"), str):
        raise SchemaError("rationale must be a string")
    raw_factors = data.get("factors")
    if not isinstance(raw_factors, dict):
        raise SchemaError("factors must be an object")
    factors, cites = {}, {}
    for name, spec in rubric["factors"].items():
        entry = raw_factors.get(name)
        if not isinstance(entry, dict):
            raise SchemaError(f"factors.{name} must be an object with 'value' and 'citations'")
        value = entry.get("value")
        if value not in spec["values"]:
            raise SchemaError(f"factors.{name}.value must be one of {list(spec['values'])}, got {value!r}")
        factors[name] = value
        cites[name] = _citations(entry.get("citations", []), f"factors.{name}.citations")
    return FactorJudgment(factors, data["eligibility"], data["rationale"], cites,
                          _citations(data.get("eligibility_citations", []), "eligibility_citations"))


def _citations(items, where) -> list:
    out = []
    for c in items or []:
        if not isinstance(c, dict) or not isinstance(c.get("quote"), str) or not isinstance(c.get("source_id"), str):
            raise SchemaError(f"{where} entries need quote and source_id strings")
        out.append(Citation(c["quote"], c["source_id"]))
    return out
