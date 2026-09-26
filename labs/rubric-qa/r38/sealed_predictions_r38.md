# r38 sealed predictions — written BEFORE any judge call (2026-08-22)

Anchor: endorsed label set (Pablo's 5 + Claude's 6 endorsed by Pablo 2026-08-22 + probe-cave 5).
ARM A = current committed 2026-08-16 PLe text (baseline reused from r37 raw seeds for the 10
overlapping natural items + probes; ARM A run fresh ONLY for probe-cave).
ARM B = r38 candidate (checking-availability driver, full rewrite, incl. Mars example swap
and the two review fixes).

Predicted ENSEMBLE MEDIAN (across haiku/sonnet/opus × 3 seeds) per item:

| item | label | A (r37 measured / predicted) | B predicted | note |
|---|---|---|---|---|
| tau-0007 | 2 | 1 (measured) | 2 | B's L2 "end of a short task" juncture should lift sonnet's 1s |
| tau-0106 | 2 | 1 (measured) | 2 | |
| tau-0146 | 2 | 1 (measured) | 2 | |
| tau-0089 | 2 | 1 (measured) | 1 | shortest tau; sonnet/opus may hold at 1 — within-1 either way |
| tau-0094 | 2 | 2 (measured) | 2 | |
| probe-kill | 1 | 1 (measured) | 1 | now tests the L1 band, not the L5 guard |
| probe-filing | 2 | 5 (measured) | 2 | THE TRAP: stakes-exclusion sentence must route it down; failure mode = judges still read unamendability as high |
| probe-cave | 5 | 4 (predicted; fresh run) | 5 | under A, "cannot be redone" may reach 5 but tie-break drags to 4; under B, "needed yet impossible" should bind |
| swe-0090 | 2 | 2 (measured) | 2 | |
| swe-0461 | 2 | 2 (measured) | 2 | |
| usaco-0002 | 3 | 3 (measured) | 3 | tests review-fix #1 (L3 scheduling clause); failure mode = judges read runnable samples as L2 |
| ab-0024 | 2 | 2 (measured) | 2 | |

Judge-offset expectation carried from r37: haiku ≈ +1, sonnet ≈ −1 around opus on natural
items; ensemble median absorbs it. Likeliest unstable cells: tau-0089/0094 (r37 spread),
probe-filing on haiku.

## Pre-registered decision rule (fixed before any judge call)

ADOPT the r38 text iff, on ARM B ensemble medians (median-of-3 seeds per judge, median
across judges):
1. within-1 of the endorsed label on >= 11 of 12 items;
2. probe-filing <= 3 (trap holds: unamendable-but-checklist-easy must NOT read high);
3. probe-cave = 5 (the new L5 is reachable);
4. no item that was within-1 of its label under ARM A moves to >= 2 off under ARM B;
5. any judge x item cell with seed spread >= 2 levels is declared unstable and excluded
   from claims (but not from the adoption test).
READY assessment (separate from adoption): interval-approx alpha on judge medians >= 0.80
and no 2-level gap between ensemble median and endorsed label anywhere.

Deviation declared in advance: ARM A numbers for the 10 overlapping items are r37's raw
seeds (same text, judges, and prompt format, run 2026-08-20/21), not re-run. probe-cave has
no ARM A history and is run fresh in both arms.
