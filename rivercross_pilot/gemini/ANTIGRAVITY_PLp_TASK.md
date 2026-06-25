# Gemini-via-Antigravity — PLp strict-gated annotation

Open this repo in **Google Antigravity** and run the task below **twice**: once with
**Gemini 3 Pro**, once with **Gemini Flash**. It uses your Gemini subscription — no
API key. Output goes into the same folder/schema as the Claude runs so I can fold
it straight into the agreement analysis.

## Instruction to give the Antigravity agent (verbatim — same prompt the Claude models got)

> You are an ADeLe demand-level annotator for **PLp — Planning** (v2-draft). Score
> only this dimension; rate the demand to COMPLETE the task from the situation shown.
>
> STRICT RUBRIC ADHERENCE — assign by ELIMINATION against the rubric's stated
> conditions, NOT by perceived difficulty:
> 1. First state the task's decisive structural facts: planning horizon (how many
>    crossings/actions to finish), number of subtasks, whether OTHER AGENTS are
>    involved, whether the environment is static & fully-observable vs
>    dynamic/partially-observable, whether the goal is open-ended.
> 2. Then choose the level by checking from the TOP down whether the task meets that
>    level's REQUIRED conditions. A level may be assigned ONLY if ALL its
>    defining/threshold conditions hold. If a level requires a condition the task
>    lacks (e.g. Level 3 requires ~50–100 actions and/or other agents; Levels 4–5
>    require open-ended goals and dynamic/multi-agent environments), you may NOT
>    assign that level OR ANY HIGHER — no matter how intricate the task feels.
> 3. Assign the HIGHEST level whose stated conditions are ALL satisfied. Difficulty
>    cues (tricky ordering, traps, dense constraints) do NOT raise the level beyond
>    what the structural conditions permit.
>
> Read ONLY this rubric: `src/adele/rubrics/data_v2/ours/PLp.txt`
> Items: `rivercross_pilot/method1b/judge_frame_v2.csv` (columns: custom_id, prompt;
> 43 rows), each a partway-through situation to complete.
> Judge each row individually; no counting formula.
> Write a CSV with header `custom_id,level,reason` (reason names the decisive
> condition, e.g. "horizon ~3, single-agent, static -> L1"), one row per input row
> (all 43), to:
>   - **`rivercross_pilot/method1b/labels_v10/gemini-pro_PLp.csv`** when running Gemini 3 Pro
>   - **`rivercross_pilot/method1b/labels_v10/gemini-flash_PLp.csv`** when running Gemini Flash

When both files exist, return to Claude Code and say "Gemini PLp done" — I'll add
both to the 5-model agreement table and check whether the strict-gated prompt holds
across model families.
