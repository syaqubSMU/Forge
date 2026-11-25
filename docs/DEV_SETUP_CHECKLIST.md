# Dev environment setup checklist (owner)

One page. Variable **names only**: never write a value or secret into this file, a chat or a commit. The Render menu names below are from general knowledge and were NOT checked against the live Render screens; the owner should correct any label that differs. Everything about the application itself is from this repository.

## 1. Service
- [ ] New **Web Service** from this repository, branch `integration` (dev only; main is the live site and is not touched by this).
- [ ] **Root directory:** `backend`
- [ ] **Build command:** `pip install -r requirements.txt`
- [ ] **Start command:** `uvicorn --factory app.main:create_app --host 0.0.0.0 --port $PORT`
- [ ] **One worker.** Do not add `--workers`, and do not scale to more than one instance: the rate limits, the model-call cap, the lookup cache and the daily caps live in each process's memory.
- [ ] **Health check path:** `/api/health` (returns `{"status":"ok", ...}`).
- [ ] Dev and production use **different databases and different passwords**.

## 2. Environment variables (set in the service's Environment tab)
| Name | Required | What it is for | Notes |
|---|---|---|---|
| `FORGE_DB` | yes | Database address | A `postgresql://` URL. For Neon use the **direct** (non-pooled) string. |
| `ADMIN_TOKEN` | yes | Admin sign-in | A long random string you generate. Admin pages and the checks below need it. |
| `FORGE_SALT` | yes | Salt for visitor hashes | A long random string, different from `ADMIN_TOKEN`. The server warns at start if it is missing. |
| `FORGE_API_KEY` | for live runs | Model key | Any of `FORGE_MODEL_KEY`, `FORGE_API_KEY`, `SIGNAL_MODEL_KEY`, `ANTHROPIC_API_KEY` works; use one. Set a spending limit with the model provider. |
| `FORGE_TRUSTED_PROXY_HOPS` | after rehearsal | Trusted proxies in front of the server | Leave unset until the rehearsal in `backend/README.md` finds the right number (expected 1). |
| `FORGE_CORS_ORIGINS` | only if pages are on another address | Page addresses allowed to call the API | Comma-separated. Empty when the server serves the pages itself. |
| `FORGE_MODEL_MAX_CONCURRENT` | optional | Cap on simultaneous model calls, whole process | Default 16. Change only after the two-simultaneous-runs rehearsal. |
| `FORGE_STATIC` | optional | Folder of web pages to serve | Default is `public/signal` in the repository; set only if the pages live elsewhere. |
| `FORGE_EFFORT` | optional | Model effort level | Leave unset (model default) until a larger repeatability check supports `low`. |

## 3. After the first start (admin token goes in the `X-Admin-Token` header; use your own terminal, never paste it into chat)
- [ ] `GET /api/health` returns `status: ok`.
- [ ] `GET /api/admin/environment` shows, without any secret value: `database: postgres`, `schema_version: 2` or higher, `admin_token_set: true`, `salt_set: true`, `model_key_variable` naming the variable you used, `static_dir_found: true`, `trusted_proxy_hops` as intended. If any is wrong, fix the variable and restart.
- [ ] **Switch the model to `claude` (easy to forget).** The default `active_model` is `mock`, which cannot rate anything. Send `PUT /api/admin/settings` with body `{"active_model": "claude"}`. **Pass:** `GET /api/admin/environment` now shows `"active_model": "claude"` and `model_key_variable` names the variable you set. **If a live run returns 502 "The model's answers could not be read", the model is still `mock`** (or the key is wrong: a wrong key gives 502 "could not be reached"); recheck this step and the key.
- [ ] Prices for cost estimates are entered as `price_per_mtok_input` and `price_per_mtok_output` in settings (the owner supplies the numbers).
- [ ] Run `python scripts/ingest.py` once (from `backend/`, `FORGE_DB` set in your shell) so runs read the stored copy; check `GET /api/admin/ingest/status`.
- [ ] Work through the rehearsal checklist in `backend/README.md`, then `FORGE_TRUSTED_PROXY_HOPS` can be set with confidence.

## 3b. Pilot budget (the owner's ceiling is $20 for the WHOLE pilot, spend already made included; live model only when important; if it is reached, ask the owner)
Assumed pilot window: Dec 2 to 6 (the PRD schedule; the owner did not state a length). Estimates use list prices for `claude-opus-5-5` of $4 per million input tokens and $20 per million output tokens (as of 2026-11-03; the owner confirms them in the provider console). A 25-judgment run used about 32,000 input and 30,000 output tokens, about $0.75; at **15 judgments about $0.44**. About $7 is assumed already spent on engineering tests, leaving about **$13, roughly 29 runs at 15 judgments**.
- [ ] **Provider spending limit (owner, in the provider console):** $20 or lower for the pilot. This is the only hard guarantee. No value or key goes in this file.
- [ ] **Safe defaults (built in by this branch):** `daily_cap` 6, `rate_limit_per_hour` 3 per visitor, `max_judgments` 15. Check them with `GET /api/admin/settings`; the old defaults (200 a day, 20 an hour, 25 judgments) could spend about $88 in a day if a public link were shared. Raise them only with the owner's approval and after checking the remaining budget. An existing database keeps any value already saved in its settings table, so check there too.
- [ ] **Prices in settings** (after the owner confirms them in the console): `PUT /api/admin/settings` with `{"price_per_mtok_input": 4.0, "price_per_mtok_output": 20.0}`. Without both, `cost_usd` stays empty.
- [ ] **Reading the cost after each run:** `counters.cost_usd` in the run response (an estimate from reported usage; `cost_basis` says so); the admin run list and `GET /api/admin/runs.csv` (column `cost_usd_estimate`) show it per run. Sum that column for the spend so far. It excludes failed or abandoned calls, so treat the real spend as a little above the sum and compare with the provider console.
- [ ] **Spend tally:** keep one running line with the owner (date, runs, sum of `cost_usd_estimate`, console figure). Check it before any batch of runs.
- [ ] **Recorded run for the public pages:** ONE real run on a fictional researcher, made with `scripts/record_run.py` (about $0.44), only after the project manager and the architect approve it. The public pages then show that recording instead of visitors spending model money.
- [ ] **When about $3 remain (by the estimate or the console):** stop live runs and show the recording. `PUT /api/admin/settings` with `{"daily_cap": 0}` makes the API answer every live run with the daily-limit message and spend nothing; the published pages run in sample or recorded mode (`live: false` in their `config.js`). Then ask the owner before reopening.
- [ ] **Not allowed without the owner's approval:** model changes, the larger repeatability check (about 500 calls, roughly $15, declined), and any engineering test run against the live model.

## 4. Do not
- Do not put values in this file, tickets or chat. Do not pass the database address with `--db` (it appears in process lists and shell history).
- Do not point the Neon smoke test, the benchmark scripts or the test suite at a production database.
