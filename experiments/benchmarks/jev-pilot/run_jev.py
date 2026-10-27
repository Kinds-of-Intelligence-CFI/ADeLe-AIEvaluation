"""Label the agentic and social benchmark tasks with TypeSafe's Jev (a System One classifier), on the five v2 rubrics.

Each rubric becomes one Score question: `instructions` hold the question and the rubric's opening paragraphs (what it
assesses and what it does not cover); `criteria` hold the six levels, each with its statement and example bullets, as
written. The state is the task text the Opus judge saw (the pinned specs' instances). All five questions go in one
request per task. Jev returns a probability per level; the label is the most probable level, and the expected level is
kept too. Rubric texts: the active catalog when this runs (the same texts as the Opus labels).

Sets: the seven clean agentic sets (spec pls-relabel and pls-relabel-long) and the three social sets (eqbench4-plms,
cooperbench-plms, gamearena-plms). Plus a repeat of 100 seeded tasks to measure determinism. A task whose state plus
longest question would exceed Jev's 32k-token budget (estimated at 3.5 characters per token) is skipped and recorded.

Responses: ~/Developer/ADELE/judge-io/jev-pilot/<set>/<task key>.json (local; no task text). Labels:
labels/jev_labels.csv. Needs TYPESAFE_API_KEY (read from ~/Developer/ADELE/.env).

    python experiments/benchmarks/jev-pilot/run_jev.py [--limit N]
"""

import argparse
import hashlib
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import pandas as pd
from dotenv import load_dotenv

from adele.agentic import load_active_catalog
from adele.mass.pin import load_instances
from adele.mass.spec import load_spec

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
ROOT = BENCH.parents[1]
IO = ROOT.parents[1] / "judge-io/jev-pilot"
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
SPECS = {"agentic": ["pls-relabel", "pls-relabel-long"],
         "social": ["eqbench4-plms", "cooperbench-plms", "gamearena-plms"]}
URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-1.13.0"
MAX_TOKENS = 32000
REPEATS, SEED = 100, 20261004


def parse(content: str) -> tuple[str, list[dict]]:
    """Opening paragraphs, and one {level, statement, examples} per level."""
    head, levels, cur = [], [], None
    for line in content.splitlines():
        m = re.match(r"Level (\d): (.*)", line)
        if m:
            cur = {"level": int(m.group(1)), "statement": m.group(2), "examples": []}
            levels.append(cur)
        elif cur is None:
            head.append(line)
        elif line.startswith("* "):
            cur["examples"].append(line[2:].strip())
        elif line.strip() and line.strip() != "Examples:":
            cur["statement"] += " " + line.strip()
    assert [lv["level"] for lv in levels] == list(range(6))
    return "\n".join(head).strip(), levels


def questions(cat) -> dict:
    out = {}
    for d in DIMS:
        r = cat[d]
        head, levels = parse(r.content)
        out[d] = {"type": "score",
                  "instructions": {"question": f"What level of demand for {r.full_name} does the task in the state make? "
                                               "Rate what the task requires, not any answer to it, using this rubric.",
                                   "rubric": head},
                  "criteria": [{"level": f"Level {lv['level']}", "definition": lv["statement"],
                                "examples": lv["examples"]} for lv in levels]}
    return out


def tasks() -> pd.DataFrame:
    frames = []
    for group, specs in SPECS.items():
        for s in specs:
            inst, _ = load_instances(load_spec(BENCH / f"mass-annotation/specs/{s}.toml", root=ROOT))
            frames.append(inst.assign(group=group, spec=s))
    return pd.concat(frames, ignore_index=True)


def key(bench: str, iid: str, rep: int) -> str:
    return hashlib.sha256(f"{bench}|{iid}".encode()).hexdigest()[:16] + ("" if rep == 1 else f"~r{rep}")


def call(client: httpx.Client, body: dict) -> dict:
    for attempt in range(6):
        r = client.post(URL, json=body, timeout=120)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(float(r.headers.get("retry-after", 2 ** attempt)))
            continue
        return {"error": r.status_code, "detail": r.text[:500]}
    return {"error": "retries exhausted"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    load_dotenv(Path.home() / "Developer/ADELE/.env")
    cat = load_active_catalog()
    qs = questions(cat)
    q_tokens = max(len(json.dumps(q)) for q in qs.values()) / 3.5
    t = tasks()
    rng = random.Random(SEED)
    reps = t.sample(REPEATS, random_state=rng.randrange(2**31))
    jobs = [(r, 1) for r in t.itertuples(index=False)] + [(r, 2) for r in reps.itertuples(index=False)]
    if args.limit:
        jobs = jobs[: args.limit]
    meta = {"model": MODEL, "rubric_sha256": {d: hashlib.sha256(cat[d].content.encode()).hexdigest() for d in DIMS},
            "questions_sha256": hashlib.sha256(json.dumps(qs, sort_keys=True).encode()).hexdigest()}
    (HERE / "labels").mkdir(exist_ok=True)
    (HERE / "labels/run.json").write_text(json.dumps(meta, indent=2) + "\n")
    client = httpx.Client(headers={"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"})

    def one(job):
        r, rep = job
        out = IO / r.spec / f"{key(r.benchmark, r.instance_id, rep)}.json"
        if out.exists():
            return
        out.parent.mkdir(parents=True, exist_ok=True)
        if len(r.prompt) / 3.5 + q_tokens > MAX_TOKENS:
            out.write_text(json.dumps({"skipped": "over the 32k state budget", "state_chars": len(r.prompt)}))
            return
        res = call(client, {"state": r.prompt, "model": MODEL, "questions": qs})
        out.write_text(json.dumps(res))

    with ThreadPoolExecutor(8) as ex:
        list(ex.map(one, jobs))

    rows = []
    for r, rep in jobs:
        res = json.loads((IO / r.spec / f"{key(r.benchmark, r.instance_id, rep)}.json").read_text())
        for d in DIMS:
            a = res.get("answers", {}).get(d)
            row = {"group": r.group, "spec": r.spec, "benchmark": r.benchmark, "instance_id": r.instance_id,
                   "repeat": rep, "rubric": d, "status": "ok" if a else res.get("skipped") or str(res.get("error"))}
            if a:
                p = {int(k): v for k, v in a["probabilities"].items()}
                row.update({"level": max(p, key=p.get), "expected": a["score"], "confidence": a["confidence"],
                            **{f"p{k}": p.get(k, 0.0) for k in range(6)}, "model": res.get("model"),
                            "input_tokens": res.get("usage", {}).get("input_tokens")})
            rows.append(row)
    lab = pd.DataFrame(rows)
    lab.to_csv(HERE / "labels/jev_labels.csv", index=False)
    print(lab.groupby(["group", "status"]).size().to_string())
    print("input tokens:", int(lab.drop_duplicates(["spec", "benchmark", "instance_id", "repeat"])["input_tokens"].sum()))


if __name__ == "__main__":
    main()
