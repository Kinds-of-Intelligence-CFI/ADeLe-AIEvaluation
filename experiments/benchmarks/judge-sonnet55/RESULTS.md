# judge-sonnet55 — results

**Question.** Does Sonnet 5.5 at high effort label like Opus 5.5 at medium effort, at a lower cost?

**Answer.** No. The pre-registered verdict is "does not", and there are three problems.
- Sonnet 5.5's safeguards block about half of the PLp prompts, and a retry does not help. Only 65 of
  88 cells got a label.
- Where it answers, it agrees with Opus medium less well than Opus low does: 72% exact against 86%.
  It reads about a quarter of a level higher.
- It is not cheaper. A call costs about what an Opus call costs, and with the blocked calls each
  usable label costs about 1.7 times as much.

**Status.** Complete (2026-09-29): 112 calls, verdict "does not". As Pablo decided, the Sonnet 5.5
medium arm is skipped.

## Design

See `PREREGISTRATION.md`, pushed before any label (`9c48a31`).

- **Cells.** PLp and PLe on the 44 SWE-bench Verified gate tasks of `swebench-pl`: 88 cells. The
  prompts are byte-identical to the Opus-medium run `swepl-gate`.
- **Judge.** Sonnet 5.5 (`claude-sonnet-5-5`) at high effort, one call per cell. Failed cells were
  judged once more.
- **References.** Opus medium, Opus low, Opus max and Sonnet 5 max labels on the same cells.

## Pre-registered results

From `results/agreement.json` (`analysis/analyse.py`).

| check (Sonnet 5.5 high against Opus medium) | result | holds |
|---|---|---|
| 1. exact agreement 0.80 or more | 0.72 on 65 cells (Opus low on the same cells: 0.86) | no |
| 2. within one level 0.98 or more | 1.00 | yes |
| 3. mean shift within ±0.15 for PLp and for PLe | +0.29 (PLp, 21 cells) and +0.23 (PLe, 44 cells) | no |
| 4. at least 95% of cells labelled by Sonnet 5.5 | 65 of 88 (74%) | no |

**Verdict: "does not"** (exact agreement below 0.75).

**Coverage.** Every failure was the same harness error: "Sonnet 5.5's safeguards flagged this
message", category `reasoning_extraction`. Claude Code does not fall back to another model here, so
the call ends without an answer.
- First pass: 24 of 88 calls failed, all PLp (24 of 44 PLp cells).
- Retry: 23 of the 24 failed again. The flag is close to deterministic for a given prompt.
- One PLe call was flagged after it had written its answer; that answer counts.
- No answer was written by another model.

**Cost.**
- The plan's 5-hour meter went from 6% to 11% over the 112 calls, my own turns included. The weekly
  meter went from 96% to 97%. That is about 0.045% of a 5-hour window per call (±0.005% from the
  meter's 1% steps).
- References: Opus medium about 0.049% per call, Opus low about 0.041%. So Sonnet 5.5 high is not
  cheaper per call.
- Per usable label it is dearer: 47 of the 112 calls gave nothing, so each label cost about 0.077%.
- Calls were fast: 11 s on average, against 16 s for Opus medium.

**Sealed predictions.**

| prediction | p | outcome |
|---|---|---|
| verdict "works well" / "does not" / "unclear" | 0.25 / 0.45 / 0.3 | "does not" |
| exact agreement 0.80 or more | 0.3 | did not happen (0.72) |
| Sonnet 5.5 reads higher than Opus medium | 0.65 | happened (+0.25) |
| cheaper per call than Opus low | 0.45 | did not happen (about the same per call; dearer per label) |
| mean time per call above 16 s | 0.85 | did not happen (11 s) |
| at least one answer by another model, or one classifier stop | 0.3 | happened (47 flagged calls; no other-model answers) |

## Exploratory results

- **Sonnet 5.5 high sits closer to the max-effort judges.** Exact agreement is 0.80 with Opus max
  and 0.88 with Sonnet 5 max, against 0.72 with Opus medium and 0.71 with Opus low. Its offset
  from Opus max is +0.14. So its labels differ from Opus medium's by calibration, not by noise:
  every label is within one level.
- **It puts far more cells at Level 3.** 44 of its 65 labels are 3 (68%). Opus medium puts 35 of
  the 88 cells at 3 (40%).
- **Why PLp and not PLe?** Both prompts carry the same instruction, which asks for written
  "CHAIN-OF-THOUGHTS REASONING STEPS". Only the rubric differs. This run cannot say which part of the
  PLp prompt triggers the classifier. Rewording the shared instruction would be a change to the
  production prompt for every judge, so it was not tried.

## Deviations and caveats

- No deviations from the pre-registration.
- The 21 PLp cells with a label are the ones the safeguard let through, not a random half. The PLp
  agreement figures describe that subset.
- The cost figures come from 1% meter steps and include my orchestration turns, as the reference
  figures for Opus do.
- One sample of 44 tasks from one benchmark. Other benchmarks may flag more or less.

## Reproduce

```
python experiments/benchmarks/judge-sonnet55/analysis/analyse.py
```

The numbers above are those committed with this file. The judges' answers stay out of the repo
(`data/annotations/s55h-gate/`).
