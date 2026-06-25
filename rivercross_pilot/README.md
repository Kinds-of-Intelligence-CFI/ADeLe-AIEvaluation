# River-crossing testbed — ADeLe demand-rubric calibration (research pilot)

A controlled, **solver-backed** testbed of parametrized river-crossing puzzles, used
to study and calibrate ADeLe **demand-annotation rubrics** — especially the v2
agentic dimensions (Planning, etc.). This folder is **exploratory research scratch**;
the reusable, tested code lives in the package **`src/adele/rivercross/`**.

## The package (reusable, tested — not here)
- `puzzle.py` — `PuzzleSpec` + generalized wolf-goat-cabbage families (conflict-graph
  topologies, missionaries-cannibals) and a natural-language `render_prompt`.
- `solver.py` — exact backward-BFS **value oracle**: cost-to-go for every state,
  solvability, optimal traces, `transition_value`, `generate_family`.
- `play.py` — parse/replay agent move-sequences (Inspect-free, unit-testable).
- `task.py` — Inspect `@task`/`@scorer` (trajectory-capturing).
- `annotate_methods.py` — builds the 1a/1b/2 judge frames + cost estimates.
- Tests: `tests/test_rivercross*.py`. Everything in *this* folder is experiments run on top.

## The three annotation methods studied
- **1a** — whole-task demand (initial state).
- **1b** — demand-*to-go* at intermediate states. **← the meaningful one.**
- **2** — per-transition demand. Found **value-blind** for this domain (a transition's
  demand doesn't track whether the move helps or hurts), so we focused on 1b.

## Key findings
- **1b carries signal**, method 2 is degenerate here.
- **Cross-model agreement** (Opus/Sonnet/Haiku) is used as a rubric-clarity signal;
  where the rubric's own variable is computable (e.g. PLp ≈ horizon), we validate
  annotations against the **exact solver**.
- Annotating *reasoning* dimensions is itself a reasoning task, so weaker judges err
  on deep structure (traps); the **best judge is dimension-dependent** (Opus right on
  QLl traps, Haiku right on PLp horizon).
- A **strict eliminative prompt** ("rule levels out by their stated conditions") fixes
  over-rating where the rubric has checkable gates — PLp all-3 agreement **49% → 74%**,
  Opus's rubric-violating over-rates → 0.
- **PLp rubric revised** (committed): planning demand defined by **search size** —
  numeric anchors per level for horizon (depth), possible actions/step (breadth), and
  the fraction of action-sequences that succeed; single-agent large searches may now
  reach the upper levels (previously gated on multi-agent).
- **Planning demand falls as the task progresses** (`figures/plp_progress.png`).

## Directory guide
| path | what |
|---|---|
| `method1b/` | the 43-state demand-to-go dataset (`judge_frame_v2.csv`, `ground_truth.csv`) + label sets: `labels_v8` (faithful QLl/MCt), `labels_v9` (feature-first PLp/PLe/MMs), `labels_v10` (strict-gated PLp + Gemini Flash) |
| `method2/` | balanced transition dataset + labels (the value-blind finding) |
| `agreement/` | the original 1a+1b+2 baseline run (QLl/PLp/MMs/MCt × Haiku/Opus) |
| `referee.py`, `ref.sh`, `puzzles/`, `solutions/`, `interactive/` | interactive solver-agent harness (agent plays against a rule-enforcing referee); `haiku_interactive_trajectories.json` |
| `adjudication_PLp.md` (+ `_key.json`) | blinded human-adjudication packet for PLp disagreements |
| `human_worksheet_v2.md` (+ `human_key.csv`) | blind human-annotation worksheet |
| `gemini/` | self-contained prompts to run Gemini via Antigravity or a chat window |
| `figures/` | `plp_vs_distance.png`, `plp_progress.png` |
| `archive/` | **superseded** intermediate runs + abandoned rubric variants — safe to delete |

## Reproduce
```bash
source <project>/.venv-adele/bin/activate      # project venv (pandas, inspect_ai, matplotlib…)
cd src/adele/rivercross/../../..               # repo root
PYTHONPATH=src python -c "from adele.rivercross import generate_mixed_family, solve, generate_instances; \
  print(generate_instances(generate_mixed_family(range(3,6),(1,2,3))).head())"
```
LLM annotation was run with **subscription-backed subagents** (Claude tiers via the
Agent tool) and **Antigravity** (Gemini); no API keys. Each label CSV is
`custom_id,level[,reason]`. The judge prompts are the strict-gated text in `gemini/`.

## Status / open
- PLp strict-gated agreement validated on the Claude tiers; Gemini **Flash** done
  (86% vs the solver's horizon); Gemini **Pro** pending.
- Next: re-test the **revised** PLp (depth/breadth/success-fraction) for agreement vs
  cost; strict-gated **PLe/MMs** runs; decide whether this pilot is committed,
  `.gitignore`d, or moved to a top-level `experiments/`.
