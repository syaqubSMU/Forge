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
| `scripts/model_check.py` | Scores the model on `evals/gold_set.json`. `--mock` for a dry run. Live mode uses the key and costs money: it prints a plan and runs only with `--yes-spend-money`. |
| `scripts/bench_judging.py` | Times the judging step with the live model on the stored corpus (costs money; prints a plan and needs `--yes-spend-money`; use `--n 3` to `5`; it writes a run into the database it is given, so use a local or dev database, never production). |
| `scripts/record_run.py` | Records ONE real run on a fictional researcher for the public pages (typically 15 to 17 calls, at most about 30, about $0.45 typical and $0.9 at most). Needs `--yes-spend-money` and `--price-in/--price-out`, works on a copy of a SQLite file, re-checks every quote against its stored source text, runs the recorded-run integrity checks and writes `recorded-run.js` plus `recorded-run.run-detail.json` (hash recorded in the file) only if all pass. `--verify` re-checks a written file and its exported detail at no cost. Refuses to spend from a dirty git tree. Not yet run. |
| `scripts/ingest.py` | Fills or refreshes the stored Grants.gov copy from a command line or scheduled job (`--db`, defaults to `FORGE_DB`). One JSON line; exit 0 all stored, 1 some details failed, 2 could not run. Measured on a local Postgres 16: 1,376 records, 68 s, 0 failures. |
| `scripts/db_smoke.py` | Smoke test of a hosted database: connects via `FORGE_DB` (never printed), migrates, writes and reads a throwaway run, measures round-trip latency, times the batched read of stored records and checks recovery after a dropped connection. Run before the first real deploy. Verified only against a local Postgres 16; not yet run on Neon. |
| `scripts/migrate.py` | Shows or applies schema migrations (servers also apply them on start). |
| `scripts/retrieval_check.py` | Ranking comparison on the frozen labelled snapshot (no model, no cost). |
| `scripts/grants_check.py` | Live Grants.gov check (no model, no key, no cost). |
| `scripts/calibrate.py`, `scripts/template_cli.py` | Rubric calibration and the Excel template for editing criteria. |

## Environment variables (server only; never sent to the page)
| Name | Purpose |
|---|---|
| `ADMIN_TOKEN` | Admin API sign-in. Required for every `/api/admin/*` call. |
| `FORGE_DB` | Run log and stored opportunities: a SQLite file path (default `forge.db`, `:memory:` for a throwaway run) or a `postgresql://` URL (Neon, Render, Supabase or any Postgres 14+). Schema migrations are applied on start. |
| `FORGE_SALT` | Salt for the visitor hash used by rate limiting. **Set it in every hosted environment**; the server logs a warning at start if a hosted database is used without it. |
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
- **Repeatability (measured 2026-11-25, small):** `scripts/repeatability.py` (needs `--yes-spend-money`) runs the same input several times with a fixed candidate set. Cancer-detection profile, 4 runs x 8 items, 8 workers (64 live calls per effort setting). Default effort: 7 of 8 items got the same tier in every run, visible-list Jaccard 0.92, list sizes 6/5/6/6, mean 17.7 s per run, 43.8k output tokens in total. Effort low: 5 of 8 stable, Jaccard 0.89, list sizes 5/6/6/5, 9.8 s per run, 27.8k output tokens (37% fewer). Tiers that moved were adjacent (Direct/Very strong, Strong/Very strong) except one record that swung between Excluded, Conditional and Strong at low effort. One profile and 4 runs is too small to call the difference between efforts significant, but low was not more stable. The visible list does change between runs; nothing in the code smooths that. Low effort is therefore not the production default until a larger check says otherwise.
- **Accuracy:** the gold-set expected labels are blank, so agreement with a human cannot be scored.
- **Email:** dummy mode only; nothing is sent.
- **Output cap and cost per run (measured from printed counters, one run each, 25 judgments):** with the old 1,500-token cap 26 calls used 33,661 input and 31,920 output tokens (8 workers) and 34,006 / 31,115 (16 workers); with the 3,000 cap 25 calls used 32,326 input and 30,350 output tokens. About 1,230 against 1,214 output tokens per call, so the larger cap adds no measurable cost; the old runs paid slightly more because the truncated answer was retried at the cap. Indicative only.
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

Errors arrive as `{"detail": {"code", "message"}}`. Limits: `pi_lookups_per_hour` (60, per visitor), `pi_lookups_per_day` (1000, all visitors); both counted in memory per process, so they reset on restart. Answers are cached in memory for 10 minutes (never in the database). Every real OpenAlex call is written to `api_calls` with endpoint, status and latency; for a name search the stored params are only the name's length; for expertise the author id is stored only as a keyed HMAC (`FORGE_SALT`), so neither the name nor who was looked up can be read back or guessed from `api_calls`. Requests carry the client name `forge-signal` and no email. Limits of the data: OpenAlex can split or merge people; terms are OpenAlex's own topic names, not the words funders use. Live check: 2 calls (one search, one expertise) for a well-known public researcher.

## Request limits and client address
Public POST bodies are capped at 400 KB (`FORGE_MAX_BODY_BYTES`; 413 above, 411 without a length). Question 1,000 characters, each research area 300, each positioning rule 600, at most 3 pasted sources of 20,000 characters each (lowered from 5 x 60,000, which could mean about 75,000 input tokens per request). The client address for rate limits is the connection's address unless `FORGE_TRUSTED_PROXY_HOPS=N` is set for N trusted proxies (then the Nth entry from the right of `X-Forwarded-For`). Additional server-side settings: `judge_deadline_s` (90), `FORGE_MODEL_MAX_CONCURRENT` (16, whole process). Run a single server worker for the demo: every cap and limiter above is per process.

**Checking the client address (do this once on the real host).** Set `ADMIN_TOKEN`, then from your own browser or `curl` call `GET /api/admin/whoami` with the `X-Admin-Token` header. It returns `believed_client_ip`, the connection's `socket_peer`, the raw `x_forwarded_for` header and the current `trusted_proxy_hops`. With `FORGE_TRUSTED_PROXY_HOPS` unset, `believed_client_ip` will be the proxy's address, the same for everyone (that is the problem to fix). Set it to 1, restart, and call again from two different networks (for example your phone off Wi-Fi): `believed_client_ip` should now be your own public address and differ between the two. If it shows a private or the proxy's address, try 2. The endpoint is admin-only; the address is never returned to the public.

**One server worker.** Production runs a single server process. Every limiter and cap described above (visitor hourly limit, daily lookup cap, model-call cap, OpenAlex cache) lives in that process's memory; with several workers each would have its own counters and the limits would multiply.

Run ids are 32 hex characters for new runs; the 12-character ids of earlier runs still open.

**Disclosure the pages must make (front end).** The name a person types is sent to OpenAlex, a third party; the page and About must say so in one line. Expertise terms are proposals: the person must be able to edit or remove each one and confirm before `POST /api/runs` is called.

**Before the first deploy**
- *Model:* the default `active_model` is `mock`, which returns `{}`; every live run then fails with 502 "answers could not be read". An admin must set `active_model` to `claude` (`PUT /api/admin/settings`) and the server needs a model key.
- *A run where nothing could be rated* (every call failed, or every answer was unreadable) is a failed run with HTTP 502, never an empty list. Two texts: "The model could not be reached..." and "The model's answers could not be read...".
- *Database address:* pass it through `FORGE_DB`, not `--db`; command lines show in process lists and shell history.
- *Neon:* session-level advisory locks (used to keep two starting servers from racing on migrations) do not work through a pooled (PgBouncer, transaction-mode) connection string. Use the direct connection string for `FORGE_DB`, or at least for `scripts/migrate.py`, and confirm on the dev rehearsal.
- *Deploys and rollbacks:* migrations must be additive (new tables or nullable columns; never drop, rename or tighten) because an old and a new server can overlap during a deploy, and rolling code back is only safe when every migration since was additive.
- *Proxy header rehearsal:* with `FORGE_TRUSTED_PROXY_HOPS` set, also send a request with a forged prefix, for example `X-Forwarded-For: 6.6.6.6` added by the client, and confirm `/api/admin/whoami` still reports your real address and not 6.6.6.6. If it reports the forged one the value is too large. Record the confirmed value for Render.
- *Cost estimate:* `cost_usd` is an estimate from reported usage and needs both prices set; it excludes calls that were abandoned or failed.

## Running the Neon smoke test (owner, on your own computer or the dev service)
Use a **dev or scratch Neon branch with its own password, never production.** The sandbox the engineers work in cannot safely hold a database password and may not reach Postgres at all, so you run this yourself. The scripts never print the database address or password.
1. In Neon, create a branch named `dev-smoke` from your project. Open its connection details and copy the **direct** connection string (host without `-pooler`), not the pooled one: the migration lock does not work through the pooler.
2. On your computer, in a terminal, from the `backend/` folder: `pip install -r requirements.txt`.
3. Put the string in an environment variable for this terminal only (do not put it on the command line): macOS or Linux `export FORGE_DB='postgresql://...'`; Windows PowerShell `$env:FORGE_DB='postgresql://...'`.
4. Run `python scripts/db_smoke.py`. **Pass:** every line starts with `PASS` and the last line is `RESULT: all checks passed` (one `SKIP` about the batched read is normal before step 5). **Fail:** any `FAIL` line, or the exit code is not 0.
5. Run `python scripts/ingest.py`. **Pass:** one JSON line with `"ok": true`, `details_failed` 0 and `schema_version` 2. It reads about 1,400 records from Grants.gov and writes them one by one, so expect a few minutes (local Postgres took 68 s; Neon will be slower, and that time is the number to report).
6. Run `python scripts/db_smoke.py` again. It now also times the batched read of 250 stored records.
7. Optional, on a **separate throwaway branch only** (the test suite drops everything in the database it is pointed at): `FORGE_TEST_PG_URL` set to that branch's direct string, then `python -m pytest -q`. Pass: all tests pass, 1 skipped.
8. Send back the full text printed by steps 4 to 7. It contains timings and PASS/FAIL lines but never the address. Then delete the `dev-smoke` branch.

## Rehearsal checklist (on the dev service, before the real deploy)
Run these once on the dev environment; none has been verified yet. Record each result in the commit that closes it.
1. **Hosted settings present:** `FORGE_SALT`, `ADMIN_TOKEN`, a model key and `FORGE_DB` (direct connection string) are set; the start-up log has no `FORGE_SALT is not set` warning; `active_model` is `claude`; one server worker.
2. **Forged header ignored:** with `FORGE_TRUSTED_PROXY_HOPS` set to 1, call `GET /api/admin/whoami` with your admin token while adding your own header `X-Forwarded-For: 6.6.6.6`. `believed_client_ip` must still be your real public address, not 6.6.6.6. If it shows 6.6.6.6 the value is too large for this host.
3. **Render hop value:** call `/api/admin/whoami` from two different networks (for example your phone off Wi-Fi). With the right value `believed_client_ip` is each network's own address and differs between the two; with the value unset it is the same proxy address for both. Write down the value that works.
4. **Two simultaneous runs:** start two live runs at the same moment from two browsers or terminals. Both must finish without a 429 or a 502, and each must report `counters.judged` above 0. If either is refused or runs slowly, note the times before changing `FORGE_MODEL_MAX_CONCURRENT` (default 16; each run uses up to `judge_concurrency`, default 8).
5. **Timing:** one live run with the default 25 judgments; note `counters.latency_ms` and `judging_ms`. The measured sandbox figure was about 22 to 24 s at 16 workers and about 44 s at 8.
6. **Failure paths:** with the model key temporarily wrong on the dev service only, a live run must return 502 "The model could not be reached...", and the run must show as failed in the admin run list.

**Cost figures are estimates.** `runs.cost_usd` (and the `cost_usd_estimate` column of the run-log CSV) is tokens reported by the model API times the prices in settings. It needs both prices set and excludes calls that were abandoned or failed. The admin page should label the column "estimate".

**Checking which settings are in effect.** `GET /api/admin/environment` (admin token) reports, without any secret value: database kind (never its address), schema version, whether `ADMIN_TOKEN` and `FORGE_SALT` are set, the NAME of the model-key variable found, the active model, effort, proxy hops, allowed page origins, the concurrency caps, and whether the static pages folder was found.

## Pilot budget controls (summary; the owner's steps are in docs/DEV_SETUP_CHECKLIST.md section 3b)
Defaults sized to a $20 pilot: `daily_cap` 3, `rate_limit_per_hour` 3, `max_judgments` 15 (tests keep their own generous fixtures). `pilot_budget_usd` (9.0, counting only this database's runs) refuses new live runs with `{"code": "budget_reached", ...}` (HTTP 503) once the recorded cost estimate reaches it; active out of the box because the default prices (4.0 and 20.0 USD per million tokens, estimates of the opus-5-5 list prices, owner to confirm) are non-zero; failed runs keep their cost; `/api/admin/environment` reports `budget_stop` (state, limit, recorded estimate, prices in use, what is counted) plus the three caps. Every script that spends model money prints its planned calls and estimated cost and needs `--yes-spend-money`.

**Mock runs cost nothing.** The mock model makes no paid call, so its runs store no `cost_usd` and never count toward the budget sum or the budget stop (its token figures are only character counts, used by tests). A test with fake priced models uses an adapter named differently from `mock`.

## Tester access codes
Live runs need an access code the owner created (`require_access_code`, default true; tests and local use turn it off). `POST /api/runs` (both the live and the pasted-evidence paths) takes it in the `X-Access-Code` header; the researcher lookup `/api/pi/*` also needs a valid code, checked but never spending an allowance. Owner endpoints (admin token): `POST /api/admin/access-codes {"label","allowance","expires_at"}` (the code is returned once), `GET /api/admin/access-codes` (usage and cost per code, never the code), `POST /api/admin/access-codes/{id}/revoke`. Public: `GET /api/access/check` (same header; `{"required","valid","remaining","expires_at"}`, spends nothing). Refusals: 403 `{"code": "missing|invalid|expired|revoked|allowance_used", "message", "recorded_example": true}`; 429 `too_many_attempts` (only FAILED attempts count, about 20 an hour per visitor address, in memory, never logged; no code is ever locked); 429 `run_in_progress` (one live run in flight per code, single process). A successful run response carries `access: {remaining}`. Codes are stored only as an HMAC keyed from `FORGE_SALT` (set it before creating codes; changing it invalidates them), never logged and never returned after creation.
**Budget reservation:** creating a code is refused (409 `budget_would_be_exceeded`, with the numbers in the message) when recorded spend plus every run still allowed to usable codes plus the new code's runs, times the estimated cost of one run, would exceed `pilot_budget_usd` (9.0). The run estimate is derived from `max_judgments` times `estimated_cost_per_judgment_usd` (0.03), so 15 judgments is $0.45 a run and raising `max_judgments` automatically raises the estimate (the reservation cannot undercount). With those values 20 runs fit exactly: six testers of 3 plus an owner code of 2 ($9.00); an owner code of 3 is refused unless the owner raises the budget on purpose. Revoking a code or using its runs frees budget. On a hosted (Postgres) database an `ADMIN_TOKEN` shorter than 32 characters disables the admin API (503, plain message). Design: `docs/BACKEND_DECISIONS.md` D7; owner steps: `docs/DEV_SETUP_CHECKLIST.md` section 3c.

If the pages are ever served from a different host than the engine, list the pages' address in `FORGE_CORS_ORIGINS`; the engine then allows the `X-Access-Code` header (as well as `Content-Type` and `X-Admin-Token`) in cross-site requests. An unexpected server error after a run has started marks that run failed (never left "running") and refunds the allowance if nothing was billed; the error text is not stored. `GET /api/admin/environment` shows `access_codes.budget_reservation` (runs still allowed, committed estimate, recorded spend, total against `pilot_budget_usd`).
