"""Fetch and decrypt HAL's TAU-bench airline traces for the tool-calling scaffold (12 runs).

HAL (agent-evals/hal_traces on Hugging Face) encrypts traces to limit contamination, with the public password from
hal-harness (hal/utils/decrypt.py). This script reproduces that decryption with `cryptography` instead of installing
hal-harness. Zips and decrypted JSON go to data/downloads/hal/ (gitignored); nothing from the traces is committed.

    python experiments/benchmarks/dtg-data/fetch_hal_tau.py
"""

import base64
import json
from pathlib import Path
from zipfile import ZipFile

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from huggingface_hub import HfApi, hf_hub_download

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data/downloads/hal"
REPO = "agent-evals/hal_traces"
PREFIX = "taubench_airline_taubench_toolcalling_"
PASSWORD = b"hal1234"  # public, from hal-harness hal/utils/decrypt.py


def cipher(salt_b64: str) -> Fernet:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=base64.b64decode(salt_b64), iterations=480000)
    return Fernet(base64.urlsafe_b64encode(kdf.derive(PASSWORD)))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = [f for f in HfApi().list_repo_files(REPO, repo_type="dataset") if f.startswith(PREFIX)]
    print(len(files), "runs")
    for f in sorted(files):
        target = OUT / f.replace("_UPLOAD.zip", ".json")
        if target.exists():
            continue
        z = hf_hub_download(REPO, f, repo_type="dataset", local_dir=OUT / "zips")
        with ZipFile(z) as zf:
            names = zf.namelist()
            assert len(names) == 1, names
            enc = json.load(zf.open(names[0]))
        data = json.loads(cipher(enc["salt"]).decrypt(base64.b64decode(enc["encrypted_data"])))
        target.write_text(json.dumps(data))
        print(target.name, f"{target.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
