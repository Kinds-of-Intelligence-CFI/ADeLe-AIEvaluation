"""Pre-registered analysis of jev-pilot. Writes results/analysis.json.

Jev labels: labels/jev_labels.csv (run_jev.py), first-pass rows with status ok. Opus labels (Opus 5.5 low, valid answers
written by claude-opus-5-5): PLp, PLe and PLs from each agentic study's release/labels_wide.csv; MSm and MSc from the
ms-benchmarks runs; the social sets from their mass runs. Per rubric, pooled and per set: exact and within-one
agreement, quadratic weighted kappa, mean signed difference (Jev - Opus), level counts. Agentic sets: Spearman of
each rubric with the set's primary outcome, Jev and Opus (ms-benchmarks' outcomes, swebench-pl's `rho`, tau2-tb4-pl's
`combined` within domain). Also: MS separation, confidence vs agreement, repeat determinism, skips. Amendment 1:
probability on Opus's level and log loss, calibration, the expected level against outcomes, and a seeded sample of
disagreements for reading Opus's reasons.

    python experiments/benchmarks/jev-pilot/analysis/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
DIMS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
MODEL = "claude-opus-5-5"
RELEASES = {"swe-bench-verified": "swebench-clean", "terminal-bench-4.0.0": "tb4-clean",
            "terminal-bench-science-0.1": "tbsci-pl", "deepswe-v1.1": "deepswe-clean", "frontierswe-v2": "frontierswe-pl",
            "programbench": "programbench-pl", "tau2": "tau2-clean"}
TAU2 = ["tau2-airline", "tau2-retail", "tau2-banking_knowledge"]
CODING = ["swe-bench-verified", "deepswe-v1.1", "programbench", "frontierswe-v2"]


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rho = load("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py").rho
combined = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py").combined
outcomes = load("msb_analyse", BENCH / "ms-benchmarks/analysis/analyse.py").outcomes


def run_labels(*runs: str) -> pd.DataFrame:
    parts = []
    for r in runs:
        lab = pd.read_csv(BENCH / f"mass-annotation/runs/{r}/labels.csv", dtype={"instance_id": str})
        lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)]
        parts.append(lab.assign(rubric=lab["rubric_ref"].str.removeprefix("v2/"))[
            ["benchmark", "instance_id", "rubric", "level"]])
    return pd.concat(parts)


def opus_labels() -> pd.DataFrame:
    parts = []
    for bench, study in RELEASES.items():
        w = pd.read_csv(BENCH / study / "release/labels_wide.csv", dtype={"instance_id": str})
        if "keep" in w:
            w = w[w["keep"].astype(bool)]
        if bench != "tau2":
            w = w.assign(benchmark=bench)
        for d in ("PLp", "PLe", "PLs"):
            parts.append(w[["benchmark", "instance_id", f"v2/{d}"]].rename(columns={f"v2/{d}": "level"})
                         .assign(rubric=d).dropna(subset=["level"]))
    ms = run_labels("ms-benchmarks", "ms-benchmarks-long")
    parts.append(ms[ms["rubric"].isin(["MSm", "MSc"])])
    parts.append(run_labels("eqbench4-plms", "cooperbench-plms", "gamearena-plms"))
    out = pd.concat(parts)
    out["level"] = out["level"].astype(int)
    assert not out.duplicated(["benchmark", "instance_id", "rubric"]).any()
    return out.rename(columns={"level": "opus"})


def qwk(a: pd.Series, b: pd.Series, k: int = 6) -> float | None:
    if len(a) < 2:
        return None
    o = np.zeros((k, k))
    for x, y in zip(a.astype(int), b.astype(int)):
        o[x, y] += 1
    w = np.array([[(i - j) ** 2 for j in range(k)] for i in range(k)]) / (k - 1) ** 2
    e = np.outer(o.sum(1), o.sum(0)) / o.sum()
    den = (w * e).sum()
    return round(float(1 - (w * o).sum() / den), 3) if den else None


def agree(g: pd.DataFrame) -> dict:
    d = g["jev"] - g["opus"]
    return {"n": int(len(g)), "exact": round(float((d == 0).mean()), 3), "within_one": round(float((d.abs() <= 1).mean()), 3),
            "qwk": qwk(g["jev"], g["opus"]), "mean_diff": round(float(d.mean()), 3),
            "jev_levels": {str(k): int(v) for k, v in g["jev"].value_counts().sort_index().items()},
            "opus_levels": {str(k): int(v) for k, v in g["opus"].value_counts().sort_index().items()}}


def main() -> None:
    jev = pd.read_csv(HERE / "labels/jev_labels.csv", dtype={"instance_id": str})
    first = jev[jev["repeat"] == 1]
    out = {"skipped": first[first["status"] != "ok"].drop_duplicates(["benchmark", "instance_id"])
           [["benchmark", "instance_id", "status"]].to_dict("records")}
    ok = first[first["status"] == "ok"].rename(columns={"level": "jev"})
    ok["jev"] = ok["jev"].astype(int)
    df = ok.merge(opus_labels(), on=["benchmark", "instance_id", "rubric"], how="inner")
    df["set"] = np.where(df["benchmark"].isin(TAU2), "tau2", df["benchmark"])
    out["n_compared"] = int(len(df))

    out["pooled"] = {d: agree(df[df["rubric"] == d]) for d in DIMS}
    out["by_group"] = {f"{grp}/{d}": agree(g) for (grp, d), g in df.groupby(["group", "rubric"])}
    out["by_set"] = {f"{s}/{d}": agree(g) for (s, d), g in df.groupby(["set", "rubric"])}
    cod = df[df["benchmark"].isin(CODING) & (df["rubric"] == "PLs")]
    out["pls_coding_mean_diff"] = round(float((cod["jev"] - cod["opus"]).mean()), 3)

    msc = df[df["rubric"] == "MSc"]
    single = msc[msc["group"] == "agentic"]
    out["ms_separation"] = {"jev_mean_MSc_single_agent": round(float(single["jev"].mean()), 2),
                            "opus_mean_MSc_single_agent": round(float(single["opus"].mean()), 2),
                            **{f"jev_mean_MSc_{s}": round(float(g["jev"].mean()), 2) for s, g in
                               [("eqbench4", msc[msc["benchmark"] == "eqbench4"]),
                                ("cooperbench_coop", msc[msc["instance_id"].str.endswith("@coop")]),
                                ("cooperbench_solo", msc[msc["instance_id"].str.endswith("@solo")]),
                                ("gamearena", msc[msc["benchmark"] == "gamearena"])]}}

    oc = outcomes()
    ag = df[df["group"] == "agentic"].merge(oc, on=["benchmark", "instance_id"], how="left")
    out["criterion"] = {}
    for (s, d), g in ag.groupby(["set", "rubric"]):
        res = {}
        for who in ("jev", "expected", "opus"):
            h = g.dropna(subset=[who, "outcome"])
            if s == "tau2":
                res[who] = combined(h, who, "outcome", "negative")["combined"]
            elif h[who].nunique() < 2:
                res[who] = {"n": int(len(h)), "note": "one level: not testable"}
            else:
                res[who] = rho(h[who], h["outcome"], "negative")
        out["criterion"][f"{s}/{d}"] = res

    # amendment 1
    p_opus = df.apply(lambda r: r[f"p{r['opus']}"], axis=1)
    df["p_opus"] = p_opus
    out["prob_on_opus"] = {d: {"mean": round(float(g["p_opus"].mean()), 3),
                               "log_loss": round(float(-np.log(g["p_opus"].clip(lower=0.01)).mean()), 3)}
                           for d, g in df.groupby("rubric")}
    cal = pd.concat([pd.DataFrame({"p": df[f"p{k}"], "hit": (df["opus"] == k).astype(int)}) for k in range(6)])
    cal["bin"] = (cal["p"].clip(upper=0.999) * 10).astype(int) / 10
    out["calibration"] = {f"{b:.1f}": {"n": int(len(g)), "opus_share": round(float(g["hit"].mean()), 3),
                                       "mean_p": round(float(g["p"].mean()), 3)} for b, g in cal.groupby("bin")}
    dis = df[df["jev"] != df["opus"]].assign(gap=lambda t: (t["jev"] - t["opus"]).abs())
    sample = pd.concat([g.sort_values("gap", ascending=False).head(40).sample(min(8, len(g)), random_state=20261004)
                        for _, g in dis.groupby("rubric")])
    out["diagnosis_sample"] = sample[["benchmark", "instance_id", "rubric", "jev", "opus", "confidence"]].to_dict("records")

    hit = (df["jev"] == df["opus"]).astype(int)
    r, p = spearmanr(df["confidence"], hit)
    out["confidence_vs_exact"] = {"rho": round(float(r), 3), "p": float(f"{p:.3g}"), "n": int(len(df))}

    rep = jev[jev["status"] == "ok"].pivot_table(index=["benchmark", "instance_id", "rubric"], columns="repeat",
                                                  values="level").dropna()
    out["repeat_identical"] = {"n": int(len(rep)), "share": round(float((rep[1] == rep[2]).mean()), 3) if len(rep) else None}
    out["input_tokens"] = int(jev.drop_duplicates(["spec", "benchmark", "instance_id", "repeat"])["input_tokens"].sum())
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/analysis.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(json.dumps({k: out[k] for k in ("n_compared", "pooled", "ms_separation", "confidence_vs_exact",
                                          "repeat_identical", "input_tokens")}, indent=1, default=str))


if __name__ == "__main__":
    main()
