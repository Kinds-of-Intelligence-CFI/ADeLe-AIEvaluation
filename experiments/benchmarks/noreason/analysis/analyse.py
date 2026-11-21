"""Pre-registered analysis of noreason (see PREREGISTRATION.md). Writes results/analysis.json and prints a summary.

Arms: NR = runs noreason-pl, noreason-ms (v2-noreason builder); R' = runs noreason-ref, noreason-ref-ms (v2 builder,
same day, current texts, 150-task subset); released = release.current_labels (relabel-v2 with relabel-v3 overrides).
Only valid answers written by claude-opus-5-5 count. Runs that are still incomplete are analysed as far as they go.

    python experiments/benchmarks/noreason/analysis/analyse.py
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
ROOT = BENCH.parents[1]
RUNS = BENCH / "mass-annotation/runs"
MODEL = "claude-opus-5-5"
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
TAU2 = ["tau2-airline", "tau2-retail", "tau2-banking_knowledge"]
KEY = ["benchmark", "instance_id", "rubric"]
SIGNAL = [("swe-bench-verified", "PLp"), ("programbench", "PLp"), ("tau2", "PLp")]


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


release = load("release", BENCH / "release.py")
combined = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py").combined
outcomes = load("msb_analyse", BENCH / "ms-benchmarks/analysis/analyse.py").outcomes


def run_labels(runs: list[str], col: str) -> pd.DataFrame:
    parts = []
    for r in runs:
        p = RUNS / r / "labels.csv"
        if not p.exists():
            continue
        lab = pd.read_csv(p, dtype={"instance_id": str})
        lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
        parts.append(pd.DataFrame({"benchmark": lab["benchmark"], "instance_id": lab["instance_id"],
                                   "rubric": lab["rubric_ref"].str.removeprefix("v2/"), col: lab["level"].astype(int),
                                   "cell_id": lab["cell_id"], "run": r}))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=KEY + [col, "cell_id", "run"])


def prompt_chars(df: pd.DataFrame) -> pd.Series:
    """Characters of each NR cell's prompt file; within a rubric this is task length plus a constant."""
    io = Path.home() / "Developer/ADELE/judge-io"
    return pd.Series([(io / r / "prompts" / f"{c}.txt").stat().st_size if (io / r / "prompts" / f"{c}.txt").exists()
                      else np.nan for r, c in zip(df["run"], df["cell_id"])], index=df.index)


def agree(a: pd.Series, b: pd.Series) -> dict:
    ok = a.notna() & b.notna()
    a, b = a[ok].astype(int), b[ok].astype(int)
    if not len(a):
        return {"n": 0}
    lv = np.arange(6)
    o = np.zeros((6, 6))
    for x, y in zip(a, b):
        o[x, y] += 1
    w = (lv[:, None] - lv[None, :]) ** 2 / 25
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    kappa = 1 - (w * o).sum() / (w * e).sum() if (w * e).sum() else float("nan")
    return {"n": int(len(a)), "exact": round(float((a == b).mean()), 3),
            "within1": round(float(((a - b).abs() <= 1).mean()), 3), "qwk": round(float(kappa), 3),
            "mean_shift": round(float((a - b).mean()), 3)}


def crit(g: pd.DataFrame, col: str) -> float | None:
    x = g.dropna(subset=[col, "outcome"])
    if not len(x) or x[col].nunique() < 2:
        return None
    if x["set"].iloc[0] == "tau2":
        return combined(x, col, "outcome", "negative")["combined"]["rho"]
    return float(spearmanr(x[col], x["outcome"])[0])


def boot(g: pd.DataFrame, n: int = 5000, seed: int = 0) -> list[float]:
    rng, out = np.random.default_rng(seed), []
    g = g.dropna(subset=["nr", "released", "outcome"]).reset_index(drop=True)
    for _ in range(n):
        s = g.iloc[rng.integers(0, len(g), len(g))]
        a, b = crit(s, "nr"), crit(s, "released")
        if a is not None and b is not None:
            out.append(a - b)
    return [round(float(v), 3) for v in np.percentile(out, [2.5, 97.5])] if out else []


def main() -> None:
    sets = sorted(set(pd.read_csv(BENCH / "pls-relabel/subset.csv")["benchmark"])) + ["eqbench4", "cooperbench", "gamearena"]
    # Released labels as release.current_labels builds them, plus the social sets' own relabel-v2 runs, which the
    # releases do not include (amendment 3). relabel-v3 overrides take precedence, as in current_labels.
    social = {"relabel-v2-social": ["relabel-v2-eqbench4", "relabel-v2-cooperbench", "relabel-v2-gamearena"]}
    rel = pd.concat([release._read(release.OVERRIDE, sets, DIMS), release._read(release.BASE, sets, DIMS),
                     release._read(social, sets, DIMS)]).drop_duplicates(KEY, keep="first")
    rel = rel[KEY + ["level"]].rename(columns={"level": "released"})
    rel["rubric"] = rel["rubric"].str.removeprefix("v2/")
    nr = run_labels(["noreason-pl", "noreason-ms", "noreason-ms-rest", "noreason-long", "noreason-eqbench4",
                     "noreason-cooperbench", "noreason-gamearena"], "nr")
    ref = run_labels(["noreason-ref", "noreason-ref-ms"], "ref")[KEY + ["ref"]]
    df = nr.merge(rel, on=KEY, how="left").merge(ref, on=KEY, how="left").merge(outcomes(), on=["benchmark",
                                                                                               "instance_id"], how="left")
    df["set"] = np.where(df["benchmark"].isin(TAU2), "tau2", df["benchmark"])
    df["chars"] = prompt_chars(df)
    out = {"n_nr": len(nr), "n_ref": len(ref), "agreement": {}, "yardstick": {}, "criterion": {}, "levels": {},
           "length": {}, "compliance": {}}

    for d, g in df.groupby("rubric"):
        out["agreement"][d] = agree(g["nr"], g["released"])
        sub = g[g["ref"].notna()]
        out["yardstick"][d] = {"ref_vs_released": agree(sub["ref"], sub["released"]),
                               "nr_vs_released": agree(sub["nr"], sub["released"]), "nr_vs_ref": agree(sub["nr"], sub["ref"])}
        out["levels"][d] = {c: {str(int(k)): int(v) for k, v in g[c].value_counts().sort_index().items()}
                            for c in ("nr", "released")}
    for (s, d), g in df.groupby(["set", "rubric"]):
        out["criterion"][f"{s}/{d}"] = {"n": int(g["outcome"].notna().sum()), "nr": crit(g, "nr"),
                                        "released": crit(g, "released")}
        if (s, d) in SIGNAL:
            out["criterion"][f"{s}/{d}"]["diff_ci95"] = boot(g)
        x = g.dropna(subset=["chars"])
        out["length"][f"{s}/{d}"] = {c: (round(float(spearmanr(x[c], x["chars"])[0]), 3)
                                         if x[c].nunique() > 1 else None) for c in ("nr", "released")}

    bare = re.compile(r"^\s*[0-5]\s*$")
    io = Path.home() / "Developer/ADELE/judge-io"
    resp = [(io / r / "responses/opus-low" / f"{c}.txt") for r, c in zip(nr["run"], nr["cell_id"])]
    texts = [p.read_text(errors="ignore") for p in resp if p.exists()]
    out["compliance"] = {"answers": len(texts), "bare_sentence": round(sum(bool(bare.match(t)) for t in texts)
                                                                       / max(1, len(texts)), 3),
                         "median_chars": float(np.median([len(t) for t in texts])) if texts else None}

    # Decision rule (PREREGISTRATION.md)
    worse = [k for k in ("swe-bench-verified/PLp", "programbench/PLp", "tau2/PLp")
             if out["criterion"].get(k, {}).get("nr") is not None
             and abs(out["criterion"][k]["nr"]) <= abs(out["criterion"][k]["released"]) - 0.10]
    close = all(out["criterion"].get(k, {}).get("nr") is not None
                and abs(out["criterion"][k]["nr"]) >= abs(out["criterion"][k]["released"]) - 0.05
                for k in ("swe-bench-verified/PLp", "programbench/PLp", "tau2/PLp"))
    gaps = {d: round(out["yardstick"][d]["nr_vs_released"].get("exact", np.nan)
                     - out["yardstick"][d]["ref_vs_released"].get("exact", np.nan), 3)
            for d in ("PLp", "PLe", "PLs") if d in out["yardstick"]}
    big = [d for d, v in gaps.items() if v <= -0.10]
    small = len(gaps) == 3 and all(v > -0.05 for v in gaps.values())
    verdict = ("reasoning matters" if len(worse) >= 2 or len(big) >= 2
               else "reasoning not needed" if close and small else "mixed")
    out["decision"] = {"signal_cells_weaker_by_0.10": worse, "agreement_gaps": gaps, "verdict": verdict}

    (HERE / "results").mkdir(parents=True, exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("n_nr", "n_ref", "decision", "compliance")}, indent=2))
    for k in ("swe-bench-verified/PLp", "programbench/PLp", "tau2/PLp"):
        print(k, out["criterion"].get(k))
    for d, y in out["yardstick"].items():
        print(d, "agreement with released:", out["agreement"][d], "| yardstick:", y)


if __name__ == "__main__":
    main()
