# jev-pilot — pre-registration

Committed and pushed before the full run (three smoke-test tasks were labelled to check the request format; their
labels are not looked at beyond the format). Pablo asked for the run on 2026-10-04 ("all new benchmarks and all
dimensions").

**Question.** Can TypeSafe's Jev, a fast System One classifier with no written reasoning, reproduce our Opus 5.5
(effort low) demand labels on agentic and social tasks, for the planning rubrics (PLp, PLe, PLs) and the social ones
(MSm, MSc)? And does it keep their criterion validity?

## Design

- **Model.** `jev-1.13.0`, pinned. One request per task with five Score questions (`run_jev.py`): the rubric's
  opening paragraphs in `instructions`; its six levels in `criteria`, each with its statement and example bullets as
  written. State: the task text the Opus judge saw. Rubric texts: the active catalog (same as the Opus labels).
- **Tasks.** The seven clean agentic sets (1,029 tasks; specs `pls-relabel`, `pls-relabel-long`) and the three social
  sets (EQ-Bench 4: 120 scenarios; CooperBench: 120 pairs × solo and coop; Game Arena: 24 game × role). 100 seeded
  tasks are labelled twice to measure determinism. Tasks over Jev's 32k-token state budget are skipped and reported.
- **Jev label.** The most probable level; the expected level and the confidence are kept too.
- **Reference.** The Opus labels already released or collected: PLp and PLe from each study's release; PLs from
  `pls-relabel`; MSm and MSc from `ms-benchmarks`; the social sets from their mass runs. Only valid answers written
  by Opus 5.5 count.
- **Analysis** (`analysis/analyse.py`). Per rubric, pooled and per set: exact agreement, within-one agreement,
  quadratic weighted κ, mean signed difference (Jev − Opus), and level distributions. For the seven agentic sets: each
  rubric's Spearman with the set's primary outcome, Jev against Opus (as `ms-benchmarks`; tau2 within domain). The
  MS separation check: mean MSc on the single-agent sets and on the social sets. Confidence: Spearman of Jev's
  confidence with exact agreement. Determinism: share of identical labels on the 100 repeats.

There is no decision rule. This is a feasibility pilot: it tells us whether a Jev arm is worth a proper study.

## Predictions (sealed)

- Pooled within-one agreement with Opus: PLp ≥ 85 per cent 0.5; PLs ≥ 85 per cent 0.45; MSc ≥ 85 per cent 0.7.
- Quadratic weighted κ ≥ 0.6 on PLp: 0.35. κ higher on MSm and MSc than on all three PL rubrics: 0.6.
- Jev puts PLs higher than Opus on the coding sets (SWE-bench, DeepSWE, ProgramBench, FrontierSWE), since it reads
  rules literally and the run-and-look clause takes reasoning: 0.65.
- MS separation holds (mean MSc at most 1 on the single-agent sets and at least 2 on EQ-Bench 4 and CooperBench coop):
  0.7.
- Criterion validity: Jev's PLp on SWE-bench Verified significant and negative 0.6; ρ ≤ −0.45 (Opus −0.58) 0.3.
  Jev's PLp tau2 within domain significant and negative: 0.45.
- Higher confidence goes with higher exact agreement (ρ > 0, p < 0.05): 0.65.
- At least 95 per cent of repeat labels identical: 0.7.
- Fewer than 20 tasks skipped for length: 0.8.

## Cost

About 16M input tokens at $0.042 per million: under $1. No subscription usage.

## Amendment 1 (2026-10-04, during the run, before any result was looked at)

Pablo asked whether to use Jev's distributions and Opus's reasoning. Added, all from labels already being collected:
- **Probability on Opus's level**: mean probability Jev puts on the level Opus chose, and the log loss of Opus's labels
  under Jev's distribution (probabilities floored at 0.01), per rubric. This credits Jev for spreading mass where a
  task is ambiguous, since a single Opus sample is itself noisy (`pls-computer`: 6 of 20 reruns changed).
- **Calibration**: for each level Jev gives probability p, the share of cases where Opus chose it, in bins of 0.1.
- **Expected level**: Spearman of Jev's expected level with each agentic set's outcome, next to its most probable
  level and Opus's label.
- **Diagnosis (descriptive)**: 8 disagreements per rubric (40), seeded, of two levels or more where possible. For
  each, Opus's written reason is read and the deciding clause is named, to see whether Jev misses the same clauses.

Predictions (sealed):
- Jev's expected level tracks the outcome at least as well as its most probable level on SWE-bench PLp: 0.6.
- Mean probability on Opus's level ≥ 0.4 for PLp: 0.5.
- In the diagnosis, a single clause explains at least half of the PLs disagreements: 0.55.
