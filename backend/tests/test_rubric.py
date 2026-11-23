import copy
from app import rubric as R
from app.fit import DEFAULT_RUBRIC


def test_default_rubric_is_publishable():
    ok, problems = R.publishable(DEFAULT_RUBRIC)
    assert ok, problems


def test_result_records_rubric_version_and_rule_ids():
    f = {"centrality": "central", "repositioning": "none", "pi_can_lead": "yes", "career_stage_excluded": "no", "positioning_violation": "no"}
    r = R.evaluate(DEFAULT_RUBRIC, f)
    assert r.tier == "Direct" and r.rule_ids == ["R5"] and r.rubric_version == R.version(DEFAULT_RUBRIC)


def test_coverage_gap_detected():
    rb = copy.deepcopy(DEFAULT_RUBRIC)
    rb["rules"] = [r for r in rb["rules"] if r["id"] != "R9"]    # partial overlap no longer decided
    assert any("coverage gap" in p for p in R.validate(rb))


def test_unreachable_rule_detected():
    rb = copy.deepcopy(DEFAULT_RUBRIC)
    rb["rules"].append({"id": "RY", "kind": "decide", "when": {"centrality": "none"}, "tier": "Excluded", "reason": "never reached"})
    assert any("RY: unreachable" in p for p in R.validate(rb))


def test_unknown_names_and_missing_reason_detected():
    rb = copy.deepcopy(DEFAULT_RUBRIC)
    rb["rules"][0]["tier"] = "Great"; rb["rules"][1]["when"] = {"centrality": "huge"}; rb["rules"][2]["reason"] = ""
    probs = R.validate(rb)
    assert any("unknown tier" in p for p in probs) and any("unknown value" in p for p in probs) and any("reason" in p for p in probs)


def test_publish_gate_blocks_failing_example():
    rb = copy.deepcopy(DEFAULT_RUBRIC)
    rb["examples"][0]["expected"] = "Strong"
    ok, problems = R.publishable(rb)
    assert not ok and any("expected Strong" in p for p in problems)


def test_publish_gate_requires_examples():
    rb = copy.deepcopy(DEFAULT_RUBRIC); rb["examples"] = []
    assert not R.publishable(rb)[0]


def test_editing_a_rule_changes_version_and_shows_in_diff():
    rb = copy.deepcopy(DEFAULT_RUBRIC)
    rb["rules"][8]["tier"] = "Conditional"    # admin makes "partial overlap" less generous
    assert R.version(rb) != R.version(DEFAULT_RUBRIC)
    assert R.diff(DEFAULT_RUBRIC, rb) == ["changed rule R9"]
    assert R.evaluate(rb, {"centrality": "partial", "repositioning": "none", "pi_can_lead": "yes",
                           "career_stage_excluded": "no", "positioning_violation": "no"}).tier == "Conditional"


def test_bad_factor_value_rejected():
    import pytest
    with pytest.raises(ValueError):
        R.evaluate(DEFAULT_RUBRIC, {"centrality": "huge"})
