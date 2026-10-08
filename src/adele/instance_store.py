"""Share frozen instance files privately: push them to a private Hugging Face dataset, fetch them on another machine.

Task texts never go in the repo: several benchmarks carry canary strings or ask that items not be posted. What is
committed is the index ``experiments/benchmarks/mass-annotation/INSTANCES.tsv``: benchmark names, counts, file names
and the sha256 of each frozen frame. ``fetch`` checks every downloaded file against that index, so a run pinned on
another machine sees exactly the texts the committed runs saw.

    adele instances push --repo ORG/NAME        # owner, once per new or changed benchmark (needs a write token)
    adele instances fetch                       # anyone with read access to the private dataset
"""

import os
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional

import pandas as pd

from adele.instances import MANIFEST_NAME, _frame_sha256, _merge_manifest

REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX = REPO_ROOT / "experiments" / "benchmarks" / "mass-annotation" / "INSTANCES.tsv"
DEFAULT_REPO = "CFI-Kinds-of-Intelligence/adele-instances"


class InstanceStoreError(RuntimeError):
    pass


def repo_id(repo: Optional[str] = None) -> str:
    """The dataset: ``repo``, else ``$ADELE_INSTANCES_REPO``, else :data:`DEFAULT_REPO`."""
    return repo or os.environ.get("ADELE_INSTANCES_REPO") or DEFAULT_REPO


def _read_index(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise InstanceStoreError(f"{path} not found")
    return pd.read_csv(path, sep="\t")


def _select(index: pd.DataFrame, benchmarks: Optional[Iterable[str]]) -> pd.DataFrame:
    if benchmarks is None:
        return index
    wanted = list(benchmarks)
    unknown = sorted(set(wanted) - set(index["benchmark"]))
    if unknown:
        raise InstanceStoreError(f"not in the index: {unknown}")
    return index[index["benchmark"].isin(wanted)]


def _check(path: Path, sha: str) -> None:
    df = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path, dtype={"instance_id": str})
    df["instance_id"] = df["instance_id"].astype(str)
    if _frame_sha256(df) != sha:
        raise InstanceStoreError(f"{path.name} does not match its sha256 in the index")


def push(instances_dir: str | Path, repo: Optional[str] = None, benchmarks: Optional[Iterable[str]] = None,
         api: Any = None, index_out: Path = INDEX) -> List[str]:
    """Upload the frozen files of ``benchmarks`` (default: all in the local index) to a PRIVATE dataset and record
    their rows in the committed index. Refuses a public dataset and files that no longer match their sha256."""
    from huggingface_hub import HfApi

    if index_out.name != MANIFEST_NAME:
        raise InstanceStoreError(f"index_out must be named {MANIFEST_NAME}")
    api = api or HfApi()
    rid, d = repo_id(repo), Path(instances_dir)
    rows = _select(_read_index(d / MANIFEST_NAME), benchmarks)
    for row in rows.itertuples(index=False):
        _check(d / row.file, row.sha256)
    api.create_repo(rid, repo_type="dataset", private=True, exist_ok=True)
    if not api.repo_info(rid, repo_type="dataset").private:
        raise InstanceStoreError(f"{rid} is public: task texts must never be uploaded there")
    for row in rows.itertuples(index=False):
        api.upload_file(path_or_fileobj=str(d / row.file), path_in_repo=row.file, repo_id=rid, repo_type="dataset",
                        commit_message=f"{row.benchmark}: {row.n_instances} instances, frame {row.sha256[:12]}")
    index_out.parent.mkdir(parents=True, exist_ok=True)
    _merge_manifest(index_out.parent, rows)  # index_out is always named INSTANCES.tsv
    return list(rows["benchmark"])


def fetch(instances_dir: str | Path, repo: Optional[str] = None, benchmarks: Optional[Iterable[str]] = None,
          download: Optional[Callable[..., str]] = None, index: Path = INDEX) -> List[str]:
    """Download the files of ``benchmarks`` (default: all in the committed index) into ``instances_dir``, check each
    against the committed sha256, and add their rows to the local ``INSTANCES.tsv``."""
    if download is None:
        from huggingface_hub import hf_hub_download as download
    rid, d = repo_id(repo), Path(instances_dir)
    rows = _select(_read_index(index), benchmarks)
    d.mkdir(parents=True, exist_ok=True)
    for row in rows.itertuples(index=False):
        path = Path(download(repo_id=rid, filename=row.file, repo_type="dataset", local_dir=str(d)))
        try:
            _check(path, row.sha256)
        except InstanceStoreError:
            path.unlink(missing_ok=True)
            raise
    _merge_manifest(d, rows)
    return list(rows["benchmark"])
