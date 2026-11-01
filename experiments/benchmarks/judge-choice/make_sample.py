"""judge-choice (README.md): draw the task sample (ids only) and write one mass spec per input folder, task group and
judge arm. Seed 20261103.

    python experiments/benchmarks/judge-choice/make_sample.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
REPO = BENCH.parents[1]
SPECS = BENCH / "mass-annotation/specs"
SEED = 20261103

GOAL = ["swe-bench-verified", "deepswe-v1.1", "frontierswe-v2", "programbench", "terminal-bench-4.0.0",
        "terminal-bench-science-0.1"]
TAU2 = ["tau2-airline", "tau2-retail", "tau2-banking_knowledge"]
SOCIAL = ["cooperbench", "eqbench4", "gamearena", "rivercross-search"]
STATIC = ["arc-agi-2", "gpqa-diamond", "arxivmath", "brokenarxiv"]
DIR = {**{b: "data/instances-goal" for b in GOAL}, **{b: "data/instances-tau2-goal" for b in TAU2},
       **{b: "data/instances" for b in SOCIAL + STATIC}}
V1 = ["AS", "AT", "CEc", "CEe", "CL", "MCr", "MCt", "MCu", "QLl", "QLq", "SNs", "VO"]  # the knowledge rubrics are left out
REFS = {"pl": ["v2/PLp", "v2/PLe"], "v1mem": [f"v1/{c}" for c in V1] + ["v2/MMe", "v2/MMp", "v2/MMs"], "msc": ["v2/MSc"]}
ARMS = {"opus-low": ("claude-opus-5-5", "low"), "sonnet-low": ("claude-sonnet-5-5", "low"),
        "haiku-low": ("claude-haiku-5-5", "low"), "haiku-medium": ("claude-haiku-5-5", "medium")}
EXTRA = ["swe-bench-verified", "cooperbench", "programbench", "tau2-retail", "arxivmath", "brokenarxiv"]  # 3 tasks, not 2


def pool(b: str) -> list:
    """The tasks a benchmark offers: the wave-1 set (released labels), or every frozen instance of a static set."""
    if b in STATIC:
        return sorted(pd.read_parquet(REPO / f"data/instances/instances_{b}.parquet")["instance_id"].astype(str))
    w = pd.read_csv(BENCH / "mass-annotation/subsets/wave1.csv", dtype=str)
    return sorted(w.loc[w["benchmark"] == b, "instance_id"])


def draw(b: str, n: int, seed: int, forced: list = ()) -> list:
    ids = [i for i in pool(b) if i not in forced]
    take = pd.Series(ids).sample(n=min(n - len(forced), len(ids)), random_state=seed).tolist()
    return sorted(list(forced) + take)


def main() -> None:
    tb_forced = list(pd.read_csv(BENCH / "tau2-tb4-pl/human-labels/unblinded.csv", dtype=str)
                     .dropna(subset=["pablo_level"])["instance_id"])
    h = pd.read_csv(BENCH / "msc-l4-note/human_items.csv", dtype=str)  # Pablo's set H: 15 tau2 tasks
    rows = []
    for k, b in enumerate(GOAL + TAU2 + SOCIAL):  # PL: 12 tasks per agentic set; Pablo's 6 TB tasks forced in
        for i in draw(b, 12, SEED + k, tb_forced if b == "terminal-bench-4.0.0" else ()):
            rows.append(("pl", b, i))
    for k, b in enumerate(GOAL + TAU2 + SOCIAL + STATIC):  # v1 + memory: 2 per set, 3 for the six largest = 40
        for i in draw(b, 3 if b in EXTRA else 2, SEED + 100 + k):
            rows.append(("v1mem", b, i))
    share = {"tau2-airline": 8, "tau2-retail": 18, "tau2-banking_knowledge": 14}  # MSc: 40 tau2 tasks, set H forced
    for k, b in enumerate(TAU2):
        forced = sorted(h.loc[h["benchmark"] == b, "instance_id"])
        for i in draw(b, max(share[b], len(forced)), SEED + 200 + k, forced):
            rows.append(("msc", b, i))
    sample = pd.DataFrame(rows, columns=["block", "benchmark", "instance_id"])
    sample.to_csv(HERE / "sample.csv", index=False)
    print(sample.groupby("block").size().to_dict(), "tasks;",
          {blk: int(n * len(REFS[blk])) for blk, n in sample.groupby("block").size().items()}, "cells per arm")
    for blk in REFS:
        for folder in ("data/instances-goal", "data/instances-tau2-goal", "data/instances"):
            part = sample[(sample["block"] == blk) & (sample["benchmark"].map(DIR) == folder)]
            if part.empty:
                continue
            tag = folder.split("/")[1].replace("instances-", "").replace("instances", "inst")
            sub = HERE / f"subset_{blk}_{tag}.csv"
            part[["benchmark", "instance_id"]].to_csv(sub, index=False)
            benches = ", ".join(f'"{b}"' for b in sorted(part["benchmark"].unique()))
            refs = ", ".join(f'"{r}"' for r in REFS[blk])
            for arm, (model, effort) in ARMS.items():
                name = f"jc-{blk}-{tag}-{arm}"
                (SPECS / f"{name}.toml").write_text(
                    f"# judge-choice (experiments/benchmarks/judge-choice): block {blk}, inputs {folder}, arm {arm}.\n"
                    f"# Jose's prompt (v1-layout-noreason) in the subagent context, through the Batch API.\n"
                    f'name = "{name}"\n\n[tasks]\nbenchmarks = [{benches}]\n'
                    f'subset = "{sub.relative_to(REPO)}"\ninstances_dir = "{folder}"\n\n'
                    f"[rubrics]\nrefs = [{refs}]\n\n[prompt]\nbuilder = \"v1-layout-noreason\"\n\n"
                    f'[judge]\nbackend = "anthropic-batch"\nmodel = "{model}"\neffort = "{effort}"\n'
                    f'harness = "subagent-v2-low"\nrepeats = 1\n'
                    f"retry = {{ fallback_writer = 1, unparsed = 1, refusal = 0, error = 2 }}\n")
    print("specs:", len(list(SPECS.glob("jc-*.toml"))))


if __name__ == "__main__":
    main()
