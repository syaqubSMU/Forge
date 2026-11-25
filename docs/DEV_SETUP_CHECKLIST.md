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

## 3b. Pilot budget (the owner's ceiling is $20 for the WHOLE pilot, spend already made included; live model only when important; if it looks like overrunning, ask the owner)
Assumed pilot window: Dec 2 to 6 (the PRD schedule; the owner did not state a length). Estimates use list prices for `claude-opus-5-5` of $4 per million input tokens and $20 per million output tokens (as of 2026-11-03; the owner confirms them in the provider console). A 25-judgment run is about $0.77 (about 32,000 input and 30,000 output tokens); at **15 judgments about $0.44**. About $7 is assumed already spent on engineering tests (not in the database), leaving about **$13**.
**Sizing the daily cap (recompute it from the real pilot length and the remaining budget):** $13 over five days (Dec 2 to 6) is $2.60 a day; at about $0.45 a run that is 5 to 6 runs a day. The built-in default is **5**. Example of a wrong number: a cap of 10 is up to $4.50 a day, about $22 over five days, more than is left.
- [ ] **Provider spending limit (owner, in the provider console):** $20 or lower for the pilot. This is the only hard guarantee; **confirm in the console whether the limit is monthly, per workspace or per key** (this document does not know the console's wording). No value or key goes in this file. The fastest hard stops are the provider limit or removing the key.
- [ ] **Safe defaults (built in):** `daily_cap` 5, `rate_limit_per_hour` 3 per visitor, `max_judgments` 15. Check with `GET /api/admin/settings` and `GET /api/admin/environment`; the old defaults (200 a day, 20 an hour, 25 judgments) could spend about $88 in a day if a public link were shared. An existing database keeps any value already saved in its settings table, so check there too.
- [ ] **Prices in settings** (after the owner confirms them in the console): `PUT /api/admin/settings` with `{"price_per_mtok_input": 4.0, "price_per_mtok_output": 20.0}`. Without both, `cost_usd` stays empty and the application budget stop is inactive.
- [ ] **Application budget stop:** setting `pilot_budget_usd` (default 11.0, send decimals such as `11.0`). Once the sum of recorded run costs (`runs.cost_usd`) reaches it, new live runs are refused with a plain message (`budget_reached`) and the recorded example run is offered instead. It reads the database, so it survives restarts. **It is inactive when no prices are set**, and `GET /api/admin/environment` says so: `budget_stop.state` is `"inactive: prices not set"`. It undercounts (failed or abandoned calls, and the roughly $7 of earlier spend are not in the database), so it sits below the provider limit, which stays the real guard.
- [ ] **Reading the cost after each run:** `counters.cost_usd` in the run response (an estimate; `cost_basis` says so); the admin run list and `GET /api/admin/runs.csv` (column `cost_usd_estimate`). Sum that column for the spend so far; treat the real spend as a little above it and compare with the provider console.
- [ ] **Spend tally:** one running line with the owner (date, runs, sum of `cost_usd_estimate`, console figure). Check it before any batch of runs.
- [ ] **Recorded run for the public pages:** ONE real run on a fictional researcher, made with `scripts/record_run.py` (about $0.44) only after the project manager and the architect approve. It writes the unedited output with its run id, model, rubric version, retrieval date, counters and input, and `python scripts/record_run.py --verify --out FILE` re-checks a written file for edits at no cost.
- [ ] **Scripts that spend money** (`bench_judging`, `repeatability`, `model_check` in live mode, `record_run`) print the planned number of calls and an estimated cost and do nothing unless `--yes-spend-money` is given. Do not add the flag without the approvals in this section.
- [ ] **Stop points:** the project manager warns the owner at about $13 estimated, and asks again at $16. **At about $15 estimated, set `daily_cap` to 0 and ask the owner**; at $18 all live calls stop unless the owner says otherwise. Switch visitors to the recorded run (`live: false` in the pages' `config.js`).
- [ ] **Limits of a stop (know these):**
  1. `daily_cap` 0 does **not** stop runs already in flight; they finish, up to the 90-second judging deadline plus calls already running.
  2. The cap check is count-then-start, not atomic, so simultaneous requests at the cap can each pass; keep the cap below the budget by a margin.
  3. The daily count resets at UTC midnight, which is 18:00 Central during Dec 2 to 6, so a cap of 5 allows 5 more runs after 18:00 Central; account for that when sizing it.
  4. Setting `active_model` to `mock` also spends nothing, but live runs then fail with 502 instead of the daily-limit message.
- [ ] **Not allowed without the owner's approval:** model changes, the larger repeatability check (about 500 calls, roughly $15, declined), and any engineering run against the live model. After ANY live call, report the calls, tokens and dollar estimate to the project manager with a running total.

## 4. Do not
- Do not put values in this file, tickets or chat. Do not pass the database address with `--db` (it appears in process lists and shell history).
- Do not point the Neon smoke test, the benchmark scripts or the test suite at a production database.
