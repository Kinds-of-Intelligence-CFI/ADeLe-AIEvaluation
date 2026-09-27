# tau2-tb4-pl — run log

## 2026-09-27 — pinned runs `tau2pl-r1` and `tb4pl-r1`

`make_prompts.py` wrote `sample.csv` and 894 prompts:
- `tau2pl-r1`: 232 tasks × 3 = 696;
- `tb4pl-r1`: 66 tasks × 3 = 198.

It checked that the rubric files, builder, judge agent and judge message match `swebench-pl`'s
`swepl-r1-low`, that the frozen texts match the hashes in `panel/tasks.csv`, and that no canary
line is left in any Terminal-Bench prompt.

Common configurations behind the solve rates:

| benchmark | common | all |
|---|---|---|
| airline | 7 | 16 |
| retail | 8 | 16 |
| banking_knowledge | 27 | 29 |
| Terminal-Bench | 27 | 27 |

`analysis/analyse.py` was run on synthetic labels (not kept) to test it before any real label.

Dry-run tasks: `uefi-bootkit` (Terminal-Bench, Security) and `banking_knowledge-task_001` (tau2),
three rubrics each.

## 2026-09-27 — dry run

Two relays, one per run (amendment 1), 20:44 UTC. All six answers parse, and the protocol check
passes on all six transcripts:
- the exact two-line message;
- effort `low`;
- no CLAUDE.md attachment;
- only the cell's own two files;
- working directory `~/Developer/ADELE`.

But a safety classifier stopped `claude-opus-5-5` on `uefi-bootkit@PLp` and `uefi-bootkit@PLs`, and
Claude Code finished both calls with `claude-opus-4-8`, which wrote those two answers. `uefi-bootkit@PLe`
and the three tau2 cells were written by `claude-opus-5-5`. Hence amendment 2 (PREREGISTRATION.md):
`writers.py` records the model that wrote each answer, and answers by another model are moved to
`responses_fallback/` and retried once. The two `uefi-bootkit` answers were moved there; their
cells are retried in the full run.

A scan of every judge transcript of this session found five earlier classifier stops, all on
SWE-bench (three in `swepl-r1`, two in `swepl-r1-low`). In each, Opus 5.5 wrote the answer itself.
