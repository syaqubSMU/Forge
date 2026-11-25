# FORGE SIGNAL: UI/UX improvement plan

Status: DRAFT for the project owner's approval. **No product code was changed.** Everything here is a plan.
Date: 25 Nov 2026. Branch: `claude/practical-franklin-ze9hk2`. Demo: Dec 2. Testers: Dec 2 to 4.
Scope: the seven static pages in `public/signal/`, in sample mode and in live mode (backend with the default **mock** model, so no paid calls).
Data: public and private only. Every researcher, opportunity and date in the screenshots is fictional sample data.

Boundaries held throughout (from `docs/SIGNAL_BOUNDARIES.md` and PRD v0.2 section 4): unsupported claims never raise a rating; quotes link to the official source; nothing is sent without a person confirming; no accuracy percentages; no promises of speed; the footer keeps the "class capstone project, not an approved or endorsed university service" framing.

---

## 0. Summary

### Top 5 changes (details in section 3)
1. **Put run status and errors where the person is looking** (Match). Today the "Running" panel, the validation error and the timer all render about 600 px below the button, off screen. A person who clicks with an empty name sees nothing happen. (M1, M5)
2. **Stop shipping a fictional researcher into real runs and real drafts** (Match, Review). In live mode the name and four research areas are pre-filled with "Dr. R. Alvarez (fictional)". I ran a live run with the default values and the draft alert greeted "Dear Dr. R. Alvarez (fictional)". (M2)
3. **Give zero results, no run and nothing-to-send honest, specific states** (Results, Calendar, Review). A run with 0 rated results currently says "No results match these filters, remove a filter above" when no filter is set, leaves Top 5 and the tables blank, and lets the person draft and "send" an alert listing 0 items. (M3, M4)
4. **Make the waiting experience honest** (Match). The step list ticks steps 1 to 3 as done after 2.7 seconds whatever the server is doing. Replace ticks with an elapsed timer, a plain "30 seconds to several minutes" message, a status that screen readers announce, and a way to stop waiting. (M5)
5. **Reduce Results and Calendar density** (should fix). Fold the evidence quotes into one disclosure per card; reorder Calendar columns so Eligibility and Next action are not off screen; add a one-line "your check" per card that says what *Needs verification* means and what to do. (S1 to S3)

Also found, small but important: the focus ring (coral on white, 2.68:1) is below the 3:1 non-text contrast minimum; text inputs have a 2.22:1 border; the Calendar export hint is 2.8:1 on navy; the Review draft is not marked DRAFT; the stale sample timestamp "screened 24 Nov 2026, 2:05 pm UTC" shows in live mode with no run.

### Files written
- `docs/UX_IMPROVEMENT_PLAN.md` (this file)
- `docs/ux/` screenshots (listed in section 1) and `docs/ux/wireframes.html` (section 6)

### Honest limits of this review
One reviewer, one machine, Chromium only, no real screen reader, no real users. The pages now use no external fonts (system font stack; Inter is used only where installed); contrast figures are computed from the CSS colours and are unaffected. Live mode used the mock model, so I did not see real model output, real quotes or real run times. The run took about 15 s with the mock (Grants.gov pull plus 25 mock judgments); that says nothing about real-model speed.

**Not tested (keep this line):** a populated live run by a person, a screen reader (NVDA, JAWS, VoiceOver), and 200 to 400 percent zoom. Automated axe-core checks found no issues, but no conformance with WCAG is claimed.

---

## 1. Heuristic review by page

Method: Nielsen's ten heuristics, plus the product's own rules (AI proposes, a person decides). Screenshots are in `docs/ux/`; `d-` is desktop 1440 px, `m-` is a 390 px phone, `z200-` is a 640 px viewport (200 percent zoom of a 1280 px window), `live-` is live mode.

Severity: **S3** blocks or misleads, **S2** causes friction or doubt, **S1** polish.

### 1.1 Home (`index.html`) · `d-index.png`
Works well: the problem, the five-step flow with human steps marked in red, and the six "what you can rely on" rules are clear and match the boundary document. The "Runs are logged" notice is present.
| # | Finding | Sev |
|---|---|---|
| H1 | The explainer video is 21 s, video only, no audio track (checked with ffprobe). Its `aria-label` is one line. WCAG 1.2.1 (Level A) needs a text alternative for video-only content. | S2 |
| H2 | Two primary calls to action ("Start a match" appears twice) and a second ghost button "See a worked example" that goes to Results, which in live mode may say "No run yet". Label it "See a sample result" only in sample mode, or hide it in live mode. | S1 |
| H3 | Nothing on Home says that a run may take minutes. A first-time visitor learns that only after clicking. One sentence under the button is enough. | S2 |

### 1.2 Match (`match.html`) · `d-match-fold.png`, `d-match-running.png`, `live-match-error.png`, `live-match-running.png`, `z200-match.png`, `m-match.png`
| # | Finding | Sev |
|---|---|---|
| M-1 | **Status is off screen.** The "Running" card (timer, step list, error, finished notice) sits below the form. At 1440x900 the button is near the fold and the card is about 600 px lower. After submit `scrollY` stayed 0 and the card was not in the viewport. A validation error ("Enter the researcher's name and at least one established research area.") appears under a heading that says "Running", in the wrong place, and focus stays on the button. Sighted users see nothing. Screen-reader users get it because of `role="alert"`. | S3 |
| M-2 | **Fictional person pre-filled in live mode.** Name "Dr. R. Alvarez (fictional)", four research areas and two positioning rules are in the fields. Confirmed in a live run: the draft alert opened "Dear Dr. R. Alvarez (fictional),". This also hides the required-field behaviour from testers. | S3 |
| M-3 | **The step list claims progress it cannot know.** Steps 1 to 3 turn green with a check after 2.7 s, then step 4 stays "now". The code comment admits "the server does not report steps". The timer text says so too, but the green ticks contradict it. That is a small trust problem in a product whose pitch is "nothing asserted without a source". | S2 |
| M-4 | **Waiting copy is inconsistent.** Sample mode: "takes under 30 seconds". Live mode replaces it with "can take a minute or more". The sample copy is a speed promise the product cannot support. | S2 |
| M-5 | **Hero is large and half empty.** On desktop the dark hero is about 370 px tall, the right half is empty, and the form starts below the first screen. This is mostly cosmetic; the fix is to shrink the hero, not to fill it (see S4). | S1 |
| M-6 | The researcher-areas textarea shows 3.5 lines, so the fourth area is cut off with no hint that it scrolls. Give it `rows` for all lines, or auto-size. | S1 |
| M-7 | The disabled "opportunity and department" radio is visually faint and the live-mode explanation ("Not available in the live engine yet.") sits to the right of a long label and wraps. Replace by a visible "Coming later" tag and take the option out of the tab order cleanly. | S1 |
| M-8 | Required fields are not marked required, have no `aria-invalid`, and the error is not tied to the field with `aria-describedby`. | S2 |
| M-9 | There is no confirm-the-profile step. PRD FR-41 calls for one. Today the "confirmation" is the person editing a pre-filled box. This is the right place to show where research areas came from once PI lookup exists. See W3. | S2 (S3 once lookup lands) |
Phone: single column, no sideways scroll (checked at 320 and 640 px).

### 1.3 Results (`results.html`) · `d-results.png`, `d-result-card-open.png`, `d-result-card-needs.png`, `live-results.png`, `live-results-norun.png`, `m-results.png`
| # | Finding | Sev |
|---|---|---|
| R-1 | **Zero-result state is wrong.** Live run with 25 screened and 0 rated: the hero says "0 of 25 screened opportunities are shown", the list says "No results match these filters. Remove a filter above to see it." although no filter is active, and "Showing all 0 results, highest fit first." appears. It never says why (everything was excluded or below the minimum rating setting) or what to try. | S3 |
| R-2 | **No-run state keeps stale hero content.** In live mode with no run, the hero still reads "Step 2 of 3 · screened 24 Nov 2026, 2:05 pm UTC" (sample text from the HTML) and shows "Open the calendar" and "Draft an alert" buttons next to "No run yet." | S3 |
| R-3 | **Cards are dense.** A card with three citations shows three quote blocks, each with a label, quote, link and date, before "How this fit was calculated". With 7 to 25 cards the page is a long scroll and the decision-relevant facts (rating, eligibility, deadline, next step) are not scannable. | S2 |
| R-4 | **"Needs verification" is explained once, in aggregate**, in the notice above the list ("Confirm every deadline and eligibility requirement on the sponsor page"). The card shows the badge but not why or what to do next. The Calendar has a "Recommended next action" column; Results does not. Because most eligibility will be "Needs verification" this is the most repeated question a tester will ask. | S2 |
| R-5 | **Run-to-run differences are not acknowledged.** Same inputs produced 2 results one time and 1 the next. Nothing on the page says that model-based screening can vary, or shows the run ID so a person can say which run they mean. | S2 |
| R-6 | The counters bar touches the hero's bottom border in live mode (no gap; compare sample mode where the filter bar follows). Cosmetic. | S1 |
| R-7 | Filter chips container has `aria-label` on a plain div (axe: `aria-prohibited-attr`, serious). | S2 |
| R-8 | Good: the "screening results, not decisions" notice; badges always carry words; "How this fit was calculated" shows factors, rule IDs and adjustments, and says unsupported claims never raise a rating; the filter result count is in an `aria-live` region. | – |

### 1.4 Calendar (`calendar.html`) · `d-calendar-fold.png`, `d-calendar-table.png`, `m-calendar.png`, `z200-calendar.png`, `live-calendar.png`
| # | Finding | Sev |
|---|---|---|
| C-1 | **The two most decision-relevant columns are off screen.** At 1440 px the first table shows Opportunity to Days left (7 of 12). Eligibility, Recommended next action and Official source need sideways scrolling. The scroll hint ("Each table has more columns than fit on screen") is a small grey line far above the tables. | S2 |
| C-2 | **Hero hint is unreadable.** "Export buttons are inactive in this preview." is 2.8:1 on navy (axe: serious). The two export buttons look active but do nothing in sample mode; they are `<button>`s with no disabled state. | S2 |
| C-3 | **Empty states are blank.** Live run with no rated results: "Top 5 for this window" is an empty heading with no list text, and the tables area is empty with no message. | S2 |
| C-4 | **A passed internal deadline is shown as a normal date.** Sample: sponsor deadline Nov 30 with internal deadline Nov 16, while the sample run date is Nov 24. This is correct logic (it is why the item is in "Decide now") but the table does not say "passed". | S2 |
| C-5 | "Needs action within 45 days" includes Low-fit items without showing the rating. Consider the badge, as in Top 5. | S1 |
| C-6 | Page overflows sideways by 11 px at 320 px wide (nowrap badges). WCAG 1.4.10 reflow. | S2 |
| C-7 | Good: "Decide now" is first, fixed/rolling/watch are separate captions, "not stated" never becomes a fake date, mobile stacks rows with a label per cell. Desktop table semantics are fine (caption, `scope="col"`). | – |

### 1.5 Review (`review.html`) · `d-review.png`, `live-review.png`, `m-review.png`
| # | Finding | Sev |
|---|---|---|
| V-1 | **Empty alert can be "sent".** With 0 High or Medium results the draft reads "0 may be worth a look:" followed by nothing, and Send alert became enabled once a recipient was typed and the box ticked. | S3 |
| V-2 | **The draft is not marked DRAFT** in its text. PRD FR-15 and the boundary document say "always marked DRAFT". A hint above the textarea says it is a draft, but the text a person would copy does not. | S2 |
| V-3 | **The button says "Send alert"** while the page is in dummy mode (nothing leaves the system). The only statement is a small grey hint under the button. Say "Log alert (nothing is emailed)" while in dummy mode. | S2 |
| V-4 | **Result message has no live region.** The confirmation or the "Not sent:" error appears in a notice that is not announced. | S2 |
| V-5 | **Greeting in live mode uses whatever was typed**, so "Dear Dr. R. Alvarez (fictional)," or "Dear Test Person,". Use a neutral "Hello," plus an editable placeholder, or leave the greeting for the person (they own the message). | S2 |
| V-6 | Good: the confirmation tick states what the person takes responsibility for; "Who this reaches", "Held back" and "Excluded" make coverage a visible decision; "Check who is missing" is a strong prompt. | – |

### 1.6 About (`about.html`) · `d-about.png`
Strong content and a good model of the boundaries. Findings: the `table-scroll` region has no focusable content (axe: `scrollable-region-focusable`, serious); the page overflows by 20 px at 320 px (the two-column `.collab` cards have a 320 px minimum width plus padding). Add a one-line "Who built this and why" and the capstone framing near the top, not only in the footer (S1).

### 1.7 Settings (`settings.html`) · `d-settings.png`
Admin page, still sample only. Findings: it is in the public main navigation with an "admin" tag, so every visitor sees and can open it; every button looks live but does nothing and gives no feedback; the API key field is a `type=text` showing bullets (use a clear "stored on the server, cannot be shown" statement, not a fake input); one empty `<th>` in the run-log table. For a public deployment hide it from the nav or label it "Admin (preview, not connected)". Not needed for the demo if the demo is not on a public link (S2).

---

## 2. WCAG 2.1 AA check

Target: WCAG 2.1 AA (SMU guidance). PRD says to design to 2.2 AA; the 2.2-only items (focus not obscured, target size minimum) are noted where I looked but are not scored.

### 2.1 What I could test automatically, and the results
Tools: axe-core 4.10.2 (rules wcag2a, wcag2aa, wcag21a, wcag21aa and best-practice) on each page at 1440 px in sample mode, Playwright keyboard walk, computed contrast from the CSS tokens, Playwright accessibility-tree dumps, viewport resizing for reflow. Automated tools find roughly a third of WCAG problems at most, so a clean axe result is not a pass.

**axe findings (sample mode, all seven pages)**
| Rule | Pages | Impact | Where | Fix |
|---|---|---|---|---|
| `color-contrast` | Calendar | serious | `#dl-hint` on the navy hero, 2.79:1 (needs 4.5:1) | Use `--on-navy-muted` (#AFC2D4, 8.8:1) |
| `aria-prohibited-attr` | Results | serious | `#chips` div has `aria-label` | `role="group"` plus label, or remove the label |
| `scrollable-region-focusable` | About | serious | `.table-scroll` with no focusable child | `tabindex="0"`, `role="region"`, `aria-label` on every `.table-scroll` |
| `heading-order` | Match, Results, Calendar | moderate | first heading after the hero `h1` is an `h3` | Use `h2` for section headings, `h3` inside cards |
| `region` | all 7 | moderate | `.mock-banner` is outside any landmark | Move the banner inside `<header>` or give it `role="region"` and a label |
| `empty-table-header` | Settings | minor | blank `<th>` in run-log table | Visually hidden "Actions" text |

**Not flagged by axe but found by hand or by computation**
| Check | Result |
|---|---|
| Focus indicator contrast (2.4.7, and 1.4.11 as most auditors read it) | `:focus-visible` is a 3 px **coral** ring (#E98262). On white it is 2.68:1, on the page background 2.43:1, on the pale-blue panels 2.42:1. Below 3:1 on the light surfaces, where most of the page is. Replace with a two-colour ring (2 px white inside, 3 px Trust Blue outside) that works on every background. |
| Text-input border (1.4.11) | `#9FB0C0` on white is 2.22:1; the field boundary is the only cue to where the input is. Darken to about `#6B7F91` (3.9:1). Select borders are the same colour. |
| Card and chip borders | Decorative. Content inside carries its own text, so these are not required to reach 3:1. |
| Rating badges (text) | High 8.16, Medium 5.25, Low 8.01 against their own backgrounds. Pass. Status is never colour alone. |
| Muted text on page and panels | 5.2:1 on warm and pale blue. Pass. |
| Coral-ink small text | 5.5:1. Pass. Accent button text 6.6:1. Pass. |
| Keyboard order | Tab stops per page: Home 18, Match 20, Results 47, Calendar 21, Review 13, About 15, Settings 30. First stop is "Skip to main content" on every page. No element had `outline: none`. Results has 47 stops because every card has its title plus up to three identical "Official source" links. |
| Reflow (1.4.10) at 320 px wide | Overflow: Calendar by 11 px (badges), About by 20 px (collab cards). Others fit. At 640 px (200 percent zoom of 1280) no page overflowed; screenshots `z200-*.png` show the nav wrapping onto two lines and the hero still readable. |
| Reduced motion | Home video does not autoplay under `prefers-reduced-motion: reduce` and has a Pause/Play button. `scroll-behavior` is set to auto. The only other motion is a 0.15 s caret rotation on `details`. |
| Language, page titles, skip link | `lang="en"`, unique `<title>` per page, working skip link. |
| Form labels | Every control has a visible `<label for>`. Radio groups are in a `fieldset` with a `legend`. |

**Screen-reader pass of the Results card and the Calendar tables.** I did not run a screen reader. I read Playwright's accessibility-tree output, which approximates what NVDA, JAWS and VoiceOver build, and flag these for a real pass:
| # | Observation from the accessibility tree |
|---|---|
| SR-1 | The result `<article>` has **no accessible name**; a user navigating by landmarks or articles hears "article" with no title. Add `aria-labelledby` pointing at the `h3`. |
| SR-2 | The meta line "Sample Federal Agency \| SS-26-118 \| Sponsor deadline: …" and the three badges are plain text in one run. The `\|` separators are read aloud. Use a `<ul>` or `<dl>` for meta, and hide separators with CSS. |
| SR-3 | **Quotes are not marked up.** The label ("centrality"), the quote and the source line are three loose text runs; the quote is not a `<blockquote>` and the label does not say what it labels. A listener hears "centrality instrumentation that advances… Official source · retrieved Nov 24, 2026". Use `<figure><blockquote>` with a `<figcaption>`. |
| SR-4 | Three links in one card are all named "Official source". Links list (2.4.4 in context passes, but poorly). Use `aria-label="Official source for SS-26-118"` or visible text that includes the call ID. |
| SR-5 | The disclosure ("How this fit was calculated") exposes as a `group`; the arrow is CSS, so it is not read. Good. Native `<details>` supports Enter and Space. |
| SR-6 | Calendar, desktop: tables expose `caption`, 12 `columnheader`s and cells. Fine. The wrapper scroll region is not focusable (sideways scroll is keyboard-reachable only through links in the row). |
| SR-7 | Calendar, phone (under 760 px): the CSS turns `table`, `tr` and `td` into `display:block`/`grid`. In the tree each cell is named "Label value" because the label is injected with `::before`, which is fine, but with `display:block` on table elements some browser and screen-reader pairs drop table semantics. Test with VoiceOver on iOS. Safer: keep table roles with `role="table"`, `role="row"` and `role="cell"` on the blocked elements. |
| SR-8 | Match: after "Screening finished" focus moves to `#done` (good). The timer line and the step list are not in a live region; nothing announces that a run started. |
| SR-9 | Review: the result message is not in a live region. |

### 2.2 What needs a human
| Item | Why automation cannot do it | Suggested check |
|---|---|---|
| Real screen-reader pass (NVDA + Firefox or Chrome on Windows, VoiceOver + Safari on Mac and iOS) of Match, a Results card, a Calendar table and the Review confirm | Output and verbosity are only known by listening; SR-1 to SR-9 are predictions | 45 min per reader, task script in section 4 (task T4 to T7) |
| Meaning of focus order and focus management (after filtering, after a run, after an error) | Axe cannot judge whether order makes sense | Tab through each page with the screen off; note surprises |
| Zoom to 200 percent and text spacing (1.4.12) in a real browser | I used viewport width as a proxy, which is the same layout width but not the same text rendering | Ctrl+plus to 200 percent on a 1280 px window; apply the text-spacing bookmarklet |
| Colour contrast over the hero video poster and any text on images | Not covered by the CSS-token calculation | Visual check of `assets/poster.jpg` states |
| Video text alternative (H1) | Need to judge whether the transcript carries the same information | Write a short transcript, review against the video |
| Plain-language reading level and error-message clarity | Judgement | Cognitive walkthrough with two reviewers; section 5 |
| Touch targets on phone (2.5.8 in 2.2) and pointer cancellation | Needs a real touch device | Try the chip close button (about 20 px) and the filter chips on a phone |
| A formal accessibility statement and conformance claim | Requires a full audit | After testers, if SMU hosts it; use SMU's route (below) |

**Hosting note (flagged once, as SMU guidance asks).** If this is hosted for people other than the class, SMU asks that it meet WCAG 2.1 AA and that accessibility, SSO, data protection, hosting, maintenance and ownership be considered before it is hosted. Run the `app-hosting-self-review` skill before contacting OIT, and ask OIT whether this overlaps an enterprise system. PRD section 12 already lists this; it is not part of this UX plan's scope.

---

## 3. Prioritised change list

Effort is my estimate for one person who knows the code, including a quick manual check, in sample and live mode. Risk is the chance of breaking something that works today. "Demo" means the Dec 2 working demo.

**Reality check.** The remaining time is claimed by backend speed, PI lookup and deployment. I therefore split "Must" into a **core (M1 to M8, about 8.5 hours)** that fixes things that mislead or hide the product's main flow, and a **stretch (M9, about 3 hours)** that is cheap accessibility hygiene. If only about 4 hours exist, do M1, M2 and the Results part of M3 (about 4 hours) and leave the rest for Dec 4.

### 3.1 Must fix before the Dec 2 demo
| ID | Change | Pages | Impact | Effort (h) | Risk | Notes |
|---|---|---|---|---|---|---|
| **M1** | Show errors and run status next to the button. On submit: validate; put the error in the "This run" card above the button and in a short summary at the top of the form; set `aria-invalid` and `aria-describedby` on the bad field; mark required fields; scroll the status into view. | Match | High: today a failed click looks like nothing happened | 1.5 | Low | See W1. Text in section 5.1 |
| **M2** | Empty researcher fields in live mode. Keep the fictional person only in sample mode, behind a "Use the sample researcher" button. Replace the draft greeting with a neutral "Hello," for the person to edit. | Match, Review | High: stops a fictional name entering real runs and real drafts | 1 | Low | One condition on `LIVE` in `app.js`; update `match.html` defaults |
| **M3** | Honest zero states. Results: if `shown === 0` and no filter is set, say "Nothing rated at or above [setting]. 25 screened; N excluded and kept in the run log" and list next steps. Calendar: a message in place of blank Top 5 and the empty tables area. Review: if nothing is High or Medium, disable "Send" and say why. | Results, Calendar, Review | High | 2 | Low | Text in 5.3 and 5.4 |
| **M4** | No-run state: hide the hero's stale timestamp, the "Open the calendar" and "Draft an alert" buttons, and "Loading…". | Results, Calendar, Review | Medium | 0.5 | Low | `noRun()` already hides `main > .wrap`; hide the hero's content too |
| **M5** | Honest waiting experience, core version: remove step ticks, show "Screening in progress, 1 min 12 s" in a `role="status"` region (update the spoken text every 30 s, the visible timer every second), say that it can take longer when several people search at once, and to keep the tab open, add "Stop waiting". Replace the sample-mode "under 30 seconds" copy. | Match | High: removes an unsupported claim and an invisible state | 2.5 | Low to medium (the abort only stops the browser waiting) | See W1 and 5.2. Design stays valid after the speed fix: if the run gets fast it just shows a short timer |
| **M6** | Review: put "DRAFT" in the subject line and the first line of the body; rename the button to "Log alert (nothing is emailed)" while in dummy mode; give the result message `role="status"`. | Review | Medium: enforces the boundary document | 0.5 | Low | |
| **M7** | Add one sentence to Results under the notice: "Screening by a model can differ between runs on the same inputs. Run ID: …" and show the run ID in the hero. | Results, Calendar | Medium: sets honest expectations and lets reviewers refer to a run | 0.25 | Low | Do not mention percentages |
| **M8** | Add a short key under the Results notice: "Needs verification means the announcement does not clearly say who may apply. Open the sponsor page and read the eligibility section, or ask the program officer." | Results | Medium: the most repeated tester question | 0.25 | Low | Per-card version is S3 |
| **M9** (stretch) | Quick accessibility fixes: focus ring (blue + white), input border colour, `#dl-hint` colour, `tabindex`/`role`/`aria-label` on `.table-scroll`, `#chips` role, banner inside `<header>`, headings `h2` under `h1`, empty `th` text, badge `white-space` at 320 px, About collab min-width. | all | Medium: clears every axe finding and the two contrast gaps | 3 | Low | One CSS commit plus small HTML edits. `app.css` uses tokens, so the focus ring and border are one-line changes |

Must total: core M1 to M8 about 8.5 h; M9 about 3 h. The 4-hour cut is in the reality check above.

### 3.2 Should fix before testers (Dec 2 to 4)
| ID | Change | Impact | Effort (h) | Risk | Notes |
|---|---|---|---|---|---|
| **S1** | Result card: summary first. Keep title, meta, badges, one-sentence rationale and a "Your check" line visible; fold quotes and "How this fit was calculated" into one "Evidence (3 quotes, all found in sources)" disclosure; keep a one-line preview of the first quote. Count and mention discarded quotes in the collapsed line. | High: biggest scan-time saving; cards roughly a third of the height | 3 | Medium (must keep every quote, link and retrieval date reachable) | W2 |
| **S2** | Calendar columns: reorder to Opportunity, Fit, Sponsor deadline, Internal deadline, Eligibility, Next action, then the rest; make the first column sticky; add a visible "Scroll sideways" shadow or a "Core columns / All columns" toggle; show "(passed)" next to a past internal deadline. | High | 3 | Medium (export keeps its own columns, so unaffected) | |
| **S3** | Per-card "Your check" line from fixed wording keyed to the eligibility value and flags (limited submission, invitation only, closing soon). Never model-written. | High | 1.5 | Low | Reuse `next_action` logic from the Calendar |
| **S4** | Match hero: cut to a compact title bar (about 120 px) so the form starts on the first screen; no new content on the right. | Medium | 1 | Low | |
| **S5** | Semantic markup for evidence and cards: `article aria-labelledby`, `figure/blockquote/figcaption` for quotes, unique link names, a `<dl>` for meta. | Medium (screen-reader users) | 2 | Low | SR-1 to SR-4 |
| **S6** | Phone table: add table roles to the blocked elements, test with VoiceOver; make the mobile stack show the first four fields only and the rest under "More". | Medium | 2 | Medium | SR-7 |
| **S7** | Home video: add a short transcript or "Describe this video" disclosure; hide the second CTA in live mode. | Low to medium | 0.75 | Low | H1, H2 |
| **S8** | Settings: hide from public nav or relabel "Admin (preview, not connected)"; show "Not connected in this preview" instead of dead buttons. | Medium if the link is public | 0.75 | Low | |
| **S9** | Results: group by rating with count headings ("High (3)", "Medium (2)", "Low (2)") and a sticky "Back to filters" link; keep filters but add result-count text near the filter bar. | Medium | 1.5 | Low | |
| **S10** | A "Tester feedback" link in the footer that opens a prefilled mailto or form with the run ID. Must not send any run data automatically. | Medium: makes Dec 2 to 4 productive | 0.5 | Low | The text must say what is shared |

Should total about 16 h. Realistically pick S1, S2, S3, S4 (about 8.5 h) if time allows; the rest wait for Dec 4 to 6.

### 3.3 Later (Dec 4 to 6 and beyond)
| ID | Change | Impact | Effort (h) |
|---|---|---|---|
| L1 | Server progress (Server-Sent Events or polling) so the Match page can show real steps, "Screened 8 of 25", and partial results as they arrive | High once speed work lands | 6 to 10 (backend plus front end) |
| L2 | The confirm-the-profile step with quoted evidence for each proposed area, once public publication lookup is allowed (PRD FR-41, O20) | High for the consultant journey | 6 to 8 | 
| L3 | Compare two runs of the same inputs side by side, to make the run-to-run variation visible | Medium | 4 |
| L4 | Print-friendly Calendar and a copy-to-clipboard of selected rows | Medium | 3 |
| L5 | Save-and-restore of the latest run beyond this tab (currently `sessionStorage`; the PRD forbids a stored faculty index, so scope carefully) | Low to medium | 3 |
| L6 | Full accessibility audit with screen readers, an accessibility statement and a VPAT if SMU asks | Needed for hosting | 12 to 20 |
| L7 | Unit-mode (opportunity plus department) UI once the engine supports it | Medium | 4 |

---

## 4. Usability test script

Purpose: find where first-time users stall, misread a rating, or trust something they should check. Not to measure model accuracy.

### 4.1 Setup
- **Reviewers: 6 to 8** (5 is enough to find most issues; plan 8 so two can be screen-reader or phone users). Mix: 3 to 4 research development or sponsored-programs staff (Script A), 2 to 3 grant consultants or faculty who look up other researchers (Script B), at least 1 using a screen reader and at least 1 on a phone.
- **Session:** 30 minutes, one facilitator and one note-taker, screen shared or in person.
- **Environment:** use sample mode for reviewers who just need to judge comprehension. Use live mode only for the facilitator-run scripted task T2 (cost and time: it calls the real model; confirm the daily cap with the owner first).
- **Data rules:** public and private data only. Use the fictional researcher by default. For Script B, reviewers may type **their own name** or a **public figure with that person's agreement**. Do not enter anything about students, health or finances. The run log stores the inputs for 90 days, so tell reviewers this before they start (the page already says it).
- **Research ethics:** this is informal capstone usability testing. Ask the instructor whether it needs any review; for anything that goes beyond class feedback, SMU Research Integrity and Compliance is the office to ask.
- **Say at the start:** "We are testing the tool, not you. There are no wrong answers. The tool is a class capstone project, not an approved or endorsed university service. If something is slow, please say what you are thinking while you wait."

### 4.2 Script A: research development staff
| # | Task (read aloud, then be quiet) | Success means | Observe | Questions after the task |
|---|---|---|---|---|
| T1 | "You want to find funding for a researcher. Start from the home page." | Reaches Match unaided | Does the person find "Start a match" or the nav? Do they read the "How it works" box? | "What do you expect to happen next?" |
| T2 | "Screen opportunities for the sample researcher, with the settings as they are." | Starts a run and notices when it finishes | Where do they look while waiting? Do they know the run has started? Do they click twice? How long before they say "is it stuck"? Record seconds. | "What did you think was happening?" "What would you have wanted to see?" |
| T3 | (With the name field empty, ask them to start a run.) "Try starting with the name blank." | Notices and fixes the error | Do they see the message? Time to recover. | "How did you know what was wrong?" |
| T4 | "Look at the results. Which opportunity would you look at first, and why?" | Names one and gives a reason that uses the fit word, deadline or eligibility | Which parts of the card do they read? Do they scroll past the quotes? | "What does 'High · Very strong fit' mean to you?" (Do not correct them) |
| T5 | "Pick one result. What does 'Needs verification' mean, and what would you do next?" | Says it is not confirmed and the next step is to check the sponsor page | Do they find the key or the next-step line? | "How confident are you in that?" (1 to 5) |
| T6 | "Where does the claim that this fits come from? Show me how you would check it." | Opens a quote and the official source link; can find "How this fit was calculated" | Do they understand that the rating is calculated by rules, not chosen by the AI? | "Who decides the rating?" |
| T7 | "Which deadline do you need to act on first? Find it on the Calendar." | Finds "Decide now" or the nearest sponsor and internal deadline | Do they notice sideways scroll? Can they find Eligibility and Next action columns? Do they understand 'internal deadline'? | "What does 'internal deadline' mean here?" |
| T8 | "Prepare an alert for the researcher but do not send it. Then tell me what would happen if you pressed the button." | Edits the draft, ticks the confirmation, can say that nothing is emailed in dummy mode | Do they read the confirmation text? Do they notice "DRAFT"? | "Who is responsible for this message?" "Is anyone missing from the list?" (look at Held back) |

### 4.3 Script B: a grant consultant looking up a PI at a university
Scenario card (read aloud): "You advise a university research office. A professor at a university has asked what funding might fit their work. You have a few minutes before a call with them."
Note for the facilitator: **automatic public-record lookup of a PI by name is not available yet** (PRD O20, FR-2, FR-41). Until it is, the researcher's areas are typed or pasted by the user. Say so honestly if asked. Test the intended future design with the wireframe W3 on paper or in the sample prototype, and ask for reactions.

| # | Task | Success means | Observe | Questions |
|---|---|---|---|---|
| B1 | "Describe this researcher to the tool. Use whatever you would know from their public page." | Enters a name (or leaves it blank for keywords) and at least one research area in the researcher's own words | Do they know what to put in "Established research areas"? Do they copy from a faculty page? Do they enter areas that are not the researcher's? | "Where would you normally get these areas from?" "How would you check them with the researcher?" |
| B2 | "Show me the sources you would trust to confirm someone's research areas." (paper wireframe W3) | Chooses faculty page, publication record, researcher themselves | Do they want to see the evidence per area? Do they understand 'keep or drop'? | "What would make you trust the proposed areas?" |
| B3 | "Run it." (then T2 observations) | As T2 | The consultant often multitasks: do they leave the tab? What do they expect to happen when they come back? | "What would you want to know when you come back?" |
| B4 | "From the results, which two would you tell the professor about, and what would you say about eligibility?" | Picks two; says eligibility is not confirmed | Which words do they borrow from the page? Do they over-claim ("this is a good match") or keep the wording "may fit"? | "How would you describe the rating to the professor?" |
| B5 | "What would you need to do before telling them?" | Checks the sponsor page, confirms deadlines and eligibility | Do they use the official source link? Does the next-step line help? | "What would you add to the card?" |
| B6 | "Export the calendar so you can use it later." (sample mode: buttons are inactive; note reaction) | Finds the export buttons | Is the inactive state clear? | "What did you expect to get?" |

### 4.4 Closing questions (both scripts, 5 minutes)
1. In your own words, what does this tool do and what does it not do? (Look for: "it proposes, a person decides", "does not send".)
2. What was the most confusing moment?
3. What one thing would you change?
4. Rate 1 to 5: "I understand why each result is shown." "I would check the sponsor page before acting." "I would use this again in my work."
5. Anything on the page you did not trust? Why?

### 4.5 Scoring sheet (one row per reviewer per task)
| Reviewer ID | Script (A or B) | Task | Success (0 = failed, 0.5 = needed hint, 1 = done unaided) | Time (seconds, to success or give-up) | Errors (count of wrong clicks, misreadings, restarts) | Confidence after task (1 to 5) | Notes and quote |
|---|---|---|---|---|---|---|---|
| R1 | A | T1 | | | | | |
| R1 | A | T2 | | | | | |
| … | | | | | | | |

Summary rows to compute after testing:
- Task success rate per task = sum of success scores ÷ reviewers. Flag any task under 0.8.
- Median time per task. Compare against the facilitator's own time as a baseline (not against any product promise).
- Mean confidence per task. A task with high success but low confidence needs wording work.
- Count of reviewers who could state the boundary (T6, closing Q1) correctly. This is the main trust measure.
- Issues log: ID, page, description, severity (S3 blocks or misleads, S2 friction, S1 polish), number of reviewers affected, proposed fix. Fix S3 first.

---

## 5. Content and wording suggestions

Rules: plain words; say what happened, why, and what to do next; no percentages; no promise of speed; never describe a named person as uncompetitive; never imply the AI decides.

### 5.1 Errors and validation
| Situation | Current | Suggested |
|---|---|---|
| Name or areas missing | "Enter the researcher's name and at least one established research area." (shown far below, under "Running") | Next to each field: "Enter the researcher's name." / "Enter at least one research area, one per line." Summary above the button: "Two things need fixing before screening can start." |
| Server unreachable | "Could not reach the server. Check your connection and try again." | "We could not reach the server. Your entries are still here. Check your connection and select Screen opportunities again." |
| Rate limit or daily cap (inferred; confirm the actual server wording) | server text | "You have reached the limit for runs in this hour. This limit keeps the free preview available for everyone. Try again after [time]." If the daily cap: "Today's preview limit has been reached. Try again tomorrow, or open the saved sample run." |
| Source down | listed under "Could not be read" | Keep that list. Add one line on Match and Results: "Some sources could not be read, so this result may be incomplete. See the list at the bottom." |
| Model failure on one opportunity | per-item record | "N opportunities could not be screened and are listed at the bottom. They were not skipped silently." |
| Opportunity-and-department not available | "Not available in the live engine yet." | "Coming later. Use a researcher, a project description or keywords for now." |
| Run abandoned by the user | none | "You stopped waiting. The run may still finish on the server; it will appear in the run log if it does." |

### 5.2 Waiting
| Current | Suggested |
|---|---|
| "A typical run reads several hundred announcements and takes under 30 seconds." (sample mode) | "A search reads current announcements and checks the best candidates. In two tests with 25 candidates and nobody else using the service, a search took 22 and 44 seconds; times vary, and it can take longer when several people search at once." Use only measured figures, state them as tests, and keep them out of headlines. |
| "Working for 27 s. The server does not report each step, so the list below is a guide. " | "Search in progress · 27 s. It can take longer when several people search at once. Keep this tab open. We cannot show step-by-step progress yet." |
| Step list with ticks | Static "What a run does" list, without ticks, collapsed by default |
| Finished: "Screening finished. 0 opportunities to review." | When 0: "Screening finished. Nothing was rated at or above your setting. See why on the next page." |

### 5.3 Empty states
| Where | Suggested |
|---|---|
| Results, nothing rated | "Nothing rated at or above 'Low and above' in this run. We screened 25 opportunities; they were ruled out (for example by a stated restriction) or had no supported connection to the research areas. They are kept in the run log. **Try:** a longer deadline window, a keyword search, or revising the research areas." |
| Results, filters hide everything | "No results match these filters. Every screened result is still in this run. [Clear all filters]" |
| Calendar, no items | "Nothing to put on the calendar. This run produced no rated opportunities. [Change the run]" |
| Top 5, fewer than 5 | "Only N opportunities were rated in this run." |
| Review, nothing to send | "Nothing to include in an alert. There are no High or Medium results in this run. You can still change the run or write a message yourself outside SIGNAL." |
| No run | "There is no run to show yet. Start a match first; results, the calendar and the draft alert are built from your latest run in this browser tab." |

### 5.4 Plain-language swaps
| Current | Suggested | Why |
|---|---|---|
| "Screen opportunities" | Keep. Under the button: "Nothing is sent or submitted." | Names the action truthfully |
| "Excluded items are kept in the run log, not here." | "N results were ruled out and are not shown. They are kept in the run log." | Plain, countable |
| "Needs verification" (badge) | Keep the badge; add the key sentence in M8 | Consistency with the PRD wording |
| "Decide now" | "Needs a decision now" with "Rated High or Medium and inside your internal lead time" | Makes clear a person decides |
| "Days left" | "Days to sponsor deadline" | Avoids confusion with the internal deadline |
| "Set once the sponsor date is known" | "Not available: no sponsor date" | Shorter |
| "Send alert" in dummy mode | "Log alert (nothing is emailed)" | Honest about what the button does |
| "Held back: Rated Low. Shown here so a quiet omission is still a visible decision." | "Not in the draft: rated Low. Listed here so that leaving them out is your choice." | Plain |
| Footer | Keep: "FORGE SIGNAL · capstone project, SMU Cox MS in AI in Business … not an approved or endorsed university service." | Required framing |

### 5.5 Things not to add
No "AI accuracy", "match score as a percentage", "saves X hours", "fast" or "instant". The only numbers on pages should be counts from the run, dates computed by code, and run IDs.

---

## 6. Wireframe-level sketches

HTML version with annotations: `docs/ux/wireframes.html`. Text summaries:

**W1 · Match: status stays where the person is looking** (M1, M5)
```
+---------------------------------------+ +-----------------------------+
| What are you starting from? (radios)  | | This run                    |
| Researcher                            | |  window / lead time / etc.  |
|  Name (required)  [______________]    | |  [ Screen opportunities ]   |
|   ! Enter the researcher's name.      | |  ! Two things need fixing   |
|  Research areas (required)            | |  -- or while running --     |
|  [ one per line ...              ]    | |  Screening in progress 1:12 |
|   ! Enter at least one area.          | |  It can take longer when   |
|  [Use the sample researcher] (sample) | |  several people search at   |
+---------------------------------------+ |  once. Keep this tab open.  |
                                          +-----------------------------+
                                          | Runs are logged. Public and |
                                          | private data only.          |
```
Status is in a `role="status"` region (announced at start and every 30 s). No ticks.

**W2 · Result card: summary first, evidence on request** (S1, S3)
```
[ Title (link to sponsor page) ]
Agency · Call ID · Sponsor deadline Jan 10, 2027 (47 days)
[High · Very strong fit] [Eligibility: Needs verification] [Limited submission]
One-sentence rationale.
+- YOUR CHECK (red edge) ------------------------------------------------+
| The announcement does not say who may apply. Read the eligibility      |
| section on the sponsor page, or ask the program officer. [Open page]   |
+------------------------------------------------------------------------+
> Evidence (3 quotes, all found in the sources)    > How this fit was calculated
```

**W3 · Confirm the researcher's profile** (L2; usable now with pasted areas)
```
Researcher > [Confirm profile] > Screen > Review
Proposed research areas for Dr. Sample Person (fictional)
[x] Photochemistry and flavin chemistry   "..." (publication record, retrieved)
[x] Protein dynamics                       "..." (faculty page)
[ ] Cancer biology  (one paper only)       "..." (publication record)
+ Add an area in the researcher's own words
Career stage [Not stated]   Positioning rules [..]
[ ] I have checked these areas and they describe this researcher's established work.
[ Screen opportunities ]  (disabled until ticked and one area kept)
```

---

## 7. Suggested order of work and what I need from you

1. Approve or trim section 3.1. My recommendation: do **M1, M2, M3, M5** first (about 7 h), then M4, M6 to M8, then M9 only if time remains.
2. Decide whether the Dec 2 demo runs on a public URL. If yes, S8 (Settings in the public nav) moves up and the hosting note in 2.2 applies now.
3. Confirm that informal usability sessions on Dec 2 to 4 need no further review.
4. Tell me the daily cap you want for live testing in T2.

No code, backend setting or branch other than this working branch was changed. The one local thing I did beyond writing these files was run the backend on port 8000 with the mock model and a throwaway SQLite file in a scratch folder, then stop it.
