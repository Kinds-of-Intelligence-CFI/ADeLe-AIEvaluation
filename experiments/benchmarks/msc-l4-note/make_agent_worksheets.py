"""Agent-side worksheets for the 15 tau2 items of msc-l4-note (2026-10-17).

Pablo's earlier tau2 labels rated the customer's side. In tau2 the benchmarked model is the customer-service agent;
the customer is a simulator LLM following a script the agent never sees. Each worksheet shows the whole task:
  1. what the agent is given: the domain policy (shared file), tools, the database records it can look up
  2. what the simulated customer is given: the script (our frozen task text) and the standing simulator rules
  3. the goal: how the run is graded (expected actions, information to communicate, outcome checks, known issues)

Sources: a sparse checkout of sierra-research/tau2-bench in data/downloads/tau2-bench (commit in README.md of the
worksheet folder); the standing simulator rules from a held-out results file (data/downloads/tau2-traces). Every
task text is checked against the frozen prompt hash. Worksheets go to ~/Developer/ADELE/worksheets/ (never
committed: they carry task text).

    uv run python experiments/benchmarks/msc-l4-note/make_agent_worksheets.py
"""

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pandas as pd

from adele.agentic.benchmarks import _taubench_prompt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TAU2 = ROOT / "data/downloads/tau2-bench"
DOMAINS = TAU2 / "data/tau2/domains"
TRACE = ROOT / ("data/downloads/tau2-traces/gpt-4-1_openai_2024-06-20/trajectories/"
                "gpt-4.1-2025-04-14_airline_default_gpt-4.1-2025-04-14_4trials.json")
OUT = Path("~/Developer/ADELE/worksheets/tau2-agent-side-2026-10-17").expanduser()


def tools(domain: str) -> list[tuple[str, str]]:
    src = (TAU2 / f"src/tau2/domains/{domain}/tools.py").read_text(encoding="utf-8")
    return re.findall(r"^\s+@is_tool\(ToolType\.(\w+)\)\s*\n\s+def (\w+)", src, flags=re.M)


def block(obj) -> str:
    return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"


def strings(obj) -> set[str]:
    """Every string anywhere in a JSON value (ids to look up)."""
    if isinstance(obj, str):
        return {obj}
    if isinstance(obj, dict):
        return set().union(*map(strings, obj.values())) if obj else set()
    if isinstance(obj, list):
        return set().union(*map(strings, obj)) if obj else set()
    return set()


def records(domain: str, task: dict, script: str) -> list[tuple[str, object]]:
    """The database records the agent would look up: the customer's account and what the task refers to."""
    if domain == "banking_knowledge":
        docs = DOMAINS / domain / "documents"
        return [(f"Knowledge-base document `{d}` (one of {len(list(docs.glob('*.json')))}; the agent searches for it)",
                 json.loads((docs / f"{d}.json").read_text(encoding="utf-8")))
                for d in task.get("required_documents") or []]
    db = json.loads((DOMAINS / domain / "db.json").read_text(encoding="utf-8"))
    ids = strings(task["evaluation_criteria"]) | set(re.findall(r"[\w#]+", script))
    users = [u for uid, u in db["users"].items() if uid in ids]
    if not users and domain == "retail":  # found by name and zip
        args = [a["arguments"] for a in task["evaluation_criteria"].get("actions") or []
                if a["name"] == "find_user_id_by_name_zip"]
        users = [u for u in db["users"].values() for a in args
                 if u["name"]["first_name"] == a["first_name"] and u["name"]["last_name"] == a["last_name"]
                 and u["address"]["zip"] == a["zip"]]
    out = [(f"Customer account `{u['user_id']}`", u) for u in users]
    if domain == "airline":
        res = [r for u in users for r in u.get("reservations", [])] + [i for i in ids if i in db["reservations"]]
        for rid in dict.fromkeys(res):
            r = db["reservations"][rid]
            out.append((f"Reservation `{rid}`", r))
            for f in r["flights"]:
                status = db["flights"][f["flight_number"]]["dates"].get(f["date"])
                out.append((f"Flight `{f['flight_number']}` on {f['date']}", status))
    else:
        for oid in dict.fromkeys([o for u in users for o in u.get("orders", [])] + [i for i in ids if i in db["orders"]]):
            out.append((f"Order `{oid}`", db["orders"][oid]))
        for pid in sorted(i for i in ids if i in db["products"]):
            p = db["products"][pid]
            wanted = {k: v for k, v in p["variants"].items() if k in ids}
            out.append((f"Product `{pid}` ({p['name']}), variants the task refers to "
                        f"(of {len(p['variants'])})", wanted))
    return out


def goal(task: dict) -> str:
    ev = task["evaluation_criteria"]
    lines = []
    purpose = (task.get("description") or {}).get("purpose")
    if purpose and not purpose.startswith("Task: "):
        lines.append(f"**Designer's purpose:** {purpose}")
    for who, label in (("assistant", "agent"), ("user", "customer")):
        acts = [a for a in ev.get("actions") or [] if a.get("requestor", "assistant") == who]
        if acts:
            lines.append(f"**Expected {label} actions.** The grader replays these and compares the final database with "
                         f"the run's; read-only lookups change nothing, so only the write actions set the outcome:")
            lines += [f"- `{a['name']}({json.dumps(a['arguments'], ensure_ascii=False)})`" for a in acts]
    if ev.get("communicate_info"):
        lines.append("**Information the agent must tell the customer:** " + "; ".join(map(str, ev["communicate_info"])))
    if ev.get("nl_assertions"):
        lines.append("**Outcome checks:**")
        lines += [f"- {a}" for a in ev["nl_assertions"]]
    lines.append(f"**Reward based on:** {', '.join(ev.get('reward_basis') or [])}")
    for i in task.get("issues") or []:
        lines.append(f"**Known task issue ({i['status']}, {i['created_at']}):** {i['title']}")
    return "\n\n".join(lines)


def main() -> None:
    items = pd.read_csv(HERE / "human_items.csv", dtype=str)
    labels = pd.read_csv(HERE / "human_labels.csv").set_index("item_id")["pablo"]
    frozen = pd.concat(pd.read_csv(ROOT / f"data/instances/instances_{b}.csv", dtype={"instance_id": str})
                       for b in items["benchmark"].unique()).set_index(["benchmark", "instance_id"])
    OUT.mkdir(parents=True, exist_ok=True)
    for d in ("airline", "retail"):
        (OUT / f"policy_{d}.md").write_text((DOMAINS / d / "policy.md").read_text(encoding="utf-8"), encoding="utf-8")
    rules = json.loads(TRACE.read_text(encoding="utf-8"))["info"]["user_info"]["global_simulation_guidelines"]
    (OUT / "simulator_rules.md").write_text(rules, encoding="utf-8")
    commit = subprocess.run(["git", "-C", str(TAU2), "log", "-1", "--format=%H %cs"], capture_output=True,
                            text=True, check=True).stdout.strip()
    tasks = {d: {str(t["id"]): t for t in json.loads((DOMAINS / d / "tasks.json").read_text(encoding="utf-8"))}
             for d in ("airline", "retail", "banking_knowledge")}
    rows = []
    for r in items.itertuples(index=False):
        domain = r.benchmark.removeprefix("tau2-")
        task = tasks[domain][r.instance_id]
        script = _taubench_prompt(domain, task["user_scenario"]["instructions"])
        assert hashlib.sha256(script.encode()).hexdigest()[:12] == frozen.loc[(r.benchmark, r.instance_id), "prompt_sha12"]
        policy = (f"[policy_{domain}.md](policy_{domain}.md) (the agent's system prompt; read once per domain)"
                  if domain != "banking_knowledge" else
                  "a bank-agent prompt that depends on the retrieval set-up (tau2-bench "
                  "`data/tau2/domains/banking_knowledge/prompts/`), plus a 698-document knowledge base it must search")
        tool_list = ", ".join(f"`{n}` ({t.lower()})" for t, n in tools(domain))
        recs = "\n\n".join(f"**{title}**\n\n{block(obj)}" for title, obj in records(domain, task, script))
        user_tools = task.get("user_tools") or []
        md = f"""# {r.item_id}: {r.benchmark} task {r.instance_id}

**Whose task you rate: the customer-service agent's.** That is the model being benchmarked. The customer is
another LLM (GPT-4.1 in most runs) that follows the script in part 2. The agent never sees parts 2 or 3. All three
parts together are the task you annotate.

## 1. What the agent is given

- **Policy:** {policy}.
- **Tools:** {tool_list}.
- **Records it can look up** (from the benchmark database; the agent sees them only through its tools):

{recs or '_none found by id_'}

## 2. What the simulated customer is given (hidden from the agent)

The script (this is our frozen task text):

```text
{script}
```

- **Standing rules for every simulated customer:** [simulator_rules.md](simulator_rules.md). In short: say one
  thing at a time, follow the script, invent nothing, reveal information only when asked, end the chat when the
  goal is met.
{f"- **Tools the customer has:** {', '.join(f'`{t}`' for t in user_tools)}." if user_tools else ""}

## 3. The goal: how the run is graded

{goal(task)}

## Your labels (agent's side)

- Enough information to explain how the customer will behave? yes / no:
- MSc:
- MSm (optional):
- Note:
"""
        (OUT / f"{r.item_id}.md").write_text(md, encoding="utf-8")
        rows.append({"item_id": r.item_id, "benchmark": r.benchmark, "instance_id": r.instance_id,
                     "customer_side_label": labels.get(r.item_id)})
    pd.DataFrame(rows).assign(enough_info="", msc="", msm="", note="").drop(columns="customer_side_label").to_csv(
        OUT / "labels.csv", index=False)
    (OUT / "README.md").write_text(
        f"# tau2 agent-side worksheets (2026-10-17)\n\nRelabel of the 15 tau2 items of msc-l4-note from the "
        f"customer-service agent's side. Sources: sierra-research/tau2-bench at {commit} (task texts match the frozen "
        f"hashes); simulator rules from the GPT-4.1 airline results file. Fill in `labels.csv`, or give labels in "
        f"chat.\n", encoding="utf-8")
    print(f"{len(rows)} worksheets in {OUT}")


if __name__ == "__main__":
    main()
