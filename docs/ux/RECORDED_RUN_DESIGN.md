# Recorded run versus live run: design (design only, not built)

Status: proposal for the architect and project manager, written to `docs/ARCHITECTURE.md` DR-8 as relayed on 25 Nov 2026. Nothing here is wired.

## The two modes
- **Recorded example:** one real run on public Grants.gov data with a fictional researcher, shown as the default pages. Nothing is logged and no model is called.
- **Live run:** a real search. Limited to named testers or the owner, behind an explicit switch (mechanism open; see below).

## 1. The label: top of every page that shows a recording, never only in the footer
A full-width bar directly under the header, on Find funding, Results, Calendar and Review:

> **Recorded example.** A real run made on [date and time], model [name], opportunities as retrieved [date], rubric [version]. Not live. Not your input. Run [id].

Visually the same weight as the current "Preview" bar, in the navy of the site, plain text. It is not dismissible.

## 2. The input shown is the input that made the recording
On Find funding in recorded mode:
- The researcher name, research areas and options are shown filled in with the recorded input, **read-only** (visibly so, not just greyed), under the heading "The input for this recorded example".
- The main button reads **See the recorded example** and opens Results. It does not claim to search.
- Beside it: **Live searches are limited.** [Why?] opens a short explanation (below).
- If a visitor tries to edit, the explanation appears: *"This example was recorded from one fixed input. To search for something else you need live access. Live searches are limited to keep this preview free."* The recorded result is never presented as the answer to anything they typed.

```
+-- Recorded example. A real run made on [date], model [name], ... Not live. -----+
Find funding for a researcher
 The input for this recorded example          (read-only)
  Name: Dr. Sample Person (fictional)
  Research areas: ...
 [ See the recorded example ]   Live searches are limited.  [Why?]
```

## 3. Deadline flags are as of the recording
"Days to deadline", "Closing soon", "(passed)" are computed as of the recording date, and the page says so: *"Deadlines are shown as of [recording date]."* If today is later than any deadline in the recording, the page adds, above the table: *"Some deadlines in this recording have now passed."* and marks those rows "passed since recording". The Calendar's "Needs a decision now" list says "as of [date]" in its heading line.

## 4. The researcher is fictional
Every page with a recording states "(fictional)" next to the name. The page never describes a named person as "non-competitive" or similar. The rating wording is unchanged: High, Medium, Low, with the reason.

## 5. A recording is a demonstration, not evidence
Copy near the label or on Results: *"This is one recorded run. It shows how SIGNAL presents a result; it is not a measure of accuracy, speed or cost."* No timing, no accuracy, no cost figure anywhere on a recorded page.

## 6. What does not appear on a recorded page
The notice "Runs are logged" and any statement that inputs are stored: **nothing is logged on the recorded view.** The notice stays on live pages (Find funding in live mode, Home only if live is possible there).

## 7. The demonstration says which parts are live
On the Dec 6 demo, the label bar states recorded or live on every page. A small "What is live and what is recorded" line on About lists: researcher lookup (live or off), search (recorded by default, live behind the switch), calendar and draft (computed from whichever run is shown), export (works on a live run; off on the recorded view unless the engineer enables it).

## When live runs are limited or off
A visitor who asks for a live run sees, in the same place the button would be:

> **Live searches are limited.** They use a paid model and are kept for named testers. You can explore the recorded example, or ask the project owner for access.

- No error styling: this is expected, not a failure.
- The button for the recorded example stays active.
- If the switch is on for a tester, the label bar changes to **Live run** and shows the live counts.

## Status after build: how live runs are limited
The proposed wording above was replaced by what is built. When live runs need an access code, or the open demo window has a daily limit, the Find funding page shows the access card and the states described in `docs/UX_IMPROVEMENT_PLAN.md` section 5.6 (no code needed, entry, problem, accepted, no live runs left, search not started, with the public-cap and reserved-budget variants). Those states use the server's own message word for word, and each one has a button to the recorded example. The recorded view itself (label bar, read-only input, deadlines counted from the recording date, no cost or timing or "runs are logged" text) is as in sections 1 to 7 and is built.

## The switch (open)
How a tester turns live mode on is the architect's decision. The page needs one thing from it: a visible state ("Recorded" or "Live") and a plain way to see which one is active. Candidate for the UI: a small segmented control in the label bar, "Recorded | Live", where Live is disabled with the explanation above unless the tester is allowed.

## What needs code (when approved)
`config.js` and the `/config.js` response would carry the mode; `app.js` reads it and switches the label bar, the read-only input, the button and the deadline "as of" handling; the sample data file is replaced by the recording. The Settings page keeps the cost and model details (the estimate from `counters.cost_usd`, labelled as an estimate), which are not shown to visitors.
