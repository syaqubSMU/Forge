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

## 3b. Pilot budget (the customer's ceiling is $20 for the whole pilot, spend already made included; if it is reached, ask the customer before spending more)
Estimates use list prices for `claude-opus-5-5` of $4 per million input tokens and $20 per million output tokens (as of 2026-11-03; confirm in the provider console). A 25-judgment run used about 32,000 input and 30,000 output tokens, so about **$0.75 per run** and about 3 cents per judgment. About $7 is assumed already spent on engineering tests, leaving about **$13, roughly 17 full runs** at 25 judgments.
- [ ] **Provider spending limit (owner, in the provider console):** set a monthly limit of $20 or lower. This is the only hard guarantee; everything below only lowers the risk. No value or key goes in this file.
- [ ] **Prices in settings** (once the service is hosted and the owner confirms them): `PUT /api/admin/settings` with `{"price_per_mtok_input": 4.0, "price_per_mtok_output": 20.0}`. Without both, `cost_usd` stays empty.
- [ ] **Runs per day:** set `daily_cap` to a small number sized to the pilot (for example 10; at about $0.75 a run that is up to about $7.50 a day, so choose it from the pilot length and the remaining budget, not from the default of 200).
- [ ] **Runs per visitor per hour:** set `rate_limit_per_hour` to 3 (default 20).
- [ ] **Judgments per run:** `max_judgments` 15 instead of 25 lowers a run to about $0.45, at the price of fewer opportunities checked. Change it only if the customer agrees.
- [ ] **Reading the cost after each run:** the run response carries `counters.cost_usd` (an estimate from reported usage, with `cost_basis` saying so); the admin run list and `GET /api/admin/runs.csv` (column `cost_usd_estimate`) show it per run. Add up that column for the spend so far. It excludes calls that failed or were abandoned, so keep a margin: treat the real spend as a little above the sum, and compare with the provider console's usage page.
- [ ] **Spend tally:** keep a running line (date, runs, sum of `cost_usd_estimate`, console figure) with the owner. Check it before each batch of test runs.
- [ ] **When the budget is nearly spent (about $15 used by the estimate, or the console shows it):** stop live runs and ask the customer. To stop: `PUT /api/admin/settings` with `{"daily_cap": 0}` (the API then answers every live run with the daily-limit message and spends nothing) and send visitors to the published pages, which run in sample mode (their `config.js` has `live: false`). Re-open only after the customer agrees to more budget.
- [ ] **Not allowed without the customer's approval:** model changes, the larger repeatability check (about 500 calls, roughly $15, declined), and any engineering test run against the live model.

## 4. Do not
- Do not put values in this file, tickets or chat. Do not pass the database address with `--db` (it appears in process lists and shell history).
- Do not point the Neon smoke test, the benchmark scripts or the test suite at a production database.
