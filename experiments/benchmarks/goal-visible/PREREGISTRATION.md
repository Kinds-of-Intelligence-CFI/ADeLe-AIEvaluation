# goal-visible — the goal written into the coding and terminal judge input (pre-registration)

Pablo, 2026-10-26: "the judge should see the goal in all benchmarks too, if available (perhaps with access to the
tests, although I do not think they are strictly needed)." tau2 got its full task in `tau2-full`. This study does the
same for the six released coding and terminal sets.

Asked what the goal should be here, Pablo ruled (2026-10-26): no tests ("Actually skip the tests, I think it is not
relevant in this case. But it should be clear what is the goal without those tests.") and no reference solution.

**Why.** The judge now reads only the text the agent gets: a GitHub issue, an `instruction.md`, or a prompt. It is not
told what the agent must deliver or how success is checked. An issue says what is wrong, not that the job is a code
change checked by hidden tests. A FrontierSWE instruction says what to build, not what earns the score.

## What the sources publish (survey)

Medians over the released tasks, in characters. None of the test or solution files is used.

| set | tasks | task text | tests the source publishes | reference solution | other goal text |
|---|---|---|---|---|---|
| SWE-bench Verified | 443 | 1,188 | FAIL_TO_PASS names 78 (1 test; max 438); PASS_TO_PASS names 3,025; `test_patch` 1,235 | gold `patch` 855 | none |
| DeepSWE v1.1 | 90 | 2,058 | FAIL_TO_PASS names 4,087 (47 tests); `test.patch` 26,063; all test code 44,216 | `solution.patch` 26,648 | one-line summary on the site |
| FrontierSWE v2 | 19 | 3,190 | verifier scripts, about 50,000 | 332 (p90 41,844) | **public task page: "Task" and "Verification" sections** |
| ProgramBench | 130 | 9,690 | hidden test names 53,126 (857 tests); code on HF, not fetched | none (the original program) | goal already in the prompt |
| Terminal-Bench 4.0 | 35 | 1,611 | `tests/` code 21,269 | `solution/` 15,098 | none |
| TB-Science 0.1 | 70 | 3,607 | `tests/` code 27,091 | `solution/` 30,658 | none |

Sources: SWE-bench Verified HF snapshot `c104f840`; deep-swe `3cda4081`; frontier-swe-v2 `v2.0.0`; ProgramBench
tests JSON as in `programbench-data`; Terminal-Bench HF `v4.0.0`; terminal-bench-science `v0.1.0`. Files were
fetched to gitignored `data/` for this survey and then deleted.

## Input

`build.py` writes `data/instances-goal/` (gitignored; task text is never committed). Each task text has two parts:
1. **What the agent is given:** the frozen text of `data/instances/`, verbatim, in a fence it cannot close. The build
   checks that every frozen text hashes to its `prompt_sha12` and is contained in the new text.
2. **The goal: what counts as success,** written by us from each benchmark's public documentation (README, paper,
   site). A one-line setting sits above both parts.

Part 2 is the same for every task of a set, except:
- SWE-bench Verified and DeepSWE name the repository (DeepSWE also the language).
- FrontierSWE adds the task's own "Task" and "Verification" sections from its public page (cached in
  `data/raw/frontierswe-v2/site/tasks/` on 2026-10-01). Each FrontierSWE task has its own score, so its goal is per
  task. These sections are prose, not test code.

Added text, median: SWE-bench 930 chars, DeepSWE 962, FrontierSWE 2,905, ProgramBench 872, TB 4.0 758,
TB-Science 768. The exact wording is in `build.py` (`SETTING`, `GOAL`).

## Design

- **Tasks.** The 787 released tasks (`pls-relabel/subset.csv` and `subset_long.csv`): SWE-bench Verified 443,
  DeepSWE 90, FrontierSWE 19, ProgramBench 130, TB 4.0 35, TB-Science 70.
- **Rubrics.** All five released on these sets: PLp, PLe, PLs, MSm, MSc (current `src/` texts).
- **Runs.** `goal-visible` (774 tasks, 3,870 cells). `goal-visible-long` (13 ProgramBench tasks, 65 cells): every task
  with a prompt over 50,000 chars or 1,500 lines under any rubric goes, with all five rubrics, to the chunked-read
  judge. These are the same 13 tasks as before. `prompt_sizes.csv` has the sizes. Specs in
  `../mass-annotation/specs/`.
- **Judge.** Opus 5.5, effort low, Claude Code subagents, bare-digit prompt (`v2-noreason`), one repeat, the mass
  runner's retries.
- **Cost.** `adele mass plan`: about 19 weekly points for `goal-visible` (input ~12.4M tokens) and under 1 for
  `goal-visible-long` (~2.4M tokens). The planner assumes 1,500 output tokens per call; bare-digit answers are much
  shorter, so this is an upper bound. API equivalent: $178 standard, $89 batch.

## Controls

Two finished runs judged the same tasks with the same rubric texts, judge and bare-digit prompt, on the old input.
Comparing with them isolates the input change.
- **PL rubrics:** `noreason-pl` and `noreason-long` (the NR arm of `noreason`). Rubric hashes match this run's.
- **MS rubrics:** `relabel-v4-ms` and `relabel-v4-ms-long`. Rubric hashes match.

Noise floor: released against control, exact agreement on these sets is PLp 86%, PLe 95%, PLs 93%, MSm and MSc
99.9%. That contrast changes only the prompt (reasoning vs bare digit) and, for PLp, part of the rubric text.

## Reported

1. Per set and rubric, new against control: exact, within one, mean shift, level counts. Primary.
2. The same against released labels (label set `current`).
3. Criterion signals: Spearman ρ of each rubric with each set's primary outcome, as `ms-benchmarks`
   (`swebench-clean`, `deepswe-clean`, `frontierswe-pl` at 0.9, `programbench-pl` at 0.9, `tb4-clean`, `tbsci-pl`),
   for new, control and released labels. A rubric with one level in a set is not testable there.
4. Run health: labels per cell, rejected attempts, writer model.

## Sealed predictions

| prediction | probability |
|---|---|
| MSm and MSc stay at Level 0 on at least 97% of tasks in every set | 0.85 |
| SWE-bench Verified PLp keeps ρ ≤ −0.45 with solve rate (released −0.55) | 0.8 |
| ProgramBench PLp keeps ρ ≤ −0.4 (released −0.51) | 0.8 |
| PLp exact agreement with control, pooled over the six sets, is below the 86% noise floor | 0.6 |
| SWE-bench Verified mean PLp rises by at least 0.1 against control (control 1.53) | 0.5 |
| At least one set × rubric gains a negative signal with p < 0.05 that its control lacks | 0.3 |

## Then

If Pablo agrees: label set `current` gets a `goal-visible` layer on top for these six sets and five rubrics, and the
releases are rebuilt. Nothing changes before his OK. Launching waits for his go.

## Calls made without asking (for veto)

- FrontierSWE's goal includes its public "Verification" section. It describes the scoring in prose (gates, metric,
  baselines), not test code. Without it, an optimisation task has no stated target.
- The PASS_TO_PASS and FAIL_TO_PASS counts are left out, as test-derived.
- The goal text is ours, in plain words, not copied from the agent harnesses. The SWE-bench agent prompt (which says
  to edit non-test files) varies by harness.
- Repository and language are named for SWE-bench and DeepSWE; time limits and hardware are not given anywhere.
- The setting line says the agent does not see the grading tests (SWE-bench, DeepSWE). This is true of the harnesses
  used for the outcomes.
- No separate gate before the full run: there are no human labels for these sets to gate on.
- Whole tasks, not single cells, are routed to the chunked judge, so all five rubrics of a task use the same judge.

## Amendment: PL freeze bar (2026-10-26, set before any result was looked at)

Pablo: "Ok, run those things so we can freeze them." PLp, PLe and PLs are frozen at their current text (sha256
`b1c3712b…`, `ab994dd7…`, `26e29e64…`, unchanged since `01018cf`) if this study meets all three:
1. **Run health.** Every PL cell has a label, or each missing one is explained (for example, safety-classifier stops).
2. **PLp** has a negative within-set link with solve rate on SWE-bench Verified, p < 0.05 (released: about −0.55).
3. **No new failure.** No PL rubric has a significantly positive link (p < 0.05, the wrong direction) on any set.
If all three hold: the freezes are recorded in `docs/rubric-provenance/`, label set `current` gets a `goal-visible`
layer under `tau2-goal`, and the six releases are rebuilt (Pablo's OK, 2026-10-26). If any fails, nothing is frozen
and the result goes to Pablo first.
