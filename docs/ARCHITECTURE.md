# Backend architecture decisions (FORGE SIGNAL)

Short decision records. Newest last. Owner: backend engineer; big ones are flagged to the project manager before building.

## D1. Judge in parallel, write to the database from one thread (2026-11-25)
**Context.** Judgments ran one after another, about 9 s each, so 25 took minutes.
**Decision.** Model calls run in a thread pool (`judge_concurrency`, default 8, capped at 16). The pool only returns results; every database write and the result ordering happen on the calling thread in ranked order. The model SDK retries 429, overload and dropped connections with backoff (`FORGE_MODEL_RETRIES`, default 6). A call that still fails is logged as a source failure with the exception type only (never the message, which could contain a key) and the run continues.
**Consequences.** Results and logs are identical whatever finishes first. Adapter token counters are lock-protected. Measured numbers are in `backend/README.md` (25 judgments in about 26 s on 8 workers at effort low). Effort `low` is needed to meet the 30 s promise.

## D2. BM25 shortlist, no embeddings (2026-11-25)
**Context.** Ranking was shared-stem counts against the profile text. On the stored corpus 9 of 10 judged records were irrelevant, and the 250-record cap cut by nearest deadline before relevance.
**Decision.** `app/retrieval.py` ranks by BM25 over title (weighted 3x) and text against the researcher's research areas only. Records sharing no term with the research areas are not sent to the model (`no_term_overlap` counter). When records come from the stored copy the detail cap is lifted, because reading the store is free; the cap still guards live pulls.
**Consequences.** Synonym-only matches (no shared word) are missed; embeddings could be added later behind the same `rank_candidates` function. Quality is checked by `scripts/retrieval_check.py` (see README for what it proves and does not).
