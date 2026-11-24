"""Calendar exports (PRD FR-13, FR-30). Built by plain code from verified dates.

A field the sponsor did not state is written "Not specified" — never zero, never guessed.
"""
import io
from datetime import date, datetime, timedelta, timezone

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

NOT_SPECIFIED = "Not specified"
HEAD_FILL = PatternFill("solid", fgColor="244B70")

# FR-30 column set, in the customer's order.
COLUMNS = ["Opportunity", "Sponsor", "Type", "NOFO / Call ID", "Fit", "Research relevance",
           "Next fixed date", "Internal deadline", "Days to next date", "Other dates in window",
           "Status", "Conditions / flags", "Amount / scale", "Eligibility",
           "Recommended next action", "Official source", "Date verified"]


def _d(v):
    return v.isoformat() if isinstance(v, (date, datetime)) else (v or NOT_SPECIFIED)


def _row_values(r, verified_on):
    return [
        r.get("title") or NOT_SPECIFIED,
        r.get("sponsor") or NOT_SPECIFIED,
        r.get("funder_type") or "Federal",
        r.get("number") or NOT_SPECIFIED,
        (r.get("fit") or "") + (" (" + r["tier"] + " fit)" if r.get("tier") else ""),
        r.get("rationale") or NOT_SPECIFIED,
        _d(r.get("close_date")),
        _d(r.get("internal_deadline")),
        NOT_SPECIFIED if r.get("days_to_deadline") is None else r["days_to_deadline"],
        "; ".join(r.get("other_dates") or []) or NOT_SPECIFIED,
        r.get("status") or NOT_SPECIFIED,
        "; ".join(r.get("flags") or []) or "None",
        r.get("amount") or NOT_SPECIFIED,
        r.get("eligibility") or NOT_SPECIFIED,
        r.get("next_action") or NOT_SPECIFIED,
        r.get("url") or NOT_SPECIFIED,
        _d(verified_on),
    ]


def _csv_safe(v):
    """A sponsor title beginning =, +, - or @ would execute as a formula when opened."""
    s = v if isinstance(v, (int, float)) or v is None else str(v)
    return "'" + s if isinstance(s, str) and s[:1] in ("=", "+", "-", "@") else s


def to_xlsx(cal, profile=None) -> bytes:
    """One sheet per group (FR-29), same columns throughout (FR-30), plus a summary sheet."""
    wb = openpyxl.Workbook()
    verified = cal.get("today") or date.today()

    ws = wb.active
    ws.title = "Summary"
    ws.column_dimensions["A"].width = 34
    ws.column_dimensions["B"].width = 96
    rows = [("FORGE SIGNAL funding calendar", ""),
            ("Generated", verified.isoformat()),
            ("Internal deadline rule", f"sponsor deadline minus {cal.get('lead_days', 14)} days"),
            ("Researcher", (profile or {}).get("investigator") or (profile or {}).get("name") or NOT_SPECIFIED),
            ("", ""),
            ("Needs action within 45 days", "")]
    for r in cal["needs_action"]:
        rows.append(("", f"{r['title']} — {r['days_to_deadline']} days (internal deadline {_d(r['internal_deadline'])})"))
    if not cal["needs_action"]:
        rows.append(("", "Nothing inside 45 days."))
    rows += [("", ""), ("Top opportunities for this window", "")]
    for r in cal["top"]:
        rows.append(("", f"{r['title']} — {r.get('fit')} ({r.get('tier')} fit)"))
    rows += [("", ""), ("Watch / rolling", "")]
    for r in cal["watch"]:
        rows.append(("", f"{r['title']} — {r['status']}"))
    if not cal["watch"]:
        rows.append(("", "Nothing on watch."))
    rows += [("", ""),
             ("Please verify", "Every deadline and eligibility statement must be confirmed on the sponsor page. "
                               "Ratings are screening results, not decisions.")]
    for a, b in rows:
        ws.append([_csv_safe(a), _csv_safe(b)])
    ws["A1"].font = Font(bold=True, size=14, color="244B70")
    for row in ws.iter_rows():
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            if c.column == 1 and c.value:
                c.font = Font(bold=True, color="244B70")

    for group in ("Fixed", "Rolling", "Watch"):
        sheet = wb.create_sheet({"Fixed": "Fixed deadlines", "Rolling": "Rolling or anytime",
                                 "Watch": "Watch"}[group])
        sheet.append(COLUMNS)
        for c in sheet[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = HEAD_FILL
            c.alignment = Alignment(wrap_text=True, vertical="top")
        for r in cal["groups"][group]:
            sheet.append([_csv_safe(v) for v in _row_values(r, verified)])
        widths = [40, 24, 12, 18, 18, 56, 15, 16, 12, 24, 12, 26, 20, 20, 44, 42, 13]
        for i, w in enumerate(widths, start=1):
            sheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
        for row in sheet.iter_rows(min_row=2):
            for c in row:
                c.alignment = Alignment(wrap_text=True, vertical="top")
        sheet.freeze_panes = "A2"
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ---------------------------------------------------------------- iCalendar
def _esc(text) -> str:
    """RFC 5545 TEXT escaping. Backslash first, or it would escape the escapes."""
    out = str(text).replace(chr(92), chr(92) * 2)      # backslash first, or it escapes the escapes
    out = out.replace(";", chr(92) + ";").replace(",", chr(92) + ",")
    return out.replace("\r\n", chr(92) + "n").replace("\n", chr(92) + "n")


def _fold(line: str) -> str:
    """RFC 5545 content lines are folded at 75 octets, continuations start with one space."""
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    out, start = [], 0
    while start < len(raw):
        end = min(start + (75 if not out else 74), len(raw))
        while end < len(raw) and (raw[end] & 0xC0) == 0x80:      # never split a UTF-8 character
            end -= 1
        chunk = raw[start:end].decode("utf-8")
        out.append(chunk if not out else " " + chunk)
        start = end
    return "\r\n".join(out)


def _ymd(d: date) -> str:
    return "%04d%02d%02d" % (d.year, d.month, d.day)


def to_ics(cal, calendar_name="FORGE SIGNAL deadlines") -> bytes:
    """All-day events. Times and time zones are the sponsor's, so none is asserted here.
    Rolling and watch items get no event: there is no date to put in a calendar."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//FORGE SIGNAL//Funding calendar//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", "X-WR-CALNAME:" + _esc(calendar_name)]
    n = 0
    for r in cal["rows"]:
        if r.get("close_date") is None:
            continue
        for kind, when in (("Internal deadline", r.get("internal_deadline")), ("Sponsor deadline", r.get("close_date"))):
            if when is None:
                continue
            n += 1
            desc = "\n".join(filter(None, [
                "Fit: %s (%s)" % (r.get("fit"), r.get("tier")) if r.get("fit") else None,
                "Eligibility: " + str(r.get("eligibility") or NOT_SPECIFIED),
                "Status: " + str(r.get("status") or NOT_SPECIFIED),
                "Conditions: " + ("; ".join(r.get("flags") or []) or "None"),
                "Next action: " + str(r.get("next_action") or NOT_SPECIFIED),
                "Sponsor deadline: " + _d(r.get("close_date")),
                "Source: " + str(r.get("url") or NOT_SPECIFIED),
                "Verify every date and eligibility statement on the sponsor page."]))
            lines += [
                "BEGIN:VEVENT",
                "UID:%s-%s-%d@forge-signal" % (str(r.get("number") or "opp").replace(" ", ""), _ymd(when), n),
                "DTSTAMP:" + stamp,
                "DTSTART;VALUE=DATE:" + _ymd(when),
                "DTEND;VALUE=DATE:" + _ymd(when + timedelta(days=1)),
                "SUMMARY:" + _esc("%s: %s" % (kind, r.get("title") or "Opportunity")),
                "DESCRIPTION:" + _esc(desc),
                "URL:" + _esc(r.get("url") or ""),
                "TRANSP:TRANSPARENT",
                "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(_fold(x) for x in lines).encode("utf-8") + b"\r\n"
