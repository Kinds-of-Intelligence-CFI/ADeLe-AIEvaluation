# plp-candidate / lab-regression — run log

## 2026-09-28 — pinned run `labreg-r1`

`make_prompts.py` wrote 198 prompts: 99 items under the current text and under C. Checks before the
seal: every prompt reproduces its hash; only the C prompts carry the new sentence; only set P has its
examples stripped; every current-text prompt outside set P equals the production prompt for that
item. The 4-gram check voided three battery items (`B-E03`, `B-P03`, `B-X01`). The analysis script
was tested on synthetic labels, which were not kept. Pre-registration pushed as `86de254`.

## 2026-09-28 — pass 1 judging

Started 15:41 UTC. Six `judge-dispatcher-low` relays of 99 cells, one model each: opus and sonnet
first, haiku after. The judging session ran from `~/Developer/ADELE`.

## 2026-09-28 — pass 1 (`labreg-r1`): complete

Six relays, 15:41–16:28 UTC, plus one retry.
- **Coverage.** 594/594 answered and parsed.
- **Writers.** Every answer was written by its registered model: `claude-haiku-4-5-20251001`,
  `claude-sonnet-5`, `claude-opus-5-5`. Five opus calls had a classifier stop. Four still wrote their
  answer. The fifth (`5dte4`, the Mars-landing example under the current text) wrote nothing and was
  judged once more; opus wrote that answer.
- **Protocol check** over all judge transcripts: exact two-line message, working directory
  `~/Developer/ADELE`, no CLAUDE.md, own files only, effort low for opus and sonnet. Haiku
  transcripts record no effort: the harness applies none to Haiku 4.5. One Write cut off by a
  classifier stop targeted the response folder and wrote nothing.
- **Cost.** Mean final context and time per call: opus 6.5k tokens and 14 s, sonnet 8.3k and 32 s,
  haiku 9.4k and 51 s.
- **Analysis.** One pass-1 loss (`B-M01`, 2 to 3 under C), no move of two levels. Pass 2 needed for
  `B-M01` only.

## 2026-09-28 — pass 2 (`labreg-r2`): complete

`make_prompts.py --replicate B-M01` wrote 2 prompts (the pass-1 texts, new ids). Six direct
`adele-judge-low` calls, 16:29–16:30 UTC. 6/6 parsed, all by the registered models, protocol clean (one opus
classifier stop, answer still written by opus). Both texts got haiku 3, sonnet 2, opus 2. The loss
is not confirmed. Verdict: pass. Weekly usage went from 88 to 93 per cent between 14:37 and 16:31
UTC, other sessions included.

## 2026-09-28 — candidate D pinned (`labreg-d1`)

Pablo asked for C's first clause only. `make_prompts.py --candidate d` wrote 99 prompts from
`PLp_candidate_d.txt`. Each equals its `labreg-r1` current-text prompt plus the one sentence (checked).
The ids do not overlap with earlier runs. The analysis script gained `--candidate d`; re-run for C, it
reproduces `results/regression.json` exactly. It was tested on synthetic D labels, which were not kept.
