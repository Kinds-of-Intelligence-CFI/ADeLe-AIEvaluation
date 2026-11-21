"""Amendment 1 of frontierswe-pl: PLp on the 15 never-solved tasks. Writes results/dropped.json.

Labels: PLp from runs frontierswe-pl (19 clean tasks) and frontierswe-pl-dropped (15 dropped); only valid answers
written by claude-opus-5-5 count.
  primary      PLp levels on the dropped tasks; count at PLp >= 4, read by the pre-registered rule:
               >= 5 the clean-set rule hides the top of the scale; <= 1 it does not; 2-4 inconclusive
  secondary    share at PLp >= 4, dropped against kept (Fisher exact, one-sided: dropped higher);
               PLp against mean_reward on all 34 tasks (Spearman, predicted negative)

    python experiments/benchmarks/frontierswe-pl/analysis/dropped.py
"""

import importlib.util
import json
from pathlib import Path

import pandas as pd
from scipy.stats import fisher_exact

HERE = Path(__file__).resolve().parents[1]
BENCH = HERE.parent
MODEL = "claude-opus-5-5"
RUNS = [BENCH / f"mass-annotation/runs/{r}/labels.csv" for r in ("frontierswe-pl", "frontierswe-pl-dropped")]

_spec = importlib.util.spec_from_file_location("swepl_analyse", BENCH / "swebench-pl/analysis/analyse.py")
_swepl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_swepl)
rho = _swepl.rho


def main() -> None:
    tasks = pd.read_csv(HERE / "tasks.csv").set_index("instance_id")
    lab = pd.concat(pd.read_csv(r, dtype={"instance_id": str}) for r in RUNS)
    lab = lab[lab["valid"].astype(bool) & lab["writer_model"].astype(str).str.startswith(MODEL)
              & (lab["rubric_ref"] == "v2/PLp")]
    assert not lab["instance_id"].duplicated().any()
    df = tasks.join(lab.set_index("instance_id")["level"].rename("PLp"))
    drop, kept = df[~df["keep"]], df[df["keep"]]
    high = int((drop["PLp"] >= 4).sum())
    verdict = "hides the top" if high >= 5 else "does not hide the top" if high <= 1 else "inconclusive"
    table = [[high, int((drop["PLp"] < 4).sum())], [int((kept["PLp"] >= 4).sum()), int((kept["PLp"] < 4).sum())]]
    all34 = df.dropna(subset=["PLp"])
    out = {"n": {"dropped": int(len(drop)), "kept": int(len(kept))},
           "unlabelled": sorted(df.index[df["PLp"].isna()]),
           "levels": {k: {int(v): int(c) for v, c in g["PLp"].value_counts().sort_index().items()}
                      for k, g in (("dropped", drop), ("kept", kept))},
           "dropped_by_task": drop["PLp"].dropna().astype(int).to_dict(),
           "primary": {"dropped_at_4_or_higher": high, "clean_set_rule": verdict},
           "fisher_dropped_vs_kept_at_4": {"table": table,
                                           "p_one_sided": float(f"{fisher_exact(table, 'greater')[1]:.3g}")},
           "PLp_vs_mean_reward_all": rho(all34["PLp"], all34["mean_reward"], "negative")}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results/dropped.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
