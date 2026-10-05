# SPv — audit against the 9 desiderata (2026-10-05)

Reading only; no judge calls. Same format as `PL-desiderata-audit.md`.
Verdicts: ✅ met · ⚠️ met with a named caveat · ❌ not met · ◻️ not assessable by reading.
Text audited: `src/adele/rubrics/data_v2/Paolo_Pablo/SPv.txt` (unchanged since v2-r70, 2026-08-26).
Evidence read: `docs/rubric-provenance/SPv.md`, the sensory plan (`docs/sensory-rubric-plan.md`),
`labs/rubric-qa/sensory-r2`, `r69`, `r70`.

| # | Desideratum | SPv |
|---|---|---|
| 1 | Taxonomy fit | ⚠️ |
| 2 | Disentangles from siblings (measured) | ⚠️ |
| 3 | Single driver | ❌ |
| 4 | Intuitive | ❌ |
| 5 | Usability / annotatability | ❌ |
| 6 | Examples disentangle | ⚠️ |
| 7 | v1 shape and voice | ❌ |
| 8 | Thoughtful | ✅ |
| 9 | Criterion validity | ❌ |

## What the evidence so far shows, and what it does not

- Every SPv result so far is **text-only**. The judges read written descriptions of images ("eggs in a carton").
  They never saw a picture.
- Every item was **designed by the rubric's author**. Placement went from 51% to 96%, and r69 got 19/19 cells exact.
  This shows the text is self-consistent. It does not show the construct is right. The sensory-r2 pre-registration says
  so itself.
- Human evidence is one label: Pablo put ARC-AGI at Level 1 (r70). The ladder items S2–S6 were reviewed by argument
  only.
- The plan's stimulus rounds (2–7: corruption sweeps, designed battery, collision pairs, routing traps, a real
  benchmark) never ran. The annotation pipeline is still text-only (`build_annotation_prompt_v2` takes a string).

## The failures, in the order I would fix them

**D3, D4 · Fineness is carved out, so the main known driver of visual difficulty belongs to no dimension.**
The preamble says content is carried "however fine, faint or small it is". A pattern "present but hard to resolve"
stays at its recovery level, and r69's microprint item (VF2) scores 1. So a Snellen chart scores 1 on every line.
The stated reason is that the scale should be "a property of the image ... rather than of the acuity brought to
reading it". But size, contrast and noise *are* properties of the image. They are not properties of the reader. The
carve swaps a stimulus property for a solver property, and it is not intuitive.
It also leaves a hole. AS owns search, SNs owns transformation, and nothing owns resolving small or faint detail.
Yet fine detail and high resolution are the main failure modes on V\*Bench, HR-Bench, ScreenSpot-Pro and ZeroBench.
Distance from a direct readout, the rubric's own driver, plainly grows as content gets smaller and fainter.
Restoring fineness inside that driver needs no second driver.

**D3 · The levels name kinds of operation, not amounts of one quantity.** Separate (2), reconstruct (3),
combine (4) and invert (5) are categories. Within a level, the amount is explicitly ignored: Level 3 holds "however
badly the image is degraded". So the plan's own oracle, the ImageNet-C severity sweep with its kill rule (ρ < 0.6
against severity), would likely fail. Blur is Level 3 at every severity, and noise is Level 2 until part of the
target is lost. The order between categories is asserted, not shown. A target camouflaged against a background
that resembles it (Level 2) can be much harder than a plate with one corner hidden (Level 3).

**D5 · There is no aggregation rule.** Real items often need several pieces of content at different levels. The
sensory-r2 pre-registration lists an aggregation rule among the fixes, but the current text has none (checked by
grep). Every other v2 rubric scores the hardest required piece; SPv says nothing.

**D5 · Annotation on real images has two unsolved problems.**
1. The judge must see the image. Our subagent judges can read image files, but the runner and prompt builder carry
   text only.
2. The judge is a vision model with the same blind spots as the models it rates. If it cannot see a fine detail, it
   cannot tell whether the content is there, and it may score the item 1 or 0. Without the answer key, the judge often
   cannot even tell which region carries the needed content. Our protocol ("the judge sees what the agent sees, never
   solutions") was set for text tasks, where that problem does not arise.

**D7 · Far outside v1 shape.** Preamble plus does-not-cover is 362 words (231 + 131). v1 preambles run 47–217,
house target near the low end. Level texts run 60–90 words against v1's ~34. Sentences in the preamble average 26
words and stay abstract ("yield it only by reasoning back through how the image was formed"). The same compression
pass PLe and PLs needed.

**D9 · No criterion evidence of any kind.** No real image has been annotated.

## The caveats behind the ⚠️s

- **D1 · Taxonomy.** The ladder maps onto CHC visual processing (Gv) in part: separation is flexibility of closure
  (disembedding), reconstruction is closure. Combining views and inverting image formation come from computer
  vision, not psychometrics. Spatial relations and visualization go to SNs, scanning to AS, visual memory to MM.
  That routing is sound. But the ordering of the levels has no taxonomic source.
- **D2 · Siblings, measured only on designed text items.** The AS carve (search) and the meaning carve bind on
  designed items. There is one human anchor (ARC = 1). Two leaks are built into the levels themselves:
  - Level 3 completes content "from the regularities of the domain", which is knowledge (KN) or language (CL). A
    water-damaged page is read by knowing the language.
  - Level 5's examples lean on spatial and physical reasoning (SNs): building height from a shadow needs sun angle and
    geometry, and a room layout from a curved reflection is a mental transformation.
- **D6 · Examples.** Placement is 96% clean, but there are two problems:
  - **One example contradicts the doctrine.** "What was written on a missing page from the impressions on the sheet
    beneath" is at Level 5, but the impressions are physically present as relief. By the preamble's own rule they are
    carried, so the example is fine-but-present content, which is Level 1 or 2 now, and Level 2 or 3 with fineness
    restored.
  - **The examples miss the domain of the benchmarks.** The 15 image examples are photographs of physical scenes or
    paper, plus one video subtitle. None is a screenshot, chart, diagram or UI, which is what most visual benchmarks
    are made of (CharXiv, ScreenSpot-Pro, OSWorld, MathVista, ZeroBench). José raised the same gap for PLs.
- **D8 · Thoughtful.** The carried-by-the-signal doctrine, the registered-layers rule and the search carve are careful
  and well argued. The faults above are construct choices, not carelessness.

## Sealed predictions for the current text (before any image is annotated)

1. On ZeroBench (100 items), ≥70% of items land at Levels 1–2, because fineness, counting and search are carved out.
   Confidence ~70%.
2. SPv against ZeroBench solve rate: ρ weaker than −0.2. Confidence ~70%.
3. On an ImageNet-C style sweep, assigned level is flat across severity for blur and contrast (ρ < 0.3 within
   family). Confidence ~75%.

## Proposed path

1. **Polish (candidate text, not adopted until regressions pass).**
   - Restore fineness inside the existing driver: small, faint or low-contrast content counts as further from a direct
     readout.
   - Add an aggregation rule: score the hardest piece the task needs.
   - Re-anchor Level 5 on inversions that are perceptual, not geometric.
   - Fix or move the impressions example.
   - Add screen, chart and document examples at Levels 1–3.
   - Compress to v1 shape.
2. **Lab regression (text-only).** sensory-r2 placement plus the r69 ladder and carves, for the current text and the
   candidate.
3. **Stimulus rounds with real images** (the plan's rounds 3–6):
   - severity sweeps (blur, noise, contrast and size, occlusion fraction) on fixed content;
   - k-view items for the 3/4 boundary;
   - routing traps (ARC, crowded scene, mental rotation).
4. **Criterion (D9).**
   - ZeroBench: 67 models × 100 items.
   - VLMEvalKit records: VCR easy and hard, Q-Bench, BLINK subsets. Per-item results, but spring-2025 models only.
   - Pre-register before labelling.
5. **Human anchor.** Pablo labels ~15 real images blind.

SPa shares the ladder. Any change to SPv's driver implies the same change to SPa later. SPa is untouched for now.
