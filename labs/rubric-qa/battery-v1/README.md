# Agentic validation battery v1 — the standing instrument

**This replaces the round-26 stress battery.** That battery was scored four times over and
the rubrics were revised against it, so improvements measured on it could no longer be
distinguished from tuning to it. It was also never built to the design targets in
`docs/agentic-open-questions.md`. This one is; `prereg.json` records the design, the full
4-dimension prediction matrix, and the hypotheses, all written before any scoring.

## Design

36 items, each scored on all four dimensions — 144 predictions.

| | |
|---|---|
| **16 pure** | 4 per dimension, high on it and low on the other three. Each such item serves three pair-directions at once, so 16 items cover all six pairs in both directions where a pairwise design would need 48. |
| **6 co-occurring** | one per pair, built to be high on *two* dimensions. This is the honesty check: a battery of pure items alone would manufacture separation. |
| **10 mid-band** | so the battery tests calibration, not just the ends. Three are MSc, deliberately — audit §4 records that MSc looks near-binary on real benchmarks, and a battery of extremes could not tell whether that is the rubric or the benchmarks. |
| **4 anchors** | 0 on everything. |

## Results

**Separation — 10 of 12 directions at a gap of 3+, the other two at a consistent 2.**

```
  PLp>>PLe [3,3,4,3]   PLe>>PLp [4,5,4,5]   PLp>>PLs [3,3,4,3]   PLs>>PLp [3,3,3,1]
  PLp>>MSc [3,3,4,3]   MSc>>PLp [3,2,3,1]   PLe>>PLs [4,5,4,4]   PLs>>PLe [2,2,3,2]
  PLe>>MSc [4,5,4,5]   MSc>>PLe [4,5,4,4]   PLs>>MSc [4,4,5,5]   MSc>>PLs [4,5,4,4]
```

**Co-occurrence — 6 of 6.** Every item built to load two dimensions scores 4+ on both. The
separation above is not an artefact of the item set.

**Anchors — clean.** All four score ≤1 on all four dimensions.

**Calibration — 10 of 11 mid-band predictions within 1.** The exception is D10 (PLs
registered 3, observed 5).

**MSc is not near-binary — audit §4 refuted on designed items.** MSc returned 2, 2, 3 on
its three mid-band items, exactly as registered. It looks binary on real benchmarks
because real benchmarks contain almost no mid-band social tasks, not because the rubric
cannot score them.

**Agreement, reported with the distribution beside it as the standing convention requires
— and not optimised, per the warning in the design targets.**

```
  PLp  alpha 0.872   levels {0:10, 1:9, 2:4, 3:7, 4:6}
  PLe  alpha 0.920   levels {0:15, 1:6, 2:5, 3:2, 4:2, 5:6}
  PLs  alpha 0.896   levels {0:18, 1:5, 2:4, 3:2, 4:2, 5:5}
  MSc  alpha 0.990   levels {0:25, 1:1, 2:2, 3:1, 4:4, 5:3}
```

MSc's 0.990 should be read against its distribution: 25 of 36 items are 0. High agreement
on a dimension that is mostly off is cheap, which is exactly why the convention exists.

## The one defect it found, and the two passes to fix it

The battery's first run failed three separation directions, all from one cause: **PLe
scored 2 on tasks that are purely conversational or purely observational** — 8 items, all
three judges. Judges were counting conversational turns and acts of looking as actions
with checkpoint feedback. The preamble already says words and tokens are not actions, but
that does not reach an offer in a negotiation.

The carve-out went at L2, where all eight items landed, per the rule confirmed three times
in rounds 20, 32 and 31.

- **Pass 1** excluded conversation *and* observation. Conversation was fixed outright — all
  four pure-MSc items went 2 → 0 — but the observation half was too broad and swallowed
  S04, the chemical plant, which r32 had just fixed. Monitoring a plant does involve acting
  on the world.
- **Pass 2** narrowed observation to tasks whose *whole* demand is establishing what is
  happening, and added that where a task also requires acting on the world those actions
  are assessed in PLe as usual. `MSc>>PLe` went from [2,2,2,2] to [4,5,4,4], S04 recovered
  to [2,3,4] inside its 2|3|4 band, and the old battery held at 53/72.

## What was deliberately not fixed

Two directions separate by 2 rather than 3, and both were left alone.

- `PLs>>PLe`: PLe scores 2 on pure-observation items like counting stock in a warehouse
  while staff move it. On reflection that is defensible — a long count *is* execution with
  checkpoints — and my registered 1 was probably too strict.
- `MSc>>PLp`: PLp scores 3 on the two-neighbour boundary dispute. Finding a settlement both
  parties will sign is a search over possible agreements, so PLp > 0 is arguable, and my
  registered 0 was too strict.

Neither met the pre-registered fix rule (2 of 3 judges missing across 2+ items sharing a
cause), and the fix budget was one round, spent. Chasing them would have reproduced exactly
the overfitting this battery exists to escape. They are recorded as measured, with the
number, and the more likely explanation is my item calibration rather than the rubrics.
