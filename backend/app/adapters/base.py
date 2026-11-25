"""Model adapter interface (hard rule 5): the model can be swapped without touching matching logic."""
import json
import threading
from abc import ABC, abstractmethod

from ..schemas import Judgment, SchemaError, parse_judgment, parse_factor_judgment

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
    last_usage = {"input_tokens": 0, "output_tokens": 0}

    def __init__(self):
        self.total_usage = {"input_tokens": 0, "output_tokens": 0}
        self.call_log = []                    # one entry per model call: seconds, tokens, stop reason
        self._lock = threading.Lock()         # judgments run in parallel threads and share these counters

    def _record(self, usage: dict):
        with self._lock:
            self.last_usage = usage
            for k in ("input_tokens", "output_tokens"):
                self.total_usage[k] = self.total_usage.get(k, 0) + int(usage.get(k, 0) or 0)
            self.call_log.append(dict(usage))

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


def build_factor_system(rubric: dict) -> str:
    """System prompt built from the rubric itself, so admin edits reach the model (FR-47)."""
    lines = ["You assess whether a researcher fits a funding opportunity, for a university research-development office.",
             "Use ONLY the provided sources. Never use outside knowledge. Never invent text.",
             "You do NOT decide the overall rating. You report factual factor values, each backed by an exact quote.",
             "", "Report these factors:"]
    for name, spec in rubric["factors"].items():
        vals = "; ".join(f"{v} = {meaning}" for v, meaning in spec["values"].items())
        lines.append(f"- {name}: {spec['description']} One of: {vals}")
    lines += ["",
              "Also report eligibility as one of: Eligible, Not eligible, Needs verification.",
              "If the sources do not state eligibility, you MUST answer 'Needs verification'. Never guess it.",
              "Every quote must be copied EXACTLY, character for character, from one source. If you cannot find",
              "supporting text for a factor, return an empty citations list for it rather than inventing a quote.",
              "Never use percentages or numeric scores. Never call a named person non-competitive.",
              "", "Return one JSON object only:",
              '{"factors": {"<name>": {"value": "<one allowed value>", "citations": [{"quote": "...", "source_id": "..."}]}},',
              ' "eligibility": "...", "eligibility_citations": [{"quote": "...", "source_id": "..."}], "rationale": "one or two plain sentences"}']
    return "\n".join(lines)


def judge_fit(adapter: "ModelAdapter", sources: dict, question: str, rubric: dict):
    """Ask for factor values with citations; retry once on invalid output, then raise (FR-11)."""
    system = build_factor_system(rubric)
    last = None
    for _ in range(2):
        raw = adapter.complete(system, build_prompt(sources, question))
        try:
            return parse_factor_judgment(json.loads(_strip_fences(raw)), rubric)
        except (json.JSONDecodeError, SchemaError) as e:
            last = e
    raise SchemaError(f"model output invalid after retry: {last}")
