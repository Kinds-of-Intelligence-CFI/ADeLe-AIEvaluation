"""Harbor-Adapter: per-trial verifier reward and model/agent ids for the sets wave 2 labels.

Source: HF dataset kendx/Harbor-Adapter at REVISION (public, not gated; licence "other", no terms
given). Pablo cleared it for analysis only: cite it, never redistribute its traces. Layout:
  harbor_adapters.manifest.parquet            one row per cell (benchmark, task_name, agent, model,
                                              trial_ids: up to the 5 most recent trials)
  data/harbor_adapters/<benchmark>/NNNNN.parquet   one row per trial: trial_id, archive (.tar.gz
                                              bytes of the trial directory), archive_sha256
Each archive holds result.json (task, agent, model, verifier_result.rewards, tokens, timings,
exception_info), config.json, agent/ (trajectory and native logs) and verifier/ (reward.txt,
test output). The task text is not stored per task; it is only inside the trajectories (the first
user step) and in the harbor-datasets repo that config.task.git_url/git_commit_id point to.

What this does, per set in SETS: download one shard at a time into data/downloads/harbor-adapter/,
check its sha256 against the HF LFS pointer, stream every row, check archive_sha256, read only
result.json and verifier/reward.txt from the in-memory tarball (nothing is extracted to disk),
write one CSV row per trial, then delete the shard unless --keep-shards. Shards are deleted by
default because the three sets are ~6.5 GB and the disk had ~5 GB free on 2026-10-11; they can be
fetched again at the pinned revision. A finished shard's CSV is kept, so a rerun resumes.

Writes (all gitignored, no task text, no trace content):
  data/downloads/harbor-adapter/README.md, harbor_adapters.manifest.parquet
  data/downloads/harbor-adapter/trials/<set>__<shard>.csv    per shard
  data/downloads/harbor-adapter/trials.csv                   all trials, joined to the manifest
  data/downloads/harbor-adapter/SOURCES.tsv                  shard, sha256, bytes, rows

Run: python -I experiments/benchmarks/harbor-adapter-data/read_rewards.py [--keep-shards]
"""

import argparse
import hashlib
import io
import json
import tarfile
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "downloads" / "harbor-adapter"
REPO = "kendx/Harbor-Adapter"
REVISION = "fa3538157a4b372b8ed36723ba0aa6dc30f6e22e"  # 2026-07-11
SETS = ["gpqa-diamond", "arc-agi-2", "terminal-bench"]
MANIFEST = "harbor_adapters.manifest.parquet"


def fetch(name: str) -> Path:
    return Path(hf_hub_download(REPO, name, repo_type="dataset", revision=REVISION, local_dir=OUT))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def read_trial(archive: bytes) -> dict:
    """result.json fields and reward.txt from one trial tarball, read in memory."""
    result, reward_txt = None, None
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r|gz") as tar:
        for m in tar:
            if not m.isfile():
                continue
            rel = m.name.split("/", 1)[-1]
            if rel == "result.json":
                result = json.load(tar.extractfile(m))
            elif rel == "verifier/reward.txt":
                reward_txt = tar.extractfile(m).read().decode(errors="replace").strip()[:32]
    r = result or {}
    ai, ar = r.get("agent_info") or {}, r.get("agent_result") or {}
    rewards = (r.get("verifier_result") or {}).get("rewards") or {}
    task = (r.get("config") or {}).get("task") or r.get("task_id") or {}
    exc = r.get("exception_info") or {}
    return {
        "task_name": r.get("task_name"),
        "agent_name": ai.get("name"), "agent_version": ai.get("version"),
        "model_name": (ai.get("model_info") or {}).get("name"),
        "model_provider": (ai.get("model_info") or {}).get("provider"),
        "config_model_name": ((r.get("config") or {}).get("agent") or {}).get("model_name"),
        "reward": rewards.get("reward"), "rewards_json": json.dumps(rewards, sort_keys=True) if rewards else None,
        "reward_txt": reward_txt,
        "exception_type": exc.get("exception_type") if isinstance(exc, dict) else str(exc)[:80],
        "n_input_tokens": ar.get("n_input_tokens"), "n_output_tokens": ar.get("n_output_tokens"),
        "n_cache_tokens": ar.get("n_cache_tokens"), "cost_usd": ar.get("cost_usd"),
        "started_at": r.get("started_at"), "finished_at": r.get("finished_at"),
        "task_path": task.get("path"), "task_git_commit": task.get("git_commit_id"),
        "task_checksum": r.get("task_checksum"), "source": r.get("source"),
        "has_result_json": result is not None,
    }


def process_shard(name: str, want_sha: str, keep: bool) -> dict:
    bench, shard = name.split("/")[-2], Path(name).stem
    part = OUT / "trials" / f"{bench}__{shard}.csv"
    if part.exists():
        return {"shard": name, "sha256": want_sha, "rows": len(pd.read_csv(part)), "status": "cached"}
    path = fetch(name)
    got = sha256_file(path)
    if got != want_sha:
        raise SystemExit(f"{name}: sha256 {got} != LFS {want_sha}")
    rows, bad = [], 0
    for batch in pq.ParquetFile(path).iter_batches(batch_size=16):
        for rec in batch.to_pylist():
            ok = hashlib.sha256(rec["archive"]).hexdigest() == rec["archive_sha256"]
            bad += not ok
            rows.append({"benchmark": bench, "shard": shard, "trial_id": rec["trial_id"], "archive_ok": ok,
                         **(read_trial(rec["archive"]) if ok else {})})
    part.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(part, index=False)
    size = path.stat().st_size
    if not keep:
        path.unlink()
    print(f"{name}: {len(rows)} trials, {bad} bad archives, {size / 1e9:.2f} GB{'' if keep else ' (deleted)'}",
          flush=True)
    return {"shard": name, "sha256": got, "bytes": size, "rows": len(rows), "status": "read"}


def summarize(trials: pd.DataFrame) -> None:
    for b, s in trials.groupby("benchmark"):
        cells = s.groupby(["task_name", "agent", "model"]).size()
        print(f"\n## {b}: {len(s)} trials, {s.task_name.nunique()} tasks, {s.model.nunique()} models, "
              f"{s.agent.nunique()} agents, {len(cells)} cells; trials/cell "
              f"{cells.value_counts().sort_index().to_dict()}; reward {s.reward.describe()[['mean', 'min', 'max']].round(3).to_dict()}; "
              f"no reward {int(s.reward.isna().sum())}; exceptions {int(s.exception_type.notna().sum())}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-shards", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    fetch("README.md")
    manifest = pd.read_parquet(fetch(MANIFEST))

    info = HfApi().dataset_info(REPO, revision=REVISION, files_metadata=True)
    shards = sorted((s.rfilename, s.lfs.sha256) for s in info.siblings
                    if any(s.rfilename.startswith(f"data/harbor_adapters/{b}/") for b in SETS))
    log = [process_shard(n, sha, args.keep_shards) for n, sha in shards]
    pd.DataFrame(log).to_csv(OUT / "SOURCES.tsv", sep="\t", index=False)

    trials = pd.concat([pd.read_csv(p, dtype={"task_name": str}) for p in sorted((OUT / "trials").glob("*.csv"))],
                       ignore_index=True)
    m = manifest[manifest.benchmark.isin(SETS)].explode("trial_ids").rename(columns={"trial_ids": "trial_id"})
    m = m.rename(columns={"task_name": "manifest_task_name"})
    trials = trials.merge(m, on=["benchmark", "trial_id"], how="left", validate="one_to_one")
    trials["in_manifest"] = trials["model"].notna()
    trials.to_csv(OUT / "trials.csv", index=False)
    print(f"trials.csv: {len(trials)} trials; in manifest {int(trials.in_manifest.sum())}; "
          f"manifest trials not in shards {len(set(m.trial_id) - set(trials.trial_id))}")
    summarize(trials)


if __name__ == "__main__":
    main()
