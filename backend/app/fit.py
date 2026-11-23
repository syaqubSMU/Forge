"""Explicit fit calculation (PRD 5.9). The MODEL only extracts factor values, each with a citation.
CODE turns the factors into a tier, so the criteria are visible, testable and admin-editable.

Tiers follow the customer's rubric: Direct, Very strong, Strong, Conditional, Excluded.
"""
from dataclasses import dataclass, field

CENTRALITY = ("central", "partial", "adjacent", "none")      # is the PI's established science in the opportunity's scope?
REPOSITIONING = ("none", "framing", "partner", "stretch")    # what must change for the PI to compete?
WORD = {"Direct": "High", "Very strong": "High", "Strong": "Medium", "Conditional": "Low", "Excluded": None}
ORDER = ["Excluded", "Conditional", "Strong", "Very strong", "Direct"]


@dataclass
class Factors:
    centrality: str
    repositioning: str
    pi_can_lead: bool = True
    career_stage_excluded: bool = False      # sponsor restricts to a stage the PI is not in
    positioning_violation: bool = False      # breaks a profile positioning rule (e.g., cancer with no mechanism bridge)


@dataclass
class FitResult:
    tier: str
    word: str | None
    rules: list = field(default_factory=list)   # human-readable "how this was calculated"


def calculate_fit(f: Factors) -> FitResult:
    if f.centrality not in CENTRALITY or f.repositioning not in REPOSITIONING:
        raise ValueError("unknown factor value")
    rules = []

    def done(tier):
        return FitResult(tier, WORD[tier], rules)

    if f.career_stage_excluded:
        rules.append("Sponsor restricts to a career stage the investigator is not in: excluded.")
        return done("Excluded")
    if f.centrality == "none":
        rules.append("Investigator's established science is not in the program scope: excluded.")
        return done("Excluded")
    if f.repositioning == "stretch":
        rules.append("Science would have to be stretched to fit: excluded (keyword overlap only).")
        return done("Excluded")

    if f.centrality == "adjacent":
        tier = "Conditional"
        rules.append("Scientifically adjacent: Conditional, only with a clear topic/partner bridge.")
    elif f.centrality == "central":
        if f.repositioning == "none":
            tier = "Direct" if f.pi_can_lead else "Very strong"
            rules.append("Central science, no repositioning" + ("; PI can lead: Direct." if f.pi_can_lead else "; PI cannot lead: Very strong."))
        elif f.repositioning == "framing":
            tier = "Very strong"; rules.append("Central science; needs sponsor-specific framing: Very strong.")
        else:
            tier = "Strong"; rules.append("Central science but depends on a partner/bridge: Strong.")
    else:  # partial
        tier = "Strong"; rules.append("Partial overlap that depends on a topic, partner or application bridge: Strong.")

    if f.positioning_violation and ORDER.index(tier) > ORDER.index("Conditional"):
        rules.append("Profile positioning rule not met (e.g., no real mechanism bridge): capped at Conditional.")
        tier = "Conditional"
    return done(tier)
