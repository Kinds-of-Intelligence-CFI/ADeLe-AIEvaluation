# tau2-tb4-pl — results

> **Superseded labels (2026-09-30).** These results use the v1 annotation prompt. The PL labels were
> redone with the adopted v2 prompt in [`pl-relabel-v2`](../pl-relabel-v2/RESULTS.md): PLp within
> tau2 domains is −0.38, PLe within domain is no longer significant (−0.11), and Terminal-Bench
> still shows no significant link. Quote the v2 numbers.

**Question.** Do the v2 planning rubrics (PLp Planning, PLe Action control and execution, PLs
Simulating) track task difficulty beyond SWE-bench Verified, on tau2 (airline, retail,
banking_knowledge) and on Terminal-Bench 4.0.0?

**Answer.** Yes on tau2 (PLp against solve rate within domain, ρ = −0.33), no on Terminal-Bench
(ρ = −0.06). On tau2 all three rubrics fall with solve rate in every domain where they vary. The
evidence is thinner than on SWE-bench:
- PLp is 2 on 198 of the 232 tasks;
- part of its signal is shared with the length of the user's scenario (exploratory).

On Terminal-Bench, PLp tracks neither solve rate nor the authors' expert-time estimates, and 26 of
its 33 analysable tasks sit at level 3. The confidence interval (−0.40 to 0.29) excludes an effect
as large as SWE-bench's (−0.57 with the same judge). One judge: Opus 5.5 at low effort.

**Status.** Complete (2026-09-28): 894 cells judged, pre-registered analysis done.

## Design

See `PREREGISTRATION.md`: design, predictions and analysis script were committed before any
label (`4ee1b34`), with two amendments before the full run.

- **Items.**
  - tau2: the 232 verifiably solvable tasks (panel rule 4) of airline (49), retail (114) and
    banking_knowledge (69). Telecom is excluded: its 2,285 tasks share five texts.
  - Terminal-Bench 4.0.0: all 66 tasks. The 34 verifiably solvable ones are the analysis set.
  - List and outcome data: `sample.csv`.
- **Task text.** tau2: the user's scenario, not the domain policy the agent follows.
  Terminal-Bench: `instruction.md` without its canary comment lines.
- **Judge.** Claude Opus (`claude-opus-5-5`) through `adele-judge-low`: effort low, tools Read and
  Write only, no CLAUDE.md, one (task, rubric) per call. Rubric files, prompt builder and agent
  are those of `swebench-pl`'s Opus-low run, checked by hash.
- **Outcomes.**
  - Solve rate: the share of scored trials with reward 1 on the frozen text, over the
    configurations that ran every analysis-set task. That is 7 in airline, 8 in retail, 27 in
    banking_knowledge and 27 on Terminal-Bench.
  - Terminal-Bench's `expert_time_estimate_hours` (0.75–16 h on the analysis set).
- **Labels.** 894 cells, all parsed: `labels/tau2pl-r1/`, `labels/tb4pl-r1/`.
  - 893 were written by the registered judge.
  - A safety classifier stopped Opus 5.5 on `uefi-bootkit@PLp` on both attempts, and Claude Code
    finished them with Opus 4.8. That cell has no registered label (amendment 2).

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`). Spearman ρ with a Fisher-z 95% CI; a
prediction is supported when p < 0.05 with the predicted sign. On tau2, per-domain ρ are combined
by the inverse-variance-weighted mean of their Fisher z.

| test | n | ρ [95% CI] | p | prediction |
|---|---|---|---|---|
| Q1 tau2: PLp vs solve rate, within domain | 232 | −0.325 [−0.440, −0.199] | 1e−6 | supported |
|   airline | 49 | −0.520 | 1e−4 | |
|   banking_knowledge | 69 | −0.300 | 0.01 | |
|   retail | 114 | −0.257 | 0.006 | |
| Q1 tau2: PLe vs solve rate (retail is all level 1, so not included) | 118 | −0.243 [−0.410, −0.059] | 0.01 | supported |
| Q1 tau2: PLs vs solve rate | 232 | −0.259 [−0.379, −0.131] | 1e−4 | supported |
| Q1 Terminal-Bench: PLp vs solve rate | 33 | −0.060 [−0.395, 0.290] | 0.74 | not supported |
| Q1 Terminal-Bench: PLs vs solve rate | 34 | −0.083 [−0.410, 0.263] | 0.64 | not supported |
| Q1 Terminal-Bench: PLe | | | | not tested: two levels only (3 and 4, 17 tasks each) |
| Q2 Terminal-Bench: PLp vs expert time | 33 | +0.192 [−0.165, 0.505] | 0.28 | not supported |
| Robustness tau2: solve rates over all configurations | 232 | PLp −0.288, PLe −0.253, PLs −0.265 | | all supported |
| Robustness tau2: pooled, no domain split | 232 | PLp −0.330, PLe −0.526, PLs −0.147 | | all supported |
| Robustness: with Opus 4.8's answer for `uefi-bootkit@PLp` | 34 | Q1 −0.060, Q2 +0.187 | | unchanged |

The pooled PLe (−0.53) is much stronger than the within-domain value because it mixes domains:
- retail has PLe 1 on every task and high solve rates;
- banking_knowledge has the highest PLe and the lowest solve rates.

That confound is why the test is within domain.

Level counts (`results/pl_levels.csv`; tasks at levels 0–5):

| | PLp | PLe | PLs |
|---|---|---|---|
| tau2 airline (49) | 0 / 12 / 35 / 2 / 0 / 0 | 0 / 45 / 4 / 0 / 0 / 0 | 0 / 7 / 42 / 0 / 0 / 0 |
| tau2 retail (114) | 0 / 8 / 104 / 2 / 0 / 0 | 0 / 114 / 0 / 0 / 0 / 0 | 2 / 5 / 107 / 0 / 0 / 0 |
| tau2 banking_knowledge (69) | 0 / 5 / 59 / 5 / 0 / 0 | 0 / 12 / 42 / 15 / 0 / 0 | 2 / 9 / 58 / 0 / 0 / 0 |
| Terminal-Bench analysis set (34) | 0 / 0 / 4 / 26 / 3 / 0 (1 no label) | 0 / 0 / 0 / 17 / 17 / 0 | 9 / 9 / 15 / 1 / 0 / 0 |
| Terminal-Bench, other 32 | 0 / 0 / 6 / 25 / 1 / 0 | 0 / 0 / 0 / 15 / 17 / 0 | 8 / 13 / 11 / 0 / 0 / 0 |

## Exploratory results

From `results/analysis.json` and `results/exploratory.json` (`analysis/exploratory.py`).

- **Planned: levels against SWE-bench** (mean level, Opus low; SWE-bench from `swebench-pl`'s 435
  solvable tasks):

  | | PLp | PLe | PLs |
  |---|---|---|---|
  | SWE-bench Verified | 1.38 | 2.77 | 1.02 |
  | tau2 airline / retail / banking | 1.80 / 1.95 / 2.00 | 1.08 / 1.00 / 2.04 | 1.86 / 1.92 / 1.81 |
  | Terminal-Bench analysis set / other 32 | 2.97 / 2.84 | 3.50 / 3.53 | 1.24 / 1.09 |

  PLp rises from SWE-bench to tau2 to Terminal-Bench. On each benchmark, most tasks share one
  level, and the level differs between benchmarks.
- **Planned: Terminal-Bench's other 32 tasks and all 66.** PLp against solve rate is +0.03 on
  both; against expert time, +0.16 and +0.15 (not significant).
- **Mean solve rate by PLp level** (1, 2, 3) falls on every tau2 domain:
  - airline: 0.97 (12 tasks), 0.79 (35), 0.55 (2);
  - retail: 0.92, 0.76, 0.69;
  - banking_knowledge: 0.51, 0.42, 0.18.

  Terminal-Bench (PLp 2, 3, 4): 0.64, 0.46, 0.62.
- **Not pre-registered: scenario length.** On tau2, longer scenarios are harder and get higher
  PLp. Given length, PLp's partial correlation with solve rate shrinks by about 15% in airline, 30%
  in retail and 64% in banking_knowledge. On SWE-bench, PLp held at −0.63 given the problem
  statement's length.

  | tau2 domain | length vs solve rate | PLp vs length | PLp vs solve rate | same, given length |
  |---|---|---|---|---|
  | airline | −0.32 | +0.52 | −0.52 | −0.44 |
  | retail | −0.34 | +0.28 | −0.26 | −0.18 |
  | banking_knowledge | −0.52 | +0.42 | −0.30 | −0.11 |

  On Terminal-Bench, length relates to neither solve rate (+0.25, not significant) nor PLp
  (+0.07).

- **Human check** (after the analysis, exploratory: `human-labels/RESULTS.md`). Pablo labelled 7
  Terminal-Bench tasks blind; one was an abstention.
  - He put none of the judge's Level 3s at 4, so there is no sign the Level 3/4 boundary is
    too strict.
  - He put 3 of 5 at 2, and on reading the rubric those look right: the judge counted
    perception, black-box probing and a one-off method choice as interacting decisions.
  - Exact agreement with the judge: 3 of 6.

- **Follow-up: Opus at max effort** (pre-registered as exploratory, run `tb4pl-max`,
  `results/effort_followup.json`). PLp on the 34 Terminal-Bench analysis-set tasks, same prompts;
  33 have a registered label on both runs.
  - Max against low: exact 0.82, within one level 1.00, κ 0.66, mean shift −0.12.
    - Four of the 26 low-effort Level-3 tasks drop to 2, one Level 4 drops to 3 and one Level 3
      rises to 4.
    - Level-2 tasks go from 4 to 8.
  - Prediction 1 held: shift below zero and more tasks at Level 2.
  - Prediction 2 failed: max agrees with Pablo's blind labels on 2 of 6, against 3 of 6 at low
    effort.
  - So the pre-registered consequence, re-judging Terminal-Bench at max effort, is not triggered.
  - Max keeps at 3 the three tasks Pablo put at 2. Its reasoning weighs the rubric's exclusions and
    still counts early architectural choices that constrain later ones. For `html-js-filter`, it
    cites the parse-and-serialise design, which follows the pattern of the rubric's Level-3
    contest example.
  - The disagreement is therefore not an effort artifact. It is a reading of the 2/3 gate, where
    almost any real engineering task has some early choice that constrains later ones.
  - On the max labels, PLp against solve rate is +0.05 [−0.30, 0.39] and against expert time
    +0.29 [−0.06, 0.58]. Two of the tasks that dropped to Level 2 are among the hardest (solve
    rates 0.05 and 0.13).

## Deviations and caveats

- **Deviations:** none. Two amendments before the full run:
  1. the dry run used one relay per run;
  2. answers written by a model other than the registered judge are set aside and retried once;
     the main analysis excludes them, and a robustness check includes them.
- **A safety classifier swaps the judge silently.** On `uefi-bootkit` (a Terminal-Bench Security
  task), Claude Code finished two of three calls with Opus 4.8 without any error. No other cell of
  the 894 was stopped. `writers.py` now checks which model wrote each answer.
- **Concentrated levels.** Off their most common level, PLp has 34 of 232 tau2 tasks and 7 of 33
  Terminal-Bench tasks. The tau2 correlations rest on those few tasks.
- **The tau2 judge sees the user's side only.** The domain policy that the agent must follow is
  not in the task text.
- **Why Terminal-Bench differs is open.** The rubric may not separate long, multi-step tasks,
  which almost all land at PLp 3. Or Terminal-Bench difficulty may lie in specialist knowledge
  (genomics, Coq proofs, hardware) rather than planning. The other rubrics, which are not yet
  judged here, would tell these apart.
- **Contamination.** Neither benchmark separates demand judgment from recall.
  - Terminal-Bench 3.0's tasks, which 4.0.0 keeps, were written in a public GitHub repository
    from January 2026 and released on 29 June 2026.
  - The judge's training data runs to about mid-2026.
- **Ceiling effects on tau2.** The common configurations are strong 2026 models: the median solve
  rate is 0.93 in airline and 0.81 in retail.
- **Power.** On Terminal-Bench, n = 33 detects |ρ| = 0.3 with probability ≈ 0.4. The interval
  rules out SWE-bench's effect size, not a modest effect.

## Reproduce

```
python experiments/benchmarks/tau2-tb4-pl/analysis/analyse.py
python experiments/benchmarks/tau2-tb4-pl/analysis/exploratory.py   # also needs data/instances/
```

The numbers above are those committed in `0446cce`. Prompts and the judges' reasoning quote task
text and stay out of the repo.
