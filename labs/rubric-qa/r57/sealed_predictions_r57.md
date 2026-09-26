# r57 sealed predictions — PLs v10, the rebuilt top band (2026-08-25)

Text under test: `/home/user/pls-v10/PLs.txt` (v10). Not yet in `src/`. Judges h/s/o, one item
per call, median of three, never Fable.

**Methodological note.** None of the ten items below appears in the rubric. Judging a rubric's
own examples is circular, and r51 and r53 both drew items from outside the text for that reason.
Each item here is structurally matched to something the text must handle but textually distinct
from it.

## What this round is for

The L5 re-key of 2026-08-22 changed the top from *precision under a known model* to *no known
model*. Until now that change had been applied to one paragraph. v10 aligns the preamble, the
driver line and the exclusions, demotes the two precision-keyed examples, and adds Pablo's
available-model case. The round asks whether the top band now discriminates on the epistemic
key rather than on precision, and whether the new forecasting pointer over-fires.

## Items and predictions

| id | item | tests | predicted |
|---|---|---|---|
| T1 | three-body star-and-two-planets, does the inner orbit cross the outer within 400 orbits | hard, chaotic, but Newtonian and established | **4** |
| T2 | rail line announced four years out; rents rise in anticipation, tenants leave before construction, departures change who the line serves; is commute time lower five years after opening | reflexive, unsettled | **5** |
| T3 | town at 41,200 growing 2.0 per cent a year for twenty years on the council's own projection; above 50,000 by 2033 | **falsifier**: a forecasting question is not automatically top band | **2** |
| T4 | 5 cm steel sphere in glycerol at 20 degrees; terminal velocity before 30 cm | **falsifier**: obscure law is knowledge, not simulating | **1** |
| T5 | two cafés on a square each match the other's loyalty scheme; does either end the quarter up | **falsifier**: coupling alone must not reach the top band | **3** |
| T6 | scrappage scheme: scrapping lifts sales, the tax funding it cuts the same households' spending, dealers raise prices; are three-year sales higher | **the decisive item**: second-order dominance with a *coarse* question | **5** |
| T7 | the T1 arrangement, with an N-body integrator and compute available | **new**: the available-model clause | **2** |
| T8 | a finished 40-move game record with final position; was it a draw | state-change regression | **0** |
| T9 | relay of twelve runners, each 3 seconds slower than the last; last finishes within 40 minutes | chain-not-coupling regression | **2** |
| T10 | reservoir fed by two streams whose flow falls as the level drops, 12 per cent evaporation; level below the intake before the rains | coupled plus threshold accuracy | **4** |

T6 is the item that matters. Under the *old* L5 it would have scored 3, because the question is
coarse. If it scores 3 now, the re-key has not reached the judges and the top band is still a
precision scale wearing new words.

T1 against T7 is the only measurement the available-model clause has ever had.

## Pre-registered decision rules

SUBMIT v10 to `src/` for Pablo's reading iff all of:

1. **The epistemic key works**: T2 = 5 and T6 = 5.
2. **Precision no longer buys the top**: T1 ≤ 4.
3. **Forecasting does not over-fire**: T3 ≤ 2.
4. **Knowledge carve holds**: T4 ≤ 2.
5. **Coupling alone does not reach the top**: T5 = 3.
6. **Available-model clause bites**: T1 − T7 ≥ 2.
7. **Regressions**: T8 = 0, T9 ≤ 2, T10 within 1 of 4.
8. **Overall**: ≥ 8/10 exact, and no 2-level miss on T2, T6 or T3.

Failure of rule 1 stops submission whatever else passes, and sends the L5 statement back to
text. Failure of rule 6 alone does not stop submission, but the available-model clause is then
reported as unmeasured rather than validated.
