"""Citation validator (hard rule 2): reject any quote not found in its source text."""
import re

from .schemas import Judgment, NO_SUPPORT


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("’", "'").replace("“", '"').replace("”", '"')).strip().lower()


def quote_supported(quote: str, source_text: str) -> bool:
    q = _norm(quote)
    return len(q) >= 12 and q in _norm(source_text)


def validate(judgment: Judgment, sources: dict) -> dict:
    """Return a report; unsupported citations are dropped and counted.

    Eligibility with no supported citation becomes 'Needs verification' (never guessed).
    Fit with no supported citation is shown with NO_SUPPORT and capped at Low.
    """
    failures = []

    def keep(cites):
        ok = []
        for c in cites:
            if c.source_id in sources and quote_supported(c.quote, sources[c.source_id]):
                ok.append(c)
            else:
                failures.append({"quote": c.quote, "source_id": c.source_id})
        return ok

    fit_c = keep(judgment.fit_citations)
    elig_c = keep(judgment.eligibility_citations)
    fit, elig, note = judgment.fit, judgment.eligibility, judgment.rationale
    if not fit_c:
        fit, note = "Low", NO_SUPPORT
    if not elig_c:
        elig = "Needs verification"
    return {"fit": fit, "eligibility": elig, "rationale": note,
            "fit_citations": fit_c, "eligibility_citations": elig_c,
            "failed_citations": failures, "citation_pass_rate": _rate(judgment, failures)}


def _rate(j: Judgment, failures: list) -> float:
    total = len(j.fit_citations) + len(j.eligibility_citations)
    return 1.0 if total == 0 else (total - len(failures)) / total
