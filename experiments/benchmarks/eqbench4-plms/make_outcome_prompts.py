"""Outcome-judge prompts for eqbench4-plms: did the persona openly disclose its hidden material?

EQ-Bench 4's published per-scenario score is a margin against neighbouring models, so scenario difficulty cancels
(../eqbench4-data/NOTES.md). This study judges a new, absolute outcome per (scenario, model) transcript: whether the
persona, in its own spoken lines, acknowledged its hidden core issue (CORE: yes / partly / no) and which of its
"deep down" items it voiced. The judge sees the persona's hidden brief (core issue and deep-down items) and the spoken
dialogue only: no model name, no persona inner monologue, no EQ-Bench scores.

Cells: the 10 models in MODELS × 120 scenarios, plus REPEATS cells judged a second time (a seeded sample, cell id
suffix `~r2`) to measure the judge's reliability. Lines are wrapped at 1,000 chars so one Read returns them whole.

Writes ~/Developer/ADELE/judge-io/eq4-outcome/prompts/<cell>.txt and cells.csv (cell, scenario, model, repeat,
prompt_sha256). Transcripts come from the pinned EQ-bench-site checkout (../eqbench4-data/fetch_outcomes.py).

    python experiments/benchmarks/eqbench4-plms/make_outcome_prompts.py
"""

import hashlib
import json
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / "data/downloads/eqbench4/EQ-bench-site/eqbench4/eqbench4_docs/transcripts"
IO = Path.home() / "Developer/ADELE/judge-io/eq4-outcome"
# Ten models across the Elo range (1385 to 993) and six families; all have 120 transcripts.
MODELS = ["claude-opus-5", "moonshotai_kimi-k3", "openai_gpt-5.5", "openai_gpt-5.6-sol", "claude-sonnet-5",
          "z-ai_glm-5.2", "deepseek_deepseek-v4-pro", "google_gemini-3.1-pro-preview", "google_gemini-3.5-flash",
          "mistralai_mistral-medium-3-5"]
REPEATS, SEED, WIDTH = 60, 0, 1000

INTRO = """You are helping score conversations for a research study.

A person came to talk to a helper. The person was role-played from a hidden brief that the helper never saw. Your job
is to decide what the person openly disclosed, in their own spoken lines, by the end of the conversation.

Rules:
- Count only what the person says. The helper suggesting something does not count, unless the person then clearly
  agrees and says it in their own words.
- Judge the substance, not the exact wording. A hint, a joke, or "maybe" is at most partial.
- Ignore how good or bad the helper was. Only the person's disclosures matter."""


def wrap(text: str) -> str:
    return "\n".join(textwrap.fill(p, WIDTH, break_long_words=True, replace_whitespace=False) if p else ""
                     for p in text.split("\n"))


def prompt(d: dict) -> str:
    core = d["doc"]["core_issue"]
    items = d["doc"]["core_adjacent_attributes"]
    lines = [INTRO, "", "HIDDEN CORE ISSUE", wrap(f"{core['label']}: {core['description'].strip()}"), "",
             "THINGS THE PERSON MAY KNOW DEEP DOWN"]
    lines += [wrap(f"A{k}. {a['label']}: {a['content'].strip()}") for k, a in enumerate(items, 1)]
    lines += ["", "CONVERSATION"]
    for k, t in enumerate(d["turns"], 1):
        who = {"assistant": "Helper", "user": "Person"}[t["role"]]
        lines.append(wrap(f"[{k}] {who}: {t['content'].strip()}"))
    lines += ["", "Answer in exactly this format, one line each, and nothing else:",
              "CORE: yes | partly | no   (did the person openly acknowledge the hidden core issue?)"]
    lines += [f"A{k}: yes | no   (did the person voice this item?)" for k in range(1, len(items) + 1)]
    return "\n".join(lines) + "\n"


def main() -> None:
    (IO / "prompts").mkdir(parents=True, exist_ok=True)
    rows = []
    for m in MODELS:
        files = sorted((SRC / m).glob("[0-9]*.json"), key=lambda f: int(f.stem))
        assert len(files) == 120, (m, len(files))
        for f in files:
            d = json.loads(f.read_text())
            text = prompt(d)
            assert max(len(x) for x in text.split("\n")) <= WIDTH + 10
            rows.append({"cell": f"{d['scenario_id']}@{m}", "scenario": d["scenario_id"], "model": m, "repeat": 1,
                         "text": text})
    df = pd.DataFrame(rows)
    rep = df.sample(REPEATS, random_state=np.random.RandomState(SEED)).assign(repeat=2)
    rep["cell"] = rep["cell"] + "~r2"
    df = pd.concat([df, rep], ignore_index=True)
    assert df["cell"].is_unique
    for r in df.itertuples():
        (IO / "prompts" / f"{r.cell}.txt").write_text(r.text, encoding="utf-8")
    df["prompt_sha256"] = [hashlib.sha256(t.encode()).hexdigest() for t in df["text"]]
    df.drop(columns="text").to_csv(IO / "cells.csv", index=False)
    lens = df["text"].str.len()
    print(f"{len(df)} cells ({len(df) - REPEATS} + {REPEATS} repeats) -> {IO}; chars median {lens.median():.0f}, "
          f"max {lens.max()}; lines max {df['text'].str.count(chr(10)).max()}")


if __name__ == "__main__":
    main()
