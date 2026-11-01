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
