# r40 sealed predictions — PLs battery, generating round (2026-08-22)

Text under test: `src/adele/rubrics/data_v2/Paolo_Pablo/PLs.txt` as committed (v2-draft,
2026-08-20), unedited. Judges haiku/sonnet/opus, 3 seeds, one item per call, never Fable.

## PROTOCOL DEVIATION, DECLARED IN ADVANCE

The battery's own protocol says "Pablo labels every item FIRST; his labels double as the
human anchor." Pablo instructed the round to run without that step. Consequence, stated
plainly: **the anchor for the A/B/C items is the battery's design intent — construction-side,
not human-side.** That is legitimate for designed probes (as with probe-cave in r38/r39,
whose label held by construction), but it means this round CANNOT settle the one thing the
battery reserved for Pablo: a cell where his reading disagrees with the design is the
measured defect, and no such disagreement can be detected here. This round therefore tests
whether the TEXT delivers the DESIGN, not whether the design is right. Stage 2 must carry
that limitation forward.

## Design intents (the anchor for this round), from the battery

| item | cell | intended | prediction |
|---|---|---|---|
| A1 | chaotic dynamics + coarse answer | ≤2 | 2 |
| A2 | chaotic + very coarse | ≤2 | 2 |
| A3 | chaotic + fine | top band (4–5) | 5 |
| A4 | no interaction + exact answer | ≤2 | 2 |
| A5 | single process + exact | ≤2 | 2 |
| A6 | compounding interaction + fine | top band (4–5) | 5 |
| A7 | compounding interaction + coarse | ≤2 | 2 |
| A8 | few couplings + FINE (the off-diagonal cell) | 4 | 4 |
| B1 | control side (planning) | ≤1 | 0 |
| B2 | prediction side, same situation | 1–2 | 1 |
| B3 | belief inference, not propagation | ≤1 | 1 |
| B4 | agents as processes to propagate | 3–4 | 3 |
| B5 | specialised knowledge, one step | ≤1 | 1 |
| B6 | calculation, one equilibration | ≤2 | 1 |
| B7 | pure execution/monitoring | ~0 | 0 |
| B8 | deterministic tracing — GENUINELY OPEN | 1–3 | 2 |
| C1 | referent absent — must floor/refuse | 0 | 0 |
| C2 | dynamics named but not described | ≤2 | 2 |
| C3 | circularity: answer-sensitivity unassessable | ≤3 | 3 |

## The fusion's falsifiers (what this round is actually for)

The driver is fused: *interacting change tracked at the precision the answer requires*,
with precision as a tolerance yardstick and NOT a second axis. The fusion is refuted if:
- **F1**: A7 (compounding interaction, coarse answer) scores in the top band — precision
  would then not be doing its work, and interaction alone would be driving the score.
- **F2**: A4 or A5 (no interaction, exact answer) score ≥3 — precision would then be acting
  as an independent axis, which is exactly what the fused driver denies.
- **F3**: A8 (few couplings, fine answer) fails to reach 4 — the fineness-not-count gate in
  L4 would then not bind, and the driver would be counting couplings after all.
A1/A2 vs A3 is the same test on the same situation, varying only the answer's fineness.

## Pre-registered decision rule

PASS (proceed to Stage 2 as confirmation, not repair) iff:
1. None of F1, F2, F3 fires.
2. A1/A2/A7 ≤ 2 AND A3/A6 ≥ 4 — the precision contrast separates by ≥2 levels.
3. Routing probes hold: B1 ≤ 1, B3 ≤ 1, B7 ≤ 1 (the carves against planning, minds,
   and execution).
4. C1 = 0 (annotatability: no guessing from an absent referent).
5. ≥ 15/19 within-1 of design intent, no 2-level gap on any A-cell.
B8's placement is recorded, not scored against a pass/fail — it is a genuinely open boundary
and whatever it returns becomes Stage 2's minimal-pair target.
FAIL on F1/F2/F3 → the fused driver is refuted and PLs is re-drafted (precision split out as
a second variable), not patched.
