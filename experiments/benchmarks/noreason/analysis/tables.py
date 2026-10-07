"""Cost-vs-precision tables for RESULTS.md, from results/arms.json (arms.py) and results/cost.csv (cost.py).
Writes results/tables.md and prints it. Run arms.py and cost.py first.

    python experiments/benchmarks/noreason/analysis/tables.py
"""

import json
from pathlib import Path

import pandas as pd

RES = Path(__file__).resolve().parents[1] / "results"
ARMS = {"R'": "Opus 5.5 low, reasoning", "NR": "Opus 5.5 low, bare digit", "SNR": "Sonnet 5.5 low, bare digit",
        "SR": "Sonnet 5.5 low, reasoning"}
RUBRICS = ["PLp", "PLe", "PLs", "MSm", "MSc"]
SIGNAL = ["swe-bench-verified/PLp", "programbench/PLp", "tau2/PLp"]


def f(x, d=2):
    return "—" if x is None or x != x else f"{x:.{d}f}"


def main() -> None:
    arms = json.loads((RES / "arms.json").read_text())
    cost = pd.read_csv(RES / "cost.csv").set_index("arm")
    out = []

    # 1. Cost vs precision, one row per arm. Agreement and cost on the reference subset (same cells for every arm).
    out += ["### Cost vs precision (reference subset: 150 tasks × PL, 40 tau2 tasks × MS)", "",
            "| arm | judge | $/label (harness) | s/call | $/label (API, batch) | coverage | "
            + " | ".join(f"{d} exact" for d in RUBRICS) + " | " + " | ".join(f"ρ {k.split('/')[0]}" for k in SIGNAL)
            + " |", "|" + "---|" * (6 + len(RUBRICS) + len(SIGNAL))]
    sub = arms["subset_vs_released"]
    for a, judge in ARMS.items():
        m = f"{a} (matched cells)"
        usd = cost.loc[m, "harness_usd_per_label"] if m in cost.index else None
        sec = cost.loc[m, "median_seconds_per_call"] if m in cost.index else None
        api = cost.loc[a, "api_batch_usd_per_label"] if a in cost.index else None
        cov = arms["coverage"][a]["share"]
        agr = [f(sub.get(d, {}).get(a, {}).get("exact")) for d in RUBRICS]
        rho = [f(arms["criterion"].get(k, {}).get(a)) if a != "R'" else "—" for k in SIGNAL]
        out.append(f"| {a} | {judge} | {f(usd, 4)} | {f(sec, 1)} | {f(api, 4)} | {f(cov, 3)} | "
                   + " | ".join(agr) + " | " + " | ".join(rho) + " |")
    rel = [f(arms["criterion"].get(k, {}).get("released")) for k in SIGNAL]
    out += [f"| released | Opus 5.5 low, reasoning (relabel-v2/v3) | — | — | — | — | "
            + " | ".join(["(target)"] * len(RUBRICS)) + " | " + " | ".join(rel) + " |", ""]

    # 2. All cells: agreement with the released labels (exact, mean shift).
    allv = arms["all_vs_released"]
    out += ["### All cells: agreement with the released labels (exact / mean shift)", "",
            "| rubric | n (NR) | NR | SNR | SR | SNR vs NR | SR vs SNR |", "|---|---|---|---|---|---|---|"]
    for d in RUBRICS:
        g = allv.get(d, {})
        cell = lambda k: (f"{f(g[k].get('exact'))} / {f(g[k].get('mean_shift'))}" if g.get(k, {}).get("n") else "—")
        out.append(f"| {d} | {g.get('NR', {}).get('n', '—')} | {cell('NR')} | {cell('SNR')} | {cell('SR')} | "
                   f"{cell('SNR|NR')} | {cell('SR|SNR')} |")
    out.append("")

    # 3. Criterion validity on all tasks, with bootstrap CIs.
    out += ["### Criterion validity: Spearman ρ of level with outcome (all tasks)", "",
            "| cell | n | released | NR | SNR | SR | SNR − released (95% CI) | SR − released (95% CI) |",
            "|---|---|---|---|---|---|---|---|"]
    for k in SIGNAL:
        c = arms["criterion"].get(k, {})
        ci = lambda key: "[" + ", ".join(f(v) for v in c[key]) + "]" if c.get(key) else "—"
        out.append(f"| {k} | {c.get('n', '—')} | {f(c.get('released'))} | {f(c.get('NR'))} | {f(c.get('SNR'))} | "
                   f"{f(c.get('SR'))} | {ci('SNR-released_ci95')} | {ci('SR-released_ci95')} |")
    out.append("")

    # 4. Decision rules.
    out += ["### Decision rules (amendments 4 and 4b)", ""]
    for a in ("snr", "sr"):
        d = arms.get(f"{a}_decision")
        if d:
            gaps = ", ".join(f"{k} {v * 100:+.0f}" for k, v in d["agreement_gaps"].items() if v == v)
            out.append(f"- **{a.upper()}**: {d['verdict_before_cost']} before cost. Agreement gaps against the "
                       f"yardstick (points): {gaps or '—'}. Signal cells close: {len(d['signal_close'])}; weaker by "
                       f"0.10: {len(d['signal_weaker_0.10'])}. Coverage {f(d['coverage'], 3)}.")
    text = "\n".join(out) + "\n"
    (RES / "tables.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
