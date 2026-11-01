"""Build the ProgramBench task table for programbench-pl: all 200 tasks, with outcomes, flags and the clean set.

Outcomes: panel/sources/programbench/runs.csv (25 runs x 200 tasks, from the MIT ProgramBench/submissions registry at
c19e570f; ../programbench-data/NOTES.md). score = passed / scored tests (the registry's score.json, as the
leaderboard). Pablo's rules (2026-10-01):
  solved cell       score >= 0.9 (the FrontierSWE threshold)
  missing cell      the run did not submit the task (attempted == False: no score.json entry; 36 cells). Cells with
                    an eval error code (compile_failed, copy_executable_failed) were evaluated and scored 0: the
                    submission did not build or left no executable, so they count as failures. No attempted cell
                    has zero scored tests, so no cell is missing for a failed evaluation.
  solve_rate_<t>    share of the task's attempted runs with score >= t, for t in 0.9 (primary), 0.75 and 0.5
  mean_score        mean score over attempted runs
Every run is its own configuration (the same model at different efforts is kept).

Clean set: drop never-solved tasks, i.e. no run reaches 0.9 (excluded_by never_solved). No external defect list names
tasks as broken, so nothing else is dropped. Flags (not exclusions), conservative, issues read 2026-10-01 against
facebookresearch/ProgramBench v1.2.5 (27f02157):
  docs_damaged     the LM-written clean.sh deleted documentation (issue #7, #15 merged into it). The issue names only
                   zk and ffmpeg and says "quite a few" tasks are hit, with no list, so the rule is: named in the
                   issue, or < 2,000 chars of documentation in the workspace (meta doc_chars).
  knowledge_gated  the 25-program skip-list (recall-only test, byte-exact render, undiscoverable entry point) of the
                   third-party audit cited in issue #50 (github.com/kimjune01/program-bench-audit at df0ebcf,
                   findings/05_runner_subset.md). Ids only: the audit is share-alike. Its 6 "contestable" programs and
                   the softer self-capturing-oracle and coverage tiers are not flagged.
  evaluator_issue  an open evaluator-bug issue names the task and v1.2.5 does not fix it: csview (#56, #59: test-name
                   prefix mismatch, a branch that never writes results.xml) and cmatrix (#37: stdout and stderr merged
                   in the agent's view while tests check stderr; cmatrix is the issue's example). #60 (oracle and build
                   output share ./executable) names no task; #64 (pytest-rerunfailures 16.6.1) names no task and is
                   fixed at v1.2.5 by pinning 16.4 (b08d862).

    python experiments/benchmarks/programbench-pl/make_set.py
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BENCH = "programbench"
TAU, SENS = 0.9, (0.75, 0.5)
DOCS_MIN = 2000
DOCS_NAMED = {"zk-org__zk.10d93d5", "ffmpeg__ffmpeg.360a402"}  # issue #7 (zk) and #15 (ffmpeg)
KNOWLEDGE_GATED = {
    "ip7z__7zip.839151e", "filosottile__age.706dfc1", "arq5x__bedtools2.dd57059", "blake3-team__blake3.15e83a5",
    "google__brotli.b3dc9cc", "hpjansson__chafa.dd4d4c1", "wfxr__csview.8ac4de0", "stathissideris__ditaa.f2286c4",
    "multiprocessio__dsq.c3ae0ba", "duckdb__duckdb.bdb65ec", "rbakbashev__elfcat.52f8cc7",
    "facebookresearch__fasttext.1142dc4", "ffmpeg__ffmpeg.360a402", "osgeo__gdal.0847f12", "cslarsen__jp2a.61d205f",
    "lz4__lz4.1519f46", "noborus__ov.b96c2ba", "kaushiksrini__parqeye.8072121", "php__php-src.c891263",
    "eliukblau__pixterm.1a93fd5", "samtools__samtools.aa823b5", "lh3__seqtk.94e7070", "chirlu__sox.42b3557",
    "typst__typst.88356d0", "facebook__zstd.1168da0"}
EVALUATOR_ISSUES = {"wfxr__csview.8ac4de0": "56;59", "abishekvashok__cmatrix.5c082c6": "37"}
FLAGS = ["docs_damaged", "knowledge_gated", "evaluator_issue"]


def main() -> None:
    meta = pd.read_csv(ROOT / f"data/instances/meta_{BENCH}.csv").set_index("instance_id")
    runs = pd.read_csv(HERE.parent / f"panel/sources/{BENCH}/runs.csv")
    assert len(meta) == 200 and len(runs) == 25 * 200 and set(runs["instance_id"]) == set(meta.index)
    assert (DOCS_NAMED | KNOWLEDGE_GATED | set(EVALUATOR_ISSUES)) <= set(meta.index) and len(KNOWLEDGE_GATED) == 25
    att = runs[runs["attempted"]]
    assert att["n_tests"].gt(0).all() and att["score"].notna().all()
    g = att.groupby("instance_id")
    out = pd.DataFrame({"n_runs": g.size(), f"n_solved_{TAU}": g["score"].apply(lambda s: int((s >= TAU).sum()))})
    for t in (TAU, *SENS):
        out[f"solve_rate_{t}"] = g["score"].apply(lambda s, t=t: (s >= t).mean()).round(4)
    out["mean_score"] = g["score"].mean().round(4)
    out["max_score"] = g["score"].max().round(4)
    v125_keep = g["score_v125"].max() >= TAU

    out = meta[["language", "difficulty"]].join(meta[["doc_chars", "prompt_chars"]].rename(
        columns={"doc_chars": "docs_chars"})).join(out)
    out["docs_damaged"] = (out["docs_chars"] < DOCS_MIN) | out.index.isin(DOCS_NAMED)
    out["knowledge_gated"] = out.index.isin(KNOWLEDGE_GATED)
    out["evaluator_refs"] = pd.Series(EVALUATOR_ISSUES).reindex(out.index).fillna("")
    out["evaluator_issue"] = out["evaluator_refs"] != ""
    out["any_flag"] = out[FLAGS].any(axis=1)
    out["excluded_by"] = (out["max_score"] < TAU).map({True: "never_solved", False: ""})
    out["keep"] = out["excluded_by"] == ""
    assert (out["keep"] == v125_keep.reindex(out.index)).all(), "clean set must not depend on the v1.2.5 rescoring"
    out = out.rename_axis("instance_id").sort_index().reset_index()
    out.to_csv(HERE / "tasks.csv", index=False)

    k = out[out["keep"]]
    print(f"{len(out)} tasks; kept {len(k)}; never_solved at {TAU}: {int((~out['keep']).sum())}; "
          f"missing cells: {int((~runs['attempted']).sum())}")
    for f in FLAGS + ["any_flag"]:
        print(f"{f}: {int(out[f].sum())} ({int(k[f].sum())} kept)"
              + (f": {', '.join(k.loc[k[f], 'instance_id'])}" if f != "docs_damaged" else ""))
    print(f"clean without flags: {int((~k['any_flag']).sum())}")
    print("difficulty (kept):", k["difficulty"].value_counts(dropna=False).to_dict(),
          "| language (kept):", k["language"].value_counts().to_dict())
    print(k[[f"solve_rate_{TAU}", *(f"solve_rate_{t}" for t in SENS), "mean_score"]].describe().round(3).to_string())
    print(f"solve_rate_{TAU} values (kept):", k[f"solve_rate_{TAU}"].round(2).value_counts().sort_index().to_dict())


if __name__ == "__main__":
    main()
