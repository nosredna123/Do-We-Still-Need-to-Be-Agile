"""Descriptive statistics helpers for Paper V9 metrics.

Exploratory summaries only: no causal inference, no hidden imputation.
Fails fast on empty or non-numeric input rather than returning partial or
default-filled results.
"""

from __future__ import annotations

import statistics
from typing import Iterable, Sequence


def descriptive_summary(values: Iterable[float]) -> dict[str, float | int]:
    """Return mean/median/std/min/max/percentiles/n for ``values``.

    Raises:
        ValueError: If ``values`` is empty or contains non-numeric items.
    """
    data: Sequence[float] = list(values)
    if not data:
        raise ValueError("descriptive_summary requires at least one value")
    for item in data:
        if isinstance(item, bool) or not isinstance(item, (int, float)):
            raise ValueError(f"descriptive_summary received a non-numeric value: {item!r}")

    sorted_data = sorted(data)
    summary: dict[str, float | int] = {
        "n": len(data),
        "mean": statistics.fmean(data),
        "median": statistics.median(data),
        "min": sorted_data[0],
        "max": sorted_data[-1],
        "std": statistics.stdev(data) if len(data) > 1 else 0.0,
    }
    if len(data) >= 4:
        quartiles = statistics.quantiles(data, n=4)
        summary["p25"] = quartiles[0]
        summary["p50"] = quartiles[1]
        summary["p75"] = quartiles[2]
    return summary
