"""Combine per-source results frames and build the model × instance matrix."""

from typing import Iterable, Optional

import pandas as pd

from adele.results.schema import validate_results


def concat_results(frames: Iterable[pd.DataFrame]) -> pd.DataFrame:
    """Concatenate schema-valid frames from several sources into one table.

    The same (benchmark, instance_id, model, scaffold) cell may legitimately
    appear via two sources (e.g. Epoch and HELM both ran GPQA); rows are kept
    distinct by ``source`` so disagreement between publishers stays visible.
    """
    frames = [f for f in frames if f is not None and len(f)]
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True, sort=False)
    validate_results(out.drop_duplicates(
        subset=["benchmark", "instance_id", "model", "scaffold", "source"]
    ))
    return out


def success_matrix(
    results: pd.DataFrame,
    *,
    benchmark: Optional[str] = None,
    key_scaffold: bool = True,
) -> pd.DataFrame:
    """Pivot to instances (rows) × model[/scaffold] (columns) of success rates.

    This is the frame demand annotations join onto (rows share the benchmark's
    instance_id space). NaN = that model was not run on that instance.
    """
    df = results if benchmark is None else results[results["benchmark"] == benchmark]
    if len(df) == 0:
        return pd.DataFrame()
    col = (
        (df["model"] + "/" + df["scaffold"]).rename("model_scaffold")
        if key_scaffold else df["model"].rename("model_scaffold")
    )
    tmp = df.assign(model_scaffold=col)
    # A cell reported by several sources: average, weighted by trials.
    tmp["_wins"] = tmp["success"] * tmp["n_trials"]
    agg = tmp.groupby(["benchmark", "instance_id", "model_scaffold"]).agg(
        _wins=("_wins", "sum"), _n=("n_trials", "sum")
    )
    agg["rate"] = agg["_wins"] / agg["_n"]
    return agg["rate"].unstack("model_scaffold")


def coverage_report(results: pd.DataFrame) -> pd.DataFrame:
    """Benchmark × model/scaffold table of instance counts — the map of what
    the public record actually covers (and where the holes are)."""
    if len(results) == 0:
        return pd.DataFrame()
    tmp = results.assign(model_scaffold=results["model"] + "/" + results["scaffold"])
    return (
        tmp.groupby(["benchmark", "model_scaffold"])["instance_id"]
        .nunique()
        .unstack("model_scaffold")
    )
