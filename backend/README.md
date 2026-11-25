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

The same server also serves the web pages from `public/signal/` (override the folder with `FORGE_STATIC`), so open `http://localhost:8000/`. It answers `/config.js` with `live: true`, which switches the pages from the fictional sample run to this API. The pages published on GitHub Pages ship their own `config.js` with `live: false`, so they keep showing sample data.

If the pages are ever hosted on a different address than the API, set `api` in the pages' `config.js` to the API's address and list the pages' address in `FORGE_CORS_ORIGINS` (comma-separated).

To use the real model, set a key (below), then switch the active model: `PUT /api/admin/settings` with `{"active_model": "claude"}`. The default is `mock`, which returns fixed answers and costs nothing.

## Tests
    python -m pytest -q                                                   # in-memory SQLite
    FORGE_TEST_PG_URL=postgresql://user@host:5432/db python -m pytest -q   # the same suite on Postgres

## Scripts (run from `backend/`)
| Script | Purpose |
|---|---|
| `scripts/model_check.py` | Scores the model on `evals/gold_set.json`. `--mock` for a dry run. Uses the key and costs a few cents live. |
| `scripts/bench_judging.py` | Times the judging step with the live model on the stored corpus (costs money; use `--n 3` to `5`). |
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
| `FORGE_EFFORT` | Model effort level (`low`, `medium`, `high`). `low` is recommended for bulk screening: about 35% fewer output tokens and 25% less time in the measured sample. |
| `FORGE_STATIC` | Folder of web pages to serve (default: `public/signal` in this repository). |
| `FORGE_CORS_ORIGINS` | Comma-separated page addresses allowed to call the API from another host. Empty by default (same-address only). |
| `FORGE_API_BASE` | Optional override of the model API address (default `https://api.anthropic.com`). |

## Endpoints
Public: `GET /api/health`, `GET /api/notice`, `GET /config.js`, `POST /api/runs` (optional per-run `options`: `horizon_months` 1 to 36 and `lead_time_days` 0 to 365; they apply to that run only, and every response carries a `source` block naming Grants.gov's public API and when the stored copy was retrieved), `POST /api/runs/{id}/email` (needs a ticked confirmation; dummy mode logs only), `GET /api/runs/{id}/calendar`, `.ics` and `.xlsx`.
Admin (header `X-Admin-Token`): settings (including the model switch) and audit trail; run log, run detail, CSV and annotations; retention; rubric view, preview and publish; `POST /api/admin/ingest`, `GET /api/admin/ingest/status`, `GET /api/admin/api-calls`.
Safeguards: per-visitor hourly rate limit, a daily run cap, no raw source text returned to the public, spreadsheet-formula protection in exports.

## Stored Grants.gov copy
`POST /api/admin/ingest` lists every posted and forecasted opportunity, reads full text for records that have none or close within 12 months, and logs every Grants.gov request in `api_calls`. Runs then read the stored copy and report when it was retrieved; until the first ingest they pull live. Measured on 2026-11-24: 1,372 records with full text in 72 s, 0 failures. Researcher profiles and judgments are never stored in this table.

## Known gaps (as of 2026-11-24)
- **Speed (addressed 2026-11-25):** judgments now run in a bounded thread pool (`judge_concurrency` setting, default 8, hard cap 16); the SDK retries 429/overload with backoff (`FORGE_MODEL_RETRIES`, default 6). Measured live on claude-opus-5-5, same profile and shortlist, stored corpus: 5 judgments sequential 46.2 s (about 9 s per call; the earlier 81 s figure was a slower moment); 5 judgments on 5 workers 11.7 s; with `FORGE_EFFORT=low` 8.6 s and 35% fewer output tokens (3,823 vs 5,791). 25 judgments, effort low: 25.7 s on 8 workers, 14.9 s on 16 workers, no rate-limit errors; sequential would be about 230 s. The 30 s promise is met only with effort low. Effort low agreed with default effort on all 10 items of one 10-item sample (it is a single sample, not an accuracy result); effort medium produced one invalid-output retry in 5 calls. Run `scripts/bench_judging.py` to repeat (it costs money).
- **Retrieval (addressed 2026-11-25):** ranking is now BM25 (`app/retrieval.py`) and the 250-record cap no longer cuts by deadline when reading the stored copy. `python scripts/retrieval_check.py` compares it with the old word-overlap ranking on a frozen snapshot of 787 posted records and 6 labelled research-area queries (no model, no cost). Result: mean recall@10 0.26 -> 0.75, MRR 0.51 -> 1.00. What this proves: on these 6 queries BM25 puts far more of the records one rater judged relevant near the top. What it does not prove: the labels come from one rater (an AI assistant) skimming keyword search results, so they are unreviewed and biased toward keyword matches; 6 queries and 3 to 10 relevant records each is too small for a reliable percentage; it ignores deadlines and says nothing about whether the model rates the records correctly. Live spot check (cancer-detection profile, 10 judgments, effort low): 7 of 10 judged records were not Excluded; the earlier photobiology profile matched almost nothing because the stored corpus has no photobiology records, so the two runs are not a like-for-like before and after.
- **PI lookup:** no OpenAlex code yet, so a researcher cannot be searched by name.
- **Front end:** Match, Results, Calendar and Review are connected (checked end to end with a real run). The Settings (admin) page is still sample data, and the opportunity-and-department path is disabled in live mode.
- **Repeatability:** the same inputs gave 2 results on one run and 1 on the next, so ratings can vary between runs. Not yet measured.
- **Accuracy:** the gold-set expected labels are blank, so agreement with a human cannot be scored.
- **Email:** dummy mode only; nothing is sent.
- **Cost:** model prices are not entered in settings, so cost per run is not reported.
