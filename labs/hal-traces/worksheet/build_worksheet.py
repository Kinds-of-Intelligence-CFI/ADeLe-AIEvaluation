"""Build the two-phase human worksheet from items.csv + collected judge reasoning.

Phase 1 (worksheet_blind.md): 38 items in randomized order, judge labels hidden.
  Fill answers.csv (order, custom_id, dim, your_level) — do NOT open the reveal
  file until done.
Phase 2 (worksheet_reveal.md): same items with the three judges' recorded labels
  and Sonnet/Opus justifications. Fill the agree/disagree + deciding-clause
  columns in answers.csv.

Then run score_worksheet.py.
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
items = pd.read_csv(HERE / "items.csv").sort_values("order")
cot = pd.read_csv(HERE / "cot.csv").set_index(["custom_id", "dim", "model"])

RUB = HERE / "../../../src/adele/rubrics/data_v2/Paolo_Pablo"
DIMF = {"PLp": "PLp - Planning", "PLe": "PLe - Action control and execution"}

blind, reveal = [], []
blind.append(
    "# Trace-checkpoint worksheet — Phase 1 (BLIND)\n\n"
    "For each item, read the frame and assign a demand level 0-5 for the named "
    "dimension, using the rubric at the bottom of this file. The TASK you score "
    "is: complete the original task correctly, starting from the situation shown. "
    "The situation is what the environment's observations establish; the agent's "
    "own claims are hypotheses. Record your level in answers.csv. "
    "Do not open worksheet_reveal.md until you have finished all 38.\n"
)
reveal.append(
    "# Trace-checkpoint worksheet — Phase 2 (REVEAL)\n\n"
    "For each item: the three judges' recorded labels and the Sonnet/Opus "
    "justifications. Mark in answers.csv: verdict (agree_sonnet / agree_opus / "
    "both_wrong / control_ok) and deciding_clause (which rubric condition "
    "settles it, in your words).\n"
)
for r in items.itertuples():
    head = f"\n---\n\n## Item {r.order:02d}  [{DIMF[r.dim]}]\n\n"
    blind.append(head + r.prompt + "\n")
    rev = head
    rev += f"*({r.kind}; recorded labels — haiku: {int(r.haiku)}, sonnet: {int(r.sonnet)}, opus: {int(r.opus)})*\n\n"
    for m in ("sonnet", "opus"):
        try:
            row = cot.loc[(r.custom_id, r.dim, m)]
            flip = "" if int(row.level) == int(getattr(r, m)) else f" (fresh label {int(row.level)} differs from recorded {int(getattr(r, m))})"
            rev += f"**{m}**{flip}: {row.justification}\n\n"
        except KeyError:
            rev += f"**{m}**: (justification missing)\n\n"
    reveal.append(rev)

for dim in ("PLp", "PLe"):
    blind.append(f"\n---\n\n# {DIMF[dim]} RUBRIC\n\n" + (RUB / f"{dim}.txt").read_text())

(HERE / "worksheet_blind.md").write_text("".join(blind))
(HERE / "worksheet_reveal.md").write_text("".join(reveal))
ans = items[["order", "custom_id", "dim"]].copy()
ans["your_level"] = ""
ans["verdict"] = ""
ans["deciding_clause"] = ""
ans.to_csv(HERE / "answers.csv", index=False)
print("wrote worksheet_blind.md, worksheet_reveal.md, answers.csv")
