"""Composite-key and temporal-checkpoint validation for Paper V9 lake datasets.

Fails fast: raises immediately when a required column is missing, a dataset
is empty, or a code-churn contract uses an outdated version. Never silently
skips a team-semester or checkpoint gap — gaps are reported explicitly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd

from paper_v9.scripts.common.artifact_policy import CURRENT_POLICY_VERSION

# Lake datasets expected to carry the (ID_Equipe, Semestre) composite key.
TEAM_SEMESTER_DATASETS: tuple[str, ...] = (
    "git_team_cuts",
    "evaluator_team_cuts",
    "git_commits",
    "git_files",
    "git_repository_snapshots",
)
REQUIRED_TEMPORAL_MARKERS: tuple[str, ...] = ("T1", "T2", "T3")
EXPECTED_CC_DEFINITION_VERSION = "cc-v2-clean-paths"


def load_team_semester_keys(parquet_path: Path) -> set[tuple[str, str]]:
    """Return the distinct (ID_Equipe, Semestre) pairs found in ``parquet_path``.

    Raises:
        FileNotFoundError: If the parquet file does not exist.
        ValueError: If the required key columns are missing or the file is empty.
    """
    if not parquet_path.is_file():
        raise FileNotFoundError(f"Lake dataset not found: {parquet_path}")

    frame = pd.read_parquet(parquet_path)
    missing_columns = {"ID_Equipe", "Semestre"} - set(frame.columns)
    if missing_columns:
        raise ValueError(f"{parquet_path.name} is missing required columns: {sorted(missing_columns)}")
    if frame.empty:
        raise ValueError(f"{parquet_path.name} has zero rows; cannot validate team-semester keys")

    return {(str(row.ID_Equipe), str(row.Semestre)) for row in frame.itertuples(index=False)}


def reference_team_semester_keys(lake_dir: Path) -> set[tuple[str, str]]:
    """Return the canonical set of observed team-semesters from repository snapshots."""
    return load_team_semester_keys(lake_dir / "git_repository_snapshots.parquet")


def validate_team_semester_keys(
    lake_dir: Path,
    dataset_names: Sequence[str] = TEAM_SEMESTER_DATASETS,
) -> dict[str, Any]:
    """Cross-validate composite keys across all team-semester lake datasets.

    Returns a report with the reference key set and, per dataset, any keys
    that are missing from or extra relative to the reference set. Never
    associates a team-semester implicitly: every key must be observed in
    ``git_repository_snapshots`` to be considered valid.
    """
    reference_keys = reference_team_semester_keys(lake_dir)
    report: dict[str, Any] = {
        "reference_dataset": "git_repository_snapshots",
        "reference_key_count": len(reference_keys),
        "reference_keys": sorted(reference_keys),
        "datasets": {},
    }
    for name in dataset_names:
        keys = load_team_semester_keys(lake_dir / f"{name}.parquet")
        report["datasets"][name] = {
            "key_count": len(keys),
            "missing_from_reference": sorted(keys - reference_keys),
            "missing_from_dataset": sorted(reference_keys - keys),
        }
    return report


def checkpoint_coverage_report(lake_dir: Path, dataset_name: str = "git_team_cuts") -> dict[str, Any]:
    """Report which (ID_Equipe, Semestre, temporal_marker) combinations are absent.

    The full expectation is the cartesian product of every reference
    team-semester with T1/T2/T3; any missing combination is listed instead of
    being silently treated as zero.
    """
    parquet_path = lake_dir / f"{dataset_name}.parquet"
    if not parquet_path.is_file():
        raise FileNotFoundError(f"Lake dataset not found: {parquet_path}")

    frame = pd.read_parquet(parquet_path)
    missing_columns = {"ID_Equipe", "Semestre", "temporal_marker"} - set(frame.columns)
    if missing_columns:
        raise ValueError(f"{parquet_path.name} is missing required columns: {sorted(missing_columns)}")

    observed = {
        (str(row.ID_Equipe), str(row.Semestre), str(row.temporal_marker))
        for row in frame.itertuples(index=False)
    }
    reference_keys = reference_team_semester_keys(lake_dir)
    expected = {
        (team, semester, marker)
        for (team, semester) in reference_keys
        for marker in REQUIRED_TEMPORAL_MARKERS
    }
    return {
        "dataset": dataset_name,
        "expected_combinations": len(expected),
        "observed_combinations": len(observed & expected),
        "missing_combinations": sorted(expected - observed),
    }


def assert_current_code_churn_contract(metadata: Mapping[str, Any]) -> None:
    """Fail fast if ``metadata`` does not use the current code-churn contract.

    Args:
        metadata: Parsed ``*.metadata.json`` sidecar for an M4/M8 artifact.

    Raises:
        ValueError: If the contract or clean-path definition version is stale
            or absent.
    """
    contract_version = metadata.get("contract_version")
    options = metadata.get("options", {})
    cc_definition_version = options.get("cc_definition_version")

    if contract_version != CURRENT_POLICY_VERSION:
        raise ValueError(
            f"Stale or missing code-churn contract_version: {contract_version!r}. "
            f"Expected {CURRENT_POLICY_VERSION!r}."
        )
    if cc_definition_version != EXPECTED_CC_DEFINITION_VERSION:
        raise ValueError(
            f"Stale or missing cc_definition_version: {cc_definition_version!r}. "
            f"Expected {EXPECTED_CC_DEFINITION_VERSION!r}."
        )


def _main() -> int:
    from paper_v9.scripts.common.paths import REPO_ROOT

    lake_dir = REPO_ROOT / "data" / "lake"
    report = {
        "team_semester_keys": validate_team_semester_keys(lake_dir),
        "checkpoint_coverage": checkpoint_coverage_report(lake_dir),
    }
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
