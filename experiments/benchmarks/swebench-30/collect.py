"""Parse judge responses of a swebench-30 run into labels.

Reads the judges' answers, <judge_io>/responses/<judge>/<instance>@<dim>.txt with judge_io
from run.json (data/annotations/<run>/responses/ before swev30-r4), extracts the level with
adele's parser, and writes
  - data/annotations/<run>/raw.jsonl   full responses, i.e. the judges' reasons
                                       (gitignored: they quote task text)
  - labels/<run>/labels_long.csv       ids, judge, level, hashes (committed)
then prints coverage per judge: expected, answered, parsed.

    python experiments/benchmarks/swebench-30/collect.py [--run swev30-r4]
"""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from adele.annotation.parsing import extract_demand_level

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="swev30-r4")
    run_id = ap.parse_args().run
    data_dir = ROOT / "data/annotations" / run_id
    labels_dir = HERE / "labels" / run_id
    index = pd.read_csv(labels_dir / "prompts_index.csv", dtype={"instance_id": str})
    run = json.loads((labels_dir / "run.json").read_text())
    judges = run["design"]["judges"]
    answers = (ROOT / run["judge_io"] if "judge_io" in run else data_dir) / "responses"

    rows = []
    for judge in judges:
        for rec in index.itertuples(index=False):
            path = answers / judge / f"{rec.instance_id}@{rec.demand}.txt"
            if not path.exists():
                continue
            response = path.read_text(encoding="utf-8")
            level, valid = extract_demand_level(response)
            rows.append({
                "benchmark": "swe-bench-verified", "instance_id": rec.instance_id,
                "demand": rec.demand, "family": rec.family, "judge": judge,
                "level": level if valid else None, "valid": bool(valid),
                "prompt_sha256": rec.prompt_sha256,
                "response_sha256": hashlib.sha256(response.encode("utf-8")).hexdigest(),
                "response": response,
            })
    raw = pd.DataFrame(rows)
    if raw.empty:
        print("no responses yet")
        return
    with open(data_dir / "raw.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    raw.drop(columns=["response"]).to_csv(labels_dir / "labels_long.csv", index=False)

    expected = len(index)
    for judge in judges:
        mine = raw[raw["judge"] == judge]
        print(f"{judge}: {len(mine)}/{expected} answered, {int(mine['valid'].sum())} parsed")


if __name__ == "__main__":
    main()
