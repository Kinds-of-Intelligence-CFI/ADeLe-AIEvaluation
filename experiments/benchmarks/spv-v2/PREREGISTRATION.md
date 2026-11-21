# spv-v2 — pre-registration, phase A (text-only lab regression)

Committed before any label of this study, with the candidate, items, prompt builder and analysis script.
Pablo asked on 2026-10-05 to fix SPv to the standard of the other v2 rubrics ("let's fix it"), after the audit in
`docs/SPv-desiderata-audit.md`.

**Why.** The audit found four failures in the current `SPv.txt`:
- **Fineness is carved out.** Small, faint or low-contrast content scores as if read at a glance. This is the main
  known cause of visual failure in models, and no dimension owns it.
- **No aggregation rule.** Nothing says how to score a task that needs several pieces of content.
- **Out of v1 shape.** The preamble plus the "does not cover" paragraph is 362 words.
- **No real-image evidence.**

Phase A tests the rewritten text on text items. Phase B (real images: severity sweeps, routing traps) and phase C
(criterion: ZeroBench, VLMEvalKit subsets) are pre-registered separately, after A.

**Candidate.** `SPv_candidate.txt`. It keeps the single driver: how far the needed content sits from a plain
reading of the image. The ladder is read off (1), brought out (2), completed (3), combined (4), inverted (5).
Changes:
1. **Fineness restored inside the driver.** Content that is small, faint, low in contrast, or laid over other content
   must be *brought out* (Level 2). Content below the image's resolution is *lost* and must be completed (Level 3).
2. **Aggregation rule.** A task is set by the hardest piece of content it needs.
3. **Level 5 re-anchored** on inversions that are perceptual: shape from shading, shape from refraction, and speech
   from a vibrating object in silent video. The examples that leaned on geometry or physics are gone: building height
   from its shadow, room layout from a curved reflection.
4. **The impressions example moved from Level 5 to Level 2.** Grooves are present in the image.
5. **Screen and chart examples at Levels 1–4.**
6. **Compressed.**

| | preamble | does not cover | level texts | examples |
|---|---|---|---|---|
| current | 231 words | 131 words | 23–90 words | 18 |
| candidate | 175 words | 108 words | 26–71 words | 22 |

Unchanged: the search, meaning, transformation, duration and generation carves; the many-plain-elements carve; the
registered-layers rule; the 3/4 and 4/5 boundaries.

## Design

- **Judge.** Opus 5.5 at effort low, `adele-judge-v2-low`, relayed by `judge-dispatcher-v2-low`.
  - v2 prompt (`build_annotation_prompt_v2`); the rubric is shown as the catalog shows it.
  - One item per call. Only answers written by `claude-opus-5-5` count.
  - Never Fable. JUDGING.md rule 3: one strong judge.
- **Blinding.** Opaque file ids; all sets and both texts shuffled into run `spv2-1`.
- **4-gram check (JUDGING.md rule 4).** Every L and M item is checked against every example bullet of both texts:
  none shares a 4-gram. Among the candidate's own examples, one shared 4-gram ("of an object from", Levels 4 and 5)
  was removed before sealing.

| set | items | texts | labels per item and text | calls |
|---|---|---|---|---|
| P placement | the candidate's 22 example bullets, each judged under the candidate with that bullet removed (all other examples kept) | cand | 3 | 66 |
| L ladder and carves | 16 items: a 0–5 ladder with fineness, overlay and below-resolution rungs; one aggregation item; six carve traps (search, counting, meaning, transformation, ARC-like induction, generation) | cur, cand | 3 | 96 |
| M minimal pairs | 5 pairs, each differing in one respect: size (M1), blur that keeps or merges digits (M2), contrast (M3), overlay against part hidden (M4), one view against several (M5) | cur, cand | 3 | 60 |

222 calls in pass 1. Items and per-text predictions are in `items.csv`.

## Decision rules (`analysis/analyse.py`)

An item's label under a text is the median of its labels (lower middle if even).
1. **Placement.**
   - At least 19 of 22 examples (85%, the sensory gate) are exact, and none is off by two or more.
   - An example off by two or more is replaced and re-placed. It does not by itself fail the text.
2. **Ladder and carves, candidate.**
   - At least 13 of 16 L items at prediction, and none off by two or more.
   - Every carve at 1 or below (generation at 0).
3. **Fineness.** L-V2s, L-V2f, M1b and M3b are at Level 2 under the candidate.
4. **Pairs, candidate.** In every pair, b is at least one level above a.
5. **Pass 2 (`spv2-2`).** Every item off by two or more, and both items of every failing pair, are judged again under
   both texts, three repeats each, and pooled with pass 1. If more than 8 items need pass 2, I stop and report first.
6. **The candidate passes phase A** if rules 1–4 hold after pass 2.
   - If it passes, phase B is pre-registered next. `SPv.txt` changes only after phase B, with Pablo's OK.
   - If it fails, the report names the failing clause. Only that clause is revised, and only the affected items
     are re-run.

**Also reported.**
- Every item's labels under both texts.
- What the current text does on the fineness items (predicted: L-V2s, L-V2f, M1b and M3b at 1).
- Which examples the candidate's answers cite.

## Predictions (sealed)

- **Placement.**
  - At least 19 of 22 exact: 0.6. None off by two or more: 0.8.
  - Likeliest misses: the crossing-lines chart (read as search, to 1): 0.4; the fog sign (to 2): 0.3; the crisp
    packet (to 4 or 3): 0.25.
- **Ladder.**
  - At least 13 of 16 L items at prediction under the candidate: 0.75.
  - L-V5 (a wall lit by an unseen television) at 5: 0.6.
  - Carves bind under both texts: 0.85.
- **Fineness.**
  - Each fineness item at 2 under the candidate: 0.75. All four: 0.5.
  - Under the current text, L-V2s and M1b at 1: 0.6 each.
- **Pairs hold under the candidate.** M1 0.75, M2 0.65, M3 0.7, M4 0.85, M5 0.8. All five: 0.35.
- **Under the current text,** M1 and M3 fail (flat at 1): 0.55 each. M2 fails (soft blur already read as 3): 0.4.
- **The candidate passes phase A**, after pass 2: 0.45.

## Cost

222 calls in pass 1, plus up to about 50 in pass 2. About 2–3 weekly points; usage was 88% on 2026-10-05, with a
reset on 2026-10-06.
