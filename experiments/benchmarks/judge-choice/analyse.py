"""judge-choice (README.md): the pre-registered rules for each candidate judge, and the prompt change on Opus.

    python experiments/benchmarks/judge-choice/analyse.py
"""

import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

from adele.mass.collect import is_requested
from adele.mass.pin import RUNS_ROOT, load_run

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
sys.path.insert(0, str(HERE))
from make_sample import GOAL, SOCIAL, STATIC, TAU2  # noqa: E402


def load(name, path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


combined = load("t2_analyse", BENCH / "tau2-tb4-pl/analysis/analyse.py").combined
outcomes = load("msb_analyse", BENCH / "ms-benchmarks/analysis/analyse.py").outcomes
v4a = load("v4a", BENCH / "ms-candidate/analysis/analyse_v4.py")
an, reg = v4a.an, v4a.reg

ARMS = ["opus-low", "sonnet-low", "haiku-low", "haiku-medium"]
CANDIDATES = ARMS[1:]
GROUP = {**{b: "coding" for b in GOAL}, **{b: "tau2" for b in TAU2}, **{b: "social" for b in SOCIAL},
         **{b: "static" for b in STATIC}}
BAR = {"PL": 0.85, "MS": 0.85, "v1": 0.80, "memory": 0.80}


def family(ref: str) -> str:
    code = ref.split("/")[1]
    return "PL" if code in ("PLp", "PLe") else "MS" if code in ("MSc", "MSm") else \
        "memory" if code.startswith("MM") else "v1"


def task_labels() -> tuple[pd.DataFrame, dict]:
    """Valid labels by the requested model, every run of every arm; and pinned cells per arm and family."""
    parts, pinned = [], {}
    for d in sorted(RUNS_ROOT.glob("jc-*")):
        run = load_run(d)
        arm = next(a for a in ARMS if d.name.endswith(a))
        for ref, n in run.cells.groupby("rubric_ref").size().items():
            pinned[(arm, family(ref))] = pinned.get((arm, family(ref)), 0) + int(n)
        lab = pd.read_csv(d / "labels.csv", dtype={"instance_id": str})
        lab = lab[lab["valid"] & lab["writer_model"].map(lambda w: is_requested(str(w), run.judge.model))]
        parts.append(lab.assign(arm=arm, key=lab["benchmark"] + "|" + lab["instance_id"] + "|" + lab["rubric_ref"],
                                group=lab["benchmark"].map(GROUP))[["arm", "key", "benchmark", "instance_id",
                                                                    "rubric_ref", "group", "level"]])
    df = pd.concat(parts)
    return df.assign(family=df["rubric_ref"].map(family)), pinned


def lab_labels() -> pd.DataFrame:
    lab = pd.read_csv(HERE / "labels_lab.csv")
    lab = lab[lab["valid"].astype(bool) & (lab["writer_model"].astype(str) == lab["model_requested"])]
    return lab.assign(key="lab|" + lab["item_id"] + "|" + lab["rubric"], group="lab", benchmark="lab",
                      instance_id=lab["item_id"], rubric_ref="v2/" + lab["rubric"], family="MS")[
        ["arm", "key", "benchmark", "instance_id", "rubric_ref", "group", "level", "family"]]


def agree(c: pd.DataFrame, o: pd.DataFrame) -> dict:
    m = c.merge(o[["key", "level"]], on="key", suffixes=("", "_opus"))
    d = m["level"] - m["level_opus"]
    by_group = {g: round(float((x["level"] == x["level_opus"]).mean()), 3) for g, x in m.groupby("group")}
    return {"n": int(len(m)), "exact": round(float((d == 0).mean()), 3), "within_1": round(float((d.abs() <= 1).mean()), 3),
            "shift": round(float(d.mean()), 3), "exact_by_group": by_group}


def link(df: pd.DataFrame, arm: str, ref: str, benches: list) -> dict:
    x = df[(df["arm"] == arm) & (df["rubric_ref"] == ref) & df["benchmark"].isin(benches)]
    x = x.merge(outcomes(), on=["benchmark", "instance_id"], how="left")
    r = combined(x.rename(columns={"level": "lv"}), "lv", "outcome", "negative")["combined"]
    return r if isinstance(r, dict) else {"note": r}


def human(df: pd.DataFrame, lab: pd.DataFrame, arm: str) -> dict:
    hum = pd.read_csv(BENCH / "tau2-tb4-pl/human-labels/unblinded.csv", dtype=str).dropna(subset=["pablo_level"])
    tb = df[(df["arm"] == arm) & (df["rubric_ref"] == "v2/PLp") & (df["benchmark"] == "terminal-bench-4.0.0")]
    tb = hum.merge(tb, on="instance_id")
    pablo = pd.read_csv(BENCH / "ms-candidate/human_labels.csv")
    pablo_full = pablo.set_index("item_id")["msc"].astype(int)
    h_lab = lab[(lab["arm"] == arm) & (lab["rubric_ref"] == "v2/MSc") & lab["instance_id"].str.endswith("-full-on-MSc")]
    h_lab = h_lab.assign(item=h_lab["instance_id"].str.split("-full").str[0])
    items = pd.read_csv(BENCH / "msc-l4-note/human_items.csv", dtype=str)
    real = df[(df["arm"] == arm) & (df["rubric_ref"] == "v2/MSc")].merge(items, on=["benchmark", "instance_id"])
    real_pablo = pablo.assign(p=pablo["msc_revised"].fillna(pablo["msc"])).set_index("item_id")["p"]
    return {"tb_plp_within1": f"{int(((tb['level'] - tb['pablo_level'].astype(int)).abs() <= 1).sum())} of {len(tb)}",
            "tb_plp_exact": int((tb["level"] == tb["pablo_level"].astype(int)).sum()),
            "setH_full_exact": int((h_lab["level"].values == h_lab["item"].map(pablo_full).values).sum()),
            "setH_full_n": int(len(h_lab)),
            "setH_real_exact": int((real["level"].values == real["item_id"].map(real_pablo).values).sum()),
            "setH_real_n": int(len(real))}


def lab_checks(lab: pd.DataFrame, arm: str) -> dict:
    med = {i: int(v) for i, v in lab[(lab["arm"] == arm) & (lab["rubric_ref"] == "v2/MSc")]
           .set_index("instance_id")["level"].items()}
    m = v4a.rule_m(med)
    out = {"refusal_B_le_3": m["B_at_3_or_less"], "refusal_AB_within_1": m["A_B_within_1"], "M_holds": m["holds"]}
    items = an.r_items()
    for rubric in ("MSc", "MSm"):
        it = items[items["rubric"] == rubric]
        md = {i: int(v) for i, v in lab[(lab["arm"] == arm) & (lab["rubric_ref"] == f"v2/{rubric}")]
              .set_index("instance_id")["level"].items()}
        ev = reg.evaluate(it, reg.resolve(it, md))
        out[f"R_{rubric}_failing"] = [n for n in an.RUBRIC_CHECKS[rubric] if not ev[n]["holds"]]
    return out


def main() -> None:
    tasks, pinned = task_labels()
    lab = lab_labels()
    for arm in ARMS:
        pinned[(arm, "MS")] = pinned.get((arm, "MS"), 0) + 230
    allv = pd.concat([tasks, lab])
    opus = allv[allv["arm"] == "opus-low"]
    out = {"coverage": {}, "agreement": {}, "links": {}, "human": {}, "lab": {}, "verdict": {}}
    plp_sets, tau2 = GOAL + TAU2, TAU2
    for arm in ARMS:
        a = allv[allv["arm"] == arm]
        out["coverage"][arm] = {f: round(len(a[a["family"] == f]) / pinned[(arm, f)], 3) for f in BAR}
        out["links"][arm] = {"PLp": link(tasks, arm, "v2/PLp", plp_sets), "MSc_tau2": link(tasks, arm, "v2/MSc", tau2)}
        out["human"][arm] = human(tasks, lab, arm)
        out["lab"][arm] = lab_checks(lab, arm)
    for arm in CANDIDATES:
        a = allv[allv["arm"] == arm]
        out["agreement"][arm] = ag = {f: agree(a[a["family"] == f], opus[opus["family"] == f]) for f in BAR}
        lk, lo, h = out["links"][arm], out["links"]["opus-low"], out["human"][arm]
        d_plp = lk["PLp"].get("rho", 0) - lo["PLp"].get("rho", 0)
        d_msc = lk["MSc_tau2"].get("rho", 0) - lo["MSc_tau2"].get("rho", 0)
        v = {}
        for f in BAR:
            g = ag[f]
            rules = {"A1": g["exact"] >= BAR[f], "A2": g["within_1"] >= 0.97, "A3": abs(g["shift"]) <= 0.15,
                     "A4": all(x >= 0.70 for x in g["exact_by_group"].values()), "K": out["coverage"][arm][f] >= 0.98}
            if f == "PL":
                rules |= {"C": d_plp >= -0.10, "H": int(h["tb_plp_within1"].split()[0]) >= 5}
            if f == "MS":
                rules |= {"C": d_msc >= -0.15, "H": h["setH_full_exact"] >= 12 and h["setH_real_exact"] >= 12}
            v[f] = {"qualifies": all(rules.values()), "rules": rules}
        v["delta_links"] = {"PLp": round(d_plp, 3), "MSc_tau2": round(d_msc, 3)}
        out["verdict"][arm] = v
    out["prompt_change_opus"] = prompt_change(opus)
    (HERE / "results.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    for arm in CANDIDATES:
        print(arm, {f: out["verdict"][arm][f]["qualifies"] for f in BAR}, out["verdict"][arm]["delta_links"])
    print(json.dumps({k: out[k] for k in ("coverage", "human", "lab", "prompt_change_opus")}, indent=1, default=str)[:6000])


def prompt_change(opus: pd.DataFrame) -> dict:
    """Opus with Jose's prompt against the production Opus labels on the same cells."""
    from adele.mass.labelset import labels as ls_labels
    from adele.mass.labelset import load_labelset
    cur = ls_labels(load_labelset("current")).rename(columns={"rubric": "rubric_ref"})
    runs = ["w1v1-swe", "w1v1-tau2", "w1v1-tau2-long", "w1v1-code", "w1v1-code-long", "w1v1-code-api", "w1v1-other",
            "bulk-w1-rivercross-plms", "bulk-w2-static"]
    prod = [cur[["benchmark", "instance_id", "rubric_ref", "level"]]]
    for r in runs:
        d = pd.read_csv(RUNS_ROOT / r / "labels.csv", dtype={"instance_id": str})
        prod.append(d[d["valid"]][["benchmark", "instance_id", "rubric_ref", "level"]])
    p = pd.concat(prod).drop_duplicates(["benchmark", "instance_id", "rubric_ref"])
    m = opus.merge(p, on=["benchmark", "instance_id", "rubric_ref"], suffixes=("", "_prod"))
    out = {}
    for f, g in m.groupby("family"):
        d = g["level"] - g["level_prod"].astype(int)
        out[f] = {"n": int(len(g)), "exact": round(float((d == 0).mean()), 3), "shift": round(float(d.mean()), 3)}
    return out


if __name__ == "__main__":
    main()
