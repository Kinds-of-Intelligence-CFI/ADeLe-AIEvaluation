"""ArXivMath (287) and BrokenArXiv (308), MathArena's monthly arXiv sets: one instance per problem, every month
that has model outputs.

Sources (public, no login, no API key, no terms accepted):
  huggingface.co/datasets/MathArena/<set>-<MMYY>  (CC BY-SA 4.0) at the revisions in REVISIONS:
      data/train-00000-of-00001.parquet (problem_idx, problem, source = arXiv id, ...) and README.md.
      ArXivMath: 1225, 0126, 0226, 0326, 0426, 0526, 0626, 0826. BrokenArXiv: 0226, 0326, 0426, 0526, 0626, 0826.
      There is no 0726 set of either, and no BrokenArXiv before 0226. The aggregate, -training, arxivlean,
      arxivcs and arxivphys sets are out of scope.
  github.com/eth-sri/matharena  (MIT) MATHARENA_COMMIT: configs/competitions/arxiv/<month>.yaml (ArXivMath) and
      arxiv_false/<month>.yaml (BrokenArXiv). MathArena's runner (src/matharena/runner.py) builds the user message as
      ``instruction + "\\n\\n{problem}"`` formatted with the problem.
  huggingface.co/datasets/MathArena/<set>-<MMYY>_outputs  (CC BY-SA 4.0) at the revisions in REVISIONS: read
      remotely, columns problem_idx, model_name, correct, problem, user_message only (no responses); nothing is kept.

What the models saw (checked against the logged user_message of every output row):
  ArXivMath 1225-0226: "You are given a difficult question ..." + a final-answer-only note + "\\boxed{}" format.
  ArXivMath 0326-0626: "You are given a difficult question. Your task is to solve the problem." + "\\boxed{}" format.
  ArXivMath 0826: told the problem is OPEN ("really attempt ... regardless of the fact it is open"), "\\boxed{}",
      then a tool harness: shell, Python, Sage, no internet, up to 12 h and $100 per attempt, scored on the answer.
  BrokenArXiv 0226-0626: "Try to generate a proof for the following statement:" then the statement.
  BrokenArXiv 0826: "Try to prove the following statement." + "regardless of the fact it is open" + the same tool
      harness. Every BrokenArXiv statement is a false perturbation of a paper's theorem; the true one
      (``original_problem``) is the hidden label and is never read into the prompt or the meta file.

Prompt rule (as in the GPQA loader: keep the item, drop harness boilerplate and statements of difficulty or format):
  ArXivMath: the ``problem`` field verbatim. The instruction is all harness: it states difficulty ("difficult
      question", "open problem"), the answer format (\\boxed{}) and, in 0826, the tools.
  BrokenArXiv: the first line of the month's instruction (the task: prove the statement; the problem field alone
      is a bare statement), then the statement, joined as MathArena joins them (three newlines). For 0226-0626 this
      is byte-identical to the logged user message. For 0826 the "open" sentence and the tool harness are dropped.
  (Alternative, not taken: the logged user message verbatim, i.e. MathArena's full instruction + problem.)
  The script fails if any problem has no logged user message equal to the MathArena prompt rendered from the pinned
  config (byte-identical, or for 0826 equal up to trailing spaces at line ends: the logged 0826 instruction has two
  that the only published august.yaml lacks), or if that rendered prompt does not start with the kept instruction line
  and end with the problem.

instance_id = "<MMYY>/<problem_idx>", e.g. "0326/7"; benchmark = "arxivmath" or "brokenarxiv". The outcome source
``adele.results.sources.matharena.fetch`` returns benchmark "<set>-<MMYY>" (from the dataset name) and instance_id
"<problem_idx>"; the join key is f"{MMYY}/{instance_id}" under the family slug. The check below runs that fetch on
the three outcome columns of every month.

Found 2026-10-11: in arxivmath-0526_outputs, Gemini 3.1 Pro Preview and Step 3.7 Flash (3 runs each) saw an earlier
text of 5 problems (small LaTeX and wording edits); in the 0826 outputs, Claude-Fable-5.1 (high) and 3 rows of
Muse Spark 1.3 (3 ArXivMath rows, all 56 BrokenArXiv rows) got an extra time-limit paragraph after the problem. Counts are in the meta file (logged_rows_matched).

Writes:
  data/instances/instances_arxivmath.parquet, instances_brokenarxiv.parquet  benchmark, instance_id, prompt,
      prompt_sha12
  data/instances/meta_arxivmath.csv, meta_brokenarxiv.csv  month, arXiv id, licence, answer type, grading,
      tools, prompt rule, check counts, provenance (no answers, no original statements)
  data/downloads/matharena/<set>-<MMYY>/{train-00000-of-00001.parquet, README.md},
  data/downloads/matharena/eth-sri-matharena/configs/competitions/..., data/downloads/matharena/SOURCES.tsv
and registers both instance files in data/instances/INSTANCES.tsv.

Run: python -I experiments/benchmarks/matharena-data/fetch_tasks.py
"""

import hashlib
import sys
import tempfile
import urllib.request
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import yaml

ROOT = Path(__file__).resolve().parents[3]
CACHE = ROOT / "data" / "downloads" / "matharena"
OUT = ROOT / "data" / "instances"
sys.path.insert(0, str(ROOT / "src"))
from adele.instances import register, validate_instances  # noqa: E402
from adele.results.sources import matharena  # noqa: E402

MATHARENA_COMMIT = "b89f2f0ad64ced464d2944f08c3c0aaeaa0df64b"
CONFIG_RAW = f"https://raw.githubusercontent.com/eth-sri/matharena/{MATHARENA_COMMIT}/configs/competitions"
HF = "https://huggingface.co/datasets/MathArena"
SHARD = "data/train-00000-of-00001.parquet"
LICENCE = "cc-by-sa-4.0"
MONTH_NAMES = {"1225": "december", "0126": "january", "0226": "february", "0326": "march", "0426": "april",
               "0526": "may", "0626": "june", "0826": "august"}
FAMILIES = {  # benchmark slug -> (config dir, months, expected problems)
    "arxivmath": ("arxiv", ["1225", "0126", "0226", "0326", "0426", "0526", "0626", "0826"], 287),
    "brokenarxiv": ("arxiv_false", ["0226", "0326", "0426", "0526", "0626", "0826"], 308),
}
REVISIONS = {  # HF dataset -> commit sha (2026-10-11)
    "arxivmath-1225": "90c60aa1eadbb72168640169d82154b079cdeaac",
    "arxivmath-1225_outputs": "6e427c4860254adc93ee95ebd37dc2b6c6028b4a",
    "arxivmath-0126": "bac939ba603c93f905aa48072980ea681a2824cd",
    "arxivmath-0126_outputs": "306b8e8d1e91c40beb6b2b003adb89e7951bd204",
    "arxivmath-0226": "a038fd1b01405ea1102e165b6ef43693fd16ca6b",
    "arxivmath-0226_outputs": "92e08f2fb94f5fd7fdbf02b335f5ce6ff9a589a8",
    "arxivmath-0326": "14ff32983ae4c72b75fb64eba750f3c27f46607a",
    "arxivmath-0326_outputs": "69bc5be7b2280c8521854515a981ed074aaa7b40",
    "arxivmath-0426": "fc2cb715b5855c100142e4c05a8042351c21f3c8",
    "arxivmath-0426_outputs": "31b49f173ea747a53fb613b8c8f24b6b4bdf6fcf",
    "arxivmath-0526": "69f701c7f266bfba235ef302ff9b19093f7455bb",
    "arxivmath-0526_outputs": "85f1009458c2d2e1527d3e592d04cf40ee8b3a90",
    "arxivmath-0626": "dca0d771ab20c1b8e8c50d0921bf693f7bfe663d",
    "arxivmath-0626_outputs": "f782eef32107837304e2ecd4e78b4cb60ee1e122",
    "arxivmath-0826": "977a3a0083198e11ac4f20fe79288351cebd6281",
    "arxivmath-0826_outputs": "64731d80cf7dd2a83d842c4deb9739c81d129efa",
    "brokenarxiv-0226": "5a0fdca0cbc3a8718667504b2ed69b815e44305c",
    "brokenarxiv-0226_outputs": "b1346bc6e4bd465b9c163debae81126b1140bfea",
    "brokenarxiv-0326": "510ad632a1dfa157a1a50ca744b5cea3b0fe37b8",
    "brokenarxiv-0326_outputs": "d719c23340e971fe956a2503bd157bfdcb67d146",
    "brokenarxiv-0426": "1c64bf1ce72ebc997b0a92896a1414a4d010add0",
    "brokenarxiv-0426_outputs": "34779f2c3c287fda88ea06b4c7885a1d10ae8b36",
    "brokenarxiv-0526": "2761f4553fdc3c49cf9776e740bc8f641a8937aa",
    "brokenarxiv-0526_outputs": "7ca7ebc694e921b56eb9b5968374918bf2a2b4e4",
    "brokenarxiv-0626": "73dd424784fbdeab599557fcba3d77559c89d1ee",
    "brokenarxiv-0626_outputs": "c4fac0ea2939a252ea72e9712fa49c639becb252",
    "brokenarxiv-0826": "6445b9740c9f932c44a3c1c6019230d08e81a793",
    "brokenarxiv-0826_outputs": "7da551be2a80d7721bd6ee77ef14c8894fdef686",
}
OUTPUT_COLUMNS = ["problem_idx", "model_name", "correct", "problem", "user_message"]


def sha12(t: str) -> str:
    return hashlib.sha256(t.encode()).hexdigest()[:12]


def get(url: str, dest: Path, sources: list) -> bytes:
    """Cached download, logged in SOURCES.tsv."""
    if dest.exists():
        blob = dest.read_bytes()
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "adele-data/0.1"})
        with urllib.request.urlopen(req, timeout=120) as r:
            blob = r.read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
    sources.append(f"{dest.relative_to(CACHE)}\t{url}\t{hashlib.sha256(blob).hexdigest()}\t{len(blob)}")
    return blob


def arxiv_id(src) -> str:
    """"arXiv:YYMM.NNNNN". Older sets store the id as a float (2512.0081 for 2512.00810); the prefix keeps CSV
    readers from parsing it as one again. Version suffixes are dropped."""
    return "arXiv:" + (f"{src:.5f}" if isinstance(src, float) else str(src).split("v")[0])


def rstrip_lines(t: str) -> str:
    return "\n".join(line.rstrip() for line in t.split("\n"))


def read_outputs(name: str) -> tuple:
    """The needed columns of one _outputs shard, read remotely by byte range (no model responses)."""
    from huggingface_hub import HfFileSystem
    fs = HfFileSystem(token=False)
    with fs.open(f"datasets/MathArena/{name}@{REVISIONS[name]}/{SHARD}", "rb") as f:
        frame = pq.read_table(f, columns=OUTPUT_COLUMNS).to_pandas()
        fetched = getattr(getattr(f, "cache", None), "total_requested_bytes", None)
    frame["problem_idx"] = frame["problem_idx"].astype(str)
    return frame, fetched


def outcome_ids(frame: pd.DataFrame, slug_month: str) -> set:
    """Instance ids exactly as adele.results.sources.matharena produces them."""
    with tempfile.TemporaryDirectory(dir=CACHE) as tmp:
        path = Path(tmp) / f"{slug_month}_outputs.parquet"
        frame[["problem_idx", "model_name", "correct"]].to_parquet(path, index=False)
        res = matharena.fetch(dataset=f"MathArena/{slug_month}_outputs", local_path=str(path))
    assert set(res["benchmark"]) == {slug_month}, set(res["benchmark"])
    return set(res["instance_id"].astype(str))


def build(slug: str, sources: list) -> tuple:
    cdir, months, expected = FAMILIES[slug]
    rows, meta, report = [], [], []
    for mm in months:
        name = f"{slug}-{mm}"
        rev = REVISIONS[name]
        readme = get(f"{HF}/{name}/resolve/{rev}/README.md", CACHE / name / "README.md", sources).decode()
        assert f"license: {LICENCE}" in readme, f"{name}: licence"
        get(f"{HF}/{name}/resolve/{rev}/{SHARD}", CACHE / name / Path(SHARD).name, sources)
        probs = pd.read_parquet(CACHE / name / Path(SHARD).name)
        assert probs["problem_idx"].is_unique, name
        cfg_url = f"{CONFIG_RAW}/{cdir}/{MONTH_NAMES[mm]}.yaml"
        cfg = yaml.safe_load(get(cfg_url, CACHE / "eth-sri-matharena" / "configs" / "competitions" / cdir /
                                 f"{MONTH_NAMES[mm]}.yaml", sources))
        assert cfg["dataset_path"] == f"MathArena/{name}" and cfg["n_problems"] == len(probs), name
        template = cfg["instruction"] if "{problem}" in cfg["instruction"] else cfg["instruction"] + "\n\n{problem}"
        head = cfg["instruction"].split("\n", 1)[0].rstrip()

        out, fetched = read_outputs(name + "_outputs")
        ids_out = outcome_ids(out, name)
        logged = out.groupby("problem_idx")["user_message"].apply(list).to_dict()
        failures = []
        for r in probs.itertuples():
            pidx = str(r.problem_idx)
            assert (out.loc[out.problem_idx == pidx, "problem"] == r.problem).all(), f"{name}/{pidx}: problem text"
            full = template.format(problem=r.problem)
            prompt = r.problem if slug == "arxivmath" else f"{head}\n\n\n{r.problem}"
            assert full.startswith(head) and full.endswith(r.problem), f"{name}/{pidx}: kept parts not in the prompt"
            msgs = logged.get(pidx, [])
            matched = sum(m == full for m in msgs)
            matched_ws = sum(rstrip_lines(m) == rstrip_lines(full) for m in msgs)
            if not matched_ws:
                failures.append(pidx)
            iid = f"{mm}/{pidx}"
            rows.append({"benchmark": slug, "instance_id": iid, "prompt": prompt, "prompt_sha12": sha12(prompt)})
            meta.append({
                "instance_id": iid, "month": mm, "problem_idx": pidx, "arxiv_id": arxiv_id(r.source),
                "licence": LICENCE,
                "answer_type": "final answer" if slug == "arxivmath" else
                               f"proof of a false statement (judge-graded, max {int(r.points)} points)",
                "grading": cfg.get("grading", "answer parser") if slug == "arxivmath"
                           else ",".join(cfg.get("judge_configs", [])),
                "tools_allowed": bool(cfg.get("allow_harness", False)),
                "prompt_rule": "problem only" if slug == "arxivmath" else "first instruction line + problem",
                "byte_identical_to_matharena": prompt == full, "prompt_chars": len(prompt),
                "logged_rows": len(msgs), "logged_rows_matched": matched,
                "logged_rows_matched_up_to_trailing_spaces": matched_ws,
                "dataset": f"MathArena/{name}", "dataset_revision": rev,
                "outputs_revision": REVISIONS[name + "_outputs"], "config_url": cfg_url,
            })
        if failures:
            raise SystemExit(f"{name}: no logged user message equals the rendered MathArena prompt for {failures}")
        ids = {str(i) for i in probs["problem_idx"]}
        rendered = out.problem_idx.map({str(r.problem_idx): rstrip_lines(template.format(problem=r.problem))
                                        for r in probs.itertuples()})
        mism = out.loc[out.user_message.map(rstrip_lines) != rendered, "model_name"]
        report.append({
            "set": name, "n": len(probs), "outcome_ids": len(ids_out),
            "join": f"{len(ids & ids_out)}/{len(ids)}", "outcome_ids_not_in_set": len(ids_out - ids),
            "rows": len(out), "models": out.model_name.nunique(),
            "rows_not_matching": len(mism), "by_model": mism.value_counts().to_dict() or "-",
            "outputs_bytes_fetched": fetched,
        })
        del out
    df = pd.DataFrame(rows)
    assert len(df) == expected, (slug, len(df))
    return df, pd.DataFrame(meta), pd.DataFrame(report)


def main() -> None:
    sources = []
    for slug in FAMILIES:
        df, m, rep = build(slug, sources)
        warnings = validate_instances(df, where=slug)
        path = OUT / f"instances_{slug}.parquet"
        df.to_parquet(path, index=False)
        m.to_csv(OUT / f"meta_{slug}.csv", index=False)
        row = register(path, benchmark=slug, n_dimensions=18)
        with pd.option_context("display.width", 250, "display.max_columns", 20, "display.max_colwidth", 80):
            print(rep.to_string(index=False))
        print(f"{path.name}: {len(df)} problems; prompt chars median {int(m.prompt_chars.median())}, "
              f"max {int(m.prompt_chars.max())}; warnings={warnings}; registered sha256 {row['sha256'][:12]}\n")
    (CACHE / "SOURCES.tsv").write_text("name\turl\tsha256\tbytes\n" + "\n".join(sources) + "\n")


if __name__ == "__main__":
    main()
