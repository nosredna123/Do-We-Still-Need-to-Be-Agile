from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "phase2_delta_dt", ROOT / "05_metric_engine.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluator_frame() -> pd.DataFrame:
    rows = []
    for cut, mean, median, iqr, std in (
        ("T1", 2.0, 2.0, 1.0, 0.5),
        ("T2", 2.5, 2.5, 1.5, 0.7),
        ("T3", 3.0, 3.0, 2.0, 0.9),
    ):
        rows.append(
            {
                "ID_Equipe": "TEAM_1",
                "Semestre": "2025.2",
                "temporal_marker": cut,
                "technical_complexity_mean": mean,
                "technical_complexity_median": median,
                "technical_complexity_iqr": iqr,
                "technical_complexity_std": std,
                "technical_complexity_n": 4,
            }
        )
    return pd.DataFrame(rows)


def test_compute_delta_dt_preserves_distribution_and_deltas() -> None:
    engine = load_engine()

    result = engine.compute_delta_dt(evaluator_frame())
    row = result.iloc[0]

    assert len(result) == 1
    assert row["technical_complexity_mean_t1"] == 2.0
    assert row["technical_complexity_median_t2"] == 2.5
    assert row["technical_complexity_iqr_t3"] == 2.0
    assert row["technical_complexity_std_t1"] == 0.5
    assert row["technical_complexity_n_t2"] == 4
    assert row["delta_dt_t1_t2"] == pytest.approx(0.5)
    assert row["delta_dt_t2_t3"] == pytest.approx(0.5)
    assert row["delta_dt_t1_t3"] == pytest.approx(1.0)
    assert bool(row["dt_available"])
    assert row["dt_observation_unit"] == "team_semester"
    assert row["dt_definition_version"] == "dt-v1"


def test_compute_delta_dt_marks_missing_longitudinal_cut() -> None:
    engine = load_engine()
    frame = evaluator_frame().loc[lambda value: value["temporal_marker"] != "T2"]

    result = engine.compute_delta_dt(frame)
    row = result.iloc[0]

    assert not bool(row["dt_available"])
    assert row["dt_unavailable_reason"] == "missing_required_temporal_cut:T2"
    assert pd.isna(row["delta_dt_t1_t3"])


def test_write_technical_degradation_metrics_writes_sidecar_and_refuses_stale(
    tmp_path: Path,
) -> None:
    engine = load_engine()
    result = engine.compute_delta_dt(evaluator_frame())
    output = tmp_path / "technical_degradation_metrics.parquet"

    engine.write_technical_degradation_metrics(
        result,
        output,
        source_checksum="dt-v1-checksum",
        options={"stage": "technical_degradation_metrics"},
    )

    assert output.exists()
    metadata = json.loads(
        output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "technical-degradation-metrics-v1"
    with pytest.raises(ValueError, match="immutable"):
        engine.write_technical_degradation_metrics(
            result,
            output,
            source_checksum="dt-v2-checksum",
            options={},
        )