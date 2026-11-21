"""Wrap prompt lines longer than 1,000 characters in the ProgramBench instances, in place (run after fetch_tasks.py).

The Claude Code judge reads its prompt with the Read tool, which cuts lines longer than 2,000 characters. A few
documentation files (minified data, long tables) have such lines. Each long line is split into consecutive pieces of
at most 1,000 characters; nothing is added or removed except the line breaks. Idempotent. Rewrites prompt and
prompt_sha12 in data/instances/instances_programbench.parquet and reports which tasks changed.

    python experiments/benchmarks/programbench-data/wrap_lines.py
"""

import hashlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
FILE = ROOT / "data/instances/instances_programbench.parquet"
WIDTH = 1000


def wrap(text: str) -> str:
    out = []
    for line in text.split("\n"):
        out += [line[i:i + WIDTH] for i in range(0, len(line), WIDTH)] or [""]
    return "\n".join(out)


def main() -> None:
    df = pd.read_parquet(FILE)
    new = df["prompt"].map(wrap)
    changed = df.loc[new != df["prompt"], "instance_id"].tolist()
    df["prompt"] = new
    df["prompt_sha12"] = new.map(lambda p: hashlib.sha256(p.encode()).hexdigest()[:12])
    df.to_parquet(FILE, index=False)
    print(f"wrapped lines in {len(changed)} of {len(df)} prompts: {changed}")


if __name__ == "__main__":
    main()
