"""Freeze the tau2 full task without part 3 (how the run is graded) as a separate instance folder.

Pablo, 2026-10-26: "Pre-register and pin a tau2 run with the full task minus part 3 (grading), same tasks, rubrics
and judge, so we can tell a truer reading from a leak of difficulty cues."

Each text is the judged tau2-full text (data/instances-tau2-full-v2/, built by ../tau2-full/build.py) cut before
"## 3. The goal", with the opening line on parts adjusted. Parts 1 and 2 are byte-identical to what tau2-full judged.
Writes data/instances-tau2-nogoal/instances_<slug>.csv and its INSTANCES.tsv (gitignored: task text).

    uv run python experiments/benchmarks/tau2-nogoal/build.py
"""

from pathlib import Path

import pandas as pd

from adele.instances import register

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "data/instances-tau2-full-v2"
OUT = ROOT / "data/instances-tau2-nogoal"
SLUGS = ("tau2-airline", "tau2-retail", "tau2-banking_knowledge")
PART3 = "\n\n## 3. The goal: how the run is graded\n"
OPENING = ("The agent never sees parts 2 or 3. All three\nparts together are the task you annotate.",
           "The agent never sees part 2. Both parts\ntogether are the task you annotate.")
MAX_LINE = 2000  # the Read tool cuts longer lines


def strip(text: str) -> str:
    assert text.count(PART3) == 1 and text.count(OPENING[0]) == 1
    return text.split(PART3)[0].rstrip().replace(*OPENING)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug in SLUGS:
        df = pd.read_csv(SRC / f"instances_{slug}.csv", dtype={"instance_id": str})
        new = df.assign(prompt=df["prompt"].map(strip))
        assert all(f.startswith(n.replace(*OPENING[::-1])) for f, n in zip(df["prompt"], new["prompt"]))
        joined = "".join(new["prompt"])
        assert all(k not in joined for k in ("## 3. The goal", "Expected agent actions", "Reward based on"))
        assert new["prompt"].map(lambda t: max(map(len, t.split("\n")))).max() <= MAX_LINE
        path = OUT / f"instances_{slug}.csv"
        new.to_csv(path, index=False)
        row = register(path, slug)
        cut = (df["prompt"].str.len() - new["prompt"].str.len()).median()
        print(f"{slug}: {row['n_instances']} tasks, median {row['median_prompt_chars']} chars "
              f"(part 3 median {cut:.0f}), sha {row['sha256'][:12]}")


if __name__ == "__main__":
    main()
