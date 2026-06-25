# Gemini-via-Antigravity annotation task

Open this repo folder in **Google Antigravity** (Gemini Flash) and give the agent
the instruction below. It uses your Gemini subscription — no API key. Output is a
CSV in the same schema as the Haiku labels, so the two are directly comparable.

---

## Instruction to paste into the Antigravity agent

> You are an ADeLe demand-level annotator. ADeLe annotates how much of a given
> cognitive demand a TASK requires (level 0–5), independent of any answer or
> whether it can be solved. Do NOT solve the puzzles — judge the demand.
>
> For each of these four dimensions, read its rubric file (it defines the 0–5
> levels), then rate every puzzle in `rivercross_pilot/method_1a.csv`
> (columns: `custom_id`, `prompt`, `optimal_len`):
>
> - **QLl** — Logical Reasoning → `rubrics/QLl.txt`
> - **MCt** — Critical Thinking → `rubrics/MCt.txt`
> - **PLp** — Planning (v2-draft) → `src/adele/rubrics/data_v2/ours/PLp.txt`
> - **MMs** — Working Memory (v2-draft) → `src/adele/rubrics/data_v2/theirs/MMs.txt`
>
> Annotate each (instance, dimension) using only that dimension's rubric
> descriptors. Then write `rivercross_pilot/gemini_flash_labels.csv` with columns
> exactly: `custom_id,QLl,PLp,MMs,MCt` (one row per instance, integer levels 0–5).
> Use the model **Gemini Flash**.

---

When `gemini_flash_labels.csv` exists, return to Claude Code and run the agreement
step — it ingests this file and compares Gemini ↔ Haiku ↔ human.
