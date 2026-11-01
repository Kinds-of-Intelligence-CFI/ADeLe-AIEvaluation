# programbench-pl — results

**Question.** Do the PL rubrics track difficulty on ProgramBench, where an agent must rebuild a whole CLI program from
its execute-only binary and documentation, with current-generation outcomes?

**Answer.** Yes for PLp, strongly: on 128 clean tasks PLp falls with solve rate at ρ = −0.48 (p = 10⁻⁸). Tasks at PLp 2
are solved by 42% of runs on average, tasks at PLp 3 by 16%. The result holds without flagged tasks (−0.30, n = 64),
at every threshold, and after controlling for prompt length (exploratory partial ρ = −0.46). PLp also rises with
ProgramBench's own difficulty label (+0.19, p = 0.03). PLe and PLs are weak or null.

**Status.** Complete (2026-10-01). 390 cells in two runs: 348 of 351 single-read cells and 38 of 39 chunked-read cells
labelled by Opus 5.5 at effort low. Unlabelled: zip-password-finder (all three rubrics; a safety classifier handed
every attempt to Opus 4.8) and age (PLp; the judge twice stopped one line short of the prompt's end, which the
full-read check rejected). Five of seven sealed predictions held.

## Design

See `PREREGISTRATION.md`, pushed before any label (`fd9d8ae`). ProgramBench v1.2.5 (200 tasks); 25 runs; a (run, task)
cell is solved when score ≥ 0.9; clean set: tasks some run brings to 0.9 (130). Prompt: the agent instruction, the
workspace listing and the full documentation. Prompts too long for one Read (13 tasks) were judged by the same model
reading in 200-line parts; the protocol check required every line to come back (`route.py`, `relay.chunk_lines`).
Labels: runs `programbench-pl` and `programbench-pl-long` of `adele mass`, v2 prompt, PLp text O.

## Pre-registered results

From `results/analysis.json` (`analysis/analyse.py`). Spearman, Fisher-z 95% intervals.

| | clean (128) | clean, unflagged (64) | no docs damage (72) | no knowledge-gated (116) |
|---|---|---|---|---|
| PLp vs solve rate at 0.9 | −0.48 [−0.61, −0.33] | −0.30 [−0.51, −0.05] | −0.39 | −0.45 |
| PLp vs solve rate at 0.75 / 0.5 | −0.42 / −0.40 | −0.26 / −0.37 | −0.34 / −0.41 | −0.39 / −0.37 |
| PLp vs mean score | −0.48 | −0.34 | −0.41 | −0.46 |
| PLp vs difficulty label | +0.19 [+0.01, +0.36], n 120 | +0.15 | +0.18 | +0.21 |
| PLe vs solve rate at 0.9 | −0.09 (ns) | | | |
| PLs vs solve rate at 0.9 | −0.14 (ns) | | | |

PLe reaches p < 0.05 only at the 0.5 threshold and on mean score (−0.19).

**Levels (clean).** PLp 2/3 = 24/104. PLe 3/4 = 116/13. PLs 1/2 = 114/15.

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| PLp vs solve rate at 0.9 negative, p < 0.05 | 0.45 | held (−0.48) |
| PLp negative in sign | 0.7 | held |
| PLp vs difficulty label positive, p < 0.05 | 0.45 | held (+0.19, p 0.033) |
| PLe vs solve rate at 0.9 negative, p < 0.05 | 0.3 | failed (−0.09) |
| PLs vs solve rate at 0.9 negative, p < 0.05 | 0.2 | failed (−0.14) |
| the 13 chunked tasks have higher mean PLp than the other 117 | 0.7 | held (3.0 against 2.79) |
| every chunked cell passes the full-read check within its retry budget | 0.8 | failed (age PLp, twice one line short) |

## Exploratory (not pre-registered)

Prompt length could drive both labels and outcomes. It barely does: solve rate falls slightly with prompt length
(ρ = −0.17) and PLp rises slightly with it (+0.16). Partialling length out leaves PLp against solve rate at −0.46;
within prompt-length terciles it is −0.59, −0.36 and −0.41.

## Reading

ProgramBench is the clearest agentic result so far after SWE-bench: PLp separates tasks the judge sees as a small,
well-specified rebuild (Level 2) from larger ones (Level 3), and agents fail the latter far more often. Unlike
Terminal-Bench and FrontierSWE, the tasks share one form (rebuild a program from its documentation), so the remaining
variation is mostly in the program, which is what PLp reads. As elsewhere, the judge uses only two levels.

## Deviations and caveats

- Two tasks are not fully labelled: zip-password-finder (no label on any rubric: classifier fallback) and
  age (no PLp label). n = 128 for PLp, 129 for PLe and PLs.
- The chunked judge stopped early on a prompt of exactly 1,001 lines: after five full 200-line parts it did not read
  line 1,001. The check caught it both times; the instruction "until a Read returns fewer than 200 lines" is fragile
  when the last part is exactly full.
- Solve rates sit near the floor (31 tasks solved by one run of 25).
