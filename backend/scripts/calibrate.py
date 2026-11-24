"""Calibrate the rubric against a customer workbook's Fit column (the answer key).
  python scripts/calibrate.py WORKBOOK.xlsx evals/private/pi_sheet_factors.json
The factors file maps opportunity name -> factor values (proposed from the sheet text; the customer reviews them).
This tests whether the RULES can reproduce her tiers. It does not test model factor extraction."""
import json, re, sys
sys.path.insert(0, ".")
import openpyxl
from app import rubric as R
from app.fit import DEFAULT_RUBRIC

def sheet_tier(text):
    m = re.search(r"(\d(?:\.\d)?)(?:\s*[–-]\s*(\d(?:\.\d)?))?\s*/\s*5", str(text))
    if not m: return None
    lo = min(float(m.group(1)), float(m.group(2) or m.group(1)))      # a range is read at its lower end
    return "Direct" if lo >= 5 else "Very strong" if lo >= 4.5 else "Strong" if lo >= 4 else "Conditional" if lo >= 3 else "Excluded"

def main():
    wb = openpyxl.load_workbook(sys.argv[1]); ws = wb.worksheets[0]
    factors = json.load(open(sys.argv[2]))
    bad = ok = 0
    for row in ws.iter_rows(min_row=10, values_only=True):
        if not row[0] or not row[4]: continue
        name, fit = row[0], row[4]
        want = sheet_tier(fit)
        f = factors.get(name)
        if f is None: print(f"NO FACTORS  {name}"); bad += 1; continue
        got = R.evaluate(DEFAULT_RUBRIC, f).tier
        flag = "ok  " if got == want else "DIFF"
        ok += got == want; bad += got != want
        print(f"{flag} sheet '{fit}' -> {want:11} rubric -> {got:11} | {name[:60]}")
    print(f"\n{ok} reproduced, {bad} differ")
main()
