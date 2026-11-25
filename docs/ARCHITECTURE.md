# FORGE SIGNAL: Architecture

Status: DRAFT by the architect session, 25 Nov 2026. Not committed until the project manager approves.
Basis: code read at commit db17872 on `claude/practical-franklin-ze9hk2`, `docs/PRD_v0.2.md`, `docs/SIGNAL_BOUNDARIES.md`, `backend/README.md`. What was run is listed in section 9; everything else is from reading code.

Decision status words: **Decided** (made by the customer or already built and accepted), **Proposed** (architect recommends, awaiting approval), **Open** (needs the project owner or more evidence).

## 1. Components

```
 Browser (static pages)            FastAPI engine (backend/app)                 Outside services
 public/signal/*.html, app.js ---> /api/runs, /api/runs/{id}/calendar... ----> Grants.gov public API (list + detail)
   config.js: live true/false      /api/admin/*  (X-Admin-Token)               Claude API (model adapter)
   sample mode = mock-data.js      pipeline.py  -> adapters/ -> validator.py   OpenAlex (PI lookup; not built,
   run kept in sessionStorage      rubric.py, calendar.py, exports.py            host blocked in the build sandbox)
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

### DR-1 Reversing "no stored opportunity index" (**Decided** for the demo; documentation **Proposed**)
Context: PRD D4 and hard rule 1 said no opportunity database; live pulls were slow and the 72 s full ingest showed a stored copy is cheap. The customer approved storing the Grants.gov corpus for the demo.
Decision: store the sponsor's public records and cleaned text (`opportunities`), with retrieval times, and stamp each result with the retrieval time. Researcher profiles and judgments are never stored in these tables; the profile exists only inside that run's log record.
Consequences: the PRD, `docs/SIGNAL_BOUNDARIES.md` and the `db.py` docstring still say "no opportunity tables" and must be updated, or a reader will believe the code breaks a hard rule. The stored copy goes stale: nightly or manual ingest is needed and runs must keep showing "retrieved at". Retention (90 days) applies to the run log, not to the opportunity copy; say so in the notice if that is intended.

### DR-2 Parallel judging and model effort (**Decided** for parallel judging; effort **Proposed**)
Decision: judge shortlisted opportunities in a bounded thread pool (`judge_concurrency`, default 8, hard cap 16); only the main thread writes to the database, in ranked order. The SDK retries 429 and overload with backoff.
Evidence (engineer's live benchmark, single samples, recorded in `backend/README.md`): 25 judgments at effort low took 25.7 s on 8 workers; sequential would be about 230 s. The 30 s target is met only at effort low.
Open points: effort low versus default has no accuracy evidence (the gold set has blank labels; the 10-item agreement is one sample); there is no global cap on concurrent model calls across simultaneous runs; there is no overall time budget for the judging step. See review conditions.

### DR-3 Retrieval (word overlap **Decided** as the current stopgap; BM25 **Proposed**; embeddings **Open, deferred**)
Before: word-overlap ranking chose which 25 of up to 250 detailed records are paid for; quality was unmeasured. Proposed by the backend engineer (commit 6c5cff9, architect APPROVED WITH CONDITIONS, project manager approved on scope; not yet integrated): BM25 over title and text against the research areas, records sharing no term are not sent to the model, the detail cap is lifted when reading the stored copy. A labelled check without the model (`scripts/retrieval_check.py`) reports mean recall@10 0.26 to 0.75 and MRR 0.51 to 1.00 on 6 queries labelled by one AI rater; this is weak evidence (few queries, unreviewed labels biased toward keywords) and is not an accuracy figure. Conditions: keep two-letter terms such as AI and ML, batch the stored-detail reads before lifting the cap, state whether parameters were tuned on the same labels, show the no-overlap count and reason on Results. Embeddings stay deferred: they add a provider, cost and a second index, and cannot be evaluated until reviewed labels exist. The engineer's own short records are in `docs/BACKEND_DECISIONS.md` (their D1 and D2); this file is the canonical structure.

### DR-4 PI lookup (**Open**)
PRD FR-2 and FR-41 want publication-based research areas from OpenAlex. Not built; `api.openalex.org` is blocked by the build sandbox network policy (PRD O20). Proposed design if approved: server-side fetch of works by name, shown to the person as proposed research areas with the titles as evidence, confirmed or edited by a person before any run, then used for that run only. Name-to-author disambiguation is an open problem; the person must choose among candidates. The manual research-areas box stays as the fallback and is what the demo can rely on.

### DR-5 Schema versioning (**Proposed**, needed before production)
Today `db.py` runs `CREATE TABLE IF NOT EXISTS` at start. That creates new tables but never alters existing ones, so any column added after the first production start will be missing in production while tests (fresh databases) pass. Proposal: a `schema_version` table and an ordered list of numbered migrations applied at start inside a transaction, tested on SQLite and Postgres from the previous version's schema. Rubric versions already exist (content hash) and are separate from this.

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
| Input size | `input_text` 4000, profile lists capped; **`sources`, `question`, profile item lengths and request body size are unbounded (gap)**. |
| CORS | Off unless `FORGE_CORS_ORIGINS` is set. |
| Exports | Formula-injection protection in CSV and spreadsheet output. |
| Run log | Inputs, citations (short quotes), counters; source text is hashed, not stored. 90 days then archived (archived rows are kept; deletion policy **Open**). |
| Data classes | Public and Private only; notice on the pages; no Restricted data. |

## 6. Operability gaps to close before Dec 2
1. Client address behind a proxy (DR-6).
2. Schema migrations (DR-5).
3. Cost per run: prices are 0 in settings, so no cost is reported.
4. Backups and export: Neon provides point-in-time restore on paid plans; confirm what the chosen plan gives. A CSV export of runs exists; there is no export of the opportunity copy (it can be re-ingested in about 72 s).
5. Observability: no structured logs, no alert when every model call in a run fails.
6. Postgres test coverage: see section 9.

## 7. Accessibility
Target WCAG 2.1 AA (SMU) and 2.2 AA (PRD). The UX session's implementation adds labelled fields, `aria-invalid` and described-by errors, `role="status"` progress, scrollable table regions with labels, and a reduced-motion rule. None of it has been tested with a screen reader or by the architect session; the UX plan states the same limit. An automated scan plus a keyboard pass is still required before Dec 2.

## 8. What the model never decides
Tier, word, dates, days to deadline, internal deadline, groupings, the 45-day action list, status flags. The model proposes factor values and quotes; a person decides everything outward-facing.

## 9. What was and was not checked
Checked: read `pipeline.py`, `adapters/`, `main.py`, `db.py`, `store.py`, `app.js` diff, `config.js`, both UX documents (skimmed for claims). Ran 133 tests on in-memory SQLite (pass). Ran the same command with `FORGE_TEST_PG_URL` against a throwaway Postgres 16 cluster (133 pass), then found the Postgres run does not cover `test_store.py` or `test_parallel_judging.py`, because `conftest.py` patches only `app.main.Database` while those files import `Database` directly. I ran the parallel-judging tests against Postgres by hand (the two order and failure tests pass; the timing and token tests were not re-run there).
Not checked: any live model call, any real Grants.gov call, a deployed environment, screen readers, the Render and Neon behaviour, the behaviour of the Anthropic SDK retry settings under real rate limits beyond what the engineer reported.
