"""ARC-AGI-2 public eval: what the model sees, one instance per task (120).

Sources (all public, no login, no API key, no terms accepted):
  github.com/arcprize/ARC-AGI-2             (Apache-2.0) TASKS_COMMIT: data/evaluation/<task>.json
  github.com/arcprize/arc-agi-benchmarking  (MIT) HARNESS_COMMIT: the ARC Prize testing harness,
      src/arc_agi_benchmarking/prompts/system_prompt.txt and prompt_manager.py
  data/downloads/arc_dump/                  local copy of HF arcprize/arc_agi_v2_public_eval (MIT):
      per-config attempt JSONs whose metadata.choices[0] is the user prompt ARC Prize sent

The prompt is built as the ARC Prize harness builds it (``convert_task_pairs_to_prompt``): the
harness template, each training pair as "--Example i--" with ``json.dumps`` grids, then the test
input. The harness sends ONE prompt per test input and scores a task as the mean over its test
inputs (results.json ``score`` 0.5 = one of two). Rule here: one instance per task, so the outcome
ids join; the prompt has the training examples once and one "--Test Input--" block per test input,
in task order. For the 75 single-test tasks this is byte-identical to the harness prompt; for the
45 tasks with 2 or 3 test inputs it is the harness prompt with the extra test blocks appended
after the first. (Alternative, not taken: the first test input only, verbatim.)

Check: every per-test harness prompt we build is compared with the prompts logged in the dump.
The dump holds two renderings: ``json.dumps`` grids on one line (most configs, the current
harness) and one row per line (an older harness, GPT-4.1 configs). Only the first is expected to
match; the script fails if any test input has no byte-identical logged prompt in the dump.
Found 2026-10-11: those three GPT-4.1 configs also hold an extra test input for 5 tasks (abc82100,
faa9f03d, f560132c, 4a21e3da, b6f77b65) that the pinned task files no longer have, i.e. they ran
an earlier revision of the set; treat their outcomes on those tasks with care.

instance_id = the 8-hex task id, as used by the dump and by ``adele.results.sources.arcprize``.

Writes:
  data/instances/instances_arc-agi-2.parquet  benchmark, instance_id, prompt, prompt_sha12
  data/instances/meta_arc-agi-2.csv           one row per task (sizes, test count, provenance, check)
  data/downloads/arc-agi-2/evaluation/<task>.json, system_prompt.txt, SOURCES.tsv
and registers the instance file in data/instances/INSTANCES.tsv.

Run: python experiments/benchmarks/arcagi2-data/fetch_tasks.py
"""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

import pandas as pd

BENCHMARK = "arc-agi-2"
ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data" / "downloads" / "arc-agi-2"
DUMP = ROOT / "data" / "downloads" / "arc_dump"
OUT = ROOT / "data" / "instances"
sys.path.insert(0, str(ROOT / "src"))
from adele.instances import register, validate_instances  # noqa: E402

TASKS_COMMIT = "f3283f727488ad98fe575ea6a5ac981e4a188e49"
HARNESS_COMMIT = "9e2828fb5bd3ab43f6b9fc545595b82b67473b93"
TASKS_RAW = f"https://raw.githubusercontent.com/arcprize/ARC-AGI-2/{TASKS_COMMIT}/data/evaluation"
TASKS_API = f"https://api.github.com/repos/arcprize/ARC-AGI-2/contents/data/evaluation?ref={TASKS_COMMIT}"
TEMPLATE_URL = (f"https://raw.githubusercontent.com/arcprize/arc-agi-benchmarking/{HARNESS_COMMIT}"
                "/src/arc_agi_benchmarking/prompts/system_prompt.txt")
EXPECTED = 120


def sha12(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()[:12]


def get(url: str, dest: Path) -> bytes:
    """Cached download."""
    if dest.exists():
        return dest.read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": "adele-data/0.1"})
    with urllib.request.urlopen(req, timeout=120) as r:
        blob = r.read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)
    return blob


def task_ids() -> list:
    dest = CACHE / "evaluation_listing.json"
    listing = json.loads(get(TASKS_API, dest))
    ids = sorted(e["name"][:-5] for e in listing if e["name"].endswith(".json"))
    assert len(ids) == EXPECTED, len(ids)
    return ids


def harness_prompt(template: str, train: list, test_input: list) -> str:
    """arc_agi_benchmarking.prompts.prompt_manager.convert_task_pairs_to_prompt, verbatim logic."""
    ex = ""
    for i, pair in enumerate(train):
        ex += f"--Example {i}-- \n\n INPUT: \n\n"
        ex += json.dumps(pair["input"]) + "\n\n"
        ex += "OUTPUT: \n\n"
        ex += json.dumps(pair["output"]) + "\n\n"
    return template.format(training_examples=ex, test_input=json.dumps(test_input))


def instance_prompt(template: str, train: list, tests: list) -> str:
    """Harness prompt for the first test input, with one more test block per further test input."""
    first = harness_prompt(template, train, tests[0]["input"])
    if len(tests) == 1:
        return first
    head, sep, tail = first.partition("--End of Test Input--")
    assert sep, "template changed: no '--End of Test Input--'"
    extra = "".join(f"\n\n--Test Input--\n{json.dumps(t['input'])}\n--End of Test Input--" for t in tests[1:])
    return head + sep + extra + tail


def logged_prompts() -> dict:
    """(task, pair_index) -> set of sha256 of the user prompts logged in the local ARC Prize dump."""
    out = {}
    for f in sorted(DUMP.glob("*/[0-9a-f]*.json")):
        try:
            attempts = json.loads(f.read_text())
        except json.JSONDecodeError:
            continue
        for i, att in enumerate(attempts if isinstance(attempts, list) else []):
            for v in att.values():
                md = (v or {}).get("metadata") if isinstance(v, dict) else None
                if not md:
                    continue
                user = [c["message"].get("content") for c in md.get("choices") or []
                        if isinstance(c.get("message"), dict) and c["message"].get("role") == "user"]
                if user and isinstance(user[0], str):
                    key = (f.stem, md.get("pair_index", i))
                    out.setdefault(key, set()).add(hashlib.sha256(user[0].encode()).hexdigest())
    return out


def main() -> None:
    template = get(TEMPLATE_URL, CACHE / "system_prompt.txt").decode()
    ids = task_ids()
    logged = logged_prompts()
    rows, meta, sources, unmatched = [], [], [], []
    for tid in ids:
        blob = get(f"{TASKS_RAW}/{tid}.json", CACHE / "evaluation" / f"{tid}.json")
        sources.append(f"{tid}.json\t{TASKS_RAW}/{tid}.json\t{hashlib.sha256(blob).hexdigest()}\t{len(blob)}")
        task = json.loads(blob)
        train, tests = task["train"], task["test"]
        matched = 0
        for j, t in enumerate(tests):
            h = hashlib.sha256(harness_prompt(template, train, t["input"]).encode()).hexdigest()
            if h in logged.get((tid, j), set()):
                matched += 1
            else:
                unmatched.append((tid, j))
        prompt = instance_prompt(template, train, tests)
        rows.append({"benchmark": BENCHMARK, "instance_id": tid, "prompt": prompt, "prompt_sha12": sha12(prompt)})
        cells = [len(g) * len(g[0]) for p in train for g in (p["input"], p["output"])]
        meta.append({
            "instance_id": tid, "n_train": len(train), "n_test": len(tests),
            "max_grid_cells": max(cells + [len(t["input"]) * len(t["input"][0]) for t in tests]),
            "prompt_chars": len(prompt), "byte_identical_to_harness": len(tests) == 1,
            "test_prompts_matched_in_dump": matched,
            "source_url": f"{TASKS_RAW}/{tid}.json", "tasks_commit": TASKS_COMMIT, "harness_commit": HARNESS_COMMIT,
        })
    (CACHE / "SOURCES.tsv").write_text("name\turl\tsha256\tbytes\n" + "\n".join(sources) + "\n")
    if unmatched:
        raise SystemExit(f"{len(unmatched)} test inputs have no byte-identical logged prompt, e.g. {unmatched[:5]}")

    df = pd.DataFrame(rows)
    warnings = validate_instances(df, where=BENCHMARK)
    path = OUT / f"instances_{BENCHMARK}.parquet"
    df.to_parquet(path, index=False)
    pd.DataFrame(meta).to_csv(OUT / f"meta_{BENCHMARK}.csv", index=False)
    row = register(path, benchmark=BENCHMARK, n_dimensions=18)
    m = pd.DataFrame(meta)
    print(f"{path.name}: {len(df)} tasks, {int(m.n_test.sum())} test inputs (all matched in the dump), "
          f"{int((m.n_test > 1).sum())} multi-test tasks; prompt chars median {int(m.prompt_chars.median())}, "
          f"max {int(m.prompt_chars.max())}; warnings={warnings}; registered sha256 {row['sha256'][:12]}")


if __name__ == "__main__":
    main()
