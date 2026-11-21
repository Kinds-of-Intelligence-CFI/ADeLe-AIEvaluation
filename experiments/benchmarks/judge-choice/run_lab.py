"""judge-choice, lab block (README.md): the MSc v4b and MSm candidate lab items in Jose's prompt, one repeat per arm,
through the Batch API with the subagent harness.

The prompts come from tie-rule-freeze's rebuilt, hash-verified lab prompts: each is split into demand name, rubric and
item, checked by rebuilding the verified prompt from those parts, and rebuilt with v1-layout-noreason. They hold task
text, so they live outside the repo (a JSONL path argument); only labels are written here.

    python experiments/benchmarks/judge-choice/run_lab.py submit PROMPTS.jsonl [ARM ...]
    python experiments/benchmarks/judge-choice/run_lab.py collect
"""

import argparse
import hashlib
import json
import time
from pathlib import Path

import pandas as pd

from adele.annotation.parsing import extract_demand_level
from adele.mass.backends.harness import answer_text, subagent_params

HERE = Path(__file__).resolve().parent
ARMS = {"opus-low": ("claude-opus-5-5", "low"), "sonnet-low": ("claude-sonnet-5-5", "low"),
        "haiku-low": ("claude-haiku-5-5", "low"), "haiku-medium": ("claude-haiku-5-5", "medium")}


def submit(prompts: Path, arms: list) -> None:
    import anthropic
    rows = [json.loads(x) for x in prompts.read_text().splitlines()]
    client = anthropic.Anthropic().with_options(max_retries=0)
    for arm in arms or list(ARMS):
        model, effort = ARMS[arm]
        reqs = [{"custom_id": f"{arm}-{k}", "params": {
            "model": model, "max_tokens": 16000, "output_config": {"effort": effort},
            **subagent_params(r["prompt"], f"/judge-io/jc-lab/prompts/{k}.txt",
                              f"/judge-io/jc-lab/responses/{arm}/{k}.txt")}} for k, r in enumerate(rows)]
        batch = client.messages.batches.create(requests=reqs)
        meta = {"batch": batch.id, "arm": arm, "model": model, "effort": effort,
                "cells": [{"k": k, "rubric": r["rubric"], "item_id": r["item_id"], "set": r["set"],
                           "prompt_sha256": hashlib.sha256(r["prompt"].encode()).hexdigest(),
                           "tie_sha256": r["tie_sha256"]} for k, r in enumerate(rows)]}
        (HERE / f"batch_lab_{arm}.json").write_text(json.dumps(meta, indent=1) + "\n")
        print(f"{arm}: submitted {len(reqs)} requests as {batch.id}")


def collect() -> None:
    import anthropic
    client = anthropic.Anthropic()
    out = []
    for f in sorted(HERE.glob("batch_lab_*.json")):
        meta = json.loads(f.read_text())
        cells = {c["k"]: c for c in meta["cells"]}
        while client.messages.batches.retrieve(meta["batch"]).processing_status != "ended":
            time.sleep(60)
        for res in client.messages.batches.results(meta["batch"]):
            c = cells[int(res.custom_id.rsplit("-", 1)[1])]
            row = {"arm": meta["arm"], "model_requested": meta["model"], "effort": meta["effort"], **c,
                   "writer_model": None, "level": None, "valid": False, "stop": res.result.type}
            if res.result.type == "succeeded":
                m = res.result.message
                level, ok = extract_demand_level(answer_text(m.content))
                row.update(writer_model=m.model, level=int(level) if ok else None, valid=bool(ok), stop=m.stop_reason)
            out.append(row)
    pd.DataFrame(out).drop(columns=["k"]).sort_values(["arm", "rubric", "item_id"]).to_csv(HERE / "labels_lab.csv",
                                                                                         index=False)
    print(f"collected {len(out)} labels")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(HERE.parents[2] / ".env")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["submit", "collect"])
    ap.add_argument("prompts", nargs="?")
    ap.add_argument("arms", nargs="*")
    a = ap.parse_args()
    submit(Path(a.prompts), a.arms) if a.cmd == "submit" else collect()
