# FORGE SIGNAL: product, brand and UX diagnosis, and recommended direction

Status: **for your review. Nothing in the product has been changed.** Implementation starts only after you approve (section E).
Date: 25 Nov 2026. Builds on `docs/UX_IMPROVEMENT_PLAN.md` (detailed page-by-page findings, WCAG check, test script, wireframes). This document adds the brand, positioning and conversion view and turns both into one design direction. Finding IDs like M1 or S2 refer to that plan.

Evidence base: the code in `public/signal/`, the brand files in `public/brand/`, `docs/REDESIGN.md`, `docs/PRD_v0.2.md`, `docs/SIGNAL_BOUNDARIES.md`, and screenshots I took of every page in sample and live mode. I have not tested with real users, so statements about what users "will" do are hypotheses to check on Dec 2 to 4.

Constraints I am holding: nothing the product cannot support (no accuracy figures, no speed promises, no invented testimonials or customers, no pricing); the AI/human boundary stays visible; the "class capstone project, not an approved or endorsed university service" framing stays; public and private data only.

---

## A. Product and brand diagnosis

### A1. Positioning

| Question | What I found | Verdict |
|---|---|---|
| Who is it for? | The only audience cue on Home is the small eyebrow "Research development". The body says "a researcher's established work". A visitor does not learn that it is for research development offices and grant consultants. | **Weak** |
| What problem? | Home says "Too many announcements, too little time", and "the burden is vigilance". Accurate, but generic: every funding tool says it. | **Generic** |
| Value in 5 seconds? | Headline: "Find the right funding signal". "Signal" is the product name used as an abstract noun; it does not say what you get. The strongest idea, "the sentence behind every claim", is in the third line of the lead paragraph. | **Not obvious** |
| Differentiator | Real and unusual: every judgment quotes a sentence; a validator rejects quotes not in the source; the rating is calculated by code, not chosen by the model; eligibility is never guessed; a person decides and nothing is sent. This is the product. It sits in the third section of Home ("What you can rely on") and the two red steps in the flow. | **Strong but buried** |
| Messaging that is vague or confusing | "Match" (nav and button) is internal jargon; a first-time visitor would say "find funding". "Screen opportunities" is fine. "Step 1 of 3" labels Match, Results, Calendar, but the two human steps (Review, Alert) sit outside the count, so the product's key idea is not in the journey it shows. "Decide now" can read as the tool telling someone what to do. "Fit" is explained in the notice, not at first use. | **Fix** |

### A2. Brand

| Element | Finding |
|---|---|
| Name and identity | "FORGE SIGNAL": a text wordmark (letter-spaced "FORGE" with "SIGNAL" underneath) in the header. The FORGE logo system from `docs/REDESIGN.md` (the F built from Trust Blue and coral strokes) exists in `public/brand/` but is **not used** on any SIGNAL page. The two files in `public/signal/assets/` (`logo-light.svg`, `logo-dark.svg`) are an older orange concentric-arc mark in `#F28C28`, are referenced by no page, and use a different orange from Forge Coral `#E98262`. Two logos and two oranges are in the repo. |
| Personality | Content voice is precise, calm and accountable ("Nothing is asserted without a source", "Fit is never a percentage"). That is the right personality for a tool that supports research compliance. Visual voice does not yet match it: a full-width coral banner and a navy hero repeat on every page, so tool pages look like landing pages. |
| Colour | A sound palette: Trust Blue `#244B70`, navy `#0d2238`, Forge Coral `#E98262` as accent, warm neutral and soft blue grounds, one meaning colour for human decisions (`--human` red `#b3112b`), green/amber/grey for fit. Good rules already exist (coral is accent only; small coral text uses coral-ink). Weak points: red for "human decision" and red for "stop/error" are close in hue; coral is used for the banner, buttons, eyebrow rules, quote edges and the focus ring, so it carries no single meaning. |
| Typography | Three families: Sora (headings), Inter (body), IBM Plex Mono for eyebrows, badges, counters, IDs. Mono in **badges** ("High · Very strong fit", "Eligibility: Needs verification") makes the most important words on the page the hardest to read at 12 px. Many supporting lines are 13 px muted grey (hints, meta, quote sources). |
| Imagery | One 21 s explainer video with no audio, showing generic document windows and the tagline "Too many opportunities. Too little time." Its caption text is low contrast on the poster. It repeats the generic problem framing rather than showing the product. No product screenshot appears anywhere on Home. |
| Iconography | None, apart from numbered circles and text glyphs. That is fine and in keeping with "clarity over decoration"; badges already use words. Not a problem to fix. |
| Tone of voice | Mostly strong. Inconsistencies: sample mode promises "under 30 seconds" (unsupportable); "Screening finished. 0 opportunities to review." with no explanation; "Held back… so a quiet omission is still a visible decision" is clever and hard to parse. |
| Credibility signals | Present and unusually honest: boundaries, the "not an approved or endorsed university service" footer, run logging notice, quote with retrieval date and official link, "How this fit was calculated". Missing: a visible "who built this and why" (capstone, SMU Cox MS in AI in Business, supervised by whom), the date sources were last read on every page, and the run ID. |
| Consistency | The seven pages share one stylesheet, so basic consistency is good. The inconsistency is structural: the logo system, the text wordmark and the unused orange logo coexist; every page has the same 300 to 370 px hero regardless of purpose; spacing is partly set inline (dozens of `style="margin-top:…"` attributes across the HTML) rather than from a scale. |

### A3. What is working, weak and missing (one view)
**Working:** the idea and its honesty; the red "human decision" step marking; the palette and AA-aware tokens; badges with words; the "How this fit was calculated" disclosure; "Decide now" first on the Calendar; the Review page's coverage panel and confirmation tick; plain, accountable copy on most screens.
**Weak:** a headline that does not say what you get; the differentiator below the fold; tool pages dressed as landing pages; mono badges; density of Results and Calendar; status hidden off screen; a fictional person pre-filled into live runs.
**Missing:** a named audience; a no-wait path to value (a sample result you can open without running); the FORGE logo; a path from "I tried it" to "I will tell you what I thought" (tester feedback); honest zero, error and waiting states; a design-system page so the next screen is built from parts.

---

## B. UX and UI audit, prioritised

Full detail, screenshots and fixes are in `docs/UX_IMPROVEMENT_PLAN.md`; this is the cross-cutting ranking.

### Critical (misleads, blocks, or breaks the product's own rules)
| # | Finding | Why it matters | Recommendation |
|---|---|---|---|
| 1 | Run status and validation errors render ~600 px below the button, off screen (Match) | A failed click looks like nothing happened; people abandon or click repeatedly. The wait is the most anxious moment in the journey. | Put status and errors in the "This run" card under the button; announce with `role="status"`. (M1, M5) |
| 2 | Fictional researcher pre-filled in live mode; the draft greets "Dear Dr. R. Alvarez (fictional)" | Puts invented data into a real run and a real message, against the "a person owns every outward message" rule. | Empty fields in live mode; "Use the sample researcher" button in sample mode only. (M2) |
| 3 | Zero-result, no-run and nothing-to-send states are wrong or empty (Results, Calendar, Review) | A first live run that finds nothing is likely (the mock run did). The product then says "remove a filter" when there is none, shows a stale sample timestamp, and lets an empty alert be logged. That ends the trial. | Distinct states with counts and next steps. (M3, M4) |
| 4 | Step ticks claim progress the server does not report; "under 30 seconds" copy | Breaks the product's own promise of not asserting what it cannot support. | Elapsed timer and honest range, no ticks. (M5) |

### High impact
| # | Finding | Why it matters | Recommendation |
|---|---|---|---|
| 5 | Headline and audience do not state the value; differentiator is buried | Visitors decide in seconds. A tester arriving from a link needs to see "for research development" and "see the sentence that proves it". | Rewrite the hero (section C6); move "What you can rely on" up as the second section. |
| 6 | Journey shows three steps but the human steps (Review, Alert) are outside it | The core idea (AI proposes, a person decides) is not in the navigation. | Show four steps: Match, Results, Calendar, **Review (you decide)**; mark the human step with the existing red. |
| 7 | Results card density; "Needs verification" unexplained per card | Scanning 7 to 25 cards is the main work; eligibility is mostly "Needs verification", so the unexplained badge repeats on nearly every card. | Summary first, evidence on request, one "Your check" line per card. (S1, S3, M8) |
| 8 | Calendar's two decision columns are off screen; no "passed" label for a missed internal date | The calendar is the deliverable people will export and diary. | Reorder columns, sticky first column, "(passed)". (S2) |
| 9 | Tool pages carry a full marketing hero (7 of 7 pages) | The first screen on Match, Review and Settings is a title and an empty right half; the form starts below. | Heroes only on Home and About; tool pages get a compact page header (S4). |
| 10 | Accessibility gaps: focus ring 2.68:1 on white, input border 2.22:1, hint 2.8:1, 6 axe findings, unlabeled result articles, 320 px overflow | WCAG 2.2 AA is the stated standard and SMU's guidance is 2.1 AA. | M9 and S5 in the plan. |

### Medium impact
| # | Finding | Recommendation |
|---|---|---|
| 11 | "Match" jargon in nav and primary button | "Find funding" as the nav label for the first step; keep "Screen opportunities" for the action. |
| 12 | Mono used for badges, eyebrows, counters, IDs | Keep mono only for IDs, call numbers and timestamps; badges in Inter semibold 13 to 14 px. |
| 13 | Spacing set by inline styles; no scale | Introduce a 4/8 px spacing scale as CSS variables and utility classes; remove inline `style` attributes. |
| 14 | Settings link visible to every visitor; dead buttons | Hide or label "Admin (preview, not connected)". (S8) |
| 15 | Video: no audio, no text alternative, generic frames | Replace with a product screenshot or a short annotated result card; keep the video only if it shows the product. Provide a transcript. (S7) |
| 16 | No tester feedback path | Footer link with the run ID; say what is shared. (S10) |
| 17 | Coral does too many jobs | Reserve coral for the primary accent button and the brand mark; use blue for focus, links and quote edges; keep red only for human decisions and a distinct darker red-brown for errors. |

### Polish
Auto-size the research-areas textarea; "Days to sponsor deadline" instead of "Days left"; counters bar spacing in live mode; "(passed)" on past internal deadlines; the disabled unit option shown as "Coming later"; the three problem cards on Home can lose their card borders (text only); consistent date format (the sample uses both "24 Nov 2026" and "Nov 24, 2026").

### Conversion and activation view
The product has no pricing, upgrade or sign-up, and should not invent any. The relevant funnel is: **arrive → understand → run → believe the first result → export or draft → give feedback**. Where it leaks:
1. *Understand:* no audience, abstract headline. Fix with copy (C6).
2. *Run:* the first step needs a researcher's name and research areas, which the visitor may not have to hand; the only route to see value without that is the sample (hidden in live mode). **Add "See a sample result" on Home and Match that opens the fictional run, labelled as sample.** This is the single best activation move and costs little.
3. *Wait:* off-screen status and an unsupported speed promise (Critical 1 and 4).
4. *Believe:* zero or all-"Needs verification" results with no explanation (Critical 3, High 7).
5. *Act:* the Review page works but says "Send alert" in dummy mode.
6. *Feedback:* no path (Medium 16).
Trust signals I recommend, all true and verifiable: the validator and "N quotes checked, N found" counts per run; source and retrieval date on every page; run ID; the boundary list; "who built this". Social proof: none exists yet; do not invent it. After Dec 2 to 4, one honest line from the testers' feedback can be added only with their permission.

### Where am I? What can I do? Why does it matter? What next?
| Screen | Where | Do | Why | Next | Gap |
|---|---|---|---|---|---|
| Home | clear | Start | weak (generic) | clear | add audience and value, sample path |
| Match | "Step 1 of 3" | clear | stated | status off screen | M1 |
| Results | "Step 2 of 3" | filter, read | notice present | "Open the calendar" but also Review | zero state; per-card next step |
| Calendar | "Step 3 of 3" | export | clear | "Draft an alert" | blank states; hidden columns |
| Review | "Human review" | edit, confirm | strong | confirm tick | empty alert possible; button wording |
| About | clear | read | strong | none | add a path back to Match |
| Settings | clear | edit | clear | none | dead buttons |

---

## C. Recommended design direction

### C1. Principles
1. **Show the source.** The signature element of the interface is the quote with its source and retrieval date. It gets one consistent component, used the same way on Results, Calendar and Review.
2. **A person decides, and the interface shows where.** Human-decision points get one visual signal everywhere (the existing red edge, label "Your check" or "You decide"). Machine-produced content never uses it.
3. **Say what we do not know.** Missing, unverified and failed items are shown in plain words, never hidden or smoothed over.
4. **Tool surfaces are not landing pages.** Marketing surfaces (Home, About) can have a hero; task surfaces (Match, Results, Calendar, Review, Settings) have a compact header and put the work on the first screen.
5. **One thing per screen.** Each screen has one primary action and one sentence of why.

### C2. Brand personality
Precise, calm, accountable, plain-spoken. Not "AI-powered", not "revolutionary", not clever. It sounds like a careful colleague who shows their workings.

### C3. Colour system (keep the palette; tighten the roles)
| Role | Colour | Use |
|---|---|---|
| Brand and action | Trust Blue `#244B70` / deep `#1B3A58` | Primary buttons, links, headings, **focus ring** (with a white inner ring) |
| Ground | Warm `#F3F4F2`, white, Soft Blue `#EFF4F8`, navy `#0d2238` (Home and About hero only) | Page, cards, panels |
| Accent | Forge Coral `#E98262` | The logo mark, the one accent button per page, eyebrow rules. Not focus, not quote edges. Coral-ink `#A4441F` for small coral text |
| Human decision | `--human` plum `#4B3A8C` (no red) | Only "Your check", "You decide", and the human steps |
| Rating | green / amber / grey (existing badges) | High / Medium / Low, always with words |
| Error | brown `#6B3A0F` on `#F3EADF` (`--stop`; no red) | Errors only; text always accompanies |
| Neutral text | Slate `#344452`, muted `#566878` (5.2:1) | Body and secondary; no text lighter than muted |
Retire `#F28C28` and the old orange logo files.

### C4. Typography
Sora for headings (as now). Inter for body, UI and **badges**. IBM Plex Mono only for call IDs, run IDs, timestamps. Scale (rem, 16 px root): 12 (counter labels only), 14 (hints, meta, table), 16 (body), 18, 22, 28, 36 (Home hero only). Minimum 14 px for anything a person must read to decide. Line length 68 characters for prose. Sentence case everywhere; drop the all-caps letter-spaced eyebrows on tool pages.

### C5. Layout, components and rules
- **Spacing:** 4 px base; named steps 4, 8, 12, 16, 24, 32, 48, 64. No inline margins.
- **Page header (new shared component):** compact (title, one-line purpose, step indicator, primary action) on tool pages; hero kept on Home and About.
- **Step indicator (new):** four steps, Match, Results, Calendar, Review, with Review in the human colour; current step marked with text and `aria-current`.
- **Buttons:** primary (blue, one per view), secondary (outline), accent (coral, one at most per page), and a text link style. Minimum 44 px high for primary, 24 px target minimum everywhere (WCAG 2.2). Disabled buttons say why.
- **Cards:** radius 8 px (down from 10 to 14), one border, no shadows except on raised panels; no card-inside-card.
- **Badges:** Inter 13 px semibold; word first. Fit, Eligibility and Status share one structure and differ by label, not by shape.
- **Evidence block (new shared component):** `figure > blockquote + figcaption`: label, quote, source link (named with the call ID) and retrieval date. Collapsed by default on Results.
- **Tables:** sticky header and first column; core columns first; row-stack under 760 px with preserved table roles.
- **Forms:** visible label, required marker, hint, error text with `aria-describedby`; inline error next to the field plus a summary near the button.
- **Status and empty states:** one component with a title, a reason, and next steps (section 5 of the UX plan holds the wording).
- **Focus:** 2 px white inner ring plus 3 px blue outer ring on every surface; never removed.
- **Motion:** none beyond a 150 ms state change; honours `prefers-reduced-motion`; no auto-playing media.
- **Navigation:** Home, Find funding, Results, Calendar, Review, About; Settings only for admin. Header carries the FORGE logo (from `public/brand/`) with "SIGNAL" as the product name.

### C6. Messaging approach
Say who it is for, what you get, and how you can check it, in that order.
| Element | Current | Proposed (for your approval) |
|---|---|---|
| Eyebrow | Research development | For research development offices and grant consultants |
| Headline | Find the right funding signal | **Find funding that fits a researcher, and see the sentence that proves it.** (alt: "Funding screening you can check line by line.") |
| Lead | SIGNAL reads current funding announcements, screens them against a researcher's established work, and shows the sentence behind every claim. It builds a deadline calendar and drafts an alert. A person decides what goes out. | SIGNAL reads current federal funding announcements and screens them against the research areas you confirm. Every judgment quotes the announcement. You review the evidence, then decide what goes out. Nothing is sent without you. |
| Primary CTA | Start a match | Screen for a researcher |
| Secondary CTA | What it is and is not | See a sample result (opens the clearly labelled fictional run) |
| Section order | Problem, How it works, Rely on | Rely on (how you can check it), How it works, then the problem as one short line |
| Feature to benefit | "Every claim carries its source" | "Check any claim in one click: the quote, the sponsor page and the date it was read." |
| Benefit lines (all true today) | – | "Eligibility is never guessed: if the announcement is silent, you see 'Needs verification' and what to check." / "Ratings are calculated from a published rubric, not chosen by the model." / "Deadlines are computed by code; a missing date stays missing." |
| Trust strip under the hero | – | "Capstone project, SMU Cox MS in AI in Business · Public Grants.gov data · Not an approved or endorsed university service" |
No percentages, no "fast", no "saves hours", no testimonials, no pricing.

### C7. Accessibility standard
Design toward WCAG 2.2 AA: contrast (text 4.5:1, UI and focus 3:1), visible focus not obscured by sticky headers, 24 px minimum targets, keyboard-only completion of every flow, labels and errors tied to fields, status announced, reflow at 320 px, 200 percent zoom, reduced motion, readable type. A real screen-reader pass is a human task (UX plan, 2.2). As flagged once already in the UX plan: if this is hosted for others, SMU's guidance also covers SSO, data protection, hosting, maintenance and ownership; run the `app-hosting-self-review` skill before contacting OIT.

---

## D. Implementation plan (for approval)

Order follows your instruction: design system, then layout and navigation, then the highest-value journey, then secondary screens. Everything preserves current behaviour and data logic; only M-items below change logic, and only for UX reasons.

| Phase | What | Files | Effort (h) | Risk |
|---|---|---|---|---|
| **1. Design system** | Tokens: spacing scale, type scale, focus ring, input border, retire orange; shared component CSS for buttons, badges (Inter), cards (8 px), evidence block, status block, empty state, page header, step indicator, table; remove inline `style` attributes into utility classes; a `design-system.html` reference page listing each component and its states | `public/signal/app.css`; all `*.html` (inline styles); new `public/signal/design-system.html` | 6 to 8 | Low to medium (visual regressions: check each page at 1440, 768, 390, 320) |
| **2. Layout and navigation** | FORGE logo in header; banner moved into header and quieter; compact page header on tool pages; four-step indicator with Review as the human step; nav label "Find funding"; Settings hidden or labelled; footer unchanged in meaning | all `*.html`, `app.css`, `app.js` (step/"No run" hero handling) | 3 to 4 | Low |
| **3. Highest-value journey: Match → Results → Calendar → Review** | UX plan M1 to M8 (status where the person looks, empty fields, zero/no-run states, honest wait, DRAFT, run ID, key for Needs verification); then S1 to S3 (summary-first card, Calendar column order, "Your check" line) | `match.html`, `results.html`, `calendar.html`, `review.html`, `app.js`, `app.css` | 12 to 16 | Medium (touches rendering and form logic; test sample and live) |
| **4. Home and secondary** | New hero copy, section order, sample-result CTA, trust strip, video replaced or given a transcript; About path back to Match and "who built this"; Settings labelling | `index.html`, `about.html`, `settings.html`, `assets/` | 3 to 4 | Low |
| **5. Verification** | Re-run axe, keyboard walk, 320/640/1440 screenshots, live-mode check with the mock model; update `docs/ux/` | `docs/ux/` | 2 | – |

Total about 26 to 34 hours. The Dec 2 time budget is mostly claimed by backend speed, PI lookup and deployment, so I recommend:
- **Before Dec 2 (about 12 h):** Phase 1 tokens and focus only (about 3 h), Phase 2 header and logo only (about 1.5 h), then the plan's M1, M2, M3, M5 (about 7 h).
- **Dec 2 to 4:** the rest of Phase 3 as tester feedback shows what matters; Phase 4 copy.
- **After:** full component set and `design-system.html`; real screen-reader pass.

## E. Decisions I need from you before implementing

1. **Positioning:** are research development offices and grant consultants the right named audience, and is "Find funding that fits a researcher, and see the sentence that proves it." acceptable? (Or choose the alternative, or give me your words.)
2. **Logo:** use the FORGE logo from `public/brand/` in the SIGNAL header and retire the orange files? (Recommended.)
3. **Tool pages:** replace the large hero on Match, Results, Calendar, Review and Settings with a compact header? (Recommended.)
4. **Scope for Dec 2:** the 12-hour cut above, or something smaller?
5. **Settings link:** hide for public visitors, or leave it labelled "preview"?
6. **Sample result:** may Home offer "See a sample result" even in live mode (clearly labelled fictional)?

I will not change any file in `public/signal/` until you answer. If you say "approved" without detail, I will start with Phase 1 and Phase 2 as written, then the M-items.

---

## F. Status after approval (25 Nov 2026)

Approved: FORGE logo in the header, compact headers on task pages, Dec 2 scope, Settings kept as a preview. Added instructions: **no red** anywhere; keep the explainer video as a placeholder (a new one later); Settings as a small gear icon.
Decisions made without an explicit answer, easy to reverse: the proposed hero headline and audience line (question 1); "See a sample result" shown in sample mode only (question 6).
Implemented in `public/signal/` (see its README, "V1 design system"): tokens and components, header and logo, page headers and four-step indicator, Match status and validation, summary-first result cards with "Your check", zero/no-run states, Calendar column order and "(passed)", Review DRAFT marking and empty-alert guard, Home messaging, About "who built this", gear icon. Verified with axe-core on all seven pages (0 issues), no sideways scroll at 320 px, and live-mode flows with the mock model. Still open: real screen-reader pass, phone table roles (S6), video text alternative is a description only, the sidebar error on Match is announced but may sit below the fold when the field error is focused.

**Logo update (25 Nov 2026).** The owner supplied the real FORGE SIGNAL logo (orange signal arcs, `#F28C28`). It replaces the FORGE-only wordmark from `public/brand/` that was used first, and the orange logo files are not retired after all. The header, favicon and Home now use it as supplied, which also matches the placeholder video. Open question: the UI accent coral (`#E98262`) and the logo orange (`#F28C28`) are two different oranges; recommend choosing one.

**Logo redesign (V5, 25 Nov 2026).** The owner asked for the logo to be redesigned for the V4 palette. Concept: the F stays a stem and two arms, like lines of text, and the middle arm is red: the highlighted sentence, the product's idea. It also matches the F-with-an-accent-arm mark FORGE used before. FORGE is navy, SIGNAL is blue, the middle arm is red `#F04B4C`. Files in `public/signal/assets/`: `forge-signal-logo.svg` (horizontal, light backgrounds, used in the header), `forge-signal-logo-on-dark.svg`, `forge-signal-logo-stacked.svg`, `forge-signal-logo-stacked-on-dark.svg`, `forge-signal-icon.svg` (favicon tile). Letterforms are outlined from the supplied logo; the supplied orange logos are kept in `docs/brand-archive/`. A board showing all versions is `docs/ux/logo-v5-board.png`.
