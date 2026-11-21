"""GPQA Diamond (198): the question and its four options, one instance per question.

Source (public, no login, no API key, no terms accepted):
  github.com/harbor-framework/harbor-datasets  (no licence file) DATASETS_COMMIT, the commit the
      Harbor-Adapter GPQA trials ran (config.task.git_commit_id, 26,971 of 26,978 trials; the other 7
      say "HEAD"): datasets/gpqa-diamond/<i>/instruction.md and task.toml. Both files are
      byte-identical at cd46908b, the commit of the ARC-AGI-2 trials (checked 2026-10-11). Built by the Harbor GPQA adapter (github.com/harbor-framework/harbor, Apache-2.0,
      adapters/gpqa-diamond/adapter.py) from Idavidrein/gpqa, config gpqa_diamond, split train.
The original Idavidrein/gpqa is gated; we did not request access. GPQA asks that its items not be
posted online, so everything this script writes stays in gitignored data/.

Task ids and option order are Harbor's: instance_id i = row i of the gpqa_diamond train split;
options are [correct] + [incorrect 1..3], shuffled with ``random.seed(42 + i)``, labelled (A)-(D).
So instance ids and option letters join with the Harbor-Adapter outcomes as they are. Other outcome
sources (Every Eval Ever, HELM) order options their own way and need a join on question text:
meta holds question_sha12 (sha256 of the stripped question) for that.

Prompt rule: the opening of Harbor's instruction.md, i.e. the GPQA paper's zero-shot format,
"What is the correct answer to this question: {question}\\n\\nChoices:\\n  (A) ...". Harbor's tail
(step-by-step scaffold, write the letter to /app/answer.txt, "This is a challenging graduate-level
question ...") is dropped: it is the agent harness, not the item, and it states the difficulty to
the judge. (Alternative, not taken: the full instruction.md verbatim.) The script fails if an
instruction does not split cleanly on the template's markers.

Writes:
  data/instances/instances_gpqa-diamond.parquet  benchmark, instance_id, prompt, prompt_sha12
  data/instances/meta_gpqa-diamond.csv           domain, subdomain, question_sha12, provenance
  data/downloads/gpqa-diamond/<i>/instruction.md, task.toml, SOURCES.tsv
and registers the instance file in data/instances/INSTANCES.tsv.

Run: python -I experiments/benchmarks/gpqa-data/fetch_tasks.py
"""

import hashlib
import re
import sys
import tomllib
import urllib.request
from pathlib import Path

import pandas as pd

BENCHMARK = "gpqa-diamond"
ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data" / "downloads" / "gpqa-diamond"
OUT = ROOT / "data" / "instances"
sys.path.insert(0, str(ROOT / "src"))
from adele.instances import register, validate_instances  # noqa: E402

DATASETS_COMMIT = "1983ac5c4d43f43cb7a9af9f89c54d09025589ec"
RAW = f"https://raw.githubusercontent.com/harbor-framework/harbor-datasets/{DATASETS_COMMIT}/datasets/gpqa-diamond"
N = 198
HEAD = "What is the correct answer to this question: \n"
TAIL = "\n\nLet's think step by step:\n"
OPTION = re.compile(r"^  \(([ABCD])\) ", re.MULTILINE)


def sha12(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()[:12]


def get(url: str, dest: Path) -> bytes:
    """Cached download."""
    if dest.exists():
        return dest.read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": "adele-data/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        blob = r.read()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)
    return blob


def item(instruction: str, i: int) -> tuple:
    """(prompt, question) from one Harbor instruction.md; fails loudly on an unexpected layout."""
    assert instruction.startswith(HEAD), f"{i}: head"
    body, sep, _ = instruction.partition(TAIL)
    assert sep, f"{i}: tail"
    question, sep, choices = body[len(HEAD):].partition("\n\nChoices:\n")
    assert sep, f"{i}: choices"
    assert OPTION.findall(choices) == ["A", "B", "C", "D"], f"{i}: options"
    return body, question.strip()


def main() -> None:
    rows, meta, sources = [], [], []
    for i in range(N):
        files = {}
        for name in ("instruction.md", "task.toml"):
            blob = get(f"{RAW}/{i}/{name}", CACHE / str(i) / name)
            files[name] = blob.decode()
            sources.append(f"{i}/{name}\t{RAW}/{i}/{name}\t{hashlib.sha256(blob).hexdigest()}\t{len(blob)}")
        prompt, question = item(files["instruction.md"], i)
        tags = tomllib.loads(files["task.toml"])["metadata"]["tags"]
        rows.append({"benchmark": BENCHMARK, "instance_id": str(i), "prompt": prompt, "prompt_sha12": sha12(prompt)})
        meta.append({
            "instance_id": str(i), "domain": tags[2] if len(tags) > 2 else None,
            "subdomain": tags[3] if len(tags) > 3 else None, "question_sha12": sha12(question),
            "instruction_sha12": sha12(files["instruction.md"]), "prompt_chars": len(prompt),
            "option_order": f"harbor: random.seed(42+{i}) shuffle of [correct, incorrect 1-3]",
            "source_url": f"{RAW}/{i}/instruction.md", "datasets_commit": DATASETS_COMMIT,
        })
    (CACHE / "SOURCES.tsv").write_text("name\turl\tsha256\tbytes\n" + "\n".join(sources) + "\n")

    df = pd.DataFrame(rows)
    warnings = validate_instances(df, where=BENCHMARK)
    path = OUT / f"instances_{BENCHMARK}.parquet"
    df.to_parquet(path, index=False)
    m = pd.DataFrame(meta)
    m.to_csv(OUT / f"meta_{BENCHMARK}.csv", index=False)
    row = register(path, benchmark=BENCHMARK, n_dimensions=18)
    print(f"{path.name}: {len(df)} questions; domains {m.domain.value_counts().to_dict()}; prompt chars median "
          f"{int(m.prompt_chars.median())}, max {int(m.prompt_chars.max())}; warnings={warnings}; "
          f"registered sha256 {row['sha256'][:12]}")


if __name__ == "__main__":
    main()
