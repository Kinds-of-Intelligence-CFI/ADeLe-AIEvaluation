# programbench-pl — run log

## 2026-10-01 — set built, not pre-registered yet

Pablo's decisions applied (recorded in `PREREGISTRATION.md`). `../programbench-data/fetch_outcomes.py` now writes the
per-run table as plain `runs.csv` (the `*.gz` ignore rule caught `runs.csv.gz`); the tracked file is the old one
decompressed, byte-identical. `../programbench-data/NOTES.md` still names `runs.csv.gz` (lines on the outcome files and
decision 6) and needs that one-line update.

`make_set.py`: 130 of 200 kept; 70 never reach 0.9 in any run. The clean set is the same under the v1.2.5 rescoring
(`score_v125`; asserted). Flags: `docs_damaged` 70 (56 kept), `knowledge_gated` 25 (13 kept), `evaluator_issue` 2
(both kept: cmatrix, csview); clean without flags 65. Clean-set solve rate at 0.9: median 0.12, IQR 0.08–0.32, max
0.84; 31 tasks are solved by a single run (0.04), 55 by at most two. Missing cells (not attempted): 36; 16 clean tasks
have 21–24 runs.

Analysis tested on synthetic labels in a scratch folder (not kept). `adele mass plan`: 390 cells (130 × 3), ~3.27M
input and ~0.58M output tokens, ~2 weekly subagent points; longest prompt 320,340 chars. Not pinned or run.

**Read feasibility (judge prompts built with `plan_cells`, nothing written).** The subagent judge must read its
prompt in one Read call. Claude Code's Read returns at most 2,000 lines, cuts lines over 2,000 chars and refuses files
over 25,000 tokens. Per cell: median 19,433 chars, 293 lines, ~4.9k tokens (chars/4); max 320,340 chars, 11,224
lines, ~80k tokens. The task text sits between the rubric and the closing answer instruction, so a cut Read loses the
end of the task and the answer format. 10 of 130 clean tasks (30 cells) break a limit:

| task | chars | lines | longest line | ~tokens |
|---|---|---|---|---|
| hairyhenderson__gomplate.05eb3aa | 320,340 | 11,224 | 1,543 | 80k |
| bensadeh__tailspin.6278437 | 309,467 | 1,459 | 2,573 | 77k |
| lfos__calcurse.49180d5 | 242,445 | 6,247 | 1,543 | 61k |
| sayanarijit__xplr.1751065 | 223,035 | 8,501 | 1,543 | 56k |
| junegunn__fzf.b56d614 | 167,088 | 4,322 | 1,543 | 42k |
| rust-lang__mdbook.37273ba | 128,329 | 3,276 | 1,543 | 32k |
| burntsushi__ripgrep.3b7fd44 | 121,214 | 2,785 | 1,543 | 30k |
| direnv__direnv.02040c7 | 91,397 | 2,744 | 1,543 | 23k |
| peco__peco.4e58dad | 91,110 | 2,815 | 1,543 | 23k |
| xampprocky__tokei.505d648 | 27,424 | 404 | 2,164 | 7k |

Over 2,000 lines: 8 tasks; a line over 2,000 chars: 2 (tailspin, tokei); over 25k tokens by chars/4: 7 (direnv and
peco are close to the limit and may cross it with the real tokenizer). Values are the largest of the 3 rubrics (they
differ by ≤ 3,030 chars). Not resolved here: it needs Pablo's choice before pinning.

## 2026-10-01 — read feasibility resolved (Pablo: option A), pre-registered

`NOTES.md` updated to `runs.csv`. Long lines: `../programbench-data/wrap_lines.py` split lines over 1,000 chars into
1,000-char pieces in 3 prompts (tailspin, dust, tokei; checked: only line breaks added); instances re-registered.
Routing (`route.py`, on judge prompts built with `plan_cells`): a task whose prompt exceeds 50,000 chars or 1,500 lines
goes to run `programbench-pl-long` (13 tasks: the 10 above plus age, shellharden, ninja, duc), read in parts of 200
lines by `adele-judge-v2-low-chunked`; the protocol check (`relay.chunk_lines`) requires every prompt line to come back
in a Read result. 117 tasks stay in `programbench-pl` (one Read; max 50,000 chars, 1,500 lines). Largest 200-line
window across the long prompts: ~79k chars, so the judge halves a part whose Read fails. Analysis reads both runs.
Predictions sealed in `PREREGISTRATION.md`.

## 2026-10-01 — labels collected, analysed

`programbench-pl` (351 cells): three rounds of 3 relays plus retries. 348 labelled; zip-password-finder's 3 cells were
answered by Opus 4.8 on both attempts (classifier fallback; no label). `check` OK. `programbench-pl-long` (39 cells):
a one-cell pilot (6 consecutive 200-line Reads, full coverage) then the other 38; the new chunked agents only loaded
into the session after a first launch attempt failed (that relay was released unsent). 38 labelled; age's PLp judge
read lines 1–1,000 of 1,001 on both attempts, rejected by the full-read check (no label). Ran `analysis/analyse.py`;
results and an exploratory prompt-length control in RESULTS.md.
