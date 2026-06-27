# River-crossing — demand-rubric calibration lab

Exploratory research scratch for calibrating ADeLe **v2 agentic demand rubrics** on a
controlled, **solver-backed** testbed. This is a *lab* folder (not part of the package);
the reusable, tested code lives in **`src/adele/rivercross/`**.

## Idea

Parametrized river-crossing puzzles (conflict-graph generalizations of wolf-goat-cabbage
across chain / star / cycle / complete topologies, plus missionaries-cannibals) with an
**exact BFS solver as a value oracle** (true cost-to-go, optimal traces). Rubrics are
annotated by subscription-backed Claude subagents (Haiku / Sonnet / Opus) under a single
**dimension-agnostic prompt**; rubric quality is judged by **cross-model agreement**
(exact %, within-1 %, quadratic-weighted κ) and **correlation with the solver's true
remaining work**. Judge frames are **leak-free** — the solver's numbers are never shown.

## Dimensions analyzed

### PLp — Planning (`method1b/`)

Rubric redefined to score demand by **search size** — depth (horizon), breadth
(actions/step), and the fraction of action-sequences that succeed — with numeric per-level
anchors. On 43 leak-free states (method **1b**, demand-to-go):

- annotations track the solver's remaining search depth at **Spearman 0.83–0.89**;
- chance-corrected agreement **QWK 0.74–0.90**, within-1 = 100%;
- large gain over the prior wording (Haiku Spearman 0.37→0.83);
- headline: **planning demand falls as the task progresses** (demand-to-go ∝ remaining search).

### PLe — Action control & execution (`ple/`)

Calibrated against **captured real agent play** vs a rule-enforcing referee, logging each
step's reasoning and self-corrections (so demand reflects the execution context, not a
static snapshot). The disagreement turned out to hinge on one ambiguous word — *feedback*
(seeing the state / a move's legality vs. an actual reward). Three rubric changes fixed it:

1. `feedback` → `reward` throughout;
2. levels recast as a **mutually-exclusive logical partition** on *horizon × reward-density*
   (explicit and/or — no "in-between");
3. an **operational definition of reward** (the environment's success signal — *not*
   observation, *not* legality).

Result on 49 trajectory states (method **1b**): the two strongest judges **Sonnet and Opus
produced identical labels (QWK 1.00)**; all-3 agreement rose 22% → 65% across the
calibration. Haiku stays the outlier for **capability** reasons (it kept reading
state-visibility as reward), not rubric ambiguity.

## Methods verdict

- **1b (demand-to-go) — the workhorse.** Only method that carries signal for both dimensions; yields the demand-vs-progress curve.
- **1a (whole-task) — dropped.** Coarse and redundant with 1b's start state (the same model labels it differently across the two framings).
- **2 (per-transition) — dropped.** Value-blind: a single action has no horizon, so it collapses to a near-constant label (kept under `ple/labels/2` as the negative result).

## Recurring lessons

1. Define demand **operationally and as a logical partition** so levels are mutually exclusive — vague feature-bundles are what drive disagreement.
2. **Annotating a reasoning dimension's demand is itself a reasoning task** — capable judges converge; the weakest lags on states it can't solve (the "best judge" is dimension-dependent).
3. **Chance-corrected agreement (QWK) + correlation with a solver oracle** beat raw exact-match (which a one-level default can inflate).
4. Keep the annotation prompt **dimension-agnostic** and the frames **leak-free**.

## Directory guide

| path | what |
| --- | --- |
| `method1b/` | **PLp** demand-to-go: `build_prompt.py` (dimension-agnostic prompt builder), `judge_frame_v2.csv` (43 leak-free states), `ground_truth.csv` (solver cost-to-go), `prompt_PLp.txt`, `labels_v10/` (prior-rubric baseline) + `labels_v11/` (revised search-size rubric × Haiku/Sonnet/Opus), `analyze_plp.py` |
| `ple/` | **PLe** via captured trajectories: `build_ple_frames.py`, `frame_PLe_{1b,2}.csv`, `prompt_PLe_{1b,2}.txt`, `labels/1b` (final reward-partition rubric) + `labels/2` (per-transition, degenerate), `analyze_ple.py` |
| `referee.py`, `ref.sh`, `specs.json`, `interactive/` | interactive solver-vs-agent harness (enforces rules, captures per-step reasoning); 6 captured trajectories |
| `puzzles/`, `solutions/` | rendered puzzle prompts and solver solutions |
| `adjudication_PLp.md` (+`_key.json`), `human_worksheet_v2.md` (+`human_key.csv`) | blind human-validation packets |
| `figures/` | `plp_vs_distance.png`, `plp_progress.png`, `ple_1b_progress.png` |

## Reproduce

```bash
source <project>/.venv-adele/bin/activate          # pandas, numpy, scipy, matplotlib
cd <repo root>
python labs/rivercross/method1b/build_prompt.py    # -> prompt_PLp.txt (PLp)
python labs/rivercross/ple/build_ple_frames.py      # -> frame_PLe_{1b,2}.csv
# annotate prompt_*.txt with subscription-backed Claude subagents (no API keys); save CSVs under labels/
python labs/rivercross/ple/analyze_ple.py           # agreement table + figures
```

Scripts locate the repo root by walking up to `src/adele`, so the lab can be moved freely.

## Settled rubrics

The calibrated rubrics live in `src/adele/rubrics/data_v2/Paolo_Pablo/` (`PLp.txt`, `PLe.txt`).
These are **v2-draft (exploratory)** dimensions — not the canonical v1.0 set.
