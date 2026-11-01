"""Carry a bare-digit run's answer files between machines as a plain TSV, so `adele mass check` on either machine
finds every recorded answer.

    python scripts/cloud/responses.py pack <run>     # judge I/O folder -> cloud-io/<run>-responses.tsv
    python scripts/cloud/responses.py unpack <run>   # cloud-io/<run>-responses.tsv -> judge I/O folder

`pack` refuses any answer over 16 bytes: only bare digits (the same information as labels.csv) may enter git, never
written reasoning. `unpack` never overwrites: a file that exists with other content stops it. The judge I/O folder
is $ADELE_JUDGE_IO (or the repo's .env) or ~/Developer/ADELE/judge-io.
"""

import csv
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAX_BYTES = 16


def io_dir(run: str) -> Path:
    root = os.environ.get("ADELE_JUDGE_IO")
    env = REPO / ".env"
    if root is None and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("ADELE_JUDGE_IO="):
                root = line.split("=", 1)[1].strip()
    return Path(root or "~/Developer/ADELE/judge-io").expanduser() / run


def pack(run: str) -> None:
    src = io_dir(run) / "responses"
    files = sorted(p for p in src.rglob("*.txt"))
    big = [str(p) for p in files if p.stat().st_size > MAX_BYTES]
    if big:
        sys.exit(f"refusing: {len(big)} answer files over {MAX_BYTES} bytes (not bare digits), e.g. {big[:3]}")
    out = REPO / "cloud-io" / f"{run}-responses.tsv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["path", "content"])
        for p in files:
            w.writerow([p.relative_to(src).as_posix(), p.read_bytes().decode("utf-8").encode("unicode_escape").decode()])
    print(f"packed {len(files)} answer files into {out.relative_to(REPO)}")


def unpack(run: str) -> None:
    tsv = REPO / "cloud-io" / f"{run}-responses.tsv"
    if not tsv.exists():
        print(f"no {tsv.relative_to(REPO)}")
        return
    dst, new = io_dir(run) / "responses", 0
    with open(tsv, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            data = row["content"].encode().decode("unicode_escape").encode("utf-8")
            p = dst / row["path"]
            if p.exists():
                if p.read_bytes() != data:
                    sys.exit(f"conflict: {p} differs from {tsv.name}")
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            new += 1
    print(f"unpacked {new} new answer files into {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("pack", "unpack"):
        sys.exit(__doc__)
    {"pack": pack, "unpack": unpack}[sys.argv[1]](sys.argv[2])
