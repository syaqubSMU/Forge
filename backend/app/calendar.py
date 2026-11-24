"""Calendar arithmetic (PRD FR-12, FR-14, FR-29, FR-38, FR-31).

All of this is ordinary deterministic code, never the model (hard rule 6).
A date the sponsor did not state stays None and is rendered "Not specified";
it is never filled in with today, zero, or a guess.
"""
from datetime import date, timedelta

STATUSES = ("Open", "Upcoming", "Rolling", "Watch", "Closed")
ACTION_WINDOW_DAYS = 45          # FR-31


def internal_deadline(close_date, lead_days: int):
    """Sponsor deadline minus the office's lead time. None when the sponsor stated no date."""
    if close_date is None:
        return None
    if lead_days < 0:
        raise ValueError("lead time cannot be negative")
    return close_date - timedelta(days=lead_days)


def days_until(d, today=None):
    return None if d is None else (d - (today or date.today())).days


def derive_status(source_status=None, close_date=None, currency_flags=(), today=None):
    """One status (FR-38). Conditions such as 'Limited submission' are separate flags, never
    folded into the status string the way the customer's workbook does."""
    today = today or date.today()
    flags = [f.lower() for f in (currency_flags or [])]
    if any("archived" in f for f in flags):
        return "Watch"                                   # archived or replaced: never a live deadline
    if close_date is not None and close_date < today:
        return "Closed"
    if (source_status or "").lower() == "forecasted":
        return "Upcoming"
    if close_date is None:
        return "Rolling"                                 # rolling/anytime: no invented deadline
    return "Open"


def derive_flags(record, today=None, lead_days=None):
    """Conditions worth showing beside the status. Read from the record, never inferred."""
    today = today or date.today()
    out = []
    d = days_until(record.get("close_date"), today)
    if lead_days is not None and d is not None and 0 <= d < lead_days:
        out.append("Internal lead time already passed")
    if d is not None and 0 <= d <= 21:
        out.append("Closing soon")
    if record.get("cost_sharing"):
        out.append("Cost sharing required")
    if record.get("related_opportunity_ids"):
        out.append("Replacement posting listed")
    for f in record.get("currency_flags") or []:
        if f not in out:
            out.append(f)
    return out


def amount_text(floor, ceiling):
    """Sponsors send 'none', '' or 0 as well as real figures. Only a positive number is an amount."""
    def num(v):
        try:
            n = int(float(str(v).strip()))
        except (TypeError, ValueError):
            return None
        return n if n > 0 else None

    def m(v):
        return "$" + format(v, ",")

    floor, ceiling = num(floor), num(ceiling)
    if ceiling and floor:
        return m(floor) + " to " + m(ceiling)
    if ceiling:
        return "up to " + m(ceiling)
    if floor:
        return "from " + m(floor)
    return None


def next_action(row):
    """A concrete next step (FR-30's 'Recommended next action'), chosen by rule, not by the model."""
    if row["status"] == "Watch":
        return "Do not act on this version. Check the sponsor page for the replacement or the next cycle."
    if row["status"] == "Closed":
        return "Closed. Watch for the next cycle."
    if row["eligibility"] == "Not eligible":
        return "Do not pursue unless the stated restriction changes."
    if row["eligibility"] == "Needs verification":
        return "Verify eligibility on the sponsor page before any outreach."
    if row["status"] == "Rolling":
        return "Contact the program officer to confirm topic fit before preparing anything."
    return "Confirm the deadline on the sponsor page, then prepare outreach."


def build_calendar(results, lead_days=14, today=None, action_window=ACTION_WINDOW_DAYS):
    """Turn screened results into calendar rows grouped Fixed / Rolling / Watch (FR-29),
    plus the closing summary (FR-31). Excluded results never reach here."""
    today = today or date.today()
    rows = []
    for r in results:
        if not r.get("fit"):
            continue                                      # Excluded stays in the run log
        close = r.get("close_date")
        status = r.get("status") or derive_status(r.get("source_status"), close, r.get("currency_flags"), today)
        row = dict(r)
        row.update({
            "status": status,
            "flags": r.get("flags") or derive_flags(r, today, lead_days),
            "internal_deadline": internal_deadline(close, lead_days),
            "days_to_deadline": days_until(close, today),
            "amount": amount_text(r.get("award_floor"), r.get("award_ceiling")),
        })
        row["next_action"] = next_action(row)
        rows.append(row)

    def key(x):
        return (x["days_to_deadline"] if x["days_to_deadline"] is not None else 10 ** 6, x.get("title", ""))

    groups = {"Fixed": [], "Rolling": [], "Watch": []}
    for row in rows:
        if row["status"] in ("Rolling",):
            groups["Rolling"].append(row)
        elif row["status"] in ("Watch", "Closed", "Upcoming") and row["close_date"] is None:
            groups["Watch"].append(row)
        elif row["status"] in ("Watch", "Closed"):
            groups["Watch"].append(row)
        else:
            groups["Fixed"].append(row)
    for g in groups.values():
        g.sort(key=key)

    order = {"High": 0, "Medium": 1, "Low": 2}
    needs_action = sorted([r for r in rows if r["days_to_deadline"] is not None
                           and 0 <= r["days_to_deadline"] <= action_window
                           and r["status"] not in ("Watch", "Closed")], key=key)
    top = sorted(rows, key=lambda r: (order.get(r["fit"], 3), key(r)))[:5]
    return {"rows": rows, "groups": groups, "needs_action": needs_action, "top": top,
            "watch": groups["Watch"] + groups["Rolling"], "lead_days": lead_days, "today": today}
