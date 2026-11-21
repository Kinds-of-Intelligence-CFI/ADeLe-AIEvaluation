"""adele.instance_store: push to a private dataset and fetch with hash checks, against a fake Hugging Face API."""

import shutil
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest

from adele.instance_store import InstanceStoreError, fetch, push
from adele.instances import MANIFEST_NAME, prepare


class FakeHub:
    """Stores uploads in a folder; ``private`` sets what repo_info reports."""

    def __init__(self, root: Path, private: bool = True):
        self.root, self.private, self.created = root, private, []

    def create_repo(self, repo_id, repo_type, private, exist_ok):
        self.created.append((repo_id, repo_type, private))

    def repo_info(self, repo_id, repo_type):
        return SimpleNamespace(private=self.private)

    def upload_file(self, path_or_fileobj, path_in_repo, repo_id, repo_type, commit_message):
        (self.root / repo_id).mkdir(parents=True, exist_ok=True)
        shutil.copy(path_or_fileobj, self.root / repo_id / path_in_repo)

    def download(self, repo_id, filename, repo_type, local_dir):
        dest = Path(local_dir) / filename
        shutil.copy(self.root / repo_id / filename, dest)
        return str(dest)


@pytest.fixture
def frozen(tmp_path):
    frame = pd.DataFrame({"prompt": ["Fix bug one in the parser.", "Fix bug two in the lexer."],
                          "source_id": ["p__p-1", "p__p-2"]})
    prepare(["swebench"], tmp_path / "local", loaders={"swebench": lambda: frame})
    return tmp_path


def test_push_then_fetch_round_trip(frozen):
    hub, index = FakeHub(frozen / "hub"), frozen / "committed" / MANIFEST_NAME
    assert push(frozen / "local", "org/x", api=hub, index_out=index) == ["swe-bench-verified"]
    assert hub.created == [("org/x", "dataset", True)] and index.exists()
    got = fetch(frozen / "elsewhere", "org/x", download=hub.download, index=index)
    assert got == ["swe-bench-verified"]
    assert (frozen / "elsewhere" / MANIFEST_NAME).exists()


def test_push_refuses_a_public_dataset(frozen):
    with pytest.raises(InstanceStoreError, match="public"):
        push(frozen / "local", "org/x", api=FakeHub(frozen / "hub", private=False),
             index_out=frozen / "c" / MANIFEST_NAME)
    assert not (frozen / "hub").exists()


def test_fetch_refuses_a_changed_file(frozen):
    hub, index = FakeHub(frozen / "hub"), frozen / "committed" / MANIFEST_NAME
    push(frozen / "local", "org/x", api=hub, index_out=index)
    f = next((frozen / "hub" / "org/x").glob("*.parquet"))
    df = pd.read_parquet(f)
    df.loc[0, "prompt"] = "tampered"
    df.to_parquet(f)
    with pytest.raises(InstanceStoreError, match="sha256"):
        fetch(frozen / "elsewhere", "org/x", download=hub.download, index=index)
    assert not list((frozen / "elsewhere").glob("*.parquet"))


def test_unknown_benchmark_is_refused(frozen):
    with pytest.raises(InstanceStoreError, match="not in the index"):
        push(frozen / "local", "org/x", benchmarks=["nope"], api=FakeHub(frozen / "hub"),
             index_out=frozen / "c" / MANIFEST_NAME)
