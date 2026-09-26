# swebench-30 — pre-registration

Committed before any label of this run exists. Run id `swev30-r1`.

**Question.** Do the ADeLe rubrics give usable, reproducible task-level demand labels on a
real agentic benchmark, through the judging path we would use at scale? This is an
annotation-quality check and a pipeline rehearsal. It is **not** a test of criterion validity:
n = 30, and SWE-bench Verified was rated Flawed by Epoch (2026-09-03) because many of its
rarely-solved tasks have tests that reject correct fixes.

## Items

- **30 new tasks** from SWE-bench Verified, excluding the 14 labelled in the 2026-09-14 pilot.
  Strata are terciles of the leaderboard solve rate (135 entries of `SWE-bench/experiments` at
  `40f164d`, official 500-task universe): low 0–0.378, mid 0.378–0.733, high 0.733–0.963.
  10 per stratum, seed 20260926 (`build_sample.py` → `sample.csv`).
- **14 anchors**: the pilot's SWE-bench tasks, re-judged on PLp, PLe and PLs only.
- Task text is the problem statement only (HF revision `c104f840`), as in both pilots.
- `suspect` = solve rate below 0.05: 4 of the new tasks, 3 anchors. Kept, and analysed with
  and without.

## Judges and protocol

- Two judges, Claude Sonnet and Claude Opus, run as Claude Code subagents (aliases `sonnet`,
  `opus`); no other provider is available. Snapshots and sampling settings cannot be pinned.
  The aliases may not map to the pilot's snapshots (that session ran Opus 5, this one Opus 5.5).
- One (task, dimension) per call, a fresh subagent each time, with the fixed instruction
  recorded in `labels/swev30-r1/run.json`.
- Prompt: `build_annotation_prompt` as on `agentic-v2`, the same for all 25 rubrics (18 v1, with
  v1's MSm replaced by the v2 MSm, plus the 7 other active v2 rubrics). Rubric examples kept.
- 792 prompts × 2 judges = 1,584 calls. Every rubric and prompt is hashed in `labels/swev30-r1/`.
- Unguessability is 100 for every task (open-ended) and is not judged.

## Pass/fail checks

1. **Parse rate** at least 98% per judge. A missing or unparseable answer is retried once, and
   the retry is recorded.
2. **Inter-judge agreement** on the 30 new tasks, per dimension: within-1 at least 80%.
   Exact agreement and quadratic-weighted κ are reported where both judges vary. A dimension
   below 80% is flagged as unreliable on this benchmark, not dropped.
3. **Test–retest** on the anchors: each judge within 1 of the same judge's pilot label on at
   least 80% of its 42 anchor cells.

## Predictions (sealed; descriptive, not gates)

- P1: PLe = 3 on at least 90% of new tasks, for each judge (checks exist but are elected).
- P2: PLs ≤ 1 on at least 90% (the executability clause).
- P3: PLp takes at least three distinct values across the 30.
- P4: MSm and MSc = 0 on at least 90% (an issue fix involves no social interaction).
- P5: Volume rises with SWE-bench's human time-to-fix bucket (Spearman ρ > 0, mean of judges).
- P6: PLp falls with solve rate (ρ < 0), with and without suspect tasks. At n = 30 the power to
  detect ρ = −0.3 is about 0.36, so a null result here is uninformative.

## Analysis

Scripts in `analysis/`, frozen outputs in `results/`. Per dimension: level distributions per
judge, with the v1 and v2 families side by side (the scale-comparison descriptive); agreement;
test–retest; P5 and P6 with and without suspect tasks. Every dimension is reported, including
those that fail a check.

## Run order and deviations

A dry run of a few calls comes first. If it changes the protocol (instruction, prompt or
judges), its labels are discarded and the change is recorded below as a deviation; otherwise
they are kept. The full run starts only after Pablo approves its measured cost.

### Deviations

None yet.
