import pytest
from app.fit import Factors, calculate_fit


def t(**kw):
    base = dict(centrality="central", repositioning="none")
    base.update(kw)
    return calculate_fit(Factors(**base))


def test_direct_and_words():
    r = t(); assert (r.tier, r.word) == ("Direct", "High")

def test_central_cannot_lead_is_very_strong():
    assert t(pi_can_lead=False).tier == "Very strong"

def test_framing_very_strong_high():
    r = t(repositioning="framing"); assert (r.tier, r.word) == ("Very strong", "High")

def test_partner_needed_is_strong_medium():
    r = t(repositioning="partner"); assert (r.tier, r.word) == ("Strong", "Medium")

def test_partial_is_strong():
    assert t(centrality="partial").tier == "Strong"

def test_adjacent_is_conditional_low():
    r = t(centrality="adjacent"); assert (r.tier, r.word) == ("Conditional", "Low")

def test_none_and_stretch_excluded():
    assert t(centrality="none").tier == "Excluded" and t(centrality="none").word is None
    assert t(repositioning="stretch").tier == "Excluded"

def test_early_career_only_excluded_even_if_central():
    assert t(career_stage_excluded=True).tier == "Excluded"

def test_positioning_violation_caps_at_conditional():
    r = t(positioning_violation=True); assert r.tier == "Conditional" and any("capped" in x for x in r.rules)

def test_every_result_explains_itself():
    assert t().rules

def test_bad_value_rejected():
    with pytest.raises(ValueError):
        calculate_fit(Factors("very central", "none"))
