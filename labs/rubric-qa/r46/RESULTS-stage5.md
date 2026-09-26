# Stage 5 (r46) — the PL dimensions on natural benchmark instances (2026-08-22)

The round the battery's section D always called for and r40 skipped. Prompted by Pablo's
question: why are we not using the benchmark tasks?

All 20 instances of `pilot/tasks.csv` (5 SWE-bench, 5 AssistantBench, 5 USACO, 5 τ-bench),
whole set, no selection. Rubrics as committed today: PLp v2-r43, PLe v2-r44, PLs v2-r45.
**Declared deviation: opus-only × 3 seeds — a screen, not a measurement.** Seal:
`sealed_predictions_stage5.md`. Raw: `results_stage5.csv`.

## Headline: PLs has almost no purchase on this benchmark set

| | L0 | L1 | L2 | L3 | L4 | L5 | levels used |
|---|---|---|---|---|---|---|---|
| PLp | 0 | 2 | 13 | 4 | 1 | 0 | 4 of 6 |
| PLe | 0 | 4 | 2 | 14 | 0 | 0 | 3 of 6 |
| **PLs** | **12** | **8** | 0 | 0 | 0 | 0 | **2 of 6** |

**PLs scores 0 on 12 of 20 and never exceeds 1.** The same rubric spans all six levels on
the designed battery. The prediction in the seal (0 on ≥16/20, ceiling 2) was close but not
exact: eight items reached 1 rather than 0, all of them τ-bench or SWE-bench cases where a
single stipulated change has to be traced one step — "what does cancelling this item do to
the order", "what does the log scale do to reversed limits". Nothing on the set requires
carrying a situation forward.

## Correlation matrix (Pearson, 20 instances)

| | PLp | PLe | PLs |
|---|---|---|---|
| PLp | +1.00 | +0.27 | −0.24 |
| PLe | +0.27 | +1.00 | −0.63 |
| PLs | −0.24 | −0.63 | +1.00 |

No collinearity anywhere — the merge signal the taxonomy artifact describes (high positive
correlation *with genuine variance in both*) does not appear. PLs's −0.63 against PLe is not
evidence of a construct relationship: it is an artefact of the τ-bench items sitting low on
PLe and at 1 on PLs while everything else sits high on PLe and at 0 on PLs. With a variance
of 0.24 and a two-level range, PLs's correlations on this set should not be interpreted.

## What this does and does not show

**It does not impugn PLs.** The dimension spans its full range on constructed items, its
falsifiers held, and it discriminates cleanly from PLp and PLe (r42). What the screen shows
is about the *instances*: SWE-bench, AssistantBench, USACO and τ-bench ask an agent to fix
code, look something up, devise an algorithm or serve a customer. None asks what a situation
will do next. **A dimension cannot be measured by a battery that does not exercise it.**

**It does sharpen a decision.** Per the pre-registered reading: PLs should not be annotated
across the agentic pilot as it stands — the labels would be almost all 0 and 1, adding cost
and no resolution. Either instances that exercise simulation are added to the battery
(forecasting, physical and mechanical prediction, ecological or economic dynamics), or PLs is
scoped as a dimension for a different instance pool than the agentic one.

**It also flags something about PLe.** 14 of 20 instances land at L3 and none above. On this
set PLe is nearly a constant — the elected-checking band absorbs almost every non-τ task.
That is not a text defect (the designed probes span 0–5) but it does mean PLe's discriminating
power over *this* pilot is concentrated in one level, which matters for the paper's claims
and was predicted at the end of r39.

## Honest notes
- Opus-only screen: no α, no judge-offset claim, and no cell here should be quoted as a
  measurement.
- No human has labelled any of these instances on any PL dimension; the whole matrix is
  model-side.
- Desideratum 9 is untouched. This is instance coverage, not criterion validity — that still
  needs solver outcomes joined to demand labels.
