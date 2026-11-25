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

## 4. Do not
- Do not put values in this file, tickets or chat. Do not pass the database address with `--db` (it appears in process lists and shell history).
- Do not point the Neon smoke test, the benchmark scripts or the test suite at a production database.
