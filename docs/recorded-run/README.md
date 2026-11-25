# Recorded run (for review; NOT published)

One real run of the FORGE SIGNAL pipeline on a FICTIONAL researcher against the stored public Grants.gov copy (retrieved 2026-11-25T14:34:02+00:00), recorded 2026-11-25. Data only: no page uses these files yet.

- `recorded-run.js`: the page-shaped data (`window.MOCK`), unedited, with its integrity block.
- `recorded-run.run-detail.json`: the run's full logged detail. Its sha256 is recorded in the file (`recorded_run.run_detail.sha256`).
- `run-output.txt`: what the script printed, including the integrity checks and the quote check.

Check without any cost: `python backend/scripts/record_run.py --verify --out docs/recorded-run/recorded-run.js` (it also checks the run-detail file next to it). The results hash only detects accidental edits; the commit message carries the run-detail sha256 and the code commit id as the stronger record.
