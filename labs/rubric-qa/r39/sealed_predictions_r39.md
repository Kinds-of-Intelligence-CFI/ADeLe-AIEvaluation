# r39 sealed predictions — written BEFORE any judge call (2026-08-22)

Purpose: confirm (or refute) the L2/L3 hypothesis r38 GENERATED, on a text change and on
items whose labels were fixed before judging; and close the anchor's coverage gap at
levels 0 and 4, which no human-labelled item has ever tested.

Text under test: `PLe_r39_candidate.txt` = adopted r38 text + the forced-vs-elected
criterion in L2 ("the checking is forced by the structure of the work: it happens whether
or not the agent goes looking for it") and its complement in L3 ("the checking is elected
rather than forced… nor that the task names one").

## Anchor labels (fixed before any judge call)

Re-anchored on the r38 analysis (declared post-hoc for r38, pre-registered for r39):
| swe-0090 | 3 | checking is elected: agent decides to run check/test suite and what it must show |
| swe-0461 | 3 | same |
| ab-0024 | 3 | same: no forced check that a retrieved record answers the question asked |

Carried unchanged (Pablo's labels / r38-endorsed):
| tau-0007 | 2 | measured 2 in r38; note 1 is defensible under forced-checking (per-call returns are forced) — within-1 either way |
| tau-0146 | 2 | measured 1 in r38; same note |
| usaco-0002 | 3 | measured 3 exact in r38 |
| probe-kill | 1 | forced per-action checks |
| probe-filing | 2 | THE STAKES TRAP: must stay low |
| probe-cave | 5 | THE OPEN-LOOP TRAP: must stay 5 |

New designed items (label is by construction, as with probe-cave):
| probe-L0a | 0 | single atomic action (title an abstract) |
| probe-L0b | 0 | single judgement, nothing to track |
| probe-L2forced | 2 | THE MINIMAL PAIR, forced arm: six stages, unit self-tests and refuses to advance |
| probe-L3elected | 3 | THE MINIMAL PAIR, elected arm: identical task, same checks available via handheld meter, but only if the technician chooses to measure |
| probe-L4a | 4 | no reference output; un-converted constant is invisible until far downstream; verification must be constructed |
| probe-L4b | 4 | plausible-in-place misreads, symptoms only in aggregate; consistency checks must be constructed |

## Predicted ensemble medians (median-of-3 seeds per judge, median across judges)

swe-0090 3 · swe-0461 3 · ab-0024 3 · tau-0007 2 · tau-0146 1 · usaco-0002 3 ·
probe-kill 1 · probe-filing 2 · probe-cave 5 · probe-L0a 0 · probe-L0b 0 ·
probe-L2forced 2 · probe-L3elected 3 · probe-L4a 4 · probe-L4b 4

## Pre-registered decision rule (fixed before any judge call)

CLOSE PLe iff all of:
1. **The minimal pair separates**: probe-L2forced ≤ 2 AND probe-L3elected ≥ 3, with the
   pair's medians differing by ≥1. (This is the whole point of the round; failure here
   means the forced/elected criterion does not bind and the L2/L3 boundary stays open.)
2. **Level 4 is reachable**: probe-L4a and probe-L4b both ≥ 4, and neither reaches 5.
3. **Level 0 is reachable**: probe-L0a and probe-L0b both = 0.
4. **Traps hold**: probe-filing ≤ 3, probe-cave = 5, probe-kill ≤ 2.
5. **Within-1 of anchor on ≥ 14 of 15 items**, no 2-level gap anywhere.
6. Cells with seed spread ≥2 declared unstable; median-of-3 stands.
α ≥ 0.80 on judge medians is REPORTED, not gating: if medians are clean and α stalls near
0.75, the residue is judge calibration and is to be accepted explicitly, not edited away.

If 1 fails → the L2 clause is reverted and the boundary is documented as open.
If 2 or 3 fails → the level in question is defective and PLe does not close.
