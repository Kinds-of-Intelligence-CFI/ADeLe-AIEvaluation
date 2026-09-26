# r41 sealed predictions — PLs confirming round (2026-08-22)

Confirms (or refutes) the two things r40 GENERATED. Nothing from r40 is re-scored here.
Text under test: `PLs_r41_candidate.txt` = committed PLs + one L0 clause on absent referents.
Judges h/s/o, 3 seeds, one item per call, never Fable.

## What r40 generated, and what each item here tests

**(1) The absent-referent defect (r40's only 2-level miss).** C1 — "predict the outcome of
the experiment described in the attached protocol", protocol absent — scored 2, not 0:
judges invented a generic experiment and scored that. The r41 clause says a task referring
to a situation it does not present belongs at L0. Tested in BOTH directions, because a
clause that floors everything would be worse than the defect:
| P1-absent | 0 | referent named, never presented |
| P1-present | 2 | same question, situation actually given: single undeflected process |

**(2) The A7 re-anchor.** r40 put A7 (billiards break, coarse "does any ball pocket?") at 3
against a design intent of 2. The judges' reason: in a break the coupling is *constitutive*
— balls move only by being struck — so even a coarse answer needs the coupling propagated.
That is the rubric working; the design intent was wrong. This round tests the distinction
the reasoning implies, on fresh items with coarse answers on both sides:
| P2-constitutive | 3 | dominoes: each event exists only because the previous one caused it |
| P2-independent | 2 | three unconnected kettles: parallel processes, no interplay |
If the pair does not separate, the constitutive/decorative distinction is not in the text
and A7's placement is unexplained.

**(3) B8's open boundary** (recorded, not scored, in r40; measured 2):
| P3-single | 2 | deterministic tracing of ONE process — calculation exclusion should floor it |
| P3-interacting | 3 | deterministic tracing where two processes feed each other |

**Carried traps/controls:** A6 = 5, A8 = 4, B7 = 0, A7 = 3 (re-anchored, carried to check
the new clause did not disturb it).

## Pre-registered decision rule

PLs CLEARS its levels iff:
1. P1-absent = 0 AND P1-present ≥ 1 (the clause binds and does not over-floor).
2. P2-constitutive − P2-independent ≥ 1, with P2-independent ≤ 2.
3. P3-interacting − P3-single ≥ 1.
4. Traps hold: A6 = 5, A8 = 4, B7 ≤ 1, A7 = 3.
5. ≥ 9/10 within-1 of the labels above, no 2-level gap.
Failure of 1 → revert the clause, log absent-referent handling as a pipeline (prompt-side)
matter rather than a rubric one. Failure of 2 → A7 stays an unexplained placement and PLs
does not clear. Failure of 3 → B8's boundary stays open and is documented as such.

## Standing limitation, carried from r40 and NOT resolved here
Pablo has still never labelled a PLs item. Every anchor in r40 and r41 is construction-side
(design intent) or Claude's. Across PLe's rounds the anchor was the thing that proved wrong
four times and the rubric text zero times, so this is the live risk on PLs and no result
below should be read as human-validated. Recommended before PLs is called finished: Pablo
labels the ten items here blind and the two label sets are compared.
