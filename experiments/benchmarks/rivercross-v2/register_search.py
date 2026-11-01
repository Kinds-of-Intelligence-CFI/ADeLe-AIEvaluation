"""Register the 54 rc-search states (amendment 2's grid) as the `adele mass` benchmark `rivercross-search`, so their
PLe and PLs labels can be made with the runner (amendment 4).

Instance = one state; prompt = the state text in frames/search_frame.csv, exactly as rc-search and plp-b2's o-search
judged it. Writes data/instances/instances_rivercross-search.parquet and registers it. Then checks that the runner's
v2 prompt for PLp (text O) reproduces o-search's prompt hashes, so PLe and PLs see the same task text as the adopted
PLp labels.

    python experiments/benchmarks/rivercross-v2/register_search.py
"""

import hashlib
from pathlib import Path

import pandas as pd

from adele.agentic import load_active_catalog
from adele.annotation.prompts import build_annotation_prompt_v2
from adele.instances import register

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCHMARK = "rivercross-search"
OUT = ROOT / "data/instances" / f"instances_{BENCHMARK}.parquet"


def main() -> None:
    frame = pd.read_csv(HERE / "frames/search_frame.csv")
    assert len(frame) == 54 and frame["custom_id"].is_unique
    inst = pd.DataFrame({"benchmark": BENCHMARK, "instance_id": frame["custom_id"], "prompt": frame["prompt"],
                         "prompt_sha12": frame["prompt"].map(lambda p: hashlib.sha256(p.encode()).hexdigest()[:12])})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    inst.to_parquet(OUT, index=False)
    register(OUT, benchmark=BENCHMARK)

    plp = load_active_catalog()["PLp"]
    o = pd.read_csv(HERE.parent / "plp-b2/labels/o-search/prompts_index.csv").set_index("instance_id")["prompt_sha256"]
    ours = {r.instance_id: hashlib.sha256(build_annotation_prompt_v2(plp.full_name, plp.content, r.prompt)
                                          .encode("utf-8")).hexdigest() for r in inst.itertuples()}
    same = sum(ours[i] == o[i] for i in o.index)
    print(f"{len(inst)} states registered as {BENCHMARK}; PLp prompt hashes equal to o-search: {same}/{len(o)}")
    assert same == len(o) == 54


if __name__ == "__main__":
    main()
