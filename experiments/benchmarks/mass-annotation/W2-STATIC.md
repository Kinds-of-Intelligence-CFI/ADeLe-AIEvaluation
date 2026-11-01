# Wave 2, static sets: pre-registration (2026-11-01)

**What.** Run `bulk-w2-static`: the 17 judged v1 rubrics plus v2 MSm on every task of ARC-AGI-2 (public eval,
120), GPQA Diamond (198), ArXivMath (287) and BrokenArXiv (308). That is 913 tasks × 18 = 16,434 cells. The sets
come from `BENCHMARKS.md`, decision 1: the static sets get no PL rubrics.

**Input.** `data/instances`, the frozen texts in the private store. Checked on 2026-11-01:
- ARC prompts end at the test input, with no test output;
- GPQA prompts give the question and options, with no key.

So the judge never sees an answer (`docs/judge-input.md`).

**Judge.** Opus 5.5, effort low, bare-digit prompt, through the Anthropic Batch API in the subagent judge's context (`judge.harness = "subagent-v2-low"`; `harness-emulation` result), so its labels pool with the subagent labels. Retries: one each for a
fallback writer and an unparsed answer, and up to two for API errors. Sent only if `gate-api-bridge` passes
(`GATE-API-BRIDGE.md`), which failed for the plain request; the harness passed (`harness-emulation`).

**Noise floor.** Run `bulk-w2-static-rejudge` re-judges a 3% stratified sample: 7 tasks per set × 18 rubrics = 504
cells. It reports exact agreement and mean shift per rubric against the first labels. It is descriptive and doesn't
gate anything.

**Cost.** `adele mass plan` estimates ~$96 at batch prices with 200 output tokens per call. It is re-estimated
from the gate's measured tokens before sending. If the estimate tops $120, ARC-AGI-2, GPQA and ArXivMath go first
and BrokenArXiv waits (`API-CREDIT-PLAN.md`).

**Analyses** (after outcome ingestion, which is separate work):
- demand profiles per set;
- per rubric, Spearman ρ with per-item success within each set (descriptive);
- the incremental-prediction analysis of `PLAN.md` §4, with these sets added.

ArXivMath and BrokenArXiv 0826 ran with tools and were told the problems are open. They are analysed apart.

**Minor calls (Pablo can veto).**
1. The rejudge sample is 7 tasks per set, drawn with seed 20261101 from the sorted instance ids.
2. Labels go in a new label-set layer, not into `current`, until Pablo says otherwise.
