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

## 2026-09-28 — candidate D, pass 1 (`labreg-d1`) and pass 2 (`labreg-d2`): complete

Pass 1: three relays of 99 cells (one per model), 18:09–18:47 UTC. 297/297 answered and parsed, all
by the registered models. Five opus calls had a classifier stop; each still wrote its answer. The
protocol check over the 297 transcripts is clean (haiku again without effort). Pass 1 found two
losses and one two-level move, so pass 2 re-ran `F-MSc-L3-4`, `F-PLs-L4-3` and `M-A1` under both texts:
18 calls (18:48–18:51 UTC), 6 per model, all parsed, protocol clean. One relay launch failed on a transient auto-mode
check and was launched again; no cell was sent twice. Verdict for D: fail (the two-level move on
`F-MSc-L3-4` repeated; neither loss did).

## 2026-09-30 — candidate S pinned (`labreg-s1`)

`make_prompts_s.py` wrote 102 prompts: S under the v2 prompt, set P with examples stripped, the three
new S examples added to set P (`items_s.csv`). The 4-gram check against S's bullets voids the same
three battery items and no others. Every pass-2 S prompt reproduces its pass-1 prompt (tested, not
kept). `analysis/analyse_s.py` was tested on synthetic labels, which were not kept. That test showed
that 83 of 101 checks hold under the reference (labreg-r1, opus-low, current text), from existing labels.
`writers.py` now maps repeat judge names (`opus-low-r1`) to their model.

## 2026-09-30/10-01 — candidate S, pass 1 (`labreg-s1`) and pass 2 (`labreg-s2`): complete

Pass 1: three `judge-dispatcher-v2-low` relays of 102 cells (one per repeat), about 11 minutes each,
run concurrently. 306/306 answered and parsed, all written by `claude-opus-5-5`, with no classifier
stop. Protocol check over 306 transcripts: exact two-line message, working directory `~/Developer/ADELE`,
effort low, no CLAUDE.md attached (the only mention is boilerplate in the harness system prompt),
Read then Write only. Exception: one judge (`kmy2z`, repeat 2) wrote its own answer twice. One pass-1
loss (`P-L1-3`), no move of two levels. Pass 2: six direct `adele-judge-v2-low` calls (both texts × 3
repeats), all parsed, all Opus 5.5. The loss repeats. Verdict: fail.

## 2026-10-01 — candidate O, pass 1 (`labreg-o1`) and pass 2 (`labreg-o2`): complete

Pass 1: three relays of 108 cells. 324/324 answered and parsed, all Opus 5.5, no classifier stop. One loss (`P-L1-3`),
no two-level move, no format-pair split. Pass 2: six direct calls; O 2, 2, 2, current text 2, 1, 1. The loss is
confirmed. Verdict: fail. Write-up in `../../plp-b2/RESULTS.md`, amendment 5.

## 2026-10-01 — O′ screen pinned (`labreg-o2s`)

`screen_o2.py pin` wrote 24 prompts: 23 set-P items under O′ (checked to be O minus the one sentence, examples
stripped), plus the covering letter's `labreg-o1` O prompt (hash checked). The analysis was tested on synthetic
labels, which were not kept.
