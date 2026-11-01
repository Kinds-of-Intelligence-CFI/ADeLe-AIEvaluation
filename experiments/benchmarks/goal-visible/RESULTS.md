# goal-visible — results

**Question.** With the goal written into the judge input of the six coding and terminal sets (no tests, no
solutions), how do the five released rubrics change, and does the PL freeze bar hold?

**Answer.** Labels barely move, and the PL signals hold or sharpen. The PL freeze bar holds.
- **Agreement with the control** (same judge and prompt, old input), all sets pooled: PLp 86% exact, PLe and PLs
  higher (92%, 94%), MSm and MSc nearly 100% (they stay at 0). All labels but one (a PLe label) are within one
  level of their control.
- **Signals (Spearman with solve rate), new vs control:**
  - SWE-bench Verified PLp **−0.59** (control −0.56) and PLe **−0.31** (−0.18).
  - ProgramBench PLp −0.47 (−0.55), still strong.
  - DeepSWE, Terminal-Bench 4.0, TB-Science: no PL signal either way.
- **Wrong-sign links are gone.** The old input gave TB-Science PLp +0.24 (p 0.047) and FrontierSWE PLe +0.52
  (p 0.02). With the goal visible, no PL rubric has a significant positive link on any set.

**Freeze bar** (amendment, `97cda10`, set before results):
1. Every PL cell labelled or each gap explained: **holds**. The only missing PL cells are ProgramBench
   `zip-password-finder` and TB-Science `protein-active-learning`. The safety classifier stopped every attempt, and
   neither task has released PL labels.
2. PLp negative on SWE-bench Verified, p < 0.05: **holds** (−0.59, p ≈ 8e-43).
3. No PL rubric significantly positive on any set: **holds**.

**Sealed predictions:** 2 of 6 held. They held for SWE-bench PLp ≤ −0.45 (−0.59) and ProgramBench PLp ≤ −0.4 (−0.47).
They failed for:
- MS at Level 0 on at least 97% of every set: FrontierSWE has one MSm task at Level 1, so 95%.
- PLp agreement below 86%: it is exactly 86%.
- SWE-bench mean PLp up by 0.1: it fell by 0.11.
- A new significant signal absent in the control: none.

**Status.** Complete (2026-10-27). 3,935 cells: 3,927 labels, all written by Opus 5.5 at effort low, bare digit.
8 cells have no label (the two classifier-stopped tasks above). `mass check` passes on both runs.

## Run notes

- The original orchestrating session was deleted mid-run (18:49 on 2026-10-26). Its round-4 answers could not be
  verified without transcripts. They sit unused in `judge-io/goal-visible/quarantine-deleted-session-20261026/`, and
  their cells were re-judged.
- The run was paused and restarted once, at Pablo's request. The ledger stayed consistent throughout.
- No pinned prompt has a line over 2,000 chars (checked on all 3,935 prompt files). `build.py` now asserts this.

## Files

- `results/analysis.json`, `results/agreement.csv` (`analysis/analyse.py`); `build.py`;
  `../mass-annotation/runs/goal-visible*/labels.csv`.
