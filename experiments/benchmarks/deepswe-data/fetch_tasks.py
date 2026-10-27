"""DeepSWE v1.1 task instructions and task.toml metadata.

Source: github.com/datacurve-ai/deep-swe (Apache-2.0 for Datacurve's task specs; upstream code
keeps its own license, see PROVENANCE.md), pinned to COMMIT, the v1.1 release state that
Datacurve's own oracle audit used. The repo has no v1.1 tag (only v1.0.0); instruction.md is
byte-identical from the "DeepSWE V1.1" commit 8cae598 to main 0b9fabb (2026-08-26). Later
commits change only task.toml (network_mode, verifier.collect, agent timeout 5400 -> 10800 s).

Each task lives at tasks/<task_id>/ with ``instruction.md`` (the prompt the agent sees, read
verbatim), ``task.toml`` and ``tests/config.json`` (only its f2p/p2p test counts are used).
The Hugging Face copy (datacurve/deep-swe, gated) was last changed on 2026-06-02 and so holds
v1.0, not v1.1; it is not used. The task pages carry a no-training canary, so outputs go only
to the gitignored data/ tree; never commit them.

Writes:
  data/instances/instances_deepswe-v1.1.parquet   benchmark, instance_id, prompt, prompt_sha12
  data/instances/meta_deepswe-v1.1.csv            task.toml metadata, test counts, upstream
      license, Epoch defect labels (epoch_defects.csv) and community issue refs
      (community_issues.csv)
Caches the sparse checkout in data/downloads/deep-swe/.

Run: python experiments/benchmarks/deepswe-data/fetch_tasks.py
"""

import hashlib
import json
import re
import subprocess
import tomllib
from pathlib import Path

import pandas as pd

REPO_URL = "https://github.com/datacurve-ai/deep-swe.git"
COMMIT = "3cda4081fed96103a6395de39c85e9b20275e307"  # "Updated README for V1.1", 2026-06-14
PROVENANCE_COMMIT = "6db64a40f3318d8659238ff34a8cc4b491c49205"  # adds PROVENANCE.md, 2026-07-10
BENCHMARK = "deepswe-v1.1"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "data" / "instances"
CACHE = ROOT / "data" / "downloads" / "deep-swe"
# Wrong language tags in task.toml, reported in datacurve-ai/deep-swe#53 and checked against the
# upstream repositories.
LANGUAGE_FIX = {"koota-entity-snapshot-rollback": "typescript",  # #53 says javascript; repo is TypeScript
                "prometheus-transactional-reload-status": "go",
                "httpx-deterministic-cookie-store": "python"}


def checkout(dest: Path) -> Path:
    """Sparse, blob-filtered checkout of instructions, task.toml and test config at COMMIT."""
    def git(*args):
        subprocess.run(["git", "-C", str(dest), *args], check=True,
                       env={"GIT_LFS_SKIP_SMUDGE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"})
    if not (dest / ".git").exists():
        dest.mkdir(parents=True, exist_ok=True)
        git("init", "-q")
        git("remote", "add", "origin", REPO_URL)
        git("sparse-checkout", "set", "--no-cone", "tasks/*/instruction.md",
            "tasks/*/task.toml", "tasks/*/tests/config.json")
    git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", COMMIT, PROVENANCE_COMMIT)
    git("checkout", "-q", COMMIT)
    return dest


def provenance(root: Path) -> dict:
    """task_id -> upstream license, from the PROVENANCE.md table (added after COMMIT)."""
    text = subprocess.run(["git", "-C", str(root), "show", f"{PROVENANCE_COMMIT}:PROVENANCE.md"],
                          check=True, capture_output=True, text=True).stdout
    rows = re.findall(r"^\|\s*([a-z0-9-]+)\s*\|\s*[^|]+\|\s*([^|]+?)\s*\|$", text, flags=re.M)
    return {t: lic for t, lic in rows}


def main() -> None:
    root = checkout(CACHE)
    licenses = provenance(root)
    epoch = pd.read_csv(HERE / "epoch_defects.csv").set_index("instance_id")
    issues = pd.read_csv(HERE / "community_issues.csv")
    issue_refs = issues.groupby("instance_id")["ref"].apply(lambda s: ";".join(map(str, sorted(set(s)))))
    task_dirs = sorted(p.parent for p in root.glob("tasks/*/instruction.md"))
    inst, meta = [], []
    for d in task_dirs:
        prompt = (d / "instruction.md").read_text(encoding="utf-8")
        toml = tomllib.loads((d / "task.toml").read_text(encoding="utf-8"))
        tests = json.loads((d / "tests" / "config.json").read_text(encoding="utf-8"))
        md, env, agent, ver = toml["metadata"], toml["environment"], toml["agent"], toml["verifier"]
        assert md["task_id"] == d.name == toml["task"]["name"].removeprefix("datacurve/"), d
        inst.append({"benchmark": BENCHMARK, "instance_id": d.name, "prompt": prompt,
                     "prompt_sha12": hashlib.sha256(prompt.encode()).hexdigest()[:12]})
        meta.append({
            "instance_id": d.name,
            "repository": md["repository_url"].removeprefix("https://github.com/").removesuffix(".git"),
            "repository_url": md["repository_url"],
            "upstream_license": licenses.get(d.name),
            "language": md["language"],
            "language_corrected": LANGUAGE_FIX.get(d.name, md["language"]),
            "category": md.get("category"),
            "display_title": md.get("display_title"),
            "base_commit_hash": md.get("base_commit_hash"),
            "n_f2p_tests": len(tests.get("f2p_node_ids", [])),
            "n_p2p_tests": len(tests.get("p2p_node_ids", [])),
            "agent_timeout_sec": agent.get("timeout_sec"),
            "verifier_timeout_sec": ver.get("timeout_sec"),
            "cpus": env.get("cpus"), "memory_mb": env.get("memory_mb"),
            "allow_internet": env.get("allow_internet"),
            "prompt_chars": len(prompt),
            "epoch_defect": epoch["epoch_defect"].get(d.name, ""),
            "epoch_mechanism_group": epoch["mechanism_group"].get(d.name, ""),
            "community_issues": issue_refs.get(d.name, ""),
        })
    assert len(inst) == 113, len(inst)
    assert set(epoch.index) <= {m["instance_id"] for m in meta}
    assert set(issues.instance_id) <= {m["instance_id"] for m in meta}
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(inst).to_parquet(OUT / f"instances_{BENCHMARK}.parquet", index=False)
    pd.DataFrame(meta).to_csv(OUT / f"meta_{BENCHMARK}.csv", index=False)
    print(f"{len(inst)} tasks at {COMMIT[:12]} ({sum(bool(m['epoch_defect']) for m in meta)} Epoch-named) -> {OUT}")


if __name__ == "__main__":
    main()
