# FORGE SIGNAL (class website)
Static two-page site: `index.html` (video hero, Signal Explorer X-Factor, chatbot) and `about.html` (project details, chatbot).
The chatbot is the Chatling bot `6621135586` (same as the travel chatbot), loaded by `chat.js`. In Chatling, allow the Pages domain.
Self-contained with relative paths: it can be served from any folder or copied to its own repo root and enabled in Settings > Pages.

## Workbench prototype (branch `claude/signal-interface-prototype`)
`app.html` + `app.js`: browser-only workbench with a faculty profile registry (Verified/Unverified/Stale), opportunity fact sheets, rubric-based screening in both directions (opportunity to faculty, faculty to opportunities), draft chair email, AI verification prompt and `.ics` calendar. Data lives in localStorage; JSON export/import. Matching is stemmed keyword overlap on quoted text only: High needs a Verified profile, 2+ shared terms and confirmed-clear eligibility. Sample records are fictional. No backend and no AI calls.

Boundaries (from the 2026 SMU Technology Showcase slide) are in `docs/SIGNAL_BOUNDARIES.md` and summarized in the Workbench.
