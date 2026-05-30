# Agentic evaluation — methodology (v0)

This note records the methodology behind the `adele.agentic` package: what we are
doing now, what we are deliberately deferring, and how the two-source v2 rubric
library is managed. It is a working document, not a published artifact.

## 1. Scope: the simplest rung first

ADeLe v2 extends the demand-level method from static tasks to agent rollouts. A
rollout can be annotated at three temporal resolutions (the "ladder"): the **whole
task**, the **residual** demand-to-go at a state, and a single **transition**.

We start with the bottom rung only:

> **Whole-task demand.** Annotate the *whole task* an agent is given — the public
> benchmark prompt — on the v2 agentic dimensions (0–5), and validate the LLM
> judge against a human annotator.

Two consequences make this genuinely simple:

- **No HAL decryption.** Whole-task demand reads the *task input*, not the
  encrypted rollout trace, so Weave / `cryptography` / a trajectory IR are out of
  scope here.
- **The judge side is unchanged.** `adele.annotation.annotate` already scores any
  rubric folder on the 0–5 scale; the agentic capability rubrics are all 0–5, so
  no annotation code changed (only an optional `catalog=` hook to feed a rubric
  set composed across folders).

Deferred (gated behind their own plans): residual and transition rungs, the typed
`task → trajectory → transition` IR, the Bayesian measurement layout / learned
value model, and the propensity rubrics (the ±3 "range" and ±5 personality scales,
which need a different prompt/parser than the 0–5 capability path).

## 2. Validation design and its main caveat

`adele.agentic.validation.rubric_agreement(judge, human, demands)` reports, per
dimension: quadratic-weighted κ, Spearman ρ, exact and adjacent (±1) agreement,
mean absolute error, and a per-level confusion matrix (to locate ambiguous
anchors).

> **Single-annotator caveat.** With one human annotator (Pablo) there is **no
> human–human agreement ceiling**, against which judge–human agreement is only
> meaningful. So these numbers are a *rubric-debugging* signal — where the judge
> and a careful human diverge, and on which level boundaries — not the full
> validation of §4 of the plan. The function is built to accept a second
> annotator's column later, which restores the ceiling.

**Cost posture.** The judge calls the model once per task × dimension. Estimate
tokens/$ and dry-run on a handful before any real batch; `agentic validate` itself
is API-free (it consumes two label CSVs).

## 3. Two-source rubric library

The v2 rubrics are drafted in **two documents** that do not fully agree:

- **ours** — Google Doc `1xBrJVip8f…` ("Incite propensities and capabilities
  rubrics"): the planning, action-control, environmental, self-control,
  communication and sensory/motor dimensions.
- **theirs** — Google Doc `1tyaEcWq…` ("OECD capabilities rubrics"): a cleaner,
  richer **memory** taxonomy. We use its memory rubrics.

Layout under `src/adele/rubrics/data_v2/` (v1.0 `data/` is untouched):

```
ours/    <code>.txt   # faithful conversions of OURS' 9 non-memory dimensions
theirs/  <code>.txt   # faithful conversions of THEIRS' 3 memory dimensions
MANIFEST.tsv          # provenance + the single "active" selection (sha256-stamped)
```

Each file is v1.0-format (a definition paragraph, then `Level 0..5` with
`Examples:`), with a `# Full Name` header line. The **active set** = ours for the 5
cognitive-agentic non-memory dimensions + theirs for the 3 memory dimensions (8
total), composed by `load_active_catalog()` (no file duplication). The four
sensory/motor rubrics (`SNp/SNk/SPa/SPv`) remain in `ours/` but are **inactive**:
text/tool-based HAL tasks don't exercise vision, audio or dexterity, so annotating
them would yield all-0 columns at extra cost. Re-activate via `_DEFERRED_MULTIMODAL`
in `adele/agentic/__init__.py` for embodied/multimodal work. `MANIFEST.tsv` records,
per active dimension, the source, the Doc heading, a version date and a content hash;
`verify_manifest()` (and a test) flags any drift. Regenerate after editing a
rubric: `python -c "from adele.agentic import build_manifest; build_manifest()"`.

**Faithful-reformat policy.** Level definitions and examples are transcribed from
the source; difficulty-factor notes are folded into the definition paragraph;
Doc-only scaffolding (parameter tables, "does not include" lists, benchmark links,
footnotes) is dropped. No rubric science is invented — gaps are flagged, not
filled (see §5).

## 4. Dimension codes and reconciliation (open team item)

Neither Doc assigns short codes, so the codes below are **ours to assign**. They
follow `AGENTIC_EVALUATION_PLAN.md` §4. The live project Sheet ("Adele v2.0") uses
*different* codes, and is itself internally inconsistent — reconciling Doc ↔ Sheet
is a team decision, not made here.

| Our code | Rubric (full name) | Source | Live Sheet code (approx.) |
|---|---|---|---|
| PLp | Planning | ours | PLp / PL |
| PLe | Action control and execution | ours | PLe |
| MSe | Environmental and situational understanding | ours | **MSs** (Sheet's `MSe` = emotion/empathy) |
| MSc | Communication and social interaction | ours | **MSp** (critical social processes) |
| ECc | Behavioral inhibition and self-control | ours | **EXb** |
| SNp | Dexterity | ours · *deferred* | SNp (proprioception/dexterity) |
| SNk | Kinesthetic processing and proprioception | ours · *deferred* | SNk |
| SPa | Auditory processing | ours · *deferred* | SPa |
| SPv | Visual processing | ours · *deferred* | SPv |
| MMe | Episodic memory | theirs | LMe |
| MMp | Long-term procedural memory | theirs | LMp |
| MMs | Working and short-term memory | theirs | EXe |

## 5. Known gaps / decisions to flag

- **`SPv` (Visual) Level 0 has no examples** in the source Doc — kept as a
  `TODO(pablo)` marker rather than invented.
- **theirs has more memory types** than our 3-way split — **Semantic** and
  **Prospective** memory — with no code yet. Left out this pass; decide whether to
  add codes, fold Prospective into `MMs`, or treat Semantic as overlapping v1 `KN*`.
- **`ours/` holds 9 dims, not 12.** OURS' own memory rubrics share one generic
  template and partly paste THEIRS' text, so creating them would duplicate noise;
  the active memory comes from THEIRS. (A small deviation from the original plan,
  for cleanliness.)
- **First HAL benchmark** for whole-task validation is unsettled — τ-bench
  recommended (planning + social + tool-use, short tasks); confirm input access.

## 6. How to run

```bash
adele agentic rubrics                       # list the active set + provenance
adele agentic template tasks.csv -o human.csv   # blank sheet for the annotator
# ... judge labels: adele.agentic.hal.run_judge(tasks, model=...)  (costs $)
adele agentic validate judge.csv human.csv  # judge-vs-human agreement (API-free)
```
