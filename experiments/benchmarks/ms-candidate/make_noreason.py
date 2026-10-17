"""Amendment 6: the frozen candidates judged without reasoning (bare digit), run mscand-nr.

Production annotates with the bare-digit prompt (build_annotation_prompt_v2_noreason). Every prompt of MSc v4
(mscand-v4) and of the MSm candidate (mscand-1, arm candidate, rubric MSm) is turned into its bare-digit twin by the
exact substitution that defines PROMPT_V2_NOREASON: the instruction paragraph is swapped and the closing sentence
dropped. Rubric and task text stay byte-identical. Same judge (adele-judge-v2-low), three repeats.

    uv run --extra annotate python experiments/benchmarks/ms-candidate/make_noreason.py
"""

import importlib.util
import random
from pathlib import Path

import pandas as pd

from adele.annotation import prompts as P

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("cand_prompts", HERE / "make_prompts.py")
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)
mp = cp.mp
RUN = "mscand-nr"
INSTR_R = P.PROMPT_V2.split("Before giving a level, ")[1].split("\nThe level of {demand}")[0]
INSTR_R = "Before giving a level, " + INSTR_R
INSTR_NR = P.PROMPT_V2_NOREASON.split("not any particular solver's attempt at it.\n\n")[1]
NAMES = {"MSc": "Communication and social interaction", "MSm": "Mind Modelling and Social Cognition"}


def to_noreason(prompt: str, rubric: str) -> str:
    closing = f"\nThe level of {NAMES[rubric]} demanded by this task is: N"
    assert prompt.count(INSTR_R) == 1 and prompt.endswith(closing), "not a v2 reasoning prompt"
    out = prompt.replace(INSTR_R, INSTR_NR).removesuffix(closing)
    assert out.endswith("as a single digit from 0 to 5, and nothing else.") and "is: N" not in out
    return out


def main() -> None:
    sources = [("mscand-v4", "MSc", "candidate_v4", "v4_nr"), ("mscand-1", "MSm", "candidate", "msm_cand_nr")]
    cells = []
    for run, rubric, arm, new_arm in sources:
        idx = pd.read_csv(HERE / f"labels/{run}/prompts_index.csv")
        idx = idx[(idx["rubric"] == rubric) & (idx["arm"] == arm)]
        for r in idx.itertuples(index=False):
            p = (cp.JUDGE_IO / run / "prompts" / f"{r.file_id}@{rubric}.txt").read_text(encoding="utf-8")
            assert mp.sha256(p.encode("utf-8")) == r.prompt_sha256
            q = to_noreason(p, rubric)
            cells.append({"item_id": r.item_id, "set": r.set, "arm": new_arm, "rubric": rubric,
                          "prompt_sha256": mp.sha256(q.encode("utf-8")), "source_run": run,
                          "source_file_id": r.file_id, "prompt": q})
    rng = random.Random(cp.SEED + 6)
    rng.shuffle(cells)
    taken = set()
    for f in cp.ROOT.glob("experiments/benchmarks/*/labels/*/prompts_index.csv"):
        idx = pd.read_csv(f)
        if "file_id" in idx:
            taken |= set(idx["file_id"].astype(str))
    for c, i in zip(cells, mp.opaque_ids(len(cells), rng, taken)):
        c["file_id"] = i
    cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
    cp.RUN = RUN
    cp.write_run(cells, {"pass": 1, "amendment": 6, "answer_format": "bare digit (PROMPT_V2_NOREASON substitution)",
                         "sources": {"MSc": "mscand-v4 candidate_v4", "MSm": "mscand-1 candidate"}})
    print(pd.DataFrame(cells).groupby(["rubric", "set"]).size().to_string())


if __name__ == "__main__":
    main()
