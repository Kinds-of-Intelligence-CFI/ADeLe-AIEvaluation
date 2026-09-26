# r51 sealed predictions — PLs v7.2 re-validation, round 1 of 2 (2026-08-22)

Text under test: `src/…/PLs.txt` v7.2. Everything below was measured against superseded
wording, so this round re-establishes it from scratch. Judges h/s/o, 3 seeds, never Fable.
Anchors are construction-side. **No human has labelled a PLs item; nothing here is a human
validation.**

## What changed since the last measured wording

1. Driver restated: demand rises with how much change must be carried forward, how much of
   it interacts, and how finely the answer discriminates. A rule that yields the answer
   without stepping through the course keeps the demand low.
2. **r47 scope clause added**: the demand is scored on what the task asks for, and running a
   situation forward merely to settle what to do belongs with the choice it serves.
3. Prose voiced to v1; examples rewritten as concrete instances; three situations recur
   across levels.

## Predictions

| item | tests | predicted |
|---|---|---|
| A1 ice, coarse | precision contrast, low arm | 2 |
| A2 rain somewhere, very coarse | same | 2 |
| A3 which valley, fine | precision contrast, high arm | 5 |
| A4 thrown ball, exact | **F2** precision is not a second axis | 2 |
| A5 compound interest, exact | **F2** | 2 |
| A6 which pocket, fine | precision contrast, high arm | 5 |
| A7 any ball any pocket, coarse | **F1** interaction alone must not reach the top band | 3 |
| A8 trough below threshold | **F3** fineness-not-count gate | 4 |
| B1 plan to get the cat down | planning carve | 1 |
| B3 Sally and the marble | mind-modelling carve | 1 |
| B7 reconcile the ledger | execution carve | 0 |
| P1-absent | L0 absent-referent clause | 0 |
| P1-present | the clause must not over-floor | 2 |
| X1-mutual road closure | coupling arm | 3 |
| X2-chain dominoes | chain arm | 2 |
| X5-mutual rabbits decade | coupling arm | 3 |
| X6-chain message relay | chain arm | 2 |
| **P3a-do** maximum matching | **r47 scope clause, do-arm** | 0 |
| **P3b-predict** pairing to fixed point | **r47 scope clause, predict-arm** | 4 |

## Pre-registered decision rule

PASS round 1 iff all of:
1. **Falsifiers do not fire**: A7 ≤ 3, A4 ≤ 2 and A5 ≤ 2, A8 ≥ 4.
2. **Precision contrast separates by ≥2**: A1/A2 vs A3, and A7 vs A6.
3. **Coupling boundary separates**: each X-mutual ≥ 3 and each X-chain ≤ 2, no overlap.
4. **Carves hold**: B1 ≤ 1, B3 ≤ 1, B7 ≤ 1.
5. **L0 clause binds both ways**: P1-absent = 0, P1-present ≥ 1.
6. **The new scope clause behaves**: P3b-predict − P3a-do ≥ 2. If the clause has broken
   something, the do-arm will have risen; P3a-do > 1 is a failure even if the gap holds.
7. ≥ 17/19 within-1 of prediction, no 2-level gap on any A-cell.

Any failure of 1, 3 or 6 stops adoption and sends the relevant clause back to text.
Round 2 (family diagonal against PLp and PLe) runs only if round 1 passes.
