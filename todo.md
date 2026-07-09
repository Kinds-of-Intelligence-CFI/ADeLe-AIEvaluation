# Agentic evaluation — progress & to-do

Tracker for the `adele.agentic` workstream. Methodology in `AGENTIC_METHODOLOGY.md`;
local branch `agentic`; private staging snapshot `PabloAMC/ADeLe-AIEvaluation`.

## Done
- [x] v2 agentic rubric library, v1.0 format, two-source (`rubrics/data_v2/{ours,theirs}/`).
- [x] `MANIFEST.tsv` provenance + active selection; `from_paths` / `load_active_catalog`
      / `verify_manifest`; drift-checked by tests.
- [x] Validation harness — `validation.rubric_agreement` (quadratic-weighted κ,
      Spearman, exact/adjacent, MAE, confusion); `hal.py` ingest + human template;
      `annotate(catalog=…)`; CLI `agentic rubrics|template|validate`; `adele[agentic]`.
- [x] Methodology + Doc↔Sheet reconciliation notes.
- [x] Multimodal/robotics rubrics (`SNp SNk SPa SPv`) deferred — out of the active
      set, kept in the library (`_DEFERRED_MULTIMODAL`).
- [x] Tests green (full suite 143 + 11 agentic); private snapshot pushed.

## Active rubric set (8, text/tool-relevant)
`PLp PLe MSe MSc ECc` (ours) · `MMe MMp MMs` (theirs). Inactive: `SNp SNk SPa SPv`.

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
      `ours/` `.txt` files (the source's duplicate/competing paragraphs were dropped).
- [x] Fix **typos/artefacts** — done in the conversions (still worth fixing upstream
      in the source Doc so regenerations stay clean).
- [x] **L4≈L5 differentiation** (#5) — active rubrics already distinguish the
      L5-only factor; Dexterity examples de-duplicated.
- [x] Preserve the dropped **factor tables + comments** for reference →
      `data_v2/REFERENCE_ours.md` (droppable; not read by code).
- [ ] Fix the `SPv` (Visual) **Level 0 has no examples** gap (`TODO(pablo)` in file).
- [ ] Decide **`ECc` (self-control)**: capability vs propensity — its examples read
      partly behavioural (propensity-like). Methodological call.
- [ ] Tighten **boundary overlap** between `MSe` (environmental), `MSc` (communication)
      and mind-modelling so annotators don't double-count (add contrastive examples).
- [ ] **PLp/PLe level-0 anchor does not transfer across model families** (GPT-5
      cross-check via `labs/rivercross/analyze_cross_family.py`; reports in
      `method1b/plp_cross_family.txt` + `ple/ple_cross_family.txt`, figures
      `figures/*_cross_family.png`; original Claude-panel pipelines untouched):
      on every
      state the Claude panel unanimously calls 0 (dist_to_goal=1 / near-terminal),
      GPT-5 assigns 1 (PLp) or 2 (PLe-1b); within-1 stays 100%/90% and the
      demand-to-go gradient replicates. Add a contrastive level-0 example ("a single
      forced or immediately obvious final move is 0") to both rubrics/prompts.

## Open decisions (team / Pablo)
- [ ] **Code reconciliation** Doc↔Sheet (e.g. our `MSe/MSc/ECc` = Sheet `MSs/MSp/EXb`).
- [ ] **Memory taxonomy**: theirs adds **Semantic** + **Prospective** (no code yet) —
      add codes? fold Prospective into `MMs`? treat Semantic as v1 `KN*`?
- [ ] **Second human annotator** to get a human–human ceiling (current single-annotator
      pass is rubric-debugging, not full validation).
- [ ] **PR path**: push `agentic` to `origin` (CFI) directly when ready — the private
      snapshot omits LFS battery data and has rewritten history (CFI LFS budget exhausted).

## Deferred / later phases (gated)
- [ ] Residual demand-to-go (rung 2) and per-transition demand (rung 3) + the typed
      `task → trajectory → transition` IR (needs HAL trace decryption / Weave).
- [ ] Propensity rubrics (±3 range, ±5 personality) — different prompt/parser.
- [ ] Bayesian measurement layout / learned value model.
- [ ] Re-activate the 4 multimodal rubrics for embodied evaluation.
