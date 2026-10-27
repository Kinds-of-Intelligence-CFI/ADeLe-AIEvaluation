# swebench-pl — the planning rubrics on all solvable SWE-bench Verified tasks

Owner: Pablo. Status: step 1 passed (`RUNLOG.md`); step 2 labels complete (1,194/1,194 parsed);
predictions locked 2026-09-27; pre-registered analysis done (`results/analysis.json`), except
the test-validity robustness check, which waits for the audit. Opus-low labels on all 435
solvable tasks (step 1c, exploratory) are in `labels/swepl-r1-low/` and `labels/swepl-gate-low/`.

PLp, PLe and PLs on the 435 SWE-bench Verified tasks with a leaderboard solve rate of at least
0.05, judged by Opus at medium effort, to test whether planning demand tracks difficulty. Step 1
checks that medium effort reproduces the max-effort labels of `swebench-30` well enough; step 2
runs only if it does. See `PREREGISTRATION.md`.

| step | command | output |
|---|---|---|
| prompts | `python experiments/benchmarks/swebench-pl/make_prompts.py` | `sample.csv`; prompts in `data/annotations/<run>/` and `../../judge-io/<run>/`; `labels/<run>/run.json`, `prompts_index.csv` |
| judging | `judge-dispatcher-medium` relays sending each cell to `adele-judge-medium` (copy both `.md` files to `.claude/agents/` two levels above the repo), message template in `run.json` | `../../judge-io/<run>/responses/opus-medium/` |
| labels | `python experiments/benchmarks/swebench-pl/collect.py --run <run>` | `labels/<run>/labels_long.csv`; reasons in `data/.../raw.jsonl` |
| gate | `python experiments/benchmarks/swebench-pl/gate.py` (after `swebench-30/collect.py --run swev30-r4`) | `results/gate.json` |

Committed files carry ids, levels and hashes only; task text and the judges' reasoning stay in
the gitignored `data/` tree.
