"""Quantitative Phase 2 metric computations with explicit unavailable values."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path, PurePosixPath
from typing import Any

import numpy as np
import pandas as pd

from pipeline_config import (
    PLANNING_DEFINITION_VERSION,
    PLANNING_FILE_EXTENSIONS,
    PLANNING_PATH_PATTERNS,
)
from phase2_contracts import load_phase2_inputs, validate_phase1_contracts
from pipeline_core import (
    input_checksum,
    invalidate_stale_artifact,
    is_current_artifact,
    write_artifact_metadata,
)

logger = logging.getLogger(__name__)


KEYS = ["ID_Equipe", "Semestre"]
CUTS = ("T1", "T2", "T3")
PLANNING_ACTIVITY_STATUSES = {"added", "modified", "renamed", "copied"}
PLANNING_REQUIRED_COLUMNS = {
    "ID_Equipe", "Semestre", "temporal_marker", "file_path", "change_status",
    "is_binary", "lines_added", "lines_deleted",
}
PLANNING_OUTPUT_REQUIRED_COLUMNS = {
    "ID_Equipe", "Semestre", "pi_observation_unit", "pi_definition_version",
    "pi_available", "planning_rework_available",
}


def is_planning_artifact(
    file_path: str,
    *,
    extensions: set[str] | None = None,
    path_patterns: set[str] | None = None,
) -> bool:
    """Return whether a file path matches the versioned planning allowlist.

    Document-oriented extensions are accepted anywhere. Configuration formats
    are accepted only when their path identifies planning or documentation.
    """
    normalized = str(file_path).replace("\\", "/").strip().lower()
    if not normalized:
        return False
    configured_extensions = extensions or PLANNING_FILE_EXTENSIONS
    configured_patterns = path_patterns or PLANNING_PATH_PATTERNS
    suffix = PurePosixPath(normalized).suffix
    if suffix not in configured_extensions:
        return False
    contextual_extensions = {".yaml", ".yml", ".json", ".toml"}
    if suffix not in contextual_extensions:
        return True
    return any(pattern.lower() in normalized for pattern in configured_patterns)


def compute_planning_metrics(
    files: pd.DataFrame,
    *,
    team_semester_keys: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compute allowlist-based planning artifact metrics by team and semester.

    Args:
        files: Validated ``git_files`` observations.
        team_semester_keys: Optional observed team-semester universe. Rows in
            this universe without file events are marked unavailable.

    Returns:
        One row per observed team-semester with PI and longitudinal planning
        activity fields.

    Raises:
        ValueError: If the input schema, temporal markers, or key universe is
            invalid.
    """
    missing = PLANNING_REQUIRED_COLUMNS - set(files.columns)
    if missing:
        raise ValueError(f"git_files missing columns: {sorted(missing)}")
    if files[["ID_Equipe", "Semestre"]].isna().any().any():
        raise ValueError("git_files team-semester keys must be non-null")
    invalid_cuts = set(files["temporal_marker"].dropna()) - set(CUTS)
    if invalid_cuts:
        raise ValueError(f"git_files has invalid temporal markers: {sorted(invalid_cuts)}")
    if {"commit_hash", "file_path"}.issubset(files.columns):
        if files.duplicated(["commit_hash", "file_path"]).any():
            raise ValueError("git_files contains duplicate commit-file observations")

    if team_semester_keys is None:
        universe = files[["ID_Equipe", "Semestre"]].drop_duplicates()
    else:
        required_keys = {"ID_Equipe", "Semestre"}
        missing_keys = required_keys - set(team_semester_keys.columns)
        if missing_keys:
            raise ValueError(f"team-semester keys missing columns: {sorted(missing_keys)}")
        if team_semester_keys.duplicated(["ID_Equipe", "Semestre"]).any():
            raise ValueError("team-semester keys must be unique")
        universe = team_semester_keys[["ID_Equipe", "Semestre"]].drop_duplicates()

    observed = files.copy()
    observed["is_planning_artifact"] = observed["file_path"].map(is_planning_artifact)
    observed = observed.loc[observed["is_planning_artifact"]].copy()
    rows: list[dict[str, Any]] = []
    for key in universe.itertuples(index=False, name=None):
        team, semester = key
        all_events = files[(files["ID_Equipe"] == team) & (files["Semestre"] == semester)]
        planning = observed[(observed["ID_Equipe"] == team) & (observed["Semestre"] == semester)]
        row: dict[str, Any] = {"ID_Equipe": team, "Semestre": semester}
        has_observed_events = not all_events.empty
        row["pi_available"] = bool(has_observed_events)
        row["pi_unavailable_reason"] = None if has_observed_events else "no_observed_git_file_events"
        for cut in CUTS:
            current = planning[planning["temporal_marker"] == cut]
            active = current[current["change_status"].isin(PLANNING_ACTIVITY_STATUSES)]
            row[f"pi_file_count_{cut.lower()}"] = int(len(active)) if has_observed_events else np.nan
            text_events = current.loc[~current["is_binary"].astype(bool)]
            line_delta = text_events[["lines_added", "lines_deleted"]].fillna(0).sum().sum()
            row[f"pi_line_delta_{cut.lower()}"] = float(line_delta) if has_observed_events else np.nan
            row[f"pi_renamed_count_{cut.lower()}"] = int((current["change_status"] == "renamed").sum()) if has_observed_events else np.nan
            row[f"pi_deleted_count_{cut.lower()}"] = int((current["change_status"] == "deleted").sum()) if has_observed_events else np.nan
            row[f"pi_binary_event_count_{cut.lower()}"] = int(current["is_binary"].astype(bool).sum()) if has_observed_events else np.nan
            row[f"planning_artifact_activity_{cut.lower()}"] = int(len(active)) if has_observed_events else np.nan
        row["planning_rework_signal_t2_t3"] = (
            int(row["planning_artifact_activity_t2"] + row["planning_artifact_activity_t3"] + row["pi_deleted_count_t2"] + row["pi_deleted_count_t3"])
            if has_observed_events else np.nan
        )
        row["planning_rework_event_n_t2_t3"] = row["planning_rework_signal_t2_t3"]
        row["planning_rework_available"] = bool(has_observed_events)
        row["planning_rework_unavailable_reason"] = row["pi_unavailable_reason"]
        row["pi_observation_unit"] = "team_semester"
        row["pi_definition_version"] = PLANNING_DEFINITION_VERSION
        rows.append(row)
    return pd.DataFrame(rows)


def write_planning_metrics(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Write the immutable planning metrics intermediate artifact.

    Args:
        results: Team-semester planning metrics.
        output_path: Parquet output path below the analysis directory.
        source_checksum: Checksum of the Git file input and PI protocol.
        options: Effective PI options recorded in the sidecar.

    Raises:
        ValueError: If the output contract is invalid or a stale artifact would
            be overwritten.
    """
    missing = PLANNING_OUTPUT_REQUIRED_COLUMNS - set(results.columns)
    if missing:
        raise ValueError(f"planning_metrics output missing columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("planning_metrics output is empty")
    if results.duplicated(KEYS).any():
        raise ValueError("planning_metrics has duplicate team-semester keys")
    if not results["pi_observation_unit"].eq("team_semester").all():
        raise ValueError("planning_metrics has an invalid observation unit")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if is_current_artifact(output_path, source_checksum):
        return
    if output_path.exists() or output_path.with_name(f"{output_path.name}.metadata.json").exists():
        raise ValueError("planning_metrics artifact is immutable and stale")
    results.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="planning-metrics-v1",
        options=options,
    )


def main() -> None:
    """Generate the resumable planning metrics intermediate artifact."""
    parser = argparse.ArgumentParser(description="Generate Phase 2 planning metrics")
    parser.add_argument("--lake-dir", type=Path, default=Path("data/lake"))
    parser.add_argument(
        "--contract-report",
        type=Path,
        default=Path("data/analysis/phase2_contract_report.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/analysis/planning_metrics.parquet"),
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not args.contract_report.exists():
        raise FileNotFoundError(f"Contract report not found: {args.contract_report}")
    report = json.loads(args.contract_report.read_text(encoding="utf-8"))
    if report.get("status") != "success":
        raise ValueError("Phase 2 contract report is not successful")
    inputs = load_phase2_inputs(args.lake_dir)
    validate_phase1_contracts(inputs)
    options = {
        "stage": "planning_metrics",
        "contract_version": "planning-metrics-v1",
        "pi_definition_version": PLANNING_DEFINITION_VERSION,
        "planning_activity_statuses": sorted(PLANNING_ACTIVITY_STATUSES),
        "planning_file_extensions": sorted(PLANNING_FILE_EXTENSIONS),
        "planning_path_patterns": sorted(PLANNING_PATH_PATTERNS),
    }
    checksum = input_checksum(
        [
            args.lake_dir / "git_files.parquet",
            args.lake_dir / "git_files.parquet.metadata.json",
        ],
        options,
    )
    if args.force:
        invalidate_stale_artifact(args.output, "force-regeneration")
    if is_current_artifact(args.output, checksum):
        logger.info("Planning metrics artifact is current: %s", args.output)
        return
    results = compute_planning_metrics(inputs["git_files"])
    invalidate_stale_artifact(args.output, checksum)
    write_planning_metrics(
        results,
        args.output,
        source_checksum=checksum,
        options=options,
    )
    logger.info("Wrote %s planning metrics team-semester observations", len(results))


def _pivot_cut(frame: pd.DataFrame, value: str, prefix: str) -> pd.DataFrame:
    pivot = frame.pivot_table(index=KEYS, columns="temporal_marker", values=value, aggfunc="first")
    pivot.columns = [f"{prefix}_{column.lower()}" for column in pivot.columns]
    return pivot.reset_index()


def build_cut_context_metrics(students: pd.DataFrame, transcripts: pd.DataFrame) -> pd.DataFrame:
    """Build IE context metrics without assigning observations to teams."""
    keys = ["Semestre", "temporal_marker"]
    student = students.groupby(keys).agg(ie_student_cognitive_load_mean=("cognitive_load_score", "mean"), ie_student_sentiment_mean=("sentiment_score", "mean"), ie_student_ai_dependency_mean=("ai_dependency_score", "mean"), ie_student_n=("cognitive_load_score", "count")).reset_index()
    transcript = transcripts.groupby(keys).agg(ie_transcript_coordination_friction_mean=("coordination_friction_score", "mean"), ie_transcript_rework_signal_mean=("rework_signal_score", "mean"), ie_transcript_session_n=("coordination_friction_score", "count")).reset_index()
    result = student.merge(transcript, on=keys, how="outer", validate="one_to_one")
    result["unit_of_analysis"] = "cut_context"
    result["ie_definition_version"] = "ie-v1"
    return result


def compute_code_churn(commits: pd.DataFrame, files: pd.DataFrame, snapshots: pd.DataFrame) -> pd.DataFrame:
    """Compute longitudinal churn normalized by observed source LOC."""
    commits = commits.copy()
    commits["commit_churn"] = commits["lines_added"] + commits["lines_deleted"]
    grouped = commits.groupby(KEYS + ["temporal_marker"]).agg(cc_total=("commit_churn", "sum"), cc_commit_n=("commit_hash", "nunique")).reset_index()
    file_counts = files.groupby(KEYS + ["temporal_marker"]).agg(cc_unique_changed_files=("file_path", "nunique")).reset_index()
    snapshot_values = snapshots[KEYS + ["temporal_marker", "repo_source_loc"]]
    grouped = grouped.merge(file_counts, on=KEYS + ["temporal_marker"], how="left", validate="one_to_one").merge(snapshot_values, on=KEYS + ["temporal_marker"], how="left", validate="one_to_one")
    grouped["cc_per_source_loc"] = grouped["cc_total"].where(grouped["repo_source_loc"] > 0) / grouped["repo_source_loc"].where(grouped["repo_source_loc"] > 0)
    grouped["cc_per_changed_file"] = grouped["cc_total"].where(grouped["cc_unique_changed_files"] > 0) / grouped["cc_unique_changed_files"].where(grouped["cc_unique_changed_files"] > 0)
    grouped["cc_mean_per_commit"] = grouped["cc_total"].where(grouped["cc_commit_n"] > 0) / grouped["cc_commit_n"].where(grouped["cc_commit_n"] > 0)
    pieces = []
    for key, subset in grouped.groupby(KEYS):
        row: dict[str, Any] = dict(zip(KEYS, key))
        for cut in CUTS:
            current = subset[subset["temporal_marker"] == cut]
            values = current.iloc[0] if not current.empty else pd.Series(dtype=object)
            for metric in ("cc_total", "cc_commit_n", "repo_source_loc", "cc_unique_changed_files", "cc_per_source_loc", "cc_per_changed_file", "cc_mean_per_commit"):
                row[f"{metric}_{cut.lower()}"] = values.get(metric, np.nan)
        row["cc_denominator_kind"] = "observed_source_loc"
        row["repo_size_definition_version"] = "source-loc-v1"
        pieces.append(row)
    return pd.DataFrame(pieces)


def compute_delta_dt(evaluator: pd.DataFrame) -> pd.DataFrame:
    """Compute technical complexity trajectory and T1-to-T3 deltas."""
    result = _pivot_cut(evaluator, "technical_complexity_mean", "technical_complexity")
    for left, right, name in (("t1", "t2", "delta_dt_t1_t2"), ("t2", "t3", "delta_dt_t2_t3"), ("t1", "t3", "delta_dt_t1_t3")):
        result[name] = result[f"technical_complexity_{right}"] - result[f"technical_complexity_{left}"]
    return result


def compute_integration_friction(commits: pd.DataFrame, cut_starts: dict[str, pd.Timestamp]) -> pd.DataFrame:
    """Compute author concentration and churn for cuts and the T3 final window."""
    required = {"timestamp", "ID_Autor_Local", "branch_or_ref", "branch_or_ref_source"}
    if not required.issubset(commits.columns):
        raise ValueError(f"git_commits missing AI fields: {sorted(required - set(commits.columns))}")
    rows = []
    for key, subset in commits.groupby(KEYS):
        row = dict(zip(KEYS, key))
        for cut in CUTS:
            current = subset[subset["temporal_marker"] == cut]
            counts = current["ID_Autor_Local"].value_counts()
            row[f"ai_commit_n_{cut.lower()}"] = int(len(current))
            row[f"ai_churn_{cut.lower()}"] = int((current["lines_added"] + current["lines_deleted"]).sum())
            row[f"ai_author_n_{cut.lower()}"] = int(current["ID_Autor_Local"].nunique())
            row[f"ai_max_author_share_{cut.lower()}"] = float(counts.iloc[0] / len(current)) if len(current) else np.nan
        start = cut_starts["T3"]
        window = subset[(subset["timestamp"] >= start - pd.Timedelta(hours=48)) & (subset["timestamp"] < start)]
        counts = window["ID_Autor_Local"].value_counts()
        row["ai_commit_n_48h_before_t3"] = int(len(window))
        row["ai_churn_48h_before_t3"] = int((window["lines_added"] + window["lines_deleted"]).sum())
        row["ai_author_n_48h_before_t3"] = int(window["ID_Autor_Local"].nunique())
        row["ai_max_author_share_48h_before_t3"] = float(counts.iloc[0] / len(window)) if len(window) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def build_team_metrics(*partials: pd.DataFrame) -> pd.DataFrame:
    """Merge team-level metric partials with declared one-to-one cardinality."""
    if not partials:
        raise ValueError("At least one metric partial is required")
    result = partials[0].copy()
    for partial in partials[1:]:
        if partial.duplicated(KEYS).any():
            raise ValueError("Metric partial has duplicate team_semester keys")
        result = result.merge(partial, on=KEYS, how="outer", validate="one_to_one")
    result["unit_of_analysis"] = "team_semester"
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()