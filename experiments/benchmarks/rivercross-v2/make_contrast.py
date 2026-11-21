"""Pin run rc-contrast of rivercross-v2 (PREREGISTRATION.md, amendment 1): does PLp follow the length of
the remaining solution or the search it needs?

For every state of 50 solvable river-crossing puzzles the solver gives
  - ctg: crossings left on a shortest solution (cost-to-go), the LENGTH of the remaining plan;
  - T:   decision points, the SEARCH it needs. This is the fewest steps, over the optimal routes from the state,
         at which a legal crossing other than undoing the previous one is not optimal. At the state itself,
         any non-optimal crossing counts, since the frame does not show the previous crossing.
Two kinds of within-puzzle pairs are drawn, so the rules and wording are the same within a pair:
  - search pairs: same puzzle and ctg, T differs by 2 or more (all such (puzzle, ctg) combinations);
  - length pairs: same puzzle and T, ctg differs by 2 or more, neither state one crossing from the goal
    (PLp Level 0 already covers a single forced crossing). One pair per puzzle, the widest gap.
Each state is judged for PLp three times (judge folders opus-low-r1..r3); the label is the median.

Writes frames/contrast_frame.csv (custom_id, prompt), frames/contrast_truth.csv (solver values, never shown
to the judge), frames/contrast_pairs.csv, and the prompts and run.json of rc-contrast.

    python experiments/benchmarks/rivercross-v2/make_contrast.py
"""

import hashlib
import json
import os
import random
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2
from adele.testbeds.rivercross.annotate_methods import _subproblem_text
from adele.testbeds.rivercross.puzzle import PuzzleSpec, conflict_topology_spec, missionaries_cannibals
from adele.testbeds.rivercross.solver import neighbors, solve

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
JUDGE_IO = ROOT.parents[1] / "judge-io"
AGENT = ROOT / "experiments/benchmarks/natural-prompt/adele-judge-v2-low.md"
RUN = "rc-contrast"
REPEATS = ["opus-low-r1", "opus-low-r2", "opus-low-r3"]
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"
SEED = 20260930


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def puzzles() -> list[PuzzleSpec]:
    specs = [conflict_topology_spec(n, t, b) for t in ("chain", "star", "cycle", "complete")
             for n in range(3, 8) for b in range(1, 5)]
    for n in (3, 4, 5):
        for b in (2, 3):
            spec = missionaries_cannibals(n, b)
            # the library names both boat sizes alike
            specs.append(PuzzleSpec(**{**spec.__dict__, "name": f"missionaries-cannibals-{n}-boat-{b}"}))
    return specs


def decision_points(spec: PuzzleSpec, dist: dict) -> dict:
    memo: dict = {}

    def f(s, prev):
        if dist[s] == 0:
            return 0
        if (s, prev) not in memo:
            nbs = neighbors(spec, s)
            opt = [n for n in nbs if dist.get(n) == dist[s] - 1]
            wrong = [n for n in nbs if n not in opt and n != prev]
            memo[(s, prev)] = (1 if wrong else 0) + min(f(n, s) for n in opt)
        return memo[(s, prev)]

    return {s: f(s, None) for s in dist}


def state_id(spec: PuzzleSpec, state) -> str:
    left, side = state
    return f"{spec.name}--{side}-{'.'.join(sorted(left)) or 'none'}"


def main() -> None:
    rng = random.Random(SEED)
    states = []
    for spec in puzzles():
        sol = solve(spec)
        if sol.optimal_len is None:
            continue
        T = decision_points(spec, sol.dist)
        for s, k in sol.dist.items():
            if k > 0:
                states.append({"custom_id": state_id(spec, s), "puzzle": spec.name, "items": len(spec.items),
                               "boat": spec.boat_capacity, "ctg": k, "T": T[s],
                               "prompt": _subproblem_text(spec, s)})
    df = pd.DataFrame(states).sort_values("custom_id").reset_index(drop=True)

    def pick(rows: pd.DataFrame) -> str:
        return rows["custom_id"].tolist()[rng.randrange(len(rows))]

    pairs = []
    for (p, k), x in df.groupby(["puzzle", "ctg"]):
        if x["T"].max() - x["T"].min() >= 2:
            pairs.append({"kind": "search", "puzzle": p, "low": pick(x[x["T"] == x["T"].min()]),
                          "high": pick(x[x["T"] == x["T"].max()])})
    for p, x in df[df["ctg"] >= 2].groupby("puzzle"):
        best = None
        for t, y in x.groupby("T"):
            gap = y["ctg"].max() - y["ctg"].min()
            if gap >= 2 and (best is None or gap > best[0]):
                best = (gap, t, y)
        if best:
            y = best[2]
            pairs.append({"kind": "length", "puzzle": p, "low": pick(y[y["ctg"] == y["ctg"].min()]),
                          "high": pick(y[y["ctg"] == y["ctg"].max()])})
    pairs = pd.DataFrame(pairs)
    used = sorted(set(pairs["low"]) | set(pairs["high"]))
    chosen = df[df["custom_id"].isin(used)]

    frames = HERE / "frames"
    frames.mkdir(exist_ok=True)
    chosen[["custom_id", "prompt"]].to_csv(frames / "contrast_frame.csv", index=False)
    chosen.drop(columns=["prompt"]).to_csv(frames / "contrast_truth.csv", index=False)
    pairs.to_csv(frames / "contrast_pairs.csv", index=False)

    catalog = load_active_catalog()
    rub = catalog["PLp"]
    io, labels = JUDGE_IO / RUN, HERE / "labels" / RUN
    for d in [io / "prompts", labels] + [io / "responses" / r for r in REPEATS]:
        d.mkdir(parents=True, exist_ok=True)
    rows = []
    for s in chosen.itertuples(index=False):
        prompt = build_annotation_prompt_v2(rub.full_name, rub.content, s.prompt)
        (io / "prompts" / f"{s.custom_id}@PLp.txt").write_text(prompt, encoding="utf-8")
        rows.append({"benchmark": "rivercross", "instance_id": s.custom_id, "file_id": s.custom_id, "demand": "PLp",
                     "family": "v2", "prompt_sha256": sha256(prompt.encode("utf-8"))})
    pd.DataFrame(rows).to_csv(labels / "prompts_index.csv", index=False)
    run = {
        "run_id": RUN,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD"),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "benchmark": ["rivercross"],
        "frame": {"file": str((frames / "contrast_frame.csv").relative_to(ROOT)),
                  "sha256": sha256((frames / "contrast_frame.csv").read_bytes()), "seed": SEED},
        "design": {"n_states": len(chosen), "n_pairs": pairs["kind"].value_counts().to_dict(), "dims": ["PLp"],
                   "n_prompts": len(rows),
                   "judges": {r: "Claude Code subagent 'adele-judge-v2-low' (effort low), model alias 'opus'; "
                                 "repeat " + r[-1] for r in REPEATS}},
        "rubrics_sha256": {"PLp": sha256(rub.content.encode("utf-8"))},
        "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                   "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
        "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
        "judge_instruction": INSTRUCTION,
        "judge_io": os.path.relpath(io, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{RUN}: {len(chosen)} states, {len(rows)} prompts x {len(REPEATS)} repeats;",
          pairs["kind"].value_counts().to_dict())
    print(pairs.merge(df[["custom_id", "ctg", "T"]], left_on="low", right_on="custom_id")
          .merge(df[["custom_id", "ctg", "T"]], left_on="high", right_on="custom_id", suffixes=("_low", "_high"))
          [["kind", "puzzle", "ctg_low", "T_low", "ctg_high", "T_high"]].to_string())


if __name__ == "__main__":
    main()
