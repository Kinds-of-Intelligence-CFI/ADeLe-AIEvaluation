"""Pin the runs of rivercross-v2 amendment 3 (PREREGISTRATION.md): the amendment 2 solver criterion with strong
solvers. The 54 prompts of rc-solve are copied unchanged (same SHA-256) into
  rc-solve-sonnet  model alias 'sonnet' (Sonnet 5.5), five attempts per state
  rc-solve-opus    model alias 'opus' (Opus 5.5), five attempts per state
through the rc-solver agent (effort low, set in the agent file).

    python experiments/benchmarks/rivercross-v2/make_strong.py
"""

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = "rc-solve"
RUNS = {"rc-solve-sonnet": "claude-sonnet-5-5", "rc-solve-opus": "claude-opus-5-5"}
TRIES = ["t1", "t2", "t3", "t4", "t5"]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> None:
    src_run = json.loads((HERE / f"labels/{SRC}/run.json").read_text())
    src_io = ROOT / src_run["judge_io"]
    index = pd.read_csv(HERE / f"labels/{SRC}/prompts_index.csv")
    for run_id, model in RUNS.items():
        io = src_io.parent / run_id
        labels = HERE / "labels" / run_id
        for d in [io / "prompts", labels] + [io / "responses" / t for t in TRIES]:
            d.mkdir(parents=True, exist_ok=True)
        for r in index.itertuples(index=False):
            name = f"{r.file_id}@{r.demand}.txt"
            shutil.copyfile(src_io / "prompts" / name, io / "prompts" / name)
            assert sha256((io / "prompts" / name).read_bytes()) == r.prompt_sha256
        index.to_csv(labels / "prompts_index.csv", index=False)
        run = {**src_run, "run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "prompts_copied_from": SRC, "intended_model": model,
               "design": {"n_prompts": len(index),
                          "judges": {t: f"rc-solver subagent (effort low), model {model}" for t in TRIES}},
               "judge_io": f"../../judge-io/{run_id}"}
        (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
        print(f"{run_id}: {len(index)} prompts x {len(TRIES)} attempts, intended model {model}")


if __name__ == "__main__":
    main()
