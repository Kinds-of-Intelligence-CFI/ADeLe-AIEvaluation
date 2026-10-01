# swebench-clean — run log

## 2026-10-01 — set built and run pinned

`make_set.py`: 443 of 500 kept (never solved 29, UTBoost 26, OpenAI-named 3; one overlap). The UTBoost file matched
its pinned sha256, and the solve rates match `swebench-pl/sample.csv`. `make_prompts.py`: all 1,239 existing PL prompts
of the clean set reproduce their hashes; run `clean-swe` has 30 tasks × 3 rubrics = 90 prompts. The analysis was tested
on synthetic labels, which were not kept.

## 2026-10-01 — run `clean-swe` complete

One `judge-dispatcher-v2-low` relay of 90 cells. 90/90 answered and parsed, all by `claude-opus-5-5`, no classifier stop;
protocol check over 90 transcripts clean (exact message, working directory, Read then Write, no CLAUDE.md). Analysis run
with `uv run --extra annotate --with scipy` (uv.lock deleted). All six predictions held.
