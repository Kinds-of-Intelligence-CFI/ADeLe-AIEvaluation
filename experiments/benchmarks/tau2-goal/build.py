"""Freeze the tau2 full task with its goal but without the grader's expected-action list.

Pablo, 2026-10-26: "keep the goal and drop the expected-action list."

Each text is the judged tau2-full text (data/instances-tau2-full-v2/, built by ../tau2-full/build.py) with two kinds of
paragraph removed from part 3: the "Expected agent actions" / "Expected customer actions" headings and the tool-call
bullets under them. Part 3 keeps the designer's purpose, what the agent must tell the customer, the outcome checks,
what the reward is based on and known task issues. Parts 1 and 2 are byte-identical to tau2-full.
Writes data/instances-tau2-goal/instances_<slug>.csv and its INSTANCES.tsv (gitignored: task text).

    uv run python experiments/benchmarks/tau2-goal/build.py
"""

import re
from pathlib import Path

import pandas as pd

from adele.instances import register

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "data/instances-tau2-full-v2"
OUT = ROOT / "data/instances-tau2-goal"
SLUGS = ("tau2-airline", "tau2-retail", "tau2-banking_knowledge")
PART3 = "\n\n## 3. The goal: how the run is graded\n\n"
ACTIONS = ("**Expected agent actions.**", "**Expected customer actions.**")
CALL = re.compile(r"- `\w+\(.*\)`", re.S)  # one expected tool call
MAX_LINE = 2000  # the Read tool cuts longer lines


def drop_actions(text: str) -> str:
    head, part3 = text.split(PART3)
    kept = [p for p in part3.split("\n\n") if not p.startswith(ACTIONS) and not CALL.fullmatch(p)]
    assert all(not p.startswith("- `") for p in kept), "an unrecognised bullet"
    return head + PART3 + "\n\n".join(kept)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug in SLUGS:
        df = pd.read_csv(SRC / f"instances_{slug}.csv", dtype={"instance_id": str})
        new = df.assign(prompt=df["prompt"].map(drop_actions))
        assert all(f.split(PART3)[0] == n.split(PART3)[0] for f, n in zip(df["prompt"], new["prompt"]))
        assert not new["prompt"].str.contains("Expected agent actions|Expected customer actions").any()
        assert new["prompt"].map(lambda t: max(map(len, t.split("\n")))).max() <= MAX_LINE
        path = OUT / f"instances_{slug}.csv"
        new.to_csv(path, index=False)
        row = register(path, slug)
        cut = (df["prompt"].str.len() - new["prompt"].str.len()).median()
        print(f"{slug}: {row['n_instances']} tasks, median {row['median_prompt_chars']} chars "
              f"(dropped median {cut:.0f}), sha {row['sha256'][:12]}")


if __name__ == "__main__":
    main()
