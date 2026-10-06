# noreason — does written reasoning about the rubric matter? (pre-registration)

Committed before any label of this study. Pablo asked for it on 2026-10-06: annotate with Opus 5.5 stating the level
only, without reasoning, and compare.

**Question.** Does asking the judge to reason about the rubric before giving the level change the labels? Does it
change their criterion validity?

**Manipulation.** A new builder, `v2-noreason` (`src/adele/annotation/prompts.py`). It is the v2 prompt with one
paragraph swapped.
- **Removed:** "write a short assessment … which level's conditions it meets, and what keeps it below the next level.
  Compare the task with the rubric's examples …".
- **Added:** "Give the level directly, without any assessment, explanation or other text."
- **Unchanged:** the "base the level on the rubric's conditions" and tie-break sentences, the rubric, the task and
  the final answer sentence. A test checks that exactly one line differs.
- **Same judge** in every arm: Opus 5.5 at effort low, `adele-judge-v2-low`, through the `adele mass` runner.
- **Caveat:** what is removed is *written* reasoning. Effort low cannot switch off the model's internal thinking. The
  study measures the value of the written assessment the protocol asks for.

## Runs (specs in `mass-annotation/specs/`)

| run | builder | tasks | rubrics | cells |
|---|---|---|---|---|
| `noreason-pl` | v2-noreason | the 1,016 single-read clean tasks of relabel-v2 (9 sets) | PLp, PLe, PLs | 3,048 |
| `noreason-ms` | v2-noreason | tau2 clean (242) | MSm, MSc | 484 |
| `noreason-ref` | v2 (with reasoning) | 150 of the 1,016, stratified by set (seed 20261006, `refresh_subset.csv`) | PLp, PLe, PLs | 450 |
| `noreason-ref-ms` | v2 (with reasoning) | the 40 tau2 tasks of that subset | MSm, MSc | 80 |

**Why a fresh reasoning reference.**
- The released labels are relabel-v2, with relabel-v3 overrides for PLp at 3–5.
- PLp's text changed between them, so released PLp mixes two texts. MSm's text also changed.
- PLe, PLs and MSc are unchanged.
- The reference arm uses the current texts on the same day. It gives two things: a clean comparison on 150 tasks, and
  the judge's own rerun noise against the released labels, which is the yardstick for agreement.

## Analysis (`analysis/analyse.py`)

- **A. Agreement.** For each rubric, the no-reasoning (NR) label against the released label: exact, within one,
  quadratic-weighted κ, and mean shift.
  - Yardstick on the 150-task subset: agreement of the fresh reasoning label (R') with the released label, on the
    same cells.
  - The gap is agree(NR, released) − agree(R', released).
  - Also agree(NR, R') directly, which is the same text on the same day.
- **B. Criterion validity.** Spearman ρ with each set's primary outcome, as in relabel-v2:
  - solve rate;
  - tau2 within domain, combined;
  - for NR and for the released labels, on all tasks.
  - Bootstrap 95% CI of ρ(NR) − ρ(released) (5,000 resamples) for the three signal cells: SWE-bench PLp,
    ProgramBench PLp and tau2 PLp.
- **C. Level distributions.** Counts per level for each arm. Does NR compress to the modal level, or spread out?
- **D. The length heuristic.** Spearman of level with task prompt length (characters), NR against released, per set.
  Do labels lean more on length without reasoning?

## Decision rule

Apply it to the three signal cells (SWE PLp, ProgramBench PLp, tau2 PLp) and to the PL agreement gaps.

- **Reasoning matters** if either holds:
  - ρ(NR) is weaker than ρ(released) by at least 0.10 in at least two of the three signal cells;
  - the exact-agreement gap is at least 10 points below the yardstick for at least two of PLp, PLe and PLs.
- **Reasoning is not needed** if both hold:
  - every signal cell's ρ(NR) is within 0.05 of ρ(released), or stronger;
  - every PL gap is under 5 points.
- **Otherwise mixed.** Report which rubrics and sets differ.

Validity: only answers written by `claude-opus-5-5` count. A cell answered with reasoning text in the NR arm is still
parsed, and the share of such answers is reported as a protocol-compliance check.

## Predictions (sealed)

- **Overall verdict:** reasoning matters 0.40, mixed 0.35, not needed 0.25.
- **Agreement.**
  - Yardstick (R' vs released) PLp exact ≥ 80%: 0.6. NR vs released PLp exact ≥ 75%: 0.45.
  - PLe and PLs NR agreement within 5 points of the yardstick: 0.55 each.
- **Criterion.**
  - SWE PLp: ρ(NR) weaker than −0.45 (released −0.55): 0.45.
  - ProgramBench PLp: ρ(NR) weaker than −0.40 (released −0.49): 0.45.
- **Length.** NR labels correlate more with prompt length than the released labels, in at least 5 of the 9 sets:
  0.6.
- **Shift.** NR PLp has a mean shift of at least +0.15 against released: 0.4. NR tends to pick a higher level when
  not made to check the conditions.
- **Compliance.** At least 95% of NR answers are the bare sentence: 0.8.

## Cost

About 19 weekly points by the runner's estimate (Opus-low calibration). NR calls are shorter, so probably less.
Usage was 94% at launch on 2026-10-06, with a reset at 22:00 CEST. Order of launch: the reference runs and
`noreason-ms` first, then `noreason-pl`, which carries on after the reset.

## Amendment 1 (2026-10-06, before any no-reasoning label was collected)

**The change.** At Pablo's request, the no-reasoning judge now answers with the bare digit. The closing sentence
"The level of … demanded by this task is: N" is gone.
- The final instruction now reads: "Answer with the level alone, as a single digit from 0 to 5, and nothing else."
- Everything before it is identical to the v2 prompt (tested).
- `extract_demand_level` now also accepts a response that is exactly one digit from 0 to 5. All other inputs parse as
  before.

**What happened to the first no-reasoning relays.**
- Two `noreason-ms` relays had started with the sentence format. They were stopped after 132 answers.
- All 132 answers were the bare sentence (median 77 characters). None was collected.
- They are kept, not analysed, in `aborted/` and in `judge-io/_aborted/`.
- `noreason-ms` and `noreason-pl` were re-pinned with the new prompt. The reference runs are unaffected.

**New check: hidden thinking.**
- The compliance check now counts answers that are a bare digit. The 0.8 prediction stands for that.
- I also report how many judge transcripts carry a thinking block, and how long those blocks are, in both arms.
- So far, in the sentence-format relays, 12 of 137 transcripts had a thinking block (0–240 characters). In the
  reference arm, 38 of 300 did.

## Amendment 2 (2026-10-06, before any no-reasoning label was collected)

At Pablo's request, the no-reasoning arm now covers every set the released (reasoning) labels cover. Each new spec is
its reasoning twin with only the run name and builder changed.

| run | twin | cells |
|---|---|---|
| `noreason-ms-rest` | MS rows of relabel-v2 on the six non-tau2 single-read sets | 1,548 |
| `noreason-long` | relabel-v2-long (ProgramBench's 13 long tasks, chunked judge) | 65 |
| `noreason-eqbench4` | relabel-v2-eqbench4 | 600 |
| `noreason-cooperbench` | relabel-v2-cooperbench | 1,200 |
| `noreason-gamearena` | relabel-v2-gamearena | 120 |

The decision rule and the predictions above are unchanged and still apply to the primary sets. On the new sets I
report agreement with the released labels, level counts and, where `ms-benchmarks` defines an outcome, ρ. These are
secondary. Pablo asked to run until the weekly quota runs out. Order: `noreason-ms` and `noreason-pl` first, then the
social sets, `noreason-long` and `noreason-ms-rest`.

## Amendment 3 (2026-10-06, before the decision rule is applied; 2,800 of 7,595 no-reasoning cells labelled)

1. **Reference labels for the social sets.**
   - `release.current_labels` covers only the agentic sets, so the analysis had no reasoning labels for EQ-Bench 4,
     CooperBench and Game Arena.
   - `analysis/analyse.py` now also reads those sets' relabel-v2 runs. relabel-v3 overrides take precedence, as in
     the releases.
   - No decision rule changes. The social sets stay secondary.
2. **Cost per label, a secondary analysis at Pablo's request ("cost vs precision").** `analysis/cost.py`:
   - **Harness cost per label.**
     - Input-side tokens come from the judge transcripts.
     - Output is estimated from the written content at 3.6 characters per token. The transcripts' `output_tokens` are
       a mid-stream snapshot and undercount.
     - Priced at Opus 5.5 rates: $4, $5 cache write, $0.20 cache read and $20 per million tokens.
   - **Wall-clock per judge call.**
   - **A plain-API counterfactual:** the prompt plus the answer, at standard and batch prices.
   - Reported for all cells and for matched cells, i.e. the reference subset judged in both arms.
   - Results are reported next to the precision results. Nothing is decided on cost.
