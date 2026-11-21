# spv-v2 — pre-registration, phase B (real images)

Committed before any label of phase B, with the stimuli, prompt builder and analysis script. Phase A passed
(`RESULTS.md`).

**Why.** Phase A used text descriptions I wrote. Phase B asks whether the candidate's driver tracks how far content
sits from a plain reading when the judge sees actual images. This is round 3 of the original sensory plan (`git show
0195b47:docs/sensory-rubric-plan.md`), whose kill rule I adopt: pooled ρ < 0.6 against severity means the driver is
wrong.

**Stimuli** (`make_stimuli.py`, seed 20261006; 66 PNGs in `stimuli/`, copied and hashed into the run folder).
- **Sweeps.** Two six-character codes, each rendered at 800×240 in bold Arial. Six families, each degrading the clean
  code in five steps (step 0 is clean):
  - size: glyph height 96, 40, 18, 10, 6 px;
  - contrast: ink grey 0, 150, 200, 225, 240 on white;
  - blur: Gaussian radius 0, 1.5, 3, 5, 8;
  - noise: Gaussian σ 0, 90, 160, 240, 330;
  - occlusion: a grey bar over 0, 15, 30, 45, 60% of every glyph's height;
  - overlay: 0, 60, 150, 300, 600 stray ink strokes drawn over the code, with every glyph whole.
- **Views.** For each code, three overlapping crops of the clean label, in shuffled order, with no offsets given.
- **Traps.** Four plain images whose difficulty lies outside SPv:
  - search: one red circle among 300 blue;
  - counting: 37 separated dots;
  - an ARC-like grid with a flip rule;
  - two block shapes, one rotated.

**Arms.**
- `cur`: the current text.
- `cand`: the candidate (after phase A's meter-example swap).
- `cand_key`: the candidate with the code given as a reference answer, sweeps and views only. This arm informs the
  open protocol question: should the SPv judge see the answer?

Two repeats per stimulus and arm. Also P-meter: the new Level 3 bullet, placed under the candidate with that bullet
removed, three repeats. **391 calls.**

**Judge.** Opus 5.5 at effort low, through a new agent `adele-judge-v2-low-image`. It is `adele-judge-v2-low` plus
permission to read the image files the prompt names. It is relayed by `judge-dispatcher-v2-low-image`. Same v2 prompt;
the task text names the images by absolute path. Only answers written by `claude-opus-5-5` count.

## Decision rules (`analysis/analyse_b.py`, candidate arm, no key)

A stimulus's label is the median of its two labels (lower if they differ).
- **B1 (kill rule).** Spearman ρ between step and level, over all labels of the size, contrast, blur and noise
  sweeps, is at least 0.6.
- **B2.** ρ is at least 0.5 within each of those four sweeps.
- **B3.** Occlusion: step 0 at 1 or below; steps 2–4 at 3 or above.
- **B4.** Overlay: step 0 at 1 or below; steps 1–4 at 2 or 3.
- **B5.** Views at 4.
- **B6.** Traps at 1 or below.
- **B7.** P-meter median at 3.

**The candidate passes phase B** if B1–B7 hold.
- If it passes, phase C (criterion validity on ZeroBench and VLMEvalKit subsets) is pre-registered next.
- If B1 fails, the driver is revised before anything else.
- If another rule fails, only the failing clause is examined. One re-run is allowed for stimuli whose two labels
  differ.

**Also reported.**
- The same statistics for `cur`.
- Key vs no-key agreement per stimulus, and where they differ.

## Predictions (sealed)

- **B1** holds under the candidate: 0.7. Under the current text, ρ is lower than under the candidate: 0.8.
- **Medians under the candidate** (step 0→4; ~ marks uncertainty):
  - size 1, 1, 2, 2, 3~;
  - contrast 1, 1, 2, 2, 2~;
  - blur 1, 1, 2~, 3, 3;
  - noise 1, 2, 2, 3~, 3;
  - occlusion 1, 2~, 3, 3, 3;
  - overlay 1, 2, 2, 2, 3~.
- **Per rule:** B2 0.55, B3 0.75, B4 0.6, B5 0.75, B6 0.85, B7 0.8.
- **The current text.**
  - Size ρ below 0.3: 0.6, since small but whole reads as 1.
  - Blur reaches 3 at step 2 or earlier: 0.6, since its blur example is at Level 3.
- **Key arm.** Same median as no-key on at least 80% of stimuli: 0.65. Where they differ, the key arm is higher on
  the hardest steps: 0.6. Without the key, the judge may misread a code it cannot make out, and call it plain.
- **The candidate passes phase B:** 0.4.

## Cost

391 calls with one to three small images each. About 3 weekly points; usage was 89% before this run.
