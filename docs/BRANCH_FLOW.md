# FORGE SIGNAL: Branch and integration flow (proposal)

Status: PROPOSED by the architect session for project manager approval. Today all three sessions commit to `claude/practical-franklin-ze9hk2`, so a proposal and an approval cannot be separated: whatever is committed is already "published" on the shared branch.

## Branches
| Branch | Owner | Rule |
|---|---|---|
| `main` | project manager | Deployed to GitHub Pages and production. Updated only by the project manager, only from `integration`, only after the owner-visible checks pass. |
| `integration` | project manager | Approved work only. Tests must pass here (SQLite and Postgres) before anything moves to `main`. |
| `feat/backend-<topic>` | engineer | Backend work. Touches `backend/` only. |
| `feat/ux-<topic>` | UI/UX session | Touches `public/signal/` and UX docs only. |
| `docs/architect-<topic>` | architect | Documents only. |

Start each topic branch from the current `integration`. One topic per branch, small, short-lived. Retire `claude/practical-franklin-ze9hk2` after its contents are triaged (below).

## Flow for one change
1. Proposer works on its own branch and **pushes the branch, not integration**. The proposal message names the branch and commit ids, the files, why, tests run (SQLite and Postgres counts), measured results and risks.
2. Architect reviews design and technical soundness and replies `APPROVED`, `APPROVED WITH CONDITIONS`, or `CHANGES REQUESTED`, copying the project manager.
3. Project manager reviews scope, schedule, risk and cost and replies the same way.
4. Only when both have sent `APPROVED <id>` does the project manager merge the branch into `integration` (squash or merge commit, with the two approval ids in the message). Conditions must be met first or recorded as tracked follow-ups with an owner and date.
5. The project manager runs the full tests on `integration`, then fast-forwards `main` for a release. Nobody else touches `main` or `integration`.
6. Proposers rebase their next branch on `integration`.

## Rules
- A session whose environment assigns it a fixed branch must still not push to the shared branch; it tells the project manager instead and the project manager decides.
- A change that touches two areas (for example an API field and the page that reads it) is two commits on two branches, merged in the order API first, and the contract (field names, example response) is written in the proposal.
- Anything touching accounts, spending, secrets, environment settings or deleting data goes to the project owner through the project manager, before merge.
- Do not push build artefacts or large images; screenshots belong in one folder with a size budget (docs/ux is already 19 MB of the 21 MB repository).
- Commit messages carry the approval ids.

## Triaging the current shared branch
Treat `claude/practical-franklin-ze9hk2` as submitted work, not as approved. The project manager creates `integration` only after the owner agrees, and does not delete or rewrite the shared branch. Cherry-pick order and status (as of 25 Nov, 14:46 UTC; PM = project manager):

| Commit | What | Architect | PM | Move to `integration` |
|---|---|---|---|---|
| ca51468 and earlier | Work before the approval process | not reviewed individually | n/a | Baseline: `integration` starts from this point |
| ae247ff | UX plan, screenshots, wireframes | changes requested (wording "one at a time", docs/ux size) | accepted | after fixes and re-review |
| e5447f0 | Brand and UX diagnosis | changes requested (same) | accepted | after re-review |
| bf68bba | V1 design system implementation | changes requested (503 message, "one at a time"; browser test of live mode) | accepted out-of-scope work | after fixes, browser test and re-review |
| e5887fc | Logo assets | as bf68bba | accepted | with bf68bba |
| db17872 | Parallel judging (P1) | APPROVED WITH CONDITIONS (total-failure run status, Postgres coverage of tests; follow-ups) | approved subject to architect conditions | after conditions met and both re-check |
| 6c5cff9 | BM25 retrieval (P2) | APPROVED WITH CONDITIONS (two-letter terms, batched reads, label wording, no-overlap display) | approved subject to architect conditions | after conditions met and both re-check |
| 815328f | OpenAlex lookup (P3, on `claude/forge-backend-work`) | not yet reviewed (branch not on the remote) | changes requested | not before both approve |

Unapproved commits stay behind with the requested changes. Update this table in each proposal message.
