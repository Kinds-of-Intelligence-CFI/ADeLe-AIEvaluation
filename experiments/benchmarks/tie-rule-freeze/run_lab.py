"""tie-rule-freeze, lab part (README.md): the MSc v4b and MSm candidate lab prompts without the tie rule, three repeats,
through the Batch API with the subagent harness.

The prompts are rebuilt at commit 1e983b1 with the study's own functions, hash-checked against the recorded
mscand-nr-v4b and mscand-nr prompts, and stripped of the tie sentence. They hold task text, so they live outside the
repo (a JSONL path argument). Only labels are written here.

    python experiments/benchmarks/tie-rule-freeze/run_lab.py submit PROMPTS.jsonl [--pass2 ITEM ...]
    python experiments/benchmarks/tie-rule-freeze/run_lab.py collect
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
MODEL, EFFORT, REPEATS = "claude-opus-5-5", "low", 3
ARMS = {"MSc": "v4b_nt", "MSm": "msm_cand_nt"}


def submit(prompts: Path, pass2: list) -> None:
    import anthropic
    rows = [json.loads(x) for x in prompts.read_text().splitlines()]
    tag = "p2" if pass2 else "p1"
    if pass2:
        rows = [r for r in rows if r["item_id"] in set(pass2)]
    reqs = []
    for k, r in enumerate(rows):
        for rep in range(1, REPEATS + 1):
            params = {"model": MODEL, "max_tokens": 16000, "output_config": {"effort": EFFORT},
                      **subagent_params(r["prompt"], f"/judge-io/mscand-nt/prompts/{k}.txt",
                                        f"/judge-io/mscand-nt/responses/opus-low-r{rep}/{k}.txt")}
            reqs.append({"custom_id": f"{tag}-{k}-r{rep}", "params": params})
    batch = anthropic.Anthropic().with_options(max_retries=0).messages.batches.create(requests=reqs)
    meta = {"batch": batch.id, "pass": tag, "cells": [{"k": k, "rubric": r["rubric"], "item_id": r["item_id"],
            "set": r["set"], "prompt_sha256": hashlib.sha256(r["prompt"].encode()).hexdigest(),
            "tie_sha256": r["tie_sha256"]} for k, r in enumerate(rows)]}
    (HERE / f"batch_lab_{tag}.json").write_text(json.dumps(meta, indent=1) + "\n")
    print(f"submitted {len(reqs)} requests ({len(rows)} items x {REPEATS}) as {batch.id}")


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
            tag, k, rep = res.custom_id.split("-")
            c = cells[int(k)]
            row = {"pass": tag, "item_id": c["item_id"], "set": c["set"], "rubric": c["rubric"],
                   "arm": ARMS[c["rubric"]], "judge": f"opus-low-{rep}", "prompt_sha256": c["prompt_sha256"],
                   "tie_sha256": c["tie_sha256"], "writer_model": None, "level": None, "valid": False}
            if res.result.type == "succeeded":
                m = res.result.message
                level, ok = extract_demand_level(answer_text(m.content))
                row.update(writer_model=m.model, level=int(level) if ok else None, valid=bool(ok))
            out.append(row)
    pd.DataFrame(out).sort_values(["pass", "rubric", "item_id", "judge"]).to_csv(HERE / "labels_lab.csv", index=False)
    print(f"collected {len(out)} labels")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(HERE.parents[2] / ".env")
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["submit", "collect"])
    ap.add_argument("prompts", nargs="?")
    ap.add_argument("--pass2", nargs="*", default=[])
    a = ap.parse_args()
    submit(Path(a.prompts), a.pass2) if a.cmd == "submit" else collect()
