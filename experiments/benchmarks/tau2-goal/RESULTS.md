# tau2-goal — results

**Question.** With the tau2 task shown with its goal but without the grader's expected-action list, how do the five
released rubrics change, and does MSc still match Pablo?

**Answer.** MSc holds. It matches Pablo on 13 of 15 (15 within one) and falls with solve rate at ρ −0.27 (p < 0.001).
That clears the bar set for freezing MSc.
- **Against tau2-full** (which also showed the expected actions): 87% of labels are identical. Most of the stronger
  signal survives: PLp −0.41 (tau2-full −0.48), PLs −0.32 (−0.34), MSc −0.27 (−0.32). MSm and PLe lose most of their
  gain: MSm −0.15 (−0.21), PLe −0.15 (−0.20). Both are still negative with p < 0.05.
- **Against the released labels** (script only): every signal is stronger. Released: PLp −0.28, PLs −0.15, PLe −0.14,
  MSm −0.12, MSc +0.10.
- **Sealed predictions:** 3 of 3 held.

**Status.** Complete (2026-10-26). 1,210 of 1,210 cells labelled, all written by Opus 5.5 at effort low, bare digit.
No rejected answers, and `mass check` passes on both runs. Weekly usage 27% → 32%. The label set and the release are
unchanged; that waits for Pablo's OK.

## Design

See `PREREGISTRATION.md` (`f9691b9`; note before launch `08c111c`). Released labels from `../tau2-full/old_labels.csv`;
tau2-full labels as `../tau2-full/analysis/analyse.py` reads them (airline and retail from `tau2-full`, banking from
the plain-text re-judge).

## Results

Levels are counts of tasks: released → tau2-full → tau2-goal.

| rubric | released | tau2-full | tau2-goal | exact vs tau2-full |
|---|---|---|---|---|
| MSc | 1:2 2:203 3:13 4:24 | 1:91 2:147 3:4 | 1:91 2:146 3:5 | 85% |
| MSm | 1:24 2:194 3:24 | 1:66 2:174 3:2 | 1:48 2:192 3:2 | 82% |
| PLp | 1:28 2:213 3:1 | 1:62 2:163 3:17 | 1:54 2:169 3:19 | 91% |
| PLe | 1:186 2:36 3:20 | 1:169 2:46 3:26 | 1:168 2:47 3:27 | 90% |
| PLs | 0:5 1:16 2:221 | 0:7 1:49 2:185 | 0:7 1:37 2:198 | 90% |

Without the expected actions, fewer MSm, PLp and PLs labels drop to Level 1, mostly in retail (MSm Level 1: 25 → 10;
PLp: 37 → 29). Per-domain tables are in `results/analysis.json`.

**Criterion signals** (Spearman with solve rate, within domain, predicted negative; n 241–242):

| rubric | released | tau2-full | tau2-goal |
|---|---|---|---|
| PLp | −0.28 | −0.48 | **−0.41** (p < 0.001) |
| PLs | −0.15 | −0.34 | **−0.32** (p < 0.001) |
| MSc | +0.10 | −0.32 | **−0.27** (p < 0.001) |
| PLe | −0.14 | −0.20 | −0.15 (p 0.02) |
| MSm | −0.12 | −0.21 | −0.15 (p 0.03) |

## MSc against Pablo's 15 labels

| | exact | within 1 | mean (judge − Pablo) |
|---|---|---|---|
| released | 5 | 6 | +1.67 |
| tau2-full | 14 | 15 | −0.07 |
| **tau2-goal** | **13** | **15** | 0.00 |

The two misses, both by one level: H-08 (retail 11), Pablo 2, judge 3; H-14 (airline 22), Pablo 2, judge 1. H-14 was
also the miss in tau2-full. All the airline refusal items the script put at 3 or 4 stay at 1.

## Sealed predictions

| prediction | sealed | result |
|---|---|---|
| MSc exact vs Pablo ≥ 12 of 15 | 0.65 | held (13) |
| PLp negative signal, p < 0.05 | 0.8 | held (−0.41) |
| pooled exact vs tau2-full ≥ 80% | 0.6 | held (87%) |

## Files

- `results/analysis.json` (`analysis/analyse.py`); `build.py`; `../mass-annotation/runs/tau2-goal*/labels.csv`.
