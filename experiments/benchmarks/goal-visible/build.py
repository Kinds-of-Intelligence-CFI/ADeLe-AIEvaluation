"""Freeze a goal-visible text of every coding and terminal task as a separate instance folder.

Pablo, 2026-10-26: the judge should see the goal of the task in every benchmark. Asked what the goal is for the coding
and terminal sets, he ruled: no tests ("not relevant in this case") and no reference solution, "but it should be clear
what is the goal without those tests". So each task text keeps the frozen text the agent is given (part 1, verbatim)
and gains a short part 2: what counts as success and how it is checked, written from the benchmark's public
documentation. Part 2 is the same for every task of a benchmark, except:
  - SWE-bench Verified and DeepSWE name the task's repository (and DeepSWE its language);
  - FrontierSWE adds the task's own "Task" and "Verification" sections from its public page on frontierswe.com
    (cached in data/raw/frontierswe-v2/site/tasks/ by frontierswe-data/fetch_outcomes.py), because each task has its
    own score.

Writes data/instances-goal/instances_<slug>.parquet and its INSTANCES.tsv (gitignored: task text). Every task's
frozen text must appear verbatim in its new text and hash to the frozen prompt_sha12. Then routes the released tasks
(pls-relabel subsets) between the single-read and chunked-read runs by the programbench-pl rule: a task is long when
any of its judge prompts exceeds 50,000 chars or 1,500 lines. Writes subset.csv, subset_long.csv and prompt_sizes.csv.

    uv run python experiments/benchmarks/goal-visible/build.py
"""

import hashlib
import html
import re
import tempfile
from pathlib import Path

import pandas as pd

from adele.instances import register
from adele.mass.pin import plan_cells
from adele.mass.spec import load_spec

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
ROOT = BENCH.parents[1]
OUT = ROOT / "data/instances-goal"
SITE = ROOT / "data/raw/frontierswe-v2/site/tasks"
SPEC = BENCH / "mass-annotation/specs/goal-visible.toml"
MAX_CHARS, MAX_LINES = 50_000, 1_500

SETTING = {
    "swe-bench-verified": "The agent works in a container with the repository `{repo}` checked out at the commit just "
                          "before the real fix. It gets the GitHub issue in part 1 and can read, edit and run the code. "
                          "It does not see the tests used for grading.",
    "deepswe-v1.1": "The agent works in a container with the repository `{repo}` ({language}) checked out. It gets the "
                    "instruction in part 1 and can read, edit and run the code. It does not see the tests used for "
                    "grading.",
    "frontierswe-v2": "The agent works alone for many hours in an offline container with a fixed time limit. It gets "
                      "the instruction in part 1 (with any README it cites) and can read, edit and run anything in "
                      "the container.",
    "programbench": "The agent gets a compiled program it can run but not read, the documentation left in its "
                    "workspace, and the prompt in part 1. It cannot see the program's source code.",
    "terminal-bench-4.0.0": "The agent works in a terminal inside a container prepared for this task. It gets the "
                            "instruction in part 1 and can run any command.",
    "terminal-bench-science-0.1": "The agent works in a terminal inside a container prepared for this scientific "
                                  "task. It gets the instruction in part 1 and can run any command.",
}
GOAL = {
    "swe-bench-verified": "Resolve the issue: change the repository's source code (not its tests) so that the "
                          "behaviour the issue asks for holds. Grading runs hidden tests taken from the real fix. "
                          "Tests that failed before must now pass, and tests that passed before must still pass. The "
                          "task is solved only if all of them pass.",
    "deepswe-v1.1": "Make the change the instruction describes and commit it. Grading applies the agent's commits to a "
                    "clean copy of the repository and runs held-out tests of the described behaviour. Existing tests "
                    "must still pass. Any solution whose observable behaviour is correct passes, whatever its "
                    "internal names or structure. The task is solved only if all these tests pass.",
    "frontierswe-v2": "Each run gets a score from 0 to 1 from an automated verifier in a separate container. Higher is "
                      "better; 1 is full credit. What the task asks and how this task's score is computed, from the "
                      "benchmark's public page for the task:",
    "programbench": "Write a new codebase from scratch whose build produces an executable that behaves exactly like "
                    "the given program: same output, files and exit codes for any input. Grading runs a hidden suite "
                    "of behavioural tests on the new executable and compares it with the original. The score is the "
                    "share of tests passed.",
    "terminal-bench-4.0.0": "Reach the end state the instruction asks for. When the agent stops, automated checks "
                            "inspect the container's final state (files, outputs, running services). The task is "
                            "solved only if every check passes; there is no partial credit.",
    "terminal-bench-science-0.1": "Reach the end state the instruction asks for. When the agent stops, automated "
                                  "checks inspect the container's final state (result files and their values). The "
                                  "task is solved only if every check passes; there is no partial credit.",
}


def fence(text: str) -> str:
    """A backtick fence longer than any backtick run in the text, so the text cannot close it."""
    return "`" * max(3, max((len(m) for m in re.findall(r"`+", text)), default=0) + 1)


def page_text(fragment: str) -> str:
    """Plain text of one section of a frontierswe.com task page: paragraphs, bullets and inline code."""
    s = re.sub(r"<!-- -->", "", fragment)
    s = re.sub(r"<code[^>]*>(.*?)</code>", lambda m: f"`{m.group(1)}`", s, flags=re.S)
    s = re.sub(r"<li[^>]*>", "\n- ", s)
    s = re.sub(r"</p>|</ul>|</ol>", "\n\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    s = re.sub(r"[ \t]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n\n", "\n".join(line.strip() for line in s.split("\n"))).strip()


def frontierswe_pages() -> dict:
    """Task name -> {"Task": text, "Verification": text}, from the cached task pages."""
    pages = {}
    for path in SITE.glob("*.html"):
        raw = path.read_text(encoding="utf-8")
        name = re.search(r"<title>FrontierSWE - (.*?)</title>", raw).group(1)
        secs = dict(re.findall(r'<section aria-labelledby="[^"]*"[^>]*><h2[^>]*>(.*?)</h2>(.*?)</section>', raw, re.S))
        pages[html.unescape(name)] = {k: page_text(secs[k]) for k in ("Task", "Verification")}
    return pages


def goal_task(slug: str, original: str, goal: str, setting: str) -> str:
    f = fence(original)
    return f"""# Task

**Whose task you rate: the agent's.** {setting}

Part 1 is the text the agent is given, verbatim. Part 2 states the goal: what counts as success and how it is checked.
Part 2 comes from the benchmark's public documentation; the agent does not get it in this form. Both parts together
are the task you annotate.

## 1. What the agent is given

{f}text
{original}
{f}

## 2. The goal: what counts as success

{goal}"""


def per_task(slug: str, ids: list) -> dict:
    """instance_id -> (setting, goal) for one benchmark."""
    if slug == "swe-bench-verified":
        path = next(Path.home().glob(".cache/huggingface/hub/datasets--princeton-nlp--SWE-bench_Verified/"
                                     "snapshots/*/data/test-*.parquet"))
        repo = pd.read_parquet(path, columns=["instance_id", "repo"]).set_index("instance_id")["repo"]
        return {i: (SETTING[slug].format(repo=repo[i]), GOAL[slug]) for i in ids}
    if slug == "deepswe-v1.1":
        meta = pd.read_csv(ROOT / "data/instances/meta_deepswe-v1.1.csv").set_index("instance_id")
        return {i: (SETTING[slug].format(repo=meta.loc[i, "repository"], language=meta.loc[i, "language_corrected"]),
                    GOAL[slug]) for i in ids}
    if slug == "frontierswe-v2":
        name = pd.read_csv(ROOT / "data/instances/meta_frontierswe-v2.csv").set_index("instance_id")["name"]
        pages = frontierswe_pages()
        return {i: (SETTING[slug], f"{GOAL[slug]}\n\n### Task\n\n{pages[name[i]]['Task']}\n\n"
                                   f"### Verification\n\n{pages[name[i]]['Verification']}") for i in ids}
    return {i: (SETTING[slug], GOAL[slug]) for i in ids}


def route() -> None:
    """Split the released tasks between the single-read and chunked-read runs (programbench-pl/route.py's rule)."""
    released = pd.concat([pd.read_csv(BENCH / f"pls-relabel/{f}.csv") for f in ("subset", "subset_long")])
    released = released[released["benchmark"].isin(SETTING)][["benchmark", "instance_id"]]
    with tempfile.TemporaryDirectory() as tmp:
        sub = Path(tmp) / "all.csv"
        released.to_csv(sub, index=False)
        spec = Path(tmp) / "spec.toml"
        spec.write_text(SPEC.read_text().replace("experiments/benchmarks/goal-visible/subset.csv", str(sub)))
        cells, prompts, _ = plan_cells(load_spec(spec))
    rows = [{"benchmark": c["benchmark"], "instance_id": c["instance_id"], "chars": len(prompts[c["cell_id"]]),
             "lines": len(prompts[c["cell_id"]].split("\n"))} for c in cells]
    size = pd.DataFrame(rows).groupby(["benchmark", "instance_id"]).max().reset_index()
    size["long"] = (size["chars"] > MAX_CHARS) | (size["lines"] > MAX_LINES)
    assert len(size) == len(released), f"{len(size)} tasks planned, {len(released)} released"
    size.to_csv(HERE / "prompt_sizes.csv", index=False)
    for name, part in (("subset", size[~size["long"]]), ("subset_long", size[size["long"]])):
        part[["benchmark", "instance_id"]].to_csv(HERE / f"{name}.csv", index=False)
    print("long tasks:", size.groupby("benchmark")["long"].sum().to_dict())


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug in SETTING:
        frozen = pd.read_parquet(ROOT / f"data/instances/instances_{slug}.parquet")
        parts = per_task(slug, list(frozen["instance_id"]))
        rows = []
        for r in frozen.itertuples():
            assert hashlib.sha256(r.prompt.encode()).hexdigest()[:12] == r.prompt_sha12, f"{slug}/{r.instance_id}"
            setting, goal = parts[r.instance_id]
            text = goal_task(slug, r.prompt, goal, setting)
            assert r.prompt in text and goal in text, f"{slug}/{r.instance_id}: text not contained"
            rows.append({"benchmark": slug, "instance_id": r.instance_id, "prompt": text})
        path = OUT / f"instances_{slug}.parquet"
        pd.DataFrame(rows).to_parquet(path, index=False)
        row = register(path, slug)
        print(f"{slug}: {row['n_instances']} tasks, median {row['median_prompt_chars']} chars, "
              f"max {row['max_prompt_chars']}, sha {row['sha256'][:12]}")
    route()


if __name__ == "__main__":
    main()
