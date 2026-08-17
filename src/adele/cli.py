"""
CLI entry point for the adele command.

Usage:
    adele annotate <dataset> [options]
    adele evaluate <model> <dataset> [options]
    adele profile <annotations_csv> [options]
    adele rubrics list
    adele benchmarks list
"""

import importlib
import logging
import click


def _require(extra: str, *modules: str) -> None:
    """Fail with an actionable message when an optional extra is missing.

    Each workflow command imports heavy dependencies lazily; without this
    guard a missing extra surfaces as a raw ``ModuleNotFoundError`` traceback.
    """
    missing = []
    for m in modules:
        try:
            importlib.import_module(m)
        except ImportError:
            missing.append(m)
    if missing:
        raise click.ClickException(
            f"this command needs the '{extra}' extra "
            f"(missing: {', '.join(missing)}). Install it with:\n"
            f'  pip install "adele[{extra}]"'
        )


@click.group()
@click.version_option(package_name="adele")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
def main(verbose):
    """ADeLe — AI Evaluation with Explanatory and Predictive Power.

    A unified toolkit for demand-level annotation, model evaluation,
    and ability profiling of AI systems.
    """
    # Load API keys and tokens from a local .env, matching Inspect's own
    # behaviour, so `adele annotate/evaluate` and `inspect eval` see the
    # same environment.
    from dotenv import load_dotenv
    load_dotenv()

    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )


# =========================================================================
# Rubrics
# =========================================================================

@main.group()
def rubrics():
    """Manage demand-level rubrics."""
    pass


@rubrics.command("list")
def rubrics_list():
    """List all available rubrics."""
    from adele.rubrics import RubricsCatalog

    catalog = RubricsCatalog()
    click.echo(f"\n{'Acronym':<12} Full Name")
    click.echo("-" * 50)
    for rubric in catalog:
        click.echo(f"  {rubric.acronym:<10} {rubric.full_name}")
    click.echo(f"\n{len(catalog)} rubrics loaded.\n")


# =========================================================================
# Benchmarks
# =========================================================================

@main.group()
def benchmarks():
    """Manage benchmark datasets."""
    pass


@benchmarks.command("list")
def benchmarks_list():
    """List all pre-configured benchmarks."""
    from adele.data.registry import list_benchmarks

    bms = list_benchmarks()
    click.echo(f"\n{'Name':<20} {'HuggingFace ID':<35} Description")
    click.echo("-" * 80)
    for b in bms:
        click.echo(f"  {b.name:<18} {b.hf_dataset_id:<33} {b.description}")
    click.echo(f"\n{len(bms)} benchmarks registered.\n")


# =========================================================================
# Annotate
# =========================================================================

@main.command()
@click.argument("dataset")
@click.option("--demands", "-d", multiple=True, help="Rubric acronyms to annotate.")
@click.option("--model", "-m", default="gpt-4o", help="Model for annotation (e.g. gpt-4o, gemini/gemini-2.0-flash, claude-sonnet-4-20250514).")
@click.option("--backend", type=click.Choice(["batch", "direct"]), default=None,
              help="Annotation backend. Auto-detected if not set.")
@click.option("--split", "-s", default=None, help="Dataset split (default: test).")
@click.option("--max-samples", "-n", type=int, default=None, help="Max samples to annotate.")
@click.option("--max-completion-tokens", type=int, default=1000, help="Max tokens per annotation response.")
@click.option("--hf-token", default=None, help="HuggingFace token for gated datasets (default: HF_TOKEN env).")
@click.option("--output-dir", "-o", default="./adele_annotations", help="Output directory.")
@click.option("--format", "fmt", type=click.Choice(["wide", "long"]), default="wide")
@click.option("--rubrics", "rubrics_folder", default=None,
              help="Folder of custom rubric .txt files (default: bundled v1.0 rubrics).")
def annotate(dataset, demands, model, backend, split, max_samples,
             max_completion_tokens, hf_token, output_dir, fmt, rubrics_folder):
    """Annotate demand levels for a benchmark dataset.

    DATASET can be a registered benchmark name (e.g. 'mmlu-pro') or a
    HuggingFace dataset ID (e.g. 'cais/mmlu').
    """
    _require("annotate", "litellm", "openai", "tenacity", "datasets")
    from adele.data import load_benchmark
    from adele.annotation import annotate as run_annotate

    click.echo(f"Loading benchmark: {dataset}")
    kwargs = {}
    if split:
        kwargs["split"] = split
    if max_samples:
        kwargs["max_samples"] = max_samples
    if hf_token:
        kwargs["hf_token"] = hf_token

    data = load_benchmark(dataset, **kwargs)
    click.echo(f"Loaded {len(data)} instances.")

    demand_list = list(demands) if demands else None

    backend_label = backend or "auto"
    click.echo(f"Starting annotation with {model} (backend={backend_label})...")
    result = run_annotate(
        data=data,
        demands=demand_list,
        rubrics_folder=rubrics_folder,
        model=model,
        backend=backend,
        max_completion_tokens=max_completion_tokens,
        output_dir=output_dir,
        format=fmt,
    )
    click.echo(f"Annotation complete! {len(result)} results saved to {output_dir}")


# =========================================================================
# Agentic (v2 rubric library + whole-task rubric validation)
# =========================================================================

@main.group()
def agentic():
    """v2 agentic rubrics and whole-task rubric validation."""
    pass


@agentic.command("rubrics")
def agentic_rubrics():
    """List the active v2 agentic rubric set and its sources."""
    from adele.agentic import read_manifest, verify_manifest

    entries = read_manifest()
    click.echo(f"\n{'Code':<6}{'Source':<8}{'Full name':<46}Doc heading")
    click.echo("-" * 96)
    for e in entries:
        click.echo(f"  {e.code:<6}{e.source:<8}{e.full_name:<44}{e.source_heading}")
    problems = verify_manifest()
    click.echo(f"\n{len(entries)} active rubrics."
               + (" Manifest OK.\n" if not problems else f" DRIFT: {problems}\n"))


@agentic.command("template")
@click.argument("tasks")
@click.option("--output", "-o", default="human_template.csv", help="Output CSV path.")
def agentic_template(tasks, output):
    """Emit a blank human-annotation sheet for TASKS (a .csv/.jsonl of whole tasks)."""
    from adele.agentic import active_demands
    from adele.agentic.hal import load_tasks, human_label_template

    frame = load_tasks(tasks)
    sheet = human_label_template(frame, active_demands())
    sheet.to_csv(output, index=False)
    click.echo(f"Wrote {len(sheet)} rows × {len(active_demands())} demands to {output}")


@agentic.command("pilot")
@click.option("--benchmarks", "-b", multiple=True,
              default=("swebench", "assistantbench", "usaco", "taubench"),
              help="Benchmarks to sample (default: the 4-benchmark pilot set).")
@click.option("--n-per", "-n", type=int, default=5, help="Tasks per benchmark.")
@click.option("--seed", type=int, default=0, help="Random seed (reproducible).")
@click.option("--output-dir", "-o", default="./pilot", help="Output directory.")
def agentic_pilot(benchmarks, n_per, seed, output_dir):
    """Sample whole tasks across benchmarks → tasks.csv + a blank human sheet.

    Downloads task inputs (not rollouts) from HuggingFace; no LLM calls.
    """
    _require("agentic", "datasets", "huggingface_hub")
    import os
    from adele.agentic import active_demands
    from adele.agentic.benchmarks import sample_pilot
    from adele.agentic.hal import human_label_template

    click.echo(f"Sampling {n_per} tasks each from: {', '.join(benchmarks)} (seed={seed})")
    tasks = sample_pilot(list(benchmarks), n_per=n_per, seed=seed)
    os.makedirs(output_dir, exist_ok=True)
    tasks_path = os.path.join(output_dir, "tasks.csv")
    template_path = os.path.join(output_dir, "human_template.csv")
    tasks.to_csv(tasks_path, index=False)
    human_label_template(tasks, active_demands()).to_csv(template_path, index=False)
    click.echo(f"Wrote {len(tasks)} tasks to {tasks_path}")
    click.echo(f"Blank annotation sheet ({len(active_demands())} demands) → {template_path}")
    click.echo("\nPer benchmark:\n" + tasks["benchmark"].value_counts().to_string())


@agentic.command("validate")
@click.argument("judge_csv")
@click.argument("human_csv")
def agentic_validate(judge_csv, human_csv):
    """Report judge-vs-human agreement from two wide label CSVs (custom_id + demands)."""
    _require("agentic", "numpy", "scipy", "sklearn")
    import pandas as pd
    from adele.agentic.validation import rubric_agreement

    report = rubric_agreement(pd.read_csv(judge_csv), pd.read_csv(human_csv))
    if not report.dimensions:
        click.echo("No overlapping demand columns / instances to compare.")
        return
    click.echo("\n" + str(report) + "\n")


# =========================================================================
# Results (public per-instance success/failure matrix)
# =========================================================================

@main.group()
def results():
    """Fetch and join public per-instance model results."""
    pass


@results.command("fetch-swebench")
@click.argument("experiments_dir")
@click.option("--split", default="verified", help="Leaderboard split (default: verified).")
@click.option("--output", "-o", default="swebench_results.parquet")
def results_swebench(experiments_dir, split, output):
    """Per-instance resolution flags from a SWE-bench/experiments checkout."""
    from adele.results.sources import swebench

    df = swebench.fetch(experiments_dir, split=split)
    df.to_parquet(output)
    click.echo(f"{len(df)} rows ({df['instance_id'].nunique()} instances × "
               f"{df.groupby(['model', 'scaffold']).ngroups} model/scaffold pairs) → {output}")


@results.command("fetch-matharena")
@click.option("--dataset", default="MathArena/aime_2026_outputs", show_default=True)
@click.option("--local-path", default=None, help="Local parquet copy (skips the Hub).")
@click.option("--output", "-o", default="matharena_results.parquet")
def results_matharena(dataset, local_path, output):
    """Per-problem correctness from MathArena output dumps."""
    _require("annotate", "datasets") if not local_path else None
    from adele.results.sources import matharena

    df = matharena.fetch(dataset, local_path=local_path)
    df.to_parquet(output)
    click.echo(f"{len(df)} rows → {output}")


@results.command("fetch-arcprize")
@click.argument("slugs", nargs=-1, required=True)
@click.option("--benchmark", default="arc-agi-2", show_default=True)
@click.option("--output", "-o", default="arcprize_results.parquet")
def results_arcprize(slugs, benchmark, output):
    """Scrape per-task results pages (e.g. anthropic-claude-opus-5)."""
    from adele.results.sources import arcprize

    df = arcprize.fetch(slugs, benchmark=benchmark)
    df.to_parquet(output)
    click.echo(f"{len(df)} rows from {len(slugs)} model pages → {output}")


@results.command("ingest-scores")
@click.argument("csv_path")
@click.option("--scaffold", default="none", show_default=True)
@click.option("--source", default="partner-extract", show_default=True)
@click.option("--output", "-o", default="ingested_results.parquet")
def results_ingest(csv_path, scaffold, source, output):
    """Ingest a partner CSV made by scripts/extract_scores_standalone.py."""
    from adele.results.sources import inspect_scores

    df = inspect_scores.from_csv(csv_path, scaffold=scaffold, source=source)
    df.to_parquet(output)
    click.echo(f"{len(df)} rows → {output}")


@results.command("join")
@click.argument("parquets", nargs=-1, required=True)
@click.option("--output", "-o", default="results_matrix.parquet")
def results_join(parquets, output):
    """Concatenate fetched frames and report coverage."""
    import pandas as pd
    from adele.results import concat_results
    from adele.results.join import coverage_report

    df = concat_results([pd.read_parquet(p) for p in parquets])
    df.to_parquet(output)
    click.echo(f"{len(df)} rows → {output}\n\nCoverage (instances per benchmark × model/scaffold):")
    click.echo(coverage_report(df).to_string())


# =========================================================================
# Evaluate
# =========================================================================

@main.command()
@click.argument("model_id")
@click.argument("dataset")
@click.option("--split", "-s", default=None, help="Dataset split.")
@click.option("--max-samples", "-n", type=int, default=None, help="Max samples.")
@click.option("--task-type", type=click.Choice(["auto", "open-ended", "multiple-choice"]),
              default="auto",
              help="Scoring mode. 'auto' (default) infers from the data: "
                   "multiple-choice when the benchmark provides options, "
                   "open-ended (exact match) otherwise.")
@click.option("--hf-token", default=None, help="HuggingFace token for gated datasets (default: HF_TOKEN env).")
@click.option("--output-dir", "-o", default="./adele_results", help="Output directory.")
def evaluate(model_id, dataset, split, max_samples, task_type, hf_token, output_dir):
    """Evaluate a model on a benchmark using Inspect AI.

    MODEL_ID is the model identifier (e.g. 'openai/gpt-4o').
    DATASET is a benchmark name or HuggingFace dataset ID.
    """
    _require("eval", "inspect_ai", "datasets")
    from adele.data import load_benchmark
    from adele.evaluation import evaluate_model
    import os

    click.echo(f"Loading benchmark: {dataset}")
    kwargs = {}
    if split:
        kwargs["split"] = split
    if max_samples:
        kwargs["max_samples"] = max_samples
    if hf_token:
        kwargs["hf_token"] = hf_token

    data = load_benchmark(dataset, **kwargs)
    click.echo(f"Loaded {len(data)} instances.")

    if task_type == "auto":
        has_choices = "choices" in data.columns and data["choices"].notna().any()
        task_type = "multiple-choice" if has_choices else "open-ended"
        click.echo(f"Inferred task type: {task_type} "
                   f"({'options present' if has_choices else 'no options column'}; "
                   "override with --task-type).")

    click.echo(f"Evaluating {model_id}...")
    # max_samples already applied at load time, so no need to re-pass it.
    results = evaluate_model(
        model=model_id,
        data=data,
        task_type=task_type,
    )

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "evaluation_results.csv")
    results.to_csv(output_path, index=False)
    click.echo(f"Evaluation complete! Results saved to {output_path}")


# =========================================================================
# Profile
# =========================================================================

@main.command()
@click.argument("annotations_csv")
@click.option("--title", "-t", default=None, help="Plot title.")
@click.option("--output", "-o", default=None, help="Output image path.")
@click.option("--color", default="#30638e", help="Base color (hex).")
def profile(annotations_csv, title, output, color):
    """Generate a demand profile plot from annotations.

    ANNOTATIONS_CSV should be a CSV file with a custom_id column and
    demand-level columns (AS, CEc, CEe, ...).
    """
    _require("analysis", "numpy", "matplotlib", "scienceplots")
    from adele.analysis.demand import plot_from_csv

    click.echo(f"Generating demand profile from {annotations_csv}...")
    plot_from_csv(
        annotations_csv,
        base_color=color,
        save_path=output,
        title=title,
    )
    click.echo("Demand profile saved!")
