"""Phase B analysis of spv-v2 (decision rules in phaseB/PREREGISTRATION_B.md).

Reads labels/spv2-b/labels_long.csv (from collect.py; only answers written by claude-opus-5-5 count).

    python experiments/benchmarks/spv-v2/analysis/analyse_b.py
"""

from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parents[1]
SWEEPS = ["size", "contrast", "blur", "noise"]


def med(s: pd.Series) -> int:
    v = sorted(int(x) for x in s)
    return v[(len(v) - 1) // 2]


def main() -> None:
    p = HERE / "labels/spv2-b/labels_long.csv"
    d = pd.read_csv(p)
    d = d[(d.writer_model == "claude-opus-5-5") & d.valid]
    idx = pd.read_csv(HERE / "labels/spv2-b/prompts_index.csv")[["file_id", "family", "step"]]
    d = d.merge(idx, on="file_id")
    d["level"] = d.level.astype(int)

    print("MEDIANS PER STIMULUS (codes 0 and 1; steps 0-4), labels in brackets")
    for arm in ("cur", "cand", "cand_key"):
        print(f"\n[{arm}]")
        for fam in SWEEPS + ["occlusion", "overlay", "views", "trap"]:
            sub = d[(d.arm == arm) & (d.family == fam)]
            if sub.empty:
                continue
            g = sub.groupby("item_id")["level"].agg([med, lambda s: "".join(map(str, s))])
            print(f"  {fam:9} " + "  ".join(f"{i.split('-', 1)[1]}:{r.iloc[0]}({r.iloc[1]})" for i, r in g.iterrows()))

    print("\nSPEARMAN rho(step, level), all labels")
    rho = {}
    for arm in ("cur", "cand", "cand_key"):
        row = []
        for fam in SWEEPS + ["occlusion", "overlay"]:
            sub = d[(d.arm == arm) & (d.family == fam)]
            r = spearmanr(sub.step, sub.level).statistic if sub.level.nunique() > 1 else float("nan")
            rho[(arm, fam)] = r
            row.append(f"{fam} {r:+.2f}")
        pooled = d[(d.arm == arm) & d.family.isin(SWEEPS)]
        rho[(arm, "pooled")] = spearmanr(pooled.step, pooled.level).statistic
        print(f"  {arm:8} pooled {rho[(arm, 'pooled')]:+.2f} | " + " | ".join(row))

    m = d.groupby(["arm", "item_id", "family", "step"])["level"].agg(med).reset_index()
    c = m[m.arm == "cand"].set_index("item_id")
    b1 = rho[("cand", "pooled")] >= 0.6
    b2 = all(rho[("cand", f)] >= 0.5 for f in SWEEPS)
    occ = c[c.family == "occlusion"]
    b3 = (occ[occ.step == 0].level <= 1).all() and (occ[occ.step >= 2].level >= 3).all()
    ov = c[c.family == "overlay"]
    b4 = (ov[ov.step == 0].level <= 1).all() and ov[ov.step >= 1].level.isin([2, 3]).all()
    b5 = (c[c.family == "views"].level == 4).all()
    b6 = (c[c.family == "trap"].level <= 1).all()
    pm = d[(d.item_id == "P-meter")].level
    b7 = med(pm) == 3
    print(f"\nP-meter labels: {''.join(map(str, pm))}")

    k = m[m.arm.isin(["cand", "cand_key"])].pivot_table(index="item_id", columns="arm", values="level")
    agree = (k.cand == k.cand_key).mean()
    print(f"key vs no key (cand), same median: {agree:.0%} of {len(k)}; "
          f"key higher on {(k.cand_key > k.cand).sum()}, lower on {(k.cand_key < k.cand).sum()}")
    for name, ok in [("B1 pooled rho >= 0.6", b1), ("B2 each sweep rho >= 0.5", b2), ("B3 occlusion", b3),
                     ("B4 overlay", b4), ("B5 views at 4", b5), ("B6 traps <= 1", b6), ("B7 meter at 3", b7)]:
        print(f"  {name}: {'holds' if ok else 'FAILS'}")
    print(f"\nVERDICT: {'PASS' if all([b1, b2, b3, b4, b5, b6, b7]) else 'FAIL'}"
          + ("" if b1 else "  (B1 is the kill rule: the driver does not track severity on images)"))


if __name__ == "__main__":
    main()
