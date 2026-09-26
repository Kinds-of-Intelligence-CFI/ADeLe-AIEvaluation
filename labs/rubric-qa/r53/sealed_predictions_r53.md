# r53 sealed predictions — PLs v9, the first round with a human anchor (2026-08-22)

Text under test: PLs v9 (model-crafting driver; scope reversed so simulating done in order to
act is scored; the state-change test; the executability clause). Not in `src/` — Pablo reviews
the text after this round, and it is submitted only if he approves.

Judges h/s/o, 3 seeds, one item per call, never Fable.

## Why this round is different from every previous one

**Six of the items carry Pablo's own labels**, given in conversation today: the first human
labels this dimension has ever had. Every earlier PLs round measured the text against my own
design intent, which is exactly the weakness the PLe rounds exposed five times. The headline
number here is agreement with those six, and it is the first number in this project that can
fail for the right reason.

| item | Pablo's label | what it tests |
|---|---|---|
| ab-0024 snow frequency | **0** | the state-change test: a static record, counted |
| usaco-0002 max triplet value | **0** | the state-change test on a hard combinatorial item |
| tau-0146 order redirect and swap | **2** | reversed scope: an action task that still scores |
| tau-0007 upgrade then cancel | **2** | same, with two changes traced |
| swe-0090 false validation error | **2** | one pass through machinery, no feedback |
| swe-0461 block-matrix multiply | **3** | one pass changes what the next sees |

## Other predictions

Falsifiers, unchanged in substance under the model framing: A7 = 3 (coupling alone must not
reach the top band), A4 = 2 and A5 = 2 (an exact answer under a supplied rule stays low),
A8 = 4 (accuracy places it, not the number of parts). Accuracy contrast: A1/A2 = 2 against
A3 = 5, and A7 = 3 against A6 = 5. Coupling boundary: X1 and X5 = 3, X2 and X6 = 2. Carves:
B1 = 1, B3 = 1, B5 = 1, B7 = 0.

**New pair for the executability clause**, which entered the text today on Pablo's tool-usage
observation:
| E1-paper | 3 | same bug, source only, nothing can be run |
| E2-shell | 1 | same bug, shell and test suite available, so the world carries the change |

## Pre-registered decision rule

SUBMIT v9 for Pablo's reading iff all of:
1. **Human agreement**: ≥ 5 of 6 anchored items exact, all 6 within-1. This is the gate that
   matters. Failing it means the re-framing did not capture what he was labelling.
2. Falsifiers do not fire: A7 ≤ 3, A4 ≤ 2, A5 ≤ 2, A8 ≥ 4.
3. Accuracy contrast separates by ≥ 2 on both pairs.
4. Coupling boundary separates with no overlap.
5. Carves hold: B1 ≤ 2, B3 ≤ 1, B5 ≤ 1, B7 = 0.
6. Executability pair separates: E1 − E2 ≥ 1.
7. ≥ 19/22 within-1 overall, no 2-level gap on any anchored item.

A failure of rule 1 stops everything else, whatever the other rules say.
