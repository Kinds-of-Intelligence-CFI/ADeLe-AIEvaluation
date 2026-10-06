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
