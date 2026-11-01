# spv-v2 — pre-registration, phase C (criterion validity on ZeroBench)

Committed before any label of phase C, with the prompt builder and analysis script. Phase B passed its kill rule; one
rule failed (B4, a miscalibrated prediction at the lightest overlay step; see `RESULTS.md`). The candidate text is
unchanged since phase B.

**Why.** Desideratum 9: does SPv track how often models fail on real visual items? ZeroBench is the only visual
benchmark found with per-question results for 2026 frontier models (`reports/Frontier sensory benchmarks.md`).

**Data and contamination.**
- ZeroBench is gated, and its terms ask that answers are not shared and that nothing is used for training. Pablo
  accepted the terms on 2026-10-05.
- The parquet stays in the gitignored `data/downloads/zerobench/`. Images go to `judge-io/spv2-c/images`, outside the
  repo. The judge's answers go to `data/annotations` and judge-io, both outside version control.
- Committed files carry question ids, levels, solve rates, question lengths and image counts. They carry no question
  text, answers or images.
- **Prompts never contain the answer.** Phase B showed the answer key changes almost nothing on synthetic stimuli.
- Outcome matrix: 67 models × 100 questions, from the public leaderboard page (`zerobench.github.io`). Its Plotly
  heatmap gives question ids explicitly. Each cell is the number of correct samples out of 5.

**Items.**
- All 100 main questions; no subquestions.
- Task text = the question, then one line per image giving its absolute path and native size, with "your view of it
  may be downscaled". 73 of the 108 images exceed 1,568 px on the long side, so the judge sees them shrunk. The size
  line tells it that fine detail may be finer than it looks. This is a protocol choice made for this run.
- Arms: `cur` and `cand`, two repeats each. **400 calls.** Same image judge as phase B.

**Outcome.** A question's solve rate is the mean over the 67 models of correct/5. The primary set is the 77 questions
solved at least once, by the project's clean-set rule; no list of named defects exists.

## Decision rule (`analysis/analyse_c.py`)

A question's level is the median of its two labels (lower if they differ).
- **Primary.** Under the candidate, Spearman ρ between level and solve rate on the 77 is at most −0.2, with one-sided
  p < 0.05 (negative direction). If so, criterion validity on ZeroBench is **supported**; otherwise it is **not
  supported**.
- This is evidence for desideratum 9, not a gate on the text. The text was settled by phases A and B.

**Also reported.**
- The same statistics for the current text.
- The bootstrap CI of (candidate ρ − current ρ).
- ρ on all 100, and against the 2026 models only (rows from Claude Opus 4.6 on).
- The partial ρ given question length and image count.
- Level counts, and repeat agreement.

**Caveats, stated before seeing labels.**
- ZeroBench is built to be hard for reasoning as well as perception. Its authors name counting, fine-detail
  recognition and multi-step arithmetic. SPv owns only the perception part, so a weak ρ is expected even for a good
  rubric.
- With 77 questions, a true ρ of −0.2 is detected only about half the time.
- Solve rates are near the floor (median 1.8%).

## Predictions (sealed)

- **Current text.** ≥ 70% of the 100 questions at Levels 1–2: 0.7. ρ weaker than −0.2 on the 77: 0.7. These are the
  audit's predictions.
- **Candidate.** Most questions at Levels 2–3: 0.6.
- **Primary.** Supported (ρ ≤ −0.2 and p < 0.05): 0.35.
- Candidate ρ more negative than current ρ: 0.65.
- The partial given length and image count keeps the candidate's sign: 0.7.
- Repeat agreement ≥ 75%: 0.7.

## Cost

400 calls with one to three real images each. About 3–4 weekly points; usage was 90% before this run.
