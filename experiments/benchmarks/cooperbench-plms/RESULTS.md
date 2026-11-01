# cooperbench-plms — results

**Question.** On CooperBench, where the same pair of coding features is built by one agent (solo) or by two agents
who must coordinate (coop), do the social rubrics of the coop task predict how much success drops from solo to coop?

**Answer.** No. The rubrics see that cooperating adds social demand: MSc and MSm are higher on the coop prompt for
every pair. But they give every coop prompt about the same level (MSc 2 on all 120, MSm 3 on 106), so they cannot
say which pairs lose most from cooperating. MSm against the drop is +0.03; MSc is constant and cannot be tested. PLp
on the solo prompt does fall with solo success (−0.18, p = 0.044), as on other coding benchmarks.

**Status.** Complete (2026-10-03). 1,200 cells (120 pairs × solo, coop × 5 rubrics), all labelled by Opus 5.5 at
effort low, check OK, no rejections. Three of six sealed predictions held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`df91fb5`). 120 pairs sampled from 452 with solo and coop results
for GPT-5, Claude Sonnet 4.5 and GPT-5.5. `drop` = solo rate − coop rate over those three models (mean solo 0.49,
coop 0.33). Primary: MSc and MSm of the coop prompt against `drop`, predicted positive.

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`).

**Levels (120 pairs).**

| rubric | solo | coop |
|---|---|---|
| PLp | 1/2/3 = 2/112/6 | 2/3 = 83/37 |
| PLe | 3 on all | 3/4 = 70/50 |
| PLs | 1/2 = 91/29 | 1/2/3 = 24/95/1 |
| MSm | 0 on all | 2/3/4 = 13/106/1 |
| MSc | 0/1 = 100/20 | 2 on all |

Coop above solo: MSm and MSc 100% of pairs, PLs 60%, PLe 42%, PLp 28%.

| test | ρ | p |
|---|---|---|
| MSc (coop) against drop (primary) | constant: not testable | |
| MSm (coop) against drop (primary) | +0.03 | 0.79 |
| MSc / MSm coop − solo against drop | +0.11 / +0.03 | 0.22 / 0.79 |
| PLp / PLe / PLs coop − solo against drop | −0.05 / −0.14 / −0.14 | ns |
| PLp (solo) against solo rate | −0.18 | 0.044 |
| PLp (coop) against coop rate | −0.18 | 0.054 |
| MSm (coop) against coop rate | −0.08 | 0.39 |
| Sensitivity, MSm (coop) against drop: unflagged (88) / site coop results | −0.05 / +0.08 | ns |

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| MSc 0 on at least 90% of solo prompts | 0.85 | failed (83%: 20 solo prompts at 1) |
| MSc higher on coop than solo for at least 90% of pairs | 0.8 | held (100%) |
| median MSc on coop prompts at least 2 | 0.7 | held (2) |
| MSc (coop) against drop positive, p < 0.05 | 0.25 | did not happen (constant) |
| MSm (coop) against drop positive, p < 0.05 | 0.2 | did not happen (+0.03) |
| PLp (solo) against solo rate negative, p < 0.05 | 0.45 | held (−0.18, p 0.044) |

## Reading

- **The contrast is right; the spread is missing.** Adding a hidden partner moves MSc from 0 to 2 and MSm from 0 to 3
  on every pair. Within the coop condition, though, the prompts all describe the same protocol (two agents, own
  feature each, a message channel), and the rubrics read the protocol, not how much the two features collide.
- **What drives the drop is not in the prompt.** Gold-patch conflicts and shared files decide how hard merging is, and
  the agents do not see the partner's feature. A demand rubric that reads only the prompt cannot see it.
- **PLp behaves as on SWE-bench**: higher planning demand, lower solo success, at a modest −0.18.
- One run per (pair, model): the drop is coarse (thirds) and noisy.

## Deviations and caveats

- No deviations.
- The prompt includes one setup paragraph that the agents do not see as such (setup and success rule).
- Models are late-2025 (GPT-5, Sonnet 4.5) plus GPT-5.5 on a different harness.
