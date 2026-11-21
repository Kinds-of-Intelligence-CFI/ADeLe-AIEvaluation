# MSc Level 4 note — results (2026-10-14)

**Verdict: fail.** The candidate breaks one lab check, confirmed in pass 2. Do not adopt it as written. `MSc.txt` is
unchanged.

**Why it fails.** Battery item M01 asks the solver to bring round a colleague who has refused a shift swap and
given his reason. The task does not say whether he keeps pushing back. Under the note, the judge reads that silence as
"no sustained opposition" and applies the prompt's tie rule ("choose the lower"). M01 lands at 3 in all six candidate
calls, below its registered 4. So the note turns *missing* information about persistence into *low* demand. That is
not what it was meant to do: it was meant to lower tasks that *show* the objection being dropped.

## Rules

| rule | result | |
|---|---|---|
| R: no lab check lost | **fail** | B MSc high: M01 at 3 (pass 1: 3, 3, 3; pass 2: 3, 3, 3). Current text: 4, 4, 3 then 3, 4, 3 |
| M1: B at 4+ on ≥ 7 of 8 pairs | holds | 8 of 8 |
| M2: A below B on ≥ 6 of 8 pairs | holds | 8 of 8 |
| H1: candidate exact ≥ current exact (fresh) | holds | 6 vs 6 of 10 |
| H2: no fresh item made 2+ off where current was within 1 | holds | none |

Every other MSc lab check holds under both texts. That includes the r36 pair, which failed on 2026-10-02 under the
older text. So today's current text passes the full MSc lab regression. Of 95 lab items, only M01 changes between
arms. All three repeats agree on 94% of item × arm cells. All 762 answers were written by `claude-opus-5-5`, with no
classifier stops.

## Minimal pairs

| pair | A current | A candidate | B current | B candidate |
|---|---|---|---|---|
| 1 airline refund | 2 | 1 | 4 | 4 |
| 2 gym pause | 3 | 1 | 4 | 4 |
| 3 shop return | 1 | 1 | 4 | 4 |
| 4 admin rights | 3 | 2 | 4 | 4 |
| 5 curfew | 2 | 1 | 4 | 4 |
| 6 delivery fee | 2 | 1 | 4 | 4 |
| 7 builder deadline | 2 | 1 | 4 | 4 |
| 8 fee waiver | 1 | 1 | 4 | 4 |

The current text already separates A from B on all eight. When the task states that the objection is dropped, the
current text does not put it at 4. The gap seen on real tau2 tasks is not about clear cases.

## Human items (Pablo, blind)

| item | released | current | candidate | Pablo |
|---|---|---|---|---|
| H-01 | 2 | 2 | 2 | 2 |
| H-02 | 4 | 4 | 4 | 2 |
| H-03 | 4 | 4 | 4 | 4 |
| H-04 | 3 | 3 | 3 | 3 |
| H-05 | 2 | 2 | 2 | 2 |
| H-06 | 4 | 4 | 4 | 3 |
| H-07 | 3 | 2 | 2 | 4 |
| H-08 | 3 | 3 | 2 | 3 |
| H-09 | 4 | 4 | 2 | 2 |
| H-10 | 2 | 2 | 2 | 2 |

Fresh: exact 6 of 10 in both arms; within one 7 (current) and 8 (candidate); mean shift against Pablo +0.3 and 0.0.
The note fixes H-09 and breaks H-08. The three largest disagreements (H-02, H-06, H-07) are the same in both arms.
On H-02 and H-06 the judge reads repeated pushback in the customer's script and gives 4.

Development items (reported only): exact 4 of 5 (current) and 3 of 5 (candidate); within one 4 and 5.

## Predictions

| prediction | p | outcome |
|---|---|---|
| R holds | 0.8 | no |
| M1 | 0.8 | yes |
| M2 | 0.75 | yes |
| current: A equals B on ≥ 4 of 8 | 0.6 | no (0 of 8) |
| H1 | 0.65 | yes |
| H2 | 0.85 | yes |
| candidate passes overall | 0.45 | no |
| candidate moves ≥ 2 of the 4 released-4 fresh items down | 0.5 | no (1: H-09) |
| current passes every MSc lab check except r36 | 0.6 | yes, and r36 holds too |

## What this means

- The note does little. It changes 1 of 95 lab items, 2 of 10 fresh tau2 items and 2 of 5 dev items.
- Its one confirmed effect on the lab set is a misfire caused by missing information.
- The open question is how the judge should treat tasks that do not say how the other party will behave. The prompt's
  tie rule ("choose the lower") is the only rule today, and the judge uses it for missing information too.
- The large human-judge gaps on tau2 (H-02, H-06, H-07) are not about this note.

## Amendment 1: the C check (2026-10-14)

**Result: 6 of 8 C items at 4 or more.** By the pre-registered rule, the current text already treats unstated
counterpart behaviour as contested (rule B by default). Keep the text and add the "underspecified" flag. Rule B stays
shelved. Prediction (≥ 6 of 8): 0.6, held.

| pair | A (current, msc-l4-1) | C (current, repeats) | B (current, msc-l4-1) |
|---|---|---|---|
| 1 airline refund | 2 | 4 (3, 4, 4) | 4 |
| 2 gym pause | 3 | 4 (3, 4, 4) | 4 |
| 3 shop return | 1 | 3 (3, 3, 4) | 4 |
| 4 admin rights | 3 | 3 (3, 3, 3) | 4 |
| 5 curfew | 2 | 4 (4, 4, 4) | 4 |
| 6 delivery fee | 2 | 4 (4, 4, 4) | 4 |
| 7 builder deadline | 2 | 4 (4, 4, 4) | 4 |
| 8 fee waiver | 1 | 4 (4, 4, 4) | 4 |

A is below C on 7 of 8 pairs. The ordering A < C ≤ B holds on every pair.

**The margin is thin.** The result sits exactly on the threshold. Three of the eight C items have split repeats. The
two below 4 are policy refusals by a support agent (shop return, admin rights), the tau2 shape. So the default is
weakest where tau2 needs it. All 24 answers were written by `claude-opus-5-5`.
