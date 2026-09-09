"""Shared descriptive-statistics primitives for the research pipeline."""

from __future__ import annotations

from typing import Any

import pandas as pd


def summarize_numeric_distribution(
    values: pd.Series,
    *,
    scale_type: str,
    scale_version: str,
    mode_order: dict[Any, int] | None = None,
) -> dict[str, Any]:
    """Summarize one numeric distribution with explicit missingness metadata.

    Args:
        values: Values in one declared analytical distribution.
        scale_type: Declared scale kind, such as ``ordinal``.
        scale_version: Version of the source score scale.
        mode_order: Optional deterministic ordering used to break mode ties.

    Returns:
        A flat mapping suitable for adding to an analytical DataFrame row.
    """
    n_total = int(len(values))
    valid = values.dropna()
    n_valid = int(len(valid))
    n_missing = n_total - n_valid
    if n_valid == 0:
        return {
            "n_total": n_total,
            "n_valid": 0,
            "n_missing": n_missing,
            "mean": None,
            "std": None,
            "median": None,
            "q1": None,
            "q3": None,
            "iqr": None,
            "mode": None,
            "mode_n": None,
            "mode_share": None,
            "scale_type": scale_type,
            "scale_version": scale_version,
            "std_ddof": 1,
            "quantile_method": "linear",
        }

    counts = valid.value_counts()
    mode = max(
        counts.index,
        key=lambda value: (
            int(counts[value]),
            mode_order.get(value, 0) if mode_order is not None else 0,
        ),
    )
    q1 = float(valid.quantile(0.25, interpolation="linear"))
    q3 = float(valid.quantile(0.75, interpolation="linear"))
    return {
        "n_total": n_total,
        "n_valid": n_valid,
        "n_missing": n_missing,
        "mean": float(valid.mean()),
        "std": float(valid.std(ddof=1)) if n_valid > 1 else None,
        "median": float(valid.median()),
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "mode": mode.item() if hasattr(mode, "item") else mode,
        "mode_n": int(counts[mode]),
        "mode_share": float(counts[mode] / n_valid),
        "scale_type": scale_type,
        "scale_version": scale_version,
        "std_ddof": 1,
        "quantile_method": "linear",
    }


def flatten_distribution_summary(
    summary: dict[str, Any],
    prefix: str,
) -> dict[str, Any]:
    """Prefix a distribution summary for wide analytical output."""
    return {f"{prefix}_{key}": value for key, value in summary.items()}