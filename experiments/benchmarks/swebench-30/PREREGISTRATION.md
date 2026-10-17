# swebench-30 — pre-registration

Committed before any label of this run exists. Run id `swev30-r1`; `swev30-r2` after
deviation 1, `swev30-r3` after deviation 2 and `swev30-r4` after deviation 3 (below).

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

1. **Judge harness (2026-09-26, before any full-run label).** The `swev30-r1` dry run
   (`labels/swev30-r1/RUNLOG.md`) showed two problems. A general-purpose subagent spends about
   69k tokens per call on its own scaffolding, against about 2k for the prompt. And Opus 5.5 was
   flagged by a safeguard on 2 of 3 attempts at one prompt, likely because the instruction asked
   it to save its reasoning. From run `swev30-r2` on, the judges are the `adele-judge` subagent
   defined in `adele-judge.md`: tools Read and Write only, and a short system prompt asking for
   the written assessment the INSTRUCTION specifies. The per-call message carries only the two
   file paths. Prompts, rubrics, sample, models, checks and predictions are unchanged. The six
   `swev30-r1` dry-run labels are discarded: kept aside under `data/`, never analysed.
2. **Judge context and effort (2026-09-26, before any full-run label).** The judges' transcripts
   from the `swev30-r2` dry run (`labels/swev30-r2/RUNLOG.md`) showed two gaps, both also present
   in r1. Claude Code gives every subagent the CLAUDE.md files of the session that launches it:
   the operator's user-level file with an imported personal profile, the workspace file, and the
   `ADELE_v2/CLAUDE.md` working guide once the judge reads a file below it. None gives rubric
   levels or expected levels, but none is part of this protocol, and others could not reproduce
   them. And the judges' reasoning effort was not set: it followed the launching session, `max`
   in both dry runs. From run `swev30-r3` on, `adele-judge.md` sets `omitClaudeMd: true` (no
   user, project or local CLAUDE.md files; Claude Code 2.1.271 or later) and `effort: max`. The
   r3 dry run checks the transcripts for any CLAUDE.md that still loads; the documentation does
   not say whether the nested guide does. Prompts, rubrics, sample, models, checks and
   predictions are unchanged. The six `swev30-r2` dry-run labels are discarded: kept aside under
   `data/`, never analysed.
3. **Judge files outside `ADELE_v2/` (2026-09-26, before any full-run label).** The `swev30-r3`
   dry run (`labels/swev30-r3/RUNLOG.md`) showed that `omitClaudeMd` removes the CLAUDE.md files a
   judge loads at start, among them the operator's auto-memory index, which r1 and r2 judges also
   received, but not the `ADELE_v2/CLAUDE.md` working guide: Claude Code attaches that one when the
   judge reads a file below its folder. From run `swev30-r4` on, the judges read their prompts from
   and write their answers to `judge-io/<run>/`, two levels above the repo, where no folder between
   the judging session's folder and the files has a CLAUDE.md. `make_prompts.py` copies the prompts
   there and `collect.py` reads the answers from there. A throwaway call in this layout carried no
   CLAUDE.md at all. Prompts, rubrics, sample, models, checks and predictions are unchanged. The one
   `swev30-r3` label is discarded: kept aside under `data/`, never analysed.
