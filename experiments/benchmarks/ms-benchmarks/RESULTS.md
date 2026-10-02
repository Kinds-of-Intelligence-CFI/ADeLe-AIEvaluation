# ms-benchmarks — results

**Question.** How do the two social rubrics, MSm (Mind modelling and social cognition) and MSc (Communication and
social interaction), rate the agentic benchmarks we labelled for planning, and do they track difficulty where other
parties are involved?

**Answer.** They separate social from single-agent tasks cleanly, but they do not track difficulty on tau2. Every
single-agent set is at 0 on both rubrics (at least 95% of tasks; only 4 of 788 labels above 0). tau2 sits at 2 on both
(MSc reaches 4 on 25 tasks, mostly airline). Within tau2, neither rubric falls with solve rate (MSc +0.09, MSm −0.07,
both ns).

**Status.** Complete (2026-10-02). 2,058 cells (1,029 tasks × MSm, MSc), 2,054 labelled by Opus 5.5 at effort low,
check OK. No label: `protein-active-learning` (TB-Science) and `zip-password-finder` (ProgramBench), both classifier
fallbacks on every attempt, as with the planning rubrics. Four of six sealed predictions held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`e628a3f`; amendment 1, `bfec0a5`, dropped rivercross). The clean
sets of the PL studies: SWE-bench Verified 443, tau2 242, Terminal-Bench 4.0 35, TB-Science 70, DeepSWE 90,
FrontierSWE 19, ProgramBench 130. Runs `ms-benchmarks` (2,032 cells) and `ms-benchmarks-long` (26 cells, chunked-read
judge). The MS lab regression (`../ms-lab-regression/`) ran first.

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`).

| set | MSm levels | MSc levels | share at 0–1 (MSm / MSc) |
|---|---|---|---|
| SWE-bench Verified (443) | all 0 | all 0 | 1.00 / 1.00 |
| ProgramBench (129) | all 0 | all 0 | 1.00 / 1.00 |
| DeepSWE (90) | all 0 | all 0 | 1.00 / 1.00 |
| Terminal-Bench 4.0 (35) | 0: 34, 1: 1 | 0: 34, 1: 1 | 1.00 / 1.00 |
| TB-Science (69) | 0: 68, 2: 1 | all 0 | 0.99 / 1.00 |
| FrontierSWE (19) | 0: 18, 2: 1 | all 0 | 0.95 / 1.00 |
| tau2 (242) | 1: 15, 2: 201, 3: 26 | 1: 1, 2: 200, 3: 16, 4: 25 | 0.06 / 0.00 |

**tau2 against solve rate, within domain** (Spearman, combined by Fisher z):

| | combined | airline (49) | retail (114) | banking (79) |
|---|---|---|---|---|
| MSm | −0.07, p 0.32 | +0.26, p 0.07 | −0.06 | −0.27, p 0.015 |
| MSc | +0.09, p 0.16 | +0.25, p 0.08 | +0.17, p 0.08 | −0.12 |

Mean MSc by domain: airline 2.80, banking 2.27, retail 2.04. On the single-agent sets the rubrics are constant or have
one task off zero, so nothing is testable there; where a coefficient exists it is not significant.

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| each single-agent set at least 90% at level 0–1 on both rubrics | 0.75 | held (lowest 95%) |
| tau2: median MSc at least 2 in every domain | 0.65 | held (2, 2, 2) |
| tau2: median MSm at least 2 in every domain | 0.45 | held (2, 2, 2) |
| tau2: MSc within domain negative, p < 0.05 | 0.4 | failed (+0.09) |
| tau2: MSm within domain negative, p < 0.05 | 0.3 | failed (−0.07) |
| single-agent sets: no rubric significant where testable | 0.7 | held |

## Reading

- **The rubrics read what they should.** Coding, terminal and program-rebuilding tasks involve no one to model or
  steer, and the judge says so almost without exception. tau2, the one benchmark with another party, sits two levels
  up on both.
- **tau2's difficulty is not social, by these labels.** Airline tasks get the highest MSc (customers pushing against
  policy, many at Level 4), yet they are not harder for agents; if anything the sign runs the other way. tau2's
  simulated users follow scripts that the judge can read, and agents fail mostly on procedure and policy, which PLp
  tracks (−0.30 within domain).
- **Banking's MSm −0.27 is the one per-domain signal**, not pre-registered as a primary test; it would need
  replication.
- These benchmarks cannot test MSm or MSc's criterion validity: there is too little social variation. That needs
  benchmarks built around other parties.

## Deviations and caveats

- Rivercross was dropped before any label (amendment 1).
- Runner fix during the run: two judges wrote to `prompts/../responses/…`; the runner now normalises paths
  (`src/adele/mass/backends/subagent.py`, local commit awaiting push approval). No answer changed.
- One chunked-read answer was written before the judge finished reading; rejected for protocol and relabelled.
