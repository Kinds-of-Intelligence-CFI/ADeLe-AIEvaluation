# tau2-tb4-pl — pre-registration

Committed before any label of this study exists, with the analysis script
(`analysis/analyse.py`). Runs `tau2pl-r1` (tau2) and `tb4pl-r1` (Terminal-Bench 4.0.0). Drafted
2026-09-27 from the plan Pablo approved that day: the three planning rubrics, judged by Opus at low
effort, on the verifiably solvable tasks of the two other benchmarks in `panel/`.

**Question.** Do the planning rubrics (PLp, PLe, PLs) separate tasks by difficulty on benchmarks
other than SWE-bench Verified? `swebench-pl` found PLp against solve rate ρ = −0.63 with Opus at
medium effort and −0.57 at low effort, on 435 SWE-bench tasks. This study asks the same question of
tau2 (customer-service conversations) and Terminal-Bench 4.0.0 (long command-line tasks), with the
same judge setting, rubric files and prompt builder.

## Judge and protocol

- Opus (alias `opus`) through `adele-judge-low` (`../swebench-pl/adele-judge-low.md`: tools Read
  and Write, `omitClaudeMd`, effort low), the judge setting Pablo chose after `swebench-pl` step 1c.
  Relays (`../swebench-pl/judge-dispatcher-low.md`) send each cell to the judge through the Agent
  tool with the two-line message in `run.json`. The judge files live in `judge-io/<run>/`, two
  levels above the repo, and the judging session runs from that folder, as in `swebench-pl`.
- Prompts are built by `build_annotation_prompt` from `swebench-pl`'s rubric files; `make_prompts.py`
  checks the rubric, builder and judge-agent hashes against its run `swepl-r1-low`. One (task,
  rubric) per call, a fresh subagent each time.
- Task text is the frozen instance (`data/instances/`, the text whose hash `panel/tasks.csv`
  records).
  - tau2: the user scenario as the `taubench` loader renders it (reason for the call, known and
    unknown information, what the user wants). The domain policy and tools are not shown; they are
    the same for every task of a domain.
  - Terminal-Bench: the task's `instruction.md`, without the HTML comment lines that carry the
    benchmark's training-corpus canary, which are not part of the task.
- A missing or unparseable answer is retried once, and the retry is recorded.
- **Answers by another model (amendment 2).** The registered judge is `claude-opus-5-5`. When a
  safety classifier stops it, Claude Code may finish the call with another model.
  - `writers.py` matches each answer file to the Write call that produced it (same SHA-256) in
    the judge's transcript, and records the writing model in `labels/<run>/writers.csv`.
  - An answer written by another model is moved to `responses_fallback/`, and the cell is retried
    once. If the retry again ends with another model, the cell has no label.
- Dry run: the first six calls (one Terminal-Bench task and one tau2 task, three rubrics each) go
  through one relay per run. The full run starts only if their transcripts pass the protocol check:
  - the exact message;
  - model and effort;
  - no CLAUDE.md attachment;
  - only the cell's own two files;
  - the judging session's folder.

  Their answers are part of the run.

## Items

- **tau2** (`tau2pl-r1`): the verifiably solvable tasks (panel rule 4) of airline (49 of 50),
  retail (114 of 114) and banking_knowledge (69 of 93), so 232 tasks × 3 rubrics = 696 calls.
  Telecom is excluded: its 2,285 tasks share five texts.
- **Terminal-Bench 4.0.0** (`tb4pl-r1`): all 66 tasks × 3 = 198 calls.
  - The 34 verifiably solvable tasks are the analysis set.
  - The other 32 are judged for exploratory comparison only: 30 are named in Epoch's review, and 2
    more fall below the 5% cut.

`sample.csv` lists every task with its run, whether it is in the analysis set, and the outcome data
the analysis uses. It is frozen before any label.

## Outcomes

- **Solve rate**: the share of scored trials with reward 1, on the frozen text (panel rules 1 and
  3).
  - On SWE-bench and Terminal-Bench, every configuration ran every task.
  - On tau2, older configurations ran earlier versions of some tasks, and their results are left
    out. Within a domain, the tasks' solve rates would therefore come from different sets of
    models: in airline, 7 configurations ran all 49 tasks and 9 older ones ran 28. Across all
    configurations and across the common ones, the airline solve rates correlate at only 0.77.
  - The solve rate is therefore taken, per benchmark (per domain on tau2), over the configurations
    that ran every analysis-set task with scored trials:
    - 7 in airline;
    - 8 in retail;
    - 27 of 29 in banking_knowledge;
    - all 27 on Terminal-Bench.
- **Expert time** (Terminal-Bench): the authors' `expert_time_estimate_hours` in each task's
  `task.toml` (0.75 to 16 hours on the analysis set).

## Analysis

Descriptive. `analysis/analyse.py` writes the frozen outputs to `results/`. Labels are those the
registered judge wrote; a task without one on a rubric drops out of that rubric's tests, and the
counts are reported. The statistics are
`swebench-pl`'s:
- Spearman ρ, with a 95% CI by Fisher z using the Bonett–Wright standard error, and a two-sided p;
- a prediction is supported if p < 0.05 with the predicted sign;
- no correction for multiple tests, and PLp is the main test.

- Level distribution of each PL rubric, per tau2 domain, and on Terminal-Bench's analysis set and
  its other 32 tasks.
- **Q1 (main).** PLp against solve rate, per benchmark. Prediction: ρ < 0. The same for PLe and
  PLs on a benchmark where they take at least three values.
  - **tau2: within domain.** Each domain's ρ is computed on its own tasks. The three are combined by
    the inverse-variance-weighted mean of their Fisher z, and the test is on the combined value.
    - Why within domain: the domains differ in policy and in the configurations behind their solve
      rates, so their solve rates are not on one scale.
    - A domain where the rubric takes a single value contributes nothing.
    - The per-domain ρ are reported, without predictions of their own.
  - **Terminal-Bench**: the 34 tasks.
- **Q2 (Terminal-Bench).** PLp against expert time, on the 34 tasks. Prediction: ρ > 0.
- **Robustness, answers by other models (amendment 2).** Q1 and Q2 again, with the answers other
  models wrote filling the cells the registered judge did not answer.
- **Robustness (tau2).**
  - Q1 with the solve rate over all configurations (the panel's `solve_rate`).
  - Q1 pooled over the 232 tasks, without the domain split.

Power (two-sided α = 0.05, Fisher z, as in `swebench-pl`):

| test | effect | probability of detecting it |
|---|---|---|
| tau2, combined within domain (Σ(n − 3) = 223) | \|ρ\| = 0.20 | ≈ 0.86 |
| tau2, combined within domain | \|ρ\| = 0.15 | ≈ 0.62 |
| Terminal-Bench (n = 34) | \|ρ\| = 0.57, SWE-bench's size at low effort | ≈ 0.95 |
| Terminal-Bench (n = 34) | \|ρ\| = 0.30 | ≈ 0.41 |

Terminal-Bench can confirm an effect as large as SWE-bench's, but cannot rule out a modest one.

**Planned exploratory analyses, not tests:**
- PLp against solve rate and against expert time on Terminal-Bench's other 32 tasks, and on all 66;
- level distributions compared with `swebench-pl`'s Opus-low labels.

## Caveats known before labels

- **The judge may recall tasks, so neither benchmark separates demand judgment from recall.**
  - SWE-bench's issues and fixes have been public since 2023.
  - Terminal-Bench 3.0's tasks were written in a public GitHub repository opened in January 2026;
    most task pull requests are from April and May. The benchmark was released on 29 June 2026, and
    4.0.0 keeps 66 of its 74 tasks, 20 of them updated.
  - The judge's training data runs to about mid-2026. Terminal-Bench's exposure before that was
    months, not years.
- **Solve rates average over configurations that differ between benchmarks** (panel rule 5), so
  every correlation is within one benchmark.
- **The tau2 judge sees the user's side of the task.** What the agent must do also depends on the
  domain policy, which the judge does not see.

## Deviations

None yet. One amendment before any label (2026-09-27): the dry run goes through one relay per
run, not a single relay, because a relay serves one judge-file folder.

Amendment 2 (2026-09-27, after the dry run, before the full run and before any analysis): in the
dry run, a safety classifier stopped the judge on two of the three calls for `uefi-bootkit`
(Terminal-Bench, Security), and Claude Code finished both with `claude-opus-4-8`. Added: the rule on
answers by another model, `writers.py`, the writing model in `labels_long.csv`, and the analysis
of cells without a label and of other models' answers. In `swebench-pl`, five of its 2,388 Opus
calls had a classifier stop, and Opus 5.5 wrote every one of those answers itself.
