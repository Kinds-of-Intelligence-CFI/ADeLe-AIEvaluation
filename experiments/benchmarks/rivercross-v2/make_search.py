"""Pin the runs of rivercross-v2 amendment 2 (PREREGISTRATION.md): does PLp follow search (depth x width) rather
than the forced length of the remaining solution?

For every state (2 or more crossings from the goal) of 93 solvable puzzles, the solver gives
  - ctg:       crossings left on a shortest solution: the EXECUTION LENGTH;
  - bits:      SEARCH, -log2 of the share of legal crossing sequences of length ctg that reach the goal,
               counting only sequences that never undo the previous crossing. A forced step multiplies the
               count by 1 and choices that all work keep the share high, so neither adds bits;
  - tree_bits: log2 of the number of those sequences, i.e. depth x width including choices that all work
               (the sensitivity measure).
The family adds 'free' items (no conflicts) to chain, star and cycle puzzles, which lengthen solutions with
little search. States are sampled on a 3 x 3 grid of ctg (2-3, 4-6, 7+) by bits (bands up to 4.5, 5-8, 8.5+),
6 per cell, at most one per puzzle in a cell.

Runs
  rc-search     PLp on the 54 states, three repeats (opus-low-r1..r3), Opus low, v2 prompt
  rc-search-vo  VO (v1 Volume rubric; there is none in the v2 set) on the 54 states, once
  rc-solve-pilot, rc-solve
                the states given to a solver model to solve, five attempts each (t1..t5): 12 pilot states
                outside the sample, then the 54. The model is fixed by the pilot rule in the pre-registration.

    python experiments/benchmarks/rivercross-v2/make_search.py
"""

import hashlib
import json
import math
import os
import random
import subprocess
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2
from adele.rubrics.catalog import RubricsCatalog, default_rubrics_dir
from adele.testbeds.rivercross.annotate_methods import _subproblem_text
from adele.testbeds.rivercross.puzzle import (PuzzleSpec, _topology_edges, conflict_graph_puzzle,
                                              conflict_topology_spec, missionaries_cannibals)
from adele.testbeds.rivercross.solver import goal_state, neighbors, solve

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JUDGE_IO = ROOT.parents[1] / "judge-io"
SEED = 20260930
CTG_BINS = {"2-3": (2, 3), "4-6": (4, 6), "7+": (7, 99)}
BITS_BANDS = {"low": (0, 4.5), "mid": (5, 8), "high": (8.5, 99)}
PER_CELL, PILOT = 6, 12
SOLVE_TRIES = ["t1", "t2", "t3", "t4", "t5"]
SOLVE_INSTRUCTION = """Work it out, then give your answer after a line that reads ANSWER. List the crossings in order, \
one per line and numbered, naming everyone in the boat, for example:
ANSWER
{example}
Stop after the crossing that gets everything to the right bank."""


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def puzzles() -> list[PuzzleSpec]:
    specs = [conflict_topology_spec(n, t, b) for t in ("chain", "star", "cycle", "complete")
             for n in range(3, 8) for b in range(1, 5)]
    for n in (3, 4, 5):
        for b in (2, 3):
            s = missionaries_cannibals(n, b)
            specs.append(PuzzleSpec(**{**s.__dict__, "name": f"missionaries-cannibals-{n}-boat-{b}"}))
    for t in ("chain", "star", "cycle"):
        for k in (3, 4):
            for f in (1, 2, 3):
                for b in (1, 2, 3):
                    core = tuple(f"item{i + 1}" for i in range(k))
                    free = tuple(f"item{k + i + 1}" for i in range(f))
                    specs.append(conflict_graph_puzzle(core + free, _topology_edges(core, t), b,
                                                       name=f"{t}-{k}+free{f}-boat-{b}"))
    return specs


def state_id(spec: PuzzleSpec, state) -> str:
    left, side = state
    return f"{spec.name}--{side}-{'.'.join(sorted(left)) or 'none'}"


def pool() -> tuple[pd.DataFrame, dict]:
    rows, specs = [], {}
    for spec in puzzles():
        sol = solve(spec)
        if sol.optimal_len is None:
            continue
        goal = goal_state(spec)

        @lru_cache(None)
        def count(s, prev, k):  # (non-undo sequences of length k, those ending at the goal)
            if k == 0:
                return (1, int(s == goal))
            a = g = 0
            for n in neighbors(spec, s):
                if n != prev:
                    x, y = count(n, s, k - 1)
                    a, g = a + x, g + y
            return (a, g)

        for s, k in sol.dist.items():
            if k < 2:
                continue
            a, g = count(s, None, k)
            cid = state_id(spec, s)
            specs[cid] = (spec, s)
            rows.append({"custom_id": cid, "puzzle": spec.name, "items": len(spec.items), "boat": spec.boat_capacity,
                         "ctg": k, "bits": round(math.log2(a / g), 4), "tree_bits": round(math.log2(a), 4)})
    return pd.DataFrame(rows).sort_values("custom_id").reset_index(drop=True), specs


def band(x: float, bands: dict) -> str | None:
    return next((k for k, (lo, hi) in bands.items() if lo <= x <= hi), None)


def write_run(run_id: str, cells: list[tuple[str, str, str]], judges: list[str], meta: dict) -> None:
    """cells: (file_id, demand, prompt)."""
    io, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
    for d in [io / "prompts", labels] + [io / "responses" / j for j in judges]:
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    for fid, dim, prompt in cells:
        (io / "prompts" / f"{fid}@{dim}.txt").write_text(prompt, encoding="utf-8")
        rows.append({"benchmark": "rivercross", "instance_id": fid, "file_id": fid, "demand": dim, "family": "v2",
                     "prompt_sha256": sha256(prompt.encode("utf-8"))})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repo_commit": git("rev-parse", "HEAD"),
           "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
           "benchmark": ["rivercross"], "design": {"n_prompts": len(rows), "judges": {j: meta["judge"] for j in judges}},
           **{k: v for k, v in meta.items() if k != "judge"},
           "judge_instruction": "Prompt file: {prompt_file}\nResponse file: {response_file}",
           "judge_io": os.path.relpath(io, ROOT),
           "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file"}
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(rows)} prompts x {len(judges)}")


def main() -> None:
    rng = random.Random(SEED)
    df, specs = pool()
    df["ctg_bin"] = [band(k, CTG_BINS) for k in df["ctg"]]
    df["bits_band"] = [band(b, BITS_BANDS) for b in df["bits"]]
    chosen = []
    for cb in CTG_BINS:
        for bb in BITS_BANDS:
            cand = df[(df["ctg_bin"] == cb) & (df["bits_band"] == bb)]
            puz = sorted(cand["puzzle"].unique())
            rng.shuffle(puz)
            assert len(puz) >= PER_CELL, (cb, bb, len(puz))
            for p in puz[:PER_CELL]:
                ids = cand[cand["puzzle"] == p]["custom_id"].tolist()
                chosen.append(ids[rng.randrange(len(ids))])
    sample = df[df["custom_id"].isin(chosen)].copy()
    rest = df[~df["custom_id"].isin(chosen) & df["ctg_bin"].notna() & df["bits_band"].notna()]
    pilot = rest.groupby(["ctg_bin", "bits_band"], group_keys=False).apply(
        lambda x: x.sample(n=min(len(x), 2), random_state=SEED)).sample(n=PILOT, random_state=SEED)

    frames = HERE / "frames"
    frames.mkdir(exist_ok=True)
    for name, x in (("search", sample), ("search_pilot", pilot)):
        x = x.copy()
        x["prompt"] = [_subproblem_text(*specs[c]) for c in x["custom_id"]]
        x[["custom_id", "prompt"]].to_csv(frames / f"{name}_frame.csv", index=False)
        x.drop(columns=["prompt"]).to_csv(frames / f"{name}_truth.csv", index=False)
    # the spec of every sampled state, so scoring can replay answers without regenerating the pool
    json.dump({c: {"spec": specs[c][0].to_dict(), "left": sorted(specs[c][1][0]), "side": specs[c][1][1]}
               for c in list(sample["custom_id"]) + list(pilot["custom_id"])},
              open(frames / "search_specs.json", "w"), indent=1)

    plp = load_active_catalog()["PLp"]
    vo = RubricsCatalog.from_paths([default_rubrics_dir() / "VO.txt"])["VO"]
    frame = dict(zip(sample["custom_id"], (_subproblem_text(*specs[c]) for c in sample["custom_id"])))
    common = {"frame": {"file": "experiments/benchmarks/rivercross-v2/frames/search_frame.csv",
                        "sha256": sha256((frames / "search_frame.csv").read_bytes()), "seed": SEED},
              "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                         "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())}}
    write_run("rc-search", [(c, "PLp", build_annotation_prompt_v2(plp.full_name, plp.content, t)) for c, t in frame.items()],
              ["opus-low-r1", "opus-low-r2", "opus-low-r3"],
              {**common, "judge": "adele-judge-v2-low, model alias 'opus'",
               "rubrics_sha256": {"PLp": sha256(plp.content.encode("utf-8"))}})
    write_run("rc-search-vo", [(c, "VO", build_annotation_prompt_v2(vo.full_name, vo.content, t)) for c, t in frame.items()],
              ["opus-low"], {**common, "judge": "adele-judge-v2-low, model alias 'opus'",
                             "rubrics_sha256": {"VO": sha256(vo.content.encode("utf-8")), "VO_version": vo.version}})

    def solve_prompt(c: str) -> str:
        spec = specs[c][0]
        example = "1. farmer, item2\n2. farmer" if spec.ferryman else f"1. {spec.items[0]}, {spec.items[-1]}\n2. {spec.items[0]}"
        return _subproblem_text(*specs[c]) + "\n\n" + SOLVE_INSTRUCTION.format(example=example)

    for run_id, ids in (("rc-solve-pilot", pilot["custom_id"]), ("rc-solve", sample["custom_id"])):
        write_run(run_id, [(c, "SOLVE", solve_prompt(c)) for c in ids], SOLVE_TRIES,
                  {"judge": "rc-solver subagent; model fixed by the pilot rule (PREREGISTRATION.md, amendment 2)",
                   "solve_instruction_sha256": sha256(SOLVE_INSTRUCTION.encode("utf-8"))})

    s = sample
    print(pd.crosstab(s["ctg_bin"], s["bits_band"]))
    print("sample Spearman ctg~bits:", round(s["ctg"].corr(s["bits"], method="spearman"), 3),
          "| ctg~tree_bits:", round(s["ctg"].corr(s["tree_bits"], method="spearman"), 3),
          "| bits~tree_bits:", round(s["bits"].corr(s["tree_bits"], method="spearman"), 3),
          "| puzzles:", s["puzzle"].nunique())


if __name__ == "__main__":
    main()
