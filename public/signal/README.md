# FORGE SIGNAL interface

Static pages served at the site root by `.github/workflows/deploy.yml`. Scope: `docs/PRD_v0.2.md`.

| File | Page |
|---|---|
| `index.html` | Home: what SIGNAL is and is not |
| `match.html` | Start a run: input type, researcher profile, per-run settings, progress |
| `results.html` | Screened opportunities, quotes, "How this fit was calculated" |
| `calendar.html` | Deadline calendar grouped Fixed / Rolling / Watch, with exports |
| `review.html` | Draft alert, coverage panel, confirmation gate before sending |
| `about.html` | Scope, AI/human boundaries, how a rating is produced, data handling |
| `settings.html` | Administrator: scope, model switch, limits, email mode, criteria, run log |
| `app.css` | Design tokens (mirrors `lib/tokens.ts`) and components |
| `app.js` | Shared rendering; takes the API response shape from `backend/app/pipeline.py` |
| `mock-data.js` | **Fictional** sample run. Replaced by `fetch()` calls when wired. |

**Nothing here is connected yet.** Every figure is fictional sample data and the export and
send buttons are inactive. Wiring to the backend API is the next step.

Design carries forward the earlier SIGNAL build (git `55cca27`): navy hero with the explainer
video, alternating bands, the numbered flow that marks **human-decision steps** in `--human`, the
two-column comparison, the navy pull quote, and the Explorer's search-filter-chip interaction, now
on Results. Palette stays the PRD brand; contrast on the navy ground was measured, not assumed
(coral 6.01:1, body text 12.85:1, muted 8.82:1 — all pass AA; coral is 2.68:1 on white, so on light
grounds it is only ever coral-ink).

Accessibility is a build constraint, not a later pass: semantic landmarks, skip link, visible
focus, keyboard-operable disclosures and filter chips, a video control that respects
`prefers-reduced-motion`, and status never signalled by colour alone (every badge carries words).
Verified at 1280, 768 and 360px: no console errors, no horizontal scrolling, one `h1` per page,
every control labelled, no dead links.

The earlier prototype (Workbench, Prompt Builder, Explorer) was removed per decision D2 in the PRD.

## V1 design system (25 Nov 2026)
Direction and rationale: `docs/BRAND_UX_DIAGNOSIS_AND_DIRECTION.md`; page-by-page findings and test script: `docs/UX_IMPROVEMENT_PLAN.md`.
- The supplied FORGE SIGNAL logo (orange signal arcs) is used as supplied: `assets/forge-signal-logo-white.svg` in the header and `-navy.svg` for light grounds; `-dark-bg` and `-light-bg` are the original files with backgrounds; `forge-signal-icon.svg` is the arcs only, used as the favicon. Transparent versions only have their empty margin cropped.
- Colour roles: Trust Blue for action and focus; coral for one accent button (the logo keeps its own orange, #F28C28; the two oranges should be unified later); plum (`--human`) only where a person decides; brown (`--stop`) for errors. No red.
- Task pages use `.pagehead` and a four-step indicator; only Home and About use `.hero`.
- Shared components: `.status` (wait, error, none), `details.evidence`, `.yourcheck`, `.steps4`, spacing scale `--s1`..`--s8` and `.mt1`..`.mb3` utilities instead of inline styles.
- Settings is a small gear icon in the header (admin preview).
- The Home explainer video is a placeholder; a new one will replace it.
