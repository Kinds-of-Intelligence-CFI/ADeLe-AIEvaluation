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

## Round 2: gate-walk protocol (diagnosis)

Re-ran the 5 USACO tasks with a "gate-walk" instruction: judges answer six
boundary questions in order, with task evidence, before any score is stated.
All three judges agree on gates 0-2 everywhere; the whole divergence is the
L3/L4 gate phrase "established methods exist for tasks of this kind".
haiku reads "kind" at class level (all of competitive programming -> ceiling
L3); sonnet reads it at instance level (no template for this exact objective
-> floor L4); opus resolves it by sketching a plan and checking whether the
outline falls out of recognizing the problem type.

## Round 3: L3/L4 patch + verification

Commit "PLp: sharpen the L3/L4 gate" makes opus's test explicit in the rubric
text. Verification on the divergent cells (2 seeds, original protocol):
sonnet on Bronze moved 4,4,4 -> 3,4; sonnet on Silver and haiku on the
Platinums unchanged; opus stable. Conclusion: the patch helps at the margin
but the L3/L4 boundary for competition programming remains partly
judge-capability-relative - whether "recognizing the type yields a plan
outline" depends on whether the judge itself can sketch the plan. Text alone
will not close the gap.

What does close it, on this data: the cross-judge MEDIAN. Median of
(haiku, sonnet, opus) equals opus's calibrated answer on every USACO task in
every round (3,3,4,4,4), because haiku and sonnet err in opposite directions.
Recommendation: keep the 3-judge median as the operational label; treat
per-judge offsets as a calibration property to monitor, not a rubric bug to
chase further. A protocol-level option for the team (touches shared
annotation code, not this branch): add the sketch test to the judge
instruction - "before deciding between Levels 3 and 4, attempt to write the
plan outline; if you can, it is Level 3".

## Round 4: paired baseline - OLD v2 rubric, same 8 tasks, same protocol

Labels in plp_oldrubric_pilot_labels.csv. Head-to-head (72 vs 72 annotations):

| metric                        | old rubric      | new rubric      |
|-------------------------------|-----------------|-----------------|
| Krippendorff alpha            | 0.611           | 0.861           |
| levels used (any judge)       | 1-3             | 1-4             |
| per-judge SD                  | 0.40-0.69       | 0.85-1.15       |
| USACO medians B,S,G,P,P       | 3,2,2,2,3       | 3,3,4,4,4       |
| monotone in division          | NO (inverted)   | YES             |
| Spearman vs division          | 0.15            | 0.66            |
| trap violations (cap 2)       | 0/18            | 1/18            |
| Platinum vs tau-bench sep.    | NONE (both 2)   | 2 levels        |

The old rubric reproduces the measured HAL failure on this battery: scores
compress into 2-3, Bronze is rated HARDER than two Platinums, and a Platinum
problem gets the same PLp as a tau-bench flight change. The judges' stated
reasons are the borrowed drivers: "no multi-agent coordination -> below
Level 3", "roughly 4-10 steps -> Level 2", "static and single-agent ->
modest planning". Under the old rubric the judges also disagree in a
DIFFERENT direction than under the new one (old: haiku above sonnet/opus;
new: sonnet above haiku/opus), i.e. old-rubric agreement is not just lower,
it is unstable in sign.

Verdict: on every metric except trap compliance (both fine), the re-keyed
rubric dominates the old one on this battery. Remaining known issue is the
haiku/sonnet L3/L4 offset under the new rubric, mitigated by the 3-judge
median (see Round 3).
