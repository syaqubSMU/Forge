import copy
import openpyxl
from app import rubric as R
from app.fit import DEFAULT_RUBRIC
from app.template_xlsx import parse_template, preview, write_template

PROFILE = {"investigator": "Investigator X (fictional)", "institution": "Sample University", "career_stage": "established",
           "horizon_months": 12, "min_award": "", "generic_calls_allowed": True, "sponsor_types": ["federal", "foundation"],
           "positioning_rules": ["Cancer only with a real mechanism bridge", "Defense only where sensing is central"],
           "lanes": [{"lane": "Photochemistry", "terms": "flavin; excited-state chemistry"}, {"lane": "Protein dynamics", "terms": "allostery; conformational change"}]}


def test_round_trip_preserves_rubric_and_profile(tmp_path):
    p = tmp_path / "t.xlsx"; write_template(p, DEFAULT_RUBRIC, PROFILE)
    rub, prof, errors = parse_template(p)
    assert errors == []
    assert R.version(rub) == R.version(DEFAULT_RUBRIC)          # identical content
    assert prof["horizon_months"] == 12 and prof["generic_calls_allowed"] is True
    assert prof["positioning_rules"] == PROFILE["positioning_rules"] and prof["lanes"] == PROFILE["lanes"]


def test_preview_of_unchanged_upload_is_publishable_with_empty_diff(tmp_path):
    p = tmp_path / "t.xlsx"; write_template(p, DEFAULT_RUBRIC, PROFILE)
    pv = preview(p, DEFAULT_RUBRIC)
    assert pv["publishable"] and pv["diff"] == [] and pv["parse_errors"] == []


def test_edited_rule_in_workbook_shows_in_diff_and_version(tmp_path):
    p = tmp_path / "t.xlsx"; write_template(p, DEFAULT_RUBRIC, PROFILE)
    wb = openpyxl.load_workbook(p); ws = wb["Rules"]
    for row in ws.iter_rows(min_row=2):
        if row[0].value == "R9": row[3].value = "Conditional"
    wb.save(p)
    pv = preview(p, DEFAULT_RUBRIC)
    assert pv["diff"] == ["changed rule R9"] and pv["rubric_version"] != R.version(DEFAULT_RUBRIC)
    assert pv["publishable"]       # no worked example depends on R9, so the edit is allowed


def test_wrong_worked_example_in_workbook_blocks_publishing(tmp_path):
    p = tmp_path / "t.xlsx"; write_template(p, DEFAULT_RUBRIC, PROFILE)
    wb = openpyxl.load_workbook(p); wb["Examples"]["C2"].value = "Strong"; wb.save(p)   # first example expects Direct
    pv = preview(p, DEFAULT_RUBRIC)
    assert not pv["publishable"] and any("expected Strong" in x for x in pv["problems"])


def test_malformed_when_and_missing_sheet_reported_not_guessed(tmp_path):
    p = tmp_path / "t.xlsx"; write_template(p, DEFAULT_RUBRIC, PROFILE)
    wb = openpyxl.load_workbook(p); wb["Rules"]["C2"].value = "centrality central"; del wb["Examples"]; wb.save(p)
    _, _, errors = parse_template(p)
    assert any("not factor=value" in e for e in errors) and any("missing sheet 'Examples'" in e for e in errors)
    assert preview(p)["publishable"] is False


def test_bad_profile_values_reported(tmp_path):
    p = tmp_path / "t.xlsx"; write_template(p, DEFAULT_RUBRIC, PROFILE)
    wb = openpyxl.load_workbook(p); ws = wb["Profile"]
    for row in ws.iter_rows(min_row=2):
        if row[0].value == "horizon_months": row[1].value = "a year"
        if row[0].value == "generic_calls_allowed": row[1].value = "maybe"
    wb.save(p)
    _, _, errors = parse_template(p)
    assert any("horizon_months" in e for e in errors) and any("generic_calls_allowed" in e for e in errors)


def test_blank_template_has_no_profile_values(tmp_path):
    p = tmp_path / "blank.xlsx"; write_template(p, DEFAULT_RUBRIC)
    _, prof, errors = parse_template(p)
    assert errors == [] and prof["lanes"] == [] and not prof.get("investigator")


def test_not_an_xlsx(tmp_path):
    p = tmp_path / "x.xlsx"; p.write_text("hello")
    assert parse_template(p)[2]
