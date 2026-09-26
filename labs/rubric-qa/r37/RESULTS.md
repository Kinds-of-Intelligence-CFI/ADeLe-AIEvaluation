# Round 37 results — PLe noise floor + v2b candidate + L5 guard (2026-08-20/21)

**Judges:** haiku/sonnet/opus subagents, one item per call, 3 seeds per judge×item, never Fable.
Sealed predictions: `sealed_predictions_r37.md`, sha256 f4cb7f6b… (written before any judge ran).
ARM A = current 2026-08-16 committed PLe text, 20 items + 2 designed probes (198 calls).
ARM B = reconstructed v2b "settles-vs-shows" candidate, run on the 4 split items + 2 stable
controls (protocol deviation from the full-20 plan, declared: A's verdict pattern made the
remaining 10 duplicates uninformative for the fixed decision rule). Raw seeds:
`results_A.csv`, `results_B.csv`.

## Headline verdicts

1. **PLe is NOT ready.** Judge-median agreement across the 20-item set is dominated by a
   systematic judge offset (haiku ≈ 3, sonnet ≈ 1, opus ≈ 2 on most items); interval-approx
   α on judge medians ≈ 0.12. Sealed-prediction agreement: 10/20 exact, 18/20 within-1.
   Level usage collapsed to 1–3 on all natural items.
2. **NEW MEASURED DEFECT — the irreversibility band collapsed on tool-mediated tasks.**
   tau-0007 and tau-0106, recorded 5/5 by both annotators on 2026-07-30, now score median 1
   (both arms). Judges reason: per-call API returns = Level-1 feedback, and L5's
   "not that some action in it happens to be destructive" clause + tie-break-lower gives an
   off-ramp from irreversibility. Yet **the L5 guard itself passed its designed probes**:
   probe-kill (destructive-but-intended) = 1 ≤ 4 ✓ and probe-filing (unamendable submission)
   = 5 ✓. So L5 is reachable when irreversibility is the stated crux, but agentic tasks whose
   crux is an unretractable tool call fall through: judges read the confirming return as
   "error caught and corrected on the spot" without noticing correction is impossible.
3. **ARM B (v2b) NOT ADOPTED**, per the pre-registered rule. Of the four splits:
   tau-0146 closed (gap 2→1); ab-0017 improved (gap 2→1) but with unstable cells;
   ab-0002 and tau-0007 unchanged. Controls (swe-0090, usaco-0002) did not regress.
   Partial closure with instability does not meet "splits close in cells stable in both arms".

## Per-item medians, ARM A (h/s/o | overall | sealed pred)

swe-0090 3/2/2|2|2 · swe-0254 3/2/2|2|2 · swe-0283 4/2/2|2|2(2-gap) · swe-0445 2/1/2|2|2 ·
swe-0461 3/2/2|2|2 · ab-0002 3/1/2|2|2(2-gap,unstable) · ab-0017 3/1/1|1|2(2-gap,unstable) ·
ab-0011 2/1/2|2|2 · ab-0020 2/1/2|2|1 · ab-0024 2/1/2|2|2 · usaco-0002 3/3/2|3|2 ·
usaco-0004 3/3/2|3|2 · usaco-0006 3/2/2|2|2 · usaco-0010 3/3/3|3|2 · usaco-0011 3/3/2|3|2 ·
tau-0146 3/1/1|1|2(2-gap) · tau-0089 2/1/1|1|2(unstable) · tau-0094 2/1/2|2|2(unstable) ·
tau-0007 3/1/1|1|**5**(2-LEVEL MISS) · tau-0106 2/1/1|1|**5**(2-LEVEL MISS) ·
probe-kill 2/1/1|1|≤4 ✓ · probe-filing 4/5/5|5|5 ✓

## Diagnosis

The three defects, in causal order:
- **(D1) Feedback-referent ambiguity, generalized.** The old "what counts as feedback" split
  has become "what is the action's purpose": sonnet/opus anchor on the tool call (return =
  per-action feedback → L1); haiku anchors on the task goal (no settling → L2-3). v2b's
  settles-vs-shows clause moves haiku/opus slightly but does not bind sonnet.
- **(D2) Recoverability dropped out of L1.** L1 says errors are "caught and corrected on the
  spot"; judges verify "caught" and never test "corrected". For irreversible calls the
  correction half is false, but nothing in the text forces the check. This is the mechanism
  behind D2's tau collapse, and it interacts with the L5 guard clause.
- **(D3) Within-model noise persists** (5/22 items with a ≥2 seed spread; opus 2,4,1 on
  tau-0094) — smaller than July's osw-0006 case but still above text-effect size on
  affected cells. Median-of-3 remains mandatory.

## Recommended next round (r38) — NOT executed, needs Pablo's pre-registration

One candidate edit, targeted at D1+D2 jointly, in L1's definition sentence:
*"…settles on the spot whether that action did what it was for — **and, if it did not, the
step can still be redone**: a return that only confirms an unretractable step has executed
places the task at the level its recovery demands."* Predicted effects: tau-0007/0106
recover toward 4–5; probe-kill must stay low (the kill is the intended outcome, recovery =
service restarts); research items unaffected. Test on the tau family + both probes + 4
stable controls, fresh seeds, Pablo's labels first.

## Honesty notes
- osw-0002/0004/0006 unrecoverable (id→task mapping lost with the July container); the
  noise-star item is gone from the comparison set.
- ARM B trimmed (declared above); v2b is a reconstruction, old seal void.
- Two earlier non-judge review agents (PLw and MSm adversarial reviews) ran on the session
  model (Fable) by omission of a model override; all r37 judges were haiku/sonnet/opus.
  Policy from 2026-08-21: every subagent gets an explicit model, Opus by default.
