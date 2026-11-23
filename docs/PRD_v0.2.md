# FORGE SIGNAL: Product Requirements Document v0.2

Status: DRAFT for customer review (Shazia Yaqub). Date: 23 Nov 2026.
Governing scope: **Forge Signal – Business Case (Nov 23, 2026)**. This PRD **supersedes PRD v0.1** (Nov 21, discovery-only). Anything not in the Business Case is in section 11 (Future builds).
Context: ITOM 6216 capstone. Nothing is built yet; `public/signal/` is a static mock only.

---

## 1. What we are building
A public, no-login web app that acts as a working agent for SMU research development. Given a PI, a project description, a keyword search, or an opportunity plus a unit, it:

1. **Matches** funding opportunities and researchers, using live pulls from the web.
2. **Rates fit** (High / Medium / Low) and **eligibility** (Eligible / Not eligible / Needs verification), each with a citation, and flags archived or replaced postings.
3. Builds a **calendar** (sponsor deadline plus computed internal deadline) with `.xlsx` and `.ics` export.
4. Drafts an **alert email** that a person must review and confirm before it can be "sent".

An **admin dashboard** (back end) sets defaults and shows the run log. A **run log** is the only database.

## 2. Decisions that govern this PRD
| # | Decision | Source |
|---|---|---|
| D1 | The Business Case is the single source of truth; PRD v0.1 is superseded. | Customer, Nov 23 |
| D2 | One UI only: the "Signal" page set from the final wireframe (Home, Match, Results, Calendar, Review, About, Visual language, Settings). The Workbench, Prompt Builder and old Explorer are removed from the product. | Customer |
| D3 | The Explorer/Match page is a real working agent, not a preview. | Customer |
| D4 | No Grants.gov sync. Opportunities and faculty evidence are **pulled live** at run time. No opportunity database, no faculty index. | Customer |
| D5 | **One database: the run log** (inputs, outputs, citation-check results, outcomes, chatbot entries). | Customer |
| D6 | Citations are required now. Every claim carries a quote and source; a validator rejects unsupported quotes. | Customer |
| D7 | Email is a **dummy** for now (log-only or a test mailbox). Real SMU sending is deferred. | Customer |
| D8 | Model: our own agent behind the adapter. The demo key is personally funded (demo only); the admin console must be able to switch to an OIT-approved platform when OIT requires. Provider not final (O1). | Customer |
| D9 | **Default scope** (Dedman College / SMU / organization / Texas, etc.) is set in the admin dashboard. | Customer |
| D10 | Schedule: working demo **Dec 2**; show to people **Dec 2 to 4**; refine **Dec 4 to 6**; demo and final submission **Dec 6**. | Customer |

## 3. Users
- **Visitor (public, no login):** grants staff, faculty, testers. Runs matches, views results and the calendar, reviews and "sends" an alert.
- **Administrator (Shazia):** logs in to the dashboard. Sets defaults, scope, model connection, caps and retention; reads and exports the run log.

No other roles in v0.2.

## 4. Hard rules (non-negotiable)
1. **No stored faculty index and no stored opportunity index.** Evidence is supplied or fetched live and kept only inside that run's log record.
2. **Every claim has a citation** (source URL, exact quote, retrieval date). The validator rejects any quote not found in its source text. Missing evidence displays exactly: "No explicit support found in the provided sources."
3. **Eligibility is never guessed.** If sources are silent it is "Needs verification".
4. **A person reviews before any email.** No automatic sending. The reviewer ticks a confirmation; the recipient is entered per send and logged.
5. **Keys and passwords live only on the server.** Never shown on the page, returned by the API, or written to logs. No "bring your own key" option.
6. **Dates, deadlines, the calendar, and exports are plain code, not the model.** The model sits behind an adapter so it can be swapped.
7. **Fit is a word, never a percentage.** Wording never says "non-competitive" about a named person.
8. **Public and Private data only.** Inputs must not contain Restricted data (student, health, financial records). The page says so, and the run-log notice repeats it.
9. **Per-visitor rate limits, a daily cap, and a saved-run fallback** keep the public link stable. Settings and the log are admin-only.

## 5. Functional requirements

### 5.1 Match (the working agent)
| ID | Requirement |
|---|---|
| FR-1 | One prompt box accepts: a PI name; a project description (key terms extracted); a keyword query; or "opportunity + unit". |
| FR-2 | **PI name:** fetch public publication records live (OpenAlex first; ORCID/Crossref later) and extract expertise terms. Show the sources used. |
| FR-3 | **Project description / keywords:** extract key terms, then search live for opportunities. |
| FR-4 | **Opportunity + unit (e.g., Biology):** read the unit's public faculty listing live (cap: 25 faculty per run, admin-editable) and rank who fits. |
| FR-5 | **Live opportunity pull:** query the Grants.gov public API at run time (not a sync). A curated list of state and foundation pages may be read live (see O3). Nothing is stored except in the run log. |
| FR-6 | Honor the active **scope** and **settings**: unit/institution, funder types (federal / state / foundation / any), deadline window, internal lead time, and minimum fit. Defaults come from the admin dashboard; the visitor may change them for the run. |
| FR-7 | If no researcher profile is available, matched opportunities still go onto the calendar with Fit shown as "Not assessed". |

### 5.2 Fit and eligibility
| ID | Requirement |
|---|---|
| FR-8 | Rate alignment **High / Medium / Low** (from the fit tiers in section 5.7) and eligibility **Eligible / Not eligible / Needs verification**, each with citation(s). |
| FR-9 | Flag **archived or replaced** postings (e.g., an NSF solicitation superseded by a newer one) by plain-code status checks plus the source's own status text, and show the replacement link if found. |
| FR-10 | The citation validator checks every quote against the fetched source text. Failures display "No explicit support found in the provided sources." and are counted in the run log. |
| FR-11 | Model output must conform to a fixed JSON schema. Invalid output is retried once, then shown as a failed step (never silently dropped). |

### 5.3 Calendar and export
| ID | Requirement |
|---|---|
| FR-12 | Every match appears on a calendar with **sponsor deadline** and **internal deadline** (sponsor deadline minus lead time). Defaults: next **3 months**; lead time **14 days**; both admin-editable and changeable per run. A search profile may set a longer horizon (e.g., rolling 12 months, per section 5.7). |
| FR-13 | Export the calendar to **.xlsx** and **.ics**. Deadlines missing from the source stay "Not specified" (never zero or invented). All-day events; the sponsor sets time zone. |
| FR-14 | All date arithmetic is deterministic code with unit tests, including the 14-day default and the holiday period. |

### 5.4 Review and alert
| ID | Requirement |
|---|---|
| FR-15 | Draft an informational alert (marked DRAFT) from the selected matches. The reviewer can edit it. |
| FR-16 | Sending requires a ticked confirmation and a recipient entered by the visitor. **For now the sender is a dummy:** the email is written to the run log (and optionally delivered to a test mailbox set in Settings). Real delivery is behind the same interface. |
| FR-17 | The review screen shows who is and is not surfaced (all High, Medium and unverified results), so a person can check coverage before sending. |

### 5.5 Admin dashboard (back end, login required)
| ID | Requirement |
|---|---|
| FR-18 | **Scope defaults:** choose the default scope level (Dedman College / SMU / an organization / state, e.g. Texas), the units in scope, and funder types. Stored as admin settings and applied to every new run. |
| FR-19 | **Model connection and switch:** the admin selects the active model provider and enters each provider's API key (stored server-side, never displayed after saving). The demo uses a personally funded key; the admin can **switch the active provider to an OIT-approved platform at any time**, effective on the next run with no redeploy. Each run logs the provider and model used, and every switch is written to an admin audit entry (who, when, from, to). Matching, validation and calendar logic do not change. |
| FR-20 | **Limits:** per-visitor rate limit, daily cap, faculty-per-run cap (25), calendar window (3 months), lead time (14 days), minimum fit. |
| FR-21 | **Email:** dummy mode on/off, test mailbox address, sender label. |
| FR-22 | **Run log viewer:** search, filter by date/user input/outcome, open one run to see inputs, sources, citations, validator results, calendar and email draft; export CSV. |
| FR-23 | **Retention:** 90 days, then archive and start a new log. Visitor notice: "Runs, inputs and calendars are logged for the pilot report, kept for 90 days, then archived. Only the administrator can see them." |
| FR-24 | The admin can edit and save run-log **annotations** (e.g., a reviewer marks a High match as agreed/disagreed) to build the gold-set accuracy figures. |

### 5.6 Public pages
Home, Match (with Results, Calendar and Review views), About, and a Settings page that is admin-only. All from the final wireframe/design canvas. About states plainly what the agent does, what it does not do, and the AI/human boundaries (reuse `docs/SIGNAL_BOUNDARIES.md`, updated).

### 5.7 Search profile and fit rubric (customer methodology)
The customer's funding-search method is a **template**, not hard-coded for one person. Each run uses a **search profile** (supplied by the visitor, or a saved admin default). A de-identified worked example is in `docs/examples/search_profile_example.md`.

| ID | Requirement |
|---|---|
| FR-25 | **Search profile fields:** investigator (name, institution); career stage (and an exclusion rule, e.g., skip early-career-only programs); research lanes (terms the science is genuinely about); positioning rules (e.g., "cancer only with a real mechanism bridge"; "defense only where sensing/biophysics is central"); search horizon (rolling N months from today); minimum award (none by default); generic calls allowed (yes/no); sponsor types to search (federal, defense, state, foundation, international, industry); trainee search on/off. |
| FR-26 | **Never infer a new research identity from a solicitation keyword.** Fit is judged against the profile's lanes only. The reason must name the concrete bridge to the investigator's established science, or state the collaboration/repositioning required. |
| FR-27 | **Fit rubric (four tiers plus exclude).** The agent assigns a tier; the page shows the High/Medium/Low word and the tier label. Never a percentage. |
| FR-28 | **Source hierarchy:** (1) official sponsor/solicitation page, (2) Grants.gov/Simpler.Grants.gov/SAM.gov, (3) institutional guidance, (4) ProposalCentral/foundation portals, (5) Halo/corporate portals, (6) aggregators. A deadline, eligibility or status claim must cite level 1 or 2. A claim supported only by levels 3 to 6 shows **"Unverified: discovery source only"** and stays "Needs verification". |
| FR-29 | **Fixed vs rolling vs watch:** each result is labelled Open / Upcoming / Rolling / Invitation only / Watch / Closed. Rolling programs show "rolling/anytime" (no invented deadline) and the prerequisite step (program-officer contact, white paper). An expected annual cycle is **WATCH: date not yet announced**, never shown as a deadline. |
| FR-30 | **Calendar table columns:** Opportunity, Sponsor, Type, NOFO/Call ID (own column), Fit, Relevance, Next fixed date, Application period/milestones, Other dates in window, Status, Amount/scale, Eligibility/conditions, Recommended next action, Official source, Date verified. Fixed, rolling and watch items are shown in separate groups, and the export keeps the same columns. |
| FR-31 | **Closing summary:** top 5 opportunities for the window, anything needing action within 45 days (computed by code, not the model), and a watch list. The trainee table (graduate students and postdocs) is a profile option and is **future** unless the customer moves it into the pilot (O12). |

**Fit tiers**
| Tier | Definition | Page word | Treatment |
|---|---|---|---|
| Direct fit | Close match to established research; little or no repositioning; investigator can lead. | **High** | Pursue. |
| Very strong fit | Strong alignment; may need sponsor-specific framing, a collaborator or interdisciplinary positioning. | **High** | Pursue after a targeted check. |
| Strong fit | Relevant, but depends on a specific topic, partner or application bridge. | **Medium** | Keep active with the stated condition. |
| Conditional fit | Scientifically adjacent; only with a clear solicitation, topic or collaborator bridge. | **Low** | Secondary or watch. |
| Low priority | Keyword overlap only; science would be stretched. | (excluded) | Not shown in results; kept in the run log only. |

## 6. Data: the run log (the only database)
One record per run (plus child rows):

| Field | Notes |
|---|---|
| `run_id`, `created_at`, `visitor_hash` | Hashed visitor ID for rate limiting; no personal data. |
| `input_type`, `input_text` | PI name / project text / keywords / opportunity+unit. |
| `scope_snapshot`, `settings_snapshot` | Settings in force for the run. |
| `sources[]` | URL, retrieval timestamp, status code, text hash. Source text is stored only if needed to re-verify citations; capped and purged on retention. |
| `matches[]` | Opportunity (title, number, status, replaced-by), researcher, fit, eligibility, deadlines. |
| `citations[]` | Quote, source, `validated` true/false, failure reason. |
| `calendar` and `export_events[]` | Generated items; downloads counted. |
| `email_events[]` | Draft text, recipient entered, confirmation ticked, mode (dummy/test), timestamp. |
| `chat_entries[]` | If the site chatbot is used, prompts and replies are logged with the same notice. |
| `model`, `latency_ms`, `tokens`, `errors` | For cost and speed measures. |
| `annotations[]` | Admin review notes for the gold set. |

Admin settings (scope, adapter, limits, email mode) are held in a small settings table in the same database. **No opportunity, faculty or profile tables.**

## 7. Architecture (recommendation, not mandate)
- **Front end:** static pages built from the final wireframe, wired to the API. Existing brand tokens (Trust Blue #244B70, Forge Coral #E98262, Sora/Inter).
- **Back end:** Python FastAPI. Modules: `adapters/model` (chatbot/LLM behind one interface), `sources` (Grants.gov, OpenAlex, faculty-page reader, curated state/foundation), `validator` (quote-in-source), `calendar` (plain code), `exports` (.xlsx/.ics), `mailer` (dummy now), `admin`, `limits`.
- **Database:** a managed Postgres (or SQLite for local), holding only the run log and settings.
- **Secrets:** environment variables; never committed.
- **Pipeline per run:** parse input → live fetch → retrieve relevant passages → model returns schema-valid JSON with quotes → validator checks quotes → plain-code dates/status/calendar → persist run → render.

## 8. Non-functional requirements
- **Accessibility:** design to WCAG 2.2 AA (covers SMU's 2.1 AA). Keyboard operable; status never by colour alone; visible focus; semantic structure.
- **Performance:** first result within 30 seconds for a typical run (Business Case target); progress shown for long runs.
- **Reliability:** if a source is down, say so and show the saved-run fallback instead of failing silently.
- **Security:** server-side calls only; input validation; admin auth; rate limiting; no raw secrets in logs; HTTPS.
- **Privacy:** no accounts for visitors; the log notice is always visible near the run button; no Restricted data.
- **Fair use:** respect Grants.gov and each website's terms; identify the client; cache politely within a run; honor robots rules for faculty pages (confirm permission, O4).

## 9. Acceptance and measures
| Measure | Target |
|---|---|
| Time to triage one announcement | Half the manual baseline (timed on 3 real announcements); first result in 30 s. |
| Citations supported by source | 100%; failures shown as "No explicit support found". |
| Eligibility guessed when sources are silent | 0 (always "Needs verification"). |
| Archived/replaced postings caught | All known cases, including the NSF replacement. |
| High matches a reviewer agrees with | Rate reported; aim for a clear majority (gold set of 8 to 10 cases). |
| Tester usefulness, trust, clarity | Ratings and top issues reported; top issues fixed. |
| North Star: qualified opportunities routed per month | Counted from the run log against a baseline counted first. |

Test plan: unit tests (dates, calendar, validator, schema, status mapping); integration tests with mocked Grants.gov/OpenAlex/faculty pages; API tests; end-to-end (enter input, view results, export, review, dummy send, check the log); signed-out test of the public link; accessibility scan and keyboard pass.

## 10. Schedule (working back from Dec 6)
| Dates | Milestone |
|---|---|
| Nov 24 to 25 | Confirm wireframe export, model/chatbot platform and API key, hosting account (O1, O2, O5). Backend skeleton, adapter, settings, run-log schema. |
| Nov 26 to 28 | Live pulls (Grants.gov, OpenAlex), validator, fit/eligibility schema, calendar + exports (with tests). |
| Nov 29 to Dec 1 | Front end from wireframe wired to API; admin dashboard; dummy mailer; rate limits. |
| **Dec 2** | **Working demo.** |
| Dec 2 to 4 | Show to testers; collect ratings; gold-set and baseline timing. |
| Dec 4 to 6 | Refine, fix top issues, signed-out test. |
| **Dec 6** | **Demo and final submission.** |

## 11. Future builds (not in v0.2)
Master opportunity database; per-researcher grant funnel (identified, alerted, interested, LOI, submitted); weekly digest; broader state/foundation coverage and other colleges' directories; optional stored faculty index; real SMU email sending; cross-college collaborator-pair team view (customer to confirm, O6); NSF coverage validation as a recurring check; SSO for admins; move to the next approved AI platform.

Removed from the product: the Workbench, Prompt Builder, browser-only profile registry, localStorage shortlist, and the Explorer's fictional records.

## 12. Risks
| Risk | Mitigation |
|---|---|
| An existing chatbot platform may not return strict structured output or exact quotes. | Test early (O1); validator and schema are mandatory; fall back to a direct LLM API behind the same adapter. |
| Live pulls are slow or blocked; faculty pages vary by department. | Caps, timeouts, saved-run fallback; start with 2 to 3 pilot units. |
| Public link with an API key can be abused. | Rate limits, daily cap, admin-set budgets, no key on the page. |
| Run log holds names and queries. | Notice, 90-day retention, admin-only access, no Restricted data. |
| Nine days to a working demo. | Thin vertical slices; PI-name path first; cut FR-4 or FR-24 before cutting citations. |
| Governance of a public hosted app (hosting, ownership, data protection, SSO, WCAG). | Start the OIT review now using the `app-hosting-self-review` skill; check overlap with existing SMU research-administration systems. |

## 13. Open items (customer to answer; not guessed)
- **O1** Which existing chatbot becomes the model adapter, and can it return structured JSON with quotes? Provide its API access.
- **O2** Hosting account for the deploy, and the live URL for the Business Case and slides.
- **O3** Which curated state and foundation sources are in the pilot (if none, federal only).
- **O4** Written confirmation that public faculty pages may be read live. Which units are in the pilot?
- **O5** Final wireframe export (all pages) and the design canvas file.
- **O6** Is the cross-college collaborator view in the pilot or future? (Default here: future.)
- **O7** Does the `.xlsx` attach to the alert email, or is it a download only? (Default here: download only.)
- **O8** NSF validation: kept as a manual pilot-report check, not a product feature. Confirm.
- **O9** Admin sign-in method for the pilot (simple password for now; SSO later).
- **O10** Real API key and daily cap values.
- **O11** Confirm the tier-to-word mapping (Direct and Very strong = High; Strong = Medium; Conditional = Low; below that excluded), or keep the 5-point numbers on the page instead of words. The Business Case says "High, Medium or Low".
- **O12** Is the trainee (graduate student and postdoc) search in the pilot? Default here: future.
- **O13** The 12-month horizon in the example versus the Business Case default of 3 months: keep 3 months as the app default with the profile able to extend it?
- **O14** Sources such as ProposalCentral, Halo, GrantWatch and CPRIT may have no public API or may restrict automated reading. Which are in the pilot? Default here: Grants.gov plus official sponsor pages read live; the rest as discovery links.
