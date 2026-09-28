# plp-candidate — results

**Question.** Does a change to Level 3 make the PLp judge read the 2/3 boundary as Pablo does?

**Answer.** No. None of the three candidates passed.
- Candidate A, a replaced sentence, moved none of Pablo's three Level-2 Terminal-Bench tasks.
- Candidate B, an explicit Level 3 rule, moved one of them: `html-js-filter`.
- Candidate C, a knowledge carve in the scope paragraph, moved the same one.

The other two tasks stayed at Level 3 under every version and both effort levels. Details for A
follow; B and C have their own sections below.

Candidate A in detail: Pablo's three Level-2 Terminal-Bench tasks stayed at Level 3 under it.
On Terminal-Bench, the candidate put slightly more tasks at 3, not fewer. It did no harm elsewhere:
the SWE-bench and tau2 correlations held or rose slightly. The pre-registered verdict is "no
effect".

**Status.** Complete (2026-09-28). No candidate passed its decision rule. Candidate C then passed
the lab regression (`lab-regression/RESULTS.md`); D, its first clause alone, did not. Which sentence
to adopt is Pablo's decision, and `PLp.txt` is unchanged.

## Design

See `PREREGISTRATION.md`, committed before any label (`2442bdc`).

- **Candidate.** One Level 3 sentence is replaced.
  - Old: "An option that looks good locally can be wrong because of its consequences several steps
    later, so alternatives must be compared by looking ahead before committing."
  - New: "The best choice at one step depends on choices at other steps, so options must be
    compared before committing."
- **Judge.** Opus at low effort, one call per task, as in the main studies.
- **Runs.**
  - `cand-tb` and `ctrl-tb`: candidate and current text on the 34 Terminal-Bench tasks. The
    control measures noise.
  - `cand-swe`: 60 SWE-bench tasks.
  - `cand-tau2`: 232 tau2 tasks.
- **Labels.** 360 cells, all parsed. One answer was written by another model: `uefi-bootkit` in the
  control. Its retry fell back too, so it has no label.

## Pre-registered results

From `results/compare.json` (`analysis/compare.py`).

| rule | result | passed |
|---|---|---|
| 1. Pablo's three Level-2 tasks move to 2 | candidate 3, 3, 3; control 3, 3, 3 | no |
| 2. No harm on SWE-bench (60 tasks) | ρ with solve rate −0.70 against −0.63 on the reference labels; mean shift +0.10 | yes |
| 3. No harm on tau2 (within domain) | ρ −0.36 [−0.48, −0.24] against −0.33; p 4e−8 | yes |

The verdict is "no effect".

The sealed predictions:
- rule 1 passes (0.45): failed;
- rule 2 passes (0.85): held;
- rule 3 passes (0.7): held;
- "helps" (0.3): did not happen.

Level counts:

| | Level 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| Terminal-Bench, candidate | 0 | 0 | 2 | 30 | 2 |
| Terminal-Bench, control | 0 | 0 | 5 | 26 | 2 |
| Terminal-Bench, original run | 0 | 0 | 4 | 26 | 3 |
| tau2, candidate | 0 | 29 | 189 | 14 | 0 |
| tau2, original run | 0 | 25 | 198 | 9 | 0 |
| SWE-bench sample, candidate | 2 | 28 | 24 | 6 | 0 |
| SWE-bench sample, original runs | 2 | 31 | 24 | 3 | 0 |

## Exploratory results

- **Judge noise.** The control agrees with the original run on 88% of the Terminal-Bench tasks.
- **The candidate moved tasks up, not down.** Candidate against control: exact 85%, mean shift
  +0.09.
- **Agreement with Pablo's six labels.** Candidate 2, control 2, original run 3.
- **Why it did not bind.** The judge finds real dependencies between choices in these tasks. On
  `html-js-filter`: "the parser you pick decides whether the formatting survives". On
  `risk-scorer-replay`: "which probes to design depends on the hypotheses". The new sentence names
  that dependence, so the judge reads it as met.
- **PLp against solve rate on Terminal-Bench:** candidate +0.19, control +0.02 (n = 33, no test).

## Candidate B: an explicit rule

Added after A's result, pre-registered before any label of B (`f2148ce`). One sentence is added
to the current Level 3: "Critically, a poor option that a standard choice avoids does not make
the decisions interact." Level 3 grows from 93 to 108 words.

| rule | result | passed |
|---|---|---|
| 1. At least 2 of Pablo's three Level-2 tasks move to 2, and his two Level-3 tasks stay at 3 | `html-js-filter` 2, `layout-config-recreation` 3, `risk-scorer-replay` 3; control 3, 3, 3. His Level-3 tasks stay at 3 | no |
| 2 and 3. No harm on SWE-bench and tau2 | not run: stage 2 runs only if rule 1 passes | — |

The verdict is "no effect". Sealed prediction: rule 1 passes, 0.5, failed.

**Exploratory, candidate B:**
- **Terminal-Bench levels.** At Level 2: 7 tasks (control 5). At 3: 24 (26). At 4: 3 (2).
- **Agreement.** Exact with Pablo's six labels: 3 (control 2). Against the control: exact 85%,
  mean shift −0.03.
- **The rule works as written.** On `html-js-filter`, the judge now says: "Avoiding a poor option
  like naive regex is not the same as the decisions truly interacting."
- **On the other two, the judge names interactions the rule does not cover.**
  - `layout-config-recreation`: a limited budget of vector shapes must be shared across the missing
    artwork. "Allocating limited resources" is in the rubric's own definition of planning.
  - `risk-scorer-replay`: the code must generalise to unseen test packets. This is close to the
    "poor option" pattern, so it is borderline.
- **The remaining disagreement is judgment, not wording.**

## Candidate C: a knowledge carve

Added after B's result, pre-registered before any label of C (`3043a15`). One sentence is added
at the end of PLp's "What this dimension does not cover" paragraph, mirroring PLs's knowledge
carve: "Knowing the established method is knowledge rather than planning, so pitfalls that the
method avoids do not raise this demand." The levels are unchanged.

| rule | result | passed |
|---|---|---|
| 1. At least 2 of Pablo's three Level-2 tasks move to 2, and his two Level-3 tasks stay at 3 | `html-js-filter` 2, `layout-config-recreation` 3, `risk-scorer-replay` 3; control 3, 3, 3. His Level-3 tasks stay at 3 | no |
| 2 and 3. No harm on SWE-bench and tau2 | not run | — |

The verdict is "no effect". Sealed prediction: rule 1 passes, 0.3, failed as expected.

**Exploratory, candidate C:**
- **Terminal-Bench levels.** At Level 2: 7 tasks (control 5). At 3: 25 (26). At 4: 2 (2).
- **Agreement.** Against the control: exact 94%, mean shift −0.06. Exact with Pablo's six
  labels: 3 (control 2).
- **Same effect as B, lower cost.** C moves the same task and needs no Level 3 guard.
- **Harm checks, run under deviation 1 at Pablo's request.** C did no harm.
  - SWE-bench, 60 tasks: ρ with solve rate −0.70 against −0.63 on the reference labels, mean shift
    +0.03.
  - tau2, within domain: ρ −0.35 [−0.47, −0.23] against −0.33 (airline −0.49, banking −0.26,
    retail −0.35). Tasks at Level 3: 6 (reference 9).
  - There is no control run on these two benchmarks, so read the small gains as noise.
  - All 292 answers were written by `claude-opus-5-5`.
- **The two remaining tasks.** The judge still reasons that early choices "may need to be revised
  after looking ahead" on `layout-config-recreation`, and that options must be compared "with an
  eye to what comes later" on `risk-scorer-replay`. This reading held under every version and
  both effort levels.

## Lab regression of candidate C

Pre-registered separately (`lab-regression/PREREGISTRATION.md`, `86de254`). Three judges (haiku,
sonnet, opus) scored 99 lab items under the current text and under C: example placement, examples
disentangle, minimal pairs, family diagonal and battery-v1. C passed: nothing that holds under the
current text breaks under C. Placement and the minimal pairs gave identical levels. One battery
loss in pass 1 did not repeat in pass 2. The new sentence was quoted in 5 of 297 answers, so on
designed items it rarely fires. Candidate D, C's first clause only, failed the same regression by
one confirmed two-level move and lowers labels more broadly than C. Details in
`lab-regression/RESULTS.md`.

## Deviations and caveats

- **Deviation 1:** candidate C's stage 2 ran although its rule 1 failed, at Pablo's request, to
  judge C as a principled change. C's verdict stays "no effect".
- **One call per task.** SWE-bench and tau2 have no control run, so their small gains may be noise.
- **Paolo's blind labels are still pending.** They would show whether the stricter reading of the
  2/3 boundary is shared by both authors.
- **What this means for the rubric.** A sentence that names dependence does not change the
  judge's reading. A stricter reading would need an explicit rule. The earlier draft had one ("That
  some options would fail later is not enough where the kind of task supplies a standard choice
  that avoids them"), but it makes Level 3 longer than any v1 level.

## Reproduce

```
python experiments/benchmarks/plp-candidate/analysis/compare.py
```

The numbers above are those committed with this file. Prompts and the judges' reasoning stay out of
the repo.
