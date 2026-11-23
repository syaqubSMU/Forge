"""Template workbook (.xlsx) round trip (PRD FR-35/36): write a blank or filled template from a rubric,
parse an uploaded one back into a rubric + investigator profile, and preview it before the admin approves.
Nothing is guessed: missing or malformed content is reported as an error."""
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

from . import rubric as R

SHEETS = ("Instructions", "Rubric", "Factors", "Tiers", "Rules", "Examples", "Profile")
PROFILE_KEYS = [
    ("investigator", "Investigator name (leave blank in a shared template)"),
    ("institution", "Institution"),
    ("career_stage", "Career stage, e.g. established; exclusion rule applies to early-career-only programs"),
    ("horizon_months", "Search horizon in months from today (whole number)"),
    ("min_award", "Minimum award (blank = none)"),
    ("generic_calls_allowed", "Generic calls allowed? yes/no"),
    ("sponsor_types", "Sponsor types, separated by semicolons (federal; defense; state; foundation; international; industry)"),
    ("positioning_rules", "Positioning rules, one per line (e.g. 'Cancer only with a real mechanism bridge')"),
]
HEAD = PatternFill("solid", fgColor="244B70")


def _head(ws, cols, widths):
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = HEAD; c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i)].width = w
    ws.freeze_panes = "A2"


def _wrap(ws):
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")


def _pairs(d):
    return "; ".join(f"{k}={v}" for k, v in d.items())


def write_template(path, rubric: dict, profile: dict = None):
    profile = profile or {}
    wb = openpyxl.Workbook()
    ws = wb.active; ws.title = "Instructions"
    for line in [
        "FORGE SIGNAL fit-criteria template",
        "Edit the Rubric, Factors, Tiers, Rules and Examples sheets to change how fit is calculated. The admin reviews a preview before anything goes live.",
        "Profile holds the investigator's research lanes and positioning rules. It is used for one run and is not stored.",
        "Rules: 'decide' rules are checked top to bottom and the first match sets the tier. 'cap' rules then lower the tier to at most the tier named.",
        "When = factor=value pairs separated by semicolons, e.g.  centrality=central; repositioning=none",
        "Tiers are listed from lowest (row 1) to highest. Leave 'Word shown' blank for a tier that is hidden from results.",
        "A rubric can be published only if every factor combination gets a tier, every worked example passes, and there is at least one example.",
        "Do not put restricted data (student, health or financial records) in this file.",
    ]:
        ws.append([line])
    ws["A1"].font = Font(bold=True, size=14); ws.column_dimensions["A"].width = 130
    ws = wb.create_sheet("Rubric"); _head(ws, ["Field", "Value"], [20, 90])
    for k in ("id", "name", "description"):
        ws.append([k, rubric.get(k, "")])
    _wrap(ws)
    ws = wb.create_sheet("Factors"); _head(ws, ["Factor", "Factor description", "Value", "Value meaning"], [24, 60, 16, 60])
    for name, spec in rubric["factors"].items():
        for i, (v, meaning) in enumerate(spec["values"].items()):
            ws.append([name, spec["description"] if i == 0 else "", v, meaning])
    _wrap(ws)
    ws = wb.create_sheet("Tiers"); _head(ws, ["Tier (lowest first)", "Word shown", "Treatment"], [24, 16, 70])
    for t in rubric["tiers"]:
        ws.append([t["name"], t["word"] or "", t.get("treatment", "")])
    _wrap(ws)
    ws = wb.create_sheet("Rules"); _head(ws, ["Rule ID", "Kind", "When", "Tier", "Reason (plain language)"], [10, 10, 60, 16, 80])
    for r in rubric["rules"]:
        ws.append([r["id"], r["kind"], _pairs(r["when"]), r["tier"], r["reason"]])
    dv = DataValidation(type="list", formula1='"decide,cap"', allow_blank=False); ws.add_data_validation(dv); dv.add("B2:B200")
    _wrap(ws)
    ws = wb.create_sheet("Examples"); _head(ws, ["Worked example", "Factors", "Expected tier"], [44, 90, 18])
    for e in rubric.get("examples", []):
        ws.append([e["name"], _pairs(e["factors"]), e["expected"]])
    _wrap(ws)
    ws = wb.create_sheet("Profile"); _head(ws, ["Field", "Value", "Help"], [26, 70, 80])
    for k, help_ in PROFILE_KEYS:
        v = profile.get(k, "")
        if isinstance(v, list): v = "\n".join(v) if k == "positioning_rules" else "; ".join(v)
        if isinstance(v, bool): v = "yes" if v else "no"
        ws.append([k, v, help_])
    ws.append([]); ws.append(["Lane", "How it should be searched (terms, mechanisms)", ""])
    for c in ws[ws.max_row]: c.font = Font(bold=True)
    for lane in profile.get("lanes", []):
        ws.append([lane["lane"], lane["terms"]])
    _wrap(ws)
    wb.save(path)


def _parse_pairs(text, where, errors):
    out = {}
    for part in [p.strip() for p in str(text or "").split(";") if p.strip()]:
        if "=" not in part:
            errors.append(f"{where}: '{part}' is not factor=value"); continue
        k, v = part.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _sheet_rows(wb, name, errors, cols):
    if name not in wb.sheetnames:
        errors.append(f"missing sheet '{name}'"); return []
    ws = wb[name]
    header = [str(c.value or "").strip() for c in ws[1]][:len(cols)]
    if [h.lower() for h in header] != [c.lower() for c in cols]:
        errors.append(f"sheet '{name}': expected columns {cols}, found {header}"); return []
    return [(i, [c for c in r]) for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2) if any(v not in (None, "") for v in r)]


def parse_template(path):
    """Return (rubric or None, profile, errors)."""
    errors = []
    try:
        wb = openpyxl.load_workbook(path, data_only=True)
    except Exception as e:  # unreadable or not an xlsx
        return None, {}, [f"could not read workbook: {e}"]
    s = lambda v: "" if v is None else str(v).strip()
    rub = {"id": "", "name": "", "description": "", "factors": {}, "tiers": [], "rules": [], "examples": []}
    for i, r in _sheet_rows(wb, "Rubric", errors, ["Field", "Value"]):
        if s(r[0]) in ("id", "name", "description"): rub[s(r[0])] = s(r[1])
    if not rub["id"]: errors.append("Rubric sheet: 'id' is required")
    cur = None
    for i, r in _sheet_rows(wb, "Factors", errors, ["Factor", "Factor description", "Value", "Value meaning"]):
        if s(r[0]):
            cur = s(r[0]); rub["factors"].setdefault(cur, {"description": s(r[1]), "values": {}})
        if cur is None: errors.append(f"Factors row {i}: value listed before any factor name"); continue
        if s(r[2]): rub["factors"][cur]["values"][s(r[2])] = s(r[3])
    for i, r in _sheet_rows(wb, "Tiers", errors, ["Tier (lowest first)", "Word shown", "Treatment"]):
        if not s(r[0]): errors.append(f"Tiers row {i}: tier name is empty"); continue
        rub["tiers"].append({"name": s(r[0]), "word": s(r[1]) or None, "treatment": s(r[2])})
    for i, r in _sheet_rows(wb, "Rules", errors, ["Rule ID", "Kind", "When", "Tier", "Reason (plain language)"]):
        rub["rules"].append({"id": s(r[0]), "kind": s(r[1]).lower(), "when": _parse_pairs(r[2], f"Rules row {i}", errors), "tier": s(r[3]), "reason": s(r[4])})
    for i, r in _sheet_rows(wb, "Examples", errors, ["Worked example", "Factors", "Expected tier"]):
        rub["examples"].append({"name": s(r[0]), "factors": _parse_pairs(r[1], f"Examples row {i}", errors), "expected": s(r[2])})
    profile = {}
    if "Profile" not in wb.sheetnames:
        errors.append("missing sheet 'Profile'")
    else:
        lanes, in_lanes = [], False
        for r in wb["Profile"].iter_rows(min_row=2, values_only=True):
            a, b = s(r[0]), s(r[1])
            if a == "Lane": in_lanes = True; continue
            if not a: continue
            if in_lanes: lanes.append({"lane": a, "terms": b})
            else: profile[a] = b
        if "horizon_months" in profile and profile["horizon_months"]:
            try: profile["horizon_months"] = int(float(profile["horizon_months"]))
            except ValueError: errors.append("Profile: horizon_months must be a whole number")
        if "generic_calls_allowed" in profile:
            v = profile["generic_calls_allowed"].lower()
            if v not in ("yes", "no", ""): errors.append("Profile: generic_calls_allowed must be yes or no")
            profile["generic_calls_allowed"] = (v == "yes") if v else None
        for k in ("sponsor_types",):
            if k in profile: profile[k] = [x.strip() for x in profile[k].split(";") if x.strip()]
        if "positioning_rules" in profile:
            profile["positioning_rules"] = [x.strip() for x in profile["positioning_rules"].splitlines() if x.strip()]
        profile["lanes"] = lanes
    return (None if errors and not rub["factors"] else rub), profile, errors


def preview(path, published: dict = None) -> dict:
    """What the admin sees before approving an upload. Takes effect only after approval (FR-35)."""
    rub, profile, errors = parse_template(path)
    out = {"parse_errors": errors, "profile": profile, "rubric_version": None, "problems": [], "publishable": False, "diff": []}
    if rub is not None and not errors:
        ok, problems = R.publishable(rub)
        out.update(rubric_version=R.version(rub), problems=problems, publishable=ok,
                   diff=R.diff(published, rub) if published else [])
    return out
