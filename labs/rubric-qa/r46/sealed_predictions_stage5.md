# Stage 5 (r46) sealed predictions — natural instances (2026-08-22)

This is the round the PLs battery called for in its **section D** ("~8 instances drawn from
the frontier-benchmark pool, selected in a later session") and that I skipped in r40. It is
also the collinearity screen from the completion plan. Pablo's challenge — *why are we not
using the benchmark tasks?* — is what prompted it.

**Instances:** all 20 of `pilot/tasks.csv` — 5 SWE-bench, 5 AssistantBench, 5 USACO,
5 τ-bench. No selection: the whole set, so nothing can be steered.
**Rubrics:** PLp v2-r43, PLe v2-r44, PLs v2-r45 (all as committed today).
**Protocol deviation, declared in advance:** opus-only × 3 seeds, the reduction the
completion plan named as defensible. Reported as a **screen**, not a measurement — no α, no
judge-offset claim. 180 calls instead of 540.

## What this round is for, and what it cannot do

It can answer two questions:
1. **Does PLs have any purchase on real agentic tasks?** Level-usage distribution on natural
   instances, compared against the designed battery.
2. **Do the three PL dimensions co-vary on real items?** The correlation matrix is the
   thing rubric QA cannot produce, and the completion plan flagged it as the stage that can
   kill a dimension.

It cannot supply criterion validity (desideratum 9) — that still needs solver outcomes — and
it cannot serve as a human anchor, because no human has labelled these for PL dimensions.

## Predictions

**PLs ≈ 0 almost everywhere.** These four benchmarks ask an agent to fix code, answer a
lookup, write an algorithm, or serve a customer. None asks what a situation will do. I
predict PLs = 0 on at least 16 of 20, with the only candidates above 0 being USACO items
where an algorithm's behaviour must be traced (and B8 in r40 put deterministic tracing at 2,
so 2 is the ceiling I expect).

**PLe spread 1–3**, per r38/r39: τ-bench items low (forced tool returns), SWE/AssistantBench
around 3 (elected checking), USACO 3.

**PLp spread 1–4**: AssistantBench lookups low, τ-bench low-to-mid, SWE-bench mid, USACO
3–4 where the approach must be found.

**Correlations:** PLp↔PLe mildly positive; **PLs↔anything ≈ undefined or near-zero, because
PLs will have almost no variance on this set.** That is the outcome I expect, and it is not
a defect — it means these benchmarks do not exercise the dimension.

## Pre-registered readings

- If PLs is 0 on ≥16/20 **and** the designed battery spans 0–5: the dimension is sound but
  **this battery cannot measure it**. The conclusion is about instance coverage, not about
  PLs — and the honest recommendation is that PLs should not be annotated across the agentic
  pilot until instances that exercise it are added.
- If PLs shows real spread here: the dimension earns its slot on agentic tasks directly, and
  the correlation matrix decides whether it is redundant with PLp.
- If PLs correlates ≥0.8 with PLp **with genuine variance in both**: that is the merge signal
  the taxonomy artifact describes, and it goes to the team rather than being settled here.
