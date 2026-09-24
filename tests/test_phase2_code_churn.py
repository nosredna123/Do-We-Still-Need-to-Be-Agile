from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "phase2_code_churn", ROOT / "05_metric_engine.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def commits_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c1", "timestamp": pd.Timestamp("2025-10-18", tz="UTC"), "lines_added": 10, "lines_deleted": 2},
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c2", "timestamp": pd.Timestamp("2025-10-19", tz="UTC"), "lines_added": 4, "lines_deleted": 1},
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c3", "timestamp": pd.Timestamp("2025-10-27", tz="UTC"), "lines_added": 2, "lines_deleted": 0},
        ]
    )


def files_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c1", "timestamp": pd.Timestamp("2025-10-18", tz="UTC"), "file_path": "src/a.py", "file_extension": ".py", "lines_added": 10, "lines_deleted": 2, "is_binary": False},
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c1", "timestamp": pd.Timestamp("2025-10-18", tz="UTC"), "file_path": "assets/logo.png", "file_extension": ".png", "lines_added": None, "lines_deleted": None, "is_binary": True},
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c2", "timestamp": pd.Timestamp("2025-10-19", tz="UTC"), "file_path": "src/b.py", "file_extension": ".py", "lines_added": 4, "lines_deleted": 1, "is_binary": False},
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c2", "timestamp": pd.Timestamp("2025-10-19", tz="UTC"), "file_path": ".history/src/b_20251019.py", "file_extension": ".py", "lines_added": 100, "lines_deleted": 100, "is_binary": False},
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c3", "timestamp": pd.Timestamp("2025-10-27", tz="UTC"), "file_path": "src/c.py", "file_extension": ".py", "lines_added": 2, "lines_deleted": 0, "is_binary": False},
        ]
    )


def snapshots_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "repository": "repo-a", "repo_source_loc": 100, "snapshot_available": True},
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T1", "repository": "repo-b", "repo_source_loc": 50, "snapshot_available": True},
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T2", "repository": "repo-a", "repo_source_loc": 0, "snapshot_available": False},
        ]
    )


def test_compute_code_churn_aggregates_repositories_and_binary_events() -> None:
    engine = load_engine()

    result = engine.compute_code_churn(commits_frame(), files_frame(), snapshots_frame())
    row = result.iloc[0]

    assert row["cc_total_t1"] == 19
    assert row["repo_source_loc_t1"] == 150
    assert row["cc_per_source_loc_t1"] == pytest.approx(19 / 150)
    assert row["cc_binary_file_events_t1"] == 0
    assert row["cc_unique_changed_files_t1"] == 3
    assert row["cc_median_per_commit_t1"] == 5
    assert row["cc_commit_churn_n_valid_t1"] == 3
    assert bool(row["cc_source_loc_available_t1"])


def test_compute_code_churn_calculates_seven_day_peak() -> None:
    engine = load_engine()

    result = engine.compute_code_churn(commits_frame(), files_frame(), snapshots_frame())

    assert result.loc[0, "cc_peak_7d"] == 17
    assert result.loc[0, "cc_mean_7d"] == pytest.approx((17 + 5 + 2) / 3)
    assert result.loc[0, "cc_peak_7d_temporal_marker"] == "T1"


def test_compute_code_churn_marks_unavailable_snapshot_and_observed_empty_cut() -> None:
    engine = load_engine()
    commits = commits_frame()
    files = files_frame()
    snapshots = snapshots_frame()
    snapshots = pd.concat(
        [
            snapshots,
            pd.DataFrame([{"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T3", "repository": "repo-a", "repo_source_loc": 120, "snapshot_available": True}]),
        ],
        ignore_index=True,
    )

    result = engine.compute_code_churn(commits, files, snapshots)
    row = result.iloc[0]

    assert pd.isna(row["cc_per_source_loc_t2"])
    assert row["cc_source_loc_unavailable_reason_t2"] == "snapshot_unavailable"
    assert row["cc_total_t2"] == 0
    assert row["cc_activity_status_t2"] == "no_observed_activity"


def test_write_code_churn_metrics_writes_sidecar_and_rejects_stale(tmp_path: Path) -> None:
    engine = load_engine()
    result = engine.compute_code_churn(commits_frame(), files_frame(), snapshots_frame())
    output = tmp_path / "code_churn_metrics.parquet"
    engine.write_code_churn_metrics(
        result,
        output,
        source_checksum="cc-v1",
        options={"stage": "code_churn_metrics"},
    )

    metadata = json.loads(
        output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "code-churn-metrics-v2"
    with pytest.raises(ValueError, match="immutable"):
        engine.write_code_churn_metrics(
            result,
            output,
            source_checksum="cc-v2",
            options={},
        )