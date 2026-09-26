# PLs (Simulating) — pre-registration battery

> Dimension renamed from PLw "World Modelling" → **PLs "Simulating"** (2026-08-20). The code
> PLs was previously borne by the deleted "Situational and Environmental Understanding"
> dimension; historical PLs-coded labels are NOT comparable to this battery.

Per the agreed protocol: **Pablo labels every item below FIRST** (his labels double as the
human anchor), Claude's expected labels stay sealed until his are in, then haiku/sonnet/opus
judge one item per call, never batched, never Fable. Decision rule fixed in advance:
cleared = within-1 on natural items AND every conflict cell resolves as Pablo pre-registered.
A measured inversion in a specific cell is the only thing that justifies restructuring the
driver (e.g. splitting precision out as a second variable).

Driver under test (fused): *how much interacting change must be tracked, at the precision
the answer requires*. Precision is the yardstick, not a second axis.

## A. Conflict cells — interaction × precision (the fusion's falsifiers)

| # | Item | Cell | Pablo |
|---|------|------|-------|
| A1 | Will the ice in a drink left in full summer sun be melted by the end of the afternoon? | chaotic dynamics + coarse answer | |
| A2 | From described conditions, will it rain somewhere in this region at some point next week? | chaotic + very coarse | |
| A3 | From the same described conditions, which of two neighbouring valleys does the storm strike three days out? | chaotic + fine | |
| A4 | Compute exactly where a thrown ball lands, no air resistance, given speed and angle. | no interaction + exact answer | |
| A5 | Exact date a savings account first exceeds a threshold under monthly compound interest. | single process + exact | |
| A6 | From a described billiards break, which pocket does the ball nearest the cushion reach? | compounding interaction + fine | |
| A7 | From the same break, does *any* ball reach *any* pocket? | compounding interaction + coarse | |
| A8 | A described predator–prey pair oscillates; state whether the prey population at the next trough falls below the stated extinction threshold. | few couplings + fine answer (the off-diagonal cell) | |

If the fusion is right: A1, A2, A7 low (≤2); A4, A5 low (≤2, load lives elsewhere);
A3, A6 top band; A8 reaches L4 under the fineness-not-count gate. If Pablo pre-registers
otherwise on any cell, that cell is the measured defect — do not patch text before the
disagreement is understood.

## B. Boundary probes — the carves (one-directional routing checks)

| # | Item | Probes | Pablo |
|---|------|--------|-------|
| B1 | Find a plan to get a frightened cat down from a tree. | control side of prediction-vs-control (planning) — PLs should stay low | |
| B2 | A ladder is placed against the tree as described; predict what the cat does. | prediction side of the same situation | |
| B3 | Sally leaves her marble in the basket; Anne moves it. Where will Sally look? | inferring a belief (minds) vs propagating a stated tendency — PLs low | |
| B4 | Both generals' doctrines and forces are described in full; predict how the described battle unfolds over the day. | agents as processes-to-propagate (should score, no mind inference needed) | |
| B5 | What happens when a lump of sodium is dropped into water? | specialised knowledge, one-step process — PLs ≤1 despite the chemistry | |
| B6 | Predict the final temperature when two described water masses are mixed, exactly. | calculation, no interaction beyond one equilibration — low | |
| B7 | Reconcile a year of a small business's ledger across twelve monthly statements, following the given procedure. | pure execution/monitoring task — PLs should stay ~0 (nothing about the world is forecast) | |
| B8 | Trace the described sorting algorithm on the given list by hand and state the list's final order. | formal single-course state evolution — does the calculation exclusion floor it, or does deterministic tracing score? Genuinely open boundary; pre-register with care | |

## C. Annotatability probes (level depends on off-text facts)

| # | Item | Trap | Pablo |
|---|------|------|-------|
| C1 | "Predict the outcome of the experiment described in the attached protocol" with the protocol absent. | judge must refuse/floor, not guess | |
| C2 | A prediction question whose system is named ("the standard model of the housing market") but whose dynamics are not described. | does knowledge-of-dynamics leak into the score? | |
| C3 | "Predict whether the described three-species pond system collapses within a decade," with couplings described only loosely. | can the judge assess answer-sensitivity without solving the task? (circularity probe from the adversarial review) | |

## D. Natural instances

~8 instances drawn from the frontier-benchmark pool (GAIA / tau-bench / forecasting-style
items), selected in a later session so selection can't be steered by the designed cells.
Report level-usage distribution with every agreement number, per protocol.
