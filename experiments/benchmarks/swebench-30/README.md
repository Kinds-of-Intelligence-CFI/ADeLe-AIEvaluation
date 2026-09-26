# swebench-30 — first real-benchmark annotation run

Owner: Pablo. Status: pre-registered; run `swev30-r3` dry run pending (`swev30-r1` and
`swev30-r2` were earlier dry runs, superseded by deviations 1 and 2 in `PREREGISTRATION.md`).

30 SWE-bench Verified tasks, stratified by leaderboard solve rate, plus the 14 pilot tasks as
test–retest anchors. They are annotated on 25 ADeLe rubrics (18 v1 and the active v2 set, MSm
once) by Claude Sonnet and Claude Opus, and joined to the per-task results of the 135
SWE-bench leaderboard entries. The aim is annotation quality and a rehearsal of the pipeline
before scaling, not criterion validity: see `PREREGISTRATION.md`.

| step | command | output |
|---|---|---|
| inputs | `adele instances prepare -b swebench`; `adele results fetch-swebench <experiments> --instance-ids data/instances/instances_swe-bench-verified.parquet` | `data/` (gitignored) |
| sample | `python experiments/benchmarks/swebench-30/build_sample.py` | `sample.csv` |
| prompts | `python experiments/benchmarks/swebench-30/make_prompts.py` | prompts in `data/annotations/swev30-r3/`; `labels/swev30-r3/run.json`, `prompts_index.csv` |
| judging | one `adele-judge` subagent per prompt (copy `adele-judge.md` to `.claude/agents/`), message template in `run.json` | `data/annotations/swev30-r3/responses/<judge>/` |
| labels | `python experiments/benchmarks/swebench-30/collect.py` | `labels/swev30-r3/labels_long.csv`; reasons in `data/.../raw.jsonl` |

Committed files carry ids, levels and hashes only. Task text and the judges' reasoning quote
the benchmark, so they stay in the gitignored `data/` tree.
