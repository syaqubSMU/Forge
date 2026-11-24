"""Data-driven rubric engine. A rubric is plain JSON (admin-editable, versioned), never hard-coded logic.

- decide rules: ordered, first match sets the tier.
- cap rules: applied after, lower the tier to at most the named tier.
- validate(): coverage (every factor combination gets a tier), unknown names, unreachable rules.
- run_examples(): worked examples that must pass before a rubric can be published.
- diff(): what changed between two versions.
"""
import hashlib, itertools, json
from dataclasses import dataclass, field


def load(path):
    with open(path) as f:
        return json.load(f)


def version(rubric: dict) -> str:
    """Stable content hash; recorded on every run so a result can be reproduced."""
    return hashlib.sha256(json.dumps(rubric, sort_keys=True).encode()).hexdigest()[:12]


def _matches(when: dict, factors: dict) -> bool:
    return all(factors.get(k) == v for k, v in when.items())


@dataclass
class Result:
    tier: str
    word: str | None
    rules: list = field(default_factory=list)
    rule_ids: list = field(default_factory=list)
    rubric_version: str = ""


def evaluate(rubric: dict, factors: dict) -> Result:
    for name, spec in rubric["factors"].items():
        if factors.get(name) not in spec["values"]:
            raise ValueError(f"factor '{name}' must be one of {list(spec['values'])}, got {factors.get(name)!r}")
    order = [t["name"] for t in rubric["tiers"]]       # low -> high
    words = {t["name"]: t["word"] for t in rubric["tiers"]}
    tier, reasons, ids = None, [], []
    for r in rubric["rules"]:
        if r["kind"] == "decide" and _matches(r["when"], factors):
            tier = r["tier"]; reasons.append(r["reason"]); ids.append(r["id"]); break
    if tier is None:
        raise ValueError("no rule decided a tier (rubric has a coverage gap)")
    for r in rubric["rules"]:
        if r["kind"] == "cap" and _matches(r["when"], factors) and order.index(tier) > order.index(r["tier"]):
            tier = r["tier"]; reasons.append(r["reason"]); ids.append(r["id"])
    return Result(tier, words[tier], reasons, ids, version(rubric))


def validate(rubric: dict) -> list:
    """Return a list of problems (empty = valid)."""
    p = []
    tiers = [t["name"] for t in rubric.get("tiers", [])]
    if len(set(tiers)) != len(tiers) or not tiers:
        p.append("tiers must be a non-empty list of unique names, ordered low to high")
    ids = [r["id"] for r in rubric.get("rules", [])]
    if len(set(ids)) != len(ids):
        p.append("rule ids must be unique")
    factors = rubric.get("factors", {})
    for name, spec in factors.items():
        default = spec.get("conservative_default")
        if default is not None and default not in spec.get("values", {}):
            p.append(f"factor '{name}': conservative_default '{default}' is not one of its values")
        if spec.get("evidence_required") and default is None:
            p.append(f"factor '{name}': evidence is required, so it needs a conservative_default")
    for r in rubric.get("rules", []):
        if r.get("kind") not in ("decide", "cap"):
            p.append(f"{r['id']}: kind must be 'decide' or 'cap'")
        if r.get("tier") not in tiers:
            p.append(f"{r['id']}: unknown tier '{r.get('tier')}'")
        if not r.get("reason"):
            p.append(f"{r['id']}: every rule needs a plain-language reason")
        for k, v in r.get("when", {}).items():
            if k not in factors:
                p.append(f"{r['id']}: unknown factor '{k}'")
            elif v not in factors[k]["values"]:
                p.append(f"{r['id']}: unknown value '{v}' for factor '{k}'")
    if p:
        return p   # coverage checks need a structurally valid rubric
    names = list(factors)
    used = set()
    for combo in itertools.product(*[list(factors[n]["values"]) for n in names]):
        f = dict(zip(names, combo))
        hit = next((r for r in rubric["rules"] if r["kind"] == "decide" and _matches(r["when"], f)), None)
        if hit is None:
            p.append("coverage gap: no decide rule for " + json.dumps(f))
            if sum(x.startswith("coverage gap") for x in p) >= 5:
                p.append("(more gaps not shown)"); break
        else:
            used.add(hit["id"])
    for r in rubric["rules"]:
        if r["kind"] == "decide" and r["id"] not in used and not any(x.startswith("coverage gap") for x in p):
            p.append(f"{r['id']}: unreachable (an earlier rule always matches first)")
    return p


def run_examples(rubric: dict) -> list:
    """Return failures among the rubric's worked examples (empty = all pass)."""
    out = []
    for ex in rubric.get("examples", []):
        try:
            got = evaluate(rubric, ex["factors"]).tier
        except ValueError as e:
            got = f"error: {e}"
        if got != ex["expected"]:
            out.append(f"example '{ex['name']}': expected {ex['expected']}, got {got}")
    return out


def publishable(rubric: dict) -> tuple:
    """Publish gate: valid, and has worked examples, and they all pass."""
    problems = validate(rubric)
    if not rubric.get("examples"):
        problems.append("add at least one worked example before publishing")
    problems += run_examples(rubric)
    return (not problems, problems)


def diff(old: dict, new: dict) -> list:
    o = {r["id"]: r for r in old.get("rules", [])}
    n = {r["id"]: r for r in new.get("rules", [])}
    out = [f"added rule {i}: {n[i]['reason']}" for i in n if i not in o]
    out += [f"removed rule {i}: {o[i]['reason']}" for i in o if i not in n]
    out += [f"changed rule {i}" for i in n if i in o and n[i] != o[i]]
    if old.get("tiers") != new.get("tiers"):
        out.append("tiers changed")
    return out
