"""Amendment 4/4a/4b analysis: every judge arm against the released labels and against each other. Writes results/arms.json.

Arms (PREREGISTRATION.md, amendments 4, 4a and 4b):
    R'      Opus 5.5 low, written reasoning (v2)       noreason-ref, noreason-ref-ms             (reference subset)
    NR      Opus 5.5 low, no reasoning (v2-noreason)   noreason-{pl,ms,ms-rest,long,...}          (all cells)
    SNR     Sonnet 5.5 low, no reasoning               noreason-s-{pl,ms,ms-rest,long,...}        (all cells)
    SR      Sonnet 5.5 low, written reasoning (v2)     noreason-sr-{pl,ms,ms-rest,long,...}       (all cells)
Only valid answers written by the arm's requested model count. Incomplete runs are analysed as far as they go.

    python experiments/benchmarks/noreason/analysis/arms.py
"""

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

import analyse as A  # same folder: agreement, criterion, bootstrap and the released labels' construction

NR_SETS = ["pl", "ms", "ms-rest", "long", "eqbench4", "cooperbench", "gamearena"]
ARMS = {
    "R'": (["noreason-ref", "noreason-ref-ms"], "claude-opus-5-5"),
    "NR": ([f"noreason-{s}" for s in NR_SETS], "claude-opus-5-5"),
    "SNR": ([f"noreason-s-{s}" for s in NR_SETS], "claude-sonnet-5-5"),
    "SR": ([f"noreason-sr-{s}" for s in NR_SETS], "claude-sonnet-5-5"),
}
FULL = ["NR", "SNR", "SR"]  # arms that cover every cell
DECIDE = {"SNR": ARMS["SNR"], "SR": (["noreason-sr-pl", "noreason-sr-ms"], "claude-sonnet-5-5")}  # 4b: PL and tau2 MS
PL = ["PLp", "PLe", "PLs"]
SIGNAL = ["swe-bench-verified/PLp", "programbench/PLp", "tau2/PLp"]


def labels(runs: list[str], model: str, col: str) -> pd.DataFrame:
    parts = []
    for r in runs:
        p = A.RUNS / r / "labels.csv"
        if not p.exists():
            continue
        lab = pd.read_csv(p, dtype={"instance_id": str})
        lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(model)]
        parts.append(pd.DataFrame({"benchmark": lab["benchmark"], "instance_id": lab["instance_id"],
                                   "rubric": lab["rubric_ref"].str.removeprefix("v2/"), col: lab["level"].astype(int),
                                   f"{col}_cell": lab["cell_id"], f"{col}_run": r}))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=A.KEY + [col])


def coverage(runs: list[str], model: str) -> dict:
    """Cells pinned, cells with a label by the requested model, and rejected attempts by reason."""
    pinned = labelled = 0
    reasons: dict[str, int] = {}
    for r in runs:
        d = A.RUNS / r
        if not (d / "cells.csv").exists():
            continue
        pinned += len(pd.read_csv(d / "cells.csv"))
        if (d / "labels.csv").exists():
            lab = pd.read_csv(d / "labels.csv")
            labelled += int((lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(model)).sum())
        if (d / "ledger.csv").exists():
            led = pd.read_csv(d / "ledger.csv")
            for k, v in led.loc[led["status"] == "rejected", "reason"].value_counts().items():
                reasons[k] = reasons.get(k, 0) + int(v)
    return {"pinned": pinned, "labelled": labelled, "share": round(labelled / pinned, 3) if pinned else None,
            "rejected_attempts": reasons}


def released() -> pd.DataFrame:
    sets = sorted(set(pd.read_csv(A.BENCH / "pls-relabel/subset.csv")["benchmark"])) + ["eqbench4", "cooperbench",
                                                                                        "gamearena"]
    social = {"relabel-v2-social": ["relabel-v2-eqbench4", "relabel-v2-cooperbench", "relabel-v2-gamearena"]}
    rel = pd.concat([A.release._read(A.release.OVERRIDE, sets, A.DIMS), A.release._read(A.release.BASE, sets, A.DIMS),
                     A.release._read(social, sets, A.DIMS)]).drop_duplicates(A.KEY, keep="first")
    rel = rel[A.KEY + ["level"]].rename(columns={"level": "released"})
    rel["rubric"] = rel["rubric"].str.removeprefix("v2/")
    return rel


def boot_diff(g: pd.DataFrame, a: str, b: str, n: int = 5000, seed: int = 0) -> list[float]:
    rng, out = np.random.default_rng(seed), []
    g = g.dropna(subset=[a, b, "outcome"]).reset_index(drop=True)
    for _ in range(n):
        s = g.iloc[rng.integers(0, len(g), len(g))]
        x, y = A.crit(s, a), A.crit(s, b)
        if x is not None and y is not None:
            out.append(x - y)
    return [round(float(v), 3) for v in np.percentile(out, [2.5, 97.5])] if out else []


def main() -> None:
    df = released()
    for arm, (runs, model) in ARMS.items():
        df = df.merge(labels(runs, model, arm), on=A.KEY, how="outer")
    df = df.merge(A.outcomes(), on=["benchmark", "instance_id"], how="left")
    df["set"] = np.where(df["benchmark"].isin(A.TAU2), "tau2", df["benchmark"])
    cols = ["released"] + list(ARMS)
    out: dict = {"coverage": {arm: coverage(*ARMS[arm]) for arm in ARMS}}

    # 1. Reference subset: the cells R' labelled. Every pair of arms, per rubric.
    ref = df[df["R'"].notna()]
    out["subset_pairs"] = {d: {f"{a}|{b}": A.agree(g[a], g[b]) for i, a in enumerate(cols) for b in cols[i + 1:]}
                           for d, g in ref.groupby("rubric")}
    out["subset_vs_released"] = {d: {a: A.agree(g[a], g["released"]) for a in ARMS} for d, g in ref.groupby("rubric")}
    out["subset_criterion"] = {f"{s}/{d}": {a: A.crit(g, a) for a in cols} | {"n": int(g["outcome"].notna().sum())}
                               for (s, d), g in ref.groupby(["set", "rubric"]) if d == "PLp"}

    # 2. All cells: SNR and NR against the released labels and against each other; criterion validity; levels.
    out["all_vs_released"] = {d: {a: A.agree(g[a], g["released"]) for a in FULL}
                              | {f"{a}|{b}": A.agree(g[a], g[b]) for a, b in (("SNR", "NR"), ("SR", "SNR"), ("SR", "NR"))}
                              for d, g in df.groupby("rubric")}
    out["criterion"] = {}
    for (s, d), g in df.groupby(["set", "rubric"]):
        k = f"{s}/{d}"
        out["criterion"][k] = {a: A.crit(g, a) for a in ["released"] + FULL} | {"n": int(g["outcome"].notna().sum())}
        if k in SIGNAL:
            for a, b in (("SNR", "released"), ("SNR", "NR"), ("SR", "released"), ("SR", "SNR")):
                out["criterion"][k][f"{a}-{b}_ci95"] = boot_diff(g, a, b)
    out["levels"] = {d: {a: {str(int(k)): int(v) for k, v in g[a].value_counts().sort_index().items()} for a in cols}
                     for d, g in df.groupby("rubric")}

    # 3. Compliance of the no-reasoning arms (bare digit) and of the reasoning arms (answer length).
    io = Path.home() / "Developer/ADELE/judge-io"
    bare = re.compile(r"^\s*[0-5]\s*$")
    out["answers"] = {}
    for arm, (runs, model) in ARMS.items():
        texts = [p.read_text(errors="ignore") for r in runs for p in (io / r / "responses").glob("*/*.txt")]
        out["answers"][arm] = {"n": len(texts), "bare_digit": round(sum(bool(bare.match(t)) for t in texts)
                                                                    / max(1, len(texts)), 3),
                               "median_chars": float(np.median([len(t) for t in texts])) if texts else None}

    # 4. Decision rules for SNR (amendment 4) and SR (4b, on PL and tau2 MS). Cost condition (iv) comes from cost.py.
    ys = out["subset_vs_released"]
    for arm, (runs, model) in DECIDE.items():
        gap = {d: round(ys[d][arm].get("exact", np.nan) - ys[d]["R'"].get("exact", np.nan), 3) for d in PL if d in ys}
        rho = {k: (out["criterion"].get(k, {}).get(arm), out["criterion"].get(k, {}).get("released")) for k in SIGNAL}
        close = [k for k, (a, b) in rho.items() if a is not None and abs(a) >= abs(b) - 0.05]
        weak = [k for k, (a, b) in rho.items() if a is not None and abs(a) <= abs(b) - 0.10]
        cov = coverage(runs, model)["share"] or 0
        usable_wo_cost = (len(gap) == 3 and all(v >= -0.05 for v in gap.values()) and len(close) >= 2
                          and not weak and cov >= 0.95)
        not_usable = sum(v <= -0.10 for v in gap.values()) >= 2 or len(weak) >= 2 or cov < 0.90
        out[f"{arm.lower()}_decision"] = {"agreement_gaps": gap, "signal_close": close, "signal_weaker_0.10": weak,
                                          "coverage": cov, "verdict_before_cost": "not usable" if not_usable else
                                          "usable if cost condition holds" if usable_wo_cost else "mixed"}

    (A.HERE / "results").mkdir(parents=True, exist_ok=True)
    (A.HERE / "results/arms.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(json.dumps({k: out[k] for k in ("coverage", "snr_decision", "sr_decision", "answers")}, indent=1))
    for d in PL + ["MSm", "MSc"]:
        if d in ys:
            print(d, {a: (v.get("n"), v.get("exact"), v.get("mean_shift")) for a, v in ys[d].items()})
    for k in SIGNAL:
        print(k, out["criterion"].get(k))


if __name__ == "__main__":
    main()
