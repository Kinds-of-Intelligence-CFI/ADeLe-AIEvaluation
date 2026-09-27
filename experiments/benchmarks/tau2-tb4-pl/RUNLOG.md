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

Dry run: `uefi-bootkit` (Terminal-Bench, Security) and `banking_knowledge-task_001` (tau2), three
rubrics each, through one relay.
