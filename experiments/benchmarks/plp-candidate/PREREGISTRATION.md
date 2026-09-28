# plp-candidate — pre-registration

Committed before any label of this study, with the analysis script.

**Question.** Does a new Level 3 sentence help PLp? The candidate replaces one sentence of Level 3.

- Old: "An option that looks good locally can be wrong because of its consequences several steps
  later, so alternatives must be compared by looking ahead before committing."
- New: "The best choice at one step depends on choices at other steps, so options must be compared
  before committing."

Nothing else changes. The full text is in `PLp_candidate.txt`.

**Why.** In the human check of `tau2-tb4-pl`, Pablo put 3 of the judge's 5 Level-3 Terminal-Bench
tasks at Level 2. Opus at max effort kept them at 3. Its reason was that an early choice could turn
out wrong later. The new sentence asks instead whether the best choice depends on other choices.

## Design

- **Judge.** Opus at low effort (`adele-judge-low`), as in the main studies, through relays
  `judge-dispatcher-low`. One call per task.
- **Runs.**
  - `cand-tb`: the candidate on the 34 Terminal-Bench analysis-set tasks.
  - `ctrl-tb`: the current text on the same 34 tasks. This measures judge noise.
  - `cand-swe`: the candidate on 60 solvable SWE-bench tasks: the 3 at PLp 3 under Opus low, plus
    57 drawn with seed 20260928.
  - `cand-tau2`: the candidate on all 232 tau2 tasks.
- **References.** The Opus-low labels of `tb4pl-r1`, `tau2pl-r1`, `swepl-gate-low` and
  `swepl-r1-low`, and Pablo's blind labels.
- **Only the sentence differs.** Prompts built with the current text reproduce the original
  prompt hashes; `make_prompts.py` checks this.
- **Other models.** Amendment 2 of `tau2-tb4-pl` applies: answers written by another model are set
  aside and the cell is retried once.
- **Cost.** 360 calls, about 2% of a week.

## Decision rule

1. **Binding.** Three tasks were Level 2 for Pablo: `html-js-filter`, `layout-config-recreation` and
   `risk-scorer-replay`. The rule passes if at least 2 of the 3 are at Level 2 under `cand-tb`, and at
   most 1 of the 3 under `ctrl-tb`.
2. **No harm on SWE-bench.** On the 60 tasks, the candidate's Spearman ρ with solve rate is within
   0.10 of the reference labels' ρ on the same tasks, and the mean level shift is within ±0.25.
3. **No harm on tau2.** The within-domain combined ρ with solve rate (Q1 of `tau2-tb4-pl`) is still
   negative with p < 0.05, and within 0.10 of −0.325.

**Verdict.**
- Helps: rules 1, 2 and 3 pass.
- No effect: rule 1 fails.
- Harms: rule 2 or 3 fails.

**Also reported:**
- level counts per run;
- control against reference, the judge's test-retest agreement;
- exact agreement with Pablo's six labels, for control and candidate;
- PLp against solve rate and expert time on Terminal-Bench (exploratory).

## Predictions (sealed)

- Rule 1 passes: 0.45.
- Rule 2 passes: 0.85.
- Rule 3 passes: 0.7.
- Verdict "helps": 0.3.

## What happens next

If it helps, the candidate goes to the lab's regression: example placement, the round-36 minimal
pairs, the family diagonal, the 4-gram independence check, and three judges. Paolo's blind labels
are also still pending. `PLp.txt` does not change before then.

## Candidate B: an explicit rule (added 2026-09-28, after candidate A's result, before any label of B)

Candidate A had no effect (`RESULTS.md`). Candidate B keeps the current Level 3 and adds one
sentence right after its look-ahead sentence:

- "Critically, a poor option that a standard choice avoids does not make the decisions interact."

Level 3 grows from 93 to 108 words. The full text is in `PLp_candidate_b.txt`.

**Runs.** `guard-tb` (the 34 Terminal-Bench tasks), then `guard-swe` (the same 60) and `guard-tau2`
(the same 232). Same judge and settings as candidate A. The control is `ctrl-tb`, already run.

**Two stages.**
1. `guard-tb` only.
2. `guard-swe` and `guard-tau2`, only if rule 1 passes.

**Decision rule.** As for candidate A, with one addition to rule 1 so that pushing every task down
cannot pass:
1. **Binding.** At least 2 of Pablo's three Level-2 tasks are at 2 under `guard-tb`, and at most 1
   of them is at 2 under `ctrl-tb`. Also, the two tasks Pablo put at 3 (`ctr-optimization`,
   `photonic-waveguide-routing`) stay at 3.
2. **No harm on SWE-bench.** As for A.
3. **No harm on tau2.** As for A.

The verdict works as for A. If stage 1 fails, the verdict is "no effect" and stage 2 does not run.

**Predictions (sealed).**
- Rule 1 passes: 0.5.
- If stage 2 runs, rule 2 passes: 0.8.
- If stage 2 runs, rule 3 passes: 0.6. tau2's few Level 3s may drop to 2.
- Verdict "helps": 0.25.

**Cost.** Stage 1: 34 calls. Stage 2: 292 calls, about 1.6% of a week.

## Deviations

None yet.
