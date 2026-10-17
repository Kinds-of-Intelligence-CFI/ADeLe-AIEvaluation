# tbsci-pl — pre-registration

Committed and pushed before any label of run `tbsci-pl`.

**Question.** Do the PL rubrics track difficulty on Terminal-Bench Science 0.1, a benchmark the labs report and that has
current-generation per-trial outcomes?

## Design

- **Tasks.** All 70 tasks of TB-Science 0.1 (tag `v0.1.0`, `f81afac`), instruction text only (`make_set.py` →
  `tasks.csv`). Pablo: annotate all, flag, filter later. Flags: `solved_any` (65) and `open_issue` (score-relevant open
  `[TASK FIX]` issues on GitHub, frozen in `open_issues.csv` on 2026-10-01: 37 tasks; the mapping is generous and is
  reviewed by Pablo before any claim rests on it).
- **Outcomes.** 12 public Harbor Hub configurations × 3 trials (GPT-6 Astra, Opus 5.5, …). Five rows, including Fable 5.1,
  have no public trials. No external review of this benchmark exists.
- **Labels.** PLp (text O), PLe, PLs; Opus 5.5 low, v2 prompt; run `tbsci-pl` via `adele mass` (210 calls).
- **Analysis** (`analysis/analyse.py`): Spearman of each rubric with solve rate and expert hours on all 70, on
  `solved_any`, and on `solved_any` without `open_issue`.

## Predictions (sealed)

- PLp against solve rate negative with p < 0.05 on all 70: 0.25 (Terminal-Bench 4.0 showed no link).
- PLp against expert hours positive with p < 0.05: 0.35.
- Most tasks at PLp 3: 0.7.
- No rubric significant on the solved, issue-free subset: 0.75.
