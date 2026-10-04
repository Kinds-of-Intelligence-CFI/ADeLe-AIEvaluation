"""Jev on the v1 battery with the 18 v1 rubrics (UG is computed, not judged). Writes sample.csv and
labels/jev_labels.csv.

Sample (seed 20261004): 1,000 battery items stratified by benchmark (each benchmark's share, at least 3 items); the
first 3 drawn per benchmark (60 items) form the core that Opus also judges (make_opus_prompts.py). The state is the
item's `question` field, the task as posed without the battery's answer-format suffix. Questions: one Score question
per v1 rubric, built as in ../jev-pilot/run_jev.py (opening paragraph in `instructions`, the six levels with their
examples in `criteria`). The paper's GPT-4o labels come with the battery.

Responses: ~/Developer/ADELE/judge-io/jev-v1/<item>.json (local). Needs TYPESAFE_API_KEY (~/Developer/ADELE/.env).

    python experiments/benchmarks/jev-v1/run_jev_v1.py
"""

import glob
import hashlib
import importlib.util
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pandas as pd
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
V1 = ROOT / "src/adele/rubrics/data_v1"
IO = ROOT.parents[1] / "judge-io/jev-v1"
DIMS = ["AS", "CEc", "CEe", "CL", "KNn", "KNa", "KNc", "KNf", "KNs", "MCt", "MCu", "MCr", "MS", "QLq", "QLl", "SNs",
        "VO", "AT"]
FILE = {"MS": "MSm"}  # the battery's MS column is data_v1/MSm.txt
N, CORE, SEED = 1000, 3, 20261004
MODEL = "jev-1.13.0"

_spec = importlib.util.spec_from_file_location("run_jev", HERE.parent / "jev-pilot/run_jev.py")
_jev = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_jev)


def battery() -> pd.DataFrame:
    f = glob.glob(str(Path.home() / ".cache/huggingface/hub/datasets--CFI-Kinds-of-Intelligence--ADeLe_battery_v1dot0"
                      "/snapshots/*/ADeLe_batterry_v1dot0.csv"))[0]
    return pd.read_csv(f)


def sample(b: pd.DataFrame) -> pd.DataFrame:
    shares = (b["benchmark"].value_counts(normalize=True) * N).round().clip(lower=CORE).astype(int)
    parts = []
    for bench, n in shares.items():
        g = b[b["benchmark"] == bench].sample(frac=1, random_state=SEED)
        parts.append(g.head(n).assign(core=[i < CORE for i in range(min(n, len(g)))]))
    return pd.concat(parts, ignore_index=True)


def rubric(code: str) -> tuple[str, str]:
    text = (V1 / f"{FILE.get(code, code)}.txt").read_text(encoding="utf-8")
    name = text.splitlines()[0].removeprefix("# ").strip()
    body = "\n".join(text.splitlines()[1:]).strip()
    body = re.sub(r"\s*Examples:\s*$", "", body, flags=re.M)  # some v1 files put "Examples:" on the level line
    return name, body


def questions() -> dict:
    out = {}
    for d in DIMS:
        name, body = rubric(d)
        head, levels = _jev.parse(body)
        out[d] = {"type": "score",
                  "instructions": {"question": f"What level of demand for {name} does the task in the state make? "
                                               "Rate what the task requires, not any answer to it, using this rubric.",
                                   "rubric": head},
                  "criteria": [{"level": f"Level {lv['level']}", "definition": lv["statement"].removesuffix(" Examples:"),
                                "examples": lv["examples"]} for lv in levels]}
    return out


def main() -> None:
    load_dotenv(Path.home() / "Developer/ADELE/.env")
    s = sample(battery())
    s[["benchmark", "instance_id", "core"] + DIMS].to_csv(HERE / "sample.csv", index=False)
    qs = questions()
    (HERE / "labels").mkdir(exist_ok=True)
    (HERE / "labels/run.json").write_text(json.dumps(
        {"model": MODEL, "questions_sha256": hashlib.sha256(json.dumps(qs, sort_keys=True).encode()).hexdigest(),
         "rubric_sha256": {d: hashlib.sha256((V1 / f"{FILE.get(d, d)}.txt").read_bytes()).hexdigest() for d in DIMS}},
        indent=2) + "\n")
    client = httpx.Client(headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"})
    IO.mkdir(parents=True, exist_ok=True)

    def one(r):
        out = IO / f"{r.instance_id}.json"
        if not out.exists():
            out.write_text(json.dumps(_jev.call(client, {"state": r.question, "model": MODEL, "questions": qs})))

    with ThreadPoolExecutor(8) as ex:
        list(ex.map(one, s.itertuples(index=False)))
    rows = []
    for r in s.itertuples(index=False):
        res = json.loads((IO / f"{r.instance_id}.json").read_text())
        for d in DIMS:
            a = res.get("answers", {}).get(d)
            row = {"benchmark": r.benchmark, "instance_id": r.instance_id, "core": r.core, "rubric": d,
                   "status": "ok" if a else str(res.get("error"))}
            if a:
                p = {int(k): v for k, v in a["probabilities"].items()}
                row.update({"level": max(p, key=p.get), "expected": a["score"], "confidence": a["confidence"],
                            **{f"p{k}": p.get(k, 0.0) for k in range(6)},
                            "input_tokens": res.get("usage", {}).get("input_tokens")})
            rows.append(row)
    lab = pd.DataFrame(rows)
    lab.to_csv(HERE / "labels/jev_labels.csv", index=False)
    print(lab["status"].value_counts().to_string())
    print("input tokens:", int(lab.drop_duplicates("instance_id")["input_tokens"].sum()))


if __name__ == "__main__":
    main()
