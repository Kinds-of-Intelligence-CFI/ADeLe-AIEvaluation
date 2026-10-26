"""Freeze the full-task text of every tau2 task (airline, retail, banking_knowledge) as a separate instance folder.

Pablo, 2026-10-26: the tau2 judge input becomes the full task, for every rubric. The full task is the agent-side
worksheet's parts 1 to 3 (msc-l4-note/make_agent_worksheets.py), with the policy and the simulator rules written in,
as ms-candidate's `full_task` builds it:
  1. what the agent is given: the domain policy, tools, the database records it can look up
  2. what the simulated customer is given: the script (the frozen task text) and the standing simulator rules
  3. the goal: how the run is graded (expected actions, information to communicate, outcome checks, known issues)
Pablo chose to include part 3 and the records (2026-10-26).

banking_knowledge has no single policy file. Its policy here is the two components that every retrieval set-up of
tau2-bench shares (`prompts/components/policy_header.md` and `additional_instructions.md`), plus a line on the
knowledge base; the worksheets had only that line. The records are the task's required documents, as before.

Writes data/instances-tau2-full/instances_<slug>.csv and its INSTANCES.tsv (gitignored: task text). Every script is
checked against the frozen hash of data/instances/, and for the airline and retail worksheet items the text is
checked against ms-candidate's full_task.

    uv run python experiments/benchmarks/tau2-full/build.py
"""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

from adele.agentic.benchmarks import _taubench_prompt
from adele.instances import register

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
ROOT = BENCH.parents[1]
OUT = ROOT / "data/instances-tau2-full"
DOMAINS = ("airline", "retail", "banking_knowledge")


def load(name: str, path: Path):
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ws = load("agent_worksheets", BENCH / "msc-l4-note/make_agent_worksheets.py")


def policy(domain: str) -> str:
    if domain != "banking_knowledge":
        return (ws.DOMAINS / domain / "policy.md").read_text(encoding="utf-8").strip()
    parts = ws.DOMAINS / domain / "prompts/components"
    n = len(list((ws.DOMAINS / domain / "documents").glob("*.json")))
    return "\n\n".join([(parts / "policy_header.md").read_text(encoding="utf-8").strip(),
                        (parts / "additional_instructions.md").read_text(encoding="utf-8").strip(),
                        f"(Knowledge base: {n} documents. How the agent searches it depends on the retrieval set-up.)"])


def full_task(domain: str, task: dict, script: str, rules: str) -> str:
    """The worksheet's parts 1 to 3 for one task, in the form ms-candidate's full_task gives them."""
    tool_list = ", ".join(f"`{n}` ({t.lower()})" for t, n in ws.tools(domain))
    recs = "\n\n".join(f"**{title}**\n\n{ws.block(obj)}" for title, obj in ws.records(domain, task, script))
    user_tools = task.get("user_tools") or []
    return f"""# Task

**Whose task you rate: the customer-service agent's.** That is the model being benchmarked. The customer is
another LLM (GPT-4.1 in most runs) that follows the script in part 2. The agent never sees parts 2 or 3. All three
parts together are the task you annotate.

## 1. What the agent is given

- **Policy:** the agent's system prompt, in full below.
- **Tools:** {tool_list}.
- **Records it can look up** (from the benchmark database; the agent sees them only through its tools):

{recs or '_none found by id_'}

**The agent's policy:**

```text
{policy(domain)}
```

## 2. What the simulated customer is given (hidden from the agent)

The script:

```text
{script}
```

- **Standing rules for every simulated customer:** below. In short: say one
  thing at a time, follow the script, invent nothing, reveal information only when asked, end the chat when the
  goal is met.
{f"- **Tools the customer has:** {', '.join(f'`{t}`' for t in user_tools)}." if user_tools else ""}

```text
{rules}
```

## 3. The goal: how the run is graded

{ws.goal(task)}"""


def main() -> None:
    rules = json.loads(ws.TRACE.read_text(encoding="utf-8"))["info"]["user_info"]["global_simulation_guidelines"].strip()
    OUT.mkdir(parents=True, exist_ok=True)
    texts = {}
    for domain in DOMAINS:
        slug = f"tau2-{domain}"
        frozen = pd.read_csv(ROOT / f"data/instances/instances_{slug}.csv", dtype={"instance_id": str}) \
            .set_index("instance_id")["prompt_sha12"]
        tasks = json.loads((ws.DOMAINS / domain / "tasks.json").read_text(encoding="utf-8"))
        rows = []
        for t in tasks:
            tid = str(t["id"])
            script = _taubench_prompt(domain, t["user_scenario"]["instructions"])
            assert hashlib.sha256(script.encode()).hexdigest()[:12] == frozen[tid], f"{slug}/{tid}: script changed"
            text = full_task(domain, t, script, rules)
            assert "{{" not in text and "](" not in text, f"{slug}/{tid}: unresolved template or link"
            rows.append({"benchmark": slug, "instance_id": tid, "prompt": text})
            texts[(slug, tid)] = text
        assert len(rows) == len(frozen), f"{slug}: {len(rows)} tasks, {len(frozen)} frozen"
        path = OUT / f"instances_{slug}.csv"
        pd.DataFrame(rows).to_csv(path, index=False)
        row = register(path, slug)
        print(f"{slug}: {row['n_instances']} tasks, median {row['median_prompt_chars']} chars, "
              f"max {row['max_prompt_chars']}, sha {row['sha256'][:12]}")
    # The airline and retail worksheet items must match the input ms-candidate judged (banking's policy is new).
    mc = load("ms_candidate_prompts", BENCH / "ms-candidate/make_prompts.py")
    items = pd.read_csv(BENCH / "msc-l4-note/human_items.csv", dtype=str)
    same = [r.item_id for r in items.itertuples() if r.benchmark != "tau2-banking_knowledge"
            and texts[(r.benchmark, r.instance_id)] == mc.full_task(r.item_id)]
    differ = [r.item_id for r in items.itertuples() if r.benchmark != "tau2-banking_knowledge"
              and r.item_id not in same]
    print(f"worksheet items identical to ms-candidate's full task: {len(same)}; different: {differ}")


if __name__ == "__main__":
    main()
