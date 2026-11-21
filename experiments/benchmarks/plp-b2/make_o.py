"""Pin the runs of candidate O, odds as the driver (PREREGISTRATION.md, amendment 5). The lab regression is
pinned by ../plp-candidate/lab-regression/make_prompts_s.py --candidate o.

O (PLp_O.txt, written by hand and approved by Pablo on 2026-10-01) rewrites S: one driver, the search left
for someone with the knowledge the task calls for, anchored by odds at each level. The script runs the word
4-gram check of all text new in O (against the current PLp.txt) against the 54 rivercross frames and the lab
items, and writes
  - o-search:   the 54 rivercross states, v2 prompt, Opus low, three repeats (as s-search; descriptive)
  - o-odds:     the same states, one Opus-low call each, with a prompt that asks for O's odds instead of a level
  - o-swe-gate: the 44 SWE-bench Verified gate tasks, v2 prompt, one Opus-low call each (as s-swe-gate)

    python experiments/benchmarks/plp-b2/make_o.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("make_sq", HERE / "make_sq.py")
sqmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sqmod)
b2mod = sqmod.b2mod

ODDS_PROMPT = """We are annotating AI evaluation tasks for a research study. Below are a rubric for {demand}, with levels from 0 to 5, and a task.

<rubric>
{rubric}
</rubric>

<task>
{task}
</task>

The rubric sizes the search by its odds: how often a plan built step by step, by someone who has the knowledge the task calls for, taking the option that looks best at each step and putting any slip right as soon as it shows, comes out workable without an earlier step having to be undone. Do not give a level. Estimate those odds for this task. Write a short assessment first. End with this sentence, with N a whole number of at least 1:
Such a plan comes out workable about one time in: N"""


def main() -> None:
    cur = load_active_catalog()["PLp"]
    o = (HERE / "PLp_O.txt").read_text(encoding="utf-8").split("\n", 2)[2].rstrip("\n")
    o_sha = b2mod.sha256(o.encode())
    new = b2mod.fourgrams(o) - b2mod.fourgrams(cur.content)
    frames = pd.read_csv(b2mod.FRAME)
    lab = pd.read_csv(HERE.parent / "plp-candidate/lab-regression/items_o.csv")
    lab = lab[lab["set"] != "P"]
    shared = {"frames": sorted({" ".join(g) for t in frames["prompt"] for g in b2mod.fourgrams(t) & new}),
              "lab_items": sorted({" ".join(g) for t in lab["text"] for g in b2mod.fourgrams(t) & new})}
    print("4-grams shared with the text new in O:", shared)
    rubric = {"candidate": "experiments/benchmarks/plp-b2/PLp_O.txt", "candidate_sha256": o_sha,
              "fourgrams_new_text_shared": shared}

    srun = json.loads((HERE / "labels/s-search/run.json").read_text())
    for run, build, repeats in (
            ("o-search", lambda t: build_annotation_prompt_v2(cur.full_name, o, t), b2mod.REPEATS),
            ("o-odds", lambda t: ODDS_PROMPT.format(demand=cur.full_name, rubric=o, task=t), ["opus-low"])):
        rows, prompts = [], {}
        for st in frames.itertuples(index=False):
            prompts[st.custom_id] = build(st.prompt)
            rows.append({"benchmark": "rivercross", "instance_id": st.custom_id, "file_id": st.custom_id,
                         "demand": "PLp", "family": "v2" if run == "o-search" else "odds",
                         "prompt_sha256": b2mod.sha256(prompts[st.custom_id].encode("utf-8"))})
        meta = {**srun, "rubric": {**srun["rubric"], **rubric},
                "design": {**srun["design"], "judges": {r: srun["design"]["judges"].get(r, "adele-judge-v2-low, "
                                                                   "model alias 'opus'") for r in repeats}}}
        if run == "o-odds":
            meta["prompt"] = {"builder": "plp-b2/make_o.py ODDS_PROMPT (exploratory; not a production prompt)",
                              "template_sha256": b2mod.sha256(ODDS_PROMPT.encode())}
        sqmod.write(run, rows, prompts, repeats, meta)

    grun = json.loads((HERE / "labels/s-swe-gate/run.json").read_text())
    gate = pd.read_csv(HERE / "labels/s-swe-gate/prompts_index.csv")
    inst = pd.read_parquet(b2mod.ROOT / "data/instances/instances_swe-bench-verified.parquet").set_index("instance_id")
    rows, prompts = [], {}
    for r in gate.itertuples(index=False):
        prompts[r.instance_id] = build_annotation_prompt_v2(cur.full_name, o, inst.loc[r.instance_id, "prompt"])
        rows.append({**r._asdict(), "s_prompt_sha256": r.prompt_sha256,
                     "prompt_sha256": b2mod.sha256(prompts[r.instance_id].encode("utf-8"))})
    sqmod.write("o-swe-gate", rows, prompts, ["opus-low"],
                {**grun, "rubric": {**grun["rubric"], **rubric},
                 "baseline": "plp-b2/labels/s-swe-gate (S) and natural-prompt/labels/npb-gate-opuslow (current text)"})


if __name__ == "__main__":
    main()
