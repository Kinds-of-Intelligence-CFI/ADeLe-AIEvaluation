# judge-choice: Jose's prompt, and which model can judge with it (pre-registration, 2026-11-02)

**Questions.**
1. **Prompt:** how does Jose's prompt change Opus 5.5's labels?
   - It is the published v1.0 wording and layout, without chain-of-thought and without the tie rule, answering with a
     bare digit (builder `v1-layout-noreason`).
   - Jose: modern models reason on their own, so asking for chain-of-thought is redundant, and "think = low" already
     sets it; drop it and the minimum rule, keep the rest as close to the original as possible.
2. **Model:** with that prompt, can Sonnet 5.5 or Haiku 5.5 replace Opus 5.5 as the judge?

The Sonnet verdict of 2026-10-07 (`noreason`) predates the adopted MSc and MSm texts, the goal-visible inputs and the
harness. Haiku 5.5 was never tested as a judge.

**Arms.** All use Jose's prompt and the subagent context (`judge.harness = "subagent-v2-low"`), through the Batch API,
one label per cell:
- `opus-low` (the reference);
- `sonnet-low`;
- `haiku-low`;
- `haiku-medium`.

**Sample** (`make_sample.py`, seed 20261103, ids in `sample.csv`): 1,184 cells per arm.

| block | rubrics | tasks | cells |
|---|---|---|---|
| PL | PLp, PLe | 12 per agentic set × 13 sets; Pablo's 6 TB tasks forced in | 312 |
| v1 + memory | AS AT CEc CEe CL MCr MCt MCu QLl QLq SNs VO (no knowledge rubrics) + MMe MMp MMs | 2 per set × 17 sets, 3 for the six largest = 40 | 600 |
| MSc on tau2 | MSc | 42 tau2 tasks: Pablo's 15 set-H tasks + random | 42 |
| MS lab | MSc v4b, MSm candidate | the lab items, one repeat, including set H on the full input | 230 |

**Inputs** are as production: goal-visible for coding and terminal, tau2-goal for tau2, `data/instances` for the
social and static sets. The lab prompts are tie-rule-freeze's rebuilt, hash-verified ones. Each is split into its
parts, checked by rebuilding the verified prompt, and rebuilt in Jose's prompt.

**Cost:** about $32 (Opus ~$20, Sonnet ~$10, Haiku ~$1).

## Rules for a candidate model (set before any label)

Each candidate arm is judged against `opus-low`, per family: **PL**, **MS** (lab + tau2), **v1** (12 rubrics) and
**memory** (3).

| rule | test | PL | MS | v1 | memory |
|---|---|---|---|---|---|
| A1 | pooled exact agreement with Opus | ≥ 0.85 | ≥ 0.85 | ≥ 0.80 | ≥ 0.80 |
| A2 | within one level | ≥ 0.97 | ≥ 0.97 | ≥ 0.97 | ≥ 0.97 |
| A3 | \|mean shift\| | ≤ 0.15 | ≤ 0.15 | ≤ 0.15 | ≤ 0.15 |
| A4 | exact ≥ 0.70 in every task group (coding, tau2, social, static) | ✓ | ✓ | ✓ | ✓ |
| K | labels ≥ 98% of cells (refusals count as missing) | ✓ | ✓ | ✓ | ✓ |
| C | solve-rate link, pooled within benchmark, minus Opus's | PLp ≥ −0.10 | tau2 MSc ≥ −0.15 | — | — |
| H | Pablo's labels | TB PLp within one on ≥ 5 of 6 | set H exact ≥ 12 of 15, full input and real tau2 input | — | — |

- **A family qualifies** if every rule in its column holds. Memory is agreement only: it has no frozen text, human
  labels or outcome links yet.
- **The C rule** uses point estimates. Bootstrap CIs (resampling tasks within benchmark) are reported. At 12 tasks per
  set they are wide, so C catches large drops only.
- **Lab rules are indicative** with one repeat (they were defined on three). Reported: the refusal pairs (B ≤ 3 on
  ≥ 4 of 5) and the R checks.
- **Verdict:** per arm and family. A model may replace Opus only in the families it qualifies in. If the cheapest arm
  qualifies everywhere but sits within 0.03 of an A bar, a confirmation run on a fresh sample comes before any bulk
  use.

## The prompt (Opus arm), descriptive

Against the production Opus labels on the same cells (label set `current` and the wave-1 and wave-2 runs), reported:
- exact agreement and mean shift per family;
- the paired change in the PLp and tau2 MSc links;
- set H, Pablo's TB labels, and the lab refusal pairs.

A formal freeze check of Jose's prompt (full PL bar, the lab with three repeats) is a follow-up, if the team adopts
the prompt. tie-rule-freeze already shows that dropping the tie rule keeps every freeze.
