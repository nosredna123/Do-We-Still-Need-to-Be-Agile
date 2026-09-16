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
    AI_AUTHOR_SHARE_DISTRIBUTION,
    AI_DEFINITION_VERSION,
    AI_GINI_METHOD,
    AI_REF_REQUIRED_FIELDS,
    AI_T3_WINDOW_BOUNDS,
    AI_T3_WINDOW_HOURS,
    EVALUATOR_TEMPORAL_CUTS,
    PLANNING_DEFINITION_VERSION,
    PLANNING_FILE_EXTENSIONS,
    PLANNING_PATH_PATTERNS,
)
from phase2_contracts import load_phase2_inputs, validate_phase1_contracts
from pipeline_core import (
    artifact_metadata_path,
    file_checksum,
    input_checksum,
    invalidate_stale_artifact,
    is_current_artifact,
    write_artifact_metadata,
)
from pipeline_statistics import summarize_numeric_distribution

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
CODE_CHURN_OUTPUT_REQUIRED_COLUMNS = {
    "ID_Equipe", "Semestre", "cc_observation_unit", "cc_definition_version",
    "cc_binary_policy", "cc_denominator_kind",
}
DELTA_DT_REQUIRED_COLUMNS = set(KEYS) | {
    "temporal_marker",
    "technical_complexity_mean",
    "technical_complexity_median",
    "technical_complexity_iqr",
    "technical_complexity_std",
    "technical_complexity_n",
}
DELTA_DT_DISTRIBUTION_FIELDS = (
    "mean", "median", "iqr", "std", "n",
)
IE_SCORE_PREFIXES = (
    "ie_student_cognitive_load_score",
    "ie_student_sentiment_score",
    "ie_student_ai_dependency_score",
    "ie_transcript_coordination_friction_score",
    "ie_transcript_rework_signal_score",
    "ie_transcript_planning_clarity_score",
)
IE_SUMMARY_FIELDS = (
    "mean", "std", "median", "q1", "q3", "iqr", "mode", "mode_n",
    "mode_share", "n_total", "n_valid", "n_missing",
)


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
    parser.add_argument(
        "--code-churn-output",
        type=Path,
        default=Path("data/analysis/code_churn_metrics.parquet"),
    )
    parser.add_argument(
        "--technical-degradation-output",
        type=Path,
        default=Path("data/analysis/technical_degradation_metrics.parquet"),
    )
    parser.add_argument(
        "--integration-friction-output",
        type=Path,
        default=Path("data/analysis/integration_friction_metrics.parquet"),
    )
    parser.add_argument(
        "--cut-context-output",
        type=Path,
        default=Path("data/analysis/cut_context_metrics.parquet"),
    )
    parser.add_argument(
        "--team-metrics-output",
        type=Path,
        default=Path("data/analysis/team_metrics.parquet"),
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
        invalidate_stale_artifact(args.code_churn_output, "force-regeneration")
        invalidate_stale_artifact(args.technical_degradation_output, "force-regeneration")
        invalidate_stale_artifact(args.integration_friction_output, "force-regeneration")
        invalidate_stale_artifact(args.cut_context_output, "force-regeneration")
        invalidate_stale_artifact(args.team_metrics_output, "force-regeneration")
        exclusions_path = args.team_metrics_output.with_name("team_metrics_exclusions.json")
        if exclusions_path.exists():
            exclusions_path.unlink()
    if is_current_artifact(args.output, checksum):
        logger.info("Planning metrics artifact is current: %s", args.output)
    else:
        results = compute_planning_metrics(inputs["git_files"])
        invalidate_stale_artifact(args.output, checksum)
        write_planning_metrics(
            results,
            args.output,
            source_checksum=checksum,
            options=options,
        )
        logger.info("Wrote %s planning metrics team-semester observations", len(results))
    churn_options = {
        "stage": "code_churn_metrics",
        "contract_version": "code-churn-metrics-v1",
        "cc_definition_version": "cc-v1",
        "cc_binary_policy": "excluded_from_line_churn_counted_as_events",
        "rolling_window_days": 7,
        "rolling_window_bounds": "[timestamp, timestamp+7d)",
    }
    churn_checksum = input_checksum(
        [
            args.lake_dir / "git_commits.parquet",
            args.lake_dir / "git_commits.parquet.metadata.json",
            args.lake_dir / "git_files.parquet",
            args.lake_dir / "git_files.parquet.metadata.json",
            args.lake_dir / "git_repository_snapshots.parquet",
            args.lake_dir / "git_repository_snapshots.parquet.metadata.json",
        ],
        churn_options,
    )
    if not args.force and is_current_artifact(args.code_churn_output, churn_checksum):
        logger.info("Code Churn artifact is current: %s", args.code_churn_output)
    else:
        churn_results = compute_code_churn(
            inputs["git_commits"],
            inputs["git_files"],
            inputs["git_repository_snapshots"],
        )
        invalidate_stale_artifact(args.code_churn_output, churn_checksum)
        write_code_churn_metrics(
            churn_results,
            args.code_churn_output,
            source_checksum=churn_checksum,
            options=churn_options,
        )
        logger.info("Wrote %s Code Churn team-semester observations", len(churn_results))

    dt_options = {
        "stage": "technical_degradation_metrics",
        "contract_version": "technical-degradation-metrics-v1",
        "dt_definition_version": "dt-v1",
        "delta_metric": "technical_complexity_mean",
        "distribution_fields": list(DELTA_DT_DISTRIBUTION_FIELDS),
        "availability_policy": "fail_if_any_cut_missing",
    }
    dt_checksum = input_checksum(
        [
            args.lake_dir / "evaluator_team_cuts.parquet",
            args.lake_dir / "evaluator_team_cuts.parquet.metadata.json",
        ],
        dt_options,
    )
    if not args.force and is_current_artifact(args.technical_degradation_output, dt_checksum):
        logger.info("Technical degradation artifact is current: %s", args.technical_degradation_output)
    else:
        dt_results = compute_delta_dt(inputs["evaluator_team_cuts"])
        invalidate_stale_artifact(args.technical_degradation_output, dt_checksum)
        write_technical_degradation_metrics(
            dt_results,
            args.technical_degradation_output,
            source_checksum=dt_checksum,
            options=dt_options,
        )
        logger.info("Wrote %s technical degradation team-semester observations", len(dt_results))

    ai_options = {
        "stage": "integration_friction_metrics",
        "contract_version": "integration-friction-metrics-v1",
        "ai_definition_version": AI_DEFINITION_VERSION,
        "ai_t3_window_hours": AI_T3_WINDOW_HOURS,
        "ai_t3_window_bounds": AI_T3_WINDOW_BOUNDS,
        "ai_gini_method": AI_GINI_METHOD,
        "ai_author_share_distribution": AI_AUTHOR_SHARE_DISTRIBUTION,
        "ai_ref_required_fields": AI_REF_REQUIRED_FIELDS,
    }
    ai_checksum = input_checksum(
        [
            args.lake_dir / "git_commits.parquet",
            args.lake_dir / "git_commits.parquet.metadata.json",
        ],
        ai_options,
    )
    if not args.force and is_current_artifact(args.integration_friction_output, ai_checksum):
        logger.info("Integration friction artifact is current: %s", args.integration_friction_output)
    else:
        cut_starts = {
            semester: pd.Timestamp(cuts["T3"][0], tz="UTC")
            for semester, cuts in EVALUATOR_TEMPORAL_CUTS.items()
        }
        ai_results = compute_integration_friction(inputs["git_commits"], cut_starts)
        invalidate_stale_artifact(args.integration_friction_output, ai_checksum)
        write_integration_friction_metrics(
            ai_results,
            args.integration_friction_output,
            source_checksum=ai_checksum,
            options=ai_options,
        )
        logger.info("Wrote %s integration friction team-semester observations", len(ai_results))

    ie_options = {
        "stage": "cut_context_metrics",
        "contract_version": "cut-context-metrics-v1",
        "ie_definition_version": "ie-v1",
        "statistical_summary_version": "distribution-summary-v1",
        "source_contract": "textual-cut-signals-v2",
        "statistical_decisions": {
            "std_ddof": 1,
            "quantile_method": "linear",
            "scale_treatment": "ordinal_with_interval_summary",
        },
    }
    ie_checksum = input_checksum(
        [
            args.lake_dir.parent / "analysis" / "textual_cut_signals.parquet",
            args.lake_dir.parent / "analysis" / "textual_cut_signals.parquet.metadata.json",
        ],
        ie_options,
    )
    if not args.force and is_current_artifact(args.cut_context_output, ie_checksum):
        logger.info("Cut context artifact is current: %s", args.cut_context_output)
    else:
        textual_path = args.lake_dir.parent / "analysis" / "textual_cut_signals.parquet"
        textual_metadata_path = textual_path.with_name(f"{textual_path.name}.metadata.json")
        textual_metadata = json.loads(textual_metadata_path.read_text(encoding="utf-8"))
        if textual_metadata.get("status") != "success" or textual_metadata.get("contract_version") != "textual-cut-signals-v2":
            raise ValueError("textual_cut_signals source contract is missing or incompatible")
        ie_results = build_cut_context_metrics(pd.read_parquet(textual_path))
        invalidate_stale_artifact(args.cut_context_output, ie_checksum)
        write_cut_context_metrics(
            ie_results,
            args.cut_context_output,
            source_checksum=ie_checksum,
            options=ie_options,
        )
        logger.info("Wrote %s cut context observations", len(ie_results))

    team_options = {
        "stage": "team_metrics",
        "contract_version": "team-metrics-v1",
        "unit_of_analysis": "team_semester",
        "ie_policy": "excluded_from_team_metrics; source_is_cut_context",
    }
    team_contract_paths = {
        "planning": args.output,
        "code_churn": args.code_churn_output,
        "technical_degradation": args.technical_degradation_output,
        "integration_friction": args.integration_friction_output,
    }
    team_checksum = input_checksum(
        [
            *team_contract_paths.values(),
            *[artifact_metadata_path(path) for path in team_contract_paths.values()],
            args.contract_report,
        ],
        team_options,
    )
    exclusions_path = args.team_metrics_output.with_name("team_metrics_exclusions.json")
    if (
        not args.force
        and is_current_artifact(args.team_metrics_output, team_checksum)
        and exclusions_path.exists()
    ):
        logger.info("Team metrics artifact is current: %s", args.team_metrics_output)
    else:
        invalidate_stale_artifact(args.team_metrics_output, team_checksum)
        if exclusions_path.exists():
            exclusions_path.unlink()
        consolidate_team_metrics(
            team_contract_paths,
            output_path=args.team_metrics_output,
            contract_report_path=args.contract_report,
            options=team_options,
        )
        logger.info("Wrote team metrics artifact: %s", args.team_metrics_output)


def write_code_churn_metrics(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Write the immutable Code Churn intermediate artifact and sidecar."""
    missing = CODE_CHURN_OUTPUT_REQUIRED_COLUMNS - set(results.columns)
    if missing:
        raise ValueError(f"code_churn_metrics output missing columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("code_churn_metrics output is empty")
    if results.duplicated(KEYS).any():
        raise ValueError("code_churn_metrics has duplicate team-semester keys")
    if not results["cc_observation_unit"].eq("team_semester").all():
        raise ValueError("code_churn_metrics has an invalid observation unit")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if is_current_artifact(output_path, source_checksum):
        return
    if output_path.exists() or output_path.with_name(f"{output_path.name}.metadata.json").exists():
        raise ValueError("code_churn_metrics artifact is immutable and stale")
    results.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="code-churn-metrics-v1",
        options=options,
    )


def _pivot_cut(frame: pd.DataFrame, value: str, prefix: str) -> pd.DataFrame:
    pivot = frame.pivot_table(index=KEYS, columns="temporal_marker", values=value, aggfunc="first")
    pivot.columns = [f"{prefix}_{column.lower()}" for column in pivot.columns]
    return pivot.reset_index()


def build_cut_context_metrics(
    students: pd.DataFrame,
    transcripts: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Transform the canonical textual-cut-signal contract into IE context."""
    if transcripts is not None and "unit_of_analysis" not in students.columns:
        keys = ["Semestre", "temporal_marker"]
        student = students.groupby(keys).agg(
            ie_student_cognitive_load_mean=("cognitive_load_score", "mean"),
            ie_student_sentiment_mean=("sentiment_score", "mean"),
            ie_student_ai_dependency_mean=("ai_dependency_score", "mean"),
            ie_student_n=("cognitive_load_score", "count"),
        ).reset_index()
        transcript = transcripts.groupby(keys).agg(
            ie_transcript_coordination_friction_mean=("coordination_friction_score", "mean"),
            ie_transcript_rework_signal_mean=("rework_signal_score", "mean"),
            ie_transcript_session_n=("coordination_friction_score", "count"),
        ).reset_index()
        result = student.merge(transcript, on=keys, how="outer", validate="one_to_one")
        result["unit_of_analysis"] = "cut_context"
        result["ie_definition_version"] = "ie-v1"
        return result
    required = {"Semestre", "temporal_marker", "unit_of_analysis", "student_n", "transcript_session_n"}
    missing = required - set(students.columns)
    if missing:
        raise ValueError(f"textual_cut_signals input missing columns: {sorted(missing)}")
    if not students["unit_of_analysis"].eq("cut_context").all():
        raise ValueError("textual_cut_signals input has an invalid unit_of_analysis")
    required_transcript_columns = {
        f"{prefix}_{field}"
        for prefix in IE_SCORE_PREFIXES[3:]
        for field in IE_SUMMARY_FIELDS
    }
    missing = required_transcript_columns - set(students.columns)
    if missing:
        raise ValueError(f"textual_cut_signals input missing columns: {sorted(missing)}")
    student_summary_columns = {
        column for column in students.columns
        if column.startswith("student_")
        and any(column.endswith(f"_{field}") for field in IE_SUMMARY_FIELDS)
    }
    has_canonical_student_summaries = all(
        f"{prefix}_{field}" in students.columns
        for prefix in IE_SCORE_PREFIXES[:3]
        for field in IE_SUMMARY_FIELDS
    )
    if not student_summary_columns and not has_canonical_student_summaries:
        raise ValueError("textual_cut_signals input missing student distribution summaries")
    if students.duplicated(["Semestre", "temporal_marker"]).any():
        raise ValueError("textual_cut_signals input has duplicate cut keys")
    result = students.copy()
    result["ie_transcript_available"] = result["transcript_session_n"].fillna(0).gt(0)
    result["ie_transcript_unavailable_reason"] = result["ie_transcript_available"].map(
        lambda available: None if available else "no_observed_transcript_sessions"
    )
    result["ie_definition_version"] = "ie-v1"
    result["statistical_summary_version"] = "distribution-summary-v1"
    result["std_ddof"] = 1
    result["quantile_method"] = "linear"
    return result


def write_cut_context_metrics(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Write the immutable IE cut-context artifact and metadata sidecar."""
    required = {"Semestre", "temporal_marker", "unit_of_analysis", "ie_definition_version", "statistical_summary_version"}
    missing = required - set(results.columns)
    if missing:
        raise ValueError(f"cut_context_metrics output missing columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("cut_context_metrics output is empty")
    if not results["unit_of_analysis"].eq("cut_context").all():
        raise ValueError("cut_context_metrics has an invalid unit_of_analysis")
    if results.duplicated(["Semestre", "temporal_marker"]).any():
        raise ValueError("cut_context_metrics has duplicate cut keys")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if is_current_artifact(output_path, source_checksum):
        return
    if output_path.exists() or output_path.with_name(f"{output_path.name}.metadata.json").exists():
        raise ValueError("cut_context_metrics artifact is immutable and stale")
    results.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="cut-context-metrics-v1",
        options=options,
    )


def compute_code_churn(commits: pd.DataFrame, files: pd.DataFrame, snapshots: pd.DataFrame) -> pd.DataFrame:
    """Compute persisted-contract-ready longitudinal Code Churn metrics."""
    required_commit = set(KEYS) | {
        "temporal_marker", "commit_hash", "timestamp", "lines_added", "lines_deleted"
    }
    required_file = set(KEYS) | {"temporal_marker", "file_path", "is_binary"}
    required_snapshot = set(KEYS) | {"temporal_marker", "repo_source_loc"}
    for frame, required, name in (
        (commits, required_commit, "git_commits"),
        (files, required_file, "git_files"),
        (snapshots, required_snapshot, "git_repository_snapshots"),
    ):
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{name} missing columns: {sorted(missing)}")
    if not isinstance(commits["timestamp"].dtype, pd.DatetimeTZDtype):
        raise ValueError("git_commits timestamp must be timezone-aware UTC")
    invalid_cuts = set(commits["temporal_marker"].dropna()) | set(files["temporal_marker"].dropna()) | set(snapshots["temporal_marker"].dropna())
    invalid_cuts -= set(CUTS)
    if invalid_cuts:
        raise ValueError(f"Code Churn has invalid temporal markers: {sorted(invalid_cuts)}")

    commits = commits.copy()
    commits["commit_churn"] = commits["lines_added"] + commits["lines_deleted"]
    snapshot_rows = snapshots.copy()
    if "snapshot_available" in snapshot_rows.columns:
        snapshot_rows["snapshot_available"] = snapshot_rows["snapshot_available"].fillna(False).astype(bool)
    else:
        snapshot_rows["snapshot_available"] = snapshot_rows["repo_source_loc"].notna()
    snapshot_rows["repo_source_loc_valid"] = snapshot_rows["repo_source_loc"].where(
        snapshot_rows["snapshot_available"] & (snapshot_rows["repo_source_loc"] > 0)
    )
    snapshot_groups = snapshot_rows.groupby(KEYS + ["temporal_marker"], dropna=False)
    snapshot_summary = snapshot_groups.agg(
        repo_snapshot_n=("repository", "nunique") if "repository" in snapshot_rows.columns else ("repo_source_loc", "size"),
        repo_snapshot_available_n=("snapshot_available", "sum"),
        repo_source_loc=("repo_source_loc_valid", "sum"),
        repo_snapshot_row_n=("repo_source_loc", "size"),
    ).reset_index()
    snapshot_summary["repo_source_loc_available"] = (
        (snapshot_summary["repo_snapshot_available_n"] == snapshot_summary["repo_snapshot_row_n"])
        & snapshot_summary["repo_source_loc"].notna()
        & (snapshot_summary["repo_source_loc"] > 0)
    )
    snapshot_summary["repo_source_loc_unavailable_reason"] = np.select(
        [snapshot_summary["repo_snapshot_row_n"].eq(0), snapshot_summary["repo_snapshot_available_n"].lt(snapshot_summary["repo_snapshot_row_n"]), snapshot_summary["repo_source_loc"].isna() | snapshot_summary["repo_source_loc"].le(0)],
        ["no_snapshot_observed", "snapshot_unavailable", "invalid_source_loc"],
        default=None,
    )

    universe = pd.concat(
        [commits[KEYS], files[KEYS], snapshots[KEYS]], ignore_index=True
    ).drop_duplicates()
    rows: list[dict[str, Any]] = []
    for team, semester in universe.itertuples(index=False, name=None):
        row: dict[str, Any] = {"ID_Equipe": team, "Semestre": semester}
        team_commits = commits[(commits["ID_Equipe"] == team) & (commits["Semestre"] == semester)]
        team_files = files[(files["ID_Equipe"] == team) & (files["Semestre"] == semester)]
        team_snapshots = snapshot_summary[(snapshot_summary["ID_Equipe"] == team) & (snapshot_summary["Semestre"] == semester)]
        all_peak_windows: list[tuple[pd.Timestamp, float, str]] = []
        for cut in CUTS:
            cut_commits = team_commits[team_commits["temporal_marker"] == cut].sort_values("timestamp")
            cut_files = team_files[team_files["temporal_marker"] == cut]
            snapshot = team_snapshots[team_snapshots["temporal_marker"] == cut]
            has_activity = not cut_commits.empty
            valid_churn = cut_commits["commit_churn"].dropna()
            prefix = cut.lower()
            row[f"cc_activity_status_{prefix}"] = "observed_activity" if has_activity else "no_observed_activity"
            row[f"cc_total_{prefix}"] = float(valid_churn.sum()) if has_activity and not valid_churn.empty else 0
            row[f"cc_commit_n_{prefix}"] = int(len(cut_commits))
            row[f"cc_commit_churn_n_total_{prefix}"] = int(len(cut_commits))
            row[f"cc_commit_churn_n_valid_{prefix}"] = int(valid_churn.notna().sum())
            row[f"cc_commit_churn_n_missing_{prefix}"] = int(len(cut_commits) - valid_churn.notna().sum())
            row[f"cc_unique_changed_files_{prefix}"] = int(cut_files["file_path"].nunique()) if not cut_files.empty else 0
            row[f"cc_binary_file_events_{prefix}"] = int(cut_files["is_binary"].fillna(False).astype(bool).sum()) if not cut_files.empty else 0
            summary = summarize_numeric_distribution(valid_churn, scale_type="continuous", scale_version="commit-churn-v1")
            row[f"cc_mean_per_commit_{prefix}"] = summary["mean"]
            row[f"cc_median_per_commit_{prefix}"] = summary["median"]
            row[f"cc_iqr_per_commit_{prefix}"] = summary["iqr"]
            row[f"cc_commit_churn_mode_{prefix}"] = summary["mode"]
            row[f"cc_commit_churn_mode_n_{prefix}"] = summary["mode_n"]
            row[f"cc_commit_churn_mode_share_{prefix}"] = summary["mode_share"]
            snapshot_exists = not snapshot.empty
            source_loc = snapshot.iloc[0]["repo_source_loc"] if snapshot_exists else np.nan
            source_available = bool(snapshot.iloc[0]["repo_source_loc_available"]) if snapshot_exists else False
            reason = snapshot.iloc[0]["repo_source_loc_unavailable_reason"] if snapshot_exists else "no_snapshot_observed"
            row[f"repo_source_loc_{prefix}"] = source_loc if source_available else np.nan
            row[f"repo_snapshot_n_{prefix}"] = int(snapshot.iloc[0]["repo_snapshot_n"]) if snapshot_exists else 0
            row[f"repo_snapshot_available_{prefix}"] = source_available
            row[f"cc_source_loc_available_{prefix}"] = source_available
            row[f"cc_source_loc_unavailable_reason_{prefix}"] = None if source_available else reason
            row[f"cc_per_source_loc_{prefix}"] = float(row[f"cc_total_{prefix}"] / source_loc) if source_available and source_loc else np.nan
            changed_files = row[f"cc_unique_changed_files_{prefix}"]
            row[f"cc_per_changed_file_{prefix}"] = row[f"cc_total_{prefix}"] / changed_files if changed_files else np.nan
            if not cut_commits.empty:
                for timestamp in cut_commits["timestamp"]:
                    end = timestamp + pd.Timedelta(days=7)
                    window = team_commits[(team_commits["timestamp"] >= timestamp) & (team_commits["timestamp"] < end)]
                    churn = float(window["commit_churn"].dropna().sum())
                    all_peak_windows.append((timestamp, churn, cut))
        if all_peak_windows:
            _peak_timestamp, peak_value, peak_cut = max(all_peak_windows, key=lambda item: (item[1], -item[0].value))
            row["cc_peak_7d"] = peak_value
            row["cc_mean_7d"] = float(np.mean([item[1] for item in all_peak_windows]))
            row["cc_peak_7d_temporal_marker"] = peak_cut
        else:
            row["cc_peak_7d"] = np.nan
            row["cc_mean_7d"] = np.nan
            row["cc_peak_7d_temporal_marker"] = None
        row["cc_denominator_kind"] = "observed_source_loc"
        row["cc_binary_policy"] = "excluded_from_line_churn_counted_as_events"
        row["repo_size_definition_version"] = "source-loc-v1"
        row["cc_observation_unit"] = "team_semester"
        row["cc_definition_version"] = "cc-v1"
        rows.append(row)
    return pd.DataFrame(rows)


def compute_delta_dt(evaluator: pd.DataFrame) -> pd.DataFrame:
    """Compute longitudinal technical degradation metrics by team-semester."""
    missing = DELTA_DT_REQUIRED_COLUMNS - set(evaluator.columns)
    if missing:
        raise ValueError(f"evaluator_team_cuts missing columns: {sorted(missing)}")
    if evaluator.duplicated(KEYS + ["temporal_marker"]).any():
        raise ValueError("evaluator_team_cuts has duplicate team-cut observations")
    invalid_cuts = set(evaluator["temporal_marker"].dropna()) - set(CUTS)
    if invalid_cuts:
        raise ValueError(f"evaluator_team_cuts has invalid temporal markers: {sorted(invalid_cuts)}")

    rows: list[dict[str, Any]] = []
    for key, group in evaluator.groupby(KEYS, dropna=False):
        row: dict[str, Any] = dict(zip(KEYS, key))
        cuts_present = set(group["temporal_marker"])
        missing_cuts = [cut for cut in CUTS if cut not in cuts_present]
        for field in DELTA_DT_DISTRIBUTION_FIELDS:
            source = f"technical_complexity_{field}"
            for cut in CUTS:
                current = group.loc[group["temporal_marker"] == cut, source]
                row[f"technical_complexity_{field}_{cut.lower()}"] = (
                    current.iloc[0] if not current.empty else np.nan
                )
        row["dt_available"] = not missing_cuts
        row["dt_unavailable_reason"] = (
            f"missing_required_temporal_cut:{missing_cuts[0]}" if missing_cuts else None
        )
        for left, right, name in (
            ("t1", "t2", "delta_dt_t1_t2"),
            ("t2", "t3", "delta_dt_t2_t3"),
            ("t1", "t3", "delta_dt_t1_t3"),
        ):
            row[name] = (
                row[f"technical_complexity_mean_{right}"]
                - row[f"technical_complexity_mean_{left}"]
                if row["dt_available"]
                else np.nan
            )
        row["dt_observation_unit"] = "team_semester"
        row["dt_definition_version"] = "dt-v1"
        rows.append(row)
    return pd.DataFrame(rows)


def write_technical_degradation_metrics(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Write the immutable technical degradation intermediate artifact."""
    required = set(KEYS) | {
        "delta_dt_t1_t2", "delta_dt_t2_t3", "delta_dt_t1_t3",
        "dt_available", "dt_unavailable_reason", "dt_observation_unit",
        "dt_definition_version",
    }
    missing = required - set(results.columns)
    if missing:
        raise ValueError(f"technical_degradation_metrics output missing columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("technical_degradation_metrics output is empty")
    if results.duplicated(KEYS).any():
        raise ValueError("technical_degradation_metrics has duplicate team-semester keys")
    if not results["dt_observation_unit"].eq("team_semester").all():
        raise ValueError("technical_degradation_metrics has an invalid observation unit")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if is_current_artifact(output_path, source_checksum):
        return
    if output_path.exists() or output_path.with_name(f"{output_path.name}.metadata.json").exists():
        raise ValueError("technical_degradation_metrics artifact is immutable and stale")
    results.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="technical-degradation-metrics-v1",
        options=options,
    )


def write_integration_friction_metrics(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Write the immutable integration-friction intermediate artifact."""
    required = set(KEYS) | {
        "ai_available", "ai_unavailable_reason", "ai_observation_unit",
        "ai_definition_version", "ai_t3_window_hours",
    }
    missing = required - set(results.columns)
    if missing:
        raise ValueError(f"integration_friction_metrics output missing columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("integration_friction_metrics output is empty")
    if results.duplicated(KEYS).any():
        raise ValueError("integration_friction_metrics has duplicate team-semester keys")
    if not results["ai_observation_unit"].eq("team_semester").all():
        raise ValueError("integration_friction_metrics has an invalid observation unit")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if is_current_artifact(output_path, source_checksum):
        return
    if output_path.exists() or output_path.with_name(f"{output_path.name}.metadata.json").exists():
        raise ValueError("integration_friction_metrics artifact is immutable and stale")
    results.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="integration-friction-metrics-v1",
        options=options,
    )


def compute_integration_friction(
    commits: pd.DataFrame,
    cut_starts: dict[str, pd.Timestamp],
    *,
    window_hours: int | None = None,
) -> pd.DataFrame:
    """Compute author concentration and integration pressure by team-semester."""
    required = set(KEYS) | {
        "timestamp", "ID_Autor_Local", "lines_added", "lines_deleted",
        *AI_REF_REQUIRED_FIELDS,
    }
    missing = required - set(commits.columns)
    if missing:
        raise ValueError(f"git_commits missing AI fields: {sorted(missing)}")
    if not isinstance(commits["timestamp"].dtype, pd.DatetimeTZDtype):
        raise ValueError("git_commits timestamp must be timezone-aware UTC")
    if not isinstance(cut_starts, dict):
        raise ValueError("cut_starts must map Semestre to T3 timestamps")
    effective_window_hours = window_hours if window_hours is not None else AI_T3_WINDOW_HOURS
    rows: list[dict[str, Any]] = []

    def gini(values: pd.Series) -> float | None:
        ordered = np.sort(values.astype(float).to_numpy())
        if len(ordered) == 0:
            return None
        if len(ordered) == 1 or ordered.sum() == 0:
            return 0.0
        index = np.arange(1, len(ordered) + 1)
        return float((2 * np.sum(index * ordered) / (len(ordered) * ordered.sum())) - (len(ordered) + 1) / len(ordered))

    for key, subset in commits.groupby(KEYS, dropna=False):
        row: dict[str, Any] = dict(zip(KEYS, key))
        semester = key[1]
        t3_start = cut_starts.get(semester)
        for cut in CUTS:
            current = subset[subset["temporal_marker"] == cut]
            prefix = cut.lower()
            row[f"ai_commit_n_{prefix}"] = int(len(current))
            row[f"ai_churn_{prefix}"] = float((current["lines_added"] + current["lines_deleted"]).sum()) if not current.empty else 0
            row[f"ai_activity_available_{prefix}"] = True
            row[f"ai_activity_status_{prefix}"] = "observed_activity" if not current.empty else "no_observed_activity"
            ref_valid = current[AI_REF_REQUIRED_FIELDS].notna().all(axis=1) & current[AI_REF_REQUIRED_FIELDS].astype(str).apply(lambda column: column.str.strip().ne("")).all(axis=1)
            row[f"ai_ref_available_{prefix}"] = bool(ref_valid.all()) if not current.empty else True
            row[f"ai_ref_unavailable_reason_{prefix}"] = None if row[f"ai_ref_available_{prefix}"] else "missing_observed_branch_or_ref"
            authors = current["ID_Autor_Local"].dropna()
            counts = authors.value_counts()
            shares = counts / len(current) if len(current) else pd.Series(dtype=float)
            concentration_available = bool(row[f"ai_ref_available_{prefix}"] and not current.empty and not authors.empty)
            row[f"ai_concentration_available_{prefix}"] = concentration_available
            row[f"ai_author_n_{prefix}"] = int(counts.size)
            row[f"ai_max_author_share_{prefix}"] = float(shares.max()) if concentration_available else np.nan
            share_summary = summarize_numeric_distribution(shares, scale_type="continuous", scale_version="ai-author-share-v1")
            row[f"ai_author_share_median_{prefix}"] = share_summary["median"] if concentration_available else np.nan
            row[f"ai_author_share_iqr_{prefix}"] = share_summary["iqr"] if concentration_available else np.nan
            row[f"ai_author_share_n_valid_{prefix}"] = share_summary["n_valid"] if concentration_available else 0
            row[f"ai_author_share_n_missing_{prefix}"] = share_summary["n_missing"] if concentration_available else int(len(current))
            row[f"ai_gini_{prefix}"] = gini(counts) if concentration_available else np.nan
        if t3_start is None:
            window = subset.iloc[0:0]
            row["ai_window_available"] = False
            row["ai_window_unavailable_reason"] = "missing_t3_start_for_semester"
        else:
            start = pd.Timestamp(t3_start)
            if start.tzinfo is None:
                start = start.tz_localize("UTC")
            window = subset[(subset["timestamp"] >= start - pd.Timedelta(hours=effective_window_hours)) & (subset["timestamp"] < start)]
            row["ai_window_available"] = True
            row["ai_window_unavailable_reason"] = None
        authors = window["ID_Autor_Local"].dropna()
        counts = authors.value_counts()
        shares = counts / len(window) if len(window) else pd.Series(dtype=float)
        window_ref_valid = window[AI_REF_REQUIRED_FIELDS].notna().all(axis=1) & window[AI_REF_REQUIRED_FIELDS].astype(str).apply(lambda column: column.str.strip().ne("")).all(axis=1)
        row["ai_commit_n_before_t3_window"] = int(len(window))
        row["ai_churn_before_t3_window"] = float((window["lines_added"] + window["lines_deleted"]).sum()) if not window.empty else 0
        row["ai_author_n_before_t3_window"] = int(counts.size)
        row["ai_ref_available_before_t3_window"] = bool(window_ref_valid.all()) if not window.empty else True
        row["ai_max_author_share_before_t3_window"] = float(shares.max()) if row["ai_window_available"] and not shares.empty and row["ai_ref_available_before_t3_window"] else np.nan
        row["ai_author_share_median_before_t3_window"] = float(shares.median()) if not shares.empty and row["ai_ref_available_before_t3_window"] else np.nan
        row["ai_author_share_iqr_before_t3_window"] = float(shares.quantile(0.75) - shares.quantile(0.25)) if not shares.empty and row["ai_ref_available_before_t3_window"] else np.nan
        row["ai_author_share_n_valid_before_t3_window"] = int(len(shares)) if row["ai_ref_available_before_t3_window"] else 0
        row["ai_gini_before_t3_window"] = gini(counts) if not shares.empty and row["ai_ref_available_before_t3_window"] else np.nan
        row["ai_t3_window_hours"] = effective_window_hours
        row["ai_window_bounds"] = AI_T3_WINDOW_BOUNDS
        row["ai_available"] = bool(row["ai_window_available"] and all(row[f"ai_concentration_available_{cut.lower()}"] for cut in CUTS))
        row["ai_unavailable_reason"] = None if row["ai_available"] else "one_or_more_cut_concentration_unavailable"
        row["ai_observation_unit"] = "team_semester"
        row["ai_definition_version"] = AI_DEFINITION_VERSION
        rows.append(row)
    return pd.DataFrame(rows)


def build_team_metrics(*partials: pd.DataFrame) -> pd.DataFrame:
    """Merge team-level metric partials with declared one-to-one cardinality."""
    if not partials:
        raise ValueError("At least one metric partial is required")
    result = partials[0].copy()
    if result.duplicated(KEYS).any():
        raise ValueError("Metric partial has duplicate team_semester keys")
    for partial in partials[1:]:
        if partial.duplicated(KEYS).any():
            raise ValueError("Metric partial has duplicate team_semester keys")
        result = result.merge(partial, on=KEYS, how="outer", validate="one_to_one")
    result["unit_of_analysis"] = "team_semester"
    return result


def _load_team_metric_contract(
    path: Path,
    *,
    contract_version: str,
    unit_column: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load and validate one persisted team-semester metric contract."""
    metadata_path = artifact_metadata_path(path)
    if not path.exists() or not metadata_path.exists():
        raise FileNotFoundError(f"Missing metric contract or sidecar: {path}")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid metric contract sidecar: {metadata_path.name}") from error
    if metadata.get("status") != "success":
        raise ValueError(f"Metric contract sidecar is not successful: {path.name}")
    if metadata.get("contract_version") != contract_version:
        raise ValueError(f"Unexpected contract version for {path.name}")
    if not metadata.get("input_checksum"):
        raise ValueError(f"Metric contract sidecar lacks checksum: {path.name}")
    frame = pd.read_parquet(path)
    missing = (set(KEYS) | {unit_column}) - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name} missing contract columns: {sorted(missing)}")
    if frame.duplicated(KEYS).any():
        raise ValueError(f"{path.name} has duplicate team-semester keys")
    if not frame[unit_column].eq("team_semester").all():
        raise ValueError(f"{path.name} has an invalid observation unit")
    return frame, metadata


def write_team_metrics(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
    exclusions: dict[str, Any],
) -> None:
    """Write the immutable consolidated team-semester contract and exclusions."""
    required = set(KEYS) | {"unit_of_analysis"}
    missing = required - set(results.columns)
    if missing:
        raise ValueError(f"team_metrics output missing columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("team_metrics output is empty")
    if results.duplicated(KEYS).any():
        raise ValueError("team_metrics has duplicate team-semester keys")
    if not results["unit_of_analysis"].eq("team_semester").all():
        raise ValueError("team_metrics has an invalid observation unit")
    if any(column.startswith("ie_") for column in results.columns):
        raise ValueError("team_metrics must not contain replicated IE columns")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    exclusions_path = output_path.with_name("team_metrics_exclusions.json")
    if is_current_artifact(output_path, source_checksum):
        return
    if output_path.exists() or artifact_metadata_path(output_path).exists():
        raise ValueError("team_metrics artifact is immutable and stale")
    results.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="team-metrics-v1",
        options=options,
    )
    exclusions_payload = {
        "status": "success",
        "contract_version": "team-metrics-exclusions-v1",
        "input_checksum": source_checksum,
        "options": options,
        **exclusions,
    }
    if exclusions_path.exists():
        raise ValueError("team_metrics exclusions artifact is immutable and stale")
    exclusions_path.write_text(
        json.dumps(exclusions_payload, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def consolidate_team_metrics(
    contract_paths: dict[str, Path],
    *,
    output_path: Path,
    contract_report_path: Path,
    options: dict[str, Any],
) -> pd.DataFrame:
    """Read, validate, merge, and persist the four team metric contracts."""
    if not contract_report_path.exists():
        raise FileNotFoundError(f"Contract report not found: {contract_report_path}")
    report = json.loads(contract_report_path.read_text(encoding="utf-8"))
    if report.get("status") != "success":
        raise ValueError("Phase 2 contract report is not successful")
    for name, expected in report.get("contracts", {}).items():
        if name in {"git_commits", "git_team_cuts"}:
            expected_path = contract_report_path.parent.parent / "lake" / f"{name}.parquet"
            if expected_path.exists() and expected.get("input_checksum") != file_checksum(expected_path):
                raise ValueError(f"Phase 2 contract report is stale for {name}")
    loaded: list[pd.DataFrame] = []
    metadata_by_source: dict[str, dict[str, Any]] = {}
    contract_specs = {
        "planning": ("planning-metrics-v1", "pi_observation_unit"),
        "code_churn": ("code-churn-metrics-v1", "cc_observation_unit"),
        "technical_degradation": ("technical-degradation-metrics-v1", "dt_observation_unit"),
        "integration_friction": ("integration-friction-metrics-v1", "ai_observation_unit"),
    }
    for name, path in contract_paths.items():
        frame, metadata = _load_team_metric_contract(
            path,
            contract_version=contract_specs[name][0],
            unit_column=contract_specs[name][1],
        )
        loaded.append(frame)
        metadata_by_source[name] = metadata
    result = build_team_metrics(*loaded)
    result["team_metrics_contract_version"] = "team-metrics-v1"
    result["team_metrics_input_checksum"] = input_checksum(
        [
            *[path for path in contract_paths.values()],
            *[artifact_metadata_path(path) for path in contract_paths.values()],
            contract_report_path,
        ],
        options,
    )
    unavailable: dict[str, Any] = {}
    for name, frame in zip(contract_paths, loaded):
        availability_columns = [column for column in frame.columns if column.endswith("_available")]
        affected_keys: list[dict[str, Any]] = []
        unavailable_columns: dict[str, int] = {}
        for column in availability_columns:
            unavailable_mask = ~frame[column].fillna(False).astype(bool)
            unavailable_columns[column] = int(unavailable_mask.sum())
            reason_column = column.removesuffix("_available") + "_unavailable_reason"
            for row in frame.loc[unavailable_mask, KEYS + [reason_column] if reason_column in frame else KEYS].itertuples(index=False, name=None):
                key_values = dict(zip(KEYS, row[:len(KEYS)]))
                reason = row[-1] if reason_column in frame else "unavailable"
                affected_keys.append({
                    **key_values,
                    "metric": column.removesuffix("_available"),
                    "reason": reason or "unavailable",
                })
        unavailable[name] = {
            "rows": int(len(frame)),
            "unavailable_columns": unavailable_columns,
            "affected_keys": affected_keys,
        }
    checksum = result["team_metrics_input_checksum"].iloc[0]
    write_team_metrics(
        result,
        output_path,
        source_checksum=checksum,
        options={**options, "input_contracts": metadata_by_source},
        exclusions={
            "sources": unavailable,
            "ie_policy": "excluded_from_team_metrics; source_is_cut_context",
        },
    )
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()