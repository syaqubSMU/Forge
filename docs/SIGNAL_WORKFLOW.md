# SIGNAL workflow: opportunity-to-PI matching (Dedman College)

Status: design draft v0.1. Owner: Research Development (Dedman). Human decision at every outward-facing step.

## 1. Two entry points, one shared core

| | Path A: PI-initiated | Path B: Opportunity-initiated |
|---|---|---|
| Trigger | A PI asks "what's coming up for me?" | A new NOFO/RFA/solicitation appears |
| Input | PI name (or lab/dept) + optional topic, career stage, preferred sponsors, timing | NOFO link/PDF/text |
| Core question | Which open or forecasted opportunities fit this person? | Which departments and faculty fit this opportunity? |
| Output | Ranked opportunity list for one PI | Match table + outreach summary + draft alert |

Both paths run the same three shared components:

1. **Verified Profile Registry** (who people are, from public SMU sources).
2. **Opportunity Fact Sheet** (what the sponsor actually says, with citations).
3. **Match + Risk engine** (rubric-based, evidence-cited, never inferred).

Path A = one profile against many fact sheets. Path B = one fact sheet against many profiles.

## 2. The gate: "scope of the PI/department is verified"

Nothing is matched against an unverified profile. A profile record holds:

- Name, department, rank/title, profile URL, **date retrieved**
- Research areas **quoted** from the Dedman page (verbatim snippets, not paraphrase)
- Centers/labs named on the page
- Optional public corroboration (Google Scholar, ORCID): stored as a separate, labeled evidence tier
- Status: `Verified` (RD staff confirmed) / `Unverified` (scraped, not reviewed) / `Stale` (older than 6 months or page changed)
- PI-confirmed fields (optional): current interests, sponsor preferences, limited-submission interest

Only `Verified` profiles can be rated High. `Unverified` profiles can appear only as "possible, needs verification."

## 3. Workflow stages

### Path B: opportunity arrives

| # | Stage | Who/what | Output | Human gate |
|---|---|---|---|---|
| B1 | Intake | RD staff pastes link/PDF/text | Raw source saved with retrieval date | Confirm it is the final NOFO, not a notice of intent or a superseded version |
| B2 | Extract Fact Sheet | AI, from sponsor text only | Priorities, scope, eligibility, constraints, deadlines, award size, each with a section/page citation | RD reviews against the NOFO |
| B3 | Eligibility screen | AI flags, RD decides | Institution-level (SMU eligible? limited submission? cost share?), PI-level (career stage, citizenship, effort), structure (lead vs. subaward, required partners) | RD resolves any "unclear" before outreach |
| B4 | Candidate retrieval | AI against Verified Registry | Longlist by keyword/department overlap | None (internal) |
| B5 | Evidence-based rating | AI, rubric in section 5 | Match table with quotes | RD confirms every High and Medium |
| B6 | Risk and gap summary | AI | Eligibility risks, structural limits, gaps between sponsor priorities and Dedman strengths | RD review |
| B7 | Outreach package | AI drafts | Outreach summary + alert email draft | **RD edits and sends. Nothing is sent by the system.** |
| B8 | Log | System | Opportunity, matches, who was alerted, responses, outcome | RD closes the loop |

### Path A: PI asks about upcoming opportunities

| # | Stage | Output | Human gate |
|---|---|---|---|
| A1 | Confirm profile | Show the PI's verified profile; ask them to confirm or correct interests, career stage, sponsor preferences, typical award size, and timeline | PI confirms (this also upgrades evidence quality) |
| A2 | Search sources | Query the sources in section 6 for open **and forecasted** opportunities in the PI's window | RD sets the lead time (for example 60+ days) |
| A3 | Fact Sheet + eligibility screen per hit | Same as B2/B3, abbreviated | RD verifies deadline and eligibility on the sponsor page |
| A4 | Rate and rank | High/Medium list with rationale; Low listed only if the PI asks | RD reviews |
| A5 | Response to PI | Short digest: what, why it fits, deadline, internal lead time needed, suggested next step (call, limited-submission, partner search) | RD sends |
| A6 | Optional watch | Save the profile's criteria for recurring alerts | PI opt-in |

## 4. Evidence tiers (this resolves the "don't infer" tension in the original prompt)

The original prompt says "do not infer" but also asks for a High/Medium/Low match. Matching is always some inference, so define what is allowed:

| Tier | Source | Allowed use |
|---|---|---|
| E1 | Direct quote from the NOFO or Dedman page | Can support any rating |
| E2 | Public corroboration (Scholar/ORCID titles, abstracts, past awards listed publicly) | Can support Medium; can support High only with a matching E1 |
| E3 | Model's own thematic reasoning | Must be labeled "framing needed," caps the rating at Medium |
| none | No evidence | Write exactly: "No explicit support found in the provided sources." |

## 5. Rating rubric

| Level | Requires |
|---|---|
| **High** | At least one sponsor priority matched to an E1 quote on the person's or department's page, **and** no unresolved eligibility blocker, **and** profile is Verified |
| **Medium** | Thematic overlap, or a High-quality match with an eligibility uncertainty or structural limit; would need framing or a partner |
| **Low** | Indirect or one-keyword overlap. Excluded from outreach by default |
| **Not eligible** | Hard blocker (institution, career stage, structure). Shown separately, never ranked |

Every row carries: sponsor-priority quote and citation, faculty/department quote and URL, rating, one-line rationale, risk note.

## 6. Source list (proposed)

- Sponsor: Grants.gov, SAM.gov assistance listings, NSF funding search, NIH Guide, NEH, DOE, DoD/DARPA BAAs, foundation pages as needed
- SMU: Dedman department and faculty pages, centers and institutes
- Corroboration: Google Scholar, ORCID (flag as E2)
- Internal (RD-maintained, not scraped): limited-submission list, internal deadline policy, PI-confirmed interests

Note: the original prompt restricts evidence to the NOFO and Dedman pages but also says to check Google Scholar. Pick one rule. This design keeps Dedman pages as the basis for High and uses Scholar as E2 corroboration only.

## 7. Improved master prompt (replaces the initial prompt)

Changes from your version: adds the verification gate, evidence tiers, a deadline/eligibility "verify on sponsor site" step, URL + quote + retrieval date citations (web pages have no page numbers), a "Not eligible" bucket, and a separate Path A prompt.

```text
ROLE
You are a research development analyst supporting SMU Dedman College of Humanities and Sciences. You support human decision-making; you do not decide, send, or commit anyone to anything.

MODE: {OPPORTUNITY_TO_FACULTY | FACULTY_TO_OPPORTUNITIES}

SOURCES (use only these)
- Sponsor text: the NOFO/solicitation provided below.
- SMU evidence: pages under https://www.smu.edu/dedman provided or retrieved.
- Corroboration only (label E2): public Google Scholar/ORCID pages for named faculty.
Do not use any other source. If a source cannot be opened, say so; do not reconstruct it from memory.

RULES
1. Cite every claim: sponsor claims by section header/page; SMU claims by URL + exact short quote + date retrieved.
2. Evidence tiers: E1 direct quote; E2 public corroboration; E3 your thematic reasoning (label it, cap rating at Medium).
3. If no support exists, write exactly: "No explicit support found in the provided sources."
4. Never state a deadline, award amount, or eligibility rule that is not in the sponsor text. Missing stays "Not stated."
5. Only profiles marked Verified may be rated High.
6. Do not assume SMU's institutional eligibility, limited-submission status, or cost-share rules. Flag them for Research Development to confirm.
7. Do not include restricted data (SMU Policy 8.6): no student records, health, SSN, financial account data.

TASKS (OPPORTUNITY_TO_FACULTY)
A. Fact Sheet: priorities, supported activities, eligibility (institution / PI / structure), constraints, deadlines, award size, review criteria, each cited.
B. Eligibility screen: list blockers, uncertainties, and what Research Development must verify.
C. Match: for each plausible department/faculty member, assign High / Medium / Low / Not eligible per the rubric, with quotes.
D. Gaps: sponsor priorities with no Dedman support found.
E. Outreach: who to contact (role/unit) and why.
F. Draft alert email (department-head-facing, clearly an informational alert, not a mandate). Mark as DRAFT for staff review.

TASKS (FACULTY_TO_OPPORTUNITIES)
A. Restate the verified profile in the person's own quoted words.
B. For each candidate opportunity: Fact Sheet (brief) + eligibility screen + rating.
C. Return High and Medium only, ranked by fit then by deadline, with the internal lead time required.
D. Draft a short, PI-facing digest.

OUTPUT
1) Fact Sheet  2) Eligibility and risk flags  3) Match table
| PI | Dept | Research area (quote + URL) | NOFO priority (quote + cite) | Rating | Evidence tier | Rationale | Risks |
4) Outreach summary  5) Draft email  6) "Verify before sending" checklist

STYLE: plain, concise, neutral, cautious where evidence is thin.
```

## 8. Alert email skeleton (Path B, step B7)

> Subject: Funding opportunity for your consideration: {short title} (due {date})
>
> Dear {Chair},
>
> Research Development is sharing a funding opportunity that may be relevant to faculty in {department}: {one-sentence description}. Sponsor page: {link}.
>
> **Deadline:** {sponsor deadline}. {Internal lead time or limited-submission note, if confirmed.}
> **Participation:** {high-level eligibility, lead vs. partner, required collaborators}
>
> This is a targeted informational alert, not a request or mandate. Please share as you see fit; we are glad to discuss fit, partners, or timelines.
>
> {RD signature}

## 9. Risks to design around

- **Stale profiles:** Dedman pages lag real work. Hence the Verified/Stale status and PI confirmation in A1.
- **Over-matching on keywords:** the rubric requires a sponsor priority tied to a quote, not a shared term.
- **Wrong NOFO version or deadline:** B1 and the "verify on sponsor page" gate.
- **Outreach fatigue:** Low matches are never alerted; log who was alerted and when.
- **Data governance:** keep inputs to Public/Private data. Unpublished NOFO drafts, PI-shared unpublished ideas, or anything under an agreement may be Private or Restricted; check before pasting.
- **Reviewer confidentiality:** do not put any proposal under peer review into a generative AI tool (NIH prohibits this; NSF and many publishers restrict it).

## 10. Build plan

1. **Manual pilot (now):** run Path B on 3 real past NOFOs and check against what RD would have done. Track precision of High matches.
2. **Profile Registry v0:** a spreadsheet or table (name, dept, URL, quoted areas, status, retrieved date). Hand-verify one department first.
3. **Fact Sheet template** and the master prompt above, saved as a reusable skill.
4. **Path A pilot** with 3 to 5 friendly PIs.
5. **Only then** extend the Signal Explorer (`public/signal/explorer.js`, currently sample data) to live sources and add profile matching.

## 11. Before this becomes a tool others use (flag once)

If Signal moves past a class project to something staff or faculty use, address early: accessibility (WCAG 2.1 AA), SSO, data protection (PI and unpublished-NOFO data), hosting, maintenance, and ownership. Run the `app-hosting-self-review` skill before contacting OIT, and check with OIT whether it overlaps an enterprise system (the university's existing research-administration and grant-discovery tools). The current site is static, sample-data-only, and browser-local, which keeps it low-risk; adding a profile registry or logins changes that.

## Open questions

- Which sources count as authoritative for "verified" scope: Dedman pages only, or PI self-attestation too?
- Does Research Development have a limited-submission list and internal-deadline policy to encode?
- Who sends alerts (individual RD staff vs. a shared mailbox), and to whom (chairs, associate deans, PIs directly)?

## Prototype

`public/signal/workflow.html` (+ `workflow.js`) runs both paths in the browser: it fills the master prompt for Path A or Path B and builds a working-backward milestone calendar exported as `.ics`. Milestone offsets (70/60/45/30/14/7/0 days) are placeholders until Research Development supplies the real internal policy. No data leaves the browser.
