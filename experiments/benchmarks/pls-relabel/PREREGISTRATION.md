# pls-relabel — pre-registration

Committed and pushed before any label of runs `pls-relabel` and `pls-relabel-long`. Pablo approved the run on
2026-10-04; it is launched after the weekly usage reset (2026-10-06, 20:00 UTC).

**Question.** How do the PLs labels of the seven agentic benchmarks change under the adopted PLs text, which adds
three computer-world examples at Levels 3 to 5 (`10725fc`; `../pls-computer`)?

**Why.** The released PLs labels were made with the earlier text. `pls-computer` found the new examples lower PLs on
runnable code tasks (DeepSWE: 12 of 13 sampled tasks at Level 2 fell to 1). The releases and `SUMMARY.md` should carry
labels from the adopted text.

## Design

- **Tasks.** The clean sets of the PL studies, as in `ms-benchmarks` (`subset.csv`, `subset_long.csv` copied from
  there): SWE-bench Verified 443, tau2 242 (airline 49, retail 114, banking 79), Terminal-Bench 4.0 35, TB-Science 70,
  DeepSWE 90, FrontierSWE 19, ProgramBench 130. 1,029 tasks. Same task texts as the released labels.
- **Rubric.** v2/PLs as now in `src/` (sha256 `7ee1ed05…`).
- **Labels.** Opus 5.5 low, v2 prompt, one call per task: run `pls-relabel` (1,016 calls) and, for ProgramBench's
  13 long prompts, run `pls-relabel-long` (13 calls) with the chunked-read judge. Specs in `../mass-annotation/specs/`.
- **Reference.** The released v2/PLs label of each task (each study's `release/labels.csv`; tau2's domain from
  `labels_wide.csv`), from the earlier text with the same judge and prompt.
- **Analysis** (`analysis/analyse.py`). Per set: old and new level counts, the old-to-new crosstab, the share
  unchanged, the mean shift, and Spearman with the set's primary outcome for old and new labels (as `ms-benchmarks`,
  predicted negative; tau2 within domain, combined).

This is a relabel, not a test of the change; the change passed `pls-computer`. There is no decision rule. The new
labels replace the old ones in the releases, and `SUMMARY.md` reports both correlations.

## Predictions (sealed)

From `pls-computer`'s sample (unchanged: SWE-bench 18 of 20, DeepSWE 4 of 20, TB 4.0 16 of 20; judge noise alone
changed 6 of 20):
- DeepSWE: at least 50 of 90 at Level 1 or lower (now 31): 0.75. Mean shift below −0.3: 0.6.
- SWE-bench Verified: at least 80 per cent unchanged: 0.75.
- tau2: at least 80 per cent unchanged: 0.75.
- No set's mean shift is above +0.2: 0.9. More sets shift down than up: 0.7.
- TB-Science keeps at least 3 tasks at Level 3: 0.6. No task anywhere at Level 4 or 5: 0.85.
- Spearman with the outcome: SWE-bench new PLs significant and negative (old −0.18): 0.5; tau2 within domain
  significant and negative (old −0.19): 0.45. No other set significant and negative: 0.75.
- On every set of 90 or more tasks, the new ρ is within 0.1 of the old: 0.6.

## Cost

1,029 Opus-low calls on the subscription. `adele mass plan`: about 5 weekly points.

## Deviations

1. **2026-10-04: launched before the weekly reset**, at Pablo's request ("Run 2"), with weekly usage at 55 per cent.
   Recorded before any label. Nothing else changed.
