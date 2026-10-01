# swebench-clean — run log

## 2026-10-01 — set built and run pinned

`make_set.py`: 443 of 500 kept (never solved 29, UTBoost 26, OpenAI-named 3; one overlap). The UTBoost file matched
its pinned sha256, and the solve rates match `swebench-pl/sample.csv`. `make_prompts.py`: all 1,239 existing PL prompts
of the clean set reproduce their hashes; run `clean-swe` has 30 tasks × 3 rubrics = 90 prompts. The analysis was tested
on synthetic labels, which were not kept.
