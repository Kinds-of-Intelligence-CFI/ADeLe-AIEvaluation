"""Terminal-Bench-Science v0.1.0 task instructions and task.toml metadata.

Source: github.com/harbor-framework/terminal-bench-science (Apache-2.0), tag v0.1.0
pinned to its commit. Each task lives at tasks/<domain>/<field>/<task>/ with an
``instruction.md`` (the text the agent sees, read verbatim as the Terminal-Bench 4.0
loader does) and a ``task.toml``. The text carries a no-training canary GUID, so the
outputs go only to the gitignored data/instances/ tree; never commit them.

Writes:
  data/instances/instances_terminal-bench-science-0.1.parquet
      benchmark, instance_id, prompt, prompt_sha12
  data/instances/meta_terminal-bench-science-0.1.csv
      instance_id plus task.toml metadata (domain, field, subfield, tags,
      expert_time_estimate_hours, resources, timeouts, ...)

Run: python experiments/benchmarks/tbsci-data/fetch_tasks.py
"""

import hashlib
import subprocess
import tempfile
import tomllib
from pathlib import Path

import pandas as pd

REPO_URL = "https://github.com/harbor-framework/terminal-bench-science.git"
TAG, COMMIT = "v0.1.0", "f81afac4f11048e77a15dfc8fb1dbfb897fea0ce"
BENCHMARK = "terminal-bench-science-0.1"
OUT = Path(__file__).resolve().parents[3] / "data" / "instances"


def checkout(dest: Path) -> Path:
    """Sparse, blob-filtered checkout of only instruction.md and task.toml at COMMIT."""
    def git(*args):
        subprocess.run(["git", "-C", str(dest), *args], check=True,
                       env={"GIT_LFS_SKIP_SMUDGE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"})
    git("init", "-q")
    git("remote", "add", "origin", REPO_URL)
    git("sparse-checkout", "set", "--no-cone", "tasks/*/*/*/instruction.md", "tasks/*/*/*/task.toml")
    git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", COMMIT)
    git("checkout", "-q", COMMIT)
    return dest


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = checkout(Path(tmp))
        task_dirs = sorted(p.parent for p in root.glob("tasks/*/*/*/instruction.md"))
        inst, meta = [], []
        for d in task_dirs:
            prompt = (d / "instruction.md").read_text(encoding="utf-8")
            toml = tomllib.loads((d / "task.toml").read_text(encoding="utf-8"))
            task, md = toml.get("task", {}), toml.get("metadata", {})
            env, agent, ver = toml.get("environment", {}), toml.get("agent", {}), toml.get("verifier", {})
            assert task.get("name") == f"terminal-bench-science/{d.name}", (d, task.get("name"))
            inst.append({"benchmark": BENCHMARK, "instance_id": d.name, "prompt": prompt,
                         "prompt_sha12": hashlib.sha256(prompt.encode()).hexdigest()[:12]})
            meta.append({
                "instance_id": d.name,
                "path": str(d.relative_to(root)),
                "domain": md.get("domain"), "field": md.get("field"), "subfield": md.get("subfield"),
                "tags": ";".join(md.get("tags", []) or []),
                "expert_time_estimate_hours": md.get("expert_time_estimate_hours"),
                "author_organization": md.get("author_organization"),
                "agent_timeout_sec": agent.get("timeout_sec"),
                "verifier_timeout_sec": ver.get("timeout_sec"),
                "cpus": env.get("cpus"), "memory_mb": env.get("memory_mb"),
                "gpus": env.get("gpus"), "gpu_types": ";".join(env.get("gpu_types", []) or []),
                "network_mode": env.get("network_mode"),
                "prompt_chars": len(prompt),
                "description": task.get("description"),
            })
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(inst).to_parquet(OUT / f"instances_{BENCHMARK}.parquet", index=False)
    pd.DataFrame(meta).to_csv(OUT / f"meta_{BENCHMARK}.csv", index=False)
    print(f"{len(inst)} tasks from {TAG} ({COMMIT[:12]}) -> {OUT}")


if __name__ == "__main__":
    main()
