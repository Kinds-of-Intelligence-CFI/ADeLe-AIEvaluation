"""``adele mass``: plan, pin, run and audit annotation runs (see experiments/benchmarks/mass-annotation/)."""

import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

import click

_EXTRAS = {"anthropic-batch": ("models", "anthropic"), "openai-batch": ("annotate", "openai"),
           "litellm": ("annotate", "litellm")}


def _load(run_ref):
    from adele.mass.pin import load_run
    try:
        return load_run(run_ref)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc))


@contextmanager
def _locked(run_dir):
    """Hold the run's lock for a mutating command; a second command on the same run fails at once."""
    from adele.mass.ledger import RunLocked, run_lock
    try:
        with run_lock(run_dir):
            yield
    except RunLocked as exc:
        raise click.ClickException(str(exc))


def _api_backend(run):
    from adele.cli import _require
    from adele.mass.backends import get_backend

    name = run.judge.backend
    if name == "subagent":
        raise click.ClickException("this run uses Claude Code subagents: use `adele mass next` "
                                   "(see the /annotate skill)")
    if name in _EXTRAS:
        _require(*_EXTRAS[name])
    return get_backend(name)


@click.group()
def mass():
    """Annotation runs over any grid of benchmarks x rubrics, with any judge backend."""


@mass.command("plan")
@click.argument("spec_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--tokens-out", type=int, default=1500, show_default=True,
              help="Assumed output tokens per call, thinking included.")
@click.option("--usd-in", type=float, default=None, help="USD per million input tokens (overrides the table).")
@click.option("--usd-out", type=float, default=None, help="USD per million output tokens.")
def plan(spec_path, tokens_out, usd_in, usd_out):
    """Cells, tokens and rough cost of SPEC_PATH. Writes nothing."""
    from adele.mass.pin import estimate
    from adele.mass.spec import SpecError, load_spec

    try:
        spec = load_spec(spec_path)
        est = estimate(spec, tokens_out=tokens_out, usd_in=usd_in, usd_out=usd_out)
    except SpecError as exc:
        raise click.ClickException(str(exc))
    reps = spec.judge.repeats
    click.echo(f"{spec.name}: {est['cells']} cells = {est['cells'] // (est['rubrics'] * reps)} tasks x "
               f"{est['rubrics']} rubrics x {reps} repeat(s)")
    for b, n in est["by_benchmark"].items():
        click.echo(f"  {b:<28} {n}")
    click.echo(f"input ~{est['tokens_in'] / 1e6:.2f}M tokens, output ~{est['tokens_out'] / 1e6:.2f}M tokens "
               f"(assumed {tokens_out}/call); longest prompt {est['max_prompt_chars']} chars")
    for k, v in est["usd"].items():
        click.echo(f"  {k:<40} " + (f"${v:,.0f}" if v is not None else f"n/a (no price for {spec.judge.model})"))
    click.echo(f"  {'subagent (Claude Code subscription)':<40} ~{est['subagent_weekly_points']:.0f} weekly points "
               "(Opus-low calibration)")
    click.echo(f"judge: {spec.judge.backend} {spec.judge.model} effort={spec.judge.effort}; "
               "retries add calls for rejected answers")


@mass.command("pin")
@click.argument("spec_path", type=click.Path(exists=True, dir_okay=False))
@click.option("--runs-root", type=click.Path(file_okay=False), default=None,
              help="Default: experiments/benchmarks/mass-annotation/runs.")
def pin_cmd(spec_path, runs_root):
    """Freeze SPEC_PATH into a run (cells, hashes, ledger) and write its prompts to $ADELE_JUDGE_IO."""
    from adele.mass.ledger import RunLocked
    from adele.mass.pin import pin
    from adele.mass.spec import SpecError, load_spec

    try:
        run, written = pin(load_spec(spec_path), runs_root=runs_root)
    except (SpecError, RunLocked) as exc:
        raise click.ClickException(str(exc))
    click.echo(f"run {run.name}: {len(run.cells)} cells in {run.dir}; {written} prompt files written to "
               f"{run.io_dir / 'prompts'}")


@mass.command("status")
@click.argument("run_ref")
def status(run_ref):
    """Done / no label / in flight / to do, by benchmark and rubric."""
    from adele.mass.ledger import Ledger
    from collections import Counter

    run = _load(run_ref)
    ledger = Ledger.load(run.dir)
    table = ledger.summary(run.cells, run.judge.retry)
    click.echo(table.to_string())
    click.echo("\ntotal: " + ", ".join(f"{k} {v}" for k, v in table.sum().items()))
    reasons = Counter(r["reason"] for r in ledger.with_status("rejected"))
    if reasons:
        click.echo("rejected attempts: " + ", ".join(f"{k} {v}" for k, v in sorted(reasons.items())))
    handles = sorted({r["handle"] for r in ledger.with_status("submitted")})
    if handles:
        click.echo(f"outstanding handles: {', '.join(handles)}")


@mass.command("next")
@click.argument("run_ref")
@click.option("--max", "max_relays", type=click.IntRange(1, 4), default=4, show_default=True,
              help="Relays to emit (never more than 4 run at once).")
@click.option("--batch-size", type=int, default=None, help="Cells per relay (default: the spec's relay.batch_size).")
def next_cmd(run_ref, max_relays, batch_size):
    """Subagent runs: record and print the next relay messages for judge-dispatcher.

    Refuses while earlier relays are outstanding, when this process's working directory (which the judges
    inherit from the session) is not the expected one, and when the agent files changed since the pin.
    """
    from adele.mass.backends.subagent import SubagentBackend, expected_cwd
    from adele.mass.ledger import Ledger
    from adele.mass.pin import agent_drift
    from adele.mass.runner import submit_next

    run = _load(run_ref)
    if run.judge.backend != "subagent":
        raise click.ClickException(f"this run uses {run.judge.backend}: use `adele mass run`")
    want = expected_cwd(run)
    click.echo(f"cwd: {os.getcwd()} (expected: {want})")
    if Path(os.getcwd()).resolve() != Path(want).resolve():
        raise click.ClickException(f"the session's working directory must be {want}: the judges inherit it")
    drift = agent_drift(run)
    if drift:
        raise click.ClickException(f"agent files changed since the pin: {', '.join(drift)}")
    with _locked(run.dir):
        ledger = Ledger.load(run.dir)
        outstanding = ledger.with_status("submitted")
        if outstanding:
            handles = sorted({r["handle"] for r in outstanding})
            raise click.ClickException(
                f"{len(outstanding)} cells of relays {', '.join(handles)} are still submitted. Wait until those "
                f"relays finish, then run `adele mass collect {run_ref} --transcripts <subagents dir> "
                f"--relays-done` (or `adele mass release` for relays that never started).")
        click.echo(f"agent: {run.judge.relay['dispatcher']} (judge {run.judge.relay['judge_agent']})")

        def show(handle, items):
            click.echo(f"=== {handle} ({len(items)} cells) ===")
            click.echo((run.io_dir / "relays" / f"{handle}.txt").read_text(encoding="utf-8"))
            click.echo("=== end ===")

        sent = submit_next(run, ledger, SubagentBackend(), batch_size=batch_size or run.judge.relay["batch_size"],
                           max_batches=max_relays, on_sent=show)
    if not sent:
        click.echo("nothing to submit")


@mass.command("release")
@click.argument("run_ref")
@click.argument("handles", nargs=-1)
@click.option("--all", "release_all", is_flag=True, help="Release every outstanding handle.")
def release_cmd(run_ref, handles, release_all):
    """Return submitted cells of HANDLES to pending without using up their attempt.

    Only for relays or batches that never reached a judge (e.g. a relay that died before starting, or a
    printed relay that was never launched); a cell whose answer file exists is kept for `collect`.
    """
    from adele.mass.ledger import Ledger
    from adele.mass.runner import release

    if bool(handles) == release_all:
        raise click.ClickException("give HANDLE... or --all")
    run = _load(run_ref)
    with _locked(run.dir):
        released, kept = release(run, Ledger.load(run.dir), None if release_all else list(handles))
    click.echo(f"released {len(released)} cells to pending"
               + (f"; kept {len(kept)} with an answer file (collect them)" if kept else ""))


@mass.command("run")
@click.argument("run_ref")
@click.option("--max-cells", type=int, default=None, help="Submit at most this many cells in this invocation.")
@click.option("--batch-size", type=int, default=None,
              help="Cells per batch job (default 1000; 50 for litellm, whose calls run in this process).")
@click.option("--poll-interval", type=int, default=60, show_default=True, help="Seconds between polls.")
@click.option("--once", is_flag=True, help="One submit/poll/fetch pass, then exit (rerun to resume).")
@click.option("--dry-run", is_flag=True, help="Show what would be sent; contact no API.")
def run_cmd(run_ref, max_cells, batch_size, poll_interval, once, dry_run):
    """API backends: submit, poll, fetch and collect until every cell is done (resumable)."""
    from adele.mass.collect import collect
    from adele.mass.ledger import Ledger
    from adele.mass.runner import preview, submit_next

    run = _load(run_ref)
    batch_size = batch_size or (50 if run.judge.backend == "litellm" else 1000)
    if dry_run:
        ledger = Ledger.load(run.dir)
        todo = ledger.to_submit(run.judge.retry)[:max_cells]
        n_out = len(ledger.with_status("submitted"))
        click.echo(f"would submit {len(todo)} cells in {-(-len(todo) // batch_size)} batch(es) with "
                   f"{run.judge.backend} {run.judge.model}; {n_out} cells already in flight")
        if todo:
            click.echo(json.dumps(preview(run, todo[0]), indent=2))
        return
    backend = _api_backend(run)
    remaining = max_cells
    with _locked(run.dir):
        ledger = Ledger.load(run.dir)
        while True:
            sent = submit_next(run, ledger, backend, batch_size=batch_size, max_cells=remaining)
            if remaining is not None:
                remaining -= sum(len(items) for _, items in sent)
            res = collect(run, backend, ledger)
            in_flight = len(ledger.with_status("submitted"))
            click.echo(f"sent {sum(len(i) for _, i in sent)}; fetched {res['fetched']}; labels {res['labels']}, "
                       f"no label {res['no_label']} of {res['cells']}; in flight {in_flight}")
            more = ledger.to_submit(run.judge.retry) and (remaining is None or remaining > 0)
            if once or (not in_flight and not more):
                break
            time.sleep(poll_interval)


@mass.command("collect")
@click.argument("run_ref")
@click.option("--transcripts", type=click.Path(exists=True, file_okay=False), default=None,
              help="Subagent runs: the judging session's subagents folder.")
@click.option("--relays-done", is_flag=True,
              help="Subagent runs: every launched relay has finished, so unanswered cells are settled.")
@click.option("--cwd", default=None, help="Subagent runs: expected judge working directory (default: the spec's).")
def collect_cmd(run_ref, transcripts, relays_done, cwd):
    """Fetch finished answers, judge them (protocol, writer rule, parse) and write labels.csv."""
    from adele.mass.backends.subagent import SubagentBackend
    from adele.mass.collect import collect
    from adele.mass.ledger import Ledger

    run = _load(run_ref)
    with _locked(run.dir):
        ledger = Ledger.load(run.dir)
        backend = None
        if ledger.with_status("submitted"):
            if run.judge.backend == "subagent":
                if relays_done and not transcripts:
                    raise click.ClickException("--relays-done needs --transcripts to attribute writers")
                backend = SubagentBackend(transcripts=transcripts, relays_done=relays_done, cwd=cwd)
            else:
                backend = _api_backend(run)
        try:
            res = collect(run, backend, ledger)
        except ValueError as exc:
            raise click.ClickException(str(exc))
    click.echo(f"fetched {res['fetched']}; judged {res['judged']}; labels {res['labels']}, "
               f"no label {res['no_label']} of {res['cells']} cells → {run.dir / 'labels.csv'}")


@mass.command("check")
@click.argument("run_ref")
@click.option("--transcripts", type=click.Path(exists=True, file_okay=False), default=None,
              help="Subagent runs: the judging session's subagents folder (enables the protocol checks).")
@click.option("--cwd", default=None, help="Expected judge working directory (default: the spec's or ~/Developer/ADELE).")
def check_cmd(run_ref, transcripts, cwd):
    """Coverage, answer-file integrity, agent files and (subagent runs) the protocol of every judge transcript."""
    from adele.mass.check import check

    run = _load(run_ref)
    rep = check(run, transcripts, cwd)
    click.echo("coverage: " + ", ".join(f"{k} {v}" for k, v in rep["totals"].items()))
    click.echo(f"rejected attempts: {rep['rejections'] or 'none'}")
    for key, label in (("changed_answers", "answer files changed since recorded"),
                       ("missing_answers", "answer files missing"), ("agent_drift", "agent files changed since pin")):
        if rep[key]:
            click.echo(f"{label}: {rep[key]}")
    p = rep["protocol"]
    if p is not None:
        click.echo(f"protocol: {p['transcripts']} judge transcripts, {len(p['failures'])} failing; models {p['models']}")
        for f in p["failures"]:
            click.echo(f"  {f['cell']}: {'; '.join(f['problems'])} ({f['transcript']})")
        if p["classifier_stops"]:
            click.echo(f"classifier stops: {', '.join(p['classifier_stops'])}")
        if p["called_more_than_once"]:
            click.echo(f"judged more than once: {', '.join(p['called_more_than_once'])}")
    if not rep["ok"]:
        raise click.ClickException("check failed")
    click.echo("check OK")
