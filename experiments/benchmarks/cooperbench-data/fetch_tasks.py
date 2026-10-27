"""CooperBench task texts: what the agent(s) see, per feature pair and condition.

CooperBench (arXiv 2601.13295) splits real pull requests into 199 features in 30 task
pools; any two features of a pool form a pair (652 pairs). Leaderboard runs of the paper
(GPT-5, Claude Sonnet 4.5, MiniMax-M2, Qwen3-Coder-30B, Qwen3-30B; OpenHands v0.54, run
Oct-Dec 2025) used a two-phase harness: a planning phase, then an implementation phase.

Conditions built here (the three with per-pair outcomes for those runs):
  solo          one agent gets both features (plans, then implements both)
  coop          two agents, one feature each; they can message each other in both phases
  coop_wo_comm  two agents; planning is the same messaging phase as coop (the plans are
                the very same files), but the implementation phase has no messaging

The templates below were copied verbatim from the agents' own logs in the HF dataset
CooperBench/trajectories (rev TRAJ_REV). The script re-downloads those logs for one pair
and asserts that every rendered template piece occurs verbatim in them. The public
harness repo has close but not identical templates (e.g. planning/templates/coop.j2 at
328e7e0); the logs are the ground truth.

The feature texts come from the harness repo at FEATURES_COMMIT (2026-02-01). The runs
predate it, but the texts match the logs (checked for the sample pair); a later spec audit
(2026-08-14) changed 23 feature.md files, so HEAD is NOT what the agents saw.

Each prompt shows only what the benchmark fixes. The plans the agents wrote in phase 1 are
model output and are replaced by a marked placeholder. The generic OpenHands system prompt
(~11.5k chars, same in all conditions) is summarised in one line; its coop-only
<COLLABORATION> section is included verbatim.

Writes (gitignored):
  data/instances/instances_cooperbench.parquet   benchmark, instance_id, prompt, prompt_sha12
  data/instances/meta_cooperbench.csv            one row per (pair, condition)
  data/downloads/cooperbench/                    cached clone and sample logs

Run: python experiments/benchmarks/cooperbench-data/fetch_tasks.py
"""

import hashlib
import itertools
import json
import re
import subprocess
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download

REPO_URL = "https://github.com/cooperbench/CooperBench.git"
FEATURES_COMMIT = "6da335198a5ea0e2a08c6c7622d19edc2d228534"  # 2026-02-01, texts as run
HEAD_COMMIT = "63b9d44d9f39a02fccf5bf0052db48a917a011fd"      # 2026-09-14, audit + gold conflicts
TRAJ_REPO = "CooperBench/trajectories"
TRAJ_REV = "906bc2f62325eb6f8ccb4cf221e63df051cb3c99"          # 2026-01-28
BENCHMARK = "cooperbench"
CONDITIONS = ("solo", "coop", "coop_wo_comm")
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "instances"
CACHE = ROOT / "data" / "downloads" / "cooperbench"
GIT_ENV = {"GIT_LFS_SKIP_SMUDGE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"}

REPOS = {  # repo dir -> (GitHub repo, language)
    "dottxt_ai_outlines_task": ("dottxt-ai/outlines", "python"),
    "dspy_task": ("stanfordnlp/dspy", "python"),
    "go_chi_task": ("go-chi/chi", "go"),
    "huggingface_datasets_task": ("huggingface/datasets", "python"),
    "llama_index_task": ("run-llama/llama_index", "python"),
    "openai_tiktoken_task": ("openai/tiktoken", "python"),
    "pallets_click_task": ("pallets/click", "python"),
    "pallets_jinja_task": ("pallets/jinja", "python"),
    "pillow_task": ("python-pillow/Pillow", "python"),
    "react_hook_form_task": ("react-hook-form/react-hook-form", "typescript"),
    "samuelcolvin_dirty_equals_task": ("samuelcolvin/dirty-equals", "python"),
    "typst_task": ("typst/typst", "rust"),
}

PLAN_SLOT = "[PLAN: the implementation plan this agent wrote and submitted in phase 1 is inserted here]"
# Phase 2 repeats the feature text verbatim; the prompt shows it once (phase 1) to save length.
FEAT_SLOT = "[FEATURE{n}: the same feature text as in phase 1 is repeated here verbatim]"

# ---- templates, verbatim from the run logs ------------------------------------------

PLAN_COOP_SYSTEM = """You are an implementation planning agent working on codebase:

**YOUR FEATURE (SEPARATE FROM THE OTHER AGENT):**
{feature}

**GOAL: PREVENT MERGE CONFLICTS**
Another agent is implementing a DIFFERENT feature in the same codebase. Coordinate with them to ensure both features can be implemented without merge conflicts.

**IMPORTANT:** You are implementing YOUR OWN feature. The other agent is implementing THEIR OWN separate feature. You are NOT working on the same feature together.

**WORKFLOW:**
1. **REACH AGREEMENT FIRST** - Coordinate with the other agent immediately to establish file ownership and coordination
2. **Explore** ONLY if absolutely necessary to understand your specific feature requirements
3. **Submit** your detailed implementation plan using agreement_reached

**CRITICAL:** Reach agreement FIRST, then explore ONLY if you cannot understand your feature requirements from the description alone. Avoid exploration unless absolutely necessary.

**TRANSITION TO FINAL PLAN:**
After reaching agreement, you should:
- Explore ONLY if you cannot proceed without understanding existing code structure
- Create your detailed step-by-step implementation plan
- Call agreement_reached with your complete plan
- Include coordination notes about what the other agent handles

**COORDINATION ESSENTIALS:**
- Share exact file paths you plan to modify
- Negotiate file ownership (who owns which files entirely)
- Coordinate line positioning for shared files

**KEY COMMUNICATION PATTERNS:**

**Conflict Detection:**
```
communicate_with_agent(
  message="I need to modify: src/models/User.js, controllers/auth.js, routes/auth.js. What files do you plan to change? Let's check for overlaps.",
  message_type="question"
)
```

**Line Coordination:**
```
communicate_with_agent(
  message="In User.js, I'll add auth fields after the existing schema. Can you add your profile fields after mine? I'll also add my imports at the top.",
  message_type="proposal"
)
```

**FINAL PLAN REQUIREMENTS:**
Your agreement_reached plan MUST include:
- Exact file paths and locations for every change
- Coordination notes about what the other agent will handle
- Clear file ownership (yours vs shared vs theirs)

**Example:**
```
agreement_reached(plan="# FEATURE IMPLEMENTATION PLAN

## COORDINATION NOTES
- Other agent handles User.js imports (lines 1-5)
- I own controllers/auth.js entirely (new file)
- Other agent adds profile fields after my auth fields in User.js

## IMPLEMENTATION
### Step 1: Create auth controller
File: controllers/auth.js (I own entirely)
[detailed steps...]")
```"""

PLAN_COOP_USER = "Begin working on your feature. Collaborate with the other agent as needed."

PLAN_SOLO_SYSTEM = """You are an implementation planning agent for codebase: {workspace}

You need to create a UNIFIED implementation plan for TWO features that will be implemented together.

**FEATURE 1:**
{feature1}

**FEATURE 2:**
{feature2}

Your workflow:
1. **Analyze** both feature requirements together
2. **Explore** the codebase structure and relevant files
3. **Understand** existing patterns and architecture
4. **Plan** a unified implementation that handles BOTH features without conflicts
5. **Present** your combined plan using the agreement_reached tool

**Tips:**
- Use tools in parallel when exploring independent items
- Thoroughly understand the codebase before creating your plan
- Your plan should implement BOTH features in a coordinated way
- Identify shared files and coordinate changes carefully
- Use relative paths within the workspace

**Your final plan must include implementation steps for BOTH features in a single, cohesive plan.**"""

PLAN_SOLO_USER = "Create a unified implementation plan for both features."

COLLABORATION = """<COLLABORATION>
**SCENARIO**: You are working on separate branches implementing different features, but your implementations will be tested by 2-way merging both branches to main. You must prevent any merge conflicts.

**COORDINATION REQUIREMENTS**:
* Communicate using 'openhands_comm_send' to prevent merge conflicts (messages from others appear automatically as "[Inter-agent message]")
* Before modifying any file, inform the other agent of the EXACT file path and line numbers you're changing (e.g., "I'm modifying src/logic/createFormControl.ts lines 1100-1140")
* Share your implementation approach early with specific line ranges so both agents can coordinate
* If the other agent reports working on the same file, discuss who modifies which specific line ranges to avoid conflicts
* NEVER use insertion markers or comments like "// [handleSubmit:onFinally] other agent inserts" - these cause merge conflicts
* Instead, coordinate by dividing the file into non-overlapping sections with specific line ranges
* Before you stop or complete your work, you MUST send a final status update message to the other agent summarizing what you've implemented

**MERGE CONFLICT PREVENTION**:
* Think of this as two developers working on separate branches that will be merged together
* Any overlapping changes to the same lines will cause merge conflicts
* Coordinate line-by-line to ensure no overlap in your modifications
</COLLABORATION>"""

EXEC_COOP_USER = """You are {agent_id} working on the following feature in parallel with another agent.

**FEATURE DESCRIPTION**:
{feature}

**IMPLEMENTATION PLAN**:
{plan}

**YOUR TASK**:
1. Implement the feature according to the plan
2. You can communicate with the other agent using MCP tools:
   - openhands_comm_send: Send messages to the other agent
   - Messages from the other agent will appear automatically as '[Inter-agent message]'
3. Coordinate to avoid conflicts by specifying exact file paths and line numbers
4. Complete the implementation

Work directory: /workspace"""

EXEC_PLAN_BLOCK = """## IMPLEMENTATION PLAN

You have been provided with the following implementation plan from the planning phase. Please follow this plan as closely as possible:

{plan}

---

## GUIDELINES

1. **Follow the implementation plan carefully** - The plan was generated specifically for this task and should guide your implementation approach.
2. **Implement the feature** - Focus on implementing the specific feature requirements without unnecessary modifications to unrelated code.
3. **DO NOT USE GIT COMMANDS** - You are strictly forbidden from using any git commands (git add, git commit, git push, git pull, etc.) during execution. Focus only on implementing the code changes.
4. **CLEAN UP TEST SCRIPTS** - Before finishing, remove any temporary test scripts, debug files, or experimental code that you may have added during the implementation process. Only keep the final, clean implementation."""

OPENHANDS_SYSTEM_NOTE = ("System message: the standard OpenHands v0.54 CodeAct system prompt "
                         "(~11,500 characters of generic coding-agent guidance; not reproduced here)")

# OpenHands tools in phase 2, from the logs ("browser" is absent in coop runs)
OH_TOOLS = ("execute_bash, str_replace_editor (file viewer and editor), execute_ipython_cell, "
            "think, task_tracker, fetch (web fetch), finish")

# ---- prompt assembly -----------------------------------------------------------------


def block(text: str) -> str:
    return "<<<\n" + text.strip("\n") + "\n>>>"


def exec_solo_user(f1: str, f2: str) -> str:
    return f"{f1}\n\n\n{f2}\n\n\n" + EXEC_PLAN_BLOCK.format(plan=PLAN_SLOT)


def exec_wo_user(f: str) -> str:
    return f"{f}\n\n\n" + EXEC_PLAN_BLOCK.format(plan=PLAN_SLOT)


def solo_prompt(repo: str, lang: str, workspace: str, f1: str, f2: str) -> str:
    return "\n\n".join([
        "# CooperBench task, solo condition",
        (f"Context for the reader (not shown to the agent): one agent works in one copy of the "
         f"{repo} repository ({lang}). It must implement two features. It works in two phases: "
         f"it explores the code and writes a plan, then it implements the plan. Its final code "
         f"change is graded by the hidden tests of both features. The task counts as solved "
         f"only if both features' tests pass."),
        "## What the agent sees",
        "### Phase 1: planning",
        "Tools: list_files, read_file, grep_search (read-only access to the repository), "
        "agreement_reached (submits the plan and ends the phase).",
        "System message:\n" + block(PLAN_SOLO_SYSTEM.format(workspace=workspace, feature1=f1, feature2=f2)),
        "User message:\n" + block(PLAN_SOLO_USER),
        "### Phase 2: implementation",
        OPENHANDS_SYSTEM_NOTE + ". Tools: " + OH_TOOLS + ", browser.",
        "User message:\n" + block(exec_solo_user(FEAT_SLOT.format(n=" 1"), FEAT_SLOT.format(n=" 2"))),
    ])


def agent_view(n: int, feature: str, comm_in_exec: bool) -> str:
    parts = [
        f"## Agent {n} sees",
        "### Phase 1: planning (both agents plan at the same time and can message each other)",
        "Tools: list_files, read_file, grep_search (read-only access to the repository), "
        "communicate_with_agent (sends a message to the other agent), agreement_reached "
        "(submits the plan and ends the phase).",
        "System message:\n" + block(PLAN_COOP_SYSTEM.format(feature=feature)),
        "User message (messages from the other agent are appended to it as a conversation "
        "history):\n" + block(PLAN_COOP_USER),
        "### Phase 2: implementation",
    ]
    if comm_in_exec:
        parts += [
            OPENHANDS_SYSTEM_NOTE + ", with this extra section:\n" + block(COLLABORATION),
            "Tools: " + OH_TOOLS + ", plus "
            "openhands_comm_send (\"Send a message to another OpenHands agent\") and "
            "openhands_comm_get (\"Get messages from other agents\").",
            "User message:\n" + block(EXEC_COOP_USER.format(agent_id=f"agent_{n}", feature=FEAT_SLOT.format(n=""),
                                                             plan=PLAN_SLOT)),
        ]
    else:
        parts += [
            OPENHANDS_SYSTEM_NOTE + ". There is no collaboration section and no messaging tool "
            "in this phase. Tools: " + OH_TOOLS + ", browser.",
            "User message:\n" + block(exec_wo_user(FEAT_SLOT.format(n=""))),
        ]
    return "\n\n".join(parts)


def coop_prompt(repo: str, lang: str, f1: str, f2: str, comm_in_exec: bool) -> str:
    cond = "coop" if comm_in_exec else "coop_wo_comm"
    talk = ("They can message each other in both phases." if comm_in_exec else
            "They can message each other while planning, but not while implementing.")
    ctx = (f"Context for the reader (not shown to the agents): two agents work at the same time, "
           f"each in its own copy of the {repo} repository ({lang}). Each agent is assigned one "
           f"feature and is shown only its own feature text. Each works in two phases: it "
           f"explores the code and writes a plan, then it implements the plan. {talk} When both "
           f"finish, their two patches are merged, and the hidden tests of both features are run "
           f"on the merged code. The task counts as solved only if the merge succeeds and both "
           f"features' tests pass.")
    return "\n\n".join([f"# CooperBench task, {cond} condition", ctx,
                        agent_view(1, f1, comm_in_exec), agent_view(2, f2, comm_in_exec)])


# ---- sources ---------------------------------------------------------------------------


def git(*a, capture=True) -> str:
    return subprocess.run(["git", "-C", str(CACHE / "CooperBench"), *a], check=True, env=GIT_ENV,
                          capture_output=capture, text=True).stdout


def clone() -> None:
    dest = CACHE / "CooperBench"
    if not (dest / ".git").exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "-q", REPO_URL, str(dest)], check=True, env=GIT_ENV)
    for c in (FEATURES_COMMIT, HEAD_COMMIT):
        try:
            git("cat-file", "-e", c)
        except subprocess.CalledProcessError:
            git("fetch", "-q", "origin")


def show(commit: str, path: str) -> str:
    return git("show", f"{commit}:{path}")


def traj(path: str) -> str:
    return hf_hub_download(TRAJ_REPO, path, repo_type="dataset", revision=TRAJ_REV,
                           cache_dir=str(CACHE / "hf"))


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def check_templates(feat: dict) -> None:
    """Assert the templates occur verbatim (modulo whitespace) in one pair's run logs."""
    r, t = "pallets_click_task", "task2068"
    f1, f2 = feat[(r, t, 1)], feat[(r, t, 2)]
    base = f"{r}/{t}/feature1_feature2/"
    pc = json.load(open(traj("coop_wo_comm/" + base +
                             "planning_traj_model1claude_model2claude_k1_feature1_feature2.json")))
    first = {}
    for e in pc["trajectory"]:
        if e["type"] == "llm_call" and e["agent_id"] not in first:
            first[e["agent_id"]] = e["data"]["input"]["messages"]
    assert norm(first["agent1"][0]["content"]) == norm(PLAN_COOP_SYSTEM.format(feature=f1))
    assert norm(first["agent2"][0]["content"]) == norm(PLAN_COOP_SYSTEM.format(feature=f2))
    assert first["agent1"][1]["content"] == PLAN_COOP_USER
    ps = json.load(open(traj("solo/" + base + "planning_traj_claude_k1_feature1_feature2.json")))
    m = ps["trajectory"][0]["data"]["input"]["messages"]
    ws = "pallets_click_task_feature1_feature2_k1"
    assert norm(m[0]["content"]) == norm(PLAN_SOLO_SYSTEM.format(workspace=ws, feature1=f1, feature2=f2))
    assert m[1]["content"] == PLAN_SOLO_USER

    def exec_msgs(cond, name):
        d = json.load(open(traj(f"{cond}/{base}{name}")))
        return d[0]["message"], d[1]["message"]

    def split_plan(user: str, before: str, after: str) -> tuple[str, str]:
        i, j = user.index(before) + len(before), user.index(after)
        return user[:i], user[j:]

    for n, f in ((1, f1), (2, f2)):
        sysm, user = exec_msgs("coop", f"execution_traj_claude_k1_feature{n}.json")
        assert COLLABORATION in sysm
        exp = EXEC_COOP_USER.format(agent_id=f"agent_{n}", feature=f, plan="@@PLAN@@")
        pre, post = split_plan(user, "**IMPLEMENTATION PLAN**:\n", "\n\n**YOUR TASK**")
        e_pre, e_post = exp.split("@@PLAN@@")
        assert norm(pre) == norm(e_pre) and norm(post) == norm(e_post), n
        sysm, user = exec_msgs("coop_wo_comm", f"execution_traj_claude_k1_feature{n}.json")
        assert "<COLLABORATION>" not in sysm and "openhands_comm" not in sysm
        pre, post = split_plan(user, "follow this plan as closely as possible:\n\n", "\n\n---\n\n## GUIDELINES")
        e_pre, e_post = exec_wo_user(f).replace(PLAN_SLOT, "@@PLAN@@").split("@@PLAN@@")
        assert norm(pre) == norm(e_pre) and norm(post) == norm(e_post), n
    sysm, user = exec_msgs("solo", "execution_traj_claude_k1_feature1_feature2.json")
    pre, post = split_plan(user, "follow this plan as closely as possible:\n\n", "\n\n---\n\n## GUIDELINES")
    e_pre, e_post = exec_solo_user(f1, f2).replace(PLAN_SLOT, "@@PLAN@@").split("@@PLAN@@")
    assert norm(pre) == norm(e_pre) and norm(post) == norm(e_post)
    print("templates match the run logs for", base)


def gold_files(patch: str) -> set[str]:
    return set(re.findall(r"^diff --git a/(\S+) b/", patch, flags=re.M))


def main() -> None:
    clone()
    paths = git("ls-tree", "-r", "--name-only", FEATURES_COMMIT, "--", "dataset").split()
    feat, gold = {}, {}
    for p in paths:
        m = re.match(r"dataset/([^/]+)/(task\d+)/feature(\d+)/feature\.(md|patch)$", p)
        if m:
            key = (m[1], m[2], int(m[3]))
            if m[4] == "md":
                feat[key] = show(FEATURES_COMMIT, p).strip()
            else:
                gold[key] = gold_files(show(FEATURES_COMMIT, p))
    check_templates(feat)

    # later edits to the dataset (spec audit 2026-08/09): per feature and per task
    changed = git("diff", "--name-only", FEATURES_COMMIT, HEAD_COMMIT, "--", "dataset").split()
    spec_changed, tests_changed, task_infra = set(), set(), set()
    for p in changed:
        m = re.match(r"dataset/([^/]+)/(task\d+)/(?:feature(\d+)/)?([^/]+)$", p)
        if not m:
            continue
        if m[3] and m[4] == "feature.md":
            spec_changed.add((m[1], m[2], int(m[3])))
        elif m[3] and m[4] == "tests.patch":
            tests_changed.add((m[1], m[2], int(m[3])))
        elif not m[3] and m[4] in ("Dockerfile", "runner.sh", "run_tests.sh", "setup.sh", "combined.patch"):
            task_infra.add((m[1], m[2]))
    gc = json.loads(show(HEAD_COMMIT, "dataset/gold_conflict_report.json"))
    gold_conflict = {(g["repo"], f"task{g['task_id']}", g["f1"], g["f2"]): g["has_conflict"]
                     for g in gc["all_results"]}
    gold_conflict.update({(r, t, b, a): v for (r, t, a, b), v in list(gold_conflict.items())})
    subsets = {}
    for name in ("lite", "flash"):
        s = json.loads(show(FEATURES_COMMIT, f"dataset/subsets/{name}.json"))
        for task in s["tasks"]:
            for a, b in task["pairs"]:
                subsets.setdefault((task["repo"], f"task{task['task_id']}", min(a, b), max(a, b)), []).append(name)

    pools = {}
    for (r, t, n) in feat:
        pools.setdefault((r, t), []).append(n)
    rows, meta = [], []
    for (r, t), ns in sorted(pools.items()):
        gh, lang = REPOS[r]
        for a, b in itertools.combinations(sorted(ns), 2):
            pair_id = f"{r}-{t[4:]}-f{a}-f{b}"
            fa, fb = feat[(r, t, a)], feat[(r, t, b)]
            ws = f"{r}_feature{a}_feature{b}_k1"
            ga, gb = gold[(r, t, a)], gold[(r, t, b)]
            for cond in CONDITIONS:
                prompt = (solo_prompt(gh, lang, ws, fa, fb) if cond == "solo"
                          else coop_prompt(gh, lang, fa, fb, comm_in_exec=(cond == "coop")))
                iid = f"{pair_id}@{cond}"
                rows.append({"benchmark": BENCHMARK, "instance_id": iid, "prompt": prompt,
                             "prompt_sha12": hashlib.sha256(prompt.encode()).hexdigest()[:12]})
                meta.append({
                    "instance_id": iid, "pair_id": pair_id, "condition": cond,
                    "repo_dir": r, "repo": gh, "language": lang, "task_id": t,
                    "feature_a": a, "feature_b": b, "n_features_in_pool": len(ns),
                    "title_a": fa.splitlines()[0].replace("**Title**:", "").strip(),
                    "title_b": fb.splitlines()[0].replace("**Title**:", "").strip(),
                    "feature_a_chars": len(fa), "feature_b_chars": len(fb),
                    "prompt_chars": len(prompt),
                    "gold_conflict": gold_conflict[(r, t, a, b)],
                    "gold_files_a": len(ga), "gold_files_b": len(gb),
                    "gold_shared_files": len(ga & gb),
                    "gold_shared_file_list": ";".join(sorted(ga & gb)),
                    "spec_changed_after_runs": ";".join(f"f{x}" for x in (a, b) if (r, t, x) in spec_changed),
                    "tests_changed_after_runs": ";".join(f"f{x}" for x in (a, b) if (r, t, x) in tests_changed),
                    "task_infra_changed_after_runs": (r, t) in task_infra,
                    "subsets": ";".join(subsets.get((r, t, a, b), [])),
                })
    df, mf = pd.DataFrame(rows), pd.DataFrame(meta)
    assert df.instance_id.is_unique and len(df) == 652 * len(CONDITIONS), len(df)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT / "instances_cooperbench.parquet", index=False)
    mf.to_csv(OUT / "meta_cooperbench.csv", index=False)
    print(f"{len(feat)} features, {len(pools)} task pools, {len(df) // len(CONDITIONS)} pairs, {len(df)} rows")
    print(mf.groupby("condition").prompt_chars.describe(percentiles=[.5, .75, .9]).round(0))


if __name__ == "__main__":
    main()
