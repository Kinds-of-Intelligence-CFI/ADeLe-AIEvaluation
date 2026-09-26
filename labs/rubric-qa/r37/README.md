# Round 37 — finish PLe: noise floor, then the settles-vs-shows candidate, then the L5 guard

Executes the order fixed in the 2026-07-30 record: **(1) noise floor first, (2) candidate
against that floor, (3) L5 scoping as a separate change with its own test.** From that record:
PLe conclusions need median-of-3; single samples are uninterpretable for this dimension
(osw-0006 scored 1,5,5,5 across identical-text opus repeats).

## Arms

- **ARM A (noise floor / regression):** current committed text (`PLe_current.txt`, the
  2026-08-16 version). Also serves as the pending post-differentiation-rewrite regression.
- **ARM B (candidate):** `PLe_v2b.txt` — reconstruction of the uncommitted 2026-07-30
  candidate from its recorded recipe: *a check counts as feedback when running it settles
  whether the step did what it was for*, expressed inside the L1/L2/L3 definitions, zero
  marker words. The original closed 4/6 splits (ab-0002 3/1→3/3, ab-0017 3/1→3/3,
  usaco-0002 2/3→3/3, swe-0090 2/3→2/2) but was not committed because the measurement
  could not be distinguished from noise. The original file is lost (previous container);
  the old sealed sha256 will not re-verify — treat this as a NEW candidate requiring a
  fresh seal.

## Item set

The 16-instance set of the 2026-07-30 run, reconstructed from the instance pipeline
(branch `benchmark-results`, canonical join keys). Recorded IDs to include verbatim:

- disputed (the six splits): ab-0002, ab-0017, osw-0004, usaco-0002, swe-0090, tau-0089
- stability anchors: tau-0007, tau-0106 (stable 5s), osw-0002, osw-0006 (the 1,5,5,5 item)
- plus the remaining items of the 16-set from `plp_ple_results.csv` if recoverable; if not,
  fill to 16 from the same five benchmarks via the pipeline and MARK the substitutes —
  their numbers start fresh baselines, not comparisons.
- L5-guard probes (part 3): the kill-frozen-process item (destructive-but-intended, must
  NOT score 5 under the restored guard) + one true point-of-no-return item (must stay 5).

## Protocol (unchanged house rules)

One dimension per prompt, one instance per call, never batched, never Fable; judges
haiku/sonnet/opus as session subagents; prompt built in the repo's
`build_annotation_prompt` format; deciding phrase + rejected runner-up required.
**Median-of-3 seeds per judge×item cell, both arms.** Expected volume: 16 items × 3 judges
× 3 seeds × 2 arms ≈ 288 calls + ~18 probe calls.

## Decision rule (fixed before any judge runs)

1. Establish the ARM-A floor: per-item across-seed spread; an item's cell is UNSTABLE if
   its three seeds span ≥2 levels.
2. ARM B is adopted only if, on the six recorded splits, the judge–judge gap closes
   (within-1) in cells that are STABLE in both arms — improvement inside noise counts as
   nothing.
3. ARM B must not regress: no stable-cell agreement lost elsewhere, PLp/PLe separation
   signature (task-dependent difference, no constant offset) preserved on the co-annotated
   items.
4. L5 guard: kill-process ≤4 AND point-of-no-return = 5, median-of-3, else the guard text
   needs its own round — do not bundle with the feedback fix.
5. PLe declared READY only if: α (ordinal, medians) ≥ 0.80 on the 16-set, no 2-level
   median gaps, and the two traps of §6 (budgets 5, per-step validation 1) still hold.

## Seals

Claude's per-item expected medians for both arms are written to `sealed_predictions_r37.md`
BEFORE any judge call and hashed; Pablo's labels, if he pre-registers, take precedence as
the human anchor.
