# rubric-qa: inter-judge pilot for the re-keyed PLp rubric

First empirical check of the single-driver PLp rubric (commit "rubrics(v2):
re-key PLp on a single demand driver"). 8 tasks from pilot/tasks.csv, 3 judges
(haiku / sonnet / opus) x 3 independent samples each = 72 annotations, using
the exact `build_annotation_prompt` format from `adele.annotation.prompts`
with the new rubric. Judges saw only the task prompt text - no benchmark name,
no USACO division label.

Battery: the 5 USACO 2025 US Open problems (Bronze/Silver/Gold/Plat/Plat,
an external-difficulty ladder), 2 tau-bench tasks as demarcation traps
(designed PLp cap 2: their difficulty is MS/PLe, not plan-finding), and 1
AssistantBench lookup as an L1 anchor probe.

Results (see plp_v2redesign_pilot_labels.csv):
- Within-judge 3-seed full agreement: haiku 4/8, sonnet 7/8, opus 8/8.
- Cross-judge: all pairs within +-1 on 8/8 tasks. Krippendorff alpha
  (interval): 0.861 over all ratings, 0.811 over judge modes.
- Spread: every judge used levels 1-4; per-judge SD 0.85-1.15 (old-rubric
  HAL labels sat at ~0.5).
- USACO ladder medians Bronze->Plat: 3,3,4,4,4 - monotone, blind to division.
- Traps: 17/18 ratings at or under the designed cap (one haiku seed gave 3).
- L1 anchor: 9/9 exact.

Known systematic effect: sonnet reads the whole USACO ladder one level higher
than haiku (haiku mode 3 vs sonnet mode 4 on all five problems; opus splits
by difficulty: 3,3,4,4,4). Constant offset between judges, not noise - the
L3/L4 gate ("can the decomposition be listed at the outset?") is applied with
different strictness. Candidate fix if it persists at scale: one more L3/L4
matched example pair.

Caveats: single small battery; judges are the harness's current haiku/sonnet/
opus builds, not the exact API snapshots used for the old HAL labels; judge
output kept to a short justification rather than full printed CoT. Next steps:
old-rubric arm on the same 8 tasks for a paired comparison, then re-annotation
of the HAL traces for the PLp/PLe separation test.
