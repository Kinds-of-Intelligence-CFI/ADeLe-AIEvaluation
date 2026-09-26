# Round 76 — PLe v2-r45 example move measured (2026-08-26)

Seal: `sealed_predictions_r76.md` (sha256 889395ab, written before judging, after the edit).
Judges h/s/o, one item per call, median of three, meta-stripped, examples kept.

## PASS: 4 of 4 medians equal the predictions. 11 of 12 cells exact.

| id | item | h | s | o | median | predicted |
|---|---|---|---|---|---|---|
| T1 | tau-0007 | **2** | 1 | 1 | **1** | 1 ✓ |
| T2 | tau-0146 | 1 | 1 | 1 | **1** | 1 ✓ |
| T3 | commissioning, forced arm | 2 | 2 | 2 | **2** | 2 ✓ |
| T4 | commissioning, elected arm | 3 | 3 | 3 | **3** | 3 ✓ |

Gate 2 (T3 must not fall to 1): HELD, unanimous — all three judges cited the juncture clause
and two explicitly distinguished stage boundaries from per-action returns. Gate 3 (tau ≤ 1):
HELD. The minimal-pair separation replicated r39 at every cell.

## Honesty notes, both against the round's own strength

1. **The tau cells are corroboration, not independent evidence.** Sonnet and opus matched
   T1/T2 to the relocated example nearly verbatim, and my framing parenthetical ("tool calls
   that each return whether they succeeded") paraphrases it. The independent evidence for the
   re-key remains r39, which measured these items at 1 with no such example in the text.
   The genuinely load-bearing cell of r76 is T3.
2. **The 4-gram independence check ran post-hoc, not at seal time** (omission — r75's lesson
   half-applied). One hit: T4 shares "a stage was done right" with the flat-pack L2 example.
   The bias runs against the prediction (toward 2), and T4 still measured 3 unanimously, so
   the cell stands, but the check belongs in the seal and the omission is recorded.

## Decisions this round closes

- PLe.txt v2-r45: the tool-interface example moved L2 → L1 VERBATIM (option (a) of the
  conflict in anchors-PLe-tau-rekey.md), on Pablo's delegation of 2026-08-26. The measured
  basis is r39's tau medians; r76 confirms the surrounding boundary is unperturbed.
- The tau re-key sheet is ADOPTED: tau-0007/0106/0146/0089/0094 PLe anchors = 1.
