# judge-sonnet55 — pre-registration

Committed and pushed before any label of this study, with the run, the judge agent and the analysis
script. Pablo asked for this test on 2026-09-29, the day after Sonnet 5.5 came out.

**Question.** Does Sonnet 5.5 at high effort label like Opus 5.5 at medium effort, at a lower cost?

**Why.** All our judging runs as Claude Code subagents on Pablo's plan, so cost means plan usage.
Sonnet 5.5 costs half as much per token as Opus 5.5 ($2 and $10 per million input and output
tokens, against $4 and $20). But high effort may think much longer.

## Design

- **Cells.** PLp and PLe on the 44 SWE-bench Verified tasks of `swebench-pl`'s gate: 88 cells. PLs is
  left out: it sits at 1 on almost every SWE-bench task, so its agreement says little.
- **Prompts.** Copied byte for byte from the gate run `swepl-gate`; `make_run.py` checks every hash.
  Only the judge differs.
- **Judge.** `adele-judge-high` (effort high; tools Read and Write; no CLAUDE.md), model alias
  `sonnet`. A probe on 2026-09-29 showed the alias now gives `claude-sonnet-5-5`. Relays
  `judge-dispatcher-high`, one call per cell. Run `s55h-gate`.
- **Writers.** `writers.py` finds the model behind each answer. Answers not written by
  `claude-sonnet-5-5` are set aside and the cell is judged once more; if that fails too, the cell
  has no label.
- **References, already stored.** Opus medium (`swepl-gate`), Opus low (`swepl-gate-low`), and Opus
  max and Sonnet 5 max (`swebench-30`, run `swev30-r4`), on the same 88 cells.
- **Yardstick.** Opus low is our current judge setting. It matches Opus medium exactly on 85% of
  these 88 cells, within one level on all of them, with mean shifts of +0.05 (PLp) and −0.07 (PLe).
  Sonnet 5 at max matched Opus max on 72%.

## Checks and verdict (`analysis/analyse.py`)

Sonnet 5.5 high against Opus medium, on the 88 cells:
1. exact agreement 0.80 or more;
2. agreement within one level 0.98 or more;
3. mean shift within ±0.15, for PLp and for PLe separately;
4. at least 95% of cells labelled by `claude-sonnet-5-5` and parsed.

**Verdict.**
- "Works well": all four checks hold.
- "Does not": exact agreement below 0.75, or within one level below 0.95, or a mean shift beyond
  ±0.25.
- "Unclear": anything else. A larger sample would be needed before any switch.

**Cost (reported; decides "cheaper").**
- I read the plan's 5-hour and weekly meters just before the run starts and just after the last
  answer, and count my own turns in between.
- References, orchestration included: Opus medium used about 0.049% of a 5-hour window per SWE-bench
  call (`swepl-r1`), and Opus low about 0.041% per call (`tau2-tb4-pl`).
- "Cheaper" means below Opus low's 0.041% per call.
- Also reported: mean time per call.

**Next steps.**
- If the verdict is "works well" and Sonnet is cheaper: a Sonnet 5.5 medium arm (cheaper still),
  then a larger sample with a validity check, before any switch.
- If the verdict is "does not": stop, and skip the medium arm (Pablo, 2026-09-29).

**Budget stop.** The weekly limit is at 96%. Judging stops if it reaches 98%, and resumes after the
reset (2026-09-29 20:00 UTC).

## Predictions (sealed)

- Verdict: "works well" 0.25, "does not" 0.45, "unclear" 0.3.
- Exact agreement with Opus medium 0.80 or more: 0.3.
- Sonnet 5.5 reads higher than Opus medium on average: 0.65.
- Sonnet 5.5 high is cheaper per call than Opus low: 0.45.
- Mean time per call above Opus medium's 16 s: 0.85.
- At least one answer written by another model, or one classifier stop: 0.3.

## Deviations

None yet.
