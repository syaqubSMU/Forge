# FORGE SIGNAL: Architecture

Status: architect document, approved by the project manager as a draft; decision statuses updated 25 Nov 2026 after the backend merge (`integration` da43450).
Basis: code read at commit db17872 on `claude/practical-franklin-ze9hk2`, `docs/PRD_v0.2.md`, `docs/SIGNAL_BOUNDARIES.md`, `backend/README.md`. What was run is listed in section 9; everything else is from reading code.

Decision status words: **Decided** (made by the customer or already built and accepted), **Proposed** (architect recommends, awaiting approval), **Open** (needs the project owner or more evidence).

## 1. Components

```
 Browser (static pages)            FastAPI engine (backend/app)                 Outside services
 public/signal/*.html, app.js ---> /api/runs, /api/runs/{id}/calendar... ----> Grants.gov public API (list + detail)
   config.js: live true/false      /api/admin/*  (X-Admin-Token)               Claude API (model adapter)
   sample mode = mock-data.js      pipeline.py  -> adapters/ -> validator.py   OpenAlex (PI lookup; P3 in review,
   run kept in sessionStorage      rubric.py, calendar.py, exports.py            host allowed by the owner 24 Nov)
                                   store.py (stored Grants.gov copy)
                                   db.py ------------------------------------> SQLite (local) or Postgres (Neon)
```

- **Pages**: seven static pages. With `live: false` (GitHub Pages) they show a fictional sample run and call nothing. With `live: true` they call the API. When the engine serves the pages itself it answers `/config.js` with `live: true`, which wins over the static file because API routes are mounted before the static folder.
- **Engine**: one FastAPI process. A run is one synchronous HTTP request.
- **Database**: one schema in SQLite or Postgres: run log (runs, matches, citations, source failures, email events, annotations), admin settings, audit trail, rubric versions, the stored Grants.gov copy (`opportunities`, `api_calls`).
- **Model**: behind `ModelAdapter`; the admin setting `active_model` picks the adapter for the next run. `mock` is the default and costs nothing.

## 2. Run data flow and trust boundaries

1. **Browser to API** (untrusted input). Visitor supplies name or text, research areas, career stage, rules, options. Validated by pydantic (length limits on `input_text` and some list sizes), per-visitor hourly limit and daily cap, option range checks.
2. **Source** (untrusted text). Stored Grants.gov copy, or a live pull until the first ingest. Sponsor text is untrusted: it goes into the model prompt.
3. **Shortlist** (plain code). Deadline window, then word-overlap ranking to bound spend. Not a fit judgment.
4. **Judge** (model, untrusted output). Threads call the adapter in parallel; the model returns factor values with quotes as JSON; the schema parser rejects anything else (one retry, then a recorded failure).
5. **Validate** (plain code). A quote must appear in the source text it names, or it is discarded and counted. A factor without a supported quote falls back to the rubric's conservative default.
6. **Rate** (plain code). `rubric.evaluate` computes the tier and word. Dates, days-to-deadline, internal deadline, calendar groups and exports are code.
7. **Log** (main thread only). Run, sources (hash only), matches, citations, failures, tokens, timing.
8. **API to browser**. No raw source text goes to the public; the run response carries the quotes, which are short extracts.

Trust boundaries: (a) browser to API; (b) API to Grants.gov and to the model provider (outbound, secrets leave only as the model key to the model host); (c) API to database; (d) admin token holder to admin API. The model key is read from server environment variables only. Residual risk named plainly: an injected instruction inside sponsor text could push the model to report a factor value and then quote the injected sentence, which the validator would accept because the sentence is in the source. The defences are the fixed rubric, code-computed tiers, conservative defaults for unsupported claims and mandatory human review; there is no technical block on this. Grants.gov is a federal source, so the risk is low for the demo and higher for any future pasted or non-federal source.

## 3. Environments

| | Local | Dev | Production (demo) |
|---|---|---|---|
| Purpose | Tests, UI work | Integration and rehearsal, real model at low volume | Dec 2 to 6 demo and testers |
| Engine | uvicorn, SQLite file or `:memory:` | Render service, branch deploy | Render service, `main` or release tag |
| Database | SQLite or throwaway Postgres | Neon branch `dev` | Neon branch `main` |
| Model | `mock` | Own key, own spending cap | Own key, own spending cap |
| Admin token | any | own | own, never reused |
| Pages | served by the engine | GitHub Pages preview or engine | GitHub Pages `live:false` for the public sample, engine address for live runs |

Status: the separation above is **Proposed**; the hosting accounts are **Open** (PRD O2, needs the project owner). Rules: dev and production never share a database, model key, spending cap or admin token; scripts that write runs (`bench_judging.py`) are run only against local or dev databases.

## 4. Decision records

### DR-1 Reversing "no stored opportunity index" (**Decided** for the demo; wording merged)
Context: PRD D4 and hard rule 1 said no opportunity database; live pulls were slow and the 72 s full ingest showed a stored copy is cheap. The customer approved storing the Grants.gov corpus for the demo.
Decision: store the sponsor's public records and cleaned text (`opportunities`), with retrieval times, and stamp each result with the retrieval time. Researcher profiles and judgments are never stored in these tables; the profile exists only inside that run's log record.
Consequences: the PRD wording and the `db.py` docstring now record the reversal (both merged). `docs/SIGNAL_BOUNDARIES.md` never mentioned an opportunity index and needed no change. The stored copy goes stale: it is refreshed by `scripts/ingest.py` or the admin button, and runs show "retrieved at". Retention (90 days) applies to the run log, not to the opportunity copy; say so on About if the owner wants it stated (**Open**).

### DR-2 Parallel judging and model effort (**Decided** and merged for parallel judging; effort **Open**)
Decision (merged): judge shortlisted opportunities in a bounded thread pool (`judge_concurrency`, default 8, hard cap 16); a process-wide cap on simultaneous model calls (`FORGE_MODEL_MAX_CONCURRENT`, default 16); an overall judging deadline (`judge_deadline_s`, default 90) after which no new paid call starts; only the main thread writes to the database, in ranked order; the SDK retries 429 and overload with backoff. A run in which nothing could be rated because of the model (calls failed or every answer unreadable) is failed with HTTP 502, not shown as an empty result. The output cap is 3,000 tokens (`FORGE_MAX_OUTPUT_TOKENS`); 1,500 had cut about 1 in 25 answers mid-JSON.
Evidence (engineer's live measurements, single samples, in `backend/README.md`): 25 judgments at default effort took 43.5 s on 8 workers and 21.8 s on 16 workers with the new cap (25 of 25 judged); sequential would be about 230 s. Under 30 s holds only at about 16 workers, which is also the global cap, so a second simultaneous run queues and takes longer. No 30 s promise belongs in copy or slides.
Open: effort low versus default has no accuracy evidence (the gold set has blank labels); the production global cap should come from the key's rate limits and a rehearsal with two simultaneous runs; `max_judgments` 25 versus about 15 is a product choice for the owner. Production runs ONE server worker because every cap, limiter and cache is per process.

### DR-3 Retrieval (**Decided** and merged: BM25; embeddings **Open, deferred**)
Merged: BM25 over title (weighted 3x) and text against the research areas only; records sharing no term with them are not sent to the model and are counted (`no_term_overlap`); two-letter capitals such as AI and ML count; the detail cap is lifted when reading the stored copy, with stored details read in chunks of 200 ids. Evidence: `scripts/retrieval_check.py` on a frozen snapshot of 787 records, mean recall@10 0.26 to 0.75 and MRR 0.51 to 1.00 on 6 queries labelled by one AI rater. This is weak evidence (few queries, unreviewed labels biased toward keywords, parameters untuned but not independent of the labeller's skim) and is not an accuracy figure; a person must review and extend the labels before any figure is quoted outside the repository. Synonym-only matches are missed by design. The Results page must show the no-overlap count and reason (UX, pending). Embeddings stay deferred: they add a provider, cost and a second index and cannot be evaluated until reviewed labels exist. The engineer's own short records are in `docs/BACKEND_DECISIONS.md`.

### DR-4 PI lookup (**Decided** for the API, merged; the page flow **Open**)
Merged: `POST /api/pi/search` (the name travels in the body) and `GET /api/pi/{id}/expertise`, server-side calls to OpenAlex (allowed by the owner on 24 Nov) with a generic client name, no key and no email; answers cached in memory only; per-visitor and daily limits; a written error table; the call log keeps only the name's length and a keyed HMAC of the author id. Design rule that the pages must follow: the person picks a candidate, sees proposed terms with the works that produced them, edits and confirms them before any run; terms are used for that run only and not stored. The page must also say that the typed name is sent to OpenAlex. Disambiguation stays a human choice (similar names are shown separately, never merged). The manual research-areas box remains the fallback. No page uses these endpoints yet (**Open**, UX).

### DR-5 Schema versioning (**Decided** and merged)
Numbered migrations in `app/migrations.py`, each applied once in its own transaction, recorded in `schema_migrations`, with a Postgres advisory lock so two starting servers cannot race. Version 1 adopts the existing schema; version 2 adds `cost_usd`. Verified by the architect: a failing migration rolls back completely on SQLite and Postgres; four simultaneous starts on an empty Postgres succeed. Rules: migrations are additive while an old and a new server can overlap during a deploy; on Neon use the direct (non-pooled) connection string because session advisory locks do not work through the pooler; pass the address through `FORGE_DB`, never `--db`. `scripts/migrate.py` reports the version without printing the address; `scripts/db_smoke.py` is for a dev database only.

### DR-6 Hosting (**Proposed**, accounts **Open**)
Plan: Render for the engine, Neon for Postgres, GitHub Pages for the static sample pages. Requirements for the engine behind Render's proxy: start uvicorn with forwarded headers trusted for the platform proxy, or every visitor will appear to come from one address (see review notes: rate limits and run ownership use the client address). Set `FORGE_SALT`, `ADMIN_TOKEN`, the model key and `FORGE_CORS_ORIGINS` as service environment variables. Confirm the platform's request timeout against the longest run. Free-tier cold starts and Neon scale-to-zero add seconds to the first request; the code already reconnects once on a dropped connection.
Governance: SMU's expectations for a hosted app (accessibility, SSO, data protection, ownership, maintenance) apply; run the `app-hosting-self-review` skill with OIT before wider use, and ask OIT whether this duplicates an existing research-administration system.

### DR-7 Run is one synchronous request (**Open**)
A run holds a request open for tens of seconds. It is the smallest design that works. The alternative (start a run, poll its status) gives real progress, survives proxy timeouts and lets a browser stop waiting without losing the result, at the cost of a background worker and a status table. Recommendation: keep synchronous for Dec 2; revisit only if the platform timeout or measured run times require it.

## 5. Security and data controls (current state)
| Control | State |
|---|---|
| Model key | Server environment only; never returned or logged (tests cover the exception text path). |
| Admin | Single shared token, constant-time compare, disabled when unset, no rate limit on failed attempts (**gap**). |
| Public limits | Hourly per visitor, daily cap on runs. Cost bound is daily cap x `max_judgments` model calls. |
| Input size | `input_text` 4000, `question` 1000, profile lists and item lengths capped, pasted sources 3 x 20,000 characters, public POST bodies limited (default 400,000 bytes, Content-Length required). |
| Client address | Socket peer unless `FORGE_TRUSTED_PROXY_HOPS=N`; then the Nth entry from the right of X-Forwarded-For. A value that is too large makes the address client-controlled, so the dev rehearsal must prove a forged prefix is ignored (`/api/admin/whoami`). The Render value is **Open**. |
| CORS | Off unless `FORGE_CORS_ORIGINS` is set. |
| Exports | Formula-injection protection in CSV and spreadsheet output. |
| Run log | Inputs, citations (short quotes), counters; source text is hashed, not stored. 90 days then archived (archived rows are kept; deletion policy **Open**). |
| Data classes | Public and Private only; notice on the pages; no Restricted data. |

## 6. Operability: status and what remains before Dec 2
Done and merged: client address handling (needs the rehearsal check above), schema migrations, cost per run (`cost_usd`, null unless both prices are set, an estimate from reported usage), all-calls-failed runs fail visibly, a daily lookup and run cap.
Remaining: (1) set `FORGE_SALT` in every hosted environment (unset it defaults to a public string; a startup warning is requested); (2) enter the model prices in settings so cost is reported; (3) backups: Neon provides point-in-time restore on paid plans, confirm what the chosen plan gives; a CSV export of runs exists and the opportunity copy can be re-ingested in about 72 s; (4) observability: no structured logs and no alert when runs fail; (5) a dev rehearsal on the hosted stack (proxy hops, two simultaneous runs, Neon direct connection, `db_smoke.py`); (6) a screen-reader pass.

## 7. Accessibility
Target WCAG 2.1 AA (SMU) and 2.2 AA (PRD). The UX session's implementation adds labelled fields, `aria-invalid` and described-by errors, `role="status"` progress, scrollable table regions with labels, and a reduced-motion rule. None of it has been tested with a screen reader or by the architect session; the UX plan states the same limit. An automated scan plus a keyboard pass is still required before Dec 2.

## 8. What the model never decides
Tier, word, dates, days to deadline, internal deadline, groupings, the 45-day action list, status flags. The model proposes factor values and quotes; a person decides everything outward-facing.

## 9. What was and was not checked (original draft; later reviews are in the approval messages)
Checked: read `pipeline.py`, `adapters/`, `main.py`, `db.py`, `store.py`, `app.js` diff, `config.js`, both UX documents (skimmed for claims). Ran 133 tests on in-memory SQLite (pass). Ran the same command with `FORGE_TEST_PG_URL` against a throwaway Postgres 16 cluster (133 pass), then found the Postgres run did not cover `test_store.py` or `test_parallel_judging.py` because `conftest.py` patches only `app.main.Database` while those files import `Database` directly. I ran the parallel-judging tests against Postgres by hand (the two order and failure tests pass; the timing and token tests were not re-run there).
Not checked: any live model call, any real Grants.gov call, a deployed environment, screen readers, the Render and Neon behaviour, the behaviour of the Anthropic SDK retry settings under real rate limits beyond what the engineer reported.

## 10. Owner decisions needed (through the project manager)
1. Hosting accounts for Render and Neon, and the live address (PRD O2). Migrations (DR-5) gate any hosted database.
2. The model key and its spending cap, separate for dev and production (PRD O10).
3. A human review of the retrieval labels (currently one AI rater, 6 queries) before any retrieval figure is quoted outside the repository.
4. The PRD wording change recording the customer-approved opportunity store (DR-1); the project manager approved the text and is asking the owner, nothing is applied until then.
5. The OIT self-review (`app-hosting-self-review`) and the question whether SIGNAL duplicates an existing research-administration system.
6. Agreement to the branch flow in `docs/BRANCH_FLOW.md`, before the project manager creates `integration`.
