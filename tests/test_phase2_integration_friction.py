from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "phase2_integration_friction", ROOT / "05_metric_engine.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def commits_frame() -> pd.DataFrame:
    rows = []
    values = [
        ("T1", "2025-12-01T00:00:00Z", "a", 10),
        ("T1", "2025-12-01T01:00:00Z", "a", 5),
        ("T1", "2025-12-01T02:00:00Z", "b", 4),
        ("T3", "2025-12-02T00:00:00Z", "a", 8),
        ("T3", "2025-12-04T00:00:00Z", "b", 6),
    ]
    for index, (cut, timestamp, author, churn) in enumerate(values):
        rows.append(
            {
                "ID_Equipe": "TEAM_1",
                "Semestre": "2025.2",
                "temporal_marker": cut,
                "commit_hash": f"c{index}",
                "timestamp": pd.Timestamp(timestamp),
                "ID_Autor_Local": author,
                "lines_added": churn,
                "lines_deleted": 0,
                "branch_or_ref": "main",
                "branch_or_ref_source": "observed",
            }
        )
    return pd.DataFrame(rows)


def test_compute_integration_friction_calculates_author_concentration_and_gini() -> None:
    engine = load_engine()
    result = engine.compute_integration_friction(
        commits_frame(), {"2025.2": pd.Timestamp("2025-12-05", tz="UTC")}
    )
    row = result.iloc[0]

    assert row["ai_commit_n_t1"] == 3
    assert row["ai_author_n_t1"] == 2
    assert row["ai_max_author_share_t1"] == pytest.approx(2 / 3)
    assert row["ai_author_share_median_t1"] == pytest.approx(0.5)
    assert row["ai_gini_t1"] == pytest.approx(1 / 6)
    assert row["ai_observation_unit"] == "team_semester"
    assert row["ai_definition_version"] == "ai-v1"


def test_compute_integration_friction_uses_configured_72_hour_window() -> None:
    engine = load_engine()
    result = engine.compute_integration_friction(
        commits_frame(), {"2025.2": pd.Timestamp("2025-12-05", tz="UTC")},
        window_hours=72,
    )
    row = result.iloc[0]

    assert row["ai_commit_n_before_t3_window"] == 2
    assert row["ai_churn_before_t3_window"] == 14
    assert row["ai_t3_window_hours"] == 72
    assert row["ai_window_bounds"] == "[t3_start - hours, t3_start)"


def test_compute_integration_friction_marks_missing_ref_without_inference() -> None:
    engine = load_engine()
    commits = commits_frame()
    commits.loc[0, "branch_or_ref"] = None
    result = engine.compute_integration_friction(
        commits, {"2025.2": pd.Timestamp("2025-12-05", tz="UTC")}
    )
    row = result.iloc[0]

    assert not bool(row["ai_ref_available_t1"])
    assert row["ai_ref_unavailable_reason_t1"] == "missing_observed_branch_or_ref"
    assert not bool(row["ai_concentration_available_t1"])
    assert row["ai_max_author_share_t3"] == pytest.approx(0.5)


def test_write_integration_friction_metrics_writes_sidecar_and_rejects_stale(tmp_path: Path) -> None:
    engine = load_engine()
    result = engine.compute_integration_friction(
        commits_frame(), {"2025.2": pd.Timestamp("2025-12-05", tz="UTC")}
    )
    output = tmp_path / "integration_friction_metrics.parquet"
    engine.write_integration_friction_metrics(
        result,
        output,
        source_checksum="ai-v1-checksum",
        options={"stage": "integration_friction_metrics"},
    )

    metadata = json.loads(
        output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "integration-friction-metrics-v1"
    with pytest.raises(ValueError, match="immutable"):
        engine.write_integration_friction_metrics(
            result, output, source_checksum="ai-v2-checksum", options={}
        )