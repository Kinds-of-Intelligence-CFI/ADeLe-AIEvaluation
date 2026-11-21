#!/usr/bin/env bash
# Prepare a fresh machine (e.g. a Claude Code cloud VM) to judge a pinned subagent run.
# Usage: scripts/cloud/bootstrap.sh <run>    e.g. scripts/cloud/bootstrap.sh w1v1-other
# Needs HF_TOKEN: read on the private instance store, write on adele-cloud-runs. See experiments/benchmarks/mass-annotation/CLOUD.md.
set -euo pipefail

RUN="${1:?usage: bootstrap.sh <run>}"
REPO="$(git rev-parse --show-toplevel)"
cd "$REPO"

# Judge I/O outside the repo; agent files from the repo. adele reads .env (gitignored) on start.
JUDGE_IO="${ADELE_JUDGE_IO:-$HOME/judge-io}"
touch .env
grep -q '^ADELE_JUDGE_IO=' .env || echo "ADELE_JUDGE_IO=$JUDGE_IO" >> .env
grep -q '^ADELE_AGENTS_DIR=' .env || echo "ADELE_AGENTS_DIR=$REPO/.claude/agents" >> .env

command -v uv >/dev/null || python3 -m pip install --quiet uv
[ -d .venv ] || uv venv --quiet
uv pip install --quiet -e '.[agentic]'
ADELE="$REPO/.venv/bin/adele"
sh scripts/install-hooks.sh  # the pre-commit contamination check

# The run's benchmarks, from its manifest; each file is checked against the committed sha256.
BENCHES=$(python3 -c "import json,sys; print(' '.join(json.load(open(sys.argv[1]))['frozen']['tasks']['benchmarks']))" \
  "experiments/benchmarks/mass-annotation/runs/$RUN/manifest.json")
for b in $BENCHES; do "$ADELE" instances fetch --benchmark "$b"; done

# Re-pin: refuses unless every frozen input is identical, then writes the prompt files this machine lacks.
SPEC=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['spec_file'])" \
  "experiments/benchmarks/mass-annotation/runs/$RUN/manifest.json")
"$ADELE" mass pin "$SPEC"
# State judged elsewhere (ledger, answers) from the private HF dataset, so `check` can verify every answer.
"$REPO/.venv/bin/python" scripts/cloud/hf_sync.py pull "$RUN"
"$ADELE" mass status "$RUN" | tail -3
echo "ready: judges must run in $REPO (pass --cwd $REPO to next, collect and check)"
