"""Calendar arithmetic and exports. All plain code (hard rule 6), so all of it is tested."""
import io
from datetime import date

import openpyxl
import pytest

from app.calendar import (ACTION_WINDOW_DAYS, amount_text, build_calendar, derive_flags,
                          derive_status, internal_deadline, next_action)
from app.exports import COLUMNS, NOT_SPECIFIED, _esc, _fold, to_ics, to_xlsx

B = chr(92)   # a literal backslash, written this way so no escaping is ambiguous

TODAY = date(2026, 11, 24)


def opp(**kw):
    base = {"title": "Sample Program", "sponsor": "Sample Agency", "number": "SS-1",
            "url": "https://example.org/1", "close_date": date(2027, 1, 5), "fit": "High",
            "tier": "Direct", "eligibility": "Eligible", "rationale": "Topic matches.",
            "award_ceiling": 500000, "currency_flags": [], "related_opportunity_ids": []}
    base.update(kw)
    return base


# ---------------------------------------------------------------- dates (FR-12, FR-14)
def test_internal_deadline_is_sponsor_minus_lead_time():
    assert internal_deadline(date(2027, 3, 15), 14) == date(2027, 3, 1)


def test_internal_deadline_crosses_year_end_and_holidays():
    assert internal_deadline(date(2027, 1, 5), 14) == date(2026, 12, 22)
    assert internal_deadline(date(2027, 1, 2), 30) == date(2026, 12, 3)


def test_internal_deadline_handles_leap_day():
    assert internal_deadline(date(2028, 3, 5), 14) == date(2028, 2, 20)
    assert internal_deadline(date(2028, 3, 1), 1) == date(2028, 2, 29)


def test_missing_sponsor_date_gives_no_internal_date_never_a_guess():
    assert internal_deadline(None, 14) is None


def test_negative_lead_time_rejected():
    with pytest.raises(ValueError):
        internal_deadline(date(2027, 1, 1), -1)


# ---------------------------------------------------------------- status and flags (FR-38)
def test_status_is_one_value_with_conditions_kept_separate():
    assert derive_status("posted", date(2027, 1, 5), today=TODAY) == "Open"
    assert derive_status("posted", None, today=TODAY) == "Rolling"
    assert derive_status("forecasted", date(2027, 6, 1), today=TODAY) == "Upcoming"
    assert derive_status("posted", date(2026, 1, 1), today=TODAY) == "Closed"
    assert derive_status("posted", date(2027, 1, 5), ["Archived on the sponsor site"], TODAY) == "Watch"


def test_archived_never_counts_as_a_live_deadline():
    cal = build_calendar([opp(currency_flags=["Archived on the sponsor site"])], 14, TODAY)
    assert cal["groups"]["Fixed"] == [] and len(cal["groups"]["Watch"]) == 1
    assert cal["needs_action"] == []


def test_flags_are_read_from_the_record():
    f = derive_flags(opp(close_date=date(2026, 12, 5), cost_sharing=True, related_opportunity_ids=["x"]), TODAY)
    assert "Closing soon" in f and "Cost sharing required" in f and "Replacement posting listed" in f
    assert derive_flags(opp(), TODAY) == []


def test_amount_text_never_invents_a_figure():
    assert amount_text(None, None) is None
    assert amount_text(None, 500000) == "up to $500,000"
    assert amount_text(50000, 500000) == "$50,000 to $500,000"


# ---------------------------------------------------------------- grouping and summary
def test_groups_separate_fixed_rolling_and_watch():
    cal = build_calendar([opp(), opp(title="Rolling one", close_date=None),
                          opp(title="Archived one", currency_flags=["Archived on the sponsor site"])], 14, TODAY)
    assert [r["title"] for r in cal["groups"]["Fixed"]] == ["Sample Program"]
    assert [r["title"] for r in cal["groups"]["Rolling"]] == ["Rolling one"]
    assert [r["title"] for r in cal["groups"]["Watch"]] == ["Archived one"]


def test_excluded_results_never_reach_the_calendar():
    assert build_calendar([opp(fit=None, tier="Excluded")], 14, TODAY)["rows"] == []


def test_needs_action_uses_the_45_day_window():
    cal = build_calendar([opp(title="soon", close_date=TODAY.replace(day=30)),
                          opp(title="far", close_date=date(2027, 6, 1))], 14, TODAY)
    assert [r["title"] for r in cal["needs_action"]] == ["soon"]
    assert ACTION_WINDOW_DAYS == 45


def test_rolling_items_are_on_the_watch_list_not_the_action_list():
    cal = build_calendar([opp(close_date=None)], 14, TODAY)
    assert cal["needs_action"] == [] and len(cal["watch"]) == 1


def test_top_list_orders_by_fit_then_deadline():
    cal = build_calendar([opp(title="low", fit="Low", tier="Conditional", close_date=date(2026, 12, 1)),
                          opp(title="high", fit="High", close_date=date(2027, 2, 1))], 14, TODAY)
    assert [r["title"] for r in cal["top"]] == ["high", "low"]


def test_next_action_follows_the_status_and_eligibility():
    assert "Verify eligibility" in next_action({"status": "Open", "eligibility": "Needs verification"})
    assert "program officer" in next_action({"status": "Rolling", "eligibility": "Eligible"})
    assert "replacement" in next_action({"status": "Watch", "eligibility": "Eligible"})
    assert "Do not pursue" in next_action({"status": "Open", "eligibility": "Not eligible"})


# ---------------------------------------------------------------- iCalendar (FR-13)
def cal_of(*rows):
    return build_calendar(list(rows) or [opp()], 14, TODAY)


def test_ics_escapes_semicolons_commas_and_backslashes():
    assert _esc("a;b,c" + B + "d") == "a" + B + ";b" + B + ",c" + B + B + "d"
    text = to_ics(cal_of(opp(title="Program; One, Two"))).decode()
    assert ("Program" + B + "; One" + B + ", Two") in text and "Program; One," not in text


def test_ics_has_two_all_day_events_per_opportunity():
    text = to_ics(cal_of()).decode()
    assert text.count("BEGIN:VEVENT") == 2                       # internal deadline and sponsor deadline
    assert "DTSTART;VALUE=DATE:20261222" in text                 # 5 Jan 2027 minus 14 days
    assert "DTSTART;VALUE=DATE:20270105" in text
    assert "DTEND;VALUE=DATE:20270106" in text                   # all-day end is exclusive
    assert "T000000" not in text.split("DTSTAMP")[1][:40]        # no invented time of day on events


def test_ics_omits_items_with_no_sponsor_date():
    assert to_ics(cal_of(opp(close_date=None))).decode().count("BEGIN:VEVENT") == 0


def test_ics_lines_are_folded_to_75_octets():
    text = to_ics(cal_of(opp(title="A " + "very long programme title " * 6))).decode()
    assert all(len(line.encode()) <= 75 for line in text.split("\r\n") if line)
    assert "\r\n " in text                                       # continuation lines present


def test_fold_never_splits_a_utf8_character():
    folded = _fold("SUMMARY:" + "é" * 60)
    for piece in folded.split("\r\n"):
        piece.encode("utf-8").decode("utf-8")                    # would raise if split mid-character
    assert all(len(p.encode()) <= 75 for p in folded.split("\r\n"))


def test_ics_structure_is_wellformed():
    text = to_ics(cal_of()).decode()
    assert text.startswith("BEGIN:VCALENDAR\r\n") and text.rstrip("\r\n").endswith("END:VCALENDAR")
    assert text.count("BEGIN:VEVENT") == text.count("END:VEVENT")
    assert len({l for l in text.split("\r\n") if l.startswith("UID:")}) == 2    # unique UIDs


# ---------------------------------------------------------------- spreadsheet (FR-13, FR-30)
def load(data):
    return openpyxl.load_workbook(io.BytesIO(data))


def test_xlsx_has_a_sheet_per_group_with_the_agreed_columns():
    wb = load(to_xlsx(cal_of(opp(), opp(title="Rolling", close_date=None))))
    assert wb.sheetnames == ["Summary", "Fixed deadlines", "Rolling or anytime", "Watch"]
    assert [c.value for c in wb["Fixed deadlines"][1]] == COLUMNS


def test_xlsx_writes_not_specified_rather_than_a_guess():
    wb = load(to_xlsx(cal_of(opp(close_date=None, award_ceiling=None, number=None))))
    row = {COLUMNS[i]: c.value for i, c in enumerate(wb["Rolling or anytime"][2])}
    assert row["Next fixed date"] == NOT_SPECIFIED and row["Internal deadline"] == NOT_SPECIFIED
    assert row["Amount / scale"] == NOT_SPECIFIED and row["Days to next date"] == NOT_SPECIFIED
    assert row["NOFO / Call ID"] == NOT_SPECIFIED


def test_xlsx_blocks_formula_injection_from_sponsor_text():
    wb = load(to_xlsx(cal_of(opp(title='=HYPERLINK("http://evil","click")'))))
    assert str(wb["Fixed deadlines"]["A2"].value).startswith("'=")


def test_xlsx_summary_carries_the_closing_lists():
    wb = load(to_xlsx(cal_of(opp(close_date=date(2026, 12, 10))), {"investigator": "Dr. Sample"}))
    text = "\n".join(str(c.value) for row in wb["Summary"].iter_rows() for c in row if c.value)
    assert "Needs action within 45 days" in text and "Top opportunities" in text
    assert "sponsor deadline minus 14 days" in text and "Dr. Sample" in text
    assert "verify" in text.lower()


def test_exports_are_consistent_with_each_other():
    cal = cal_of(opp(), opp(title="Rolling", close_date=None))
    wb = load(to_xlsx(cal))
    assert wb["Fixed deadlines"].max_row == 2 and wb["Rolling or anytime"].max_row == 2
    assert to_ics(cal).decode().count("BEGIN:VEVENT") == 2       # only the dated one produces events


def test_amount_text_survives_the_strings_sponsors_actually_send():
    # Grants.gov sends the string 'none' rather than null; a real pull hit this.
    assert amount_text("none", "none") is None
    assert amount_text("", None) is None
    assert amount_text(0, 0) is None                      # zero is unstated, not an award of nothing
    assert amount_text("none", "500000") == "up to $500,000"
    assert amount_text("50000.0", "500000.0") == "$50,000 to $500,000"


def test_a_deadline_inside_the_lead_time_is_flagged():
    """A real pull showed deadlines days away, whose internal deadline is already past.
    The arithmetic is right; the office needs to be told."""
    cal = build_calendar([opp(close_date=date(2026, 11, 30))], 14, TODAY)     # 6 days away
    row = cal["groups"]["Fixed"][0]
    assert row["internal_deadline"] == date(2026, 11, 16)                    # genuinely in the past
    assert "Internal lead time already passed" in row["flags"]
    assert build_calendar([opp(close_date=date(2027, 3, 1))], 14, TODAY)["rows"][0]["flags"] == []
