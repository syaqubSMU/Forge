import json
import pytest

from app.adapters.mock import MockAdapter
from app.schemas import NO_SUPPORT, SchemaError, parse_judgment
from app.validator import validate

SRC = {"nsf-1": "Applicants must be U.S. institutions of higher education. Proposals are due March 15, 2027."}


def good(**kw):
    d = {"fit": "High", "eligibility": "Eligible", "rationale": "ok",
         "fit_citations": [{"quote": "Proposals are due March 15, 2027.", "source_id": "nsf-1"}],
         "eligibility_citations": [{"quote": "Applicants must be U.S. institutions of higher education", "source_id": "nsf-1"}]}
    d.update(kw)
    return d


def test_supported_quotes_pass():
    r = validate(parse_judgment(good()), SRC)
    assert r["fit"] == "High" and r["eligibility"] == "Eligible" and r["citation_pass_rate"] == 1.0


def test_fabricated_quote_rejected_and_downgraded():
    d = good(eligibility_citations=[{"quote": "Open to all institutions worldwide", "source_id": "nsf-1"}])
    r = validate(parse_judgment(d), SRC)
    assert r["eligibility"] == "Needs verification"          # never guessed
    assert len(r["failed_citations"]) == 1 and r["citation_pass_rate"] < 1.0


def test_no_fit_support_is_low_with_standard_message():
    r = validate(parse_judgment(good(fit_citations=[])), SRC)
    assert r["fit"] == "Low" and r["rationale"] == NO_SUPPORT


def test_unknown_source_id_rejected():
    d = good(fit_citations=[{"quote": "Proposals are due March 15, 2027.", "source_id": "other"}])
    assert validate(parse_judgment(d), SRC)["failed_citations"]


def test_schema_rejects_percentage_and_bad_enums():
    with pytest.raises(SchemaError):
        parse_judgment(good(fit="85%"))
    with pytest.raises(SchemaError):
        parse_judgment(good(eligibility="Probably"))


def test_adapter_retries_once_then_succeeds():
    m = MockAdapter(["not json", "```json\n" + json.dumps(good()) + "\n```"])
    assert m.judge(SRC, "q").fit == "High" and m.calls == 2


def test_adapter_fails_after_two_bad_outputs():
    with pytest.raises(SchemaError):
        MockAdapter(["nope"]).judge(SRC, "q")
