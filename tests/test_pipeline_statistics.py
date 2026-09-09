from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_statistics():
    spec = importlib.util.spec_from_file_location(
        "pipeline_statistics_test", ROOT / "pipeline_statistics.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_summarize_numeric_distribution_reports_shape_and_sample_dispersion() -> None:
    statistics = load_statistics()

    result = statistics.summarize_numeric_distribution(
        pd.Series([0, 0, 4, 4, None]),
        scale_type="ordinal",
        scale_version="v1",
    )

    assert result["n_total"] == 5
    assert result["n_valid"] == 4
    assert result["n_missing"] == 1
    assert result["mean"] == 2.0
    assert result["std"] == pytest.approx(2.3094010768)
    assert result["median"] == 2.0
    assert result["q1"] == 0.0
    assert result["q3"] == 4.0
    assert result["iqr"] == 4.0
    assert result["mode"] == 0
    assert result["mode_n"] == 2
    assert result["mode_share"] == 0.5
    assert result["scale_type"] == "ordinal"
    assert result["scale_version"] == "v1"


def test_summarize_numeric_distribution_returns_null_std_for_single_value() -> None:
    statistics = load_statistics()

    result = statistics.summarize_numeric_distribution(
        pd.Series([3, None]),
        scale_type="ordinal",
        scale_version="v1",
    )

    assert result["n_valid"] == 1
    assert result["std"] is None
    assert result["mode_share"] == 1.0