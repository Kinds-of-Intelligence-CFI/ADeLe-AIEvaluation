# Harness emulation: can the Batch API reproduce the subagent judge? (pre-registration, 2026-11-01)

**Why.** `gate-api-bridge` failed on PLp. Through the API, the same judge on byte-identical prompts reads PLp lower
than as a Claude Code subagent (exact 0.78, shift −0.18). The PLe and PLs labels agree. The subagent sees more
than the prompt:
- a system prompt: the agent file plus three Claude Code notes, taken verbatim from a `noreason-pl` judge
  transcript's `prompt_snapshot`;
- a two-line instruction and a reminder;
- the prompt as a line-numbered Read tool result (`1\t…`);
- Read and Write tools.

In that transcript, the judge also wrote a short visible note ("…Likely 3.") before its Write call. The API judge
answers with the digit directly.

**Arms** (Batch API, Opus 5.5, effort low; prompts from `gate-api-bridge`, byte-identical to `noreason-pl`):
- **E, emulated:** that system prompt, the tools Read, Write and SubagentHandback, and the conversation up to the
  Read result. The judge then continues on its own. Its level is the `content` of its Write call, else a digit in
  its text. All 450 cells (PLp, PLe, PLs).
- **R, plain repeat:** the gate's request again, on the 150 PLp cells. It measures the API's own rerun noise.

**Bar** (the gate's, against the `noreason-pl` subagent labels):
- **E qualifies** if:
  - PLp exact ≥ 0.84 and PLe, PLs ≥ 0.88;
  - every |shift| ≤ 0.15;
  - coverage ≥ 95%.
- **R** is descriptive: API-vs-API exact agreement and shift on PLp.

**Decision.**
- **If E qualifies,** the emulated request becomes the API judge setting. Wave 2 and any wave-1 work on the API use
  it, so its labels pool with the subagent labels.
- **If not,** wave 2 runs on the plain API as its own label layer, and a 10% wave-1 re-judge on the API measures
  each v1 rubric's backend shift.

**Cost:** about $6.

## Result (2026-11-01): E qualifies

600 requests, all answered by `claude-opus-5-5` (`run.py analyse`):

| arm | against | PLp exact / shift | PLe exact / shift | PLs exact / shift |
|---|---|---|---|---|
| E, emulated | subagent (`noreason-pl`) | **0.900 / −0.05** | 0.893 / −0.04 | 0.960 / −0.03 |
| R, plain repeat | first API run (`gate-api-bridge`) | 0.947 / +0.01 | — | — |
| R, plain repeat | subagent | 0.807 / −0.17 | — | — |

**The plain API is stable but offset; emulation removes the offset.** In E, the judge wrote a short note before its
Write in 36% of calls. An E call is about 5,900 tokens in and 155 out, roughly $0.013 at batch prices.

**Decision, by the rule above:** the emulated request is the API judge setting, as `judge.harness = "subagent-v2-low"`
(`src/adele/mass/backends/harness.py`, verified identical to this test's requests). The wave-2 specs use it.

## v1 bridge (2026-11-02): the harness also matches the subagent on the v1 rubrics

Runs `w1-rejudge-goal` and `w1-rejudge-tau2` cover 10% of the finished wave-1 tasks (85 tasks: SWE 44, code 18,
tau2 23) × 17 v1 rubrics = 1,445 cells. They go through the API with the harness, on prompts byte-identical to the
subagent judgements, and every cell was labelled by `claude-opus-5-5`. Against the subagent labels:
- **Overall:** exact 0.931, within 1 1.000, mean shift +0.03.
- **Per rubric:** exact 0.85–0.99, every |shift| ≤ 0.15. The largest gap is AS (exact 0.85, shift +0.15); next are
  QLq (0.91, −0.05) and AT (0.88, +0.02).

So wave 2's v1 labels (API with the harness) pool with wave 1's (subagents). The run also gives a per-rubric
reliability estimate for wave 1. Cost ≈ $19.
