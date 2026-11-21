"""Amendment 7 analysis: MSc v4b (v4 without the Level 1 library example) against the current text and against v4.

Arms: v4b with reasoning (mscand-v4b) and bare digit (mscand-nr-v4b); v4 (mscand-v4, mscand-nr); current (mscand-1).
  R   the MSc lab checks, per v4b arm, against the current text (pass 2 runs: mscand-v4b-2, mscand-nr-v4b-2)
  M   amendment 3's refusal rule, per v4b arm; pairs 5 to 7 reported
  H   exact matches with Pablo's labels (full task and script), per arm; H2 against the current text (full task)
  N3  v4b bare digit against v4b reasoning: at least 80% exact, 97% within one
v4b replaces v4 if, under both prompts, R holds, M holds, H exact (full) is at least v4's, and H2 holds.

    uv run python experiments/benchmarks/ms-candidate/analysis/analyse_v4b.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
_s = importlib.util.spec_from_file_location("v4a", HERE / "analysis/analyse_v4.py")
v4a = importlib.util.module_from_spec(_s)
_s.loader.exec_module(v4a)
an, reg = v4a.an, v4a.reg
L = HERE / "labels"


def med(run: str, arm: str, pass2: str | None = None) -> dict:
    out = v4a.meds(L / f"{run}/labels_long.csv", arm)
    if pass2 and (L / f"{pass2}/labels_long.csv").exists():
        out.update(v4a.meds(L / f"{pass2}/labels_long.csv", arm))
    return out


def h_meds(run: str, arm: str) -> dict:
    lab = pd.read_csv(ROOT / f"data/annotations/{run}/sealed_H.csv")
    lab = lab[(lab["rubric"] == "MSc") & (lab["arm"] == arm) & lab["valid"].astype(bool)
              & lab["writer_model"].astype(str).str.startswith(reg.OPUS)]
    return {i: reg.lower_median([int(x) for x in g["level"]]) for i, g in lab.groupby("item_id")}


def main() -> None:
    items = an.r_items()
    items = items[items["rubric"] == "MSc"].copy()
    pablo = pd.read_csv(HERE / "human_labels.csv").set_index("item_id")["msc"].astype(int).to_dict()
    cur = v4a.meds(L / "mscand-1/labels_long.csv", "current")
    c_cur = reg.evaluate(items, reg.resolve(items, cur))
    h_cur = h_meds("mscand-1", "current")
    arms = {"v4b_reasoning": ("mscand-v4b", "candidate_v4b", "mscand-v4b-2"),
            "v4b_bare": ("mscand-nr-v4b", "v4b_nr", "mscand-nr-v4b-2"),
            "v4_reasoning": ("mscand-v4", "candidate_v4", "mscand-v4-2"),
            "v4_bare": ("mscand-nr", "v4_nr", "mscand-nr-2")}
    out = {}
    names = an.RUBRIC_CHECKS["MSc"]
    for name, (run, arm, p2) in arms.items():
        m1, m2 = med(run, arm), med(run, arm, p2)
        lost = [n for n in names if c_cur[n]["holds"] and not reg.evaluate(items, reg.resolve(items, m1))[n]["holds"]]
        c2 = reg.evaluate(items, reg.resolve(items, m2))
        confirmed = [n for n in lost if not c2[n]["holds"]]
        pending = sorted({i for n in lost for i in reg.evaluate(items, reg.resolve(items, m1))[n]["failing"]}
                         - set(med(p2, arm) if (L / f"{p2}/labels_long.csv").exists() else {}))
        h = h_meds(run, arm)
        exact = {inp: sum(h.get(f"{t}-{inp}-on-MSc") == v for t, v in pablo.items()) for inp in ("full", "script")}
        h2 = [t for t, v in pablo.items() if abs(h[f"{t}-full-on-MSc"] - v) >= 2 and abs(h_cur[f"{t}-full-on-MSc"] - v) <= 1]
        out[name] = {"R_lost_pass1": lost, "R_confirmed": confirmed, "R_pass2_pending": pending if lost else [],
                     "M": v4a.rule_m(m2), "H_exact": exact, "H2_items": h2,
                     "H_full": {t: h[f"{t}-full-on-MSc"] for t in pablo}}
    r, b = med(*arms["v4b_reasoning"][:2]), med(*arms["v4b_bare"][:2])
    shared = [i for i in r if i in b and not i.startswith("H-")]
    out["N3_v4b"] = {"exact": round(sum(r[i] == b[i] for i in shared) / len(shared), 3),
                     "within_1": round(sum(abs(r[i] - b[i]) <= 1 for i in shared) / len(shared), 3)}
    v4b_ok = all(not out[a]["R_confirmed"] and not out[a]["R_pass2_pending"] and out[a]["M"]["holds"]
                 and not out[a]["H2_items"] and out[a]["H_exact"]["full"] >= out[a.replace("v4b", "v4")]["H_exact"]["full"]
                 for a in ("v4b_reasoning", "v4b_bare"))
    out["verdict"] = "v4b replaces v4" if v4b_ok else "v4 stays (or pass 2 pending)"
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/results_v4b.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    out["pablo"] = pablo
    for a in arms:
        o = out[a]
        print(f"{a:14} R lost {o['R_lost_pass1']} confirmed {o['R_confirmed']} pending {o['R_pass2_pending']} | "
              f"M {o['M']['B_at_3_or_less']}/5 {o['M']['A_B_within_1']}/5 needed {o['M']['needed_B_at_4_plus']}/3 | "
              f"H exact full {o['H_exact']['full']} script {o['H_exact']['script']} | H2 {o['H2_items']}")
    print("H per item (full):", {t: [pablo[t]] + [out[a]["H_full"][t] for a in arms] for t in pablo})
    print("N3 v4b:", out["N3_v4b"], "| verdict:", out["verdict"])


if __name__ == "__main__":
    main()
