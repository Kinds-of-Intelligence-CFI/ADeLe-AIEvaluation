# relabel-v2 — pre-registration

Committed and pushed before any label of this study. Pablo approved the relabel on 2026-10-04, after the examples
review (`../examples-review`, `d4ec2ec`); it runs after the examples regression (`../examples-regression`) and after
the weekly usage reset (2026-10-06, 20:00 UTC), in a new session.

**Question.** How do the PLp, PLe, PLs, MSm and MSc labels of the seven agentic clean sets and the three social sets
change under the reviewed examples, and do the rubrics' signals hold?

## Design

- **Runs** (specs in `../mass-annotation/specs/`): `relabel-v2` (1,016 agentic tasks, as `pls-relabel`),
  `relabel-v2-long` (ProgramBench's 13 long tasks, chunked judge), `relabel-v2-eqbench4` (120), `relabel-v2-cooperbench`
  (120 pairs × solo and coop), `relabel-v2-gamearena` (24). Five rubrics each: 7,065 calls. Opus 5.5 low, v2 prompt.
- **Scope rule.** A rubric that fails the examples regression is left out and reported; the specs are edited before
  pinning if so.
- **Old labels.** `old_labels.csv`, frozen now from the labels then released or collected (7,052 rows).
- **Analysis** (`analysis/analyse.py`). Per set and rubric: level counts, share unchanged, mean shift; agentic sets:
  Spearman of old and new labels with the outcome (as `ms-benchmarks`; tau2 within domain); social sets: mean MSm and
  MSc, old and new. The social studies' own tests (EQ-Bench 4 disclosure, CooperBench drop, Game Arena edge) and Jev are
  rerun on the new labels afterwards and reported as an update to those studies.
- **Releases.** The seven agentic releases take all five rubrics from these runs.

## Predictions (sealed)

From the regression's real tasks (unchanged: PLp 80, PLe 90, PLs 90, MSm 90, MSc 100 per cent; judge noise alone
changed 20, 5, 20, 15 and 0 per cent):
- Pooled share unchanged at least 80 per cent: PLp 0.55, PLe 0.75, PLs 0.7, MSm 0.8, MSc 0.95.
- No set's mean shift above +0.3 or below −0.3 on any rubric: 0.7.
- SWE-bench Verified PLp keeps ρ ≤ −0.5 (old −0.58): 0.8. ProgramBench PLp stays significant and negative: 0.85.
- tau2 PLs stays significant and negative within domain (old −0.20): 0.55. DeepSWE PLs stays significant (old −0.22,
  p 0.03): 0.4.
- MS separation holds (mean MSc ≤ 1 on the single-agent sets, ≥ 2 on EQ-Bench 4 and CooperBench coop): 0.95.

## Cost

7,065 Opus-low calls; `adele mass plan` estimates about 35 weekly points (the PLs relabel used about 4 for 1,029 calls,
so likely about 28). Run with `/annotate`, at most four relays at a time, stopping at 85 per cent weekly usage.
