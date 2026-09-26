# Stages 3 and 4 — PL family discrimination and the PLp fix (2026-08-22)

Judges h/s/o, 3 seeds, one item per call, never Fable.
Seal: `sealed_predictions_stage3.md` (sha256 81c514b0…). Raw: `results_stage3.csv`,
`../stage4/results_stage4.csv`. Stage 3 ran PLp **unfixed**, by design.

## Headline: the Stage-0 text-read was WRONG. The drafted PLp fix is not needed.

Stage 0 concluded by reading that PLp fails desideratum 2 because its upper levels are
defined through lookahead. Stage 3 measured it. The cross-scoring matrix (ensemble medians,
9 items × 3 rubrics):

| item | built for | PLp | PLe | PLs |
|---|---|---|---|---|
| PLp-1 wedding seating | PLp | **3** | 1 | 0 |
| PLp-2 exam timetabling | PLp | **3** | 1 | 0 |
| PLp-3 chess middlegame plan | PLp | **3** | 0 | 4 ← |
| PLe-1 sealed-suit protocol | PLe | 0 | **5** | 1 |
| PLe-2 survey transcription | PLe | 0 | **4** | 0 |
| PLe-3 compliance report | PLe | 1 | **3** | 0 |
| PLs-1 reservoir + sluice feedback | PLs | 1 | 0 | **4** |
| PLs-2 two-firm price war | PLs | 1 | 0 | **4** |
| PLs-3 gear train | PLs | 0 | 0 | 2 ✗ |

Diagonal holds 8/9. **Exactly one off-diagonal leak: PLp-3 × PLs = 4.**

## What the leak actually is

The controls settle it. PLp-1 and PLp-2 are high-planning *without* lookahead — constraint
satisfaction over a static situation — and they score **0** on PLs. Stage 4 added PLp-4
(contest-programming approach choice, lookahead-flavoured but abstract): PLp 3, PLs **0**.
So the leak is not a general PLp→PLs contamination. It is specific to chess, where a plan
genuinely cannot be evaluated without running the position forward.

Stage 4 then applied the drafted exclusion to PLp and re-scored. **PLp's scores did not move
on any item** — the chess plan stayed at 3, and opus's reasoning shows why: the exclusion's
own carve-back ("consequences bear on it only as what makes candidates hard to tell apart
before committing") is precisely the role consequences play in chess. The fix is inert on
the case it was drafted for.

**Double dissociation, measured in both directions:**
- PLp high / PLs low: PLp-1 (3, 0), PLp-2 (3, 0), PLp-4 (3, 0)
- PLs high / PLp low: PLs-1 (1, 4), PLs-2 (1, 4)
- Co-load: PLp-3 chess only (3, 4)

A co-load on one task *type* is a property of that task, not of the rubrics. Desideratum 2
for PLp↔PLs is therefore **met, measured** — the opposite of the Stage-0 reading.

## Recommendation: do NOT apply the PLp fix

The project's stopping rule is *no rubric text change without a measured wrong score first*,
with adversarial text-reads running about 2 in 15. This one was a miss, and Stage 3 is the
measurement that says so. The drafted clause is harmless (it changed nothing) but unjustified,
and applying an inert clause weakens the rule that has kept this catalogue honest.
`PLp_r43_candidate.txt` is kept as a record, not proposed. **PLp's text stays as committed.**

## Also measured

- **PLe↔PLs and PLe↔PLp are clean.** PLe's items score 0–1 elsewhere; no other dimension
  reaches 3 on a PLe item. This closes desideratum 2 for PLe, which the audit had at ⚠️.
- **Desideratum 6** (examples/items disentangle) is now supported for all three: every
  designed item loads its own dimension and stays ≤1 elsewhere, chess excepted.

## My own failure in this round

PLs-3 (gear train) scored 2 on its own dimension and fails the ≥3 diagonal, so it is dropped
from the analysis per rule 1. The reason is worth recording: a gear train is a *sequential
chain*, not mutual coupling — the identical mistake I made with the domino probe in r41.
Twice now I have built a chain when the design called for coupling. Any future PLs item
intended to load L3+ must be checked against that specific error.

## What remains for PLs

Unchanged by these rounds: the one six-item boundary round (mutual coupling vs sequential
chain, coarse answers), and **the standing fact that Pablo has never labelled a PLs item.**
Stages 3 and 4 were legitimate without human labels because their claims are relational —
a diagonal and a dissociation, not a level placement. That exemption does not extend to the
boundary round.
