# ms-benchmarks — pre-registration

Committed and pushed before any label of runs `ms-benchmarks` and `ms-benchmarks-long`.

**Question.** How do the two social rubrics, MSm (Mind modelling and social cognition) and MSc (Communication and
social interaction), rate the agentic benchmarks we labelled for planning, and do they track difficulty where other
parties are involved?

## Design

- **Tasks** (Pablo, 2026-10-02: "MSc and MSm for all of those benchmarks"). The clean sets of the PL studies, 1,083
  tasks (`make_subset.py`): SWE-bench Verified 443, tau2 242 (airline 49, retail 114, banking 79), Terminal-Bench 4.0
  35, TB-Science 70, DeepSWE 90, FrontierSWE 19, ProgramBench 130, rivercross grid 54. Same task texts as the PL labels.
- **Rubrics.** v2/MSm and v2/MSc, team drafts unchanged since 2026-09-02 (`docs/rubric-provenance/MSm.md`, `MSc.md`).
  MSc has human anchor labels at every level; MSm has none.
- **Labels.** Opus 5.5 low, v2 prompt, one call per task and rubric: run `ms-benchmarks` (2,140 calls) and, for
  ProgramBench's 13 long prompts, run `ms-benchmarks-long` (26 calls) with the chunked-read judge (stopping rule
  fixed 2026-10-01). Specs in `../mass-annotation/specs/`.
- **Analysis** (`analysis/analyse.py`). Per set: level distribution, share at level 0 or 1, and Spearman with the set's
  primary outcome (solve rate; tau2 within domain, combined; rivercross: Opus's non-optimal share).

## Predictions (sealed)

Priors: only tau2 has another party (a simulated customer with goals). The other sets are single-agent; at most a
judge may credit inferring an issue author's or user's intent.

- On each single-agent set (all except tau2), at least 90% of tasks at level 0 or 1 on both rubrics: 0.75.
- tau2: median MSc at least 2 in every domain: 0.65; median MSm at least 2 in every domain: 0.45.
- tau2: MSc within domain negative with p < 0.05: 0.4. MSm: 0.3.
- On the single-agent sets, no rubric is significant (p < 0.05) against the outcome where testable: 0.7.

**Cost.** 2,166 Opus-low calls on the subscription.

## Amendment 1 (2026-10-02, before any label)

- **Rivercross dropped** (Pablo): it has no other agents, so both rubrics are 0 by construction and the 108 calls would
  test nothing. 1,029 tasks remain; `ms-benchmarks` has 2,032 cells and `ms-benchmarks-long` 26.
- **Order** (Pablo): the run waits for the MS lab regression (`../ms-lab-regression/`), which checks that today's judge
  and prompt reproduce the lab's results for MSm and MSc. If that regression fails, this run is held and Pablo decides.
- Predictions unchanged.
