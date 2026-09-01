"""Run the full rivercross MMs pilot with a hidden API-key prompt."""

from __future__ import annotations

import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
REPO = RIVERCROSS.parent.parent
RUNNER = HERE / "run_prompt_annotation.py"
ANALYZER = HERE / "analyze_mms_delta.py"
STATE_PROMPT = RIVERCROSS / "prompts" / "generated" / "prompt_MMs_1b_state_visible.txt"
HISTORY_PROMPT = RIVERCROSS / "prompts" / "generated" / "prompt_MMs_1b_history_only.txt"
LABEL_DIR = HERE / "labels"
LOCAL_KEY_FILE = HERE / "local_anthropic_key.txt"


def run(cmd: list[str], env: dict[str, str]) -> None:
    print()
    print("Running: " + " ".join(cmd))
    subprocess.run(cmd, cwd=REPO, env=env, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-4-20250514")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    env = os.environ.copy()
    if not args.dry_run and not env.get("ANTHROPIC_API_KEY"):
        key = ""
        if LOCAL_KEY_FILE.exists():
            key = LOCAL_KEY_FILE.read_text(encoding="utf-8").strip()
            if key == "PASTE_ANTHROPIC_API_KEY_HERE":
                key = ""
        if not key:
            key = getpass.getpass("Paste ANTHROPIC_API_KEY (hidden): ")
        if not key.strip():
            raise SystemExit("No API key entered.")
        env["ANTHROPIC_API_KEY"] = key.strip()

    common = [sys.executable, str(RUNNER), "--model", args.model]
    if args.dry_run:
        common.append("--dry-run")

    run(common + ["--prompt", str(STATE_PROMPT), "--name", "mms_state_visible_sonnet"], env)
    run(common + ["--prompt", str(HISTORY_PROMPT), "--name", "mms_history_only_sonnet"], env)

    if args.dry_run:
        return

    state_labels = LABEL_DIR / "mms_state_visible_sonnet.csv"
    history_labels = LABEL_DIR / "mms_history_only_sonnet.csv"
    run([
        sys.executable,
        str(ANALYZER),
        "--state-visible-labels",
        str(state_labels),
        "--history-only-labels",
        str(history_labels),
    ], env)


if __name__ == "__main__":
    main()
