"""
CLI entry point for the adele command.

Usage:
    adele annotate <dataset> [options]
    adele evaluate <model> <dataset> [options]
    adele profile <annotations_csv> [options]
    adele rubrics list
    adele benchmarks list
"""

import logging
import click


@click.group()
@click.version_option(package_name="adele")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging.")
def main(verbose):
    """ADeLe — AI Evaluation with Explanatory and Predictive Power.

    A unified toolkit for demand-level annotation, model evaluation,
    and ability profiling of AI systems.
    """
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
@click.option("--output-dir", "-o", default="./adele_annotations", help="Output directory.")
@click.option("--format", "fmt", type=click.Choice(["wide", "long"]), default="wide")
def annotate(dataset, demands, model, backend, split, max_samples, output_dir, fmt):
    """Annotate demand levels for a benchmark dataset.

    DATASET can be a registered benchmark name (e.g. 'mmlu-pro') or a
    HuggingFace dataset ID (e.g. 'cais/mmlu').
    """
    from adele.data import load_benchmark
    from adele.annotation import annotate as run_annotate

    click.echo(f"Loading benchmark: {dataset}")
    kwargs = {}
    if split:
        kwargs["split"] = split
    if max_samples:
        kwargs["max_samples"] = max_samples

    data = load_benchmark(dataset, **kwargs)
    click.echo(f"Loaded {len(data)} instances.")

    demand_list = list(demands) if demands else None

    backend_label = backend or "auto"
    click.echo(f"Starting annotation with {model} (backend={backend_label})...")
    result = run_annotate(
        data=data,
        demands=demand_list,
        model=model,
        backend=backend,
        output_dir=output_dir,
        format=fmt,
    )
    click.echo(f"Annotation complete! {len(result)} results saved to {output_dir}")


# =========================================================================
# Evaluate
# =========================================================================

@main.command()
@click.argument("model_id")
@click.argument("dataset")
@click.option("--split", "-s", default=None, help="Dataset split.")
@click.option("--max-samples", "-n", type=int, default=None, help="Max samples.")
@click.option("--task-type", type=click.Choice(["open-ended", "multiple-choice"]),
              default="open-ended")
@click.option("--output-dir", "-o", default="./adele_results", help="Output directory.")
def evaluate(model_id, dataset, split, max_samples, task_type, output_dir):
    """Evaluate a model on a benchmark using Inspect AI.

    MODEL_ID is the model identifier (e.g. 'openai/gpt-4o').
    DATASET is a benchmark name or HuggingFace dataset ID.
    """
    from adele.data import load_benchmark
    from adele.evaluation import evaluate_model
    import os

    click.echo(f"Loading benchmark: {dataset}")
    kwargs = {}
    if split:
        kwargs["split"] = split
    if max_samples:
        kwargs["max_samples"] = max_samples

    data = load_benchmark(dataset, **kwargs)
    click.echo(f"Loaded {len(data)} instances.")

    click.echo(f"Evaluating {model_id}...")
    results = evaluate_model(
        model=model_id,
        data=data,
        task_type=task_type,
        max_samples=max_samples,
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
    from adele.analysis.demand import plot_from_csv

    click.echo(f"Generating demand profile from {annotations_csv}...")
    fig = plot_from_csv(
        annotations_csv,
        base_color=color,
        save_path=output,
    )
    click.echo(f"Demand profile saved!")
