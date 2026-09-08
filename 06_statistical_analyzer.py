"""Declared, non-causal statistical analyses for Phase 2."""

from __future__ import annotations

from typing import Any

import pandas as pd
from scipy.stats import spearmanr


def run_declared_correlations(frame: pd.DataFrame, registry: list[dict[str, Any]]) -> pd.DataFrame:
    """Run only explicitly registered Spearman correlations."""
    rows: list[dict[str, Any]] = []
    for analysis in registry:
        x_name = analysis["x"]
        y_name = analysis["y"]
        missing = {name for name in (x_name, y_name) if name not in frame.columns}
        if missing:
            raise ValueError(f"Correlation {analysis['analysis_id']} has missing columns: {sorted(missing)}")
        values = frame[[x_name, y_name]].dropna()
        row = {"analysis_id": analysis["analysis_id"], "unit_of_analysis": analysis["unit_of_analysis"], "x": x_name, "y": y_name, "n": int(len(values))}
        if len(values) < 3:
            row.update({"status": "unavailable", "reason": "insufficient_n", "coefficient": None, "p_value": None})
        elif values[x_name].nunique() < 2 or values[y_name].nunique() < 2:
            row.update({"status": "unavailable", "reason": "zero_variance", "coefficient": None, "p_value": None})
        else:
            coefficient, p_value = spearmanr(values[x_name], values[y_name])
            row.update({"status": "success", "reason": None, "coefficient": float(coefficient), "p_value": float(p_value)})
        rows.append(row)
    return pd.DataFrame(rows)


def build_statistical_manifest(team_metrics: pd.DataFrame, context_metrics: pd.DataFrame) -> dict[str, Any]:
    """Describe available analytical columns without including raw text."""
    return {
        "status": "success",
        "manifest_version": "phase2-statistics-v1",
        "datasets": [
            {"name": "team_metrics", "unit_of_analysis": "team_semester", "n": int(len(team_metrics)), "variables": sorted(str(column) for column in team_metrics.columns)},
            {"name": "cut_context_metrics", "unit_of_analysis": "cut_context", "n": int(len(context_metrics)), "variables": sorted(str(column) for column in context_metrics.columns)},
        ],
        "pii_status": "text_fields_excluded",
    }