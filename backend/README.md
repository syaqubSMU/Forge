# FORGE SIGNAL backend

The engine behind the SIGNAL pages: it reads Grants.gov, asks a model whether each opportunity fits a researcher, checks that every quote the model gives really appears in the source, computes the rating and deadlines in plain code, and logs every run. Scope: `docs/PRD_v0.2.md`.

## How one run works
1. **Input.** A researcher's confirmed research areas, career stage and positioning rules (per run, never stored).
2. **Source.** Opportunities come from the stored Grants.gov copy once it has been ingested, otherwise from a live pull (`app/store.py`, `app/sources/grants_gov.py`).
3. **Shortlist.** Plain code keeps records closing inside the deadline window and ranks them by word overlap with the profile (`app/pipeline.py`). This is a cost control, not a fit judgment.
4. **Judge.** The model returns factor values, an eligibility call and exact quotes as JSON (`app/adapters/`, `app/schemas.py`).
5. **Validate.** Any quote not found in its source text is rejected (`app/validator.py`).
6. **Rate.** The tier (Direct, Very strong, Strong, Conditional, Excluded) is computed from the published rubric (`app/rubric.py`, `rubrics/default.json`).
7. **Calendar.** Internal deadlines, groups and exports are computed in code (`app/calendar.py`, `app/exports.py`).
8. **Log.** Run, sources, citations, failures, tokens and timing go to the run log (`app/db.py`).

## Run locally
    pip install -r requirements.txt
    export ADMIN_TOKEN=choose-a-long-random-string     # the admin API is disabled without it
    export FORGE_DB=forge.db                           # SQLite file, :memory:, or a postgresql:// URL
    uvicorn --factory app.main:create_app --port 8000

The server does not serve the web pages yet; they are static files in `public/signal/` and still show sample data.

To use the real model, set a key (below), then switch the active model: `PUT /api/admin/settings` with `{"active_model": "claude"}`. The default is `mock`, which returns fixed answers and costs nothing.

## Tests
    python -m pytest -q                                                   # in-memory SQLite
    FORGE_TEST_PG_URL=postgresql://user@host:5432/db python -m pytest -q   # the same suite on Postgres

## Scripts (run from `backend/`)
| Script | Purpose |
|---|---|
| `scripts/model_check.py` | Scores the model on `evals/gold_set.json`. `--mock` for a dry run. Uses the key and costs a few cents live. |
| `scripts/grants_check.py` | Live Grants.gov check (no model, no key, no cost). |
| `scripts/calibrate.py`, `scripts/template_cli.py` | Rubric calibration and the Excel template for editing criteria. |

## Environment variables (server only; never sent to the page)
| Name | Purpose |
|---|---|
| `ADMIN_TOKEN` | Admin API sign-in. Required for every `/api/admin/*` call. |
| `FORGE_DB` | Run log and stored opportunities: a SQLite file path (default `forge.db`, `:memory:` for a throwaway run) or a `postgresql://` URL (Neon, Render, Supabase or any Postgres 14+). Tables are created on first start. |
| `FORGE_SALT` | Salt for the visitor hash used by rate limiting. |
| `FORGE_MODEL_KEY`, `FORGE_API_KEY`, `SIGNAL_MODEL_KEY`, `ANTHROPIC_API_KEY` | Model key. Any one works; the first set wins in that order. Never returned by the API or logged. |
| `FORGE_MODEL` | Model id for the Claude adapter (default `claude-opus-5-5`). |
| `FORGE_EFFORT` | Optional model effort level, to cut cost and time on bulk screening. |
| `FORGE_API_BASE` | Optional override of the model API address (default `https://api.anthropic.com`). |

## Endpoints
Public: `GET /api/health`, `GET /api/notice`, `POST /api/runs`, `POST /api/runs/{id}/email` (needs a ticked confirmation; dummy mode logs only), `GET /api/runs/{id}/calendar`, `.ics` and `.xlsx`.
Admin (header `X-Admin-Token`): settings (including the model switch) and audit trail; run log, run detail, CSV and annotations; retention; rubric view, preview and publish; `POST /api/admin/ingest`, `GET /api/admin/ingest/status`, `GET /api/admin/api-calls`.
Safeguards: per-visitor hourly rate limit, a daily run cap, no raw source text returned to the public, spreadsheet-formula protection in exports.

## Stored Grants.gov copy
`POST /api/admin/ingest` lists every posted and forecasted opportunity, reads full text for records that have none or close within 12 months, and logs every Grants.gov request in `api_calls`. Runs then read the stored copy and report when it was retrieved; until the first ingest they pull live. Measured on 2026-11-24: 1,372 records with full text in 72 s, 0 failures. Researcher profiles and judgments are never stored in this table.

## Known gaps (as of 2026-11-24)
- **Speed:** judgments run one after another. 5 judgments took 81 s; the default of 25 would take minutes. Needs parallel judging and a lower-effort setting.
- **Retrieval:** ranking is word overlap only. Its quality has not been measured against labelled answers.
- **PI lookup:** no OpenAlex code yet, so a researcher cannot be searched by name.
- **Front end:** the pages are not connected to this API.
- **Accuracy:** the gold-set expected labels are blank, so agreement with a human cannot be scored.
- **Email:** dummy mode only; nothing is sent.
- **Cost:** model prices are not entered in settings, so cost per run is not reported.
