"""Tests for the Task 1.2 input contracts: composite keys, checkpoint
coverage, code-churn contract versioning, and the generated input inventory.

Unit tests use synthetic fixtures for isolated contract logic. The
``test_real_lake_*`` tests are integration checks against the actual
repository data lake, per the plan's requirement to validate with real data.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from paper_v9.scripts.common.paths import REPO_ROOT
from paper_v9.scripts.common.validate_keys import (
    assert_current_code_churn_contract,
    checkpoint_coverage_report,
    load_team_semester_keys,
    reference_team_semester_keys,
    validate_team_semester_keys,
)


def _write_parquet(path: Path, rows: list[dict[str, object]]) -> None:
    pd.DataFrame(rows).to_parquet(path)


def _make_synthetic_lake(tmp_path: Path) -> Path:
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()
    reference_rows = [
        {"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1"},
        {"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T2"},
        {"ID_Equipe": "TEAM_02", "Semestre": "2025.2", "temporal_marker": "T1"},
    ]
    _write_parquet(lake_dir / "git_repository_snapshots.parquet", reference_rows)
    _write_parquet(lake_dir / "git_team_cuts.parquet", reference_rows[:2])
    return lake_dir


def test_load_team_semester_keys_fails_fast_on_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_team_semester_keys(tmp_path / "missing.parquet")


def test_load_team_semester_keys_fails_fast_on_missing_columns(tmp_path: Path) -> None:
    parquet_path = tmp_path / "bad.parquet"
    _write_parquet(parquet_path, [{"Semestre": "2025.2"}])
    with pytest.raises(ValueError, match="missing required columns"):
        load_team_semester_keys(parquet_path)


def test_load_team_semester_keys_fails_fast_on_empty_dataset(tmp_path: Path) -> None:
    parquet_path = tmp_path / "empty.parquet"
    _write_parquet(parquet_path, [{"ID_Equipe": "x", "Semestre": "y"}])
    pd.read_parquet(parquet_path).iloc[0:0].to_parquet(parquet_path)
    with pytest.raises(ValueError, match="zero rows"):
        load_team_semester_keys(parquet_path)


def test_reference_team_semester_keys_matches_git_repository_snapshots(tmp_path: Path) -> None:
    lake_dir = _make_synthetic_lake(tmp_path)
    keys = reference_team_semester_keys(lake_dir)
    assert keys == {("TEAM_01", "2025.2"), ("TEAM_02", "2025.2")}


def test_validate_team_semester_keys_reports_missing_from_dataset(tmp_path: Path) -> None:
    lake_dir = _make_synthetic_lake(tmp_path)
    report = validate_team_semester_keys(lake_dir, dataset_names=("git_team_cuts",))
    assert report["reference_key_count"] == 2
    assert report["datasets"]["git_team_cuts"]["missing_from_dataset"] == [("TEAM_02", "2025.2")]
    assert report["datasets"]["git_team_cuts"]["missing_from_reference"] == []


def test_checkpoint_coverage_report_lists_missing_combinations(tmp_path: Path) -> None:
    lake_dir = _make_synthetic_lake(tmp_path)
    report = checkpoint_coverage_report(lake_dir, dataset_name="git_team_cuts")
    assert report["expected_combinations"] == 6  # 2 teams x 3 markers
    assert report["observed_combinations"] == 2
    assert ("TEAM_01", "2025.2", "T3") in report["missing_combinations"]
    assert ("TEAM_02", "2025.2", "T2") in report["missing_combinations"]


def test_assert_current_code_churn_contract_accepts_current_version() -> None:
    metadata = {
        "contract_version": "code-churn-metrics-v2",
        "options": {"cc_definition_version": "cc-v2-clean-paths"},
    }
    assert_current_code_churn_contract(metadata)  # must not raise


@pytest.mark.parametrize(
    "metadata",
    [
        {"contract_version": "code-churn-metrics-v1", "options": {"cc_definition_version": "cc-v2-clean-paths"}},
        {"contract_version": "code-churn-metrics-v2", "options": {"cc_definition_version": "cc-v1-legacy-paths"}},
        {"options": {"cc_definition_version": "cc-v2-clean-paths"}},
        {},
    ],
)
def test_assert_current_code_churn_contract_rejects_stale_or_missing(metadata: dict) -> None:
    with pytest.raises(ValueError):
        assert_current_code_churn_contract(metadata)


def test_real_lake_has_fourteen_team_semesters() -> None:
    lake_dir = REPO_ROOT / "data" / "lake"
    report = validate_team_semester_keys(lake_dir)
    assert report["reference_key_count"] == 14
    for dataset_report in report["datasets"].values():
        assert dataset_report["missing_from_dataset"] == []
        assert dataset_report["missing_from_reference"] == []


def test_real_code_churn_metrics_use_current_contract() -> None:
    metadata_path = REPO_ROOT / "data" / "analysis" / "code_churn_metrics.parquet.metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert_current_code_churn_contract(metadata)  # must not raise


def test_real_input_inventory_is_well_formed_json() -> None:
    inventory_path = REPO_ROOT / "paper_v9" / "data" / "manifests" / "input_inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))

    assert inventory["team_semester_key_validation"]["reference_key_count"] == 14
    assert inventory["artifact_policy"]["current_policy_version"] == "code-churn-metrics-v2"
    assert inventory["git_parent_mirrors"]["repo_count"] == 14
    for contract in inventory["lake_contracts"].values():
        assert contract["rows"] > 0
