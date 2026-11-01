# pls-relabel — run log

## 2026-10-04 — setup

Specs written from `ms-benchmarks.toml` and `ms-benchmarks-long.toml` with the rubric and names changed. `adele mass
plan`: 1,016 and 13 cells, about 5 weekly points. `analysis/analyse.py` was tested on synthetic new labels (not kept);
on the released labels it reproduces the old Spearman values in `SUMMARY.md` (SWE-bench −0.18, ProgramBench −0.14,
DeepSWE 0.00, FrontierSWE −0.01, TB 4.0 +0.05, TB-Science +0.09). Not pinned yet: pinning records the agent and
rubric hashes at launch.

## 2026-10-04 — runs `pls-relabel` and `pls-relabel-long`: complete

Launched before the weekly reset at Pablo's request (deviation 1). Pinned both specs. Six rounds of at most four
`judge-dispatcher-v2-low` relays (21 relays of up to 50 cells), plus one `judge-dispatcher-v2-low-chunked` relay
for the 13 long prompts, about 5 minutes per round. `collect` and `check` after every round: all protocol checks
passed. Two cells hit safety-classifier stops on every attempt, with the answer finished by Opus 4.8 or a malformed
call (rejected as `fallback_writer` and `protocol`); they have no label. 1,027 of 1,029 cells labelled. Weekly usage
went from 55 to 59 per cent.

Afterwards a subagent switched the seven releases to these labels (`release.py` lets a run contribute only some
rubrics). Checks: PLp, PLe, MSm and MSc rows byte-identical to before; every PLs row matches the run. Then
`analysis/analyse.py` was pinned to the old releases at `cd608bf`; its output is unchanged.
