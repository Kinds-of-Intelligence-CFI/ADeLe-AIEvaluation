"""EQ-Bench 4 scenarios: what the tested model sees, plus the persona simulator's hidden prompt.

Sources (both public, no login):
  * github.com/EQ-bench/eqbench4 (harness + dataset), pinned to HARNESS_COMMIT. Licence: BSD-3-Clause
    with the Commons Clause (no selling), added 2026-09-26. Dataset: src/eqbench/datasets/test.json
    (v0.17, 120 scenarios). Prompt templates: src/eqbench/prompts/*.txt.
  * results/r23.json at the same commit (20 MB): the Claude Haiku 4.5 run. It stores the exact system
    prompts sent in every conversation. Used only to check the rendering below, byte for byte.

The harness code is NOT imported or run. The two prompt builders of src/eqbench/core/prompts.py
(build_evaluated_system_prompt, build_persona_system_prompt; canon "no_state_no_unlock" variant) are
re-implemented here from the pinned source, and checked against r23.json.

Conversation set-up (src/eqbench/core/conversation_runner.py): the tested model speaks first. Its
messages are [system prompt for turn 1, user: '[Presenting issue (what begins this conversation):
"<presenting text>"]']. 8 turns each side (num_turns=8); the persona may end early.

`prompt` = the tested model's turn-1 system prompt + its first user message, then a labelled section
with the persona simulator's system prompt (hidden from the tested model). No transcript.

Writes (gitignored data/ tree only; the scenario text must not be committed):
  data/instances/instances_eqbench4.parquet   benchmark, instance_id, prompt, prompt_sha12
  data/instances/meta_eqbench4.csv            scenario tags, turns, prompt chars
Caches under data/downloads/eqbench4/.

Run: python experiments/benchmarks/eqbench4-data/fetch_tasks.py
"""

import hashlib
import json
import re
import subprocess
import urllib.request
from pathlib import Path

import pandas as pd

HARNESS_URL = "https://github.com/EQ-bench/eqbench4.git"
HARNESS_COMMIT = "93dcb7f5d430433ad49d501e672a98bcff2c9678"  # "add license", 2026-09-26
BENCHMARK = "eqbench4"
NUM_TURNS = 8  # config default and the official leaderboard runs (r23.json __meta__)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "data" / "instances"
CACHE = ROOT / "data" / "downloads" / "eqbench4"
HARNESS = CACHE / "eqbench4"
CHECK_RUN = CACHE / "raw_results" / "r23.json"

FIRST_USER_MESSAGE = '[Presenting issue (what begins this conversation): "{presenting_issue}"]'
HEADER = ("[EQ-Bench 4] Multi-turn roleplay chat. The tested model plays the other person's {rel}. "
          "It speaks first. Up to {n} turns each; the simulated person may end the chat early.")
SEP_SEEN = "=== WHAT THE TESTED MODEL SEES AT THE START ==="
SEP_SYS = "--- System prompt (turn 1 of {n}) ---"
SEP_USER = "--- First user message ---"
SEP_HIDDEN = ("=== HIDDEN FROM THE TESTED MODEL: the persona simulator's system prompt "
              "(the simulated person, played by Gemini 3.1 Pro Preview) ===")

PERSONALITY_CATS = {"cognitive_style", "emotional_tendency", "interpersonal_style", "self_perception",
                    "behavioral_pattern", "relational_pattern", "communication_style"}


def checkout() -> Path:
    """Sparse, blob-filtered checkout of the harness at HARNESS_COMMIT, without the 1.8 GB of run files."""
    def git(*args):
        subprocess.run(["git", "-C", str(HARNESS), *args], check=True)
    if not (HARNESS / ".git").exists():
        HARNESS.mkdir(parents=True, exist_ok=True)
        git("init", "-q")
        git("remote", "add", "origin", HARNESS_URL)
        git("sparse-checkout", "set", "--no-cone", "/*", "!/results/", "/results/elo_results.json",
            "/results/judge_bias_report.json", "/results/model_summaries.json")
    git("fetch", "-q", "--filter=blob:none", "origin", HARNESS_COMMIT)
    git("checkout", "-q", HARNESS_COMMIT)
    if not CHECK_RUN.exists():
        CHECK_RUN.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://raw.githubusercontent.com/EQ-bench/eqbench4/{HARNESS_COMMIT}/results/r23.json"
        urllib.request.urlretrieve(url, CHECK_RUN)
    return HARNESS


def template(name: str) -> str:
    return (HARNESS / "src" / "eqbench" / "prompts" / name).read_text(encoding="utf-8")


def is_hand(s: dict) -> bool:
    return s.get("source_type") == "hand_authored" or bool(s.get("hand_authored"))


def public_setup(s: dict) -> dict:
    ps = (s.get("hand_authored") or {}).get("public_setup") or {}
    return ps if isinstance(ps, dict) else {}


def respondent_presenting(s: dict) -> str:
    pi = s.get("presenting_issue", {})
    default = pi.get("description", pi.get("label", ""))
    ctx = str(public_setup(s).get("assistant_context", "") or "").strip() if is_hand(s) else ""
    return f"[scenario background]\n{ctx}\n\n[user message]\n{default}" if ctx else default


def chatbot_context(rel: str) -> str:
    if rel != "chatbot":
        return ""
    context = (
        "In this roleplay, you are essentially playing yourself, a chatbot, naturally. "
        "Be mindful of balancing what the user asks for, what they need "
        "in the context of the chat, and what they want/need long-term. Also factor "
        "in the need to build trust & relationship across more chats than just this "
        "one. The user may or may not choose to return; calibrate your interaction "
        "accordingly. Remember that all users are different: some want to be "
        "challenged; some want to be validated; many will have their own complex "
        "preferences and sensitivities that don't map cleanly to this dichotomy. "
        "This isn't prescriptive advice; just context to remind you that the human "
        "user will remember what you do & say."
    )
    return f"## CHATBOT RELATIONSHIP CONTEXT\n\n{context}\n"


def evaluated_system_prompt(s: dict, current_turn: int = 1) -> str:
    """Re-implements prompts.build_evaluated_system_prompt."""
    rel = s.get("assistant_relationship", "therapist")
    demo = {"age": "", "gender": "", "sexuality": ""}
    for m in s.get("modifiers", []):
        if m.get("category", "") in demo:
            demo[m["category"]] = m.get("label", "")
    parts = [demo[k] for k in ("age", "gender", "sexuality") if demo[k]]
    demographics = public_setup(s).get("demographics") or (", ".join(parts) if parts else "Not specified")
    p = template("evaluated_system_prompt.txt")
    p = p.replace("{assistant_relationship}", rel)
    p = p.replace("{relationship_context}", chatbot_context(rel))
    p = p.replace("{num_turns}", str(NUM_TURNS))
    p = p.replace("{current_turn}", str(current_turn))
    p = p.replace("{demographics_str}", demographics)
    p = p.replace("{presenting_description}", respondent_presenting(s))
    p += " No special formatting needed."
    if current_turn == 1:
        p += template("evaluated_first_turn_section.txt")
    return p


def verbal_section(persona: dict) -> str:
    v = persona.get("verbal_sophistication")
    if not isinstance(v, dict):
        return ""
    label = str(v.get("label", "") or "").strip()
    desc = str(v.get("description", "") or "").strip()
    if not label and not desc:
        return ""
    return f"""
**Verbal sophistication ({label or "specified"}):**
{desc or label}

This is about how polished your thoughts and speech sound under pressure. It is not intelligence, worth, education, or emotional depth. Match your internal monologue and dialogue to this level; do not make every persona unusually articulate or insight-ready.
""".strip()


def fmt_list(items) -> str:
    return "\n".join(f"- {i}" for i in items) if items else "(None)"


def hand_context(s: dict) -> str:
    hand = s.get("hand_authored")
    if not hand:
        return ""
    pp = hand.get("persona", {})
    pctx = str(public_setup(s).get("persona_context", "") or "").strip()
    sections = [
        "## HAND-AUTHORED TASK CONTEXT",
        hand.get("shared_task_context", "").strip(),
        f"### {hand.get('task_context_title', 'Task Context')}",
        hand.get("task_context", "").strip(),
        "## HAND-AUTHORED CHARACTER CARD",
        f"**Scenario title:** {hand.get('title', '')}",
        "",
        "**Scenario background for your role:**",
        pctx or "(None)",
        "",
        "**Persona-specific tags and internal local state:**",
        f"- Trust style marker: {pp.get('trust_style', '')}",
        f"- Defense style marker: {pp.get('defense_style', '')}",
        f"- Help-seeking stance marker: {pp.get('help_seeking_stance', '')}",
        f"- Sensitivities: {', '.join(pp.get('sensitivities', []) or []) or '(None)'}",
        f"- Preferences: {', '.join(pp.get('preferences', []) or []) or '(None)'}",
        f"- Internal local state to track: {', '.join(pp.get('hidden_local_state', []) or []) or '(None)'}",
        "**Scenario-local backfire tendencies:**",
        fmt_list(hand.get("backfires", []) or []),
        "",
        "Use these notes to understand the interactional design of this specific card. "
        "They should shape your reactions, guardedness, and what feels speakable, but they are not dialogue to recite. "
        "They do not define a correct path through the conversation.",
    ]
    return "\n\n" + "\n".join(x for x in sections if x is not None).strip() + "\n"


def norm_adjacent(label: str) -> str:
    label = re.sub(r"(?i)\b(low|medium|high)\s+trust/respect-gated\s+private\s+material\s+", "Situation material ", label)
    return re.sub(r"(?i)\b(low|medium|high)\s+admission-threshold\s+internal\s+material\s+", "Situation material ", label)


def persona_system_prompt(s: dict) -> str:
    """Re-implements prompts.build_persona_system_prompt (canon no_state_no_unlock templates)."""
    rel = s.get("assistant_relationship", "therapist")
    persona, core = s["persona"], s["core_issue"]
    no_core = core.get("category") == "no_core_issue"
    hand = is_hand(s)
    demographics, personality, background = [], [], []
    for m in s.get("modifiers", []):
        cat, content = m.get("category", ""), m.get("content", m.get("label", ""))
        if cat in ("age", "gender", "sexuality"):
            demographics.append(content)
        elif cat in PERSONALITY_CATS:
            personality.append(f"- {m.get('label', '')}: {content}")
        else:
            background.append(content)
    demographics_str = public_setup(s).get("demographics") or (", ".join(demographics) if demographics else "Not specified")
    sens = "\n".join(f"- {x.get('label', '')}: {x.get('content', '')}" for x in s.get("sensitivities", [])) or "None"
    prefs = "\n".join(f"- {x.get('label', '')}: {x.get('content', '')}" for x in s.get("preferences", [])) or "None"
    p = template("persona_system_prompt_no_core_issue_no_state_no_unlock.txt" if no_core
                 else "persona_system_prompt_no_state_no_unlock.txt")
    p = p.replace("{assistant_relationship}", rel)
    p = p.replace("{demographics_str}", demographics_str)
    p = p.replace("{background_str}", "; ".join(background) if background else "Not specified")
    p = p.replace("{personality_str}", "\n".join(personality) if personality else "None specified")
    pi = s.get("presenting_issue", {})
    p = p.replace("{presenting_description}", pi.get("description", pi.get("label", "")))
    p = p.replace("{core_issue_description}", core.get("description", ""))
    if hand:
        p = p.replace("{core_issue_heading}", "SCENARIO DYNAMIC")
        p = p.replace("{core_issue_intro}", "This describes the situation dynamic that shapes what you notice, resist, reveal, and need. Portray it as a living pressure in the scene, not as a target answer, reveal script, or problem you are required to solve during the conversation.")
    else:
        p = p.replace("{core_issue_heading}", "SITUATION CONTEXT")
        p = p.replace("{core_issue_intro}", "This context describes the situation pressure that may shape your feelings, reactions, defenses, and what you notice. Portray it as part of how the scene feels from inside your character, not as a target answer, reveal script, or problem you are required to solve during the conversation.")
    p = p.replace("{hand_authored_context}", hand_context(s))
    for key in ("trust_style", "defense_style", "help_seeking_stance"):
        p = p.replace("{%s_name}" % key, persona[key]["name"])
        p = p.replace("{%s_description}" % key, persona[key]["description"])
    p = p.replace("{verbal_sophistication_section}", verbal_section(persona))
    p = p.replace("{sensitivities_str}", sens)
    p = p.replace("{preferences_str}", prefs)
    # The no_state templates have no state placeholders; prompts.py's state replacements are no-ops here.
    if not no_core:
        adj = [f"- [{a.get('sensitivity', 'medium').upper()} admission threshold] "
               f"{norm_adjacent(a.get('label', ''))}: {a.get('content', '')}"
               for a in s.get("core_adjacent_attributes", [])]
        p = p.replace("{adjacent_str}", "\n".join(adj) if adj else "None")
    return p


def check_against_run(docs: list) -> int:
    """Compare the rendered prompts with the prompts stored in the Haiku 4.5 run (r23.json)."""
    run = json.loads(CHECK_RUN.read_text(encoding="utf-8"))["r1"]
    by_id = {d["id"]: d for d in docs}
    n = 0
    for sid, convs in run.items():
        if sid.startswith("__"):
            continue
        pr = convs[0]["prompts"]
        s = by_id[sid]
        assert convs[0]["doc"] == s, f"dataset differs from the run's copy: {sid}"
        assert pr["evaluated_system_prompts_per_turn"][0] == evaluated_system_prompt(s, 1), f"evaluated prompt: {sid}"
        assert pr["persona_system_prompt"] == persona_system_prompt(s), f"persona prompt: {sid}"
        n += 1
    return n


def main() -> None:
    checkout()
    data = json.loads((HARNESS / "src/eqbench/datasets/test.json").read_text(encoding="utf-8"))
    docs = data["docs"]
    assert len(docs) == 120 == len({d["id"] for d in docs}), len(docs)
    n_checked = check_against_run(docs)
    assert n_checked == 120, n_checked
    inst, meta = [], []
    for s in docs:
        rel = s["assistant_relationship"]
        system = evaluated_system_prompt(s, 1)
        first_user = FIRST_USER_MESSAGE.format(presenting_issue=respondent_presenting(s))
        persona = persona_system_prompt(s)
        seen = "\n\n".join([SEP_SYS.format(n=NUM_TURNS), system, SEP_USER, first_user])
        prompt = "\n\n".join([HEADER.format(rel=rel.replace("_", " "), n=NUM_TURNS), SEP_SEEN, seen,
                              SEP_HIDDEN, persona])
        inst.append({"benchmark": BENCHMARK, "instance_id": s["id"], "prompt": prompt,
                     "prompt_sha12": hashlib.sha256(prompt.encode()).hexdigest()[:12]})
        hand = s.get("hand_authored") or {}
        mods = {m.get("category"): m.get("label") for m in s.get("modifiers", [])}
        meta.append({
            "instance_id": s["id"],
            "doc_id": s.get("doc_id"),
            "source_type": s.get("source_type"),
            "task_type": s.get("task_type") or "",
            "hand_authored_id": hand.get("id", ""),
            "title": hand.get("title") or s["presenting_issue"].get("label"),
            "assistant_relationship": rel,
            "presenting_issue_id": s["presenting_issue"].get("id"),
            "presenting_severity": s["presenting_issue"].get("severity_hint"),
            "core_issue_id": s["core_issue"].get("id"),
            "core_issue_category": s["core_issue"].get("category"),
            "core_issue_subcategory": s["core_issue"].get("subcategory"),
            "trust_style": s["persona"]["trust_style"]["id"],
            "defense_style": s["persona"]["defense_style"]["id"],
            "help_seeking_stance": s["persona"]["help_seeking_stance"]["id"],
            "verbal_sophistication": (s["persona"].get("verbal_sophistication") or {}).get("id", ""),
            "age": mods.get("age", ""), "gender": mods.get("gender", ""),
            "sensitivities": ";".join(x["id"].removeprefix("modifier|") for x in s.get("sensitivities", [])),
            "preferences": ";".join(x["id"].removeprefix("modifier|") for x in s.get("preferences", [])),
            "n_adjacent_attributes": len(s.get("core_adjacent_attributes", [])),
            "num_turns": NUM_TURNS,
            "prompt_chars": len(prompt),
            "seen_chars": len(seen),
            "persona_prompt_chars": len(persona),
        })
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(inst).to_parquet(OUT / f"instances_{BENCHMARK}.parquet", index=False)
    pd.DataFrame(meta).to_csv(OUT / f"meta_{BENCHMARK}.csv", index=False)
    print(f"{len(inst)} scenarios at {HARNESS_COMMIT[:12]}; prompts match r23.json for {n_checked} -> {OUT}")


if __name__ == "__main__":
    main()
