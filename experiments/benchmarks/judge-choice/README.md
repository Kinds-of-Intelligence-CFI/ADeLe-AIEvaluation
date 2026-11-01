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

## Result (2026-11-02): no candidate qualifies; Opus stays the judge

All four arms ran in full (`analyse.py`, `results.json`). Every label is by the requested model.

**Agreement with Opus** (Jose's prompt, same cells):

| arm | PL exact / shift | MS exact / shift | v1 exact / shift | memory exact / shift |
|---|---|---|---|---|
| sonnet-low | 0.74 / +0.10 | 0.75 / **+0.35** | 0.70 / −0.06 | 0.68 / −0.23 |
| haiku-low | 0.64 / +0.21 | 0.76 / +0.28 | 0.60 / −0.22 | 0.51 / −0.47 |
| haiku-medium | 0.65 / +0.15 | 0.76 / +0.21 | 0.61 / −0.23 | 0.60 / −0.34 |

**Bars:** 0.85 for PL and MS, 0.80 for v1 and memory. No arm reaches any of them. Every family fails A1, and most
fail A4 too (exact below 0.70 in at least one task group).

**MSc is where the cheaper models fail most:**
- **Refusal pairs:** both read refusals as negotiations. B ≤ 3 on 0 of 5 pairs, against Opus's 4 of 5.
- **Set H:** Sonnet 4 of 15 on the full input and 5 of 15 on the real tau2 input; Haiku 3–6. Opus: 12 and 15.
- **Haiku also fails most MSc and MSm lab checks:** 9 MSc checks and 5 MSm checks.

**PLp solve-rate link** (pooled within benchmark, 9 sets × 12 tasks):

| judge | ρ | p |
|---|---|---|
| production Opus, same tasks | −0.30 | |
| Opus, Jose's prompt | −0.25 | 0.03 |
| Sonnet | −0.12 | |
| Haiku low | −0.19 | |
| Haiku medium | −0.12 | |

**Haiku setup artefact.** In 33% (low) and 62% (medium) of lab items, Haiku called Read again instead of answering. The
one-turn harness gives no second Read result, so those items have no label. The main runs retried them and recovered.
This affects coverage only: the agreement figures use cells both models labelled.

**Correction (analysis, not design):** the table's C rule was written "≥ −0.10", but the links are negative, so a
weaker link is a positive difference. `analyse.py` now tests weakening ≤ 0.10 (PLp) and ≤ 0.15 (MSc). No verdict
changes.

**Jose's prompt on Opus** (against production labels on the same cells):
- **Labels:** exact 0.83–0.84 per family, shift +0.12 (MS), +0.13 (PL), +0.16 (v1).
- **Your labels:** set H 12 of 15 on the full input (at the bar) and 15 of 15 on the real tau2 input; TB within one
  6 of 6.
- **Lab:** MSc R and M hold. MSm fails only F-on-MSm, the overlap Pablo accepted on 2026-10-02.
- **PLp link:** −0.25 against −0.30 in production on these 107 tasks.

The prompt reads about 0.13 higher, as expected without the tie rule, and keeps the human and lab checks. Its formal
freeze check (full PL bar, the lab with three repeats) is still to do, if adopted.
