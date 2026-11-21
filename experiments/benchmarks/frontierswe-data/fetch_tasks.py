"""FrontierSWE v2 task instructions and task.toml metadata.

Source: github.com/Proximal-Labs/frontier-swe-v2 (no license file), tag v2.0.0 pinned
to its commit. Each task lives at tasks/<task>/ with an ``instruction.md`` (the prompt
Harbor gives the agent, read verbatim) and a ``task.toml``. Most instructions are short
and point the agent to ``/app/README.md`` for the full contract; that README is copied
into the image from the task's environment/ tree. The prompt is what the agent sees (Pablo,
2026-10-01): ``instruction.md`` verbatim and, when it cites the README (25 of 34), a blank
line, the header line ``Contents of <container path>:`` and the README verbatim. Task text
goes only to the gitignored data/instances/ tree; never commit it.

Writes:
  data/instances/instances_frontierswe-v2.parquet
      benchmark, instance_id, prompt, prompt_sha12, has_readme   (prompt = instruction.md [+ README])
  data/instances/meta_frontierswe-v2.csv
      instance_id plus README category, site slug, task.toml metadata, resources, timeouts
  data/instances/readme_frontierswe-v2.parquet
      instance_id, container_path, source_path, text, text_sha12   (agent-visible README)

Run: python experiments/benchmarks/frontierswe-data/fetch_tasks.py
Then: adele instances register data/instances/instances_frontierswe-v2.parquet --benchmark frontierswe-v2
(remove the old frontierswe-v2 row of data/instances/INSTANCES.tsv first if the prompt changed)
"""

import hashlib
import re
import subprocess
import tempfile
import tomllib
from pathlib import Path

import pandas as pd

REPO_URL = "https://github.com/Proximal-Labs/frontier-swe-v2.git"
TAG, COMMIT = "v2.0.0", "da83f84f8fbcec3cbf0f2b17c98ebc811355c2df"
BENCHMARK = "frontierswe-v2"
OUT = Path(__file__).resolve().parents[3] / "data" / "instances"
# Agent-visible README per task: the file the Dockerfile copies to the path the
# instruction cites. Default is environment/workspace/README.md -> /app/README.md.
README_SOURCE = {
    "flight-sim-renderer-in-opengl": ("environment/app/README.md", "/app/README.md"),
    "snooker-prediction": ("environment/workspace/data/README.md", "/app/data/README.md"),
}


def checkout(dest: Path) -> Path:
    """Sparse, blob-filtered checkout of the files read below at COMMIT."""
    def git(*args):
        subprocess.run(["git", "-C", str(dest), *args], check=True,
                       env={"GIT_LFS_SKIP_SMUDGE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"})
    git("init", "-q")
    git("remote", "add", "origin", REPO_URL)
    git("sparse-checkout", "set", "--no-cone", "README.md", "tasks/*/instruction.md", "tasks/*/task.toml",
        "tasks/*/job.yaml", "tasks/*/environment/workspace/README.md", "tasks/*/environment/app/README.md",
        "tasks/*/environment/workspace/data/README.md")
    git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", COMMIT)
    git("checkout", "-q", COMMIT)
    return dest


def readme_table(root: Path) -> dict:
    """Task dir -> (number, display name, categories) from the top-level README table."""
    rows = re.findall(r"^\| (\d\d) \| \[([^\]]+)\]\(tasks/([^/]+)/\) \| ([^|]+) \|$",
                      (root / "README.md").read_text(encoding="utf-8"), re.M)
    return {d: (int(n), name, cats.strip()) for n, name, d, cats in rows}


def sha12(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def with_readme(instruction: str, container_path: str, readme: str) -> str:
    """Instruction verbatim, one blank line, a header line, then the README verbatim."""
    sep = "\n" if instruction.endswith("\n") else "\n\n"
    return f"{instruction}{sep}Contents of {container_path}:\n{readme}"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = checkout(Path(tmp))
        table = readme_table(root)
        task_dirs = sorted(p.parent for p in root.glob("tasks/*/instruction.md"))
        assert len(task_dirs) == len(table) == 34, (len(task_dirs), len(table))
        inst, meta, readmes = [], [], []
        for d in task_dirs:
            prompt = (d / "instruction.md").read_text(encoding="utf-8")
            toml = tomllib.loads((d / "task.toml").read_text(encoding="utf-8"))
            task, md = toml.get("task", {}), toml.get("metadata", {})
            env, agent, ver = toml.get("environment", {}), toml.get("agent", {}), toml.get("verifier", {})
            num, name, cats = table[d.name]
            src, dst = README_SOURCE.get(d.name, ("environment/workspace/README.md", "/app/README.md"))
            readme = d / src
            cites_readme = dst in prompt
            if cites_readme:
                assert readme.exists(), (d.name, src)
                text = readme.read_text(encoding="utf-8")
                readmes.append({"instance_id": d.name, "container_path": dst, "source_path": f"tasks/{d.name}/{src}",
                                "text": text, "text_sha12": sha12(text)})
            full = with_readme(prompt, dst, text) if cites_readme else prompt
            inst.append({"benchmark": BENCHMARK, "instance_id": d.name, "prompt": full,
                         "prompt_sha12": sha12(full), "has_readme": cites_readme})
            meta.append({
                "instance_id": d.name,
                "num": num, "name": name, "categories": cats,
                "toml_name": task.get("name"),
                "difficulty": md.get("difficulty"), "toml_category": md.get("category"),
                "oracle_reward_threshold": md.get("oracle_reward_threshold"),
                "keywords": ";".join(task.get("keywords", []) or []),
                "agent_timeout_sec": agent.get("timeout_sec"),
                "verifier_timeout_sec": ver.get("timeout_sec"),
                "verifier_environment_mode": ver.get("environment_mode"),
                "cpus": env.get("cpus"), "memory_mb": env.get("memory_mb"), "storage_mb": env.get("storage_mb"),
                "gpus": env.get("gpus", 0), "gpu_types": ";".join(env.get("gpu_types", []) or []),
                "network_mode": env.get("network_mode"),
                "has_job_yaml": (d / "job.yaml").exists(),
                "instruction_chars": len(prompt),
                "prompt_chars": len(full),
                "prompt_cites_readme": cites_readme,
                "readme_chars": len(text) if cites_readme else None,
                "description": task.get("description"),
            })
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(inst).to_parquet(OUT / f"instances_{BENCHMARK}.parquet", index=False)
    pd.DataFrame(meta).to_csv(OUT / f"meta_{BENCHMARK}.csv", index=False)
    pd.DataFrame(readmes).to_parquet(OUT / f"readme_{BENCHMARK}.parquet", index=False)
    print(f"{len(inst)} tasks ({len(readmes)} cite a README) from {TAG} ({COMMIT[:12]}) -> {OUT}")


if __name__ == "__main__":
    main()
