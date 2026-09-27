"""tau2/tau3-bench results: per-domain aggregates, and per-task rewards.

:func:`fetch_aggregates` reads the public leaderboard submissions
(``web/leaderboard/public/submissions/*/submission.json`` in
https://github.com/sierra-research/tau2-bench), which carry pass@1..4 per domain.
That AGGREGATE frame is kept outside the instance-level schema so it cannot be
joined by mistake. Schema verified against the repo (65 submissions, 2026-08).

:func:`fetch_instances` reads the per-task rewards from Sierra's public S3 bucket
``sierra-tau-bench-public``: each text-track submission keeps one results file per
domain directly under ``submissions/<entry>/trajectories/``, whose ``simulations[]``
carry ``task_id``, ``trial`` and ``reward_info.reward`` and whose ``tasks[]`` carry
the task definitions the run used (verified 2026-09-27; voice-track submissions,
``modality: voice``, keep per-call folders instead and are skipped).
"""

import json
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from adele.results.schema import normalize

logger = logging.getLogger(__name__)


def fetch_aggregates(tau2_repo: str | Path) -> pd.DataFrame:
    """One row per (submission, domain) with pass@k and metadata."""
    sub_dir = Path(tau2_repo) / "web" / "leaderboard" / "public" / "submissions"
    if not sub_dir.is_dir():
        raise FileNotFoundError(
            f"{sub_dir} not found — pass a checkout of sierra-research/tau2-bench"
        )
    rows = []
    for f in sorted(sub_dir.glob("*/submission.json")):
        entry = f.parent.name
        if entry.startswith("A_EXAMPLE"):
            continue
        try:
            d = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("skipping %s: %s", entry, exc)
            continue
        for domain, res in (d.get("results") or {}).items():
            if not res:
                continue
            rows.append({
                "benchmark": f"tau2-{domain}",
                "model": d.get("model_name", entry),
                "scaffold": "tau2-agent",
                "submitting_org": d.get("submitting_organization"),
                "submission_date": d.get("submission_date"),
                "reasoning_effort": d.get("reasoning_effort"),
                "user_simulator": (d.get("methodology") or {}).get("user_simulator"),
                **{k: res.get(k) for k in ("pass_1", "pass_2", "pass_3", "pass_4", "cost")},
                "trajectories_available": bool(d.get("trajectories_available")),
                "entry": entry,
                "source": "tau2-leaderboard",
            })
    df = pd.DataFrame(rows)
    logger.info("tau2 leaderboard: %d (submission, domain) aggregate rows — "
                "NO instance-level data; see fetch_instances", len(df))
    return df


# ---------------------------------------------------------------- per-task rewards

S3_BUCKET = "https://sierra-tau-bench-public.s3.amazonaws.com/"
DOMAINS = ("airline", "retail", "telecom", "banking_knowledge")
_S3 = "{http://s3.amazonaws.com/doc/2006-03-01/}"


def _get(url: str) -> bytes:
    import urllib.request
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def list_bucket(bucket: str = S3_BUCKET, prefix: str = "submissions/") -> pd.DataFrame:
    """Every object under ``prefix``: key, size, etag (paged S3 ListObjectsV2)."""
    import urllib.parse
    import xml.etree.ElementTree as ET

    rows, token = [], None
    while True:
        query = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            query["continuation-token"] = token
        root = ET.fromstring(_get(bucket + "?" + urllib.parse.urlencode(query)))
        for c in root.iter(_S3 + "Contents"):
            rows.append({"key": c.findtext(_S3 + "Key"), "size": int(c.findtext(_S3 + "Size")),
                         "etag": c.findtext(_S3 + "ETag", "").strip('"')})
        token = root.findtext(_S3 + "NextContinuationToken")
        if not token:
            return pd.DataFrame(rows)


def result_files(listing: pd.DataFrame, bucket: str = S3_BUCKET) -> pd.DataFrame:
    """The text-track results files: JSON files directly under an entry's
    ``trajectories/`` whose ``submission.json`` is not ``modality: voice``,
    joined with that submission's metadata."""
    import urllib.parse

    parts = listing["key"].str.split("/")
    files = listing[(parts.str.len() == 4) & (parts.str[2] == "trajectories")
                    & listing["key"].str.endswith(".json")].copy()
    files["entry"] = files["key"].str.split("/").str[1]
    meta = {}
    for entry in sorted(files["entry"].unique()):
        try:
            meta[entry] = json.loads(_get(bucket + urllib.parse.quote(f"submissions/{entry}/submission.json")))
        except Exception as exc:  # noqa: BLE001 - a missing submission.json leaves the metadata blank
            logger.warning("no submission.json for %s: %s", entry, exc)
            meta[entry] = {}
    files = files[[meta[e].get("modality", "text") != "voice" for e in files["entry"]]]
    for col, field in (("model", "model_name"), ("reasoning_effort", "reasoning_effort"),
                       ("submission_date", "submission_date")):
        files[col] = [meta[e].get(field) for e in files["entry"]]
    files["model"] = files["model"].fillna(files["entry"])
    return files.reset_index(drop=True)


def parse_results(data: dict, domains: tuple = DOMAINS) -> pd.DataFrame:
    """One results file → one row per task: success (share of trials with reward 1),
    n_trials, mean_reward, and task_prompt_sha12, the hash of the prompt rebuilt from
    the file's own task definition by the loader that freezes the instances, so the
    text behind each task id can be checked against the frozen instance."""
    import hashlib

    from adele.agentic.benchmarks import _taubench_prompt

    info = data.get("info") or {}
    domain = (info.get("environment_info") or {}).get("domain_name")
    if domain not in domains:
        return pd.DataFrame()
    prompt_sha = {
        str(t["id"]): hashlib.sha256(_taubench_prompt(
            domain, (t.get("user_scenario") or {}).get("instructions", {})).encode()).hexdigest()[:12]
        for t in data.get("tasks", [])
    }
    rewards: dict[str, list[float]] = {}
    for sim in data.get("simulations", []):
        reward = (sim.get("reward_info") or {}).get("reward")
        rewards.setdefault(str(sim["task_id"]), []).append(float(reward or 0.0))
    return pd.DataFrame([{
        "benchmark": f"tau2-{domain}", "instance_id": task,
        "success": sum(r >= 1.0 for r in rs) / len(rs), "n_trials": len(rs),
        "mean_reward": sum(rs) / len(rs), "task_prompt_sha12": prompt_sha.get(task),
        "user_simulator": (info.get("user_info") or {}).get("llm"),
        "agent_llm": (info.get("agent_info") or {}).get("llm"),
        "agent_impl": (info.get("agent_info") or {}).get("implementation"),
    } for task, rs in sorted(rewards.items())])


def fetch_instances(bucket: str = S3_BUCKET, *, entries: Optional[list] = None,
                    domains: tuple = DOMAINS, cache_dir: Optional[str | Path] = None) -> pd.DataFrame:
    """Per-task success for every text-track submission in the public bucket.

    Each results file (up to ~400 MB) is streamed to a temporary file, parsed and
    deleted, so only the rewards are kept. With ``cache_dir``, each file's parsed
    rows are saved there (keyed by the object's ETag) and reused on later calls.
    ``entries`` limits the submissions. A submission with two runs of one domain
    (e.g. two banking configurations) keeps both, labelled by file name.
    """
    import shutil
    import tempfile
    import urllib.parse
    import urllib.request

    files = result_files(list_bucket(bucket), bucket)
    if entries is not None:
        files = files[files["entry"].isin(entries)]
    frames = []
    for f in files.itertuples(index=False):
        cached = Path(cache_dir) / f.entry / f"{Path(f.key).stem}.{f.etag}.parquet" if cache_dir else None
        if cached is not None and cached.exists():
            parsed = pd.read_parquet(cached)
        else:
            with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
                with urllib.request.urlopen(bucket + urllib.parse.quote(f.key), timeout=600) as r:
                    shutil.copyfileobj(r, tmp, length=1 << 20)
                tmp.flush()
                with open(tmp.name, encoding="utf-8") as fh:
                    parsed = parse_results(json.load(fh), domains)
            if cached is not None:
                cached.parent.mkdir(parents=True, exist_ok=True)
                parsed.to_parquet(cached)
        if parsed.empty:
            logger.info("skipped %s (domain not requested)", f.key)
            continue
        frames.append(parsed.assign(model=f.model, scaffold="tau2-agent", source="sierra-tau2-s3",
                                    entry=f.entry, reasoning_effort=f.reasoning_effort,
                                    submission_date=f.submission_date, source_key=f.key,
                                    source_etag=f.etag))
        logger.info("%s: %d tasks", f.key, len(parsed))
    if not frames:
        return pd.DataFrame()
    return normalize(label_runs(pd.concat(frames, ignore_index=True)))


def label_runs(df: pd.DataFrame) -> pd.DataFrame:
    """One run = one results file. Label runs by entry, or by entry/file when an entry
    has two runs of a domain; runs sharing a model name get their label as scaffold, so
    they stay separate columns of the success matrix."""
    df = df.copy()
    df["run"] = df["entry"]
    multi = df.groupby(["benchmark", "entry"])["source_key"].transform("nunique") > 1
    df.loc[multi, "run"] = df.loc[multi, "entry"] + "/" + df.loc[multi, "source_key"].map(lambda k: Path(k).stem)
    shared = df.groupby(["benchmark", "instance_id", "model"])["run"].transform("nunique") > 1
    df.loc[shared, "scaffold"] = "tau2-agent#" + df.loc[shared, "run"]
    return df
