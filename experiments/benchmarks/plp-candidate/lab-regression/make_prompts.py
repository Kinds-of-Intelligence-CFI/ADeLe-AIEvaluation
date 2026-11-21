"""Build the items, the 4-gram check and the prompts of the lab regression for PLp candidate C.

See PREREGISTRATION.md. Two arms, the same items and the same judges:
  cur  the current PLp text, as the catalog loads it for production
  C    ../PLp_candidate_c.txt, which is the current text plus one sentence at the end of the
       "What this dimension does not cover" paragraph
Item sets:
  P  placement (r25): PLp's 20 example bullets, scored with every Examples block stripped
  F  examples disentangle (r34): the PLe, PLs and MSc example bullets at Levels 3 to 5, scored by PLp
  M  minimal pairs (r36): rebuilt from the round's descriptions (reconstructed_items.csv)
  D  family diagonal (r42, r43): rebuilt from the round's descriptions (reconstructed_items.csv)
  B  battery-v1: the 36 standing items, verbatim from the lab record
Every item outside P is checked for shared word 4-grams against every example bullet of the
candidate file. An item with any shared 4-gram is void and is not judged (JUDGING.md rule 4, r75).
Prompts go to ~/Developer/ADELE/judge-io/<run>/prompts/<id>@PLp.txt. The ids are opaque and the
two arms are shuffled together, so nothing in a file name tells a judge the set, level or arm.

    python experiments/benchmarks/plp-candidate/lab-regression/make_prompts.py             # pass 1
    python experiments/benchmarks/plp-candidate/lab-regression/make_prompts.py --replicate ITEM [ITEM ...]
    python experiments/benchmarks/plp-candidate/lab-regression/make_prompts.py --candidate d [--replicate ITEM ...]

Candidate D (added after C passed) is C's first clause only. It is judged alone (labreg-d1), against
the current-text labels of labreg-r1; its pass 2 is labreg-d2.
"""

import argparse
import hashlib
import io
import json
import os
import random
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
JUDGE_IO = ROOT.parents[1] / "judge-io"
LAB = "7159671"  # rubrics/v2-lab-record (on origin): battery-v1 and the r36 labels
CANDIDATE = HERE.parent / "PLp_candidate_c.txt"
AGENT = ROOT / "experiments/benchmarks/swebench-pl/adele-judge-low.md"
JUDGES = {f"{m}-low": f"Claude Code subagent 'adele-judge-low' (tools: Read, Write; omitClaudeMd; effort low), "
                      f"model alias '{m}'" for m in ("haiku", "sonnet", "opus")}
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"
SCOPE_END = "Note, such features raise this demand only insofar as they make a workable plan harder to find."
CARVE = ("Knowing the established method is knowledge rather than planning, so pitfalls that the method "
         "avoids do not raise this demand.")
# Candidate D (added after C passed): the first clause of C only.
CANDIDATE_D = HERE.parent / "PLp_candidate_d.txt"
CARVE_D = "Knowing the established method is knowledge rather than planning."
ID_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"
SEED = 20260928
# Stored PLp medians of the rebuilt items, from the round records (r36 README and labels; r42 and
# r43 results tables). They were measured on older texts and on the original item wordings.
STORED_REBUILT = {"M-A1": 1, "M-A2": 3, "M-A3": 1, "M-D1": 1, "M-D2": 3, "D-PLp1": 3, "D-PLp2": 3,
                  "D-PLp3": 3, "D-PLp4": 3, "D-PLe1": 0, "D-PLe2": 0, "D-PLe3": 1, "D-PLs1": 1, "D-PLs2": 1}


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def bullets(content: str) -> list[tuple[int, str]]:
    """(level, text) for every example bullet, in file order."""
    out, level = [], None
    for line in content.splitlines():
        m = re.match(r"Level (\d):", line)
        if m:
            level = int(m.group(1))
        elif line.startswith("* "):
            out.append((level, line[2:].strip()))
    return out


def strip_examples(content: str) -> str:
    """The rubric with every Examples block removed (the r25 placement design)."""
    kept = [l for l in content.splitlines() if l.strip() != "Examples:" and not l.startswith("* ")]
    return "\n".join(kept)


def fourgrams(text: str) -> set[tuple[str, ...]]:
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}


def build_items(plp_cur: str, plp_c: str, catalog) -> pd.DataFrame:
    rows = []
    counts = {}
    for level, text in bullets(plp_cur):
        counts[level] = counts.get(level, 0) + 1
        rows.append({"item_id": f"P-L{level}-{counts[level]}", "set": "P", "own_dim": "PLp", "target": level,
                     "family": "", "source": "PLp.txt example bullet", "text": text})
    for dim in ("PLe", "PLs", "MSc"):
        counts = {}
        for level, text in bullets(catalog[dim].content):
            counts[level] = counts.get(level, 0) + 1
            if level >= 3:
                rows.append({"item_id": f"F-{dim}-L{level}-{counts[level]}", "set": "F", "own_dim": dim,
                             "target": level, "family": "", "source": f"{dim}.txt example bullet", "text": text})
    rebuilt = pd.read_csv(HERE / "reconstructed_items.csv")
    for r in rebuilt.itertuples(index=False):
        rows.append({"item_id": r.item_id, "set": r.set, "own_dim": r.own_dim, "target": r.target, "family": "",
                     "source": f"rebuilt from {r.round}: {r.rebuilt_from}", "text": r.text,
                     "stored_median": STORED_REBUILT[r.item_id]})
    battery = pd.read_csv(io.StringIO(git("show", f"{LAB}:labs/rubric-qa/battery-v1/items.csv")))
    prereg = pd.read_csv(io.StringIO(git("show", f"{LAB}:labs/rubric-qa/battery-v1/prereg.csv"))).set_index("item_id")
    r36 = pd.read_csv(io.StringIO(git("show", f"{LAB}:labs/rubric-qa/r36/labels.csv")))
    stored = r36[r36["dim"] == "PLp"].groupby("item_id")["assigned"].median()
    for r in battery.itertuples(index=False):
        p = prereg.loc[r.item_id]
        rows.append({"item_id": f"B-{r.item_id}", "set": "B", "own_dim": "", "target": int(p["PLp"]),
                     "family": p["family"], "reg_PLe": int(p["PLe"]), "reg_PLs": int(p["PLs"]),
                     "reg_MSc": int(p["MSc"]), "source": "battery-v1 items.csv", "text": r.task,
                     "stored_median": int(stored[r.item_id])})
    items = pd.DataFrame(rows)
    # 4-gram independence against every example bullet of the candidate file.
    cand = [(lvl, i, fourgrams(t)) for i, (lvl, t) in enumerate(bullets(plp_c), 1)]
    hits, shared = [], []
    for r in items.itertuples(index=False):
        if r.set == "P":
            hits.append(None)
            shared.append("n/a: the item is a bullet of this file, and the rubric shown has no examples")
            continue
        found = [(lvl, i, sorted(fourgrams(r.text) & g)) for lvl, i, g in cand if fourgrams(r.text) & g]
        hits.append(sum(len(s) for _, _, s in found))
        shared.append("; ".join(f"bullet {i} (Level {lvl}): " + " | ".join(" ".join(g) for g in s) for lvl, i, s in found))
    items["fourgram_hits"] = hits
    items["fourgram_shared"] = shared
    items["status"] = ["void" if h else "judged" for h in items["fourgram_hits"].fillna(0)]
    return items


def write_run(run_id: str, cells: list[dict], note: dict, arms: tuple[str, ...] = ("cur", "C")) -> None:
    io_dir, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
    for d in [io_dir / "prompts", labels] + [io_dir / "responses" / j for j in JUDGES]:
        d.mkdir(parents=True, exist_ok=True)
    for c in cells:
        (io_dir / "prompts" / f"{c['file_id']}@PLp.txt").write_text(c.pop("prompt"), encoding="utf-8")
    pd.DataFrame(cells).to_csv(labels / "prompts_index.csv", index=False)
    run = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repo_commit": git("rev-parse", "HEAD").strip(),
        "repo_dirty_tracked_files": git("status", "--porcelain", "--untracked-files=no").splitlines(),
        "design": {"n_cells": len(cells), "dims": ["PLp"], "arms": list(arms), "judges": JUDGES},
        **note,
        "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt",
                   "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
        "judge_agent": {"file": str(AGENT.relative_to(ROOT)), "sha256": sha256(AGENT.read_bytes())},
        "judge_instruction": INSTRUCTION,
        "judge_instruction_sha256": sha256(INSTRUCTION.encode("utf-8")),
        "judge_io": os.path.relpath(JUDGE_IO / run_id, ROOT),
        "sampling": "harness defaults; snapshot cannot be pinned for subagents; effort is set in the agent file",
    }
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(cells)} prompts")


def opaque_ids(n: int, rng: random.Random, taken: set[str]) -> list[str]:
    out = []
    while len(out) < n:
        i = "".join(rng.choice(ID_CHARS) for _ in range(5))
        if i not in taken:
            taken.add(i)
            out.append(i)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", choices=["c", "d"], default="c",
                    help="c: both texts, run labreg-r1. d: candidate D alone, run labreg-d1 (baseline: labreg-r1)")
    ap.add_argument("--replicate", nargs="+", metavar="ITEM", help="write pass 2 (labreg-r2 or labreg-d2)")
    args = ap.parse_args()
    catalog = load_active_catalog()
    plp = catalog["PLp"]
    plp_c = CANDIDATE.read_text(encoding="utf-8")
    assert plp.content.count(SCOPE_END) == 1
    assert plp_c == plp.content.replace(SCOPE_END, f"{SCOPE_END} {CARVE}"), "candidate is not current + one sentence"
    assert bullets(plp_c) == bullets(plp.content)
    arms = {"cur": plp.content, "C": plp_c}
    note = {"rubric": {"file": str(Path(plp.file_path).relative_to(ROOT)),
                       "sha256": sha256(Path(plp.file_path).read_bytes()),
                       "candidate": "plp-candidate/PLp_candidate_c.txt",
                       "candidate_sha256": sha256(CANDIDATE.read_bytes()),
                       "inserted_after": SCOPE_END, "inserted_sentence": CARVE,
                       "set_P": "every Examples block stripped from the rubric shown (r25 design)"},
            "items": "lab-regression/items.csv", "lab_record_commit": LAB}

    if args.candidate == "d":
        plp_d = plp.content.replace(SCOPE_END, f"{SCOPE_END} {CARVE_D}")
        CANDIDATE_D.write_text(plp_d, encoding="utf-8")
        note = {**note, "rubric": {**note["rubric"], "candidate": "plp-candidate/PLp_candidate_d.txt",
                                   "candidate_sha256": sha256(plp_d.encode("utf-8")), "inserted_sentence": CARVE_D}}
        if args.replicate:  # pass 2 for D: the pass-1 prompts of both texts, under new ids
            r1 = pd.read_csv(HERE / "labels/labreg-r1/prompts_index.csv").assign(pass1_run="labreg-r1")
            d1 = pd.read_csv(HERE / "labels/labreg-d1/prompts_index.csv").assign(pass1_run="labreg-d1")
            todo = pd.concat([r1[r1["arm"] == "cur"], d1])
            todo = todo[todo["item_id"].isin(args.replicate)]
            assert set(todo["item_id"]) == set(args.replicate), "unknown item"
            taken = set(pd.concat(pd.read_csv(p) for p in HERE.glob("labels/*/prompts_index.csv"))["file_id"])
            cells = []
            for r, new in zip(todo.sample(frac=1, random_state=SEED + 12).itertuples(index=False),
                              opaque_ids(len(todo), random.Random(SEED + 12), taken)):
                prompt = (JUDGE_IO / r.pass1_run / "prompts" / f"{r.file_id}@PLp.txt").read_text(encoding="utf-8")
                assert sha256(prompt.encode("utf-8")) == r.prompt_sha256
                cells.append({"file_id": new, "item_id": r.item_id, "set": r.set, "arm": r.arm, "demand": "PLp",
                              "prompt_sha256": r.prompt_sha256, "pass1_run": r.pass1_run,
                              "pass1_file_id": r.file_id, "prompt": prompt})
            write_run("labreg-d2", cells, {**note, "pass": 2, "replicates": ["labreg-r1", "labreg-d1"]}, ("cur", "D"))
            return
        judged = pd.read_csv(HERE / "items.csv").query("status == 'judged'")
        cells = []
        for r in judged.itertuples(index=False):
            rubric = strip_examples(plp_d) if r.set == "P" else plp_d
            prompt = build_annotation_prompt(demand_name=plp.full_name, rubric_content=rubric, task_instance=r.text)
            cells.append({"item_id": r.item_id, "set": r.set, "arm": "D", "demand": "PLp",
                          "prompt_sha256": sha256(prompt.encode("utf-8")), "prompt": prompt})
        rng = random.Random(SEED + 10)
        rng.shuffle(cells)
        taken = set(pd.concat(pd.read_csv(p) for p in HERE.glob("labels/*/prompts_index.csv"))["file_id"])
        for c, i in zip(cells, opaque_ids(len(cells), rng, taken)):
            c["file_id"] = i
        cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
        write_run("labreg-d1", cells, {**note, "pass": 1, "baseline": "labreg-r1, arm cur"}, ("D",))
        return

    if args.replicate:
        r1 = pd.read_csv(HERE / "labels/labreg-r1/prompts_index.csv")
        todo = r1[r1["item_id"].isin(args.replicate)]
        assert set(todo["item_id"]) == set(args.replicate), "unknown item"
        rng = random.Random(SEED + 2)
        taken = set(r1["file_id"])
        cells = []
        for r, new in zip(todo.sample(frac=1, random_state=SEED + 2).itertuples(index=False),
                          opaque_ids(len(todo), rng, taken)):
            prompt = (JUDGE_IO / "labreg-r1/prompts" / f"{r.file_id}@PLp.txt").read_text(encoding="utf-8")
            assert sha256(prompt.encode("utf-8")) == r.prompt_sha256
            cells.append({"file_id": new, "item_id": r.item_id, "set": r.set, "arm": r.arm, "demand": "PLp",
                          "prompt_sha256": r.prompt_sha256, "r1_file_id": r.file_id, "prompt": prompt})
        write_run("labreg-r2", cells, {**note, "pass": 2, "replicates": "labreg-r1"})
        return

    items = build_items(plp.content, plp_c, catalog)
    cols = ["item_id", "set", "own_dim", "target", "family", "reg_PLe", "reg_PLs", "reg_MSc", "stored_median",
            "status", "fourgram_hits", "fourgram_shared", "source", "text"]
    items[cols].to_csv(HERE / "items.csv", index=False)
    judged = items[items["status"] == "judged"]
    cells = []
    for r in judged.itertuples(index=False):
        for arm, content in arms.items():
            rubric = strip_examples(content) if r.set == "P" else content
            prompt = build_annotation_prompt(demand_name=plp.full_name, rubric_content=rubric, task_instance=r.text)
            cells.append({"item_id": r.item_id, "set": r.set, "arm": arm, "demand": "PLp",
                          "prompt_sha256": sha256(prompt.encode("utf-8")), "prompt": prompt})
    rng = random.Random(SEED)
    rng.shuffle(cells)
    for c, i in zip(cells, opaque_ids(len(cells), rng, set())):
        c["file_id"] = i
    cells = [{"file_id": c["file_id"], **{k: v for k, v in c.items() if k != "file_id"}} for c in cells]
    write_run("labreg-r1", cells, {**note, "pass": 1})
    print(items.groupby(["set", "status"]).size().to_string())


if __name__ == "__main__":
    main()
