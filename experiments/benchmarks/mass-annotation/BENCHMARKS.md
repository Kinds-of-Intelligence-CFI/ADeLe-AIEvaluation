# Bulk annotation — which benchmarks (decided 2026-10-07)

Pablo asked for the exact list. This builds on `reports/Benchmarks to annotate.md` (2026-10-07) and the decisions of
2026-10-01 in `PLAN.md`. Criteria, in order:
1. used with frontier models;
2. sanitized;
3. per-item success flags;
4. traces;
5. tests that really check the result.

Dimension fit comes last. Multimodal and robotic benchmarks are out.

All runs use the default judge: Opus 5.5, effort low, bare-digit prompt (`v2-noreason`), through the Anthropic Batch
API. Costs below are `adele mass plan` estimates at batch prices.

## Wave 1: decided, ready to run after the gates

Every task that already has the released PL and MS labels, plus rivercross. The bulk adds the v1 rubrics, so every
rubric covers the same tasks. The tasks are listed in `subsets/wave1.csv`, built by `subsets/make_subsets.py`.

| benchmark | tasks | per-item outcomes we hold |
|---|---|---|
| SWE-bench Verified (clean set) | 443 | panel; OpenHands Index adds G0 traces (results work, no labels) |
| tau2 airline / retail / banking | 49 / 114 / 79 | panel |
| Terminal-Bench 4.0.0 (clean set) | 35 | panel |
| Terminal-Bench Science 0.1 | 70 | yes |
| DeepSWE v1.1 | 90 | yes |
| FrontierSWE v2 | 19 | yes |
| ProgramBench | 129 | yes |
| EQ-Bench 4 | 120 | yes |
| CooperBench (sample) | 240 | yes |
| Kaggle Game Arena | 24 | yes |
| rivercross-search (lab set) | 54 | lab |
| **total** | **1,466** | |

| run spec | rubrics | calls | cost |
|---|---|---|---|
| `bulk-w1-v1` | the 17 judged v1 rubrics (v2 MSm replaces v1 MSm; UG is computed) | 24,922 | ~$195 |
| `bulk-w1-rivercross-plms` | PLp, PLe, PLs, MSm, MSc on rivercross | 270 | ~$2 |
| `bulk-w1-memory` | MMe, MMp, MMs. **Waits for the team and gate 3** | 4,398 | ~$32 |

Left out of wave 1:
- **tau2-telecom.** 2,280 of its 2,285 instances share one text.
- **WeirdML v2.** Only 4 of its tasks are loaded (6 public).
- **The 31 Terminal-Bench 4.0.0 tasks outside the clean set.** These have Epoch-listed defects or no agent solves them.

## Wave 2: decided, needs loaders and results ingestion first

| benchmark | tasks | why | rubrics | calls |
|---|---|---|---|---|
| Terminal-Bench 2.1 | 89 | densest multi-generation agentic set: G0 (GPT-6 Astra, Fable 5) and G1, with traces; 2.1 fixed 28 tasks | v1 + PL + MS (22) | 1,958 |
| Toolathlon-Verified | 108 | in Anthropic's September 2026 cards; verified release; traces for 13 configs | v1 + PL + MS (22) | 2,376 |
| ARC-AGI-2 (public eval) | 120 | frontier-reported; human-calibrated; 72 configs already local | v1 + MSm (18) | 2,160 |
| GPQA Diamond | 198 | per-item flags for 66 models (Every Eval Ever); expert-validated | v1 + MSm (18) | 3,564 |
| ArXivMath + BrokenArXiv (every month with outputs) | ~590 | ArXivMath is in the September cards; fresh monthly, so low contamination; BrokenArXiv is our only clean MCu/MCt outcome | v1 + MSm (18) | ~10,600 |
| **total** | **~1,105** | | | **~20,700, about $150–200** |

- **Agentic vs static sets.** The agentic sets get the full set. The static sets get the v1 rubrics and v2 MSm, with no
  PL rubrics.
- **Keep task texts out of the repo.** Terminal-Bench 2.1, Toolathlon and GPQA carry canaries or ask that items not be
  posted. Their texts stay in `data/` (gitignored), like the rest.
- **The work per set:**
  - an instance loader;
  - outcome ingestion: Harbor Hub job pages, the Toolathlon trajectories, the ARC dump, the Every Eval Ever datastore,
    the MathArena outputs.

## Not now, and why

- **Harbor-Adapter.** The best trace source (60 sets, 15 G1 models), but the author and licence are unknown. Ask
  before downloading. If cleared, it becomes wave 3: traces for GPQA, ARC-AGI-2 and TB 2.0, which wave 2 already labels.
- **OpenHands GAIA.** Gated and older. Its SWE-bench Verified outcomes are used in wave 1 as results only.
- **HAL.** G2 models only.
- **Exgentic AppWorld.** G1 and G2 only. Keep it as a demands-to-go candidate.
- **SWE-bench Pro, HLE and SimpleQA Verified.** Flawed, or no per-item data.
- **METR.** Its task texts are private.
- **OSWorld 2.0.** Multimodal.

## Decisions taken here (Pablo can veto)

1. Static sets get the v1 rubrics plus v2 MSm, not the PL rubrics.
2. Harbor-Adapter waits until its licence is clear.
3. ArXivMath and BrokenArXiv take every month that has model outputs, not only the latest.
4. The Epoch request is narrowed to G0 outcomes: GPQA G1 is now covered by Every Eval Ever.

## Needed from Pablo

- An Anthropic API key with a budget of about $450:
  - wave 1, about $230 with memory;
  - wave 2, about $200;
  - the gates, about $10.
- A Hugging Face token with access to the gated v1 battery, for gate 2.
- A Harbor Hub login, for bulk Terminal-Bench 2.1 trace downloads.
- Whether to email the Harbor-Adapter author.
