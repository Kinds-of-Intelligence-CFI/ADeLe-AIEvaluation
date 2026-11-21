"""Build the items, the 4-gram check and the prompts of pls-computer (see PREREGISTRATION.md).

Two texts: `cur` is PLs as the catalog loads it; `cand` is PLs_candidate.txt, which is `cur` plus three example
bullets (computer worlds that cannot be run first, at Levels 3, 4 and 5). Item sets:
  P  the three new bullets, judged under `cur` (which does not contain them), three repeats
  M  four minimal pairs of computer situations (pairs.csv), both texts, three repeats
  B  battery-v1, the lab's standing items (lab record 7159671), both texts, one label each
  R  60 real tasks (SWE-bench Verified, DeepSWE, Terminal-Bench 4.0 clean sets; 20 each, seeded): `cand` once,
     with the released label as reference; 20 of them (7, 7, 6) again under `cur`, to measure judge noise
R prompts are the released prompts (found by SHA-256 in judge-io) with the rubric text swapped, or verbatim for
the noise replicate. Every item of P, M and B is checked for shared word 4-grams against every example bullet of
the rubric it is shown with; a shared 4-gram voids it. One prompt file per call, with an opaque id, all sets and
texts shuffled together into run plsc-1 (judge folder opus-low).

    python experiments/benchmarks/pls-computer/make_prompts.py
    python experiments/benchmarks/pls-computer/make_prompts.py --pass2 ITEM [ITEM ...]   # run plsc-2
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
from adele.annotation.prompts import build_annotation_prompt_v2

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
ROOT = BENCH.parents[1]
JUDGE_IO = ROOT.parents[1] / "judge-io"
LAB = "7159671"
SEED = 20261004
ID_CHARS = "abcdefghjkmnpqrstuvwxyz23456789"
REPEATS = 3
REAL = {"swebench-clean": ("SWE-bench Verified", 7), "deepswe-clean": ("DeepSWE", 7), "tb4-clean": ("TB 4.0", 6)}
N_REAL = 20
REF_DIRS = ["v2-swe", "clean-swe", "npb-gate-opuslow", "deepswe-clean", "v2-tb4"]
AGENT = Path.home() / "Developer/ADELE/.claude/agents/adele-judge-v2-low.md"
INSTRUCTION = "Prompt file: {prompt_file}\nResponse file: {response_file}"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def bullets(content: str) -> list[tuple[int, str]]:
    out, level = [], None
    for line in content.splitlines():
        m = re.match(r"Level (\d):", line)
        if m:
            level = int(m.group(1))
        elif line.startswith("* "):
            out.append((level, line[2:].strip()))
    return out


def fourgrams(text: str) -> set[tuple[str, ...]]:
    w = re.findall(r"[a-z0-9]+", text.lower())
    return {tuple(w[i:i + 4]) for i in range(len(w) - 3)}


def shared(text: str, rubric: str) -> str:
    g = fourgrams(text)
    return "; ".join(f"Level {lvl}: " + " | ".join(" ".join(x) for x in sorted(g & fourgrams(b)))
                     for lvl, b in bullets(rubric) if g & fourgrams(b))


def opaque_ids(n: int, rng: random.Random, taken: set[str]) -> list[str]:
    out = []
    while len(out) < n:
        i = "".join(rng.choice(ID_CHARS) for _ in range(5))
        if i not in taken:
            taken.add(i)
            out.append(i)
    return out


def reference_prompts() -> dict[str, Path]:
    out = {}
    for d in REF_DIRS:
        for p in (JUDGE_IO / d / "prompts").glob("*PLs*.txt"):
            out[sha256(p.read_bytes())] = p
    return out


def write_run(run_id: str, cells: list[dict], note: dict) -> None:
    io_dir, labels = JUDGE_IO / run_id, HERE / "labels" / run_id
    for d in (io_dir / "prompts", io_dir / "responses/opus-low", labels):
        d.mkdir(parents=True, exist_ok=True)
    for c in cells:
        (io_dir / "prompts" / f"{c['file_id']}@PLs.txt").write_bytes(c.pop("prompt").encode("utf-8"))
    pd.DataFrame(cells).to_csv(labels / "prompts_index.csv", index=False)
    run = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "repo_commit": git("rev-parse", "HEAD").strip(),
           "design": {"n_cells": len(cells), "dims": ["PLs"], "judges": {
               "opus-low": "Claude Code subagent 'adele-judge-v2-low' (Read, Write; omitClaudeMd; effort low), "
                           "model alias 'opus', relayed by 'judge-dispatcher-v2-low'"}},
           **note,
           "prompt": {"builder": "adele.annotation.prompts.build_annotation_prompt_v2",
                      "builder_file_sha256": sha256((ROOT / "src/adele/annotation/prompts.py").read_bytes())},
           "judge_agent": {"file": "~/Developer/ADELE/.claude/agents/adele-judge-v2-low.md",
                           "sha256": sha256(AGENT.read_bytes())},
           "judge_instruction": INSTRUCTION, "judge_io": os.path.relpath(io_dir, ROOT)}
    (labels / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    print(f"{run_id}: {len(cells)} prompts")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass2", nargs="+", metavar="ITEM", help="judge these items again, both texts, three repeats")
    args = ap.parse_args()
    cat = load_active_catalog()
    pls = cat["PLs"]
    cur = pls.content
    # The catalog shows the file without its title line, the blank line after it and the final newline.
    cand = (HERE / "PLs_candidate.txt").read_text(encoding="utf-8").removeprefix("# Simulating\n\n").rstrip("\n")
    assert Path(pls.file_path).read_text(encoding="utf-8").removeprefix("# Simulating\n\n").rstrip("\n") == cur
    new = [b for b in bullets(cand) if b not in bullets(cur)]
    assert [lvl for lvl, _ in new] == [3, 4, 5] and len(bullets(cand)) == len(bullets(cur)) + 3
    added = {"* " + t for _, t in new}
    assert [l for l in cand.splitlines() if l not in added] == cur.splitlines(), "candidate is not cur plus three bullets"
    texts = {"cur": cur, "cand": cand}
    note = {"rubric": {"file": str(Path(pls.file_path).relative_to(ROOT)), "sha256": sha256(cur.encode("utf-8")),
                       "candidate": "pls-computer/PLs_candidate.txt", "candidate_sha256": sha256(cand.encode("utf-8"))},
            "lab_record_commit": LAB}

    def prompt(arm: str, text: str) -> str:
        return build_annotation_prompt_v2(demand_name=pls.full_name, rubric_content=texts[arm], task_instance=text)

    if args.pass2:
        items = pd.read_csv(HERE / "items.csv").set_index("item_id")
        r1 = pd.read_csv(HERE / "labels/plsc-1/prompts_index.csv")
        taken = set(r1["file_id"])
        cells = []
        for item in args.pass2:
            for arm in ("cur", "cand"):
                if items.loc[item, "set"] == "R":
                    src = r1[(r1["item_id"] == item) & (r1["arm"] == arm)]
                    if len(src):
                        p = (JUDGE_IO / "plsc-1/prompts" / f"{src['file_id'].iloc[0]}@PLs.txt").read_bytes().decode("utf-8")
                    else:  # cur arm of a task outside the noise subset: the released prompt
                        p = Path(items.loc[item, "ref_prompt"]).expanduser().read_bytes().decode("utf-8")
                else:
                    p = prompt(arm, items.loc[item, "text"])
                cells += [{"item_id": item, "set": items.loc[item, "set"], "arm": arm, "repeat": k,
                           "prompt_sha256": sha256(p.encode("utf-8")), "prompt": p} for k in range(1, REPEATS + 1)]
        rng = random.Random(SEED + 2)
        rng.shuffle(cells)
        for c, i in zip(cells, opaque_ids(len(cells), rng, taken)):
            c["file_id"] = i
        write_run("plsc-2", [{"file_id": c.pop("file_id"), **c} for c in cells], {**note, "pass": 2})
        return

    rows = [{"item_id": f"P-L{lvl}", "set": "P", "target": str(lvl), "text": t,
             "fourgram_shared": shared(t, cur)} for lvl, t in new]
    for r in pd.read_csv(HERE / "pairs.csv").itertuples(index=False):
        rows.append({"item_id": r.item_id, "set": "M", "pair": r.pair, "role": r.role, "target": r.target,
                     "text": r.text, "fourgram_shared": shared(r.text, cand)})
    battery = pd.read_csv(io.StringIO(git("show", f"{LAB}:labs/rubric-qa/battery-v1/items.csv")))
    prereg = pd.read_csv(io.StringIO(git("show", f"{LAB}:labs/rubric-qa/battery-v1/prereg.csv"))).set_index("item_id")
    for r in battery.itertuples(index=False):
        rows.append({"item_id": f"B-{r.item_id}", "set": "B", "role": prereg.loc[r.item_id, "family"],
                     "target": str(prereg.loc[r.item_id, "PLs"]), "text": r.task, "fourgram_shared": shared(r.task, cand)})
    refs = reference_prompts()
    rng = random.Random(SEED)
    for study, (name, n_noise) in REAL.items():
        lab = pd.read_csv(BENCH / study / "release/labels.csv")
        lab = lab[lab["rubric"] == "v2/PLs"].sort_values("instance_id")
        pick = lab.sample(N_REAL, random_state=rng.randrange(2**31))
        for k, r in enumerate(pick.itertuples(index=False)):
            ref = refs[r.prompt_sha256]
            rows.append({"item_id": f"R-{r.instance_id}", "set": "R", "pair": name, "role": "noise" if k < n_noise else "",
                         "target": str(r.level), "text": "", "ref_prompt": "~/" + str(ref.relative_to(Path.home())),
                         "ref_prompt_sha256": r.prompt_sha256, "ref_response_sha256": r.response_sha256})
    items = pd.DataFrame(rows)
    items["status"] = ["void" if s else "judged" for s in items["fourgram_shared"].fillna("")]
    items.to_csv(HERE / "items.csv", index=False)

    cells = []
    for r in items[items["status"] == "judged"].itertuples(index=False):
        if r.set == "P":
            cells += [{"item_id": r.item_id, "set": "P", "arm": "cur", "repeat": k, "prompt": prompt("cur", r.text)}
                      for k in range(1, REPEATS + 1)]
        elif r.set == "M":
            cells += [{"item_id": r.item_id, "set": "M", "arm": a, "repeat": k, "prompt": prompt(a, r.text)}
                      for a in texts for k in range(1, REPEATS + 1)]
        elif r.set == "B":
            cells += [{"item_id": r.item_id, "set": "B", "arm": a, "repeat": 1, "prompt": prompt(a, r.text)} for a in texts]
        else:
            ref = Path(r.ref_prompt).expanduser().read_bytes().decode("utf-8")  # keeps any \r
            assert sha256(ref.encode("utf-8")) == r.ref_prompt_sha256 and ref.count(cur) == 1
            cells.append({"item_id": r.item_id, "set": "R", "arm": "cand", "repeat": 1, "prompt": ref.replace(cur, cand)})
            if r.role == "noise":
                cells.append({"item_id": r.item_id, "set": "R", "arm": "cur", "repeat": 1, "prompt": ref})
    for c in cells:
        c["prompt_sha256"] = sha256(c["prompt"].encode("utf-8"))
    rng = random.Random(SEED + 1)
    rng.shuffle(cells)
    for c, i in zip(cells, opaque_ids(len(cells), rng, set())):
        c["file_id"] = i
    write_run("plsc-1", [{"file_id": c.pop("file_id"), **c} for c in cells], {**note, "pass": 1})
    print(items.groupby(["set", "status"]).size().to_string())
    print(pd.DataFrame(cells).groupby(["set", "arm"]).size().to_string())


if __name__ == "__main__":
    main()
