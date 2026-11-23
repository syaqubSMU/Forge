"""Fit calculation: thin wrapper over the data-driven rubric (rubrics/default.json). See PRD 5.9."""
import os
from dataclasses import dataclass

from . import rubric as R

DEFAULT_RUBRIC = R.load(os.path.join(os.path.dirname(__file__), "..", "rubrics", "default.json"))
CENTRALITY = tuple(DEFAULT_RUBRIC["factors"]["centrality"]["values"])
REPOSITIONING = tuple(DEFAULT_RUBRIC["factors"]["repositioning"]["values"])


@dataclass
class Factors:
    centrality: str
    repositioning: str
    pi_can_lead: bool = True
    career_stage_excluded: bool = False
    positioning_violation: bool = False

    def as_dict(self):
        yn = lambda b: "yes" if b else "no"
        return {"centrality": self.centrality, "repositioning": self.repositioning, "pi_can_lead": yn(self.pi_can_lead),
                "career_stage_excluded": yn(self.career_stage_excluded), "positioning_violation": yn(self.positioning_violation)}


def calculate_fit(f: Factors, rubric: dict = None) -> R.Result:
    return R.evaluate(rubric or DEFAULT_RUBRIC, f.as_dict())
