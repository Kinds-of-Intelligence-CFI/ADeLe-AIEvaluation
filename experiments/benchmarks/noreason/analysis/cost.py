"""Cost per label of each noreason arm (secondary analysis, amendment 3). Writes results/cost.csv and prints a table.

Two measures:
1. Harness cost: what one Claude Code subagent judge call processed. Input-side tokens (uncached, cache writes,
   cache reads) come from the `usage` that the judge transcripts log at the start of each assistant message. Those
   are reliable. The logged `output_tokens` are a mid-stream snapshot and undercount: a 1,090-character answer is
   logged as 47 tokens. So output is estimated from what the judge wrote (text, tool inputs, thinking), at 3.6
   characters per token. Priced at the judge's rates per million tokens: Opus 5.5 $4 input, $5 cache write, $0.20
   cache read, $20 output; Sonnet 5.5 $2, $2.50, $0.20, $10 (amendment 4). Wall-clock is the span from the transcript's first to its last timestamp. Every judge call
   counts, re-judged and rejected ones included; cost per label = total cost / labels collected.
2. Plain API counterfactual: one Messages API call with the prompt file as the only input and the answer file as the
   output (3.6 characters per token), at standard and at batch (50%) prices, with no agent harness and no caching.

Arms: R' = noreason-ref (+ -ms), NR = the noreason-* runs (Opus); SNR = noreason-s-*, SR = noreason-sr-* (Sonnet).
Matched comparison: the 150 + 40 tasks of the reference subset, where every arm judged the same rubric and task.

    python experiments/benchmarks/noreason/analysis/cost.py --transcripts <session>/subagents
"""

import argparse
import glob
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
RUNS = HERE.parent / "mass-annotation/runs"
IO = Path.home() / "Developer/ADELE/judge-io"
CPT = 3.6
PRICES = {"opus": {"in": 4e-6, "cw": 5e-6, "cr": 0.2e-6, "out": 20e-6},
          "sonnet": {"in": 2e-6, "cw": 2.5e-6, "cr": 0.2e-6, "out": 10e-6}}
SETS = ["ms", "pl", "ms-rest", "long", "eqbench4", "cooperbench", "gamearena"]
ARMS = {"R'": ["noreason-ref", "noreason-ref-ms"],
        "NR": [f"noreason-{s}" for s in SETS],
        "SNR": [f"noreason-s-{s}" for s in SETS],
        "SR": [f"noreason-sr-{s}" for s in SETS]}
MODEL = {"R'": "opus", "NR": "opus", "SNR": "sonnet", "SR": "sonnet"}
RUN_MODEL = {r: MODEL[a] for a, runs in ARMS.items() for r in runs}
REPIN_MS = "2026-10-06T18:11:37"  # noreason-ms transcripts before the re-pin belong to the aborted sentence format


def judge_calls(transcripts: Path) -> pd.DataFrame:
    rows = []
    pat = re.compile(r"judge-io/(noreason-[\w-]+?)/prompts/(v2\w+-[0-9a-f]+)\.txt")
    for f in glob.glob(str(transcripts / "agent-*.jsonl")):
        lines = open(f).readlines()
        if not lines or not (m := pat.search(lines[0])):
            continue
        run, cell = m.groups()
        first = json.loads(lines[0])
        if run == "noreason-ms" and first.get("timestamp", "") < REPIN_MS:
            continue
        usage, chars, stamps = {}, 0, []
        for line in lines:
            d = json.loads(line)
            stamps.append(d.get("timestamp", ""))
            msg = d.get("message", {})
            if msg.get("role") != "assistant":
                continue
            usage.setdefault(msg.get("id"), msg.get("usage") or {})
            for b in msg.get("content") or []:
                chars += len(b.get("text", "")) + len(b.get("thinking", "")) + (
                    len(json.dumps(b.get("input", {}))) if b.get("type") == "tool_use" else 0)
        u = pd.DataFrame(list(usage.values())).fillna(0)
        s = [t for t in stamps if t]
        rows.append({"run": run, "cell_id": cell,
                     "in": float(u.get("input_tokens", pd.Series([0])).sum()),
                     "cw": float(u.get("cache_creation_input_tokens", pd.Series([0])).sum()),
                     "cr": float(u.get("cache_read_input_tokens", pd.Series([0])).sum()),
                     "out": chars / CPT,
                     "seconds": (pd.Timestamp(max(s)) - pd.Timestamp(min(s))).total_seconds() if s else np.nan})
    df = pd.DataFrame(rows)
    df = df[df.run.isin(RUN_MODEL)].copy()
    price = df.run.map(RUN_MODEL).map(PRICES)
    df["usd"] = sum(df[k] * price.map(lambda p: p[k]) for k in ("in", "cw", "cr", "out"))
    df["usd_out"] = df["out"] * price.map(lambda p: p["out"])
    return df


def plain_api(run: str) -> pd.DataFrame:
    rows = []
    for p in glob.glob(str(IO / run / "prompts/*.txt")):
        cell = Path(p).stem
        answers = glob.glob(str(IO / run / f"responses/{RUN_MODEL[run]}-low*/{cell}.txt"))
        if answers:
            rows.append({"run": run, "cell_id": cell, "prompt_tok": len(open(p).read()) / CPT,
                         "answer_tok": len(open(answers[0]).read()) / CPT})
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcripts", required=True, type=Path)
    calls = judge_calls(ap.parse_args().transcripts)
    labels = {r: len(pd.read_csv(RUNS / r / "labels.csv").query("valid")) for a in ARMS.values() for r in a
              if (RUNS / r / "labels.csv").exists()}
    out = []
    for arm, runs in ARMS.items():
        c = calls[calls.run.isin(runs)]
        n_lab = sum(labels.get(r, 0) for r in runs)
        api = pd.concat([plain_api(r) for r in runs])
        if api.empty or c.empty:
            continue
        price = PRICES[MODEL[arm]]
        api_usd = api.prompt_tok * price["in"] + api.answer_tok * price["out"]
        out.append({"arm": arm, "judge_calls": len(c), "labels": n_lab,
                    "harness_usd_per_label": c.usd.sum() / max(n_lab, 1),
                    "harness_output_share": c.usd_out.sum() / c.usd.sum(),
                    "median_seconds_per_call": c.seconds.median(),
                    "api_usd_per_label": api_usd.mean(), "api_batch_usd_per_label": api_usd.mean() / 2,
                    "median_answer_tokens": api.answer_tok.median(), "median_prompt_tokens": api.prompt_tok.median()})
    # Matched cells: the same (benchmark, task, rubric) judged in both arms (the reference subset).
    cells = pd.concat([pd.read_csv(RUNS / r / "cells.csv", dtype={"instance_id": str}).assign(run=r)
                       for a in ARMS.values() for r in a if (RUNS / r / "cells.csv").exists()])
    key = ["benchmark", "instance_id", "rubric_ref"]
    calls_k = calls.merge(cells[["run", "cell_id"] + key], on=["run", "cell_id"])
    ref_keys = calls_k[calls_k.run.isin(ARMS["R'"])][key].drop_duplicates()
    for arm, runs in ARMS.items():
        c = calls_k[calls_k.run.isin(runs)].merge(ref_keys, on=key)
        c = c.sort_values("seconds").drop_duplicates(key)  # one call per matched cell
        if c.empty:
            continue
        out.append({"arm": arm + " (matched cells)", "judge_calls": len(c), "labels": len(c),
                    "harness_usd_per_label": c.usd.mean(),
                    "harness_output_share": c.usd_out.sum() / c.usd.sum(),
                    "median_seconds_per_call": c.seconds.median()})
    res = pd.DataFrame(out)
    (HERE / "results").mkdir(exist_ok=True)
    res.to_csv(HERE / "results/cost.csv", index=False)
    print(res.round(5).to_string(index=False))


if __name__ == "__main__":
    main()
