# swebench-clean — pre-registration

Committed and pushed before any label of run `clean-swe`.

**Question.** Do the PL results on SWE-bench Verified hold on a cleaner task set, which drops the tasks known or
likely to be broken and keeps the hard tasks that some agent has solved?

## The clean set (Pablo's rule, 2026-10-01)

All 500 SWE-bench Verified tasks, minus (`make_set.py` → `tasks.csv`):
- **never solved** (29): no entry of the 135 in `SWE-bench/experiments` (`40f164d`) resolves it. With no fix ever
  accepted, a task cannot be told apart from a broken one;
- **OpenAI-named** (3): the tasks OpenAI's 2026 audit names as defective (`pylint-dev__pylint-4551`,
  `sympy__sympy-18199`, `django__django-14725`). The audit's full list of 138 tasks is not public;
- **UTBoost weak tests** (26): the Verified tasks whose tests UTBoost (ACL 2025) showed accept wrong patches
  (`augTest.json` at UTBoost commit `47a47c2`, sha256 pinned in `make_set.py`).

One task is in two groups. **443 tasks remain.** Unlike `swebench-pl`'s cut (solve rate ≥ 0.05), this keeps 35 hard
tasks solved by 1 to 6 of 135 entries: some agent's fix passed, so their tests can be passed.

## Design

- **Labels.** PLp (text O), PLe and PLs, Opus 5.5 at effort low, v2 prompt, one call per cell. 413 clean tasks already
  have all three labels (`plp-o-relabel`, `plp-b2` gate, `pl-relabel-v2`, `natural-prompt` gate). Run `clean-swe`
  labels the other 30 (90 calls). `make_prompts.py` rebuilt all 1,239 existing prompts of the clean set and matched
  their stored hashes, so the new cells use exactly the same inputs.
- **Writers.** Answers by another model are set aside and the cell is judged once more; if that fails too, the cell
  has no label.
- **Analysis** (`analysis/analyse.py`). `swebench-pl`'s pre-registered `questions()`: Q1, each PL rubric with at
  least three distinct levels against solve rate (predicted negative); Q2, PLp against SWE-bench's time-to-fix bucket
  (predicted positive). Main: the 443. Robustness: the clean tasks with solve rate ≥ 0.05 (408). Descriptive: level
  counts; PLp on the 35 rarely solved tasks against the rest. Tested on synthetic labels, which were not kept.

## Predictions (sealed)

Values on `swebench-pl`'s 435 solvable tasks (same labels) in brackets.
- PLp against solve rate negative with p < 0.05 on the 443 (−0.57): 0.97. More negative on the 443 than on the 408: 0.7.
  Between −0.65 and −0.50 on the 443: 0.65.
- PLp against time to fix positive with p < 0.05 (+0.45): 0.95.
- PLe against solve rate negative with p < 0.05 (−0.29): 0.85.
- PLs has three or more distinct levels and so is tested: 0.3.
- The 35 rarely solved tasks have a higher mean PLp than the rest: 0.85. At least one of them is at PLp 3: 0.6.

## Caveats, fixed in advance

- Contamination is not addressed: models, and our judge, may recall some fixes (OpenAI 2026). A pass by 1 of 135
  entries shows the tests can be passed, not that they were passed fairly.
- The never-solved rule and the 0.05 cut both select on outcome; the exclusions by OpenAI and UTBoost do not.
- The 135 entries span 2023–2026, so "rarely solved" mixes hard tasks and weak older entries.

## Cost

90 Opus-low calls, under one weekly point.
