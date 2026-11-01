"""Amendment 6 analysis: the frozen candidates without reasoning (mscand-nr) against the same texts with reasoning.

Reasoning labels: MSc v4 from mscand-v4 (and pass 2 mscand-v4-2), MSm candidate from mscand-1 (and mscand-2). Set H sealed.
  N1  every R check that holds with reasoning also holds without (pass 2 for losses: mscand-nr-2, bare digit)
  N2  M-refusal holds without reasoning (MSc)
  N3  per rubric, on the R and M items: bare-digit medians equal the reasoning medians on at least 80%, and are within
      one level on at least 97%

    uv run python experiments/benchmarks/ms-candidate/analysis/analyse_nr.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("v4a", HERE / "analysis/analyse_v4.py")
v4a = importlib.util.module_from_spec(_s)
_s.loader.exec_module(v4a)
an, reg = v4a.an, v4a.reg


def meds(path: Path, arm: str, rubric: str) -> dict[str, int]:
    if not path.exists():
        return {}
    lab = pd.read_csv(path)
    lab = lab[(lab["arm"] == arm) & (lab["rubric"] == rubric) & lab["valid"].astype(bool)
              & lab["writer_model"].astype(str).str.startswith(reg.OPUS)]
    return {i: reg.lower_median([int(x) for x in g["level"]]) for i, g in lab.groupby("item_id")}


def main() -> None:
    L = HERE / "labels"
    items = an.r_items()
    out = {}
    for dim, (r_run, r_arm), nr_arm in (("MSc", ("mscand-v4", "candidate_v4"), "v4_nr"),
                                        ("MSm", ("mscand-1", "candidate"), "msm_cand_nr")):
        it = items[items["rubric"] == dim].copy()
        if dim == "MSc":
            it = pd.concat([it, it[it["item_id"] == "P-MSc-L1-1"].assign(item_id="P-MSc-L1-atlas", text="")],
                           ignore_index=True)
        p2 = {"MSc": L / "mscand-v4-2/labels_long.csv", "MSm": L / "mscand-2/labels_long.csv"}[dim]
        r = {**meds(L / f"{r_run}/labels_long.csv", r_arm, dim), **meds(p2, r_arm, dim)}
        nr = meds(L / "mscand-nr/labels_long.csv", nr_arm, dim)
        nr2 = {**nr, **meds(L / "mscand-nr-2/labels_long.csv", nr_arm, dim)}
        names = an.RUBRIC_CHECKS[dim]
        c_r = reg.evaluate(it, reg.resolve(it, r))
        c_nr = reg.evaluate(it, reg.resolve(it, nr))
        lost = [n for n in names if c_r[n]["holds"] and not c_nr[n]["holds"]]
        res = {"lost_pass1": lost, "rerun": sorted({i for n in lost for i in c_nr[n]["failing"] + c_nr[n]["unlabelled"]})}
        if lost and nr2 != nr:
            c2 = reg.evaluate(it, reg.resolve(it, nr2))
            res["confirmed"] = [n for n in lost if not c2[n]["holds"]]
        res["N1"] = "holds" if not lost else ("pending pass 2" if "confirmed" not in res else
                                              ("fails" if res["confirmed"] else "holds"))
        shared = [i for i in r if i in nr and not i.startswith("H-")]
        exact = sum(r[i] == nr[i] for i in shared) / len(shared)
        within = sum(abs(r[i] - nr[i]) <= 1 for i in shared) / len(shared)
        res["N3"] = {"n": len(shared), "exact": round(exact, 3), "within_1": round(within, 3),
                     "holds": exact >= 0.80 and within >= 0.97,
                     "differ": {i: {"reasoning": r[i], "bare": nr[i]} for i in shared if r[i] != nr[i]}}
        if dim == "MSc":
            res["N2"] = v4a.rule_m(nr)
        out[dim] = res
    out["H"] = "sealed"
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/results_nr.json").write_text(json.dumps(out, indent=2, default=str) + "\n")
    for dim in ("MSc", "MSm"):
        r = out[dim]
        print(f"{dim}: N1 {r['N1']} (lost {r['lost_pass1']}) | N3 exact {r['N3']['exact']} within1 {r['N3']['within_1']} "
              f"-> {r['N3']['holds']} | differ {r['N3']['differ']}")
    m = out["MSc"]["N2"]
    print(f"MSc N2: refusal B<=3 {m['B_at_3_or_less']}/5, A-B within 1 {m['A_B_within_1']}/5 -> {m['holds']}; "
          f"needed B 4+ {m['needed_B_at_4_plus']}/3")


if __name__ == "__main__":
    main()
