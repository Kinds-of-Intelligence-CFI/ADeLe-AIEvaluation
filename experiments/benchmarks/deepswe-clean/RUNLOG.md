# deepswe-clean — run log

## 2026-10-01 — set built, not pre-registered yet

Pablo's decisions applied (recorded in `PREREGISTRATION.md`). Outcome files moved from `panel/sources/deepswe-v1.1/` to
`data/raw/deepswe-v1.1/` (gitignored); `fetch_outcomes.py` rewritten to write there plus a tracked aggregate leaderboard
(now with `metrics_source`). Rerun from the cached site JSON: the moved files are byte-identical.

`make_set.py`: 90 of 113 kept (Epoch defect 23; never solved 0). `community_issue`: 7 tasks, 4 of them kept
(bandit-structured-nosec-directives, csstree-shorthand-expansion-compression, gql-incremental-graphql-delivery,
quill-shared-toolbar-focus). Clean-set solve rate: min 0.036, median 0.607, max 0.917; one task below 0.05 (gql).
The two sensitivity rates correlate with the primary at Spearman 0.993 and 0.994 on the 90.

Analysis tested on synthetic labels (not kept). `adele mass plan`: 270 cells (90 × 3), ~0.81M input and ~0.41M output
tokens, ~1 weekly subagent point. Not pinned or run.

Trial durations do not settle the timeout question: `agent_duration_seconds` exceeds 5,400 s in 29 configurations run
before the change, so it is not the agent budget.
