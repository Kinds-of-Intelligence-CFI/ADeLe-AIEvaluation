"""Download the public WeirdML sources into data/results/weirdml/ (gitignored).

All URLs are pinned to a git commit, so the sha256 values below are stable.
Live (unpinned) equivalents: https://htihle.github.io/data/weirdml_v3_results.json,
https://htihle.github.io/assets/data/weirdml_v3.json,
https://htihle.github.io/data/weirdml_data.csv, https://htihle.github.io/prompts/*.html.

    python experiments/benchmarks/weirdml-data/fetch.py

Writes each file plus SOURCES.tsv (name, url, sha256, bytes). Fails on a hash
mismatch. No LLM calls.
"""

import hashlib
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "data" / "results" / "weirdml"

SITE = "https://raw.githubusercontent.com/htihle/htihle.github.io/9553938f2cb0c7077ab47ba0cadde18bc440e71d"
WTH = "https://raw.githubusercontent.com/htihle/weirdml-time-horizons/965c7f11d843eac3c81a22a62c3cef2a9c0be7f8"

# (local name, url, sha256)
SOURCES = [
    # v3: per-run, per-submission results (983 runs, generated 2026-09-29)
    ("weirdml_v3_results.json", f"{SITE}/data/weirdml_v3_results.json",
     "5b6e97d070da115d15eda879c2d00e587372cb0e289618021e01a2515e449e69"),
    # v3: prepared plotting data (aggregates)
    ("weirdml_v3_prepared.json", f"{SITE}/assets/data/weirdml_v3.json",
     "7ad78838e827a19a14e56f9ffbafb1f13a93b56931a3ddfe90534e126e0e8a2b"),
    # v2: per-model x per-task MEAN accuracy, 162 configs (no per-run scores)
    ("weirdml_v2_data.csv", f"{SITE}/data/weirdml_data.csv",
     "3fd32a608d557d0c9d94c5ea27fd6a32044329e8557d64d43d827ec262642688"),
    # v2: per-run scores, 87 models x 17 tasks, snapshot 2026-02-13
    ("weirdml_v2_runs_timehorizons.json", f"{WTH}/data/weirdml_results.json",
     "680d668bbd441f75af45be30c246f98ca7bb6255d228ca7287cc0971b36fed31"),
    # v2: LLM-estimated human completion times (4 estimators x 5 thresholds x 17 tasks)
    ("timehorizons_all_estimates.json", f"{WTH}/data/all_estimates.json",
     "8efad1afb23fc3ffac95b3a6ce99b522963eb6bbd223cea6287ffa5492096991"),
    ("timehorizons_human_estimates.json", f"{WTH}/data/human_estimates.json",
     "e23340e2a75bed430789b4e505ea9262679c6113a689e80fb90a9c8131b7daa6"),
    # prompts (v1/v2 public task prompts + system prompts)
    ("prompts/system_prompt.md", f"{SITE}/prompts/system_prompt.md",
     "937a3e234b51653598251393e26d230cdba89ad1760f12648fe646f5d031d899"),
    ("prompts/system_prompt_v2.md", f"{SITE}/prompts/system_prompt_v2.md",
     "7bff6bf8d9b935bf7cb646e45a5879cbbd643bc74c869a88715f98a2f4454b14"),
    ("prompts/task_prompt_chess_winners.md", f"{SITE}/prompts/task_prompt_chess_winners.md",
     "207a672ed23ab686661440fd762cfe9090774606860d9d01ef29f0a27a265896"),
    ("prompts/task_prompt_digits_unsup.md", f"{SITE}/prompts/task_prompt_digits_unsup.md",
     "68c5cb559e4d054965ba85198608e7cb95808c89bcb473bc677ec75777129d35"),
    ("prompts/task_prompt_shapes_easy.md", f"{SITE}/prompts/task_prompt_shapes_easy.md",
     "89f28f708ce448c7bbb8ce0f1942e434de0ace63b610ce8e686d3ca5380461c4"),
    ("prompts/task_prompt_shapes_hard.md", f"{SITE}/prompts/task_prompt_shapes_hard.md",
     "9c8deb0c8e4818cedfee3f126a618edef536f7454cddb6025425266996537796"),
    ("prompts/task_prompt_shuffle_easy.md", f"{SITE}/prompts/task_prompt_shuffle_easy.md",
     "fb628e2dec96cdb60be3c0eff28066a4ace5c1ccb1def2788586f245d685c98c"),
    ("prompts/task_prompt_shuffle_hard.md", f"{SITE}/prompts/task_prompt_shuffle_hard.md",
     "c1b86780db196af78df31c81d00919bc0060a28c23c9e98bfab3f7310026a078"),
]


def main() -> int:
    rows, bad = [], []
    for name, url, want in SOURCES:
        dest = OUT / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=120) as r:
            blob = r.read()
        got = hashlib.sha256(blob).hexdigest()
        dest.write_bytes(blob)
        ok = got == want
        if not ok:
            bad.append(name)
        rows.append(f"{name}\t{url}\t{got}\t{len(blob)}")
        print(f"{'ok ' if ok else 'BAD'} {name} {len(blob):>9} {got[:12]}")
    (OUT / "SOURCES.tsv").write_text("name\turl\tsha256\tbytes\n" + "\n".join(rows) + "\n")
    if bad:
        print(f"sha256 mismatch: {bad}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
