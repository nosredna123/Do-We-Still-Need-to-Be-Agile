from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.metrics.m4_clean_change_dynamics import generate


def test_m4_real_outputs_use_current_clean_contract() -> None:
    result = generate()
    assert result["status"] in {"generated", "resumed"}
    metrics = Path("paper_v9/data/metrics")
    magnitude = pd.read_csv(metrics / "m4_churn_magnitude.csv")
    intensity = pd.read_csv(metrics / "m4_commit_intensity.csv")
    composition = pd.read_csv(metrics / "m4_artifact_composition.csv")
    rolling = pd.read_csv(metrics / "m4_rolling_7day_trajectory.csv")
    pooled_magnitude = pd.read_csv(metrics / "m4_churn_magnitude_pooled.csv")
    pooled_intensity = pd.read_csv(metrics / "m4_commit_intensity_pooled.csv")
    pooled_composition = pd.read_csv(metrics / "m4_artifact_composition_pooled.csv")
    pooled_rolling = pd.read_csv(metrics / "m4_rolling_7day_trajectory_pooled.csv")
    assert len(magnitude) == 42
    assert len(intensity) == 42
    assert len(rolling) == 994
    assert len(pooled_magnitude) == 3
    assert len(pooled_intensity) == 3
    assert len(pooled_rolling) == 71
    assert "Semestre" not in pooled_magnitude.columns
    assert "Semestre" not in pooled_rolling.columns
    assert set(pooled_composition["temporal_marker"]) == {"T1", "T2", "T3"}
    assert magnitude["clean_churn"].ge(0).all()
    assert composition["churn_lines"].ge(0).all()
    assert rolling["clean_churn_7d"].ge(0).all()
    assert set(composition["file_category"]) <= {"clean_source_or_test", "excluded_or_non_measurement"}
    metadata = json.loads((metrics / "m4_clean_change_dynamics.metadata.json").read_text())
    assert metadata["status"] == "success"
    assert metadata["policy_version"] == "code-churn-metrics-v2"
    assert metadata["rq"] == "RQ2"
