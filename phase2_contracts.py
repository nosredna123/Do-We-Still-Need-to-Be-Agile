"""Validation of the independent Phase 2 input contracts."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from pipeline_core import artifact_metadata_path, file_checksum


CONTRACT_NAMES = (
    "student_responses",
    "evaluator_team_cuts",
    "git_team_cuts",
    "git_commits",
    "git_files",
    "git_repository_snapshots",
    "transcript_sessions",
)
TEMPORAL_MARKERS = {"T1", "T2", "T3"}
TEAM_CUT_KEY = ["ID_Equipe", "Semestre", "temporal_marker"]

MINIMUM_COLUMNS: dict[str, set[str]] = {
    "student_responses": {"Semestre", "temporal_marker", "source_file", "source_type"},
    "evaluator_team_cuts": {"ID_Equipe", "Semestre", "temporal_marker", "technical_complexity_mean"},
    "git_team_cuts": {"ID_Equipe", "Semestre", "temporal_marker", "lines_added", "lines_deleted", "files_changed", "num_authors", "num_commits"},
    "git_commits": {"ID_Equipe", "Semestre", "temporal_marker", "commit_hash", "timestamp", "files_changed", "lines_added", "lines_deleted", "ID_Autor_Local", "branch_or_ref", "branch_or_ref_source"},
    "git_files": {"ID_Equipe", "Semestre", "temporal_marker", "commit_hash", "timestamp", "file_path", "change_status", "is_binary"},
    "git_repository_snapshots": {"ID_Equipe", "Semestre", "temporal_marker", "repository", "snapshot_commit_hash", "snapshot_timestamp", "snapshot_available", "repo_source_loc"},
    "transcript_sessions": {"session_id", "transcript_file", "Semestre", "temporal_marker", "temporal_marker_source", "transcript_text"},
}


@dataclass(frozen=True)
class Phase2Inputs:
    """DataFrames loaded from the seven independent lake contracts."""

    lake_dir: Path
    frames: dict[str, pd.DataFrame]
    checksums: dict[str, str]

    def __getitem__(self, name: str) -> pd.DataFrame:
        """Return a contract DataFrame by its canonical name."""
        return self.frames[name]


def _contract_path(lake_dir: Path, name: str) -> Path:
    return lake_dir / f"{name}.parquet"


def _validate_sidecar(path: Path) -> dict[str, Any]:
    sidecar_path = artifact_metadata_path(path)
    if not sidecar_path.exists():
        raise FileNotFoundError(f"Missing sidecar for {path.name}")
    try:
        metadata = json.loads(sidecar_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid sidecar for {path.name}") from error
    if metadata.get("status") != "success":
        raise ValueError(f"Invalid sidecar status for {path.name}")
    return metadata


def _validate_schema(name: str, frame: pd.DataFrame) -> None:
    missing = sorted(MINIMUM_COLUMNS[name] - set(frame.columns))
    if missing:
        raise ValueError(f"{name} schema missing columns: {missing}")


def load_phase2_inputs(lake_dir: Path) -> Phase2Inputs:
    """Load and minimally validate all Phase 2 lake contracts.

    Args:
        lake_dir: Directory containing the seven canonical Parquet contracts.

    Returns:
        Loaded, schema-checked contract DataFrames and their checksums.

    Raises:
        FileNotFoundError: If a Parquet or sidecar is missing.
        ValueError: If a sidecar or minimum schema is invalid.
    """
    if not lake_dir.is_dir():
        raise FileNotFoundError(f"Lake directory not found: {lake_dir}")
    frames: dict[str, pd.DataFrame] = {}
    checksums: dict[str, str] = {}
    for name in CONTRACT_NAMES:
        path = _contract_path(lake_dir, name)
        if not path.exists():
            raise FileNotFoundError(f"Missing required contract: {path.name}")
        _validate_sidecar(path)
        try:
            frame = pd.read_parquet(path)
        except (OSError, ValueError, ImportError) as error:
            raise ValueError(f"Unable to read contract {path.name}") from error
        _validate_schema(name, frame)
        frames[name] = frame
        checksums[name] = file_checksum(path)
    return Phase2Inputs(lake_dir=lake_dir, frames=frames, checksums=checksums)


def _ensure_temporal_markers(frames: dict[str, pd.DataFrame]) -> None:
    for name, frame in frames.items():
        invalid = set(frame["temporal_marker"].dropna().unique()) - TEMPORAL_MARKERS
        if invalid:
            raise ValueError(f"{name} has invalid temporal_marker values: {sorted(invalid)}")
        if frame["temporal_marker"].isna().any():
            raise ValueError(f"{name} has null temporal_marker values")


def _ensure_unique_key(name: str, frame: pd.DataFrame, key: list[str]) -> None:
    if frame.duplicated(key).any():
        raise ValueError(f"{name} has duplicate key {key}")


def _ensure_utc(frame: pd.DataFrame, column: str, name: str, allow_null: bool = False) -> None:
    dtype = frame[column].dtype
    timezone = getattr(dtype, "tz", None)
    if timezone is None or str(timezone) != "UTC":
        raise ValueError(f"{name}.{column} must be timezone-aware UTC")
    if not allow_null and frame[column].isna().any():
        raise ValueError(f"{name}.{column} contains null timestamps")


def _reconcile_git(inputs: Phase2Inputs) -> dict[str, int]:
    commits = inputs["git_commits"]
    team_cuts = inputs["git_team_cuts"]
    grouped = (
        commits.groupby(TEAM_CUT_KEY, dropna=False)
        .agg(
            lines_added=("lines_added", "sum"),
            lines_deleted=("lines_deleted", "sum"),
            files_changed=("files_changed", "sum"),
            num_authors=("ID_Autor_Local", "nunique"),
            num_commits=("commit_hash", "nunique"),
        )
        .reset_index()
    )
    expected = team_cuts[TEAM_CUT_KEY + ["lines_added", "lines_deleted", "files_changed", "num_authors", "num_commits"]]
    merged = expected.merge(grouped, on=TEAM_CUT_KEY, how="outer", suffixes=("_declared", "_recalculated"), indicator=True)
    value_columns = ["lines_added", "lines_deleted", "files_changed", "num_authors", "num_commits"]
    mismatch = merged["_merge"].ne("both")
    for column in value_columns:
        mismatch |= merged[f"{column}_declared"].ne(merged[f"{column}_recalculated"])
    if mismatch.any():
        raise ValueError("git_team_cuts reconciliation diverges from git_commits")
    return {"declared_rows": int(len(expected)), "recalculated_rows": int(len(grouped))}


def validate_phase1_contracts(inputs: Phase2Inputs) -> dict[str, Any]:
    """Validate keys, temporal fields, timestamps, snapshots, and Git totals.

    Args:
        inputs: Contracts returned by :func:`load_phase2_inputs`.

    Returns:
        A privacy-preserving contract report containing schemas, counts,
        checksums, and reconciliation status.

    Raises:
        ValueError: If any contract invariant is violated.
    """
    frames = inputs.frames
    _ensure_temporal_markers(frames)
    _ensure_unique_key("evaluator_team_cuts", frames["evaluator_team_cuts"], TEAM_CUT_KEY)
    _ensure_unique_key("git_team_cuts", frames["git_team_cuts"], TEAM_CUT_KEY)
    _ensure_unique_key(
        "git_repository_snapshots",
        frames["git_repository_snapshots"],
        TEAM_CUT_KEY + ["repository"],
    )

    students = frames["student_responses"]
    if students["source_file"].isna().any() or students["source_file"].astype(str).str.strip().eq("").any():
        raise ValueError("student_responses source_file must be non-empty")
    _ensure_utc(frames["git_commits"], "timestamp", "git_commits")
    _ensure_utc(frames["git_files"], "timestamp", "git_files")
    _ensure_utc(
        frames["git_repository_snapshots"],
        "snapshot_timestamp",
        "git_repository_snapshots",
        allow_null=True,
    )

    snapshots = frames["git_repository_snapshots"]
    available = snapshots["snapshot_available"].fillna(False).astype(bool)
    if snapshots.loc[available, "snapshot_commit_hash"].isna().any():
        raise ValueError("observable snapshot requires snapshot_commit_hash")
    if snapshots.loc[available, "snapshot_timestamp"].isna().any():
        raise ValueError("observable snapshot requires snapshot_timestamp")
    if snapshots.loc[available, "repo_source_loc"].isna().any() or (snapshots.loc[available, "repo_source_loc"] < 0).any():
        raise ValueError("observable snapshot repo_source_loc must be non-negative")

    reconciliation = _reconcile_git(inputs)
    contract_reports: dict[str, dict[str, Any]] = {}
    for name, frame in frames.items():
        contract_reports[name] = {
            "rows": int(len(frame)),
            "columns": sorted(str(column) for column in frame.columns),
            "dtypes": {str(column): str(dtype) for column, dtype in frame.dtypes.items()},
            "null_counts": {str(column): int(count) for column, count in frame.isna().sum().items()},
            "keys": {
                "columns": (
                    TEAM_CUT_KEY + ["repository"]
                    if name == "git_repository_snapshots"
                    else TEAM_CUT_KEY
                    if name in {"evaluator_team_cuts", "git_team_cuts"}
                    else []
                ),
                "duplicate_rows": int(
                    frame.duplicated(
                        TEAM_CUT_KEY + ["repository"]
                        if name == "git_repository_snapshots"
                        else TEAM_CUT_KEY
                    ).sum()
                )
                if name in {"evaluator_team_cuts", "git_team_cuts", "git_repository_snapshots"}
                else None,
            },
            "counts_by_semester_and_cut": (
                frame.groupby(["Semestre", "temporal_marker"], dropna=False)
                .size()
                .rename("rows")
                .reset_index()
                .to_dict("records")
            ),
            "input_checksum": inputs.checksums[name],
        }

    return {
        "status": "success",
        "contract_version": "phase2-inputs-v1",
        "contracts": contract_reports,
        "violations": [],
        "git_reconciliation": {"status": "success", **reconciliation},
    }


def write_contract_report(report: dict[str, Any], output_path: Path) -> None:
    """Write a JSON contract report without raw research text.

    Args:
        report: Privacy-preserving report returned by the validator.
        output_path: Destination JSON path.
    """
    if report.get("status") != "success":
        raise ValueError("Only successful contract reports may be written")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    """Validate the lake contracts and write the Phase 2 contract report."""
    parser = argparse.ArgumentParser(description="Validate Phase 2 lake contracts")
    parser.add_argument("--lake-dir", type=Path, default=Path("data/lake"))
    parser.add_argument("--output", type=Path, default=Path("data/analysis/phase2_contract_report.json"))
    args = parser.parse_args()
    report = validate_phase1_contracts(load_phase2_inputs(args.lake_dir))
    write_contract_report(report, args.output)


if __name__ == "__main__":
    main()