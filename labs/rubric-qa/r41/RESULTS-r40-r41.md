# PLs — Stage 1 (r40, generating) and Stage 2 (r41, confirming). 2026-08-22

Judges haiku/sonnet/opus, 3 seeds, one item per call, never Fable.
Seals: r40 `sealed_predictions_r40.md` (sha256 57a3ce23…), r41 `sealed_predictions_r41.md`.
Raw seeds: `../pls-r40/results_r40.csv`, `results_r41.csv`.

## Verdict: the fused driver SURVIVES. PLs does NOT yet clear — one pre-registered rule failed.

### r40 (generating round, 19 battery items, committed PLs text)

All three falsifiers of the fused driver failed to fire:
- **F1** — A7 (compounding interaction, coarse answer) did NOT reach the top band (3, not 4–5).
- **F2** — A4 and A5 (no interaction, exact answer) stayed at 2; precision does **not** act as
  an independent axis.
- **F3** — A8 (few couplings, FINE answer, the off-diagonal cell) reached **4**; the
  fineness-not-count gate binds.
The precision contrast on one and the same situation separated by three levels:
A1/A2 (coarse) = 2 vs A3 (fine) = 5; and A7 (coarse) = 3 vs A6 (fine) = 5.
**This is the central claim of the dimension and it held.**

Routing carves held: B1 (planning side) = 1, B3 (belief inference) = 1, B7 (pure execution)
= 0, B5 (specialised knowledge, one step) = 1. B4 (agents as processes) = 3 as designed.
18/19 within-1 of design intent, 16 exact, α = 0.971.

Two departures:
- **C1 = 2, intent 0** (the only 2-level miss): given "predict the outcome of the experiment
  described in the attached protocol" with no protocol, judges invented a generic experiment
  and scored it. A real annotatability defect.
- **A7 = 3, intent 2**: judges reasoned that in a billiards break the coupling is
  *constitutive* — balls move only by being struck — so even a coarse answer needs it
  propagated. **The rubric was working; the design intent was wrong.**

### r41 (confirming round, 10 items, PLs + one L0 clause)

| rule | result |
|---|---|
| 1. absent-referent clause binds both ways | ✅ P1-absent = 0, P1-present = 2 |
| 2. constitutive vs independent coupling separates | ❌ **2 vs 2 — no separation** |
| 3. deterministic tracing: interacting vs single | ✅ 4 vs 2 |
| 4. traps hold (A6 5, A8 4, B7 0, A7 3) | ✅ all four |
| 5. ≥9/10 within-1, no 2-level gap | ✅ 10/10, α = 1.0 |

**Rule 2 failed, so PLs does not clear.** Diagnosis: the probe, not the rubric. I built the
"constitutive" arm as a domino chain, and judges correctly observed that a chain is
*sequential one-directional causation*, not mutual influence — "each domino's fall is
independently guaranteed by the stated spacing condition." Billiards has momentum exchanged
in both directions; dominoes do not. So the pair tested the wrong contrast and A7's
placement at 3 remains explained by judge reasoning but **unconfirmed by measurement**.

Note also **P3-interacting = 4 against a predicted 3** (within-1): the two-queue trace was
finer than intended — the asked-for predicate (queue 2 empty while queue 1 holds ≥3) is
exactly the kind of fine answer L4 keys on. That is the rubric behaving correctly on an
item I mis-predicted.

## What is needed to close PLs

One short round (~6 items), testing the contrast that r41's probe missed, all with COARSE
answers: mutual coupling (traffic rerouting; predator–prey trend; two-shop price war) vs
sequential chain (dominoes; a relay of messages; a falling stack) — prediction: mutual = 3,
sequential = 2. If it separates, A7's 3 is confirmed and the L2/L3 boundary of PLs is
measured rather than argued.

## Standing limitation — the one that matters most

**Pablo has still never labelled a PLs item.** Every anchor in r40 and r41 is
construction-side or Claude's. Across PLe's rounds the anchor proved wrong four times and
the rubric text zero times; on this evidence the anchor is the method's weak point, and PLs
currently has no human anchor at all. Nothing above should be reported as human-validated.
The cheapest fix is Pablo labelling the r41 ten blind and comparing.

## Text status
`PLs_r41_candidate.txt` (committed PLs + L0 absent-referent clause) is **validated for that
clause** by rule 1 and is safe to adopt. The rest of PLs is unchanged from the committed
text. No edit is proposed for A7's boundary until the closing round measures it.
