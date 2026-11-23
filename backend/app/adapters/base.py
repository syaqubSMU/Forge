"""Model adapter interface (hard rule 5): the model can be swapped without touching matching logic."""
import json
from abc import ABC, abstractmethod

from ..schemas import Judgment, SchemaError, parse_judgment

SYSTEM = (
    "You judge whether a researcher fits a funding opportunity. Use ONLY the provided sources. "
    "Return one JSON object: {fit: High|Medium|Low, eligibility: Eligible|Not eligible|Needs verification, "
    "rationale: string, fit_citations: [{quote, source_id}], eligibility_citations: [{quote, source_id}]}. "
    "Every quote must be copied exactly from a source. If sources are silent on eligibility, answer "
    "'Needs verification'. Never invent facts. Never use percentages."
)


def build_prompt(sources: dict, question: str) -> str:
    blocks = "\n\n".join(f"[source_id: {k}]\n{v}" for k, v in sources.items())
    return f"{question}\n\nSOURCES:\n{blocks}"


class ModelAdapter(ABC):
    name = "base"

    @abstractmethod
    def complete(self, system: str, prompt: str) -> str:
        """Return the model's raw text."""

    def judge(self, sources: dict, question: str) -> Judgment:
        """Call the model; retry once on invalid output (FR-11), then raise."""
        last = None
        for _ in range(2):
            raw = self.complete(SYSTEM, build_prompt(sources, question))
            try:
                return parse_judgment(json.loads(_strip_fences(raw)))
            except (json.JSONDecodeError, SchemaError) as e:
                last = e
        raise SchemaError(f"model output invalid after retry: {last}")


def _strip_fences(t: str) -> str:
    t = t.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[-1].rsplit("```", 1)[0]
    return t
