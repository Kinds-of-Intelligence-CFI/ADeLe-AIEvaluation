"""tie-rule-freeze (README.md): every freeze rule, re-run without the tie rule.

    python experiments/benchmarks/tie-rule-freeze/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
MC = BENCH / "ms-candidate"


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gv = load("gv_analyse", BENCH / "goal-visible/analysis/analyse.py")
t2 = load("t2goal_analyse", BENCH / "tau2-goal/analysis/analyse.py")
v4a = load("v4a", MC / "analysis/analyse_v4.py")
an, reg = v4a.an, v4a.reg


def shift(new: pd.DataFrame, old: pd.DataFrame, keys: list) -> dict:
    m = new.merge(old, on=keys, suffixes=("_nt", "_tie"))
    d = m["level_nt"] - m["level_tie"]
    return {"n": int(len(m)), "exact": round(float((d == 0).mean()), 3), "mean_shift": round(float(d.mean()), 3),
            "up": round(float((d > 0).mean()), 3), "down": round(float((d < 0).mean()), 3)}


def pl() -> dict:
    sub = pd.read_csv(HERE / "subset_goal.csv", dtype={"instance_id": str})
    nt = gv.run_labels(["notie-pl-goal"], gv.PL)
    tie = gv.run_labels(["goal-visible", "goal-visible-long"], gv.PL)
    out = {"PL1_labelled": f"{len(nt)} of {len(sub) * 3}",
           "PL1_missing": sub.merge(nt, how="left").query("level.isna()", engine="python")[
               ["benchmark", "instance_id"]].drop_duplicates().to_dict("records") if len(nt) < len(sub) * 3 else [],
           "shift": {d: shift(nt[nt.demand == d], tie[tie.demand == d], ["benchmark", "instance_id", "demand"])
                     for d in gv.PL}, "rho": {}}
    oc = gv.outcomes()
    for name, lab in (("notie", nt), ("tie", tie)):
        wide = lab.pivot_table(index=["benchmark", "instance_id"], columns="demand", values="level").reset_index()
        wide = sub.merge(wide, how="left").merge(oc, how="left")
        for b, g in wide.groupby("benchmark"):
            for d in gv.PL:
                h = g.dropna(subset=[d, "outcome"])
                out["rho"][f"{name}/{b}/{d}"] = ({"n": int(len(h)), "note": "one level"} if h[d].nunique() < 2
                                                 else gv.rho(h[d], h["outcome"], "negative"))
    r = out["rho"]
    swe = r["notie/swe-bench-verified/PLp"]
    out["PL2_holds"] = bool(swe["rho"] < 0 and swe["p_two_sided"] < 0.05)
    wrong = [k for k, v in r.items() if k.startswith("notie/") and v.get("rho", 0) > 0 and v.get("p_two_sided", 1) < 0.05]
    out["PL3_wrong_direction"], out["PL3_holds"] = wrong, not wrong
    hum = pd.read_csv(BENCH / "tau2-tb4-pl/human-labels/unblinded.csv", dtype={"instance_id": str})
    hum = hum.dropna(subset=["pablo_level"])
    tb = lambda lab: lab[(lab.benchmark == "terminal-bench-4.0.0") & (lab.demand == "PLp")].set_index("instance_id")["level"]  # noqa: E731
    h = hum.assign(notie=hum.instance_id.map(tb(nt)), tie=hum.instance_id.map(tb(tie))).dropna(subset=["notie", "tie"])
    out["human_tb_plp"] = {"n": int(len(h)), **{c: {"exact": int((h[c] == h.pablo_level).sum()),
                           "within_1": int(((h[c] - h.pablo_level).abs() <= 1).sum())} for c in ("tie", "notie")}}
    return out


def msc_tau2() -> dict:
    def labs(runs):
        parts = []
        for run in runs:
            lab = pd.read_csv(BENCH / f"mass-annotation/runs/{run}/labels.csv", dtype={"instance_id": str})
            lab = lab[lab.valid.astype(bool) & lab.writer_model.astype(str).str.startswith("claude-opus-5-5")]
            parts.append(lab[lab.rubric_ref == "v2/MSc"][["benchmark", "instance_id", "level"]])
        return pd.concat(parts)
    nt, tie = labs(["notie-msc-tau2"]), labs(["tau2-goal", "tau2-goal-long"])
    oc = t2.outcomes()
    out = {"labelled": int(len(nt)), "shift": shift(nt, tie, ["benchmark", "instance_id"])}
    for name, lab in (("notie", nt), ("tie", tie)):
        h = lab.merge(oc, on=["benchmark", "instance_id"]).dropna(subset=["level", "outcome"])
        out[f"rho_{name}"] = t2.combined(h, "level", "outcome", "negative")["combined"]
        df = lab.assign(rubric="MSc").rename(columns={"level": "new"})
        for c in ("released", "full"):
            df[c] = df["new"]
        out[f"human_tau2_{name}"] = t2.human(df)["new"]
    v = out["rho_notie"]
    out["T1_holds"] = bool(v["rho"] < 0 and v["p_two_sided"] < 0.05)
    return out


def lab() -> dict:
    nt = pd.read_csv(HERE / "labels_lab.csv")
    nt = nt[nt.valid.astype(bool) & nt.writer_model.astype(str).str.startswith(reg.OPUS)]

    def med(df, rubric, passes=("p1",)):
        g = df[(df.rubric == rubric) & df["pass"].isin(passes)]
        return {i: reg.lower_median([int(x) for x in s["level"]]) for i, s in g.groupby("item_id")}

    def tie_med(run, arm, rubric):
        parts = [pd.read_csv(MC / f"labels/{run}/labels_long.csv"),
                 pd.read_csv(BENCH.parents[1] / f"data/annotations/{run}/sealed_H.csv")]
        g = pd.concat(parts)
        g = g[(g.arm == arm) & (g.rubric == rubric) & g.valid.astype(bool) & g.writer_model.astype(str).str.startswith(reg.OPUS)]
        return {i: reg.lower_median([int(x) for x in s["level"]]) for i, s in g.groupby("item_id")}

    out = {}
    items = an.r_items()
    for rubric, run, arm in (("MSc", "mscand-nr-v4b", "v4b_nr"), ("MSm", "mscand-nr", "msm_cand_nr")):
        it = items[items.rubric == rubric]
        t, n1 = tie_med(run, arm, rubric), med(nt, rubric)
        n12 = {**n1, **med(nt, rubric, ("p2",))}
        names = an.RUBRIC_CHECKS[rubric]
        c_t, c_1 = reg.evaluate(it, reg.resolve(it, t)), reg.evaluate(it, reg.resolve(it, n1))
        lost = [n for n in names if c_t[n]["holds"] and not c_1[n]["holds"]]
        c_2 = reg.evaluate(it, reg.resolve(it, n12))
        confirmed = [n for n in lost if not c_2[n]["holds"]]
        pending = sorted({i for n in lost for i in c_1[n]["failing"]} - set(med(nt, rubric, ("p2",))))
        shared = [i for i in t if i in n1 and not i.startswith("H-")]
        out[rubric] = {"R_lost_pass1": lost, "R_confirmed": confirmed, "R_pass2_items": pending,
                       "R_holds": not confirmed and not pending,
                       "shift": {"n": len(shared), "exact": round(sum(t[i] == n1[i] for i in shared) / len(shared), 3),
                                 "mean_shift": round(sum(n1[i] - t[i] for i in shared) / len(shared), 3)}}
        if rubric == "MSc":
            out["MSc"]["M"] = v4a.rule_m(n1)
            pablo = pd.read_csv(MC / "human_labels.csv").set_index("item_id")["msc"].astype(int).to_dict()
            h_t = {k: t.get(f"{k}-full-on-MSc") for k in pablo}
            h_n = {k: n1.get(f"{k}-full-on-MSc") for k in pablo}
            exact_t = sum(h_t[k] == v for k, v in pablo.items())
            exact_n = sum(h_n[k] == v for k, v in pablo.items())
            h2 = [k for k, v in pablo.items() if h_n[k] is not None and abs(h_n[k] - v) >= 2 and abs(h_t[k] - v) <= 1]
            out["MSc"].update({"H1_exact": {"tie": exact_t, "notie": exact_n}, "H1_holds": exact_n >= 12,
                               "H2_items": h2, "H2_holds": not h2,
                               "H_items": {k: [v, h_t[k], h_n[k]] for k, v in pablo.items()}})
    return out


def main() -> None:
    out = {}
    for name, fn in (("PL", pl), ("MSc_tau2", msc_tau2), ("lab", lab)):
        try:
            out[name] = fn()
        except FileNotFoundError as e:
            out[name] = {"pending": str(e)}
    pl_ok = out["PL"].get("PL2_holds") and out["PL"].get("PL3_holds")
    lab_ = out.get("lab", {})
    msc_ok = all(lab_.get("MSc", {}).get(k) for k in ("R_holds", "H1_holds", "H2_holds")) and \
        lab_.get("MSc", {}).get("M", {}).get("holds") and out["MSc_tau2"].get("T1_holds")
    msm_ok = lab_.get("MSm", {}).get("R_holds")
    out["verdict"] = {"PL stays frozen": bool(pl_ok), "MSc stays frozen": bool(msc_ok), "MSm stays frozen": bool(msm_ok)}
    (HERE / "results.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps(out, indent=1, default=str)[:12000])


if __name__ == "__main__":
    main()
