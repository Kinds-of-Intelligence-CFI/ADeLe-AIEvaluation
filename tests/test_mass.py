"""Tests for adele.mass: spec validation, pinning, ledger, backends (fakes and mocked SDKs), collect and check.

Nothing here calls a judge, an API or the network.
"""

import hashlib
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pandas as pd
import pytest
from click.testing import CliRunner

from adele.cli import main
from adele.instances import prepare
from adele.mass.backends.anthropic_batch import AnthropicBatchBackend
from adele.mass.backends.fake import FakeBackend
from adele.mass.backends.litellm_backend import LiteLLMBackend
from adele.mass.backends.openai_batch import OpenAIBatchBackend, build_request as openai_request
from adele.mass.backends.subagent import SubagentBackend
from adele.mass.check import check
from adele.mass.collect import collect, is_requested
from adele.mass.ledger import MAX_RETURNS, Ledger, run_lock
from adele.mass.pin import cell_id, load_run, pin, plan_cells
from adele.mass.runner import release, submit_next, sync
from adele.mass.spec import REPO_ROOT, SpecError, load_spec

SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
OPUS = "claude-opus-5-5"
CWD = "/Users/someone/Developer/ADELE"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@pytest.fixture
def env(tmp_path, monkeypatch):
    """A toy frozen benchmark (3 tasks, one with \\r\\n line ends), a judge-io folder and agent files."""
    monkeypatch.setenv("ADELE_JUDGE_IO", str(tmp_path / "io"))
    monkeypatch.setenv("ADELE_AGENTS_DIR", str(tmp_path / "agents"))
    (tmp_path / "agents").mkdir()
    for name in ("judge-dispatcher-v2-low", "adele-judge-v2-low"):
        (tmp_path / "agents" / f"{name}.md").write_text(f"---\nname: {name}\n---\n")
    frame = pd.DataFrame({"prompt": ["Fix bug number 0 in the parser module.\r\nThen run the tests carefully.",
                                     "Fix bug number 1 in the parser module, carefully.",
                                     "Fix bug number 2 in the parser module, carefully."],
                          "source_id": ["proj__proj-1", "proj__proj-2", "proj__proj-3"]})
    prepare(["swebench"], tmp_path / "instances", loaders={"swebench": lambda: frame})
    return tmp_path


def write_spec(root: Path, name: str = "toy", refs=("v1/AT", "v2/PLp"), builder: str = "v2",
               judge: str = 'backend = "fake"\nmodel = "claude-opus-5-5"\neffort = "low"', extra_tasks: str = "",
               fname: str = None) -> Path:
    refs_toml = ", ".join(f'"{r}"' for r in refs)
    text = (f'name = "{name}"\n[tasks]\nbenchmarks = ["swe-bench-verified"]\n'
            f'instances_dir = "{root / "instances"}"\n{extra_tasks}\n'
            f'[rubrics]\nrefs = [{refs_toml}]\n[prompt]\nbuilder = "{builder}"\n[judge]\n{judge}\n')
    path = root / (fname or f"{name}.toml")
    path.write_text(text)
    return path


def pinned(env, **kw):
    run, _ = pin(load_spec(write_spec(env, **kw)), runs_root=env / "runs")
    return run


def subagent(cwd: str = CWD, **relay) -> str:
    extra = "".join(f"\n{k} = {v}" for k, v in relay.items())
    return f'backend = "subagent"\nmodel = "claude-opus-5-5"\neffort = "low"\n[judge.relay]\ncwd = "{cwd}"{extra}'


# ----------------------------------------------------------------------------- spec

@pytest.mark.parametrize("refs,match", [
    (["v1/XX"], "unknown rubric ref"),
    (["v1/UG_choice_num"], "UG_choice_num"),
    (["AT"], "v1/<code>"),
    (["v3/AT"], "v1/<code>"),
    (["v1/AT", "v1/AT"], "duplicates"),
])
def test_spec_rejects_bad_rubric_refs(env, refs, match):
    with pytest.raises(SpecError, match=match):
        load_spec(write_spec(env, refs=refs))


def test_spec_rejects_bad_builder_backend_and_keys(env):
    with pytest.raises(SpecError, match="prompt.builder"):
        load_spec(write_spec(env, builder="v3"))
    with pytest.raises(SpecError, match="judge.backend"):
        load_spec(write_spec(env, judge='backend = "carrier-pigeon"\nmodel = "x"'))
    with pytest.raises(SpecError, match="unknown key"):
        load_spec(write_spec(env, judge='backend = "fake"\nmodel = "x"\ntemprature = 0'))
    with pytest.raises(SpecError, match="retry"):
        load_spec(write_spec(env, judge='backend = "fake"\nmodel = "x"\nretry = { typo = 1 }'))
    with pytest.raises(SpecError, match="effort is required"):
        load_spec(write_spec(env, judge='backend = "subagent"\nmodel = "claude-opus-5-5"'))


def test_spec_defaults_for_subagent(env):
    spec = load_spec(write_spec(env, judge='backend = "subagent"\nmodel = "claude-opus-5-5"\neffort = "low"'))
    assert spec.judge.folder == "opus-low" and spec.judge.relay["batch_size"] == 50
    assert spec.judge.relay["dispatcher"] == "judge-dispatcher-v2-low"
    assert spec.judge.relay["judge_agent"] == "adele-judge-v2-low"
    assert spec.judge.retry == {"fallback_writer": 1, "unparsed": 1, "refusal": 1, "error": 1, "protocol": 1}


def test_codes_shared_across_generations_stay_distinct(env):
    cells, prompts, frozen = plan_cells(load_spec(write_spec(env, refs=["v1/MSm", "v2/MSm"])))
    v1 = [c for c in cells if c["rubric_ref"] == "v1/MSm"]
    v2 = [c for c in cells if c["rubric_ref"] == "v2/MSm"]
    assert len(v1) == len(v2) == 3 and {c["code"] for c in cells} == {"MSm"}
    assert not {c["cell_id"] for c in v1} & {c["cell_id"] for c in v2}
    assert {c["prompt_sha256"] for c in v1}.isdisjoint({c["prompt_sha256"] for c in v2})
    assert frozen["rubrics"]["v1/MSm"]["file"].endswith("data_v1/MSm.txt")
    assert frozen["rubrics"]["v2/MSm"]["file"].endswith("Paolo_Pablo/MSm.txt")


def test_subset_with_keep_column(env):
    (env / "subset.csv").write_text("instance_id,keep\nproj__proj-1,True\nproj__proj-2,False\n")
    cells, _, frozen = plan_cells(load_spec(write_spec(env, extra_tasks=f'subset = "{env / "subset.csv"}"')))
    assert {c["instance_id"] for c in cells} == {"proj__proj-1"}
    assert frozen["tasks"]["subset"]["n_ids"] == 1
    (env / "subset.csv").write_text("instance_id\nnope\n")
    with pytest.raises(SpecError, match="not in the benchmarks"):
        plan_cells(load_spec(write_spec(env, extra_tasks=f'subset = "{env / "subset.csv"}"')))


# ----------------------------------------------------------------------------- pin

def test_cell_ids_are_safe_and_stable():
    ids = {cell_id(b, i, r, k) for b in ("swe-bench-verified", "tau2-x") for i in ("a/b__c d", "é", "x" * 300)
           for r in ("v1/AT", "v2/PLp") for k in (1, 2)}
    assert len(ids) == 24 and all(SAFE_ID.match(c) and "__" not in c for c in ids)
    assert cell_id("b", "i", "v2/PLp", 1) == cell_id("b", "i", "v2/PLp", 1)


def test_pin_writes_manifest_cells_ledger_and_prompts(env):
    run = pinned(env)
    m = run.manifest
    assert len(run.cells) == 6 and m["frozen"]["cells"]["n"] == 6
    for ref, r in m["frozen"]["rubrics"].items():
        assert r["sha256"] == sha((REPO_ROOT / r["file"]).read_bytes())
    inst = m["frozen"]["tasks"]["benchmarks"]["swe-bench-verified"]
    assert inst["file_sha256"] == sha((env / "instances" / inst["file"]).read_bytes()) and inst["n_selected"] == 3
    assert m["frozen"]["prompt"]["source_sha256"] == sha((REPO_ROOT / "src/adele/annotation/prompts.py").read_bytes())
    assert m["frozen"]["spec"]["sha256"] and "commit" in m["git"]
    assert m["frozen"]["cells"]["sha256"] == sha((run.dir / "cells.csv").read_bytes())
    for c in run.cells.itertuples():
        assert sha(run.prompt_path(c.cell_id).read_bytes()) == c.prompt_sha256
    assert {r["status"] for r in Ledger.load(run.dir).rows.values()} == {"pending"}


def test_prompts_with_crlf_keep_their_bytes(env):
    run = pinned(env)
    crlf = [c for c in run.cells.index if b"\r\n" in run.prompt_path(c).read_bytes()]
    assert len(crlf) == 2  # task 0 x 2 rubrics
    assert "\r\n" in run.prompt(crlf[0])
    backend = FakeBackend()
    sent = submit_next(run, Ledger.load(run.dir), backend, batch_size=10)
    assert sum(len(i) for _, i in sent) == 6


def test_repin_is_identical_and_keeps_the_ledger(env):
    run = pinned(env)
    ledger = Ledger.load(run.dir)
    first = next(iter(ledger.rows))
    ledger.set(*first, status="submitted", handle="h1")
    ledger.save()
    run.prompt_path(first[0]).unlink()
    cells_before = (run.dir / "cells.csv").read_bytes()
    again, written = pin(load_spec(env / "toy.toml"), runs_root=env / "runs")
    assert written == 1 and (again.dir / "cells.csv").read_bytes() == cells_before
    assert Ledger.load(run.dir).rows[first]["status"] == "submitted"


def test_pin_recovers_from_a_crash_before_the_manifest(env):
    run = pinned(env)
    (run.dir / "manifest.json").unlink()
    again = pinned(env)
    assert len(again.cells) == 6 and (again.dir / "manifest.json").exists()


def test_pin_refuses_a_different_spec_under_the_same_name(env):
    pinned(env)
    with pytest.raises(SpecError, match="different inputs"):
        pin(load_spec(write_spec(env, refs=["v1/AT"], fname="other.toml")), runs_root=env / "runs")


def test_pin_refuses_drifted_instances(env):
    f = env / "instances" / "instances_swe-bench-verified.parquet"
    df = pd.read_parquet(f)
    df.loc[1, "prompt"] = "Fix bug number 9 in the parser module, carefully."
    df.to_parquet(f)
    with pytest.raises(SpecError, match="no longer matches"):
        pinned(env)


# ----------------------------------------------------------------------------- ledger, runner

def test_prompts_are_all_checked_before_anything_is_recorded(env):
    run = pinned(env)
    ledger = Ledger.load(run.dir)
    last = list(run.cells.index)[-1]
    run.prompt_path(last).write_bytes(b"tampered")
    with pytest.raises(ValueError, match="pinned sha256"):
        submit_next(run, ledger, FakeBackend(), batch_size=2)
    assert {r["status"] for r in Ledger.load(run.dir).rows.values()} == {"pending"}


def test_release_and_the_not_sent_cap(env):
    run = pinned(env)
    ledger = Ledger.load(run.dir)
    seen = []
    sent = submit_next(run, ledger, FakeBackend(), batch_size=2, on_sent=lambda h, items: seen.append(h))
    assert seen == [h for h, _ in sent] and len(seen) == 3
    a = sent[0][1][0]
    run.response_path(*a).parent.mkdir(parents=True)
    run.response_path(*a).write_text("an answer")
    released, kept = release(run, ledger, [sent[0][0]])
    assert kept == [a] and released == [sent[0][1][1]]
    assert Ledger.load(run.dir).rows[released[0]]["returns"] == "1"
    cell = released[0]
    for _ in range(MAX_RETURNS - 1):
        assert ledger.release(*cell)
    assert not ledger.release(*cell)
    assert ledger.rows[cell]["status"] == "rejected" and ledger.rows[cell]["reason"] == "error"


def test_run_lock_is_exclusive(env):
    run = pinned(env)
    with run_lock(run.dir):
        out = CliRunner().invoke(main, ["mass", "collect", str(run.dir)])
        assert out.exit_code != 0 and "locked" in out.output
    assert CliRunner().invoke(main, ["mass", "collect", str(run.dir)]).exit_code == 0


# ----------------------------------------------------------------------------- end to end, fake backend

def drain(run, backend, ledger):
    for _ in range(10):
        submit_next(run, ledger, backend, batch_size=4)
        collect(run, backend, ledger)
        if not ledger.to_submit(run.judge.retry) and not ledger.with_status("submitted"):
            return
    raise AssertionError("run did not finish")


def test_end_to_end_with_retries_resume_and_budget(env):
    judge = ('backend = "fake"\nmodel = "claude-opus-5-5"\neffort = "low"\n'
             'retry = { fallback_writer = 1, unparsed = 1, refusal = 0, error = 1 }')
    run = pinned(env, judge=judge)
    a, b, c, d = list(run.cells.index)[:4]
    backend = FakeBackend(script={(a, 1): "wrong_writer", (b, 1): "unparsed", (b, 2): "unparsed",
                                  (c, 1): "refusal", (d, 1): "error"})
    ledger = Ledger.load(run.dir)
    submit_next(run, ledger, backend, batch_size=2, max_cells=3)
    # Interrupted before fetching: a fresh process sees the submissions and does not send them again.
    ledger = Ledger.load(run.dir)
    assert len(ledger.with_status("submitted")) == 3 and len(ledger.to_submit(run.judge.retry)) == 3
    sync(run, ledger, backend)
    drain(run, backend, Ledger.load(run.dir))
    assert len(backend.calls) == len(set(backend.calls)) == 6 + 3  # a, b and d retried once each
    lab = pd.read_csv(run.dir / "labels.csv").set_index("cell_id")
    assert len(lab) == 6
    assert lab.loc[a, "valid"] and lab.loc[a, "attempt"] == 2 and lab.loc[a, "writer_model"] == OPUS
    assert not lab.loc[b, "valid"] and lab.loc[b, "attempt"] == 2 and pd.isna(lab.loc[b, "level"])
    assert not lab.loc[c, "valid"] and lab.loc[c, "attempt"] == 1
    assert lab.loc[d, "valid"] and lab.loc[d, "attempt"] == 2
    assert set(lab.columns) >= {"run", "rubric_ref", "generation", "model_requested", "prompt_builder",
                                "prompt_sha256", "response_sha256", "effort", "backend", "protocol_ok"}
    assert lab["valid"].sum() == 4 and lab["protocol_ok"].isna().all()
    rep = check(run)
    assert rep["ok"] and rep["totals"] == {"done": 4, "no_label": 2, "in_flight": 0, "todo": 0}
    assert rep["rejections"] == {"fallback_writer": 1, "unparsed": 2, "refusal": 1, "error": 1}
    # The first, rejected answer of `a` is kept in its own folder; the label is the retry's.
    assert run.response_path(a, 1).exists() and run.response_path(a, 2).parent.name == f"{run.judge.folder}-a2"
    run.response_path(a, 2).unlink()
    assert not check(run)["ok"] and check(run)["missing_answers"] == [str(run.response_path(a, 2))]


def test_is_requested_allows_snapshots_only():
    assert is_requested("claude-opus-5-5", OPUS) and is_requested("claude-haiku-4-5-20251001", "claude-haiku-4-5")
    assert not is_requested("claude-opus-5-5", "claude-opus-5") and not is_requested("", OPUS)
    assert not is_requested("claude-opus-4-8", OPUS) and is_requested("gpt-4o-2024-08-06", "gpt-4o")
    assert is_requested("claude-opus-5-5", f"anthropic/{OPUS}") and not is_requested("gpt-4o-mini", "gpt-4o")


def test_cli_plan_pin_run_status_collect_check(env):
    spec = write_spec(env)
    r = CliRunner()
    out = r.invoke(main, ["mass", "plan", str(spec)])
    assert out.exit_code == 0, out.output
    assert "6 cells = 3 tasks x 2 rubrics" in out.output and not (env / "runs").exists()
    assert r.invoke(main, ["mass", "pin", str(spec), "--runs-root", str(env / "runs")]).exit_code == 0
    run_dir = str(env / "runs" / "toy")
    dry = r.invoke(main, ["mass", "run", run_dir, "--dry-run"])
    assert "would submit 6 cells" in dry.output and Ledger.load(run_dir).with_status("pending")
    out = r.invoke(main, ["mass", "run", run_dir, "--max-cells", "4", "--poll-interval", "0"])
    assert out.exit_code == 0, out.output
    assert len(Ledger.load(run_dir).with_status("parsed")) == 4
    r.invoke(main, ["mass", "run", run_dir, "--poll-interval", "0"])
    for cmd in ("status", "collect", "check"):
        out = r.invoke(main, ["mass", cmd, run_dir])
        assert out.exit_code == 0, out.output
    assert "check OK" in out.output and len(pd.read_csv(Path(run_dir) / "labels.csv")) == 6
    assert "use `adele mass run`" in r.invoke(main, ["mass", "next", run_dir]).output


# ----------------------------------------------------------------------------- subagent backend

def transcript(dirpath: Path, name: str, prompt: Path, response: Path, text: str, model: str = OPUS,
               write_record: bool = True, extra: list = (), attachments: list = (), reads: list = None) -> None:
    """A judge transcript shaped like Claude Code's subagent JSONL files. ``reads``: (offset, limit) Read calls
    whose results number the returned prompt lines as the Read tool does; default one plain Read."""
    recs = [{"type": "user", "cwd": CWD, "timestamp": "2026-10-01T10:00:00Z",
             "message": {"role": "user", "content": f"Prompt file: {prompt}\nResponse file: {response}"}}]
    recs += [{"type": "attachment", "attachment": {"type": t}} for t in attachments]
    if reads is None:
        recs.append({"type": "assistant", "timestamp": "2026-10-01T10:00:01Z", "perTurnEffort": "low",
                     "message": {"model": model, "content": [
                         {"type": "tool_use", "name": "Read", "input": {"file_path": str(prompt)}}]}})
    lines = prompt.read_text().split("\n") if reads else []
    for k, (offset, limit) in enumerate(reads or []):
        recs.append({"type": "assistant", "perTurnEffort": "low", "message": {"model": model, "content": [
            {"type": "tool_use", "id": f"r{k}", "name": "Read",
             "input": {"file_path": str(prompt), "offset": offset, "limit": limit}}]}})
        got = "\n".join(f"{n}\t{lines[n - 1]}" for n in range(offset, min(offset + limit, len(lines) + 1)))
        recs.append({"type": "user", "message": {"content": [
            {"type": "tool_result", "tool_use_id": f"r{k}", "content": got}]}})
    recs += extra
    if write_record:
        recs.append({"type": "assistant", "timestamp": "2026-10-01T10:00:05Z", "perTurnEffort": "low",
                     "message": {"model": model, "content": [
                         {"type": "tool_use", "name": "Write",
                          "input": {"file_path": str(response), "content": text}}]}})
    recs.append({"type": "user", "timestamp": "2026-10-01T10:00:06Z", "message": {"content": [
        {"type": "tool_result", "content": f"File created successfully at: {response} (file state is current)"}]}})
    recs.append({"type": "assistant", "message": {"model": model, "content": [
        {"type": "tool_use", "name": "SubagentHandback", "input": {"message": "DONE"}}]}})
    (dirpath / f"agent-{name}.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    (dirpath / f"agent-{name}.meta.json").write_text(json.dumps({"agentType": "adele-judge-v2-low"}))


def test_subagent_next_message_format(env, monkeypatch):
    run = pinned(env, judge=subagent(cwd=str(env), batch_size=4))
    ledger = Ledger.load(run.dir)
    sent = submit_next(run, ledger, SubagentBackend(), batch_size=4, max_batches=4)
    assert [len(items) for _, items in sent] == [4, 2]
    handle, items = sent[0]
    msg = (run.io_dir / "relays" / f"{handle}.txt").read_text()
    assert msg == "\n".join([f"Model: opus", f"I/O folder: {run.io_dir}", "Judge folder name: opus-low",
                             "Cells (4):", *[c for c, _ in items]])
    assert all(ledger.rows[it]["handle"] == handle for it in items)
    out = CliRunner().invoke(main, ["mass", "next", str(run.dir)])
    assert out.exit_code != 0 and "must be" in out.output  # the test's cwd is not the run's
    monkeypatch.chdir(env)
    out = CliRunner().invoke(main, ["mass", "next", str(run.dir)])
    assert out.exit_code != 0 and "still submitted" in out.output and f"cwd: {env}" in out.output
    out = CliRunner().invoke(main, ["mass", "release", str(run.dir), "--all"])
    assert out.exit_code == 0 and "released 6" in out.output
    out = CliRunner().invoke(main, ["mass", "next", str(run.dir), "--max", "1"])
    assert out.exit_code == 0 and out.output.count("=== end ===") == 1 and "agent: judge-dispatcher-v2-low" in out.output


def test_next_and_check_refuse_changed_agent_files(env, monkeypatch):
    run = pinned(env, judge=subagent(cwd=str(env)))
    monkeypatch.chdir(env)
    (env / "agents" / "adele-judge-v2-low.md").write_text("edited")
    out = CliRunner().invoke(main, ["mass", "next", str(run.dir)])
    assert out.exit_code != 0 and "agent files changed" in out.output
    rep = check(run)
    assert not rep["ok"] and rep["agent_drift"] == ["adele-judge-v2-low"]


def test_subagent_fetch_attributes_writers_and_settles_cells(env):
    run = pinned(env, judge=subagent())
    ledger = Ledger.load(run.dir)
    (h, items), = submit_next(run, ledger, SubagentBackend(), batch_size=10, max_cells=5)
    tdir = env / "subagents"
    tdir.mkdir()
    (ok, other, confirmed, dropped, failed) = [c for c, _ in items]
    for i, (cell, model, write_record) in enumerate([(ok, OPUS, True), (other, "claude-opus-4-8", True),
                                                     (confirmed, OPUS, False)]):
        text = f"Short assessment.\nThe level of X demanded by this task is: {i + 1}"
        run.response_path(cell, 1).write_text(text)
        transcript(tdir, f"a{i}", run.prompt_path(cell), run.response_path(cell, 1), text, model, write_record)
    # `failed` reached a judge that wrote nothing; `dropped` never reached one.
    transcript(tdir, "a9", run.prompt_path(failed), run.response_path(failed, 1), "x", write_record=False)
    (tdir / "agent-a9.jsonl").write_text((tdir / "agent-a9.jsonl").read_text().replace("File created", "Error"))
    res = collect(run, SubagentBackend(tdir, relays_done=True), ledger)
    latest = Ledger.load(run.dir).latest()
    assert latest[ok]["status"] == "parsed" and latest[ok]["level"] == "1" and latest[ok]["protocol"] == "ok"
    assert latest[other]["status"] == "rejected" and latest[other]["reason"] == "fallback_writer"
    assert latest[other]["writer_model"] == "claude-opus-4-8"
    assert latest[confirmed]["status"] == "parsed" and latest[confirmed]["writer_model"] == OPUS
    assert latest[dropped]["status"] == "pending" and latest[dropped]["handle"] == ""
    assert latest[failed]["status"] == "rejected" and latest[failed]["reason"] == "error"
    assert res["labels"] == 2
    assert pd.read_csv(run.dir / "labels.csv")["protocol_ok"].tolist() == [True, True]
    # Retries go to a fresh folder and never resend a settled cell.
    nxt = submit_next(run, ledger, SubagentBackend(), batch_size=10)
    assert sorted((c, a) for _, its in nxt for c, a in its) == sorted(
        [(other, 2), (failed, 2), (dropped, 1)] + [(c, 1) for c in run.cells.index if c not in
                                                   {ok, other, confirmed, dropped, failed}])
    assert any("Judge folder name: opus-low-a2" in (run.io_dir / "relays" / f"{h}.txt").read_text()
               for h, _ in nxt)


def test_subagent_protocol_breach_rejects_the_answer(env):
    run = pinned(env, judge=subagent().replace('effort = "low"', 'effort = "low"\nretry = { protocol = 0 }'))
    ledger = Ledger.load(run.dir)
    (_, items), = submit_next(run, ledger, SubagentBackend(), batch_size=10, max_cells=2)
    tdir = env / "subagents"
    tdir.mkdir()
    bash = {"type": "assistant", "message": {"model": OPUS, "content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}}
    text = "The level of X demanded by this task is: 2"
    for i, (cell, _) in enumerate(items):
        run.response_path(cell, 1).write_text(text)
        transcript(tdir, f"p{i}", run.prompt_path(cell), run.response_path(cell, 1), text,
                   extra=[bash] if i == 0 else [])
    collect(run, SubagentBackend(tdir, relays_done=True), ledger)
    lab = pd.read_csv(run.dir / "labels.csv").set_index("cell_id")
    bad, good = items[0][0], items[1][0]
    assert not lab.loc[bad, "valid"] and not lab.loc[bad, "protocol_ok"]
    assert lab.loc[good, "valid"] and lab.loc[good, "protocol_ok"]
    assert "Bash" in Ledger.load(run.dir).latest()[bad]["protocol"]
    # The rejected attempt's breach no longer fails the check.
    rep = check(run, tdir)
    assert not rep["protocol"]["failures"] and [f["cell"] for f in rep["protocol"]["rejected_failures"]] == [bad]


def test_subagent_fetch_refuses_untraceable_answers(env):
    run = pinned(env, judge=subagent())
    ledger = Ledger.load(run.dir)
    (_, items), = submit_next(run, ledger, SubagentBackend(), batch_size=10, max_cells=2)
    tdir = env / "elsewhere"
    tdir.mkdir()
    with pytest.raises(ValueError, match="no judge transcripts"):
        collect(run, SubagentBackend(tdir, relays_done=True), ledger)
    a, b = [c for c, _ in items]
    transcript(tdir, "x", run.prompt_path(a), run.response_path(a, 1), "what the judge wrote")
    run.response_path(a, 1).write_text("edited by hand")
    with pytest.raises(ValueError, match="match no Write call"):
        collect(run, SubagentBackend(tdir, relays_done=True), Ledger.load(run.dir))
    assert len(Ledger.load(run.dir).with_status("submitted")) == 2


def test_subagent_collect_waits_until_relays_are_done(env):
    run = pinned(env, judge=subagent())
    ledger = Ledger.load(run.dir)
    submit_next(run, ledger, SubagentBackend(), batch_size=10)
    collect(run, SubagentBackend(), ledger)
    assert len(Ledger.load(run.dir).with_status("submitted")) == 6


def test_protocol_check(env):
    run = pinned(env, judge=subagent())
    tdir = env / "subagents"
    tdir.mkdir()
    cells = list(run.cells.index)
    for i, cell in enumerate(cells[:3]):
        transcript(tdir, f"g{i}", run.prompt_path(cell), run.response_path(cell, 1), "x")
    rep = check(run, tdir)
    assert rep["ok"] and rep["protocol"]["transcripts"] == 3 and rep["protocol"]["models"] == {OPUS: 3}
    bash = {"type": "assistant", "message": {"model": OPUS, "content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}}]}}
    transcript(tdir, "b1", run.prompt_path(cells[3]), run.response_path(cells[3], 1), "x", extra=[bash])
    transcript(tdir, "b2", run.prompt_path(cells[4]), run.response_path(cells[4], 1), "x",
               attachments=["nested_memory"])
    rep = check(run, tdir)
    problems = {f["cell"]: " ".join(f["problems"]) for f in rep["protocol"]["failures"]}
    assert not rep["ok"] and set(problems) == {cells[3], cells[4]}
    assert "Read(prompt) then Write" in problems[cells[3]] and "nested_memory" in problems[cells[4]]
    for f in ("b1", "b2"):
        (tdir / f"agent-{f}.jsonl").unlink()
    transcript(tdir, "b3", run.prompt_path(cells[0]), run.response_path(cells[0], 1), "x")
    rep = check(run, tdir)
    assert not rep["ok"] and rep["protocol"]["called_more_than_once"] == [str(run.response_path(cells[0], 1))]
    assert "cwd" in " ".join(check(run, tdir, cwd="/elsewhere")["protocol"]["failures"][0]["problems"])


def test_chunked_reads_must_return_every_prompt_line(env):
    run = pinned(env, judge=subagent(chunk_lines=2))
    tdir = env / "subagents"
    tdir.mkdir()
    cells = list(run.cells.index)
    n = len(run.prompt_path(cells[0]).read_text().split("\n"))
    chunks = [(o, 2) for o in range(1, n + 1, 2)]
    transcript(tdir, "c0", run.prompt_path(cells[0]), run.response_path(cells[0], 1), "x", reads=chunks)
    transcript(tdir, "c1", run.prompt_path(cells[1]), run.response_path(cells[1], 1), "x", reads=chunks[:-1])
    rep = check(run, tdir)
    problems = {f["cell"]: " ".join(f["problems"]) for f in rep["protocol"]["failures"]}
    assert set(problems) == {cells[1]} and "not returned by any Read" in problems[cells[1]]
    long = run.prompt_path(cells[2])
    long.write_text(long.read_text() + "\n" + "y" * 2001)
    m = len(long.read_text().split("\n"))
    transcript(tdir, "c2", long, run.response_path(cells[2], 1), "x", reads=[(o, 2) for o in range(1, m + 1, 2)])
    problems = {f["cell"]: " ".join(f["problems"]) for f in check(run, tdir)["protocol"]["failures"]}
    assert "longer than 2000" in problems[cells[2]]
    # Without chunk_lines a second Read breaks the protocol.
    plain = pinned(env, name="plain", judge=subagent())
    pdir = env / "plain-subagents"
    pdir.mkdir()
    c = list(plain.cells.index)[0]
    transcript(pdir, "p0", plain.prompt_path(c), plain.response_path(c, 1), "x", reads=[(1, 2), (3, 100)])
    assert "Read(prompt) then Write" in " ".join(check(plain, pdir)["protocol"]["failures"][0]["problems"])


def test_equivalent_paths_are_the_same_file(env):
    run = pinned(env, judge=subagent())
    tdir = env / "subagents"
    tdir.mkdir()
    cell = list(run.cells.index)[0]
    response = run.response_path(cell, 1)
    detour = run.io_dir / "prompts" / ".." / "responses" / response.parent.name / response.name
    transcript(tdir, "d0", run.prompt_path(cell), response, "x")
    (tdir / "agent-d0.jsonl").write_text((tdir / "agent-d0.jsonl").read_text().replace(
        f'"file_path": "{response}", "content"', f'"file_path": "{detour}", "content"'))
    assert str(detour) in (tdir / "agent-d0.jsonl").read_text()
    assert check(run, tdir)["ok"]


def test_spec_rejects_bad_chunk_lines(env):
    with pytest.raises(SpecError, match="chunk_lines"):
        load_spec(write_spec(env, judge=subagent(chunk_lines=0)))


# ----------------------------------------------------------------------------- API backends (mocked)

def answer_text(level: int) -> str:
    return f"Assessment.\nThe level of X demanded by this task is: {level}"


class FakeAnthropic:
    """Result types by request index: 0 errored, 1 refusal, 2 expired, others succeeded."""

    def __init__(self, model=OPUS):
        self.requests, self.model, self.options = None, model, None
        self.messages = SimpleNamespace(batches=self)

    def with_options(self, **kw):
        self.options = kw
        return self

    def create(self, requests):
        self.requests = requests
        return SimpleNamespace(id="msgbatch_1")

    def retrieve(self, batch_id):
        return SimpleNamespace(processing_status="ended")

    def results(self, batch_id):
        out = []
        for i, r in enumerate(self.requests):
            if i in (0, 2):
                kind = "errored" if i == 0 else "expired"
                out.append(SimpleNamespace(custom_id=r["custom_id"], result=SimpleNamespace(type=kind)))
                continue
            msg = SimpleNamespace(model=self.model, stop_reason="refusal" if i == 1 else "end_turn",
                                  content=[SimpleNamespace(type="text", text=answer_text(3))],
                                  usage=SimpleNamespace(input_tokens=1000, output_tokens=50))
            out.append(SimpleNamespace(custom_id=r["custom_id"], result=SimpleNamespace(type="succeeded", message=msg)))
        return reversed(out)  # results come in any order


def test_anthropic_batch_backend(env):
    run = pinned(env, judge='backend = "anthropic-batch"\nmodel = "claude-opus-5-5"\neffort = "low"\n'
                            'retry = { refusal = 0, error = 0 }')
    client = FakeAnthropic()
    backend = AnthropicBatchBackend(client=client)
    ledger = Ledger.load(run.dir)
    submit_next(run, ledger, backend, batch_size=100)
    assert client.options == {"max_retries": 0}
    req = client.requests[0]
    assert req["params"]["output_config"] == {"effort": "low"} and req["params"]["model"] == OPUS
    assert "thinking" not in req["params"] and "temperature" not in req["params"]
    assert req["params"]["messages"][0]["content"] == run.prompt(req["custom_id"].rsplit("-a", 1)[0])
    assert all(SAFE_ID.match(r["custom_id"]) for r in client.requests)
    assert {r["handle"] for r in Ledger.load(run.dir).rows.values()} == {"msgbatch_1"}
    res = collect(run, backend, ledger)
    assert res["labels"] == 3 and res["no_label"] == 2
    rows = Ledger.load(run.dir).rows.values()
    assert {r["reason"] for r in rows if r["status"] == "rejected"} == {"error", "refusal"}
    assert {r["tokens_in"] for r in rows if r["status"] == "parsed"} == {"1000"}
    expired = [r for r in rows if r["status"] == "pending"]
    assert len(expired) == 1 and expired[0]["returns"] == "1" and expired[0]["attempt"] == "1"


def openai_client(uploaded, status="completed", models=None):
    def files_create(file, purpose):
        uploaded["lines"] = [json.loads(x) for x in file[1].decode().splitlines()]
        return SimpleNamespace(id="file-in")

    def content(file_id):
        n = len(uploaded["lines"]) if status == "completed" else 2
        lines = [{"custom_id": r["custom_id"], "response": {"status_code": 200, "body": {
            "model": (models or {}).get(i, "gpt-5.2-2026-01-01"),
            "choices": [{"message": {"content": answer_text(2)}}],
            "usage": {"prompt_tokens": 900, "completion_tokens": 40}}}} for i, r in enumerate(uploaded["lines"][:n])]
        return SimpleNamespace(text="\n".join(json.dumps(x) for x in lines))

    client = SimpleNamespace(
        files=SimpleNamespace(create=files_create, content=content),
        batches=SimpleNamespace(create=lambda **kw: SimpleNamespace(id="batch_1"),
                                retrieve=lambda bid: SimpleNamespace(status=status, output_file_id="file-out",
                                                                     error_file_id=None)))
    client.with_options = lambda **kw: uploaded.update(options=kw) or client
    return client


def test_openai_batch_backend(env):
    run = pinned(env, judge='backend = "openai-batch"\nmodel = "gpt-5.2"\neffort = "medium"')
    uploaded = {}
    backend = OpenAIBatchBackend(client=openai_client(uploaded, models={0: "gpt-5.2-mini"}))
    ledger = Ledger.load(run.dir)
    submit_next(run, ledger, backend, batch_size=100)
    assert uploaded["options"] == {"max_retries": 0}
    body = uploaded["lines"][0]["body"]
    assert body["reasoning_effort"] == "medium" and "temperature" not in body
    assert uploaded["lines"][0]["url"] == "/v1/chat/completions"
    res = collect(run, backend, ledger)
    # A dated snapshot of the requested model counts as the model; another model does not.
    assert res["labels"] == 5
    assert len([r for r in Ledger.load(run.dir).rows.values() if r["reason"] == "fallback_writer"]) == 1


def test_openai_expired_batch_returns_unrun_cells_to_pending(env):
    run = pinned(env, judge='backend = "openai-batch"\nmodel = "gpt-4o"')
    uploaded = {}
    backend = OpenAIBatchBackend(client=openai_client(uploaded, status="expired", models={0: "gpt-4o", 1: "gpt-4o"}))
    ledger = Ledger.load(run.dir)
    submit_next(run, ledger, backend, batch_size=100)
    assert uploaded["lines"][0]["body"]["temperature"] == 0
    collect(run, backend, ledger)
    rows = Ledger.load(run.dir).rows.values()
    assert sum(r["status"] == "parsed" for r in rows) == 2 and sum(r["status"] == "pending" for r in rows) == 4


def test_openai_temperature_rule(env):
    for model, has_temp in (("gpt-5.2", False), ("o3", False), ("gpt-4o", True)):
        run = pinned(env, name=f"t-{model.replace('.', '')}", judge=f'backend = "openai-batch"\nmodel = "{model}"')
        body = openai_request(run, run.cells.index[0], 1)["body"]
        assert ("temperature" in body) is has_temp, model


def test_litellm_backend_records_the_handle_first_and_resumes(env):
    run = pinned(env, judge='backend = "litellm"\nmodel = "gemini/gemini-3-flash"\nretry = { error = 0 }')
    calls = []

    def completion(**kw):
        calls.append(kw)
        if len(calls) == 1:
            raise RuntimeError("rate limited")
        return SimpleNamespace(model="gemini-3-flash", choices=[SimpleNamespace(
            message=SimpleNamespace(content=answer_text(4)))], usage=SimpleNamespace(prompt_tokens=5,
                                                                                    completion_tokens=6))

    backend = LiteLLMBackend(completion=completion, max_workers=1)
    ledger = Ledger.load(run.dir)
    (handle, items), = submit_next(run, ledger, backend, batch_size=100)
    assert not calls and {r["handle"] for r in Ledger.load(run.dir).rows.values()} == {handle}
    # An earlier, interrupted pass already answered the first item: only the other five are called.
    first = items[0]
    (run.io_dir / "api" / f"{handle}.jsonl").write_text(json.dumps(
        {"custom_id": f"{first[0]}-a{first[1]}", "text": answer_text(1), "model": "gemini-3-flash",
         "tokens_in": 1, "tokens_out": 1}) + "\n")
    res = collect(run, backend, ledger)
    assert len(calls) == 5 and calls[0]["temperature"] == 0.0 and "reasoning_effort" not in calls[0]
    assert res["labels"] == 5 and res["no_label"] == 1


# ----------------------------------------------------------------------------- the example specs

SPECS = REPO_ROOT / "experiments/benchmarks/mass-annotation/specs"
HAVE_INSTANCES = (REPO_ROOT / "data/instances/INSTANCES.tsv").exists()


@pytest.mark.skipif(not HAVE_INSTANCES, reason="frozen instances not present")
def test_example_spec_pins_offline(tmp_path, monkeypatch):
    monkeypatch.setenv("ADELE_JUDGE_IO", str(tmp_path / "io"))
    spec = load_spec(SPECS / "swebench-clean-v1.toml")
    assert spec.refs[-2:] == ["v2/MSm", "v2/MSc"] and len(spec.refs) == 19
    run, written = pin(spec, runs_root=tmp_path / "runs")
    assert len(run.cells) == written == 443 * 19
    assert run.cells["cell_id"].map(lambda c: bool(SAFE_ID.match(c))).all()
    crlf = [c for c in run.cells.index[:2000] if b"\r" in run.prompt_path(c).read_bytes()]
    assert crlf and run.prompt(crlf[0])  # prompts with \r read back with their pinned hash
    again, written = pin(spec, runs_root=tmp_path / "runs")
    assert written == 0 and again.manifest == run.manifest


@pytest.mark.skipif(not HAVE_INSTANCES, reason="frozen instances not present")
@pytest.mark.parametrize("name,n", [("tbsci-pl", 70 * 3), ("weirdml-v2-pl", 4 * 3)])
def test_pl_example_specs_plan(name, n):
    spec = load_spec(SPECS / f"{name}.toml")
    try:
        cells, _, _ = plan_cells(spec)
    except SpecError as exc:
        pytest.skip(f"instances not registered here: {exc}")
    assert len(cells) == n and spec.refs == ["v2/PLp", "v2/PLe", "v2/PLs"]


def test_noreason_builder_differs_from_v2_only_in_the_instruction():
    from adele.annotation import prompts
    from adele.mass.spec import BUILDERS, judge_from_dict

    a = prompts.build_annotation_prompt_v2("Planning", "RUBRIC", "TASK")
    b = prompts.build_annotation_prompt_v2_noreason("Planning", "RUBRIC", "TASK")
    diff = [(x, y) for x, y in zip(a.splitlines(), b.splitlines()) if x != y]
    assert len(a.splitlines()) == len(b.splitlines()) and len(diff) == 1
    assert "assessment" in diff[0][0] and "without any assessment" in diff[0][1]
    assert a.rsplit("\n", 1)[1] == b.rsplit("\n", 1)[1]  # same final answer sentence
    assert BUILDERS["v2-noreason"] == "build_annotation_prompt_v2_noreason"
    j = judge_from_dict({"backend": "subagent", "model": "claude-opus-5-5", "effort": "low"}, "v2-noreason")
    assert j.relay["judge_agent"] == "adele-judge-v2-low"
