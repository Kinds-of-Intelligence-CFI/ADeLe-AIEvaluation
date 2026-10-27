# programbench-pl — pre-registration

Committed and pushed before any label of runs `programbench-pl` and `programbench-pl-long`.

**Question.** Do the PL rubrics track difficulty on ProgramBench, where an agent must rebuild a whole CLI program from
its execute-only binary and documentation, with current-generation outcomes?

## Design

- **Tasks.** The 200 tasks of ProgramBench (facebookresearch/ProgramBench tag `v1.2.5`, `27f0215`; `make_set.py` →
  `tasks.csv`). Data and sources: `../programbench-data/NOTES.md`.
- **Prompt** (Pablo, 2026-10-01): what the agent sees, in full. The mini-SWE-agent system template and the task part
  of the instance template (identical for all tasks), a listing of every workspace file with its size, and the full
  text of each documentation file. No truncation. Clean set: median 9,690 chars, max 308,987.
- **Outcomes.** The ProgramBench/submissions registry (MIT, `c19e570`, 2026-09-30): 25 runs × 200 tasks, all
  mini-SWE-agent, single attempt, 20 models; every run is its own configuration (same model at other efforts kept).
  score = passed / scored tests. A (run, task) cell is solved when score ≥ 0.9 (Pablo; the FrontierSWE threshold).
  Task solve rate = share of the task's attempted runs solved. A run that did not submit the task is missing, not a
  failure (36 cells). Cells with an eval error code (compile_failed 137, copy_executable_failed 21) are failures: the
  submission did not build or left no executable. No attempted cell has zero scored tests, so no cell is missing for a
  failed evaluation. Test branches that errored (5.5% of cells) are absent from the score, as on the leaderboard.
  Sensitivity: thresholds 0.75 and 0.5, and the mean score over attempted runs.
- **Clean set.** Drop never-solved tasks: no run reaches 0.9. That drops 70 and keeps **130**. The same set results
  under the v1.2.5 ignore list (`score_v125`). No external defect list names tasks as broken, so nothing else is
  dropped.
- **Flags** (not exclusions; mapping rules in `make_set.py`, issues read 2026-10-01).
  `docs_damaged`: the LM-written `clean.sh` deleted docs (issue #7; #15 merged into it). The issue names only zk and
  ffmpeg and gives no list, so the rule is: named, or < 2,000 chars of documentation. 70 tasks, 56 kept.
  `knowledge_gated`: the 25-program skip-list (recall-only tests, byte-exact renders, an undiscoverable subcommand) of
  the third-party audit in issue #50 (kimjune01/program-bench-audit at `df0ebcf`; ids only, share-alike). 13 kept.
  `evaluator_issue`: an open evaluator-bug issue names the task and v1.2.5 does not fix it: csview (#56, #59) and
  cmatrix (#37). Both kept. #60 and #64 name no task; #64 is fixed at v1.2.5. Clean set without flags: 65 tasks.
- **Outcome on the clean set.** Solve rate at 0.9: median 0.12, IQR 0.08–0.32, max 0.84. Floor-heavy: 31 tasks are
  solved by one run only (0.04), 55 by at most two. Difficulty (ProgramBench's easy / medium / hard, 9 clean tasks
  unlabelled): 24 / 93 / 4; it correlates with solve rate at 0.9 at ρ = −0.28 on the clean set.
- **Labels.** PLp (text O), PLe, PLs; Opus 5.5 low, v2 prompt; 390 calls on the 130 clean tasks, in two `adele mass`
  runs that differ only in how the judge reads its prompt (Pablo, option A, 2026-10-01). The Claude Code judge's Read
  tool returns at most 2,000 lines and about 25k tokens, and cuts lines over 2,000 chars. So:
  (1) `../programbench-data/wrap_lines.py` splits prompt lines over 1,000 chars into 1,000-char pieces (3 tasks:
  tailspin, dust, tokei; line breaks only); (2) `route.py` builds the judge prompts as the runner does and sends a task
  to the chunked run when a prompt exceeds 50,000 chars or 1,500 lines: 13 tasks (39 calls, run `programbench-pl-long`,
  agents `judge-dispatcher-v2-low-chunked` / `adele-judge-v2-low-chunked`, which read in parts of 200 lines; the
  protocol check, `relay.chunk_lines`, requires every prompt line to come back in some Read result). The other 117
  (351 calls) go to `programbench-pl` with the usual one-Read judge. Specs in `../mass-annotation/specs/`.
- **Analysis** (`analysis/analyse.py`). Spearman (swebench-pl's `rho`) of each rubric with solve rate at 0.9,
  predicted negative. Primary: PLp on the 130 clean tasks. Secondary: PLe and PLs. Sensitivity, same direction:
  solve rate at 0.75 and 0.5, mean score; and all outcomes on the clean set without flagged tasks (65), without
  `docs_damaged` (74) and without `knowledge_gated` (117). Against ProgramBench's difficulty label (easy 1, medium 2,
  hard 3), predicted positive. Only valid answers written by claude-opus-5-5 count. At n = 130, p < 0.05 needs
  |ρ| ≥ 0.17; at n = 65, ≥ 0.24.

## Predictions (sealed)

Priors: PLp tracks solve rate on SWE-bench and tau2, not on Terminal-Bench 4.0 or TB-Science. ProgramBench tasks differ
mostly in the size and intricacy of the program to rebuild, which the documentation shows; the solve rate sits near the
floor, which weakens any correlation.

- PLp against solve rate at 0.9 negative with p < 0.05 on the 130: 0.45.
- PLp against solve rate at 0.9 negative in sign: 0.7.
- PLp against ProgramBench's difficulty label positive with p < 0.05: 0.45.
- PLe against solve rate at 0.9 negative with p < 0.05: 0.3.
- PLs against solve rate at 0.9 negative with p < 0.05: 0.2.
- The 13 chunked tasks have a higher mean PLp than the other 117: 0.7.
- Every chunked cell passes the full-read check within its retry budget: 0.8.
