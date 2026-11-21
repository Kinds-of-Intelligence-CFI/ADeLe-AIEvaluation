"""Pre-registered analysis of o-odds (PREREGISTRATION.md, amendment 5; exploratory). Writes results/o_odds.json.

Each answer ends "Such a plan comes out workable about one time in: N". Only answers written by claude-opus-5-5
count (labels/o-odds/writers.csv). The estimate is log2 N, compared with the states' search bits and crossings left
(rivercross-v2 frames/search_truth.csv). Bits are a proxy: they count non-undo random sequences, not O's agent.
  Q1  Spearman of log2 N with bits at least 0.5
  Q2  OLS log2 N ~ bits + ctg (standardised, HC3): bits coefficient > 0 with p < 0.05, and larger than ctg's

    python experiments/benchmarks/plp-b2/analysis/odds_o.py
"""

import json
import math
import re
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

from analyse import ols

HERE = Path(__file__).resolve().parents[1]
RC = HERE.parent / "rivercross-v2"
PATTERN = re.compile(r"one time in:\s*\**\s*([\d,]+)", re.IGNORECASE)


def main() -> None:
    run = json.loads((HERE / "labels/o-odds/run.json").read_text())
    io = HERE.parents[2] / run["judge_io"] / "responses/opus-low"
    writers = pd.read_csv(HERE / "labels/o-odds/writers.csv").set_index("file_id")["writer_model"]
    est, unparsed = {}, []
    for f in sorted(io.glob("*@PLp.txt")):
        sid = f.name.split("@")[0]
        m = PATTERN.findall(f.read_text(encoding="utf-8"))
        if not str(writers.get(sid, "")).startswith("claude-opus-5-5"):
            continue
        if not m:
            unparsed.append(sid)
            continue
        est[sid] = math.log2(max(1, int(m[-1].replace(",", ""))))
    truth = pd.read_csv(RC / "frames/search_truth.csv").set_index("custom_id")
    d = truth.join(pd.Series(est, name="log2_odds")).dropna(subset=["log2_odds"])
    rho_b, p_b = spearmanr(d["log2_odds"], d["bits"])
    rho_c, p_c = spearmanr(d["log2_odds"], d["ctg"])
    model = ols(d["log2_odds"], d[["bits", "ctg"]])
    checks = {"Q1_rho_bits_ge_0.5": bool(rho_b >= 0.5),
              "Q2_bits_sig_and_above_ctg": bool(model["bits"]["coef"] > 0 and model["bits"]["p"] < 0.05
                                                and model["bits"]["coef"] > model["ctg"]["coef"])}
    out = {"n": int(len(d)), "unparsed": unparsed,
           "rho_bits": {"rho": round(float(rho_b), 3), "p": float(f"{p_b:.3g}")},
           "rho_ctg": {"rho": round(float(rho_c), 3), "p": float(f"{p_c:.3g}")},
           "model": model, "checks": checks,
           "descriptive": {"log2_odds_by_cell": {r: {c: float(v) for c, v in row.items()} for r, row in
                                                 d.groupby(["ctg_bin", "bits_band"])["log2_odds"].mean().round(2)
                                                 .unstack().iterrows()},
                           "odds_quantiles": {q: round(2 ** float(d["log2_odds"].quantile(q)), 1)
                                              for q in (0.1, 0.5, 0.9)}}}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/o_odds.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
