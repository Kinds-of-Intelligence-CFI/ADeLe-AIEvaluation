"""MSc and MSm candidates of 2026-10-17 (Pablo: MSc on one driver, in MSm's style; MSm as close to v1 MS as possible).

MSc_candidate.txt = src MSc.txt with a new intro, new level statements and one reworded example. The driver is what the
task needs from the other party; every other line, including all other examples and the "does not cover" paragraph,
is unchanged.
MSm_candidate.txt = src MSm.txt with three edits back toward data_v1/MSm.txt:
  1. the v1 intro restored (the 2026-08-25 rewording rested on a false claim that no other v1 file opens this way;
     AS and QLq do);
  2. the "does not cover" Note gains the sincerity condition ("unless the task gives reason to doubt it");
  3. the Level 4 stated-stance passage is removed, since the Note already says it; Level 4 is v1 word for word.
Level 2 (truth-teller routing) and Level 5 (interlock rule) keep their v2 text: both change labels and were tested.

The script checks that nothing else differs. Nothing in src/ changes.

    uv run python experiments/benchmarks/ms-candidate/make_candidates.py
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SRC = ROOT / "src/adele/rubrics/data_v2/Paolo_Pablo"
V1 = ROOT / "src/adele/rubrics/data_v1/MSm.txt"

MSC_INTRO = (
    "This rubric assesses the difficulty level of tasks requiring an interaction to be steered. Steering covers choosing "
    "what to say so that another party comes to understand, accept or do what the task needs from them. It ranges from "
    "tasks that need nothing from anyone to those in which several parties in conflict must be brought along together.")
MSC_LEVELS = {
    0: "Level 0: None. The task does not require communication, or needs nothing from another party.",
    1: "Level 1: Very low. The task requires communication that a familiar script covers, or a message sent with no "
       "reply to adapt to. Nothing that is said depends on how the other party responds.",
    2: "Level 2: Low. The task requires a cooperative exchange to be guided. What to say next depends on what the other "
       "party has just said, but nothing they want stands against what the task needs from them.",
    3: "Level 3: Intermediate. The task requires someone to be won over. They do not yet accept what the task needs from "
       "them, and each doubt or objection they raise sets the next move. However, they are open to being persuaded.",
    4: "Level 4: High. The task requires an exchange to be steered against opposition. The other party pursues an outcome "
       "that conflicts with what the task needs from them, so each move must answer their counter-moves as they push "
       "back.",
    5: "Level 5: Very high. The task requires several parties in conflict to be brought along together. What the task "
       "needs from each cannot all be had at once, and every move toward one is felt by the others. Critically, if what "
       "the task needs from them is compatible, the task belongs below, however many parties there are.",
}
REFUND_OLD = ("* Keep refusing a refund the policy does not allow to a customer who is shouting and demanding a manager, "
              "without conceding it and without the exchange breaking down.")
REFUND_NEW = ("* Refuse a refund the policy does not allow to a customer who is shouting for it, and keep them talking "
              "until they accept the store credit it does offer.")

MSM_NOTE_OLD = ("Note, a stance the other party has stated outright, together with their reasons, does not have to be "
                "modelled, since the inferring has already been done.")
MSM_NOTE_NEW = ("Note, a stance the other party has stated outright, together with their reasons, does not have to be "
                "modelled unless the task gives reason to doubt it.")


def msc() -> str:
    lines = (SRC / "MSc.txt").read_text(encoding="utf-8").split("\n")
    out, changed = [], 0
    for i, line in enumerate(lines):
        if i == 2:
            assert line.startswith("This rubric assesses"), line
            out.append(MSC_INTRO)
            changed += 1
        elif line.startswith("Level "):
            out.append(MSC_LEVELS[int(line[6])])
            changed += 1
        elif line == REFUND_OLD:
            out.append(REFUND_NEW)
            changed += 1
        else:
            out.append(line)
    assert changed == 8, changed  # intro + 6 levels + 1 example
    return "\n".join(out)


def msm() -> str:
    text = (SRC / "MSm.txt").read_text(encoding="utf-8")
    v1 = V1.read_text(encoding="utf-8").split("\n")
    lines = text.split("\n")
    assert lines[2].startswith("This rubric assesses") and v1[2].startswith("This criterion assesses")
    lines[2] = v1[2]
    text = "\n".join(lines)
    assert text.count(MSM_NOTE_OLD) == 1
    text = text.replace(MSM_NOTE_OLD, MSM_NOTE_NEW)
    l4 = next(i for i, l in enumerate(text.split("\n")) if l.startswith("Level 4:"))
    v1_l4 = next(l for l in v1 if l.startswith("Level 4:")).rstrip()
    cur = text.split("\n")
    assert cur[l4].startswith(v1_l4 + " Critically, a stance the other party has stated outright"), cur[l4][:200]
    cur[l4] = v1_l4
    return "\n".join(cur)


# v2 (amendment 2): Level 4 and the refund example reworded after v1 failed rule M (judges read "conflicts with what
# the task needs" as conflict with the task's outcome, and cited the refund example for every refusal).
MSC_L4_V2 = ("Level 4: High. The task requires someone to be brought round against their will. It cannot succeed unless "
             "they accept or do something they are working against, so each move must answer their counter-moves as they "
             "push back.")
REFUND_V2 = "* Bring a customer who is shouting for a refund the policy does not allow to accept the store credit it does offer."


def msc_v2() -> str:
    v1 = msc()
    assert v1.count(MSC_LEVELS[4]) == 1 and v1.count(REFUND_NEW) == 1
    return v1.replace(MSC_LEVELS[4], MSC_L4_V2).replace(REFUND_NEW, REFUND_V2)


def main() -> None:
    for name, body in (("MSc_candidate.txt", msc()), ("MSm_candidate.txt", msm()), ("MSc_candidate_v2.txt", msc_v2())):
        (HERE / name).write_text(body, encoding="utf-8")
        src = SRC / (name.split("_")[0] + ".txt")
        print(f"{name}: {len(body.split())} words (src {len(src.read_text().split())})")


if __name__ == "__main__":
    main()
