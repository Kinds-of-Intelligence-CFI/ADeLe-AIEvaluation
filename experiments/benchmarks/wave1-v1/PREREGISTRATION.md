# wave1-v1 — the v1 rubrics on the wave-1 tasks, on Claude Code subagents (pre-registration, 2026-10-27)

**What.** Wave 1 of the bulk annotation (`../mass-annotation/BENCHMARKS.md`): the 17 judged v1 rubrics (AS AT CEc CEe CL
KNa KNc KNf KNn KNs MCr MCt MCu QLl QLq SNs VO) on the 1,466 wave-1 tasks (`../mass-annotation/subsets/wave1.csv`: the
tasks of label set `current`, plus rivercross-search). Also the five released rubrics (PLp PLe PLs MSm MSc) on
rivercross-search, the one wave-1 set without them (`bulk-w1-rivercross-plms`). v1 MSm is left out (v2 MSm replaces
it); UG is computed. The memory rubrics (`bulk-w1-memory`) wait for the team.

**Why.** Full demand profiles on the tasks with per-task results, so the PLAN.md §4 analyses can run, above all
incremental prediction (desideratum 9): v1 → v1 + PL → v1 + PL + MS.

**Why subagents.** The plan was the Batch API. Pablo prefers to use subscription credit first. The judge is the same.

## Input (docs/judge-input.md)

| run | benchmarks | tasks | input |
|---|---|---|---|
| `w1v1-swe` | SWE-bench Verified | 443 | `data/instances-goal` (task + goal) |
| `w1v1-tau2` | tau2 airline, retail, banking_knowledge | 229 | `data/instances-tau2-goal` (full task + goal, no expected actions) |
| `w1v1-tau2-long` | same | 13 | same, chunked judge |
| `w1v1-code` | DeepSWE, FrontierSWE, ProgramBench, TB 4.0, TB-Science | 330 | `data/instances-goal` |
| `w1v1-code-long` | ProgramBench | 13 | same, chunked judge |
| `w1v1-other` | CooperBench, EQ-Bench 4, Game Arena, rivercross-search | 438 | `data/instances`, as their released labels |
| `bulk-w1-rivercross-plms` | rivercross-search | 54 | `data/instances` |

**Routing.** `route.py` builds all 17 prompts of every task. A task goes, with all 17 rubrics, to the chunked judge
when any prompt exceeds 50,000 chars or 1,500 lines. `prompt_sizes.csv` has the sizes. One task has a line over 2,000
chars: `gamearena/go@player`, 2,701 chars (see minor call 4).

## Judge

Opus 5.5, effort low, bare-digit prompt (`v2-noreason`), one repeat, rubric text as the catalog serves it
(canonical `src/adele/rubrics/data_v1`). Subagents `judge-dispatcher-v2-low` / `adele-judge-v2-low`, chunked runs
`-chunked` with 200-line reads. The mass runner's retries (one for a fallback writer, one for an unparsed answer).

## Cost (`adele mass plan`)

25,192 calls, about 102M input tokens, about 125 weekly points: more than one week of the Max plan. Runs go in this
order: `w1v1-swe` (38), `w1v1-tau2` (19), `w1v1-tau2-long` (1), `w1v1-code` (28), `w1v1-code-long` (1), `w1v1-other`
(37), `bulk-w1-rivercross-plms` (1). Rounds stop at 95% weekly (Pablo, 2026-10-27: "I think you could go up to 95%, do
not be shy") or 90% of the 5-hour window, and resume after the reset.
At the Batch API this would be about $170.

## Minor calls (Pablo can veto)

1. Canonical v1 rubric texts, not the unadopted `v1-upgrade` candidate. Pablo ruled this on 2026-10-27: "I think we
   want the canonical, Jose Orallo preferred keeping those dimensions identical to what they were."
2. Gates: `gate-dryrun` is replaced by the first relay (parsing, sizes, refusals). `gate-api-bridge` is moot (no API).
   `gate-v1-bridge` still needs the HF token; until it runs, these v1 labels are not claimed comparable to the
   published GPT-4o labels.
3. CooperBench, EQ-Bench 4, Game Arena and rivercross keep `data/instances`: the input of their released labels.
   judge-input.md names no goal build for them.
4. `go@player`: the cut part of its long line is a JSON copy of the board. The ASCII board earlier on the same line is
   fully visible. Kept as is, the same input as its released labels.
5. ProgramBench `agourlay__zip-password-finder.704700d` is in the goal-visible set but not in label set `current`, so not
   in wave 1.
6. The noise floor (3% re-judge) and the anchor set (PLAN.md §3.4) are not part of these runs. They come after.
7. No change to label set `current` or to releases without Pablo's OK.
