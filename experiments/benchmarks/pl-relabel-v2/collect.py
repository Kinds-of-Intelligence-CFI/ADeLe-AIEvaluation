"""Parse judge responses of a pl-relabel-v2 run into labels (as plp-candidate/collect.py).

Reads <judge_io>/responses/<judge>/<file_id>@<dim>.txt, with judge_io from run.json, extracts
the level with adele's parser, adds the model that wrote each answer (labels/<run>/writers.csv,
from writers.py), and writes
  - data/annotations/<run>/raw.jsonl   full responses, i.e. the judges' reasons
                                       (gitignored: they quote task text)
  - labels/<run>/labels_long.csv       ids, judge, writer model, level, hashes (committed)
then prints coverage per judge: expected, answered, parsed.

    python experiments/benchmarks/pl-relabel-v2/collect.py --run v2-swe
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
    ap.add_argument("--run", required=True)
    run_id = ap.parse_args().run
    data_dir = ROOT / "data/annotations" / run_id
    labels_dir = HERE / "labels" / run_id
    index = pd.read_csv(labels_dir / "prompts_index.csv", dtype={"instance_id": str})
    run = json.loads((labels_dir / "run.json").read_text())
    answers = ROOT / run["judge_io"] / "responses"
    writers = pd.read_csv(labels_dir / "writers.csv").set_index(["judge", "file_id", "demand"])["writer_model"]

    rows = []
    for judge in run["design"]["judges"]:
        for rec in index.itertuples(index=False):
            path = answers / judge / f"{rec.file_id}@{rec.demand}.txt"
            if not path.exists():
                continue
            response = path.read_text(encoding="utf-8")
            level, valid = extract_demand_level(response)
            rows.append({
                "benchmark": rec.benchmark, "instance_id": rec.instance_id,
                "demand": rec.demand, "family": rec.family, "judge": judge,
                "writer_model": writers[(judge, rec.file_id, rec.demand)],
                "level": level if valid else None, "valid": bool(valid),
                "prompt_sha256": rec.prompt_sha256,
                "response_sha256": hashlib.sha256(response.encode("utf-8")).hexdigest(),
                "response": response,
            })
    if not rows:
        print("no responses yet")
        return
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(data_dir / "raw.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    pd.DataFrame(rows).drop(columns=["response"]).to_csv(labels_dir / "labels_long.csv", index=False)
    for judge in run["design"]["judges"]:
        mine = [r for r in rows if r["judge"] == judge]
        print(f"{judge}: {len(mine)}/{len(index)} answered, {sum(r['valid'] for r in mine)} parsed")


if __name__ == "__main__":
    main()
