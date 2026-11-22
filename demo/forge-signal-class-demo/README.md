# FORGE SIGNAL class demo

Standalone, no-build demo for the Generative AI class. Open `index.html` in a browser.

- Runs entirely in the browser on invented sample data (all records are marked SAMPLE).
- Live code: admin scope, verify gate, runway bands, deduplication, change log, quote-or-NOT-FOUND extraction, decision rule, guardrail checker, upload scanner.
- AI layer: the Ask SIGNAL panel calls a model through `window.claude.use("sample")` with a `search_passages` tool over the in-scope, verified corpus, then a Critic checks citations and language rules. That runtime exists only when the page is published as a Claude artifact; opened as a plain file it falls back to retrieval only.
- Stand-ins: the assessment extractor is rule-based; no live sponsor feed or sign-in.
- Live web retrieval from official sponsor sites needs a backend retrieval service (see the Agents and RAG tab).
- The Risk register tab maps 18 risks to controls and links each to the panel that demonstrates it.
- The Agents and RAG tab describes the agents and retrieval indexes that replace the stand-ins.

Preliminary screening only: not institutional approval, legal advice or a final eligibility determination.
Before wider use, review accessibility (WCAG 2.1 AA), SSO, data protection, hosting and ownership with SMU OIT.

## Links

Every record carries a program announcement link and a sponsor site link, labelled by BRD source tier (official domain, institutional, or a lead to verify). Sample records use `example.org` placeholders. Use "Add a record" to enter a real opportunity with real links; Verify stays disabled until an announcement link is on file.
