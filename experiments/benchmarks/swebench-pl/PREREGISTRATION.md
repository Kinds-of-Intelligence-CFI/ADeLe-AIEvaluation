# swebench-pl — pre-registration

Committed before any label of this study exists. Runs `swepl-gate` (step 1) and `swepl-r1`
(step 2). Drafted 2026-09-26 on Pablo's design: an effort gate, then the three planning rubrics
on every solvable SWE-bench Verified task with one judge.

**Question.** Do the v2 planning rubrics (PLp, PLe, PLs) separate SWE-bench Verified tasks by
difficulty? `swebench-30` checks annotation quality on 30 tasks and 25 rubrics with two judges;
this study annotates all solvable tasks on the three PL rubrics with one judge, so that the
demand–difficulty relation can be tested with adequate power.

## Judge and protocol

- Opus (alias `opus`), through the `adele-judge-medium` subagent (`adele-judge-medium.md`): the
  `swebench-30` judge with only `effort: medium` in place of `max` (tools Read and Write,
  `omitClaudeMd`). Harness as in `swebench-30` run `swev30-r4`: relays (`judge-dispatcher-medium.md`)
  send each cell to the judge through the Agent tool with the two-line message in `run.json`, and
  the judge files live in `judge-io/<run>/`, two levels above the repo.
- Prompts are built exactly as in `swebench-30`: same builder, same rubric files (hashes in
  `run.json`), problem statement only. One (task, rubric) per call, a fresh subagent each time.
- A missing or unparseable answer is retried once, and the retry is recorded.

## Step 1 — effort gate (run `swepl-gate`)

Opus at medium judges the 132 PL cells of `swebench-30`: its 30 tasks and 14 anchors × PLp, PLe,
PLs, with prompts identical to `swev30-r4` (checked hash by hash). Reference labels are those of
`swev30-r4`: Opus at max (all 132 cells) and Sonnet at max (the PL cells it has answered when the
gate is computed). The three pairwise agreements are reported (exact, within-1, mean level shift,
quadratic-weighted κ). Step 2 starts only if all of the following hold:

1. within-1 agreement of Opus-medium with Opus-max ≥ 90%;
2. on the cells with a Sonnet label, exact agreement of Opus-medium with Opus-max ≥ exact agreement
   of Sonnet-max with Opus-max;
3. mean level shift (medium − max) within ±0.25 on each of PLp, PLe and PLs;
4. parse rate of the gate run ≥ 98%.

Otherwise step 2 does not start, and the gate result is reported.

## Step 2 — scale-up (run `swepl-r1`)

- **Items.** All SWE-bench Verified tasks (official 500, HF revision `c104f840`) whose leaderboard
  solve rate over the 135 entries of `SWE-bench/experiments` at `40f164d` is at least 0.05: 435
  tasks. The 37 of them already judged in step 1 are not re-judged; `swepl-r1` covers the other
  398 × 3 rubrics = 1,194 calls. `sample.csv` lists every task of both runs with its solve rate.
- Tasks below 0.05 are excluded. OpenAI's 2026 audit found that most rarely-solved Verified tasks
  have tests that reject correct fixes, and Epoch rates SWE-bench Verified as Flawed, so for those
  tasks the solve rate does not measure difficulty.

## Analysis

Descriptive; scripts in `analysis/`, frozen outputs in `results/`. Analysis set: the 435 solvable
tasks, pooling step 1 (its 37 solvable tasks) and step 2.

- Level distribution of each PL rubric.
- **Q1 (main).** Spearman ρ between PLp and solve rate. Prediction: ρ < 0. The same for PLe and PLs
  if they take at least three values.
- **Q2.** Spearman ρ between PLp and SWE-bench's human time-to-fix bucket (`difficulty`).
  Prediction: ρ > 0.
- **Robustness.** Q1 and Q2 without the 37 step-1 tasks.

Power: at n = 435, a true |ρ| of 0.15 is detected with probability ≈ 0.88 and |ρ| = 0.20 with
≈ 0.99 (two-sided α = 0.05, Fisher z).

## Deviations

None yet.
