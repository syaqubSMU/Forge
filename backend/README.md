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
    FORGE_TEST_PG_URL=postgresql://user@host:5432/db python -m pytest -q   # the same suite on Postgres (conftest swaps every module's Database, tests included)

## Scripts (run from `backend/`)
| Script | Purpose |
|---|---|
| `scripts/model_check.py` | Scores the model on `evals/gold_set.json`. `--mock` for a dry run. Uses the key and costs a few cents live. |
| `scripts/bench_judging.py` | Times the judging step with the live model on the stored corpus (costs money; use `--n 3` to `5`; it writes a run into the database it is given, so use a local or dev database, never production). |
| `scripts/ingest.py` | Fills or refreshes the stored Grants.gov copy from a command line or scheduled job (`--db`, defaults to `FORGE_DB`). One JSON line; exit 0 all stored, 1 some details failed, 2 could not run. Measured on a local Postgres 16: 1,376 records, 68 s, 0 failures. |
| `scripts/migrate.py` | Shows or applies schema migrations (servers also apply them on start). |
| `scripts/retrieval_check.py` | Ranking comparison on the frozen labelled snapshot (no model, no cost). |
| `scripts/grants_check.py` | Live Grants.gov check (no model, no key, no cost). |
| `scripts/calibrate.py`, `scripts/template_cli.py` | Rubric calibration and the Excel template for editing criteria. |

## Environment variables (server only; never sent to the page)
| Name | Purpose |
|---|---|
| `ADMIN_TOKEN` | Admin API sign-in. Required for every `/api/admin/*` call. |
| `FORGE_DB` | Run log and stored opportunities: a SQLite file path (default `forge.db`, `:memory:` for a throwaway run) or a `postgresql://` URL (Neon, Render, Supabase or any Postgres 14+). Schema migrations are applied on start. |
| `FORGE_SALT` | Salt for the visitor hash used by rate limiting. |
| `FORGE_MODEL_KEY`, `FORGE_API_KEY`, `SIGNAL_MODEL_KEY`, `ANTHROPIC_API_KEY` | Model key. Any one works; the first set wins in that order. Never returned by the API or logged. |
| `FORGE_MODEL` | Model id for the Claude adapter (default `claude-opus-5-5`). |
| `FORGE_EFFORT` | Model effort level (unset = model default; production value not yet decided: low is fastest but was not more repeatable and its accuracy has not been measured against labelled answers, since the gold labels are blank) (`low`, `medium`, `high`). `low` is recommended for bulk screening: about 35% fewer output tokens and 25% less time in the measured sample. |
| `FORGE_STATIC` | Folder of web pages to serve (default: `public/signal` in this repository). |
| `FORGE_CORS_ORIGINS` | Comma-separated page addresses allowed to call the API from another host. Empty by default (same-address only). |
| `FORGE_TRUSTED_PROXY_HOPS` | Number of trusted proxies in front of the server (Render: 1, to be confirmed). Default 0: `X-Forwarded-For` ignored. |
| `FORGE_MAX_BODY_BYTES` | Cap on public POST bodies (default 400000). |
| `FORGE_MODEL_MAX_CONCURRENT` | Process-wide cap on simultaneous model calls (default 16). |
| `FORGE_API_BASE` | Optional override of the model API address (default `https://api.anthropic.com`). |

## Endpoints
Public: `POST /api/pi/search` and `GET /api/pi/{author_id}/expertise` (see Researcher lookup), `GET /api/health`, `GET /api/notice`, `GET /config.js`, `POST /api/runs` (optional per-run `options`: `horizon_months` 1 to 36 and `lead_time_days` 0 to 365; they apply to that run only, and every response carries a `source` block naming Grants.gov's public API and when the stored copy was retrieved), `POST /api/runs/{id}/email` (needs a ticked confirmation; dummy mode logs only), `GET /api/runs/{id}/calendar`, `.ics` and `.xlsx`.
Admin (header `X-Admin-Token`): settings (including the model switch) and audit trail; run log, run detail, CSV and annotations; retention; rubric view, preview and publish; `POST /api/admin/ingest`, `GET /api/admin/ingest/status`, `GET /api/admin/api-calls`.
Safeguards: per-visitor hourly rate limit, a daily run cap, no raw source text returned to the public, spreadsheet-formula protection in exports.

## Stored Grants.gov copy
`POST /api/admin/ingest` lists every posted and forecasted opportunity, reads full text for records that have none or close within 12 months, and logs every Grants.gov request in `api_calls`. Runs then read the stored copy and report when it was retrieved; until the first ingest they pull live. Measured on 2026-11-24: 1,372 records with full text in 72 s, 0 failures. Researcher profiles and judgments are never stored in this table.

## Known gaps (as of 2026-11-24)
- **Speed (addressed 2026-11-25):** judgments now run in a bounded thread pool (`judge_concurrency` setting, default 8, hard cap 16); the SDK retries 429/overload with backoff (`FORGE_MODEL_RETRIES`, default 6). Measured live on claude-opus-5-5, same profile and shortlist, stored corpus: 5 judgments sequential 46.2 s (about 9 s per call; the earlier 81 s figure was a slower moment); 5 judgments on 5 workers 11.7 s; with `FORGE_EFFORT=low` 8.6 s and 35% fewer output tokens (3,823 vs 5,791). 25 judgments, effort low: 25.7 s on 8 workers, 14.9 s on 16 workers, no rate-limit errors; sequential would be about 230 s. The 30 s promise is met only with effort low. Effort low agreed with default effort on all 10 items of one 10-item sample (it is a single sample, not an accuracy result); effort medium produced one invalid-output retry in 5 calls. **25 judgments at default effort (measured later the same day, cancer-detection profile):** 43.5 s on 8 workers and 24.1 s on 16 workers, no rate-limit or timeout errors. Both runs lost 1 of 25 judgments to truncated JSON: the model output cap was 1,500 tokens and one long answer was cut off (the retry hit the same cap). The cap is now 3,000 (`FORGE_MAX_OUTPUT_TOKENS`); a rerun on 16 workers gave 25 of 25 judged in 21.8 s, 30.4k output tokens. So the under-30 s promise holds at default effort only with about 16 workers (one run each, a single profile; 8 workers misses it at 43 s). Before this fix, any long answer silently dropped out of a run as "model output invalid". Run `scripts/bench_judging.py` to repeat (it costs money).
- **Retrieval (addressed 2026-11-25):** ranking is now BM25 (`app/retrieval.py`). Behaviour change users may notice: when reading the stored copy the shortlist now ranks every in-window record by relevance; the old 250-record cap cut by nearest deadline first. Records sharing no word with the research areas are not screened (`counters.no_term_overlap`); synonym-only matches are missed by design. Two-letter field names (AI, ML) count only when written in capitals. `python scripts/retrieval_check.py` compares it with the old word-overlap ranking on a frozen snapshot of 787 posted records and 6 labelled research-area queries (no model, no cost). Result: mean recall@10 0.26 -> 0.75, MRR 0.51 -> 1.00. What this proves: on these 6 queries BM25 puts far more of the records one rater judged relevant near the top. Tuning: K1 1.5 and B 0.75 are the standard defaults, and TITLE_WEIGHT 3, the stemmer and the boilerplate word list were written before the labelled check was first run and not changed after it, but I had skimmed corpus titles while labelling, so treat them as untuned rather than independent. MRR 1.00 on 6 queries is a ceiling, not a result, and `tests/test_retrieval.py` uses the labels only as a regression guard. A person (the project owner or a research administrator) should review and extend `evals/retrieval_labels.json` before any figure is quoted outside the repository. What it does not prove: the labels come from one rater (an AI assistant) skimming keyword search results, so they are unreviewed and biased toward keyword matches; 6 queries and 3 to 10 relevant records each is too small for a reliable percentage; it ignores deadlines and says nothing about whether the model rates the records correctly. Live spot check (cancer-detection profile, 10 judgments, effort low): 7 of 10 judged records were not Excluded; the earlier photobiology profile matched almost nothing because the stored corpus has no photobiology records, so the two runs are not a like-for-like before and after.
- **PI lookup (built locally, not yet approved or merged):** `GET /api/pi/search?name=` and `GET /api/pi/{author_id}/expertise` (OpenAlex, public). Verified live once against a public figure's records; not yet connected to the front end. OpenAlex sometimes splits one person into several records and can attach a namesake's works, which is why every term lists its source works and the person confirms before anything is screened.
- **Front end:** Match, Results, Calendar and Review are connected (checked end to end with a real run). The Settings (admin) page is still sample data, and the opportunity-and-department path is disabled in live mode.
- **Repeatability (measured 2026-11-25, small):** `scripts/repeatability.py` runs the same input several times with a fixed candidate set. Cancer-detection profile, 4 runs x 8 items, 8 workers (64 live calls per effort setting). Default effort: 7 of 8 items got the same tier in every run, visible-list Jaccard 0.92, list sizes 6/5/6/6, mean 17.7 s per run, 43.8k output tokens in total. Effort low: 5 of 8 stable, Jaccard 0.89, list sizes 5/6/6/5, 9.8 s per run, 27.8k output tokens (37% fewer). Tiers that moved were adjacent (Direct/Very strong, Strong/Very strong) except one record that swung between Excluded, Conditional and Strong at low effort. One profile and 4 runs is too small to call the difference between efforts significant, but low was not more stable. The visible list does change between runs; nothing in the code smooths that. Low effort is therefore not the production default until a larger check says otherwise.
- **Accuracy:** the gold-set expected labels are blank, so agreement with a human cannot be scored.
- **Email:** dummy mode only; nothing is sent.
- **Cost (code done, prices still needed):** each run now stores `cost_usd` = tokens x `price_per_mtok_input` / `price_per_mtok_output` (settings, USD per million tokens) and returns it in `counters`. It is `null`, not zero, while no price is set. The owner must enter current prices for the active model; I did not guess them.
- **Schema versioning:** numbered migrations in `app/migrations.py` (version 1 = the earlier schema, version 2 = `runs.cost_usd`), recorded in `schema_migrations`, tested on SQLite and Postgres including adoption of an unversioned database and rollback of a failing migration.

## Researcher lookup (OpenAlex)
`POST /api/pi/search` body `{"name": "..."}` (a POST so the name never appears in a URL or access log) returns `{status: single|multiple|ambiguous|no_match, note, candidates: [{openalex_id, name, institutions[], works_count, cited_by_count, last_active_year, top_topics[]}], source}`, up to 10 candidates. Same-name records are never merged; `ambiguous` says so. `GET /api/pi/{author_id}/expertise` returns `{status: ok|no_works, note, works_considered, from_year, terms: [{term, work_count, proposed: true, works: [{title, year, url}]}], source}`: terms are proposals the person edits; the front end confirms by calling `POST /api/runs` with them as `profile.lanes`.

| Situation | HTTP | `detail.code` | Text shown as written |
|---|---|---|---|
| No researcher matches | 200 | (status `no_match`) | note: "OpenAlex has no researcher matching that name. Check the spelling, try fewer words, or type the research areas yourself." |
| Name under 2 or over 120 characters | 400 | `name_too_short` / `name_too_long` | "Enter at least 2 characters of the researcher's name." / "That name is too long. Enter at most 120 characters." |
| Bad author id | 400 | `bad_author_id` | "That is not a valid OpenAlex author id. Search by name and pick a candidate." |
| Our hourly limit (per visitor) | 429 | `hourly_limit` | "Too many lookups from this visitor. Please try again in about an hour." |
| Our daily limit (all visitors) | 429 | `daily_limit` | "The daily limit for researcher lookups has been reached. Please try again tomorrow." |
| OpenAlex timeout (15 s) | 504 | `upstream_timeout` | "OpenAlex took too long to answer. Please try again in a moment." |
| OpenAlex rate limit | 503 | `upstream_rate_limited` | "OpenAlex is limiting requests right now. Please wait a minute and try again." |
| OpenAlex outage or non-200 | 502 | `upstream_unavailable` | "OpenAlex could not be reached or is having an outage. You can continue by typing the research areas yourself." |
| Unreadable answer | 502 | `upstream_bad_response` | "OpenAlex returned an answer that could not be read. You can continue by typing the research areas yourself." |

Errors arrive as `{"detail": {"code", "message"}}`. Limits: `pi_lookups_per_hour` (60, per visitor), `pi_lookups_per_day` (1000, all visitors); both counted in memory per process, so they reset on restart. Answers are cached in memory for 10 minutes (never in the database). Every real OpenAlex call is written to `api_calls` with endpoint, status and latency; for a name search the stored params are the name's length and a truncated SHA-256, never the name. Requests carry the client name `forge-signal` and no email. Limits of the data: OpenAlex can split or merge people; terms are OpenAlex's own topic names, not the words funders use. Live check: 2 calls (one search, one expertise) for a well-known public researcher.

## Request limits and client address
Public POST bodies are capped at 400 KB (`FORGE_MAX_BODY_BYTES`; 413 above, 411 without a length). Question 1,000 characters, each research area 300, each positioning rule 600, at most 5 pasted sources of 60,000 characters each. The client address for rate limits is the connection's address unless `FORGE_TRUSTED_PROXY_HOPS=N` is set for N trusted proxies (then the Nth entry from the right of `X-Forwarded-For`). Additional server-side settings: `judge_deadline_s` (90), `FORGE_MODEL_MAX_CONCURRENT` (16, whole process). Run a single server worker for the demo: every cap and limiter above is per process.
