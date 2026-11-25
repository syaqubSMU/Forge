# FORGE SIGNAL: Branch and integration flow

Status: in force. Proposed by the architect session; the owner's approval rule below was added on 25 Nov 2026 at the owner's direction. (Original note: Today all three sessions commit to `claude/practical-franklin-ze9hk2`, so a proposal and an approval cannot be separated: whatever is committed is already "published" on the shared branch.)

## Approval rule (owner, 25 Nov 2026)
The owner is the customer, admin, super user and system owner of FORGE SIGNAL.

**Nothing is committed to the project line on GitHub (`integration` or `main`) unless all three hold:**
1. the **project manager approves**;
2. the **owner approves**;
3. the change **aligns with the business documents**: `docs/PRD_v0.2.md`, `docs/ARCHITECTURE.md` (including DR-8, DR-9 and its open-window amendment), `docs/SIGNAL_BOUNDARIES.md`, the brand and UX direction documents, `docs/brand/logo-final/LOGO_USAGE.md`, and the course rubric the capstone is graded on.

The architect's review stays in the flow and is how technical and design alignment is checked first. UI/UX work goes through the project manager and the architect before it reaches the owner, so the owner's decisions are aligned with the overall design and any adjustment is found early.

**All sessions (UI/UX, engineer, architect) may work on their own branches and test branches. Only the project manager merges into `integration` or `main`, and only when the three conditions above hold.** Branches pushed for review are proposals.

Every proposal carries an **alignment note**: the decisions and documents it follows, any deviation or document change needed, what was tested and what was not, and in plain words what the owner is asked to approve.

## Branches
| Branch | Owner | Rule |
|---|---|---|
| `main` | project manager | Deployed to GitHub Pages and production. Updated only by the project manager, only from `integration`, only after the owner-visible checks pass and the approval rule above is met. |
| `integration` | project manager | Approved work only. Tests must pass here (SQLite and Postgres) before anything moves to `main`. |
| `feat/backend-<topic>` | engineer | Backend work. Touches `backend/` only. |
| `feat/ux-<topic>` | UI/UX session | Touches `public/signal/` and UX docs only. |
| `docs/architect-<topic>` | architect | Documents only. |

Start each topic branch from the current `integration`. One topic per branch, small, short-lived. Retire `claude/practical-franklin-ze9hk2` after its contents are triaged (below).

## Flow for one change
1. Proposer works on its own branch and **pushes the branch, not integration**. The proposal message names the branch and commit ids, the files, why, tests run (SQLite and Postgres counts), measured results and risks.
2. Architect reviews design and technical soundness and replies `APPROVED`, `APPROVED WITH CONDITIONS`, or `CHANGES REQUESTED`, copying the project manager.
3. Project manager reviews scope, schedule, risk and cost and replies the same way.
4. Only when both have sent `APPROVED <id>`, **the owner has approved, and the change aligns with the business documents** does the project manager merge the branch into `integration` (squash or merge commit, with the approval ids in the message). Conditions must be met first or recorded as tracked follow-ups with an owner and date.
5. The project manager runs the full tests on `integration`, then, with the owner's approval of the release, updates `main`. Nobody else touches `main` or `integration`.
6. Proposers rebase their next branch on `integration`.

## Rules
- A session whose environment assigns it a fixed branch must still not push to the shared branch; it tells the project manager instead and the project manager decides.
- A change that touches two areas (for example an API field and the page that reads it) is two commits on two branches, merged in the order API first, and the contract (field names, example response) is written in the proposal.
- Anything touching accounts, spending, secrets, environment settings or deleting data goes to the project owner through the project manager, before merge.
- Do not push build artefacts or large images; screenshots belong in one folder with a size budget (docs/ux is already 19 MB of the 21 MB repository).
- Commit messages carry the approval ids.

## Current state (25 Nov 2026)
`integration` was created at 2684f33 (baseline ca51468 plus these two documents); it is now at da43450 after the PRD wording and the approved backend (P1 to P5) were merged. The project owner agreed to this flow. Base every new branch, documents included, on `integration`, never on the shared branch (a branch based on the shared tip carries its unapproved commits into any merge). The project manager does not delete or rewrite the shared branch.

## Triage of the shared branch `claude/practical-franklin-ze9hk2`
Treat it as submitted work, not as approved. Status as of 25 Nov (PM = project manager):

| Commit | What | Architect | PM | Move to `integration` |
|---|---|---|---|---|
| ca51468 and earlier | Work before the approval process | not reviewed individually | n/a | Done: it is the baseline of `integration` |
| ae247ff | UX plan, screenshots, wireframes | changes requested (wording "one at a time", docs/ux size) | accepted | Not yet. Waiting for the resubmission: "one at a time" wording removed, docs/ux compressed, then re-review |
| e5447f0 | Brand and UX diagnosis | changes requested (same) | accepted | Not yet: after re-review |
| bf68bba | V1 design system implementation | changes requested (503 message, "one at a time", message when all model calls fail; browser test of live mode) | accepted out-of-scope work | Not yet. Waiting for the resubmission: 503 messages, the message when every model call fails (the API now returns 502 with two messages), the no-term-overlap count, the OpenAlex name disclosure and confirm step, no run-time promise in copy, a live-mode browser test, then re-review. My scan of the pages found 0 axe violations |
| e5887fc | Logo assets | as bf68bba | accepted | Not yet: with bf68bba |
| 46fc710 to 104a092 (clean branch `claude/forge-backend-review`) | Backend: parallel judging (P1), BM25 retrieval (P2), OpenAlex lookup (P3), migrations (P4), cost logging (P5), request limits, proxy setting, 32-hex run ids, README and db.py wording | APPROVED 104a092 after two review rounds | approved | Done: merged as da43450 (backend/ and docs/BACKEND_DECISIONS.md only) |
| db17872, 6c5cff9 (old shared-branch copies) | The same P1 and P2 as first submitted | superseded by the clean branch | superseded | Not needed: stay behind on the shared branch |
| 815328f (on `claude/forge-backend-work`) | First P3 | superseded by the clean branch | superseded | Not needed |

Unapproved commits stay behind with the requested changes. Update this table in each proposal message.
