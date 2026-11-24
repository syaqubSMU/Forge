# FORGE SIGNAL backend (v0.2 skeleton)

Scope: `docs/PRD_v0.2.md` (governed by the Business Case). Nothing here calls a live model or a live source yet.

## Run locally
    pip install -r requirements.txt
    export ADMIN_TOKEN=choose-a-long-random-string     # admin API is disabled without it
    export FORGE_DB=forge.db                           # SQLite file; :memory: for a throwaway run
    uvicorn --factory app.main:create_app --port 8000

## Tests
    python -m pytest -q

## Environment variables (server only; never sent to the page)
| Name | Purpose |
|---|---|
| `ADMIN_TOKEN` | Admin API sign-in. Required for every `/api/admin/*` call. |
| `FORGE_DB` | Run log location: a SQLite file path (default `forge.db`, `:memory:` for a throwaway run) or a `postgresql://` URL (Neon, Render, Supabase or any Postgres 14+). The tables are created on first start. |
| `FORGE_SALT` | Salt for the visitor hash used by rate limiting. |
| `ANTHROPIC_API_KEY` | Only when the active model is `claude`. Never returned by the API. |
| `FORGE_MODEL` | Optional model id for the Claude adapter. |

## Endpoints
Public: `GET /api/health`, `GET /api/notice`, `POST /api/runs`, `POST /api/runs/{id}/email` (needs a ticked confirmation).
Admin (`X-Admin-Token`): settings (incl. the model switch), audit, run log + detail + CSV, annotations, retention, rubric view/preview/publish.

## Not built yet
Live source pulls (Grants.gov, OpenAlex, faculty pages), calendar and .xlsx/.ics exports, real email delivery,
model factor extraction for the rubric, the front end. `POST /api/runs` currently requires supplied `sources`.

## Stored Grants.gov copy (replaces the live-only pull)
`POST /api/admin/ingest` (admin token) lists every posted and forecasted opportunity, reads full text for records
that have none or close within 12 months, and logs every Grants.gov request in `api_calls`
(`GET /api/admin/api-calls`, `GET /api/admin/ingest/status`). Runs then read the stored copy and report when it was
retrieved; until the first ingest they pull live, as before. Measured on 2026-11-24: 1,372 records with full text
in 72 s, 0 failures. Researcher profiles and judgments are never stored in this table.
