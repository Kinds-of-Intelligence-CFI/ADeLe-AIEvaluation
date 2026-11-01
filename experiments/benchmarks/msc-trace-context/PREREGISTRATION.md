# MSc with counterpart context from traces — pilot pre-registration

Drafted 2026-10-14 at Pablo's request ("Design the trace-summary pilot: list the tau2 configurations and sizes to
fetch before downloading anything, and pre-register it."). To be committed and pushed before any download or label.
The download needs Pablo's explicit OK (`fetch_list.csv`).

**Question.** Does showing the judge how the simulated customer actually behaves in earlier runs make MSc labels on
tau2 more accurate and more stable?

**Why.** tau2 task texts are the simulated user's script, and they often leave its behaviour open. In msc-l4-note,
the judge and Pablo disagreed most on such tasks. Pablo's idea (2026-10-14): show the judge only the counterpart's
messages from a few traces, as context.

## The hazard and how the design handles it

The simulated user reacts to the agent. An agent that gives in early meets no pushback; one that holds firm meets
more. So the user's turns carry part of the agent's performance. Labels built from them could encode success, and
testing them against solve rate would be circular. The design limits this four ways:
1. **Held-out runs only.** Context comes only from configurations *not* used for the panel's solve rates on that
   domain (`fetch_list.csv`). The solve-rate configurations ("common configurations": airline 7, retail 8) never
   supply context.
2. **Several runs per task, mixed outcomes.** Each task gets up to three runs. When both outcomes exist, at least one
   is a failure.
3. **Counterpart turns only.** The agent's messages, tool calls and tool results are left out.
4. **Same procedure for every item in the arm.** No item gets context because it looks unclear.

**Contamination.** Traces stay in gitignored `data/downloads/tau2-traces/`. Prompts with trace text go to
`~/Developer/ADELE/judge-io/` only. Commit only ids, levels, counts and hashes. Run `contamination_check.py` before
every push.

## What to fetch (`fetch_list.csv`)

17 results files, about **272 MB**, from Sierra's public bucket `sierra-tau-bench-public`. Each file holds every
simulation of one configuration on one domain.

| domain | configurations (all held out) | files | MB |
|---|---|---|---|
| airline | Claude 3.7 Sonnet, GPT-4.1, GPT-4.1 mini, o4-mini, GPT-5, Qwen3-Max-Thinking (preview and final), Nemotron-Orchestrator-8B, Gemini 3 Flash | 9 | 105 |
| retail | the same, without Gemini 3 Flash (common on retail) | 8 | 167 |

Banking is left out. Only two of its 29 configurations are held out, and its files run to 4.5 GB. Where the
filenames say so, the user simulator is GPT-4.1; the scripts record it per file.

## Items

The tau2 items of msc-l4-note that have at least one held-out run on the frozen text. A run counts only if its
task definition rebuilds to the frozen prompt hash (`task_prompt_sha12`, as in the panel).
- **Labelled (10):** H-02, H-04, H-06, H-09, H-13, H-14, H-15 (airline); H-05, H-08, H-10 (retail). Pablo's labels
  of 2026-10-14 were given without context: blind ones in `msc-l4-note/human_labels.csv`, adjudicated ones once he
  confirms them.
- **Fresh2 (10):** H-16 to H-19, H-21, H-23, H-24 (airline); H-20, H-22, H-25 (retail). Pablo labels these blind to
  the judge, **with the same context the judge sees**. They are the informed reference.
- Four items have no held-out run on their text (H-01, H-03, H-07, H-11) and are left out.

## Arms and judge

- **none:** the v2 prompt as in msc-l4-note (current MSc text).
- **context:** the same prompt with one block inserted right after `</task>`:

```
<counterpart_turns>
These are the other party's messages from {k} earlier runs of this task with other agents. The agents' messages are
left out. Use them only to see how the other party behaves. Do not rate any agent's attempt.

Run 1:
User: ...
User: ...

Run 2:
...
</counterpart_turns>
```

The block is dimension-agnostic. It names no rubric and no level. Runs are numbered; the outcome of each run is not
shown. Up to 20 user turns per run. Truncations are recorded.

- **Judge:** `adele-judge-v2-low` (Opus 5.5, effort low), three repeats, relays as before. Lower median.
- **Calls:** 20 items × 2 arms × 3 repeats = **120 calls**.

**Run selection (seeded, `SEED = 20261017`).** Per task, take the held-out simulations with matching text. Keep at
most one per configuration first, then fill. If both outcomes occur, include at least one failure (reward < 1).
Take three, or all if fewer.

## Rules

- **P1 (accuracy, fresh2).** Exact agreement with Pablo's informed labels:
  - context at least 2 items above none: **helps**;
  - within 1: **no clear effect**;
  - context at least 2 below: **hurts**.
- **P2 (stability, all 20).** The share of items whose three repeats agree is at least as high with context as without.

**Decision.** If P1 says "helps" and P2 holds, propose a full tau2 run with context for MSc: all airline and retail
tasks, with a criterion test on the common configurations. Otherwise, drop trace context for MSc.

**Also reported:**
- the 10 labelled items against Pablo's uninformed labels, blind and adjudicated;
- per item, the level with and without context;
- H-13 (worksheet M04, the single-objection case);
- **leak guard:** Spearman of the level change (context − none) against the common-configuration solve rate, across
  the 20 items. |ρ| above 0.5 is flagged as possible outcome leakage, with n = 20 descriptive only;
- run lengths, truncations and user simulators.

## Predictions (sealed)

| | p |
|---|---|
| P1 helps | 0.35 |
| P1 no clear effect | 0.45 |
| P1 hurts | 0.2 |
| P2 holds | 0.55 |
| H-13 at 3 or less with context | 0.5 |
| leak guard flagged | 0.15 |

## Caveats

- **This is a pilot.** Ten informed labels cannot show a small effect. It decides whether a larger run is worth it.
- **Pablo has already seen the judge's labels on the 10 labelled items.** Only fresh2 is blind.
- **Held-out configurations are older models.** The user simulator may behave differently with stronger agents.
- **The informed reference is Pablo reading the same context.** A pass means the judge uses context as he does. It
  does not show that context makes either of them right.

## Cost

120 Opus-low calls, about 5% of a 5-hour window. The download is about 272 MB.
