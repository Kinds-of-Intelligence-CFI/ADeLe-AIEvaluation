"""ProgramBench task texts: the agent's instruction plus the documentation in its workspace.

The agent gets no task-specific text in its messages. The mini-SWE-agent prompt is the
same for all 200 tasks; what differs is /workspace in the task's Docker image
(``programbench/<owner>_1776_<repo>.<sha>:task_cleanroom_v6``): an execute-only
``./executable`` plus the documentation, examples and assets left after source removal.
The agent is told to "explore all documentation files" first.

So a task's prompt here is: the benchmark instruction (mini-SWE-agent ``programbench.yaml``
system template plus the task part of the instance template, i.e. without the generic
"Command Execution Rules" and "Useful command examples" scaffold sections), then a listing
of /workspace (path and size of every file), then the full text of each documentation file.

A documentation file is a UTF-8 text file that is not a licence (LICENSE*, COPYING*, ...),
whose basename has no extension or a prose/manual extension (.md .rst .txt .adoc .org .texi
.pod .man and man sections .1-.9), and which is not under a top-level fixture directory
(assets/, testdata/, tests/, data/, fonts/, examples/, ...). Everything else (licences, CSS,
JSON/YAML, SVG, fonts, test fixtures, binaries) is only listed. Inlining every text file
instead gives prompts up to 7.1M chars (median 12k), mostly from fixture files. The
per-file parquet below keeps all texts so prompts can be recomposed under another rule.

Workspace contents come from the image's last layer only (no 33 GB of clone layers): that
step wipes .git, re-inits it and commits the whole cleaned workspace, so the layer's git
objects hold every committed file. ``./executable`` is moved in after the commit and is
listed but not read. Files ignored by the workspace's .gitignore would be missed; the
script lists any non-git file in the layer to show there are none besides the executable.

Sources (all public, no login):
  github.com/facebookresearch/ProgramBench   v1.2.5 = COMMIT; task.yaml + tests.json per task
  github.com/SWE-agent/mini-swe-agent        v2.4.5 = MSWEA_COMMIT; programbench.yaml
  Docker Hub programbench/*:task_cleanroom_v6 last layer (blob GETs, not manifest pulls)

Texts are third-party docs (various licences) and go only to the gitignored data/ tree.

Writes:
  data/instances/instances_programbench.parquet   benchmark, instance_id, prompt, prompt_sha12
  data/instances/meta_programbench.csv            per-task metadata
  data/instances/workspace_programbench.parquet   one row per committed workspace file: instance_id,
      path, type, size_bytes, is_text, is_licence, in_prompt, text (to recompose prompts)
  data/downloads/programbench/layers/              cached layer blobs (~1.9 GB)

Run: python experiments/benchmarks/programbench-data/fetch_tasks.py
"""

import hashlib
import json
import re
import subprocess
import tarfile
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import yaml

REPO_URL = "https://github.com/facebookresearch/ProgramBench.git"
TAG, COMMIT = "v1.2.5", "27f02157c785f8da3647aa6dbbe6b9137f99f10e"
MSWEA_TAG, MSWEA_COMMIT = "v2.4.5", "e187bcb2ff5825d85761a6f9c1f98c9fa6cfbc79"
MSWEA_YAML = (f"https://raw.githubusercontent.com/SWE-agent/mini-swe-agent/{MSWEA_COMMIT}/"
              "src/minisweagent/config/benchmarks/programbench.yaml")
IMAGE_TAG = "task_cleanroom_v6"
BENCHMARK = "programbench"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "instances"
CACHE = ROOT / "data" / "downloads" / "programbench"
GIT_ENV = {"GIT_LFS_SKIP_SMUDGE": "1", "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"}
SCAFFOLD_CUT = "## Command Execution Rules"
LICENCE_NAMES = ("LICENSE", "LICENCE", "COPYING", "COPYRIGHT", "UNLICENSE")
DOC_NAME = re.compile(r"^([^.]+|.+\.(md|markdown|rst|txt|adoc|asciidoc|org|texi|texinfo|pod|man|[1-9]))$", re.I)
FIXTURE_DIRS = {"assets", "testdata", "test", "tests", "data", "fonts", "fixtures", "samples", "sample",
                "examples", "example"}


def is_licence(path: str) -> bool:
    return path.rsplit("/", 1)[-1].upper().startswith(LICENCE_NAMES)


def is_doc(path: str) -> bool:
    parts = path.split("/")
    return bool(DOC_NAME.match(parts[-1])) and not is_licence(path) and not (
        len(parts) > 1 and parts[0].lower() in FIXTURE_DIRS)


def git(*args, cwd=None, inp=None) -> bytes:
    return subprocess.run(["git", *args], cwd=cwd, input=inp, check=True, capture_output=True, env=GIT_ENV).stdout


def checkout(dest: Path) -> Path:
    """Sparse, blob-filtered checkout of only task.yaml and tests.json at COMMIT."""
    git("init", "-q", str(dest))
    for a in [("remote", "add", "origin", REPO_URL),
              ("sparse-checkout", "set", "--no-cone", "src/programbench/data/tasks/*/task.yaml",
               "src/programbench/data/tasks/*/tests.json"),
              ("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", COMMIT),
              ("checkout", "-q", COMMIT)]:
        git("-C", str(dest), *a)
    return dest


def fetch(url: str, headers: dict | None = None, tries: int = 5) -> bytes:
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=300).read()
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(10 * (i + 1))


def instruction() -> str:
    agent = yaml.safe_load(fetch(MSWEA_YAML))["agent"]
    task_part = agent["instance_template"].split(SCAFFOLD_CUT)[0]
    assert "{{" not in agent["system_template"] + task_part
    return agent["system_template"].rstrip() + "\n\n" + task_part.rstrip() + "\n"


def last_layer(iid: str) -> dict:
    """Last layer of the cleanroom image, from the Docker Hub web API (no pull counted)."""
    repo = iid.replace("__", "_1776_")
    img = json.loads(fetch(f"https://hub.docker.com/v2/repositories/programbench/{repo}/tags/{IMAGE_TAG}/images"))
    layers = [l for l in img[0]["layers"] if l.get("digest")]
    assert "git checkout -f origin/clean" in layers[-1]["instruction"], iid
    return {"image_digest": img[0]["digest"], "image_size": img[0]["size"], **layers[-1]}


def download(iid: str, layer: dict) -> Path:
    path = CACHE / "layers" / (layer["digest"].split(":")[1] + ".tar.gz")
    if path.exists():
        return path
    repo = "programbench/" + iid.replace("__", "_1776_")
    tok = json.loads(fetch(f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:{repo}:pull"))
    data = fetch(f"https://registry-1.docker.io/v2/{repo}/blobs/{layer['digest']}",
                 {"Authorization": f"Bearer {tok['token']}"})
    assert "sha256:" + hashlib.sha256(data).hexdigest() == layer["digest"], iid
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")
    tmp.write_bytes(data)
    tmp.rename(path)
    return path


def workspace(layer_path: Path) -> tuple[list[dict], dict[str, bytes], list[str]]:
    """Committed files of /workspace (path, size, mode) with contents, plus non-git layer files."""
    with tempfile.TemporaryDirectory() as tmp, tarfile.open(layer_path, "r:gz") as tf:
        members = [m for m in tf.getmembers() if m.name.startswith("workspace/")]
        gitm = [m for m in members if m.name.startswith("workspace/.git/") and "/.wh." not in m.name
                and (m.isfile() or m.isdir())]
        tf.extractall(tmp, members=gitm, filter="data")
        gd = str(Path(tmp) / "workspace" / ".git")
        entries = []
        for line in git("--git-dir", gd, "ls-tree", "-r", "-l", "HEAD").decode().splitlines():
            meta, path = line.split("\t", 1)
            mode, typ, sha, size = meta.split()
            entries.append({"path": path, "mode": mode, "type": typ, "sha": sha,
                            "size": int(size) if size != "-" else None})
        blobs = [e for e in entries if e["type"] == "blob"]
        out = git("--git-dir", gd, "cat-file", "--batch", inp="".join(e["sha"] + "\n" for e in blobs).encode())
        contents, i = {}, 0
        for e in blobs:
            nl = out.index(b"\n", i)
            size = int(out[i:nl].split()[2])
            contents[e["path"]] = out[nl + 1:nl + 1 + size]
            i = nl + 1 + size + 1
        tracked = {e["path"] for e in entries}
        other = sorted(m.name[len("workspace/"):] for m in members
                       if m.isfile() and not m.name.startswith("workspace/.git/") and "/.wh." not in m.name
                       and m.name[len("workspace/"):] not in tracked)
    return entries, contents, other


def as_text(b: bytes) -> str | None:
    if b"\0" in b:
        return None
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return None


def build(iid: str, head: str) -> tuple[dict, dict, list[dict]]:
    layer = last_layer(iid)
    entries, contents, other = workspace(download(iid, layer))
    print(f"{iid}: {len(entries)} files", flush=True)
    texts = {p: as_text(b) for p, b in contents.items()}
    listing = "\n".join(f"{e['size'] if e['size'] is not None else '-':>10}  {e['path']}"
                        + ("" if e["type"] == "blob" else f"  ({e['type']})")
                        + ("" if texts.get(e["path"]) is not None and is_doc(e["path"]) else "  (not inlined)")
                        for e in entries)
    listing += "".join(f"\n{'-':>10}  {p}  (not committed; execute-only)" if p == "executable"
                       else f"\n{'-':>10}  {p}  (not committed)" for p in other)
    doc = {p: t for p, t in texts.items() if t is not None and is_doc(p)}
    docs = "".join(f"\n===== {p} =====\n{t.rstrip()}\n" for p, t in doc.items())
    prompt = (head + "\n## Workspace contents (/workspace)\n\n" + listing
              + "\n\n## Documentation files in /workspace\n" + docs)
    files = [{"instance_id": iid, "path": e["path"], "type": e["type"], "size_bytes": e["size"],
              "is_text": texts.get(e["path"]) is not None, "is_licence": is_licence(e["path"]),
              "in_prompt": e["path"] in doc,
              "text": texts.get(e["path"])} for e in entries]
    n_text = sum(t is not None for t in texts.values())
    m = {"workspace_files": len(entries), "workspace_text_files": n_text,
         "workspace_binary_files": len(contents) - n_text,
         "workspace_text_chars": sum(len(t) for t in texts.values() if t is not None),
         "doc_files": len(doc), "doc_chars": sum(len(t) for t in doc.values()),
         "readme_present": any(p.rsplit("/", 1)[-1].upper().startswith("README") for p in doc),
         "workspace_binary_bytes": sum(len(b) for p, b in contents.items() if texts[p] is None),
         "untracked_files": ";".join(other), "image_digest": layer["image_digest"],
         "image_size_bytes": layer["image_size"], "last_layer_digest": layer["digest"],
         "last_layer_bytes": layer["size"]}
    return ({"benchmark": BENCHMARK, "instance_id": iid, "prompt": prompt,
             "prompt_sha12": hashlib.sha256(prompt.encode()).hexdigest()[:12]}, m, files)


def main() -> None:
    head = instruction()
    with tempfile.TemporaryDirectory() as tmp:
        root = checkout(Path(tmp))
        task_dirs = sorted(p.parent for p in root.glob("src/programbench/data/tasks/*/task.yaml")
                           if not p.parent.name.startswith("testorg__"))  # test fixture, not a task
        tasks = {}
        for d in task_dirs:
            ty = yaml.safe_load((d / "task.yaml").read_text())
            br = json.loads((d / "tests.json").read_text())["branches"]
            active = [b for b, v in br.items() if not v["ignored"]]
            reasons = [r["id"] for v in br.values() for t in v.get("ignored_tests") or [] for r in t["reasons"]]
            tasks[d.name] = {
                "instance_id": d.name, "repository": ty["repository"], "commit": ty["commit"],
                "language": ty["language"], "difficulty": ty.get("difficulty"),
                "test_branches": len(br), "test_branches_active": len(active),
                "tests_listed_active": sum(len(br[b]["tests"]) for b in active),
                "ignored_tests": sum(len(v.get("ignored_tests") or []) for v in br.values()),
                **{f"ignored_reason_{k}": reasons.count(k) for k in sorted(set(reasons))},
            }
    assert len(tasks) == 200, len(tasks)
    with ThreadPoolExecutor(8) as pool:
        res = dict(zip(tasks, pool.map(lambda i: build(i, head), tasks)))
    inst = [r[0] for r in res.values()]
    meta = [{**tasks[i], **res[i][1], "prompt_chars": len(res[i][0]["prompt"])} for i in tasks]
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(inst).to_parquet(OUT / f"instances_{BENCHMARK}.parquet", index=False)
    meta = pd.DataFrame(meta)
    reasons = [c for c in meta.columns if c.startswith("ignored_reason_")]
    meta[reasons] = meta[reasons].fillna(0).astype(int)
    meta.to_csv(OUT / f"meta_{BENCHMARK}.csv", index=False)
    pd.DataFrame([f for r in res.values() for f in r[2]]).to_parquet(OUT / f"workspace_{BENCHMARK}.parquet", index=False)
    print(f"{len(inst)} tasks from {TAG} ({COMMIT[:12]}), prompt from mini-swe-agent {MSWEA_TAG} -> {OUT}")


if __name__ == "__main__":
    main()
