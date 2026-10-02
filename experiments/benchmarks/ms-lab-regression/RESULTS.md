# ms-lab-regression — results

**Question.** Do today's judge and prompt reproduce the lab's results for the two social rubrics, MSm (Mind modelling
and social cognition) and MSc (Communication and social interaction)?

**Answer.** Yes, where the lab's items survive verbatim; the regression still fails on two confirmed checks, neither a
judging problem. Every example of both rubrics lands within 1 of its level, Pablo's seven MSc labels are matched as in
August (6 exact, 7 within 1), and 30 of 35 stored lab medians reproduce exactly. The failures: PLs's two
expectation-driven Level 5 examples (arms race, bank run) score 4 on MSm, a genuine overlap the PLs examples carry;
and one rebuilt r36 item scores 3 on MSc where the lost original scored 5.

**Status.** Complete (2026-10-02). 540 pass-1 calls and 9 pass-2 calls, all written by Opus 5.5 at effort low, no
classifier stops. 14 of 16 checks held in pass 1; both failures were confirmed in pass 2. Verdict by the
pre-registered rule: **fail**. Sealed predictions: 13 of 16 check probabilities on the right side; the pass-1 failure
(0.95) happened; overall pass (0.3) did not; the F-on-MSm leaks were PLs Level 5 examples (0.7), as predicted.

## Design

See `PREREGISTRATION.md`, pushed before any label (`8bacd8e`). 180 items, each judged three times with the v2 prompt
(`ms-labreg1`); the items behind a failure judged three more times (`ms-labreg2`). No rubric text changed.

## Results

From `results/regression.json` (`analysis/analyse.py`).

| check | kind | pass 1 | pass 2 |
|---|---|---|---|
| P-MSm placement (19) | new | holds: 15 exact, 19 within 1 | |
| P-MSc placement (20) | lab | holds: 19 exact, 20 within 1 | |
| F-on-MSc no leak (33) | lab | holds: no PL example above 2 | |
| F-on-MSm no leak (33) | new | **fails**: PLs L5 arms race 4, bank run 4 | **confirmed** (4, 4) |
| L r30 MSc minimal pairs | lab | holds | |
| L r36 MSc pair | lab | **fails**: D2 at 3 (target 5 ± 1); D1 at 3 | **confirmed** (3) |
| L r60 stated-stance carve | lab | holds (B1 1, B2 4) | |
| L r60 anti-count guard | lab | holds (B3 0) | |
| L r60/r69 Level 4/5 boundary | lab | holds (B4 4, M5 5) | |
| L r75 MSc ladder | lab | holds: all nine at their medians | |
| L r70 human labels | lab | holds: 6 exact, 7 within 1 | |
| B MSc high, mid-band, anchors | lab | hold | |
| B MSm low (20) | new | holds | |
| B MSm on pure MSc items | new | holds | |

**Stored lab medians against today's** (exploratory): 30 of 35 exact. The five differences are the four rebuilt items
(r36 D1 4→3, D2 5→3; r60 B1 0→1, B2 5→4, whose stored 5 the lab had recorded as contaminated) and battery D07 (2→1).
Every verbatim r30, r69 and r75 item reproduces exactly. All three repeats agree on 95% of items.

**Sibling cross-loading (S, descriptive).** MSc's examples at Levels 3–5 score 2–5 on MSm (mostly 3; Level 5's
examples 4–5). MSm's examples score 0–1 on MSc, except its two negotiation-like Level 5 examples (3 and 5). The overlap
runs one way: steering someone requires modelling them, but modelling someone does not require steering them.

## Reading

- **The judge and prompt are not the problem.** Where the lab's items exist verbatim, today's judge reproduces them
  exactly, including the full MSc ladder and Pablo's labels.
- **PLs's Level 5 examples load MSm.** An arms race and a bank run are forecasts in which each side's expectation of
  the other drives the outcome; MSm reads that as beliefs about beliefs. This is a desideratum-6 question for PLs's
  examples (they should load PLs alone), or a construct ruling that reflexive expectations count for both, as the
  PLp/PLs chess co-load was accepted. Pablo decides.
- **The r36 failure is most likely the rebuild.** r36 saved only "dozens of custody splits, most unworkable". The
  rebuilt text has parents who each reject any split favouring the other, which MSc's own Level 5 note places below 5
  when the required positions can be reconciled. It cannot separate rebuild from judge; every verbatim item argues for
  the rebuild.
- **On real tasks MSm and MSc will correlate** where there is steering, because MSc tasks carry MSm demand.

## Deviations and caveats

- No deviations from the pre-registration.
- Seven items are rebuilt from descriptions; r61's originals behind Pablo's labels are lost (his labels were read
  against r75's reconstructions).
- Set P judges the examples with every Examples block stripped, a lower bound for the top band.
