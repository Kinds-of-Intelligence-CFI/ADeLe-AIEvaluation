# Round 38 results — PLe rewrite on the checking-availability driver (2026-08-22)

Judges haiku/sonnet/opus, 3 seeds per judge×item, one item per call, never Fable.
Sealed predictions: `sealed_predictions_r38.md` (sha256 c7de1252…), written before any call.
Anchor: endorsed label set (Pablo's five + six proposed-and-endorsed + probe-cave 5).
ARM A baseline = r37 raw seeds (same text, 2026-08-20/21) for the 10 overlapping items;
probe-cave run fresh in both arms (`results_A_probe-cave.csv`). ARM B raw seeds: `results_B.csv`.

## Verdict: ADOPT, per the pre-registered rule

Per-item judge medians (h/s/o | ensemble | label):

tau-0007 2/2/1|2|2 · tau-0106 2/1/1|1|2 · tau-0146 3/1/1|1|2 · tau-0089 1/1/1|1|2 ·
tau-0094 2/1/2|2|2 · probe-kill 2/1/1|1|1 · **probe-filing 2/2/3|2|2** ·
**probe-cave 5/5/5|5|5** · swe-0090 4/3/3|3|2 · swe-0461 3/3/3|3|2 ·
usaco-0002 3/3/3|3|3 · ab-0024 3/1/3|3|2

1. Within-1 of the endorsed label: **12/12** (exact on 6). Rule required ≥11. ✓
2. **probe-filing = 2** (required ≤3). Under the old text it measured 5; the stakes-exclusion
   sentence routes it correctly — opus quoted "however consequential it is" verbatim as its
   reason. The trap that motivated the whole redesign holds. ✓
3. **probe-cave = 5, unanimous across all 9 cells.** The new L5 is reachable exactly when
   checking is needed yet impossible. (ARM A also gives probe-cave 5 — via the old
   recovery reading, h 5,4,5 — so the old text was not wrong on this item, just wrong on
   probe-filing.) ✓
4. No regression: every item that was within-1 of its label under ARM A stays within-1
   under ARM B. ✓
5. Unstable cells declared (seed spread ≥2): sonnet/tau-0007 (2,3,1), sonnet/ab-0024
   (1,1,3). Both medians unaffected. Median-of-3 remains mandatory.

## READY assessment (separate from adoption)

Interval-approx α on judge medians = **0.74** (r37: ≈0.12). The r37 judge offset
(h≈3/s≈1/o≈2, level usage collapsed to 1–3) is essentially gone: judges now use 1–5 and
mostly sit within 1 of each other. The 0.80 READY bar is not yet met; the residue is
haiku running +1 on two items (tau-0146→3, swe-0090→4) and sonnet running −1 on
tau-family/ab items. No 2-level gap between any ensemble median and the anchor. Status:
**adopted, one α-hair short of READY** — plausibly closable by judge-prompt calibration
rather than further rubric text changes.

## One construct question for the team (not a defect)

Under the new L3 clause ("the agent must decide when to check…"), swe-0090, swe-0461 and
ab-0024 read as 3 where Pablo's labels say 2 ("the checks are provided; the agent has only
to reach them"). All three judges consistently reason: nothing fires automatically, the
agent must invoke the repro/test/source-check → L3. Within-1, so it neither blocked
adoption nor breaks READY, but the boundary is now: does a task-named check the agent must
invoke count as "provided" (L2) or "self-scheduled" (L3)? Two options if 2 is the intended
answer: add to L2 "a check the task itself names — a supplied reproduction, a given
validation — counts as provided even when the agent must invoke it"; or re-anchor the
labels to 3 for solve-then-verify tasks. Team call; no edit made.

## Honesty notes
- ARM A numbers for the 10 overlapping items are r37's raw seeds, not re-run (declared in
  the sealed predictions before judging).
- Sealed-prediction accuracy this round: 10/12 ensemble medians exact, 12/12 within-1
  (misses: tau-0106/tau-0146 predicted 2, measured 1).
- Six of the twelve anchor labels were proposed by Claude and endorsed by Pablo; the five
  tau labels and probe-filing's 2 are Pablo's own.
- Deployment note (2026-08-22): the adopted text merged into src/…/PLe.txt differs from the
  judged candidate in ONE L0 example — Pablo's simplification "Find the winning move in a
  given chess position" (with a one-clause explainer) replaces the winning-line/transcription
  example. Pablo's two other direct src edits (L5 "no correctness checks are possible";
  synthesis parenthetical removed) were already subsumed by the rewrite. No probe or scored
  item targets L0, so the tested-vs-deployed gap is declared, not re-judged.
