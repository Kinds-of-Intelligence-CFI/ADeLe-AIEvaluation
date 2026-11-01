# Gate: API judge = subagent judge (pre-registration, 2026-11-01)

**Question.** Does the same judge give the same labels through the Anthropic Batch API as through Claude Code
subagents? The judge is Opus 5.5 at effort low, with the bare-digit prompt. The bulk runs on the API (wave 2,
and maybe part of wave 1) rely on this.

**Design.** Spec `specs/gate-api-bridge.toml`: 150 reference tasks × PLp, PLe, PLs = 450 cells. All 450 prompts are
byte-identical to run `noreason-pl` (subagent, 2026-10-06/07), checked before pinning. The API run uses one repeat
and the runner's retries. A 10-cell dry run comes first.

**Bar, set before any API label exists.** The noise yardstick is a same-day rerun of the released judge (`noreason`
R′ vs released: PLp 0.89, PLe 0.93, PLs 0.93 exact). Per rubric, comparing API labels with `noreason-pl` labels
on the cells both labelled:
- **pass** if:
  - exact agreement ≥ yardstick − 5 points (PLp ≥ 0.84, PLe ≥ 0.88, PLs ≥ 0.88);
  - |mean shift| ≤ 0.15;
  - API coverage ≥ 95% of the 450 cells.
- **fail** if any rubric's exact agreement is below the yardstick − 10 points, or coverage is below 90%.
- **mixed** otherwise.

**Decision rule.**
- **Pass:** API labels may join subagent labels in one label set, with the backend recorded per label. Wave 2 goes
  to the API.
- **Mixed or fail:** stop API judging and ask Pablo before anything else is sent.

**Also recorded:** input and output tokens per call from the batch results. They give the real cost per call, which
re-estimates every planned API run before it is sent (`API-CREDIT-PLAN.md`).

## Result (2026-11-01): FAIL on PLp

All 450 cells were labelled, every one by `claude-opus-5-5`. Run `analyse_gates.py api`:

| rubric | exact | bar | within 1 | shift (API − subagent) | verdict |
|---|---|---|---|---|---|
| PLp | 0.780 | 0.84 | 1.000 | −0.18 | fail (below yardstick − 10) |
| PLe | 0.893 | 0.88 | 0.987 | +0.01 | pass |
| PLs | 0.927 | 0.88 | 1.000 | −0.03 | pass |

**The PLp difference is directional, not noise.** The API is lower in 30 cells and higher in 3, mostly 2→1 and 3→2,
on 8 of 9 benchmarks. The prompts are identical, so the difference is the harness. The subagent sees the agent
file's system prompt and Claude Code's line-numbered Read output; the API sees the bare prompt.

**Measured cost:** 3,570 input tokens per call (3.27 chars per token) and about 14 output tokens (thinking is rare at
effort low). That is about $0.0073 per call at batch prices.

**Per the decision rule:** API judging stopped, pending Pablo.

## Gate 2, v1 bridge (PLAN.md §3; bar set there)

60 battery items × 18 v1 rubrics, all 1,080 labelled. Our judge against the published GPT-4o levels
(`analyse_gates.py v1`):
- **Comparable** (within 1 ≥ 0.85, |shift| ≤ 0.3): CEc, CEe, KNs, MCr, MCt, MSm, QLl, QLq, SNs, VO.
- **Not comparable to the v1 battery:** AS, AT, CL, KNa, KNc, KNf, KNn, MCu. Our judge reads lower on all of them:
  KNc −1.00, KNa −0.95, CL −0.78, MCu −0.75, and −0.3 to −0.4 for the rest.

These are still annotated, and marked as such.
