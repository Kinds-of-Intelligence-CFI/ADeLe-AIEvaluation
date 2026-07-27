# Agentic evaluation — progress & to-do

Tracker for the `adele.agentic` workstream. Methodology in `AGENTIC_METHODOLOGY.md`;
local branch `agentic`; `origin` is the CFI repo.

## Done
- [x] v2 agentic rubric library, v1.0 format, two-source
      (`rubrics/data_v2/{Paolo_Pablo,Marko}/`).
- [x] `MANIFEST.tsv` provenance + active selection; `from_paths` / `load_active_catalog`
      / `verify_manifest`; drift-checked by tests.
- [x] Validation harness — `validation.rubric_agreement` (quadratic-weighted κ,
      Spearman, exact/adjacent, MAE, confusion); `hal.py` ingest + human template;
      `annotate(catalog=…)`; CLI `agentic rubrics|template|validate`; `adele[agentic]`.
- [x] Methodology + Doc↔Sheet reconciliation notes.
- [x] Multimodal/robotics rubrics (`SNp SNk SPa SPv`) deferred — out of the active
      set, kept in the library (`_DEFERRED_MULTIMODAL`).
- [x] Tests green (full suite 143 + 11 agentic).
- [x] **Agentic rubric re-key** — `PLp`/`PLe`/`PLs`/`MSc` each re-keyed on a single
      driver with explicit routing; `MSe`→`PLs` re-filed; `ECc` removed. ~700 judge
      annotations over 16 rounds on branch `rubrics/v2-improved`; labels in
      `labs/rubric-qa/`, write-up in `docs/agentic-rubric-redesign.md`.

## Active rubric set (7, text/tool-relevant)
`PLp PLe PLs MSc` (Paolo_Pablo) · `MMe MMp MMs` (Marko). Inactive: `SNp SNk SPa SPv`.
`MSe` was renamed `PLs` and re-filed to the PL family; `ECc` was removed (propensity).

## Next steps
- [x] **Pilot benchmark set + sample** — 4 benchmarks (SWE-bench Verified,
      AssistantBench, USACO, τ-bench), 5 tasks each → `pilot/tasks.csv` +
      `pilot/human_template.csv`. Reproducible: `adele agentic pilot --seed 0`
      (`benchmarks.py`; downloads task inputs only, no rollouts/LLM calls).
- [ ] **Pablo annotates** `pilot/human_template.csv` (fill the 8 demand columns 0–5)
      → save as e.g. `pilot/human_labels.csv`.
- [ ] **Dry-run + cost-gate** the judge: `hal.run_judge(tasks, model=…)` on ~2–3
      tasks first (token/$ estimate); then the 20.
- [ ] **First agreement numbers**: `adele agentic validate judge.csv human_labels.csv`;
      read the per-level confusion to find ambiguous anchors.
- [ ] **Revise rubrics** where agreement is weak; re-annotate.
- [ ] Later: stratified/high-level oversample (random under-samples levels 4–5);
      add GAIA/AppWorld; second annotator for a human–human ceiling.

## Rubric quality backlog (see review)
- [x] Keep **one polished definition per level**, ADeLe v1.0 style — done in the
      `Paolo_Pablo/` `.txt` files (the source's duplicate/competing paragraphs were dropped).
- [x] Fix **typos/artefacts** — done in the conversions (still worth fixing upstream
      in the source Doc so regenerations stay clean).
- [x] **L4≈L5 differentiation** (#5) — active rubrics already distinguish the
      L5-only factor; Dexterity examples de-duplicated.
- [x] Preserve the dropped **factor tables + comments** for reference →
      `data_v2/REFERENCE_Paolo_Pablo.md` (droppable; not read by code).
- [ ] Fix the `SPv` (Visual) **Level 0 has no examples** gap (`TODO(pablo)` in file).
- [x] Example-placement test over the four agentic rubrics (round 25): 75% -> 92%
      of examples recovered to their own level by 3/3 judges.
- [x] Decide **`ECc` (self-control)**: resolved — removed from the demand set as a
      propensity, not an ability. See `docs/agentic-rubric-redesign.md` §5.
- [x] Tighten **boundary overlap** between `PLs` (situational), `MSc` (communication)
      and mind-modelling — done via single-driver re-keys, explicit routing sentences and
      contrastive anchors; validated over 16 rounds. See `docs/agentic-rubric-redesign.md`.

## Open decisions (team / Pablo)
- [ ] **Code reconciliation** Doc↔Sheet (historically our `MSe/MSc/ECc` = Sheet
      `MSs/MSp/EXb`; `MSe` is now `PLs` and `ECc` is withdrawn, so the mapping needs
      restating before it is used).
- [ ] **Memory taxonomy**: Marko's set adds **Semantic** + **Prospective** (no code yet) —
      add codes? fold Prospective into `MMs`? treat Semantic as v1 `KN*`? A proposed
      decomposition and a minimal-pair test for Prospective are in
      `docs/agentic-open-questions.md` §2b (prior: retention → `MMe`, cue-noticing → `PLe`,
      so probably no new code needed).
- [ ] **Second human annotator** to get a human–human ceiling (current single-annotator
      pass is rubric-debugging, not full validation).
- [ ] **PR path**: push to `origin` (CFI) directly when ready. Note the CFI LFS budget
      is exhausted, so avoid re-pushing battery data.

## Deferred / later phases (gated)
- [ ] Residual demand-to-go (rung 2) and per-transition demand (rung 3) + the typed
      `task → trajectory → transition` IR (needs HAL trace decryption / Weave).
- [ ] Propensity rubrics (±3 range, ±5 personality) — different prompt/parser.
- [ ] Bayesian measurement layout / learned value model.
- [ ] Re-activate the 4 multimodal rubrics for embodied evaluation.
      `SPv`/`SPa` planned on branch `multimodal` — see
      `docs/multimodal-rubric-plan.md`. `SNk`/`SNp` stay deferred: no current
      benchmark exercises them, so they cannot be validated even in principle.
