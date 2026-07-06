"""Score the filled answers.csv against the recorded judge labels.

Reports, separately for disagreement items and controls:
  - blind human level vs each judge (exact / within-1)
  - boundary tiebreaks: on Sonnet-Opus splits, whom the blind human sided with
  - phase-2 endorsement rates and the clauses named in disagreements
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
a = pd.read_csv(HERE / "answers.csv")
items = pd.read_csv(HERE / "items.csv")
df = a.merge(items, on=["order", "custom_id", "dim"])
df = df[df.your_level.notna() & (df.your_level.astype(str) != "")]
df["your_level"] = df.your_level.astype(int)
print(f"scored {len(df)} of {len(a)} items\n")

for kind, sub in df.groupby("kind"):
    print(f"== {kind} (n={len(sub)}) ==")
    for m in ("haiku", "sonnet", "opus"):
        d = (sub.your_level - sub[m]).abs()
        print(f"  vs {m:7s} exact={(d == 0).mean():.2f} within-1={(d <= 1).mean():.2f}")

dis = df[df.kind == "disagreement"]
if len(dis):
    side_s = (dis.your_level == dis.sonnet).sum()
    side_o = (dis.your_level == dis.opus).sum()
    other = len(dis) - side_s - side_o
    print(f"\nboundary tiebreaks (n={len(dis)}): sided with sonnet {side_s}, "
          f"with opus {side_o}, with neither {other}")
    for dim, s in dis.groupby("dim"):
        print(f"  {dim}: sonnet {(s.your_level == s.sonnet).sum()}, "
              f"opus {(s.your_level == s.opus).sum()}, "
              f"neither {(s.your_level != s.sonnet).sum() - (s.your_level == s.opus).sum() + 0}")
if df.verdict.astype(str).str.strip().any():
    print("\nphase-2 verdicts:", df.verdict.value_counts().to_dict())
    named = df[df.deciding_clause.astype(str).str.strip() != ""]
    if len(named):
        print("deciding clauses named on", len(named), "items — see answers.csv")
