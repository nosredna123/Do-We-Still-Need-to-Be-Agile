"""Cross-evidence extension computations."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

import pandas as pd
import plotly.graph_objects as plotly_go
from plotly.subplots import make_subplots
from scipy import stats as scipy_stats
from scipy.stats import spearmanr

from pipeline_config import (
    CROSS_EVIDENCE_ARTIFACT_REGISTRY,
    CROSS_EVIDENCE_CONTRACT_VERSION,
    CROSS_EVIDENCE_EXCLUSIONS_PATH,
    CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY,
    CROSS_EVIDENCE_MANIFEST_VERSION,
    FILE_CATEGORY_DEFINITION_VERSION,
    FILE_CATEGORY_RULES,
)
from pipeline_core import file_checksum, input_checksum, invalidate_stale_artifact, is_current_artifact, write_artifact_metadata


logger = logging.getLogger(__name__)
CROSS_EVIDENCE_ARTIFACT_REGISTRY = {
    artifact_id: dict(entry)
    for artifact_id, entry in CROSS_EVIDENCE_ARTIFACT_REGISTRY.items()
}


NORMAL_CONFIDENCE = 1.0
WARNING_CONFIDENCE = 0.8
UNKNOWN_CONFIDENCE = 0.5
FILE_CATEGORY_CHURN_CONTRACT_VERSION = CROSS_EVIDENCE_CONTRACT_VERSION
FILE_CATEGORY_EXCLUSIONS_CONTRACT_VERSION = CROSS_EVIDENCE_MANIFEST_VERSION
FILE_CATEGORY_EXCLUSIONS_SCHEMA_VERSION = "file-category-exclusions-v1"
EVALUATOR_OUTCOME_CONTRACT_VERSION = CROSS_EVIDENCE_CONTRACT_VERSION
AUTHOR_PRESSURE_CONTRACT_VERSION = CROSS_EVIDENCE_CONTRACT_VERSION
TEMPORAL_ESCALATION_CONTRACT_VERSION = CROSS_EVIDENCE_CONTRACT_VERSION
LATE_INSTABILITY_CONTRACT_VERSION = CROSS_EVIDENCE_CONTRACT_VERSION
CROSS_EVIDENCE_PANEL_CONTRACT_VERSION = CROSS_EVIDENCE_CONTRACT_VERSION
CROSS_EVIDENCE_CORRELATION_CONTRACT_VERSION = "cross-evidence-correlations-v1"
CROSS_EVIDENCE_BEST_WORST_CONTRACT_VERSION = "cross-evidence-best-worst-contrasts-v1"
CROSS_EVIDENCE_LEAVE_ONE_OUT_CONTRACT_VERSION = "cross-evidence-leave-one-out-v1"
CROSS_EVIDENCE_EXTREME_OVERLAP_CONTRACT_VERSION = "cross-evidence-extreme-overlap-v1"
CROSS_EVIDENCE_SEMESTER_STRATIFIED_CONTRACT_VERSION = "cross-evidence-semester-stratified-v1"
CROSS_EVIDENCE_PRIORITY_MATRIX_CONTRACT_VERSION = "cross-evidence-priority-matrix-v1"
CROSS_EVIDENCE_VISUAL_SPEC_VERSION = "cross-evidence-visual-spec-v1"
CROSS_EVIDENCE_FIGURE_CATEGORIES = ("prioritarias", "exploratorias", "dashboard_interativo")
CROSS_EVIDENCE_FIGURE_EXPORT_FORMATS = ("html", "png", "svg", "pdf")
CROSS_EVIDENCE_FIGURE_WIDTH = 1400
CROSS_EVIDENCE_FIGURE_HEIGHT = 850
CROSS_EVIDENCE_FIGURE_PNG_SCALE = 2
CROSS_EVIDENCE_VISUAL_PALETTE = {
    "scope": "#2563EB",
    "planning": "#D97706",
    "instability": "#DC2626",
    "author": "#15803D",
    "context": "#64748B",
    "unavailable": "#94A3B8",
}
CROSS_EVIDENCE_VISUAL_FONT = "Arial, sans-serif"
CROSS_EVIDENCE_VISUAL_ANONYMIZATION_POLICY = "public_visual_ranked_or_aggregate"
CUTS = ("T1", "T2", "T3")
TEAM_SEMESTER_KEYS = ["ID_Equipe", "Semestre"]
TEAM_SEMESTER_CUT_KEYS = ["ID_Equipe", "Semestre", "temporal_marker"]
TEMPORAL_ESCALATION_PAIR_SPECS = (("t1", "t2"), ("t2", "t3"), ("t1", "t3"))
TEMPORAL_ESCALATION_METRIC_SPECS = (
    {
        "metric_id": "planning_artifact_activity",
        "source_artifact": "planning_metrics",
        "columns": {"t1": "planning_artifact_activity_t1", "t2": "planning_artifact_activity_t2", "t3": "planning_artifact_activity_t3"},
        "narrative_acts": [2, 3],
    },
    {
        "metric_id": "pi_line_delta",
        "source_artifact": "planning_metrics",
        "columns": {"t1": "pi_line_delta_t1", "t2": "pi_line_delta_t2", "t3": "pi_line_delta_t3"},
        "narrative_acts": [2],
    },
    {
        "metric_id": "cc_total",
        "source_artifact": "code_churn_metrics",
        "columns": {"t1": "cc_total_t1", "t2": "cc_total_t2", "t3": "cc_total_t3"},
        "narrative_acts": [2, 3, 4],
    },
    {
        "metric_id": "cc_commit_n",
        "source_artifact": "code_churn_metrics",
        "columns": {"t1": "cc_commit_n_t1", "t2": "cc_commit_n_t2", "t3": "cc_commit_n_t3"},
        "narrative_acts": [2, 3],
    },
    {
        "metric_id": "technical_complexity_mean",
        "source_artifact": "technical_degradation_metrics",
        "columns": {"t1": "technical_complexity_mean_t1", "t2": "technical_complexity_mean_t2", "t3": "technical_complexity_mean_t3"},
        "narrative_acts": [2, 3],
    },
)
EVALUATOR_OUTCOME_METRICS = (
    "engagement_participation",
    "project_progress",
    "scope_applicability",
    "technical_complexity",
)
EVALUATOR_OUTCOME_FIELDS = ("mean", "median", "iqr", "std", "n")
EVALUATOR_OUTCOME_REQUIRED_COLUMNS = set(TEAM_SEMESTER_KEYS) | {"temporal_marker"} | {
    f"{metric}_{field}"
    for metric in EVALUATOR_OUTCOME_METRICS
    for field in EVALUATOR_OUTCOME_FIELDS
}
AUTHOR_PRESSURE_REQUIRED_COLUMNS = set(TEAM_SEMESTER_CUT_KEYS) | {
    "commit_hash",
    "ID_Autor_Local",
    "lines_added",
    "lines_deleted",
    "files_changed",
}
AUTHOR_PRESSURE_STATUS_LABELS = ("low", "moderate", "high", "critical")
LATE_INSTABILITY_TEAM_REQUIRED_COLUMNS = set(TEAM_SEMESTER_KEYS) | {
    "planning_rework_signal_t2_t3",
    "planning_artifact_activity_t3",
    "pi_line_delta_t3",
    "cc_total_t3",
    "cc_per_source_loc_t3",
    "delta_dt_t2_t3",
}
LATE_INSTABILITY_FILE_CATEGORY_REQUIRED_COLUMNS = set(TEAM_SEMESTER_CUT_KEYS) | {
    "file_category",
    "event_n",
    "churn_lines",
}
LATE_INSTABILITY_AUTHOR_REQUIRED_COLUMNS = set(TEAM_SEMESTER_CUT_KEYS) | {
    "commits_per_author",
    "commit_gini",
    "active_author_pressure_status",
    "churn_lines",
}
LATE_INSTABILITY_INDEX_COMPONENTS = (
    "planning_rework_signal_t2_t3",
    "planning_artifact_activity_t3",
    "pi_line_delta_t3",
    "source_churn_t3",
    "source_events_t3",
    "commits_per_author_t3",
    "delta_dt_t2_t3",
)
CROSS_EVIDENCE_PANEL_EVALUATOR_COLUMNS = [
    "project_progress_mean_t1",
    "project_progress_mean_t2",
    "project_progress_mean_t3",
    "project_progress_mean_delta_t1_t3",
    "scope_applicability_mean_t1",
    "scope_applicability_mean_t2",
    "scope_applicability_mean_t3",
    "scope_applicability_mean_delta_t1_t3",
    "technical_complexity_mean_t1",
    "technical_complexity_mean_t2",
    "technical_complexity_mean_t3",
    "technical_complexity_mean_delta_t1_t3",
    "engagement_participation_mean_t1",
    "engagement_participation_mean_t2",
    "engagement_participation_mean_t3",
    "engagement_participation_mean_delta_t1_t3",
    "progress_scope_gap_t1",
    "progress_scope_gap_t2",
    "progress_scope_gap_t3",
    "progress_scope_gap_delta_t1_t3",
    "evaluator_outcome_available",
]
CROSS_EVIDENCE_PANEL_LATE_COLUMNS = [
    "planning_rework_signal_t2_t3",
    "planning_artifact_activity_t3",
    "pi_line_delta_t3",
    "cc_total_t3",
    "cc_per_source_loc_t3",
    "source_churn_t3",
    "source_events_t3",
    "commits_per_author_t3",
    "commit_gini_t3",
    "active_author_pressure_status_t3",
    "author_churn_lines_t3",
    "delta_dt_t2_t3",
    "late_instability_index",
    "late_instability_component_available_n",
    "late_instability_component_missing_n",
]
CROSS_EVIDENCE_CORRELATION_REGISTRY = {
    "scope_vs_source_churn_t3": {
        "x": "source_churn_t3",
        "y": "scope_applicability_mean_t3",
        "priority": "primary_candidate",
        "expected_direction": "negative",
        "narrative_acts": [2, 3],
    },
    "scope_vs_source_events_t3": {
        "x": "source_events_t3",
        "y": "scope_applicability_mean_t3",
        "priority": "primary_candidate",
        "expected_direction": "negative",
        "narrative_acts": [2, 3],
    },
    "scope_vs_pi_line_delta_t3": {
        "x": "pi_line_delta_t3",
        "y": "scope_applicability_mean_t3",
        "priority": "primary_candidate",
        "expected_direction": "negative",
        "narrative_acts": [2, 3],
    },
    "scope_vs_planning_artifact_activity_t3": {
        "x": "planning_artifact_activity_t3",
        "y": "scope_applicability_mean_t3",
        "priority": "primary_candidate",
        "expected_direction": "negative",
        "narrative_acts": [2, 3],
    },
    "scope_vs_planning_rework_t2_t3": {
        "x": "planning_rework_signal_t2_t3",
        "y": "scope_applicability_mean_t3",
        "priority": "primary_candidate",
        "expected_direction": "negative",
        "narrative_acts": [2, 3],
    },
    "scope_vs_commits_per_author_t3": {
        "x": "commits_per_author_t3",
        "y": "scope_applicability_mean_t3",
        "priority": "primary_candidate",
        "expected_direction": "negative",
        "narrative_acts": [3],
    },
    "scope_vs_late_instability_index": {
        "x": "late_instability_index",
        "y": "scope_applicability_mean_t3",
        "priority": "secondary_support",
        "expected_direction": "negative",
        "narrative_acts": [2, 3],
    },
}
CROSS_EVIDENCE_BEST_WORST_SCORE_VARIABLES = (
    "scope_applicability_mean_t3",
    "project_progress_mean_t3",
    "late_instability_index",
)
CROSS_EVIDENCE_BEST_WORST_OUTCOME_VARIABLES = (
    "planning_rework_signal_t2_t3",
    "planning_artifact_activity_t3",
    "pi_line_delta_t3",
    "source_churn_t3",
    "source_events_t3",
    "commits_per_author_t3",
    "late_instability_index",
    "scope_applicability_mean_t3",
)
CROSS_EVIDENCE_BEST_WORST_GROUP_SIZE = 4
CROSS_EVIDENCE_EXTREME_OVERLAP_VARIABLES = (
    "planning_rework_signal_t2_t3",
    "source_churn_t3",
    "commits_per_author_t3",
    "scope_applicability_mean_t3",
)
CROSS_EVIDENCE_EXTREME_OVERLAP_GROUP_SIZE = 4
CROSS_EVIDENCE_EXTREME_OVERLAP_MODES = ("top_top", "top_bottom", "bottom_bottom")
CROSS_EVIDENCE_SEMESTER_STRATA = ("global", "2025.2", "2026.1")
EVIDENCE_PRIORITY_SOURCE_ARTIFACTS = (
    "cross_evidence_correlations",
    "best_worst_project_contrasts",
    "leave_one_out_sensitivity",
    "extreme_case_overlap",
    "semester_stratified_results",
)
FILE_CATEGORY_CHURN_REQUIRED_COLUMNS = {
    "ID_Equipe",
    "Semestre",
    "temporal_marker",
    "file_path",
    "file_path_old",
    "file_extension",
    "change_status",
    "lines_added",
    "lines_deleted",
    "is_binary",
}
FILE_CATEGORY_CHURN_GROUP_COLUMNS = ["ID_Equipe", "Semestre", "temporal_marker", "file_category"]
EXCLUSIONS_AFFECTED_KEY_SAMPLE_LIMIT = 50
RUNTIME_PATHS = {
    "analysis": Path("data/analysis"),
    "lake": Path("data/lake"),
}
DEFAULT_REGISTRY_PATHS = {
    artifact_id: str(entry["path"])
    for artifact_id, entry in CROSS_EVIDENCE_ARTIFACT_REGISTRY.items()
    if "path" in entry
}


def _resolve_runtime_path(value: str | Path) -> Path:
    """Resolve configured data paths against the active CLI roots."""
    path = Path(value)
    normalized = path.as_posix()
    if normalized.startswith("data/analysis/"):
        return RUNTIME_PATHS["analysis"] / normalized[len("data/analysis/"):]
    if normalized == "data/analysis":
        return RUNTIME_PATHS["analysis"]
    if normalized.startswith("data/lake/"):
        return RUNTIME_PATHS["lake"] / normalized[len("data/lake/"):]
    if normalized == "data/lake":
        return RUNTIME_PATHS["lake"]
    return path


def _configure_runtime_paths(*, analysis_dir: Path, lake_dir: Path) -> None:
    """Apply CLI roots to registry paths used by legacy builder functions."""
    RUNTIME_PATHS["analysis"] = analysis_dir
    RUNTIME_PATHS["lake"] = lake_dir
    for artifact_id, entry in CROSS_EVIDENCE_ARTIFACT_REGISTRY.items():
        if artifact_id in DEFAULT_REGISTRY_PATHS:
            entry["path"] = _resolve_runtime_path(DEFAULT_REGISTRY_PATHS[artifact_id]).as_posix()


def cross_evidence_visual_spec(
    figure_id: str,
    *,
    category: str = "exploratorias",
    variables: list[str] | None = None,
    required: bool = False,
) -> dict[str, object]:
    """Return the shared, versioned visual specification for one figure."""
    if not figure_id.strip():
        raise ValueError("figure_id must not be empty")
    if category not in CROSS_EVIDENCE_FIGURE_CATEGORIES:
        raise ValueError(f"Unknown cross-evidence figure category: {category}")
    export_formats = list(CROSS_EVIDENCE_FIGURE_EXPORT_FORMATS)
    if not required:
        export_formats.remove("pdf")
    return {
        "visual_spec_version": CROSS_EVIDENCE_VISUAL_SPEC_VERSION,
        "figure_id": figure_id,
        "category": category,
        "required": required,
        "theme": "plotly_white",
        "font_family": CROSS_EVIDENCE_VISUAL_FONT,
        "width": CROSS_EVIDENCE_FIGURE_WIDTH,
        "height": CROSS_EVIDENCE_FIGURE_HEIGHT,
        "png_scale": CROSS_EVIDENCE_FIGURE_PNG_SCALE,
        "palette": dict(CROSS_EVIDENCE_VISUAL_PALETTE),
        "variables": list(variables or []),
        "scale_default": "linear",
        "log_scale_policy": "use_log_only_when_positive_dynamic_range_exceeds_100x",
        "anonymization_policy": CROSS_EVIDENCE_VISUAL_ANONYMIZATION_POLICY,
        "export_formats": export_formats,
    }


def apply_cross_evidence_visual_theme(
    figure: plotly_go.Figure,
    *,
    title: str | None = None,
) -> plotly_go.Figure:
    """Apply the shared Plotly theme and publication dimensions in place."""
    figure.update_layout(
        template="plotly_white",
        width=CROSS_EVIDENCE_FIGURE_WIDTH,
        height=CROSS_EVIDENCE_FIGURE_HEIGHT,
        font={"family": CROSS_EVIDENCE_VISUAL_FONT, "color": "#1E293B"},
        title={"text": title, "x": 0.02, "xanchor": "left"} if title else None,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        margin={"l": 80, "r": 40, "t": 80, "b": 80},
        hoverlabel={"font": {"family": CROSS_EVIDENCE_VISUAL_FONT}},
    )
    figure.update_xaxes(showgrid=False, zeroline=False, linecolor="#CBD5E1")
    figure.update_yaxes(showgrid=True, gridcolor="#E2E8F0", zeroline=False, linecolor="#CBD5E1")
    return figure


def choose_cross_evidence_scale(values: pd.Series) -> dict[str, object]:
    """Choose linear or log display without applying a lossy transformation."""
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    positive = numeric[numeric > 0]
    if positive.empty:
        return {
            "scale": "linear",
            "reason": "non_positive_values_present_or_no_positive_values",
            "dynamic_range": None,
        }
    dynamic_range = float(positive.max() / positive.min())
    if len(positive) == len(numeric) and dynamic_range > 100:
        return {
            "scale": "log",
            "reason": "positive_dynamic_range_exceeds_100x",
            "dynamic_range": dynamic_range,
        }
    return {
        "scale": "linear",
        "reason": "default_linear_or_dynamic_range_within_100x",
        "dynamic_range": dynamic_range,
    }


def anonymize_cross_evidence_visual_data(
    frame: pd.DataFrame,
    *,
    team_column: str = "ID_Equipe",
    output_column: str = "anonymized_team_id",
) -> pd.DataFrame:
    """Return visual data with stable public team IDs and no raw identifiers."""
    if team_column not in frame.columns:
        raise ValueError(f"Visual data missing team identifier column: {team_column}")
    result = frame.copy()
    identifiers = sorted(result[team_column].dropna().astype(str).unique())
    mapping = {identifier: f"TEAM_{index:02d}" for index, identifier in enumerate(identifiers, start=1)}
    result[output_column] = result[team_column].map(mapping)
    if output_column != team_column:
        result = result.drop(columns=[team_column])
    return result


def cross_evidence_figure_export_paths(
    figure_id: str,
    *,
    category: str = "exploratorias",
    figure_root: Path | None = None,
    figure_data_root: Path | None = None,
) -> dict[str, Path]:
    """Return stable data and publication paths for a cross-evidence figure."""
    if category not in CROSS_EVIDENCE_FIGURE_CATEGORIES:
        raise ValueError(f"Unknown cross-evidence figure category: {category}")
    figure_root = figure_root or Path("assets/figures/cross_evidence")
    figure_data_root = figure_data_root or RUNTIME_PATHS["analysis"] / "cross_evidence/figure_data"
    directory = figure_root / category
    data_path = figure_data_root / f"{figure_id}.csv"
    return {
        "data": data_path,
        "html": directory / f"{figure_id}.html",
        "png": directory / f"{figure_id}.png",
        "svg": directory / f"{figure_id}.svg",
        "pdf": directory / f"{figure_id}.pdf",
        "plotly_json": directory / f"{figure_id}.plotly.json",
    }


def build_cross_evidence_figure_manifest_entry(
    figure: plotly_go.Figure,
    data: pd.DataFrame,
    *,
    figure_id: str,
    category: str,
    source: str,
    unit_of_analysis: str,
    variables: list[str],
    transformations: list[str] | None = None,
    scale_notes: list[str] | None = None,
    limitations: list[str] | None = None,
    paths: dict[str, Path] | None = None,
    required: bool = False,
) -> dict[str, object]:
    """Build a manifest-ready figure entry after the caller writes exports."""
    spec = cross_evidence_visual_spec(
        figure_id,
        category=category,
        variables=variables,
        required=required,
    )
    paths = paths or cross_evidence_figure_export_paths(figure_id, category=category)
    existing_checksums = {
        key: file_checksum(path)
        for key, path in paths.items()
        if path.is_file() and key != "html"
    }
    available_static_paths = {
        key: path.as_posix()
        for key, path in paths.items()
        if key in {"png", "svg", "pdf"} and path.is_file()
    }
    valid = data.dropna(subset=[column for column in variables if column in data]) if variables and all(column in data for column in variables) else data
    return {
        "figure_id": figure_id,
        "category": category,
        "priority": "required" if required else "exploratory",
        "status": "success",
        "source": source,
        "unit_of_analysis": unit_of_analysis,
        "variables": variables,
        "visual_spec_version": spec["visual_spec_version"],
        "theme": spec["theme"],
        "dimensions": {"width": spec["width"], "height": spec["height"], "png_scale": spec["png_scale"]},
        "anonymization_policy": spec["anonymization_policy"],
        "transformations": transformations or [],
        "scale_notes": scale_notes or [],
        "limitations": limitations or [],
        "n_total": int(len(data)),
        "n_valid": int(len(valid)),
        "n_missing": int(len(data) - len(valid)),
        "plotly_trace_n": len(figure.data),
        "data_path": paths["data"].as_posix(),
        "data_metadata_path": f"{paths['data'].as_posix()}.metadata.json",
        "interactive_path": paths["html"].as_posix(),
        "static_paths": available_static_paths,
        "checksums": existing_checksums,
        "export_formats": spec["export_formats"],
    }


SCOPE_LATE_INSTABILITY_FIGURE_SPECS = (
    {
        "plot_id": "scope_vs_late_instability_index",
        "y": "late_instability_index",
        "title": "Late instability index",
        "y_title": "Late instability index",
        "y_scale": "linear",
    },
    {
        "plot_id": "scope_vs_source_churn_t3",
        "y": "source_churn_t3",
        "title": "Source churn at T3",
        "y_title": "Source churn (lines, log scale)",
        "y_scale": "log",
    },
    {
        "plot_id": "scope_vs_planning_artifact_activity_t3",
        "y": "planning_artifact_activity_t3",
        "title": "Planning artifact activity at T3",
        "y_title": "Planning artifact activity (log scale)",
        "y_scale": "log",
    },
    {
        "plot_id": "scope_vs_commits_per_author_t3",
        "y": "commits_per_author_t3",
        "title": "Commits per author at T3",
        "y_title": "Commits per author",
        "y_scale": "linear",
    },
)
SCOPE_LATE_INSTABILITY_SEMESTER_COLORS = {
    "2025.2": "#2563EB",
    "2026.1": "#D97706",
}
SOURCE_CHURN_PLANNING_REWORK_SEMESTER_COLORS = SCOPE_LATE_INSTABILITY_SEMESTER_COLORS
TEMPORAL_ESCALATION_FIGURE_METRICS = (
    {
        "metric_id": "planning_artifact_activity",
        "source": "temporal_escalation_metrics",
        "columns": {"T1": "mean_t1", "T2": "mean_t2", "T3": "mean_t3"},
        "title": "Planning artifact activity",
    },
    {
        "metric_id": "pi_line_delta",
        "source": "temporal_escalation_metrics",
        "columns": {"T1": "mean_t1", "T2": "mean_t2", "T3": "mean_t3"},
        "title": "Planning artifact line delta",
    },
    {
        "metric_id": "cc_total",
        "source": "temporal_escalation_metrics",
        "columns": {"T1": "mean_t1", "T2": "mean_t2", "T3": "mean_t3"},
        "title": "Total churn",
    },
    {
        "metric_id": "cc_commit_n",
        "source": "temporal_escalation_metrics",
        "columns": {"T1": "mean_t1", "T2": "mean_t2", "T3": "mean_t3"},
        "title": "Commit count",
    },
    {
        "metric_id": "technical_complexity_mean",
        "source": "temporal_escalation_metrics",
        "columns": {"T1": "mean_t1", "T2": "mean_t2", "T3": "mean_t3"},
        "title": "Technical complexity",
    },
    {
        "metric_id": "project_progress",
        "source": "evaluator_outcome_metrics",
        "columns": {"T1": "project_progress_mean_t1", "T2": "project_progress_mean_t2", "T3": "project_progress_mean_t3"},
        "title": "Perceived project progress",
    },
)
FILE_CATEGORY_CHURN_FIGURE_CATEGORIES = (
    "source",
    "planning",
    "generated",
    "config",
    "localization",
    "asset",
    "test",
    "unknown",
)
FILE_CATEGORY_CHURN_FIGURE_COLORS = {
    "source": "#2563EB",
    "planning": "#D97706",
    "generated": "#DC2626",
    "config": "#7C3AED",
    "localization": "#DB2777",
    "asset": "#059669",
    "test": "#0891B2",
    "unknown": "#64748B",
}
AUTHOR_PRESSURE_FIGURE_SPECS = (
    {
        "plot_id": "author_pressure_vs_source_churn_t3",
        "y": "source_churn_t3",
        "title": "Source churn at T3",
        "y_title": "Source churn (lines, log scale)",
    },
    {
        "plot_id": "author_pressure_vs_planning_rework_t2_t3",
        "y": "planning_rework_signal_t2_t3",
        "title": "Late planning rework",
        "y_title": "Planning rework signal (log scale)",
    },
    {
        "plot_id": "author_pressure_vs_planning_activity_t3",
        "y": "planning_artifact_activity_t3",
        "title": "Planning artifact activity at T3",
        "y_title": "Planning activity (log scale)",
    },
)
PARETO_EXTREME_CASES_COLORSCALE = [[0.0, "#F8FAFC"], [0.5, "#93C5FD"], [1.0, "#1D4ED8"]]
LEAVE_ONE_OUT_ROBUSTNESS_COLORS = {
    "robust_all": "#15803D",
    "robust_most": "#2563EB",
    "fragile": "#D97706",
    "no_support": "#64748B",
}


def compute_scope_vs_late_instability_figure_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Prepare anonymized long-form data for the CE-4.2 subplot figure."""
    required = {"ID_Equipe", "Semestre", "scope_applicability_mean_t3"} | {
        str(spec["y"]) for spec in SCOPE_LATE_INSTABILITY_FIGURE_SPECS
    }
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"cross_evidence_panel missing columns: {sorted(missing)}")
    working = anonymize_cross_evidence_visual_data(
        panel[["ID_Equipe", "Semestre", "scope_applicability_mean_t3", *[str(spec["y"]) for spec in SCOPE_LATE_INSTABILITY_FIGURE_SPECS]]]
    )
    rows: list[dict[str, object]] = []
    for spec in SCOPE_LATE_INSTABILITY_FIGURE_SPECS:
        y_name = str(spec["y"])
        for row in working.to_dict("records"):
            x_value = pd.to_numeric(row["scope_applicability_mean_t3"], errors="coerce")
            y_value = pd.to_numeric(row[y_name], errors="coerce")
            rows.append(
                {
                    "figure_id": "scope_vs_late_instability",
                    "plot_id": spec["plot_id"],
                    "anonymized_team_id": row["anonymized_team_id"],
                    "semester": row["Semestre"],
                    "x": "scope_applicability_mean_t3",
                    "x_value": x_value,
                    "y": y_name,
                    "y_value": y_value,
                    "x_scale": "linear",
                    "y_scale": spec["y_scale"],
                    "transformation": "complete_case_pair",
                }
            )
    return pd.DataFrame(rows)


def _scope_late_instability_figure(
    figure_data: pd.DataFrame,
) -> plotly_go.Figure:
    """Build the CE-4.2 four-panel Plotly figure from prepared data."""
    figure = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[str(spec["title"]) for spec in SCOPE_LATE_INSTABILITY_FIGURE_SPECS],
        horizontal_spacing=0.12,
        vertical_spacing=0.16,
    )
    for panel_index, spec in enumerate(SCOPE_LATE_INSTABILITY_FIGURE_SPECS):
        row_index = panel_index // 2 + 1
        column_index = panel_index % 2 + 1
        subset = figure_data.loc[figure_data["plot_id"] == spec["plot_id"]]
        for semester in sorted(subset["semester"].dropna().astype(str).unique()):
            points = subset.loc[subset["semester"].astype(str) == semester].dropna(subset=["x_value", "y_value"])
            figure.add_trace(
                plotly_go.Scatter(
                    x=points["x_value"],
                    y=points["y_value"],
                    mode="markers",
                    name=semester,
                    legendgroup=semester,
                    showlegend=panel_index == 0,
                    marker={"size": 10, "color": SCOPE_LATE_INSTABILITY_SEMESTER_COLORS.get(semester, CROSS_EVIDENCE_VISUAL_PALETTE["context"]), "line": {"width": 0.8, "color": "#FFFFFF"}},
                    customdata=points[["anonymized_team_id", "semester"]],
                    hovertemplate="%{customdata[0]} (%{customdata[1]})<br>Scope applicability: %{x}<br>Value: %{y}<extra></extra>",
                ),
                row=row_index,
                col=column_index,
            )
        figure.update_xaxes(
            title_text="Scope applicability at T3",
            row=row_index,
            col=column_index,
        )
        figure.update_yaxes(
            title_text=str(spec["y_title"]),
            type="log" if spec["y_scale"] == "log" else "linear",
            row=row_index,
            col=column_index,
        )
    apply_cross_evidence_visual_theme(figure, title="Scope applicability and late instability")
    return figure


def build_scope_vs_late_instability_figure(
    *,
    output_data_path: Path | None = None,
    figure_root: Path = Path("assets/figures/cross_evidence"),
    figure_data_root: Path = Path("data/analysis/cross_evidence/figure_data"),
    force: bool = False,
) -> pd.DataFrame:
    """Build or load CE-4.2 figure data and publication exports."""
    panel_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_panel"]["path"]))
    _require_success_sidecar(panel_path)
    panel_sidecar = panel_path.with_name(f"{panel_path.name}.metadata.json")
    paths = cross_evidence_figure_export_paths(
        "scope_vs_late_instability",
        category="prioritarias",
        figure_root=figure_root,
        figure_data_root=figure_data_root,
    )
    output_data_path = output_data_path or paths["data"]
    options = {
        "stage": "scope_vs_late_instability",
        "visual_spec_version": CROSS_EVIDENCE_VISUAL_SPEC_VERSION,
        "subplot_specs": SCOPE_LATE_INSTABILITY_FIGURE_SPECS,
        "semester_colors": SCOPE_LATE_INSTABILITY_SEMESTER_COLORS,
        "anonymization_policy": CROSS_EVIDENCE_VISUAL_ANONYMIZATION_POLICY,
        "export_formats": list(CROSS_EVIDENCE_FIGURE_EXPORT_FORMATS),
    }
    checksum = input_checksum([panel_path, panel_sidecar], options)
    export_paths = dict(paths)
    export_paths["data"] = output_data_path
    manifest_path = output_data_path.with_name(f"{output_data_path.stem}.manifest.json")
    output_paths_ready = all(export_paths[key].is_file() for key in ("html", "png", "svg", "pdf")) and manifest_path.is_file()
    if force:
        invalidate_stale_artifact(output_data_path, "force-regeneration")
    if not force and output_paths_ready and is_current_artifact(output_data_path, checksum):
        logger.info("Scope versus late instability figure is current: %s", output_data_path)
        return pd.read_csv(output_data_path)

    figure_data = compute_scope_vs_late_instability_figure_data(pd.read_parquet(panel_path))
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    figure_data.to_csv(output_data_path, index=False)
    write_artifact_metadata(
        output_data_path,
        checksum,
        contract_version="cross-evidence-figure-data-v1",
        options=options,
    )
    figure = _scope_late_instability_figure(figure_data)
    for path in (export_paths["html"], export_paths["png"], export_paths["svg"], export_paths["pdf"]):
        path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(export_paths["html"], include_plotlyjs="cdn", full_html=True)
    figure.write_image(export_paths["png"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT, scale=CROSS_EVIDENCE_FIGURE_PNG_SCALE)
    figure.write_image(export_paths["svg"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_image(export_paths["pdf"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_json(export_paths["plotly_json"])
    manifest_entry = build_cross_evidence_figure_manifest_entry(
        figure,
        figure_data,
        figure_id="scope_vs_late_instability",
        category="prioritarias",
        source=panel_path.as_posix(),
        unit_of_analysis="team_semester",
        variables=["scope_applicability_mean_t3", "late_instability_index", "source_churn_t3", "planning_artifact_activity_t3", "commits_per_author_t3"],
        transformations=["complete_case_pair", "anonymize_team_id", "four_subplot_panel", "log_y_source_churn_and_planning_activity"],
        scale_notes=["scope and late instability linear", "source churn and planning activity logarithmic", "commits per author linear"],
        limitations=["observational association", "team-semester sample n=14", "semester 2026.1 has n=5"],
        paths=export_paths,
        required=True,
    )
    manifest_entry["data_metadata_path"] = f"{output_data_path.as_posix()}.metadata.json"
    manifest_path.write_text(json.dumps(manifest_entry, indent=2, sort_keys=True, default=str), encoding="utf-8")
    logger.info("Wrote scope versus late instability figure: %s", export_paths["png"])
    return figure_data


def compute_source_churn_vs_planning_rework_figure_data(late_instability: pd.DataFrame) -> pd.DataFrame:
    """Prepare anonymized data for the source-churn versus rework figure."""
    required = {
        "ID_Equipe",
        "Semestre",
        "planning_rework_signal_t2_t3",
        "source_churn_t3",
    }
    missing = required - set(late_instability.columns)
    if missing:
        raise ValueError(f"late_instability_metrics missing columns: {sorted(missing)}")
    working = anonymize_cross_evidence_visual_data(
        late_instability[["ID_Equipe", "Semestre", "planning_rework_signal_t2_t3", "source_churn_t3"]]
    )
    working["planning_rework_signal_t2_t3"] = pd.to_numeric(working["planning_rework_signal_t2_t3"], errors="coerce")
    working["source_churn_t3"] = pd.to_numeric(working["source_churn_t3"], errors="coerce")
    working = working.dropna(subset=["planning_rework_signal_t2_t3", "source_churn_t3"])
    if (working[["planning_rework_signal_t2_t3", "source_churn_t3"]] <= 0).any().any():
        raise ValueError("source churn and planning rework must be positive for log scales")
    return working.rename(
        columns={
            "planning_rework_signal_t2_t3": "x_value",
            "source_churn_t3": "y_value",
        }
    ).assign(
        figure_id="source_churn_vs_planning_rework",
        x="planning_rework_signal_t2_t3",
        y="source_churn_t3",
        x_scale="log",
        y_scale="log",
        transformation="complete_case_pair|source_category_only",
    )[
        [
            "figure_id",
            "anonymized_team_id",
            "Semestre",
            "x",
            "x_value",
            "y",
            "y_value",
            "x_scale",
            "y_scale",
            "transformation",
        ]
    ].rename(columns={"Semestre": "semester"})


def _source_churn_vs_planning_rework_figure(figure_data: pd.DataFrame) -> plotly_go.Figure:
    """Build the CE-4.3 log-log scatter figure."""
    figure = plotly_go.Figure()
    for semester in sorted(figure_data["semester"].astype(str).unique()):
        points = figure_data.loc[figure_data["semester"].astype(str) == semester]
        figure.add_trace(
            plotly_go.Scatter(
                x=points["x_value"],
                y=points["y_value"],
                mode="markers",
                name=semester,
                marker={
                    "size": 11,
                    "color": SOURCE_CHURN_PLANNING_REWORK_SEMESTER_COLORS.get(semester, CROSS_EVIDENCE_VISUAL_PALETTE["context"]),
                    "line": {"width": 0.8, "color": "#FFFFFF"},
                },
                customdata=points[["anonymized_team_id", "semester"]],
                hovertemplate="%{customdata[0]} (%{customdata[1]})<br>Planning rework: %{x}<br>Source churn: %{y}<extra></extra>",
            )
        )
    apply_cross_evidence_visual_theme(figure, title="Source churn versus late planning rework")
    figure.update_xaxes(
        title_text="Late planning rework signal (T2-T3, log scale)",
        type="log",
        showgrid=True,
        gridcolor="#E2E8F0",
    )
    figure.update_yaxes(
        title_text="Source churn at T3 (lines, log scale)",
        type="log",
        showgrid=True,
        gridcolor="#E2E8F0",
    )
    return figure


def build_source_churn_vs_planning_rework_figure(
    *,
    output_data_path: Path | None = None,
    figure_root: Path = Path("assets/figures/cross_evidence"),
    figure_data_root: Path = Path("data/analysis/cross_evidence/figure_data"),
    force: bool = False,
) -> pd.DataFrame:
    """Build or load CE-4.3 figure data and publication exports."""
    source_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["late_instability_metrics"]["path"]))
    _require_success_sidecar(source_path)
    source_sidecar = source_path.with_name(f"{source_path.name}.metadata.json")
    paths = cross_evidence_figure_export_paths(
        "source_churn_vs_planning_rework",
        category="prioritarias",
        figure_root=figure_root,
        figure_data_root=figure_data_root,
    )
    output_data_path = output_data_path or paths["data"]
    export_paths = dict(paths)
    export_paths["data"] = output_data_path
    options = {
        "stage": "source_churn_vs_planning_rework",
        "visual_spec_version": CROSS_EVIDENCE_VISUAL_SPEC_VERSION,
        "x": "planning_rework_signal_t2_t3",
        "y": "source_churn_t3",
        "x_scale": "log",
        "y_scale": "log",
        "source_policy": "file_category_source_only_t3",
        "anonymization_policy": CROSS_EVIDENCE_VISUAL_ANONYMIZATION_POLICY,
        "export_formats": list(CROSS_EVIDENCE_FIGURE_EXPORT_FORMATS),
    }
    checksum = input_checksum([source_path, source_sidecar], options)
    manifest_path = output_data_path.with_name(f"{output_data_path.stem}.manifest.json")
    output_paths_ready = all(export_paths[key].is_file() for key in ("html", "png", "svg", "pdf")) and manifest_path.is_file()
    if force:
        invalidate_stale_artifact(output_data_path, "force-regeneration")
    if not force and output_paths_ready and is_current_artifact(output_data_path, checksum):
        logger.info("Source churn versus planning rework figure is current: %s", output_data_path)
        return pd.read_csv(output_data_path)

    figure_data = compute_source_churn_vs_planning_rework_figure_data(pd.read_parquet(source_path))
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    figure_data.to_csv(output_data_path, index=False)
    write_artifact_metadata(
        output_data_path,
        checksum,
        contract_version="cross-evidence-figure-data-v1",
        options=options,
    )
    figure = _source_churn_vs_planning_rework_figure(figure_data)
    for path in (export_paths["html"], export_paths["png"], export_paths["svg"], export_paths["pdf"]):
        path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(export_paths["html"], include_plotlyjs="cdn", full_html=True)
    figure.write_image(export_paths["png"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT, scale=CROSS_EVIDENCE_FIGURE_PNG_SCALE)
    figure.write_image(export_paths["svg"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_image(export_paths["pdf"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_json(export_paths["plotly_json"])
    manifest_entry = build_cross_evidence_figure_manifest_entry(
        figure,
        figure_data,
        figure_id="source_churn_vs_planning_rework",
        category="prioritarias",
        source=source_path.as_posix(),
        unit_of_analysis="team_semester",
        variables=["planning_rework_signal_t2_t3", "source_churn_t3"],
        transformations=["complete_case_pair", "source_category_only_t3", "anonymize_team_id", "log_x", "log_y"],
        scale_notes=["positive heavy-tailed variables shown on logarithmic axes"],
        limitations=["observational association", "team-semester sample n=14", "source churn excludes non-source file categories"],
        paths=export_paths,
        required=True,
    )
    manifest_entry["data_metadata_path"] = f"{output_data_path.as_posix()}.metadata.json"
    manifest_path.write_text(json.dumps(manifest_entry, indent=2, sort_keys=True, default=str), encoding="utf-8")
    logger.info("Wrote source churn versus planning rework figure: %s", export_paths["png"])
    return figure_data


def compute_temporal_escalation_figure_data(
    temporal_metrics: pd.DataFrame,
    evaluator_outcomes: pd.DataFrame,
    semester_source_frames: dict[str, pd.DataFrame] | None = None,
) -> pd.DataFrame:
    """Prepare T1/T2/T3 values and T1-relative indices for CE-4.4."""
    rows: list[dict[str, object]] = []
    for spec in TEMPORAL_ESCALATION_FIGURE_METRICS:
        source_name = str(spec["source"])
        frame = temporal_metrics if source_name == "temporal_escalation_metrics" else evaluator_outcomes
        metric_id = str(spec["metric_id"])
        if source_name == "temporal_escalation_metrics":
            required = {"metric_id", *dict(spec["columns"]).values()}
            missing = required - set(frame.columns)
            if missing:
                raise ValueError(f"{source_name} missing columns: {sorted(missing)}")
            matches = frame.loc[frame["metric_id"] == metric_id]
            if len(matches) != 1:
                raise ValueError(f"{source_name} must contain exactly one row for metric_id: {metric_id}")
            source_row = matches.iloc[0]
            values = {cut: pd.to_numeric(source_row[column], errors="coerce") for cut, column in dict(spec["columns"]).items()}
            n_valid = {cut: int(source_row.get(f"n_valid_{cut.lower()}", 0)) for cut in ("T1", "T2", "T3")}
        else:
            required = {"Semestre", *dict(spec["columns"]).values()}
            missing = required - set(frame.columns)
            if missing:
                raise ValueError(f"{source_name} missing columns: {sorted(missing)}")
            series_values = {cut: pd.to_numeric(frame[column], errors="coerce") for cut, column in dict(spec["columns"]).items()}
            values = {cut: (float(series.mean()) if series.notna().any() else pd.NA) for cut, series in series_values.items()}
            n_valid = {cut: int(series_values[cut].notna().sum()) for cut in ("T1", "T2", "T3")}
        baseline = values["T1"]
        for cut in ("T1", "T2", "T3"):
            current = values[cut]
            relative = current / baseline if pd.notna(baseline) and baseline != 0 else pd.NA
            rows.append(
                {
                    "figure_id": "temporal_escalation_panel",
                    "metric_id": metric_id,
                    "metric_title": spec["title"],
                    "source_artifact": source_name,
                    "temporal_marker": cut,
                    "series": "global",
                    "semester": pd.NA,
                    "aggregation": "source_mean" if source_name == "temporal_escalation_metrics" else "all_team_semester_mean",
                    "value_raw": current,
                    "baseline_t1": baseline,
                    "value_relative_t1": relative,
                    "n_valid": n_valid[cut],
                    "transformation": "relative_to_t1_baseline",
                }
            )
        if source_name == "temporal_escalation_metrics" and semester_source_frames is not None:
            source_artifact = str(next(item["source_artifact"] for item in TEMPORAL_ESCALATION_METRIC_SPECS if item["metric_id"] == metric_id))
            source_frame = semester_source_frames.get(source_artifact)
            if source_frame is None:
                raise ValueError(f"Missing semester source frame: {source_artifact}")
            source_spec = next(item for item in TEMPORAL_ESCALATION_METRIC_SPECS if item["metric_id"] == metric_id)
            source_columns = dict(source_spec["columns"])
            required_source = set(TEAM_SEMESTER_KEYS) | set(source_columns.values())
            missing_source = required_source - set(source_frame.columns)
            if missing_source:
                raise ValueError(f"{source_artifact} missing columns: {sorted(missing_source)}")
            for semester, group in source_frame.groupby("Semestre", dropna=False):
                semester_values = {
                    cut: pd.to_numeric(group[column], errors="coerce")
                    for cut, column in source_columns.items()
                }
                semester_means = {
                    cut: float(values_series.mean()) if values_series.notna().any() else pd.NA
                    for cut, values_series in semester_values.items()
                }
                semester_baseline = semester_means["t1"]
                for cut in ("t1", "t2", "t3"):
                    current = semester_means[cut]
                    relative = current / semester_baseline if pd.notna(semester_baseline) and semester_baseline != 0 else pd.NA
                    rows.append(
                        {
                            "figure_id": "temporal_escalation_panel",
                            "metric_id": metric_id,
                            "metric_title": spec["title"],
                            "source_artifact": source_name,
                            "temporal_marker": cut.upper(),
                            "series": "semester",
                            "semester": semester,
                            "aggregation": "semester_mean",
                            "value_raw": current,
                            "baseline_t1": semester_baseline,
                            "value_relative_t1": relative,
                            "n_valid": int(semester_values[cut].notna().sum()),
                            "transformation": "relative_to_t1_baseline",
                        }
                    )
        if source_name == "evaluator_outcome_metrics":
            for semester, group in frame.groupby("Semestre", dropna=False):
                semester_values = {cut: pd.to_numeric(group[column], errors="coerce") for cut, column in dict(spec["columns"]).items()}
                semester_means = {cut: float(values_series.mean()) if values_series.notna().any() else pd.NA for cut, values_series in semester_values.items()}
                semester_baseline = semester_means["T1"]
                for cut in ("T1", "T2", "T3"):
                    current = semester_means[cut]
                    relative = current / semester_baseline if pd.notna(semester_baseline) and semester_baseline != 0 else pd.NA
                    rows.append(
                        {
                            "figure_id": "temporal_escalation_panel",
                            "metric_id": metric_id,
                            "metric_title": spec["title"],
                            "source_artifact": source_name,
                            "temporal_marker": cut,
                            "series": "semester",
                            "semester": semester,
                            "aggregation": "semester_mean",
                            "value_raw": current,
                            "baseline_t1": semester_baseline,
                            "value_relative_t1": relative,
                            "n_valid": int(semester_values[cut].notna().sum()),
                            "transformation": "relative_to_t1_baseline",
                        }
                    )
    return pd.DataFrame(rows)


def _temporal_escalation_figure(figure_data: pd.DataFrame) -> plotly_go.Figure:
    """Build the CE-4.4 six-panel relative T1 escalation figure."""
    figure = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=[str(spec["title"]) for spec in TEMPORAL_ESCALATION_FIGURE_METRICS],
        horizontal_spacing=0.12,
        vertical_spacing=0.13,
    )
    for index, spec in enumerate(TEMPORAL_ESCALATION_FIGURE_METRICS):
        row_index = index // 2 + 1
        column_index = index % 2 + 1
        subset = figure_data.loc[figure_data["metric_id"] == spec["metric_id"]]
        global_values = subset.loc[subset["series"] == "global"].dropna(subset=["value_relative_t1"])
        figure.add_trace(
            plotly_go.Scatter(
                x=global_values["temporal_marker"],
                y=global_values["value_relative_t1"],
                mode="lines+markers",
                name="Global",
                legendgroup="Global",
                showlegend=index == 0,
                line={"color": CROSS_EVIDENCE_VISUAL_PALETTE["context"], "width": 3},
                marker={"size": 9},
                customdata=global_values[["value_raw", "n_valid"]],
                hovertemplate="Global %{x}<br>Relative to T1: %{y:.2f}<br>Raw: %{customdata[0]}<br>n: %{customdata[1]}<extra></extra>",
            ),
            row=row_index,
            col=column_index,
        )
        for semester in sorted(subset["semester"].dropna().astype(str).unique()):
            semester_values = subset.loc[(subset["series"] == "semester") & (subset["semester"].astype(str) == semester)].dropna(subset=["value_relative_t1"])
            figure.add_trace(
                plotly_go.Scatter(
                    x=semester_values["temporal_marker"],
                    y=semester_values["value_relative_t1"],
                    mode="lines+markers",
                    name=semester,
                    legendgroup=semester,
                    showlegend=index == 0,
                    line={"color": SOURCE_CHURN_PLANNING_REWORK_SEMESTER_COLORS.get(semester, CROSS_EVIDENCE_VISUAL_PALETTE["context"]), "width": 2},
                    marker={"size": 7},
                    customdata=semester_values[["value_raw", "n_valid"]],
                    hovertemplate=f"{semester} %{{x}}<br>Relative to T1: %{{y:.2f}}<br>Raw: %{{customdata[0]}}<br>n: %{{customdata[1]}}<extra></extra>",
                ),
                row=row_index,
                col=column_index,
            )
        figure.update_xaxes(title_text="Temporal cut", categoryorder="array", categoryarray=["T1", "T2", "T3"], row=row_index, col=column_index)
        figure.update_yaxes(title_text="Relative to T1 (T1=1.0)", row=row_index, col=column_index)
    apply_cross_evidence_visual_theme(figure, title="Temporal escalation across planning, engineering, and perceived progress")
    return figure


def build_temporal_escalation_figure(
    *,
    output_data_path: Path | None = None,
    figure_root: Path = Path("assets/figures/cross_evidence"),
    figure_data_root: Path = Path("data/analysis/cross_evidence/figure_data"),
    force: bool = False,
) -> pd.DataFrame:
    """Build or load CE-4.4 temporal escalation figure data and exports."""
    temporal_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["temporal_escalation_metrics"]["path"]))
    evaluator_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["evaluator_outcome_metrics"]["path"]))
    for path in (temporal_path, evaluator_path):
        _require_success_sidecar(path)
    semester_source_frames: dict[str, pd.DataFrame] = {}
    semester_source_paths: list[Path] = []
    for source_artifact in {str(spec["source_artifact"]) for spec in TEMPORAL_ESCALATION_METRIC_SPECS}:
        entry = CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY[f"analysis.{source_artifact}"]
        source_path = Path("data/analysis") / Path(str(entry["path"])).name
        source_sidecar = Path("data/analysis") / Path(str(entry["metadata_path"])).name
        _require_success_sidecar(source_path)
        semester_source_frames[source_artifact] = pd.read_parquet(source_path)
        semester_source_paths.extend([source_path, source_sidecar])
    paths = cross_evidence_figure_export_paths("temporal_escalation_panel", category="prioritarias", figure_root=figure_root, figure_data_root=figure_data_root)
    output_data_path = output_data_path or paths["data"]
    export_paths = dict(paths)
    export_paths["data"] = output_data_path
    options = {
        "stage": "temporal_escalation_panel",
        "visual_spec_version": CROSS_EVIDENCE_VISUAL_SPEC_VERSION,
        "metrics": TEMPORAL_ESCALATION_FIGURE_METRICS,
        "normalization": "relative_to_t1_baseline",
        "series": ["global", "semester"],
        "export_formats": list(CROSS_EVIDENCE_FIGURE_EXPORT_FORMATS),
    }
    inputs = [path for source in (temporal_path, evaluator_path) for path in (source, source.with_name(f"{source.name}.metadata.json"))]
    inputs.extend(semester_source_paths)
    checksum = input_checksum(inputs, options)
    manifest_path = output_data_path.with_name(f"{output_data_path.stem}.manifest.json")
    output_paths_ready = all(export_paths[key].is_file() for key in ("html", "png", "svg", "pdf")) and manifest_path.is_file()
    if force:
        invalidate_stale_artifact(output_data_path, "force-regeneration")
    if not force and output_paths_ready and is_current_artifact(output_data_path, checksum):
        logger.info("Temporal escalation figure is current: %s", output_data_path)
        return pd.read_csv(output_data_path)

    figure_data = compute_temporal_escalation_figure_data(
        pd.read_parquet(temporal_path),
        pd.read_parquet(evaluator_path),
        semester_source_frames,
    )
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    figure_data.to_csv(output_data_path, index=False)
    write_artifact_metadata(output_data_path, checksum, contract_version="cross-evidence-figure-data-v1", options=options)
    figure = _temporal_escalation_figure(figure_data)
    for path in (export_paths["html"], export_paths["png"], export_paths["svg"], export_paths["pdf"]):
        path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(export_paths["html"], include_plotlyjs="cdn", full_html=True)
    figure.write_image(export_paths["png"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT, scale=CROSS_EVIDENCE_FIGURE_PNG_SCALE)
    figure.write_image(export_paths["svg"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_image(export_paths["pdf"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_json(export_paths["plotly_json"])
    manifest_entry = build_cross_evidence_figure_manifest_entry(
        figure,
        figure_data,
        figure_id="temporal_escalation_panel",
        category="prioritarias",
        source=f"{temporal_path.as_posix()} + {evaluator_path.as_posix()}",
        unit_of_analysis="metric_family_cut",
        variables=[spec["metric_id"] for spec in TEMPORAL_ESCALATION_FIGURE_METRICS],
        transformations=["relative_to_t1_baseline", "global_and_semester_series", "no_interpolation"],
        scale_notes=["all subplots use relative T1 index; raw values preserved in CSV"],
        limitations=["observational descriptive panel", "2026.1 semester has n=5", "relative index is not a common raw unit"],
        paths=export_paths,
        required=True,
    )
    manifest_entry["data_metadata_path"] = f"{output_data_path.as_posix()}.metadata.json"
    manifest_path.write_text(json.dumps(manifest_entry, indent=2, sort_keys=True, default=str), encoding="utf-8")
    logger.info("Wrote temporal escalation figure: %s", export_paths["png"])
    return figure_data


def compute_file_category_churn_figure_data(file_category_churn: pd.DataFrame) -> pd.DataFrame:
    """Prepare category-complete absolute and relative data for CE-4.5."""
    required = {"temporal_marker", "file_category", "event_n", "churn_lines", "total_event_n", "total_churn_lines", "category_event_share", "category_churn_share"}
    missing = required - set(file_category_churn.columns)
    if missing:
        raise ValueError(f"file_category_churn_metrics missing columns: {sorted(missing)}")
    cuts = [cut for cut in ("T1", "T2", "T3") if cut in set(file_category_churn["temporal_marker"])]
    if not cuts:
        raise ValueError("file_category_churn_metrics has no recognized temporal cuts")
    observed = file_category_churn.groupby(["temporal_marker", "file_category"], as_index=False).agg(
        event_n=("event_n", "sum"),
        churn_lines=("churn_lines", "sum"),
        total_event_n=("total_event_n", "max"),
        total_churn_lines=("total_churn_lines", "max"),
    )
    grid = pd.MultiIndex.from_product(
        [cuts, FILE_CATEGORY_CHURN_FIGURE_CATEGORIES],
        names=["temporal_marker", "file_category"],
    ).to_frame(index=False)
    result = grid.merge(observed, on=["temporal_marker", "file_category"], how="left")
    for column in ("event_n", "churn_lines"):
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0.0)
    totals = result.groupby("temporal_marker")
    result["total_event_n"] = totals["event_n"].transform("sum")
    result["total_churn_lines"] = totals["churn_lines"].transform("sum")
    result["category_event_share"] = result["event_n"] / result["total_event_n"].where(result["total_event_n"] != 0)
    result["category_churn_share"] = result["churn_lines"] / result["total_churn_lines"].where(result["total_churn_lines"] != 0)
    result[["category_event_share", "category_churn_share"]] = result[["category_event_share", "category_churn_share"]].fillna(0.0)
    result["figure_id"] = "file_category_churn_by_cut"
    result["absolute_value"] = result["churn_lines"]
    result["relative_value"] = result["category_churn_share"]
    result["transformation"] = "category_complete_grid|absolute_log_and_relative_100_percent"
    return result[
        [
            "figure_id",
            "temporal_marker",
            "file_category",
            "event_n",
            "churn_lines",
            "total_event_n",
            "total_churn_lines",
            "category_event_share",
            "category_churn_share",
            "absolute_value",
            "relative_value",
            "transformation",
        ]
    ].sort_values(["temporal_marker", "file_category"]).reset_index(drop=True)


def _file_category_churn_figure(figure_data: pd.DataFrame) -> plotly_go.Figure:
    """Build the CE-4.5 absolute-log and relative-100-percent bar panel."""
    figure = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=["Absolute source-repository churn", "Churn composition by category"],
        horizontal_spacing=0.12,
    )
    for category in FILE_CATEGORY_CHURN_FIGURE_CATEGORIES:
        subset = figure_data.loc[figure_data["file_category"] == category]
        color = FILE_CATEGORY_CHURN_FIGURE_COLORS[category]
        figure.add_trace(
            plotly_go.Bar(
                x=subset["temporal_marker"],
                y=subset["absolute_value"],
                name=category,
                legendgroup=category,
                marker_color=color,
                customdata=subset[["event_n", "churn_lines", "category_churn_share"]],
                hovertemplate=f"{category}<br>%{{x}}<br>Churn lines: %{{customdata[1]}}<br>Events: %{{customdata[0]}}<extra></extra>",
            ),
            row=1,
            col=1,
        )
        figure.add_trace(
            plotly_go.Bar(
                x=subset["temporal_marker"],
                y=subset["relative_value"],
                name=category,
                legendgroup=category,
                showlegend=False,
                marker_color=color,
                customdata=subset[["event_n", "churn_lines", "category_churn_share"]],
                hovertemplate=f"{category}<br>%{{x}}<br>Churn share: %{{y:.1%}}<br>Churn lines: %{{customdata[1]}}<extra></extra>",
            ),
            row=1,
            col=2,
        )
    figure.update_layout(barmode="stack")
    apply_cross_evidence_visual_theme(figure, title="File-category churn by temporal cut")
    figure.update_xaxes(title_text="Temporal cut", categoryorder="array", categoryarray=["T1", "T2", "T3"], row=1, col=1)
    figure.update_xaxes(title_text="Temporal cut", categoryorder="array", categoryarray=["T1", "T2", "T3"], row=1, col=2)
    figure.update_yaxes(title_text="Churn lines (log scale)", type="log", row=1, col=1)
    figure.update_yaxes(title_text="Share of churn lines", tickformat=".0%", range=[0, 1], row=1, col=2)
    return figure


def build_file_category_churn_figure(
    *,
    output_data_path: Path | None = None,
    figure_root: Path = Path("assets/figures/cross_evidence"),
    figure_data_root: Path = Path("data/analysis/cross_evidence/figure_data"),
    force: bool = False,
) -> pd.DataFrame:
    """Build or load CE-4.5 file-category churn figure data and exports."""
    source_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["file_category_churn_metrics"]["path"]))
    _require_success_sidecar(source_path)
    source_sidecar = source_path.with_name(f"{source_path.name}.metadata.json")
    paths = cross_evidence_figure_export_paths("file_category_churn_by_cut", category="prioritarias", figure_root=figure_root, figure_data_root=figure_data_root)
    output_data_path = output_data_path or paths["data"]
    export_paths = dict(paths)
    export_paths["data"] = output_data_path
    options = {
        "stage": "file_category_churn_by_cut",
        "visual_spec_version": CROSS_EVIDENCE_VISUAL_SPEC_VERSION,
        "categories": list(FILE_CATEGORY_CHURN_FIGURE_CATEGORIES),
        "absolute_measure": "churn_lines",
        "absolute_scale": "log",
        "relative_measure": "category_churn_share",
        "relative_scale": "100_percent_stacked",
        "zero_fill_policy": "explicit_category_cut_grid",
        "export_formats": list(CROSS_EVIDENCE_FIGURE_EXPORT_FORMATS),
    }
    checksum = input_checksum([source_path, source_sidecar], options)
    manifest_path = output_data_path.with_name(f"{output_data_path.stem}.manifest.json")
    output_paths_ready = all(export_paths[key].is_file() for key in ("html", "png", "svg", "pdf")) and manifest_path.is_file()
    if force:
        invalidate_stale_artifact(output_data_path, "force-regeneration")
    if not force and output_paths_ready and is_current_artifact(output_data_path, checksum):
        logger.info("File-category churn figure is current: %s", output_data_path)
        return pd.read_csv(output_data_path)

    figure_data = compute_file_category_churn_figure_data(pd.read_parquet(source_path))
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    figure_data.to_csv(output_data_path, index=False)
    write_artifact_metadata(output_data_path, checksum, contract_version="cross-evidence-figure-data-v1", options=options)
    figure = _file_category_churn_figure(figure_data)
    for path in (export_paths["html"], export_paths["png"], export_paths["svg"], export_paths["pdf"]):
        path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(export_paths["html"], include_plotlyjs="cdn", full_html=True)
    figure.write_image(export_paths["png"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT, scale=CROSS_EVIDENCE_FIGURE_PNG_SCALE)
    figure.write_image(export_paths["svg"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_image(export_paths["pdf"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_json(export_paths["plotly_json"])
    manifest_entry = build_cross_evidence_figure_manifest_entry(
        figure,
        figure_data,
        figure_id="file_category_churn_by_cut",
        category="prioritarias",
        source=source_path.as_posix(),
        unit_of_analysis="team_semester_cut_category",
        variables=["file_category", "temporal_marker", "churn_lines", "category_churn_share"],
        transformations=["category_complete_grid", "zero_fill_missing_category_cut", "absolute_log_panel", "relative_100_percent_panel"],
        scale_notes=["absolute churn lines shown on logarithmic scale", "relative panel shows 100 percent composition"],
        limitations=["unknown category is retained", "absolute churn is volume-sensitive", "observational descriptive figure"],
        paths=export_paths,
        required=True,
    )
    manifest_entry["data_metadata_path"] = f"{output_data_path.as_posix()}.metadata.json"
    manifest_path.write_text(json.dumps(manifest_entry, indent=2, sort_keys=True, default=str), encoding="utf-8")
    logger.info("Wrote file-category churn figure: %s", export_paths["png"])
    return figure_data


def compute_author_pressure_vs_churn_figure_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Prepare anonymized long-form data for the CE-4.6 subplot figure."""
    required = {"ID_Equipe", "Semestre", "commits_per_author_t3", "commit_gini_t3", "active_author_pressure_status_t3"} | {
        str(spec["y"]) for spec in AUTHOR_PRESSURE_FIGURE_SPECS
    }
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"cross_evidence_panel missing columns: {sorted(missing)}")
    columns = ["ID_Equipe", "Semestre", "commits_per_author_t3", "commit_gini_t3", "active_author_pressure_status_t3", *[str(spec["y"]) for spec in AUTHOR_PRESSURE_FIGURE_SPECS]]
    working = anonymize_cross_evidence_visual_data(panel[columns])
    for column in ["commits_per_author_t3", "commit_gini_t3", *[str(spec["y"]) for spec in AUTHOR_PRESSURE_FIGURE_SPECS]]:
        working[column] = pd.to_numeric(working[column], errors="coerce")
    rows: list[dict[str, object]] = []
    for spec in AUTHOR_PRESSURE_FIGURE_SPECS:
        y_name = str(spec["y"])
        subset = working.dropna(subset=["commits_per_author_t3", y_name])
        if (subset[["commits_per_author_t3", y_name]] <= 0).any().any():
            raise ValueError("author pressure and outcomes must be positive for the configured scales")
        for row in subset.to_dict("records"):
            rows.append(
                {
                    "figure_id": "author_pressure_vs_churn",
                    "plot_id": spec["plot_id"],
                    "anonymized_team_id": row["anonymized_team_id"],
                    "semester": row["Semestre"],
                    "x": "commits_per_author_t3",
                    "x_value": row["commits_per_author_t3"],
                    "y": y_name,
                    "y_value": row[y_name],
                    "x_scale": "linear",
                    "y_scale": "log",
                    "commit_gini_t3": row["commit_gini_t3"],
                    "active_author_pressure_status_t3": row["active_author_pressure_status_t3"],
                    "transformation": "complete_case_pair|source_category_only_t3_for_churn",
                }
            )
    return pd.DataFrame(rows)


def _author_pressure_vs_churn_figure(figure_data: pd.DataFrame) -> plotly_go.Figure:
    """Build the CE-4.6 three-panel author pressure figure."""
    figure = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[str(spec["title"]) for spec in AUTHOR_PRESSURE_FIGURE_SPECS],
        horizontal_spacing=0.09,
    )
    for index, spec in enumerate(AUTHOR_PRESSURE_FIGURE_SPECS, start=1):
        subset = figure_data.loc[figure_data["plot_id"] == spec["plot_id"]]
        for semester in sorted(subset["semester"].astype(str).unique()):
            points = subset.loc[subset["semester"].astype(str) == semester]
            figure.add_trace(
                plotly_go.Scatter(
                    x=points["x_value"],
                    y=points["y_value"],
                    mode="markers",
                    name=semester,
                    legendgroup=semester,
                    showlegend=index == 1,
                    marker={"size": 10, "color": SOURCE_CHURN_PLANNING_REWORK_SEMESTER_COLORS.get(semester, CROSS_EVIDENCE_VISUAL_PALETTE["context"]), "line": {"width": 0.8, "color": "#FFFFFF"}},
                    customdata=points[["anonymized_team_id", "semester", "commit_gini_t3", "active_author_pressure_status_t3"]],
                    hovertemplate="%{customdata[0]} (%{customdata[1]})<br>Commits per author: %{x}<br>Outcome: %{y}<br>Gini: %{customdata[2]:.3f}<br>Pressure: %{customdata[3]}<extra></extra>",
                ),
                row=1,
                col=index,
            )
        figure.update_xaxes(title_text="Commits per author at T3", row=1, col=index)
        figure.update_yaxes(title_text=str(spec["y_title"]), type="log", row=1, col=index)
    apply_cross_evidence_visual_theme(figure, title="Author integration pressure and late instability")
    return figure


def build_author_pressure_vs_churn_figure(
    *,
    output_data_path: Path | None = None,
    figure_root: Path = Path("assets/figures/cross_evidence"),
    figure_data_root: Path = Path("data/analysis/cross_evidence/figure_data"),
    force: bool = False,
) -> pd.DataFrame:
    """Build or load CE-4.6 author-pressure figure data and exports."""
    panel_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_panel"]["path"]))
    _require_success_sidecar(panel_path)
    panel_sidecar = panel_path.with_name(f"{panel_path.name}.metadata.json")
    paths = cross_evidence_figure_export_paths("author_pressure_vs_churn", category="prioritarias", figure_root=figure_root, figure_data_root=figure_data_root)
    output_data_path = output_data_path or paths["data"]
    export_paths = dict(paths)
    export_paths["data"] = output_data_path
    options = {
        "stage": "author_pressure_vs_churn",
        "visual_spec_version": CROSS_EVIDENCE_VISUAL_SPEC_VERSION,
        "x": "commits_per_author_t3",
        "y_variables": [str(spec["y"]) for spec in AUTHOR_PRESSURE_FIGURE_SPECS],
        "x_scale": "linear",
        "y_scale": "log",
        "source_policy": "source_churn_t3_is_source_category_only",
        "metadata_only": ["commit_gini_t3", "active_author_pressure_status_t3"],
        "export_formats": list(CROSS_EVIDENCE_FIGURE_EXPORT_FORMATS),
    }
    checksum = input_checksum([panel_path, panel_sidecar], options)
    manifest_path = output_data_path.with_name(f"{output_data_path.stem}.manifest.json")
    output_paths_ready = all(export_paths[key].is_file() for key in ("html", "png", "svg", "pdf")) and manifest_path.is_file()
    if force:
        invalidate_stale_artifact(output_data_path, "force-regeneration")
    if not force and output_paths_ready and is_current_artifact(output_data_path, checksum):
        logger.info("Author-pressure figure is current: %s", output_data_path)
        return pd.read_csv(output_data_path)

    figure_data = compute_author_pressure_vs_churn_figure_data(pd.read_parquet(panel_path))
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    figure_data.to_csv(output_data_path, index=False)
    write_artifact_metadata(output_data_path, checksum, contract_version="cross-evidence-figure-data-v1", options=options)
    figure = _author_pressure_vs_churn_figure(figure_data)
    for path in (export_paths["html"], export_paths["png"], export_paths["svg"], export_paths["pdf"]):
        path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(export_paths["html"], include_plotlyjs="cdn", full_html=True)
    figure.write_image(export_paths["png"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT, scale=CROSS_EVIDENCE_FIGURE_PNG_SCALE)
    figure.write_image(export_paths["svg"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_image(export_paths["pdf"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_json(export_paths["plotly_json"])
    manifest_entry = build_cross_evidence_figure_manifest_entry(
        figure,
        figure_data,
        figure_id="author_pressure_vs_churn",
        category="prioritarias",
        source=panel_path.as_posix(),
        unit_of_analysis="team_semester",
        variables=["commits_per_author_t3", "source_churn_t3", "planning_rework_signal_t2_t3", "planning_artifact_activity_t3"],
        transformations=["complete_case_pair", "source_category_only_t3_for_churn", "anonymize_team_id", "log_y_outcomes"],
        scale_notes=["commits per author linear", "source churn, planning rework, and planning activity logarithmic"],
        limitations=["observational association", "team-semester sample n=14", "Gini and pressure status are metadata, not primary visual dimensions"],
        paths=export_paths,
        required=True,
    )
    manifest_entry["data_metadata_path"] = f"{output_data_path.as_posix()}.metadata.json"
    manifest_path.write_text(json.dumps(manifest_entry, indent=2, sort_keys=True, default=str), encoding="utf-8")
    logger.info("Wrote author-pressure figure: %s", export_paths["png"])
    return figure_data


def compute_pareto_extreme_cases_figure_data(overlap: pd.DataFrame) -> pd.DataFrame:
    """Prepare heatmap cells for extreme-case Jaccard overlap."""
    required = {"overlap_id", "left_variable", "left_extreme", "right_variable", "right_extreme", "overlap_n", "jaccard", "group_size_requested"}
    missing = required - set(overlap.columns)
    if missing:
        raise ValueError(f"extreme_case_overlap missing columns: {sorted(missing)}")
    result = overlap.copy()
    result["pair_label"] = result["left_variable"] + " vs " + result["right_variable"]
    result["mode"] = result["left_extreme"] + "_" + result["right_extreme"]
    result["cell_label"] = result["overlap_n"].astype(int).astype(str) + "/" + result["group_size_requested"].astype(int).astype(str)
    result["figure_id"] = "pareto_extreme_cases"
    result["transformation"] = "jaccard_heatmap|overlap_n_over_k_cell_labels|anonymized_aggregate"
    return result[["figure_id", "overlap_id", "pair_label", "mode", "left_variable", "right_variable", "left_extreme", "right_extreme", "overlap_n", "group_size_requested", "jaccard", "overlap_rate_left", "overlap_rate_right", "cell_label", "transformation"]].sort_values(["pair_label", "mode"]).reset_index(drop=True)


def _pareto_extreme_cases_figure(figure_data: pd.DataFrame) -> plotly_go.Figure:
    """Build the CE-4.7 Jaccard heatmap."""
    pairs = sorted(figure_data["pair_label"].unique())
    modes = ["top_top", "top_bottom", "bottom_bottom"]
    matrix = figure_data.pivot(index="pair_label", columns="mode", values="jaccard").reindex(index=pairs, columns=modes)
    labels = figure_data.pivot(index="pair_label", columns="mode", values="cell_label").reindex(index=pairs, columns=modes)
    figure = plotly_go.Figure(
        data=plotly_go.Heatmap(
            z=matrix.values,
            x=modes,
            y=pairs,
            text=labels.values,
            texttemplate="%{text}",
            colorscale=PARETO_EXTREME_CASES_COLORSCALE,
            zmin=0,
            zmax=1,
            colorbar={"title": "Jaccard"},
            hovertemplate="%{y}<br>%{x}<br>Jaccard: %{z:.2f}<br>Overlap: %{text}<extra></extra>",
        )
    )
    apply_cross_evidence_visual_theme(figure, title="Extreme-case overlap across evidence dimensions")
    figure.update_xaxes(title_text="Extreme pairing")
    figure.update_yaxes(title_text="Variable pair", autorange="reversed")
    return figure


def build_pareto_extreme_cases_figure(
    *,
    output_data_path: Path | None = None,
    figure_root: Path = Path("assets/figures/cross_evidence"),
    figure_data_root: Path = Path("data/analysis/cross_evidence/figure_data"),
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the CE-4.7 extreme-case overlap figure."""
    source_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["extreme_case_overlap"]["path"]))
    _require_success_sidecar(source_path)
    source_sidecar = source_path.with_name(f"{source_path.name}.metadata.json")
    paths = cross_evidence_figure_export_paths("pareto_extreme_cases", category="prioritarias", figure_root=figure_root, figure_data_root=figure_data_root)
    output_data_path = output_data_path or paths["data"]
    export_paths = dict(paths)
    export_paths["data"] = output_data_path
    options = {
        "stage": "pareto_extreme_cases",
        "visual_spec_version": CROSS_EVIDENCE_VISUAL_SPEC_VERSION,
        "source_artifact": "extreme_case_overlap",
        "heatmap_measure": "jaccard",
        "cell_label": "overlap_n_over_group_size_requested",
        "privacy_policy": "aggregate_only_no_overlap_keys_in_figure_data",
        "export_formats": list(CROSS_EVIDENCE_FIGURE_EXPORT_FORMATS),
    }
    checksum = input_checksum([source_path, source_sidecar], options)
    manifest_path = output_data_path.with_name(f"{output_data_path.stem}.manifest.json")
    output_paths_ready = all(export_paths[key].is_file() for key in ("html", "png", "svg", "pdf")) and manifest_path.is_file()
    if force:
        invalidate_stale_artifact(output_data_path, "force-regeneration")
    if not force and output_paths_ready and is_current_artifact(output_data_path, checksum):
        logger.info("Pareto extreme-case figure is current: %s", output_data_path)
        return pd.read_csv(output_data_path)
    figure_data = compute_pareto_extreme_cases_figure_data(pd.read_csv(source_path))
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    figure_data.to_csv(output_data_path, index=False)
    write_artifact_metadata(output_data_path, checksum, contract_version="cross-evidence-figure-data-v1", options=options)
    figure = _pareto_extreme_cases_figure(figure_data)
    for path in (export_paths["html"], export_paths["png"], export_paths["svg"], export_paths["pdf"]):
        path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(export_paths["html"], include_plotlyjs="cdn", full_html=True)
    figure.write_image(export_paths["png"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT, scale=CROSS_EVIDENCE_FIGURE_PNG_SCALE)
    figure.write_image(export_paths["svg"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_image(export_paths["pdf"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_json(export_paths["plotly_json"])
    manifest_entry = build_cross_evidence_figure_manifest_entry(
        figure, figure_data, figure_id="pareto_extreme_cases", category="prioritarias", source=source_path.as_posix(), unit_of_analysis="ranked_team_semester", variables=["jaccard", "overlap_n"], transformations=["jaccard_heatmap", "overlap_n_over_k_cell_labels", "anonymized_aggregate"], scale_notes=["Jaccard bounded from 0 to 1"], limitations=["descriptive extreme-case overlap", "no causal interpretation", "overlap keys excluded from figure data"], paths=export_paths, required=True,
    )
    manifest_entry["data_metadata_path"] = f"{output_data_path.as_posix()}.metadata.json"
    manifest_path.write_text(json.dumps(manifest_entry, indent=2, sort_keys=True, default=str), encoding="utf-8")
    logger.info("Wrote Pareto extreme-case figure: %s", export_paths["png"])
    return figure_data


def compute_leave_one_out_robustness_figure_data(sensitivity: pd.DataFrame) -> pd.DataFrame:
    """Prepare aggregate interval data for the leave-one-out robustness figure."""
    required = {"analysis_id", "original_coefficient", "coefficient_min", "coefficient_max", "p_value_max", "loo_support_share", "robustness_class"}
    missing = required - set(sensitivity.columns)
    if missing:
        raise ValueError(f"leave_one_out_sensitivity missing columns: {sorted(missing)}")
    result = sensitivity.copy()
    result["figure_id"] = "leave_one_out_robustness"
    result["transformation"] = "coefficient_interval_with_original_point|aggregate_only"
    return result[["figure_id", "analysis_id", "original_coefficient", "coefficient_min", "coefficient_max", "p_value_max", "loo_support_share", "robustness_class", "transformation"]].sort_values(["robustness_class", "analysis_id"]).reset_index(drop=True)


def _leave_one_out_robustness_figure(figure_data: pd.DataFrame) -> plotly_go.Figure:
    """Build the CE-4.7 leave-one-out coefficient interval figure."""
    figure = plotly_go.Figure()
    ordered = figure_data.reset_index(drop=True)
    y_values = list(range(len(ordered)))
    for robustness_class, color in LEAVE_ONE_OUT_ROBUSTNESS_COLORS.items():
        subset = ordered.loc[ordered["robustness_class"] == robustness_class]
        if subset.empty:
            continue
        indices = subset.index
        for index in indices:
            row = ordered.loc[index]
            figure.add_trace(plotly_go.Scatter(x=[row["coefficient_min"], row["coefficient_max"]], y=[index, index], mode="lines", line={"color": color, "width": 5}, name=robustness_class, legendgroup=robustness_class, showlegend=bool(index == indices[0])))
        figure.add_trace(plotly_go.Scatter(x=subset["original_coefficient"], y=list(indices), mode="markers", marker={"color": color, "size": 10}, name=f"{robustness_class} original", legendgroup=robustness_class, showlegend=False, customdata=subset[["analysis_id", "p_value_max", "loo_support_share"]], hovertemplate="%{customdata[0]}<br>Original rho: %{x:.3f}<br>Max p-value: %{customdata[1]:.3f}<br>Support share: %{customdata[2]:.1%}<extra></extra>"))
    figure.add_vline(x=0, line_dash="dash", line_color="#64748B")
    apply_cross_evidence_visual_theme(figure, title="Leave-one-out robustness of exploratory correlations")
    figure.update_xaxes(title_text="Spearman coefficient", range=[-1, 1])
    figure.update_yaxes(title_text="Analysis", tickmode="array", tickvals=y_values, ticktext=ordered["analysis_id"], autorange="reversed")
    return figure


def build_leave_one_out_robustness_figure(
    *,
    output_data_path: Path | None = None,
    figure_root: Path = Path("assets/figures/cross_evidence"),
    figure_data_root: Path = Path("data/analysis/cross_evidence/figure_data"),
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the CE-4.7 leave-one-out robustness figure."""
    source_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["leave_one_out_sensitivity"]["path"]))
    _require_success_sidecar(source_path)
    source_sidecar = source_path.with_name(f"{source_path.name}.metadata.json")
    paths = cross_evidence_figure_export_paths("leave_one_out_robustness", category="prioritarias", figure_root=figure_root, figure_data_root=figure_data_root)
    output_data_path = output_data_path or paths["data"]
    export_paths = dict(paths)
    export_paths["data"] = output_data_path
    options = {"stage": "leave_one_out_robustness", "visual_spec_version": CROSS_EVIDENCE_VISUAL_SPEC_VERSION, "interval_measure": "coefficient_min_to_max", "point_measure": "original_coefficient", "export_formats": list(CROSS_EVIDENCE_FIGURE_EXPORT_FORMATS)}
    checksum = input_checksum([source_path, source_sidecar], options)
    manifest_path = output_data_path.with_name(f"{output_data_path.stem}.manifest.json")
    output_paths_ready = all(export_paths[key].is_file() for key in ("html", "png", "svg", "pdf")) and manifest_path.is_file()
    if force:
        invalidate_stale_artifact(output_data_path, "force-regeneration")
    if not force and output_paths_ready and is_current_artifact(output_data_path, checksum):
        logger.info("Leave-one-out robustness figure is current: %s", output_data_path)
        return pd.read_csv(output_data_path)
    figure_data = compute_leave_one_out_robustness_figure_data(pd.read_csv(source_path))
    output_data_path.parent.mkdir(parents=True, exist_ok=True)
    figure_data.to_csv(output_data_path, index=False)
    write_artifact_metadata(output_data_path, checksum, contract_version="cross-evidence-figure-data-v1", options=options)
    figure = _leave_one_out_robustness_figure(figure_data)
    for path in (export_paths["html"], export_paths["png"], export_paths["svg"], export_paths["pdf"]):
        path.parent.mkdir(parents=True, exist_ok=True)
    figure.write_html(export_paths["html"], include_plotlyjs="cdn", full_html=True)
    figure.write_image(export_paths["png"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT, scale=CROSS_EVIDENCE_FIGURE_PNG_SCALE)
    figure.write_image(export_paths["svg"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_image(export_paths["pdf"], width=CROSS_EVIDENCE_FIGURE_WIDTH, height=CROSS_EVIDENCE_FIGURE_HEIGHT)
    figure.write_json(export_paths["plotly_json"])
    manifest_entry = build_cross_evidence_figure_manifest_entry(
        figure, figure_data, figure_id="leave_one_out_robustness", category="prioritarias", source=source_path.as_posix(), unit_of_analysis="analysis_result", variables=["original_coefficient", "coefficient_min", "coefficient_max", "robustness_class"], transformations=["coefficient_interval_with_original_point", "aggregate_only"], scale_notes=["coefficient bounded from -1 to 1", "zero reference line"], limitations=["leave-one-out is sensitivity evidence, not causal validation", "individual removed observations are not displayed"], paths=export_paths, required=True,
    )
    manifest_entry["data_metadata_path"] = f"{output_data_path.as_posix()}.metadata.json"
    manifest_path.write_text(json.dumps(manifest_entry, indent=2, sort_keys=True, default=str), encoding="utf-8")
    logger.info("Wrote leave-one-out robustness figure: %s", export_paths["png"])
    return figure_data


def _normalize_path(value: str | None) -> str:
    """Normalize repository paths for deterministic category matching."""
    return str(value or "").replace("\\", "/").strip().lower().lstrip("./")


def _normalize_extension(file_path: str, file_extension: str | None) -> str:
    """Return an explicit extension or infer one from the normalized path."""
    extension = str(file_extension or "").strip().lower()
    if extension and not extension.startswith("."):
        extension = f".{extension}"
    if extension:
        return extension
    return PurePosixPath(file_path).suffix.lower()


def _matches_path_pattern(file_path: str, pattern: str) -> bool:
    """Return whether a normalized path matches a configured path pattern."""
    normalized_pattern = pattern.replace("\\", "/").strip().lower().lstrip("./")
    if not normalized_pattern:
        return False
    if normalized_pattern.endswith("/"):
        return file_path.startswith(normalized_pattern) or f"/{normalized_pattern}" in file_path
    return file_path == normalized_pattern or normalized_pattern in file_path


def _result(category: str, rule: str, confidence: float, warning: str | None = None) -> dict[str, object]:
    """Build the classifier result payload used by dataframe expansion."""
    return {
        "file_category": category,
        "category_rule": rule,
        "category_confidence": confidence,
        "category_warning": warning,
    }


def classify_file_category(
    file_path: str | None,
    file_extension: str | None = None,
    change_status: str | None = None,
    file_path_old: str | None = None,
    *,
    rules: dict[str, Any] | None = None,
) -> dict[str, object]:
    """Classify one Git file event into the versioned cross-evidence taxonomy.

    Args:
        file_path: Current or primary file path from the Git event.
        file_extension: Optional extension column from the lake. If empty, the
            extension is inferred from ``file_path``.
        change_status: Git change status. Accepted for API symmetry with the
            persisted lake schema; CE-1.2 does not branch on status yet.
        file_path_old: Previous path, used only as a fallback when ``file_path``
            is empty.
        rules: Optional taxonomy override for tests.

    Returns:
        Dict with ``file_category``, ``category_rule``,
        ``category_confidence`` and ``category_warning``.
    """
    del change_status
    taxonomy = rules or FILE_CATEGORY_RULES
    selected_path = _normalize_path(file_path) or _normalize_path(file_path_old)
    extension = _normalize_extension(selected_path, file_extension)
    path_patterns = taxonomy["path_patterns"]
    filename_suffixes = taxonomy["filename_suffixes"]
    extensions = taxonomy["extensions"]
    contextual = taxonomy["contextual_extensions"]
    warnings = taxonomy["warnings"]

    for pattern in path_patterns.get("generated", set()):
        if _matches_path_pattern(selected_path, pattern):
            warning = None
            confidence = NORMAL_CONFIDENCE
            if extension in extensions.get("source", set()) or extension in extensions.get("planning", set()):
                warning = str(warnings["generated_source_like_path"])
                confidence = WARNING_CONFIDENCE
            return _result("generated", f"path:generated:{pattern}", confidence, warning)

    planning_context = any(
        _matches_path_pattern(selected_path, pattern)
        for pattern in path_patterns.get("planning", set())
    )
    planning_contextual_extensions = contextual.get("planning_when_path_matches_planning", set())
    if planning_context and extension in extensions.get("planning", set()):
        warning = None
        confidence = NORMAL_CONFIDENCE
        if extension in planning_contextual_extensions:
            warning = str(warnings["planning_config_extension"])
            confidence = WARNING_CONFIDENCE
        return _result("planning", "path:planning", confidence, warning)

    for pattern in path_patterns.get("test", set()):
        if _matches_path_pattern(selected_path, pattern):
            return _result("test", f"path:test:{pattern}", NORMAL_CONFIDENCE)

    for category in taxonomy["category_order"]:
        for suffix in filename_suffixes.get(category, set()):
            if selected_path.endswith(suffix):
                return _result(category, f"filename_suffix:{category}:{suffix}", NORMAL_CONFIDENCE)

    if not extension:
        return _result(
            str(taxonomy["default_category"]),
            "extension:empty",
            UNKNOWN_CONFIDENCE,
            str(warnings["empty_extension"]),
        )

    for category in taxonomy["category_order"]:
        if category == "unknown":
            continue
        if category == "planning" and extension in planning_contextual_extensions:
            continue
        if extension in extensions.get(category, set()):
            return _result(category, f"extension:{category}:{extension}", NORMAL_CONFIDENCE)

    return _result(
        str(taxonomy["default_category"]),
        f"extension:unknown:{extension}",
        UNKNOWN_CONFIDENCE,
    )


def _require_success_sidecar(path: Path) -> dict[str, Any]:
    """Load and validate the required sidecar for an input artifact."""
    metadata_path = path.with_name(f"{path.name}.metadata.json")
    if not path.is_file():
        raise FileNotFoundError(f"Required artifact not found: {path}")
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Required sidecar not found: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("status") != "success":
        raise ValueError(f"Artifact sidecar is not successful: {metadata_path}")
    return metadata


def _gini(values: pd.Series) -> float:
    """Compute standard Gini for non-negative counts."""
    ordered = sorted(float(value) for value in values if pd.notna(value))
    if not ordered or len(ordered) == 1 or sum(ordered) == 0:
        return 0.0
    weighted_sum = sum(index * value for index, value in enumerate(ordered, start=1))
    return float((2 * weighted_sum / (len(ordered) * sum(ordered))) - ((len(ordered) + 1) / len(ordered)))


def _pressure_statuses(values: pd.Series) -> pd.Series:
    """Assign quartile-based pressure labels to commits-per-author values."""
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.empty:
        return pd.Series(dtype="object")
    ranks = numeric.rank(method="average", pct=True)
    labels: list[str] = []
    for percentile in ranks:
        if pd.isna(percentile):
            labels.append("unavailable")
        elif percentile <= 0.25:
            labels.append(AUTHOR_PRESSURE_STATUS_LABELS[0])
        elif percentile <= 0.50:
            labels.append(AUTHOR_PRESSURE_STATUS_LABELS[1])
        elif percentile <= 0.75:
            labels.append(AUTHOR_PRESSURE_STATUS_LABELS[2])
        else:
            labels.append(AUTHOR_PRESSURE_STATUS_LABELS[3])
    return pd.Series(labels, index=values.index, dtype="object")


def compute_evaluator_outcome_metrics(evaluator: pd.DataFrame) -> pd.DataFrame:
    """Pivot evaluator outcomes by team-semester and temporal cut."""
    missing = EVALUATOR_OUTCOME_REQUIRED_COLUMNS - set(evaluator.columns)
    if missing:
        raise ValueError(f"evaluator_team_cuts missing columns: {sorted(missing)}")
    if evaluator[TEAM_SEMESTER_KEYS + ["temporal_marker"]].isna().any().any():
        raise ValueError("evaluator_team_cuts keys must be non-null")
    if evaluator.duplicated(TEAM_SEMESTER_KEYS + ["temporal_marker"]).any():
        raise ValueError("evaluator_team_cuts has duplicate team-cut observations")
    invalid_cuts = set(evaluator["temporal_marker"].dropna()) - set(CUTS)
    if invalid_cuts:
        raise ValueError(f"evaluator_team_cuts has invalid temporal markers: {sorted(invalid_cuts)}")

    rows: list[dict[str, Any]] = []
    for key, group in evaluator.groupby(TEAM_SEMESTER_KEYS, dropna=False):
        row: dict[str, Any] = dict(zip(TEAM_SEMESTER_KEYS, key))
        cuts_present = set(group["temporal_marker"])
        missing_cuts = [cut for cut in CUTS if cut not in cuts_present]
        for metric in EVALUATOR_OUTCOME_METRICS:
            for field in EVALUATOR_OUTCOME_FIELDS:
                source = f"{metric}_{field}"
                for cut in CUTS:
                    current = group.loc[group["temporal_marker"] == cut, source]
                    row[f"{source}_{cut.lower()}"] = current.iloc[0] if not current.empty else pd.NA
            for left, right, name in (
                ("t1", "t2", f"{metric}_mean_delta_t1_t2"),
                ("t2", "t3", f"{metric}_mean_delta_t2_t3"),
                ("t1", "t3", f"{metric}_mean_delta_t1_t3"),
            ):
                row[name] = (
                    row[f"{metric}_mean_{right}"] - row[f"{metric}_mean_{left}"]
                    if not missing_cuts
                    else pd.NA
                )

        for cut in CUTS:
            lower = cut.lower()
            row[f"progress_scope_gap_{lower}"] = (
                row[f"project_progress_mean_{lower}"] - row[f"scope_applicability_mean_{lower}"]
                if not pd.isna(row[f"project_progress_mean_{lower}"]) and not pd.isna(row[f"scope_applicability_mean_{lower}"])
                else pd.NA
            )
        for left, right, name in (
            ("t1", "t2", "progress_scope_gap_delta_t1_t2"),
            ("t2", "t3", "progress_scope_gap_delta_t2_t3"),
            ("t1", "t3", "progress_scope_gap_delta_t1_t3"),
        ):
            row[name] = row[f"progress_scope_gap_{right}"] - row[f"progress_scope_gap_{left}"] if not missing_cuts else pd.NA

        row["evaluator_outcome_available"] = not missing_cuts
        row["evaluator_outcome_unavailable_reason"] = (
            f"missing_required_temporal_cut:{missing_cuts[0]}" if missing_cuts else None
        )
        row["evaluator_outcome_observation_unit"] = "team_semester"
        row["evaluator_outcome_contract_version"] = EVALUATOR_OUTCOME_CONTRACT_VERSION
        rows.append(row)
    return pd.DataFrame(rows).sort_values(TEAM_SEMESTER_KEYS).reset_index(drop=True)


def write_evaluator_outcome_metrics(
    metrics: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist evaluator outcome metrics and their sidecar."""
    required = set(TEAM_SEMESTER_KEYS) | {
        "scope_applicability_mean_t3",
        "project_progress_mean_t3",
        "progress_scope_gap_t3",
        "evaluator_outcome_available",
        "evaluator_outcome_observation_unit",
        "evaluator_outcome_contract_version",
    }
    missing = required - set(metrics.columns)
    if missing:
        raise ValueError(f"evaluator_outcome_metrics output missing columns: {sorted(missing)}")
    if metrics.empty:
        raise ValueError("evaluator_outcome_metrics output is empty")
    if metrics.duplicated(TEAM_SEMESTER_KEYS).any():
        raise ValueError("evaluator_outcome_metrics has duplicate team-semester keys")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=EVALUATOR_OUTCOME_CONTRACT_VERSION,
        options=options,
    )


def build_evaluator_outcome_metrics(
    *,
    lake_dir: Path = Path("data/lake"),
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the persisted evaluator outcome metrics artifact."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["evaluator_outcome_metrics"]["path"]))
    evaluator_input = CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY["lake.evaluator_team_cuts"]
    evaluator_path = lake_dir / Path(str(evaluator_input["path"])).name
    evaluator_sidecar = lake_dir / Path(str(evaluator_input["metadata_path"])).name
    _require_success_sidecar(evaluator_path)
    options = {
        "stage": "evaluator_outcome_metrics",
        "contract_version": EVALUATOR_OUTCOME_CONTRACT_VERSION,
        "metrics": list(EVALUATOR_OUTCOME_METRICS),
        "fields": list(EVALUATOR_OUTCOME_FIELDS),
        "delta_pairs": ["t1_t2", "t2_t3", "t1_t3"],
        "progress_scope_gap": "project_progress_mean_minus_scope_applicability_mean",
        "availability_policy": "complete_t1_t2_t3_required_for_deltas",
    }
    checksum = input_checksum([evaluator_path, evaluator_sidecar], options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Evaluator outcome metrics artifact is current: %s", output_path)
        return pd.read_parquet(output_path)

    evaluator = pd.read_parquet(evaluator_path)
    metrics = compute_evaluator_outcome_metrics(evaluator)
    invalidate_stale_artifact(output_path, checksum)
    write_evaluator_outcome_metrics(metrics, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s evaluator outcome observations", len(metrics))
    return metrics


def compute_author_pressure_metrics(commits: pd.DataFrame) -> pd.DataFrame:
    """Compute author pressure metrics for observed team-semester-cut groups."""
    missing = AUTHOR_PRESSURE_REQUIRED_COLUMNS - set(commits.columns)
    if missing:
        raise ValueError(f"git_commits missing columns: {sorted(missing)}")
    if commits[TEAM_SEMESTER_CUT_KEYS].isna().any().any():
        raise ValueError("git_commits team-semester-cut keys must be non-null")
    invalid_cuts = set(commits["temporal_marker"].dropna()) - set(CUTS)
    if invalid_cuts:
        raise ValueError(f"git_commits has invalid temporal markers: {sorted(invalid_cuts)}")
    numeric_lines = commits[["lines_added", "lines_deleted", "files_changed"]].apply(pd.to_numeric, errors="coerce")
    if numeric_lines.isna().any().any():
        raise ValueError("git_commits line and file counts must be numeric")
    if (numeric_lines < 0).any().any():
        raise ValueError("git_commits line and file counts must not be negative")

    working = commits.copy()
    working["lines_added_observed"] = numeric_lines["lines_added"]
    working["lines_deleted_observed"] = numeric_lines["lines_deleted"]
    working["files_changed_observed"] = numeric_lines["files_changed"]
    working["churn_lines"] = working["lines_added_observed"] + working["lines_deleted_observed"]

    rows: list[dict[str, Any]] = []
    for key, group in working.groupby(TEAM_SEMESTER_CUT_KEYS, dropna=False):
        authors = group["ID_Autor_Local"].dropna()
        counts = authors.value_counts()
        commit_n = int(len(group))
        author_n = int(counts.size)
        shares = counts / commit_n if commit_n else pd.Series(dtype=float)
        row: dict[str, Any] = dict(zip(TEAM_SEMESTER_CUT_KEYS, key))
        row["commit_n"] = commit_n
        row["author_n"] = author_n
        row["commits_per_author"] = float(commit_n / author_n) if author_n else pd.NA
        row["max_author_share"] = float(shares.max()) if not shares.empty else pd.NA
        row["commit_gini"] = _gini(counts)
        row["churn_lines"] = float(group["churn_lines"].sum())
        row["lines_added"] = float(group["lines_added_observed"].sum())
        row["lines_deleted"] = float(group["lines_deleted_observed"].sum())
        row["files_changed"] = int(group["files_changed_observed"].sum())
        row["churn_per_author"] = float(row["churn_lines"] / author_n) if author_n else pd.NA
        row["commits_per_author_rank_pct"] = pd.NA
        row["active_author_pressure_status"] = "unavailable"
        row["author_pressure_available"] = bool(commit_n > 0 and author_n > 0)
        row["author_pressure_unavailable_reason"] = None if row["author_pressure_available"] else "no_observed_author_commits"
        row["author_pressure_observation_unit"] = "team_semester_cut"
        row["author_pressure_contract_version"] = AUTHOR_PRESSURE_CONTRACT_VERSION
        rows.append(row)

    result = pd.DataFrame(rows).sort_values(TEAM_SEMESTER_CUT_KEYS).reset_index(drop=True)
    if not result.empty:
        result["commits_per_author_rank_pct"] = pd.to_numeric(result["commits_per_author"], errors="coerce").rank(method="average", pct=True)
        result["active_author_pressure_status"] = _pressure_statuses(result["commits_per_author"])
    return result


def write_author_pressure_metrics(
    metrics: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist author pressure metrics and their sidecar."""
    required = set(TEAM_SEMESTER_CUT_KEYS) | {
        "commit_n",
        "author_n",
        "commits_per_author",
        "max_author_share",
        "commit_gini",
        "active_author_pressure_status",
        "author_pressure_observation_unit",
        "author_pressure_contract_version",
    }
    missing = required - set(metrics.columns)
    if missing:
        raise ValueError(f"author_pressure_metrics output missing columns: {sorted(missing)}")
    if metrics.empty:
        raise ValueError("author_pressure_metrics output is empty")
    if metrics.duplicated(TEAM_SEMESTER_CUT_KEYS).any():
        raise ValueError("author_pressure_metrics has duplicate team-semester-cut keys")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=AUTHOR_PRESSURE_CONTRACT_VERSION,
        options=options,
    )


def build_author_pressure_metrics(
    *,
    lake_dir: Path = Path("data/lake"),
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the persisted author pressure metrics artifact."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["author_pressure_metrics"]["path"]))
    commits_input = CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY["lake.git_commits"]
    commits_path = lake_dir / Path(str(commits_input["path"])).name
    commits_sidecar = lake_dir / Path(str(commits_input["metadata_path"])).name
    _require_success_sidecar(commits_path)
    options = {
        "stage": "author_pressure_metrics",
        "contract_version": AUTHOR_PRESSURE_CONTRACT_VERSION,
        "unit_of_analysis": "observed_team_semester_cut",
        "gini_method": "author_commit_count_standard_gini",
        "single_author_gini": 0.0,
        "pressure_status_policy": "global_commits_per_author_rank_quartiles",
        "include_churn_lines": True,
    }
    checksum = input_checksum([commits_path, commits_sidecar], options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Author pressure metrics artifact is current: %s", output_path)
        return pd.read_parquet(output_path)

    commits = pd.read_parquet(commits_path)
    metrics = compute_author_pressure_metrics(commits)
    invalidate_stale_artifact(output_path, checksum)
    write_author_pressure_metrics(metrics, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s author pressure observations", len(metrics))
    return metrics


def _wilcoxon_summary(left: pd.Series, right: pd.Series) -> dict[str, object]:
    """Return signed-rank test diagnostics for one paired metric comparison."""
    pair = pd.DataFrame({"left": pd.to_numeric(left, errors="coerce"), "right": pd.to_numeric(right, errors="coerce")}).dropna()
    diff = pair["right"] - pair["left"]
    if pair.empty:
        return {"status": "unavailable", "reason": "insufficient_pair_n", "statistic": pd.NA, "p_value": pd.NA}
    if (diff != 0).sum() == 0:
        return {"status": "unavailable", "reason": "zero_delta", "statistic": pd.NA, "p_value": pd.NA}
    statistic, p_value = scipy_stats.wilcoxon(pair["left"], pair["right"], zero_method="wilcox")
    return {"status": "success", "reason": None, "statistic": float(statistic), "p_value": float(p_value)}


def compute_temporal_escalation_metrics(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Summarize temporal escalation for declared metrics across T1/T2/T3."""
    rows: list[dict[str, object]] = []
    for spec in TEMPORAL_ESCALATION_METRIC_SPECS:
        source_artifact = str(spec["source_artifact"])
        if source_artifact not in frames:
            raise ValueError(f"Missing source artifact frame: {source_artifact}")
        frame = frames[source_artifact]
        columns = dict(spec["columns"])
        missing = (set(TEAM_SEMESTER_KEYS) | set(columns.values())) - set(frame.columns)
        if missing:
            raise ValueError(f"{source_artifact} missing columns: {sorted(missing)}")
        if frame[TEAM_SEMESTER_KEYS].isna().any().any():
            raise ValueError(f"{source_artifact} team-semester keys must be non-null")
        if frame.duplicated(TEAM_SEMESTER_KEYS).any():
            raise ValueError(f"{source_artifact} has duplicate team-semester keys")

        values = {
            cut: pd.to_numeric(frame[column], errors="coerce")
            for cut, column in columns.items()
        }
        row: dict[str, object] = {
            "metric_id": spec["metric_id"],
            "source_artifact": source_artifact,
            "unit_of_analysis": "metric_family",
            "n_total": int(len(frame)),
            "narrative_acts": json.dumps(spec["narrative_acts"]),
            "temporal_escalation_contract_version": TEMPORAL_ESCALATION_CONTRACT_VERSION,
        }
        for cut in ("t1", "t2", "t3"):
            series = values[cut].dropna()
            row[f"n_valid_{cut}"] = int(len(series))
            row[f"mean_{cut}"] = float(series.mean()) if not series.empty else pd.NA
            row[f"median_{cut}"] = float(series.median()) if not series.empty else pd.NA
            row[f"min_{cut}"] = float(series.min()) if not series.empty else pd.NA
            row[f"max_{cut}"] = float(series.max()) if not series.empty else pd.NA

        for left, right in TEMPORAL_ESCALATION_PAIR_SPECS:
            pair_name = f"{left}_{right}"
            pair = pd.DataFrame({"left": values[left], "right": values[right]}).dropna()
            diff = pair["right"] - pair["left"]
            row[f"{pair_name}_paired_n"] = int(len(pair))
            row[f"{pair_name}_increase_n"] = int((diff > 0).sum())
            row[f"{pair_name}_same_n"] = int((diff == 0).sum())
            row[f"{pair_name}_decrease_n"] = int((diff < 0).sum())
            row[f"{pair_name}_mean_delta"] = float(diff.mean()) if not diff.empty else pd.NA
            row[f"{pair_name}_median_delta"] = float(diff.median()) if not diff.empty else pd.NA
            row[f"{pair_name}_min_delta"] = float(diff.min()) if not diff.empty else pd.NA
            row[f"{pair_name}_max_delta"] = float(diff.max()) if not diff.empty else pd.NA
            test = _wilcoxon_summary(pair["left"], pair["right"])
            row[f"{pair_name}_wilcoxon_status"] = test["status"]
            row[f"{pair_name}_wilcoxon_reason"] = test["reason"]
            row[f"{pair_name}_wilcoxon_statistic"] = test["statistic"]
            row[f"{pair_name}_wilcoxon_p_value"] = test["p_value"]

        t1_t3_pair = pd.DataFrame({"t1": values["t1"], "t3": values["t3"]}).dropna()
        nonzero_denominator = t1_t3_pair.loc[t1_t3_pair["t1"] != 0]
        ratios = nonzero_denominator["t3"] / nonzero_denominator["t1"]
        row["t3_t1_ratio_valid_n"] = int(len(ratios))
        row["t3_t1_ratio_zero_denominator_n"] = int(len(t1_t3_pair) - len(nonzero_denominator))
        row["t3_t1_ratio_mean"] = float(ratios.mean()) if not ratios.empty else pd.NA
        row["t3_t1_ratio_median"] = float(ratios.median()) if not ratios.empty else pd.NA
        row["t3_t1_ratio_max"] = float(ratios.max()) if not ratios.empty else pd.NA
        rows.append(row)
    return pd.DataFrame(rows).sort_values("metric_id").reset_index(drop=True)


def write_temporal_escalation_metrics(
    metrics: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist temporal escalation metrics and their sidecar."""
    required = {
        "metric_id",
        "source_artifact",
        "unit_of_analysis",
        "n_total",
        "t1_t3_paired_n",
        "t1_t3_increase_n",
        "t1_t3_wilcoxon_status",
        "t3_t1_ratio_zero_denominator_n",
        "temporal_escalation_contract_version",
    }
    missing = required - set(metrics.columns)
    if missing:
        raise ValueError(f"temporal_escalation_metrics output missing columns: {sorted(missing)}")
    if metrics.empty:
        raise ValueError("temporal_escalation_metrics output is empty")
    if metrics["metric_id"].duplicated().any():
        raise ValueError("temporal_escalation_metrics has duplicate metric_id rows")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=TEMPORAL_ESCALATION_CONTRACT_VERSION,
        options=options,
    )


def build_temporal_escalation_metrics(
    *,
    analysis_dir: Path = Path("data/analysis"),
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the persisted temporal escalation metrics artifact."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["temporal_escalation_metrics"]["path"]))
    input_aliases = ["analysis.planning_metrics", "analysis.code_churn_metrics", "analysis.technical_degradation_metrics"]
    input_paths: list[Path] = []
    frames: dict[str, pd.DataFrame] = {}
    for alias in input_aliases:
        entry = CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY[alias]
        path = analysis_dir / Path(str(entry["path"])).name
        sidecar = analysis_dir / Path(str(entry["metadata_path"])).name
        _require_success_sidecar(path)
        input_paths.extend([path, sidecar])
        frames[alias.removeprefix("analysis.")] = pd.read_parquet(path)
    options = {
        "stage": "temporal_escalation_metrics",
        "contract_version": TEMPORAL_ESCALATION_CONTRACT_VERSION,
        "metric_specs": TEMPORAL_ESCALATION_METRIC_SPECS,
        "wilcoxon_pairs": [f"{left}_{right}" for left, right in TEMPORAL_ESCALATION_PAIR_SPECS],
        "ratio_policy": "exclude_zero_t1_denominator_and_count",
        "source_policy": "specialized_phase2_parquets",
    }
    checksum = input_checksum(input_paths, options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Temporal escalation metrics artifact is current: %s", output_path)
        return pd.read_parquet(output_path)

    metrics = compute_temporal_escalation_metrics(frames)
    invalidate_stale_artifact(output_path, checksum)
    write_temporal_escalation_metrics(metrics, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s temporal escalation metric summaries", len(metrics))
    return metrics


def compute_late_instability_metrics(
    team_metrics: pd.DataFrame,
    file_category_churn: pd.DataFrame,
    author_pressure: pd.DataFrame,
) -> pd.DataFrame:
    """Consolidate late-cycle instability signals at team-semester level."""
    missing_team = LATE_INSTABILITY_TEAM_REQUIRED_COLUMNS - set(team_metrics.columns)
    if missing_team:
        raise ValueError(f"team_metrics missing columns: {sorted(missing_team)}")
    missing_file_category = LATE_INSTABILITY_FILE_CATEGORY_REQUIRED_COLUMNS - set(file_category_churn.columns)
    if missing_file_category:
        raise ValueError(f"file_category_churn_metrics missing columns: {sorted(missing_file_category)}")
    missing_author = LATE_INSTABILITY_AUTHOR_REQUIRED_COLUMNS - set(author_pressure.columns)
    if missing_author:
        raise ValueError(f"author_pressure_metrics missing columns: {sorted(missing_author)}")
    for name, frame, keys in (
        ("team_metrics", team_metrics, TEAM_SEMESTER_KEYS),
        ("file_category_churn_metrics", file_category_churn, TEAM_SEMESTER_CUT_KEYS),
        ("author_pressure_metrics", author_pressure, TEAM_SEMESTER_CUT_KEYS),
    ):
        if frame[keys].isna().any().any():
            raise ValueError(f"{name} keys must be non-null")
    if team_metrics.duplicated(TEAM_SEMESTER_KEYS).any():
        raise ValueError("team_metrics has duplicate team-semester keys")

    t3_source = file_category_churn.loc[
        (file_category_churn["temporal_marker"] == "T3")
        & (file_category_churn["file_category"] == "source")
    ]
    if t3_source.duplicated(TEAM_SEMESTER_KEYS).any():
        raise ValueError("source file-category churn has duplicate T3 team-semester rows")
    source_t3 = t3_source.groupby(TEAM_SEMESTER_KEYS, as_index=False).agg(
        source_churn_t3=("churn_lines", "sum"),
        source_events_t3=("event_n", "sum"),
    )

    t3_author = author_pressure.loc[author_pressure["temporal_marker"] == "T3"].copy()
    if t3_author.duplicated(TEAM_SEMESTER_KEYS).any():
        raise ValueError("author_pressure_metrics has duplicate T3 team-semester rows")
    t3_author = t3_author[
        TEAM_SEMESTER_KEYS
        + ["commits_per_author", "commit_gini", "active_author_pressure_status", "churn_lines"]
    ].rename(
        columns={
            "commits_per_author": "commits_per_author_t3",
            "commit_gini": "commit_gini_t3",
            "active_author_pressure_status": "active_author_pressure_status_t3",
            "churn_lines": "author_churn_lines_t3",
        }
    )

    result = team_metrics[
        TEAM_SEMESTER_KEYS
        + [
            "planning_rework_signal_t2_t3",
            "planning_artifact_activity_t3",
            "pi_line_delta_t3",
            "cc_total_t3",
            "cc_per_source_loc_t3",
            "delta_dt_t2_t3",
        ]
    ].copy()
    result = result.merge(source_t3, on=TEAM_SEMESTER_KEYS, how="left", validate="one_to_one")
    result = result.merge(t3_author, on=TEAM_SEMESTER_KEYS, how="left", validate="one_to_one")

    for component in LATE_INSTABILITY_INDEX_COMPONENTS:
        values = pd.to_numeric(result[component], errors="coerce")
        result[f"{component}_rank_pct"] = values.rank(method="average", pct=True)
    rank_columns = [f"{component}_rank_pct" for component in LATE_INSTABILITY_INDEX_COMPONENTS]
    result["late_instability_component_available_n"] = result[rank_columns].notna().sum(axis=1)
    result["late_instability_component_missing_n"] = len(LATE_INSTABILITY_INDEX_COMPONENTS) - result["late_instability_component_available_n"]
    result["late_instability_index"] = result[rank_columns].mean(axis=1, skipna=True)
    result["late_instability_index_definition"] = "mean_available_percentile_ranks_v1"
    result["late_instability_observation_unit"] = "team_semester"
    result["late_instability_contract_version"] = LATE_INSTABILITY_CONTRACT_VERSION
    return result.sort_values(TEAM_SEMESTER_KEYS).reset_index(drop=True)


def write_late_instability_metrics(
    metrics: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist late instability metrics and their sidecar."""
    required = set(TEAM_SEMESTER_KEYS) | {
        "planning_rework_signal_t2_t3",
        "planning_artifact_activity_t3",
        "pi_line_delta_t3",
        "cc_total_t3",
        "cc_per_source_loc_t3",
        "source_churn_t3",
        "source_events_t3",
        "commits_per_author_t3",
        "delta_dt_t2_t3",
        "late_instability_index",
        "late_instability_observation_unit",
        "late_instability_contract_version",
    }
    missing = required - set(metrics.columns)
    if missing:
        raise ValueError(f"late_instability_metrics output missing columns: {sorted(missing)}")
    if metrics.empty:
        raise ValueError("late_instability_metrics output is empty")
    if metrics.duplicated(TEAM_SEMESTER_KEYS).any():
        raise ValueError("late_instability_metrics has duplicate team-semester keys")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=LATE_INSTABILITY_CONTRACT_VERSION,
        options=options,
    )


def build_late_instability_metrics(
    *,
    analysis_dir: Path = Path("data/analysis"),
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the persisted late instability metrics artifact."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["late_instability_metrics"]["path"]))
    team_entry = CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY["analysis.team_metrics"]
    team_path = analysis_dir / Path(str(team_entry["path"])).name
    team_sidecar = analysis_dir / Path(str(team_entry["metadata_path"])).name
    file_category_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["file_category_churn_metrics"]["path"]))
    file_category_sidecar = file_category_path.with_name(f"{file_category_path.name}.metadata.json")
    author_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["author_pressure_metrics"]["path"]))
    author_sidecar = author_path.with_name(f"{author_path.name}.metadata.json")
    for path in (team_path, file_category_path, author_path):
        _require_success_sidecar(path)
    options = {
        "stage": "late_instability_metrics",
        "contract_version": LATE_INSTABILITY_CONTRACT_VERSION,
        "index_definition": "mean_available_percentile_ranks_v1",
        "index_components": list(LATE_INSTABILITY_INDEX_COMPONENTS),
        "component_missing_policy": "mean_available_ranks_and_count_missing",
        "source_churn_policy": "file_category_source_only_t3",
        "author_pressure_policy": "t3_observed_team_semester_cut",
    }
    checksum = input_checksum(
        [team_path, team_sidecar, file_category_path, file_category_sidecar, author_path, author_sidecar],
        options,
    )
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Late instability metrics artifact is current: %s", output_path)
        return pd.read_parquet(output_path)

    metrics = compute_late_instability_metrics(
        pd.read_parquet(team_path),
        pd.read_parquet(file_category_path),
        pd.read_parquet(author_path),
    )
    invalidate_stale_artifact(output_path, checksum)
    write_late_instability_metrics(metrics, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s late instability observations", len(metrics))
    return metrics


def _t3_source_extras(file_category_churn: pd.DataFrame) -> pd.DataFrame:
    """Return curated T3 source category extras for the cross-evidence panel."""
    required = set(TEAM_SEMESTER_CUT_KEYS) | {"file_category", "event_n", "churn_lines", "category_event_share", "category_churn_share"}
    missing = required - set(file_category_churn.columns)
    if missing:
        raise ValueError(f"file_category_churn_metrics missing columns: {sorted(missing)}")
    source = file_category_churn.loc[
        (file_category_churn["temporal_marker"] == "T3")
        & (file_category_churn["file_category"] == "source")
    ]
    if source.duplicated(TEAM_SEMESTER_KEYS).any():
        raise ValueError("source file-category churn has duplicate T3 team-semester rows")
    return source[TEAM_SEMESTER_KEYS + ["category_event_share", "category_churn_share"]].rename(
        columns={
            "category_event_share": "source_event_share_t3",
            "category_churn_share": "source_churn_share_t3",
        }
    )


def _t3_author_extras(author_pressure: pd.DataFrame) -> pd.DataFrame:
    """Return curated T3 author pressure extras for the cross-evidence panel."""
    required = set(TEAM_SEMESTER_CUT_KEYS) | {"commit_n", "author_n", "max_author_share", "churn_per_author"}
    missing = required - set(author_pressure.columns)
    if missing:
        raise ValueError(f"author_pressure_metrics missing columns: {sorted(missing)}")
    t3_author = author_pressure.loc[author_pressure["temporal_marker"] == "T3"]
    if t3_author.duplicated(TEAM_SEMESTER_KEYS).any():
        raise ValueError("author_pressure_metrics has duplicate T3 team-semester rows")
    return t3_author[TEAM_SEMESTER_KEYS + ["commit_n", "author_n", "max_author_share", "churn_per_author"]].rename(
        columns={
            "commit_n": "commit_n_t3",
            "author_n": "author_n_t3",
            "max_author_share": "max_author_share_t3",
            "churn_per_author": "churn_per_author_t3",
        }
    )


def compute_cross_evidence_panel(
    evaluator_outcomes: pd.DataFrame,
    late_instability: pd.DataFrame,
    author_pressure: pd.DataFrame,
    file_category_churn: pd.DataFrame,
) -> pd.DataFrame:
    """Build the curated team-semester panel for cross-evidence analyses."""
    evaluator_required = set(TEAM_SEMESTER_KEYS) | set(CROSS_EVIDENCE_PANEL_EVALUATOR_COLUMNS)
    late_required = set(TEAM_SEMESTER_KEYS) | set(CROSS_EVIDENCE_PANEL_LATE_COLUMNS)
    missing_evaluator = evaluator_required - set(evaluator_outcomes.columns)
    if missing_evaluator:
        raise ValueError(f"evaluator_outcome_metrics missing columns: {sorted(missing_evaluator)}")
    missing_late = late_required - set(late_instability.columns)
    if missing_late:
        raise ValueError(f"late_instability_metrics missing columns: {sorted(missing_late)}")
    for name, frame in (("evaluator_outcome_metrics", evaluator_outcomes), ("late_instability_metrics", late_instability)):
        if frame[TEAM_SEMESTER_KEYS].isna().any().any():
            raise ValueError(f"{name} team-semester keys must be non-null")
        if frame.duplicated(TEAM_SEMESTER_KEYS).any():
            raise ValueError(f"{name} has duplicate team-semester keys")

    panel = evaluator_outcomes[TEAM_SEMESTER_KEYS + CROSS_EVIDENCE_PANEL_EVALUATOR_COLUMNS].copy()
    panel = panel.merge(
        late_instability[TEAM_SEMESTER_KEYS + CROSS_EVIDENCE_PANEL_LATE_COLUMNS],
        on=TEAM_SEMESTER_KEYS,
        how="left",
        validate="one_to_one",
        indicator="late_join_status",
    )
    if not panel["late_join_status"].eq("both").all():
        raise ValueError("cross_evidence_panel late_instability join lost team-semester coverage")
    panel = panel.drop(columns=["late_join_status"])

    source_extras = _t3_source_extras(file_category_churn)
    panel = panel.merge(
        source_extras,
        on=TEAM_SEMESTER_KEYS,
        how="left",
        validate="one_to_one",
        indicator="source_join_status",
    )
    if not panel["source_join_status"].eq("both").all():
        raise ValueError("cross_evidence_panel source churn join lost team-semester coverage")
    panel = panel.drop(columns=["source_join_status"])

    author_extras = _t3_author_extras(author_pressure)
    panel = panel.merge(
        author_extras,
        on=TEAM_SEMESTER_KEYS,
        how="left",
        validate="one_to_one",
        indicator="author_join_status",
    )
    if not panel["author_join_status"].eq("both").all():
        raise ValueError("cross_evidence_panel author pressure join lost team-semester coverage")
    panel = panel.drop(columns=["author_join_status"])
    panel["cross_evidence_panel_available"] = True
    panel["cross_evidence_panel_observation_unit"] = "team_semester"
    panel["cross_evidence_panel_contract_version"] = CROSS_EVIDENCE_PANEL_CONTRACT_VERSION
    return panel.sort_values(TEAM_SEMESTER_KEYS).reset_index(drop=True)


def write_cross_evidence_panel(
    panel: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist the curated cross-evidence panel and sidecar."""
    required = set(TEAM_SEMESTER_KEYS) | {
        "scope_applicability_mean_t3",
        "project_progress_mean_t3",
        "progress_scope_gap_t3",
        "planning_rework_signal_t2_t3",
        "source_churn_t3",
        "commits_per_author_t3",
        "late_instability_index",
        "cross_evidence_panel_available",
        "cross_evidence_panel_observation_unit",
        "cross_evidence_panel_contract_version",
    }
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"cross_evidence_panel output missing columns: {sorted(missing)}")
    if panel.empty:
        raise ValueError("cross_evidence_panel output is empty")
    if panel.duplicated(TEAM_SEMESTER_KEYS).any():
        raise ValueError("cross_evidence_panel has duplicate team-semester keys")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=CROSS_EVIDENCE_PANEL_CONTRACT_VERSION,
        options=options,
    )


def build_cross_evidence_panel(
    *,
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the curated cross-evidence panel artifact."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_panel"]["path"]))
    evaluator_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["evaluator_outcome_metrics"]["path"]))
    late_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["late_instability_metrics"]["path"]))
    author_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["author_pressure_metrics"]["path"]))
    file_category_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["file_category_churn_metrics"]["path"]))
    inputs = [evaluator_path, late_path, author_path, file_category_path]
    input_paths: list[Path] = []
    for path in inputs:
        _require_success_sidecar(path)
        input_paths.extend([path, path.with_name(f"{path.name}.metadata.json")])
    options = {
        "stage": "cross_evidence_panel",
        "contract_version": CROSS_EVIDENCE_PANEL_CONTRACT_VERSION,
        "panel_shape": "wide_curated_team_semester",
        "base_artifact": "evaluator_outcome_metrics",
        "join_policy": "fail_fast_one_to_one_complete_coverage",
        "t3_source_extras": ["source_event_share_t3", "source_churn_share_t3"],
        "t3_author_extras": ["commit_n_t3", "author_n_t3", "max_author_share_t3", "churn_per_author_t3"],
    }
    checksum = input_checksum(input_paths, options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Cross-evidence panel artifact is current: %s", output_path)
        return pd.read_parquet(output_path)

    panel = compute_cross_evidence_panel(
        pd.read_parquet(evaluator_path),
        pd.read_parquet(late_path),
        pd.read_parquet(author_path),
        pd.read_parquet(file_category_path),
    )
    invalidate_stale_artifact(output_path, checksum)
    write_cross_evidence_panel(panel, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s cross-evidence panel observations", len(panel))
    return panel


def _correlation_verdict(coefficient: float | None, p_value: float | None, expected_direction: str) -> str:
    """Classify whether one exploratory correlation supports its expected direction."""
    if coefficient is None or p_value is None:
        return "unavailable"
    if p_value >= 0.05:
        return "inconclusive"
    if expected_direction == "negative" and coefficient < 0:
        return "supports"
    if expected_direction == "positive" and coefficient > 0:
        return "supports"
    return "contradicts"


def compute_cross_evidence_correlations(panel: pd.DataFrame) -> pd.DataFrame:
    """Run declared Spearman correlations for the cross-evidence panel."""
    if panel[TEAM_SEMESTER_KEYS].isna().any().any():
        raise ValueError("cross_evidence_panel team-semester keys must be non-null")
    rows: list[dict[str, object]] = []
    for analysis_id, spec in CROSS_EVIDENCE_CORRELATION_REGISTRY.items():
        x_name = str(spec["x"])
        y_name = str(spec["y"])
        missing = [column for column in (x_name, y_name) if column not in panel.columns]
        if missing:
            raise ValueError(f"Cross-evidence correlation {analysis_id} has missing columns: {missing}")
        pair = panel[[x_name, y_name]].apply(pd.to_numeric, errors="coerce")
        valid = pair.notna().all(axis=1)
        values = pair.loc[valid]
        n_total = int(len(pair))
        n_valid = int(len(values))
        row: dict[str, object] = {
            "analysis_id": analysis_id,
            "unit_of_analysis": "team_semester",
            "test": "spearman",
            "priority": spec["priority"],
            "x": x_name,
            "y": y_name,
            "expected_direction": spec["expected_direction"],
            "narrative_acts": json.dumps(spec["narrative_acts"]),
            "n_total": n_total,
            "n_valid": n_valid,
            "n_missing": n_total - n_valid,
            "x_missing": int(pair[x_name].isna().sum()),
            "y_missing": int(pair[y_name].isna().sum()),
            "coefficient": pd.NA,
            "p_value": pd.NA,
            "status": "unavailable",
            "reason": None,
            "warning": None,
            "verdict": "unavailable",
            "contract_version": CROSS_EVIDENCE_CORRELATION_CONTRACT_VERSION,
        }
        if n_valid < 3:
            row["reason"] = "insufficient_n"
        elif values[x_name].nunique() < 2 or values[y_name].nunique() < 2:
            row["reason"] = "zero_variance"
        else:
            coefficient, p_value = spearmanr(values[x_name], values[y_name])
            row["coefficient"] = float(coefficient)
            row["p_value"] = float(p_value)
            row["status"] = "success"
            row["warning"] = "small_sample_n_lt_10" if n_valid < 10 else None
            row["verdict"] = _correlation_verdict(float(coefficient), float(p_value), str(spec["expected_direction"]))
        rows.append(row)
    return pd.DataFrame(rows)


def write_cross_evidence_correlations(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist cross-evidence correlations and their sidecar."""
    required = {
        "analysis_id",
        "unit_of_analysis",
        "x",
        "y",
        "test",
        "priority",
        "n_total",
        "n_valid",
        "coefficient",
        "p_value",
        "status",
        "verdict",
        "narrative_acts",
        "contract_version",
    }
    missing = required - set(results.columns)
    if missing:
        raise ValueError(f"cross_evidence_correlations output missing columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("cross_evidence_correlations output is empty")
    if results["analysis_id"].duplicated().any():
        raise ValueError("cross_evidence_correlations has duplicate analysis_id rows")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=CROSS_EVIDENCE_CORRELATION_CONTRACT_VERSION,
        options=options,
    )


def build_cross_evidence_correlations(
    *,
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the persisted cross-evidence correlations result."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_correlations"]["path"]))
    panel_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_panel"]["path"]))
    _require_success_sidecar(panel_path)
    panel_sidecar = panel_path.with_name(f"{panel_path.name}.metadata.json")
    options = {
        "stage": "cross_evidence_correlations",
        "contract_version": CROSS_EVIDENCE_CORRELATION_CONTRACT_VERSION,
        "registry": CROSS_EVIDENCE_CORRELATION_REGISTRY,
        "support_rule": "p_lt_0_05_and_expected_direction",
    }
    checksum = input_checksum([panel_path, panel_sidecar], options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Cross-evidence correlations artifact is current: %s", output_path)
        return pd.read_csv(output_path)

    results = compute_cross_evidence_correlations(pd.read_parquet(panel_path))
    invalidate_stale_artifact(output_path, checksum)
    write_cross_evidence_correlations(results, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s cross-evidence correlation rows", len(results))
    return results


def _cliffs_delta(low_values: pd.Series, high_values: pd.Series) -> float | None:
    """Compute Cliff's delta comparing high group values against low group values."""
    low = pd.to_numeric(low_values, errors="coerce").dropna().tolist()
    high = pd.to_numeric(high_values, errors="coerce").dropna().tolist()
    if not low or not high:
        return None
    greater = 0
    less = 0
    for high_value in high:
        for low_value in low:
            if high_value > low_value:
                greater += 1
            elif high_value < low_value:
                less += 1
    return float((greater - less) / (len(low) * len(high)))


def compute_best_worst_project_contrasts(panel: pd.DataFrame) -> pd.DataFrame:
    """Compare bottom/top project groups for declared score variables."""
    required = set(TEAM_SEMESTER_KEYS) | set(CROSS_EVIDENCE_BEST_WORST_SCORE_VARIABLES) | set(CROSS_EVIDENCE_BEST_WORST_OUTCOME_VARIABLES)
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"cross_evidence_panel missing columns: {sorted(missing)}")
    rows: list[dict[str, object]] = []
    for score_variable in CROSS_EVIDENCE_BEST_WORST_SCORE_VARIABLES:
        scored = panel.dropna(subset=[score_variable]).sort_values([score_variable, *TEAM_SEMESTER_KEYS]).reset_index(drop=True)
        if len(scored) < CROSS_EVIDENCE_BEST_WORST_GROUP_SIZE * 2:
            raise ValueError(f"Not enough rows for best/worst contrast: {score_variable}")
        bottom = scored.head(CROSS_EVIDENCE_BEST_WORST_GROUP_SIZE)
        top = scored.tail(CROSS_EVIDENCE_BEST_WORST_GROUP_SIZE)
        for outcome_variable in CROSS_EVIDENCE_BEST_WORST_OUTCOME_VARIABLES:
            low_values = pd.to_numeric(bottom[outcome_variable], errors="coerce").dropna()
            high_values = pd.to_numeric(top[outcome_variable], errors="coerce").dropna()
            status = "success"
            reason = None
            u_statistic: float | None = None
            p_value: float | None = None
            if len(low_values) < 1 or len(high_values) < 1:
                status = "unavailable"
                reason = "insufficient_group_n"
            elif low_values.nunique() < 2 and high_values.nunique() < 2:
                status = "unavailable"
                reason = "zero_variance"
            else:
                u_statistic, p_value = scipy_stats.mannwhitneyu(low_values, high_values, alternative="two-sided")
                u_statistic = float(u_statistic)
                p_value = float(p_value)
            low_median = float(low_values.median()) if not low_values.empty else pd.NA
            high_median = float(high_values.median()) if not high_values.empty else pd.NA
            rows.append(
                {
                    "contrast_id": f"{score_variable}__{outcome_variable}__top_bottom_4",
                    "unit_of_analysis": "team_semester",
                    "score_variable": score_variable,
                    "outcome_variable": outcome_variable,
                    "group_rule": "top_bottom_fixed_n",
                    "group_size_requested": CROSS_EVIDENCE_BEST_WORST_GROUP_SIZE,
                    "low_group_n": int(len(low_values)),
                    "high_group_n": int(len(high_values)),
                    "low_score_min": float(bottom[score_variable].min()),
                    "low_score_max": float(bottom[score_variable].max()),
                    "high_score_min": float(top[score_variable].min()),
                    "high_score_max": float(top[score_variable].max()),
                    "low_mean": float(low_values.mean()) if not low_values.empty else pd.NA,
                    "low_median": low_median,
                    "high_mean": float(high_values.mean()) if not high_values.empty else pd.NA,
                    "high_median": high_median,
                    "median_difference_high_minus_low": (high_median - low_median) if not pd.isna(low_median) and not pd.isna(high_median) else pd.NA,
                    "cliffs_delta_high_vs_low": _cliffs_delta(low_values, high_values),
                    "test": "mann_whitney_u",
                    "u_statistic": u_statistic,
                    "p_value": p_value,
                    "status": status,
                    "reason": reason,
                    "interpretation": "exploratory_observational",
                    "contract_version": CROSS_EVIDENCE_BEST_WORST_CONTRACT_VERSION,
                }
            )
    return pd.DataFrame(rows)


def write_best_worst_project_contrasts(
    contrasts: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist best/worst project contrasts and sidecar."""
    required = {
        "contrast_id",
        "score_variable",
        "outcome_variable",
        "group_rule",
        "low_group_n",
        "high_group_n",
        "low_median",
        "high_median",
        "cliffs_delta_high_vs_low",
        "test",
        "status",
        "contract_version",
    }
    missing = required - set(contrasts.columns)
    if missing:
        raise ValueError(f"best_worst_project_contrasts output missing columns: {sorted(missing)}")
    if contrasts.empty:
        raise ValueError("best_worst_project_contrasts output is empty")
    if contrasts["contrast_id"].duplicated().any():
        raise ValueError("best_worst_project_contrasts has duplicate contrast_id rows")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    contrasts.to_csv(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=CROSS_EVIDENCE_BEST_WORST_CONTRACT_VERSION,
        options=options,
    )


def build_best_worst_project_contrasts(
    *,
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load persisted best/worst project contrasts."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["best_worst_project_contrasts"]["path"]))
    panel_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_panel"]["path"]))
    _require_success_sidecar(panel_path)
    panel_sidecar = panel_path.with_name(f"{panel_path.name}.metadata.json")
    options = {
        "stage": "best_worst_project_contrasts",
        "contract_version": CROSS_EVIDENCE_BEST_WORST_CONTRACT_VERSION,
        "score_variables": list(CROSS_EVIDENCE_BEST_WORST_SCORE_VARIABLES),
        "outcome_variables": list(CROSS_EVIDENCE_BEST_WORST_OUTCOME_VARIABLES),
        "group_rule": "top_bottom_fixed_n",
        "group_size": CROSS_EVIDENCE_BEST_WORST_GROUP_SIZE,
        "test": "mann_whitney_u_two_sided",
        "effect_size": "cliffs_delta_high_vs_low",
    }
    checksum = input_checksum([panel_path, panel_sidecar], options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Best/worst project contrasts artifact is current: %s", output_path)
        return pd.read_csv(output_path)

    contrasts = compute_best_worst_project_contrasts(pd.read_parquet(panel_path))
    invalidate_stale_artifact(output_path, checksum)
    write_best_worst_project_contrasts(contrasts, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s best/worst contrast rows", len(contrasts))
    return contrasts


def compute_leave_one_out_sensitivity(panel: pd.DataFrame, correlations: pd.DataFrame) -> pd.DataFrame:
    """Summarize leave-one-out sensitivity for declared cross-evidence correlations."""
    if "analysis_id" not in correlations.columns:
        raise ValueError("cross_evidence_correlations missing analysis_id")
    rows: list[dict[str, object]] = []
    for analysis_id, spec in CROSS_EVIDENCE_CORRELATION_REGISTRY.items():
        if analysis_id not in set(correlations["analysis_id"]):
            raise ValueError(f"cross_evidence_correlations missing analysis row: {analysis_id}")
        original = correlations.loc[correlations["analysis_id"] == analysis_id].iloc[0]
        x_name = str(spec["x"])
        y_name = str(spec["y"])
        missing = [column for column in (x_name, y_name) if column not in panel.columns]
        if missing:
            raise ValueError(f"Leave-one-out {analysis_id} has missing columns: {missing}")
        pair = panel[[*TEAM_SEMESTER_KEYS, x_name, y_name]].copy()
        valid_pair = pair[[x_name, y_name]].apply(pd.to_numeric, errors="coerce").notna().all(axis=1)
        pair = pair.loc[valid_pair].reset_index(drop=True)
        coefficients: list[float] = []
        p_values: list[float] = []
        verdicts: list[str] = []
        unavailable_n = 0
        for index in range(len(pair)):
            subset = pair.drop(index=index)
            values = subset[[x_name, y_name]].apply(pd.to_numeric, errors="coerce").dropna()
            if len(values) < 3 or values[x_name].nunique() < 2 or values[y_name].nunique() < 2:
                unavailable_n += 1
                continue
            coefficient, p_value = spearmanr(values[x_name], values[y_name])
            coefficient = float(coefficient)
            p_value = float(p_value)
            coefficients.append(coefficient)
            p_values.append(p_value)
            verdicts.append(_correlation_verdict(coefficient, p_value, str(spec["expected_direction"])))
        tested_n = len(coefficients)
        supports_n = sum(verdict == "supports" for verdict in verdicts)
        if tested_n == 0 or supports_n == 0:
            robustness = "no_support"
        elif supports_n == tested_n and unavailable_n == 0:
            robustness = "robust_all"
        elif supports_n / tested_n >= 0.8:
            robustness = "robust_most"
        else:
            robustness = "fragile"
        rows.append(
            {
                "analysis_id": analysis_id,
                "unit_of_analysis": "team_semester",
                "test": "spearman_leave_one_out",
                "priority": spec["priority"],
                "x": x_name,
                "y": y_name,
                "expected_direction": spec["expected_direction"],
                "narrative_acts": json.dumps(spec["narrative_acts"]),
                "original_coefficient": original.get("coefficient", pd.NA),
                "original_p_value": original.get("p_value", pd.NA),
                "original_verdict": original.get("verdict", pd.NA),
                "loo_total_n": int(len(pair)),
                "loo_tested_n": int(tested_n),
                "loo_unavailable_n": int(unavailable_n),
                "loo_supports_n": int(supports_n),
                "loo_support_share": float(supports_n / tested_n) if tested_n else 0.0,
                "coefficient_min": min(coefficients) if coefficients else pd.NA,
                "coefficient_median": float(pd.Series(coefficients).median()) if coefficients else pd.NA,
                "coefficient_max": max(coefficients) if coefficients else pd.NA,
                "p_value_min": min(p_values) if p_values else pd.NA,
                "p_value_median": float(pd.Series(p_values).median()) if p_values else pd.NA,
                "p_value_max": max(p_values) if p_values else pd.NA,
                "robustness_class": robustness,
                "contract_version": CROSS_EVIDENCE_LEAVE_ONE_OUT_CONTRACT_VERSION,
            }
        )
    return pd.DataFrame(rows)


def write_leave_one_out_sensitivity(
    sensitivity: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist leave-one-out sensitivity results and sidecar."""
    required = {
        "analysis_id",
        "unit_of_analysis",
        "test",
        "loo_total_n",
        "loo_tested_n",
        "loo_supports_n",
        "original_coefficient",
        "original_p_value",
        "original_verdict",
        "coefficient_min",
        "p_value_max",
        "robustness_class",
        "contract_version",
    }
    missing = required - set(sensitivity.columns)
    if missing:
        raise ValueError(f"leave_one_out_sensitivity output missing columns: {sorted(missing)}")
    if sensitivity.empty:
        raise ValueError("leave_one_out_sensitivity output is empty")
    if sensitivity["analysis_id"].duplicated().any():
        raise ValueError("leave_one_out_sensitivity has duplicate analysis_id rows")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sensitivity.to_csv(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=CROSS_EVIDENCE_LEAVE_ONE_OUT_CONTRACT_VERSION,
        options=options,
    )


def build_leave_one_out_sensitivity(
    *,
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load leave-one-out sensitivity results."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["leave_one_out_sensitivity"]["path"]))
    panel_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_panel"]["path"]))
    correlations_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_correlations"]["path"]))
    for path in (panel_path, correlations_path):
        _require_success_sidecar(path)
    options = {
        "stage": "leave_one_out_sensitivity",
        "contract_version": CROSS_EVIDENCE_LEAVE_ONE_OUT_CONTRACT_VERSION,
        "registry": CROSS_EVIDENCE_CORRELATION_REGISTRY,
        "robustness_policy": "robust_all_total_robust_most_ge_0_8_fragile_gt_0_no_support_eq_0",
        "granularity": "one_row_per_analysis",
    }
    checksum = input_checksum(
        [
            panel_path,
            panel_path.with_name(f"{panel_path.name}.metadata.json"),
            correlations_path,
            correlations_path.with_name(f"{correlations_path.name}.metadata.json"),
        ],
        options,
    )
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Leave-one-out sensitivity artifact is current: %s", output_path)
        return pd.read_csv(output_path)

    sensitivity = compute_leave_one_out_sensitivity(pd.read_parquet(panel_path), pd.read_csv(correlations_path))
    invalidate_stale_artifact(output_path, checksum)
    write_leave_one_out_sensitivity(sensitivity, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s leave-one-out sensitivity rows", len(sensitivity))
    return sensitivity


def _ranked_extreme_keys(
    panel: pd.DataFrame,
    variable: str,
    *,
    ascending: bool,
    group_size: int,
) -> list[tuple[str, str]]:
    """Return deterministic anonymized team-semester keys for one extreme."""
    ranked = panel[[*TEAM_SEMESTER_KEYS, variable]].copy()
    ranked[variable] = pd.to_numeric(ranked[variable], errors="coerce")
    ranked = ranked.dropna(subset=[variable]).sort_values(
        [variable, *TEAM_SEMESTER_KEYS], ascending=[ascending, True, True]
    )
    if len(ranked) < group_size:
        raise ValueError(f"Not enough valid rows for extreme ranking: {variable}")
    return [
        (str(row[TEAM_SEMESTER_KEYS[0]]), str(row[TEAM_SEMESTER_KEYS[1]]))
        for row in ranked.head(group_size).to_dict("records")
    ]


def compute_extreme_case_overlap(panel: pd.DataFrame) -> pd.DataFrame:
    """Measure overlap among deterministic top/bottom extreme rankings."""
    required = set(TEAM_SEMESTER_KEYS) | set(CROSS_EVIDENCE_EXTREME_OVERLAP_VARIABLES)
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"cross_evidence_panel missing columns: {sorted(missing)}")
    rankings: dict[str, dict[str, list[tuple[str, str]]]] = {}
    for variable in CROSS_EVIDENCE_EXTREME_OVERLAP_VARIABLES:
        rankings[variable] = {
            "top": _ranked_extreme_keys(
                panel,
                variable,
                ascending=False,
                group_size=CROSS_EVIDENCE_EXTREME_OVERLAP_GROUP_SIZE,
            ),
            "bottom": _ranked_extreme_keys(
                panel,
                variable,
                ascending=True,
                group_size=CROSS_EVIDENCE_EXTREME_OVERLAP_GROUP_SIZE,
            ),
        }

    rows: list[dict[str, object]] = []
    for left_index, left_variable in enumerate(CROSS_EVIDENCE_EXTREME_OVERLAP_VARIABLES):
        for right_variable in CROSS_EVIDENCE_EXTREME_OVERLAP_VARIABLES[left_index + 1:]:
            for mode in CROSS_EVIDENCE_EXTREME_OVERLAP_MODES:
                left_side, right_side = mode.split("_")
                left_keys = set(rankings[left_variable][left_side])
                right_keys = set(rankings[right_variable][right_side])
                overlap = sorted(left_keys & right_keys)
                union_n = len(left_keys | right_keys)
                rows.append(
                    {
                        "overlap_id": f"{left_variable}__{left_side}__{right_variable}__{right_side}",
                        "unit_of_analysis": "team_semester",
                        "left_variable": left_variable,
                        "left_extreme": left_side,
                        "right_variable": right_variable,
                        "right_extreme": right_side,
                        "group_rule": "top_bottom_fixed_n",
                        "group_size_requested": CROSS_EVIDENCE_EXTREME_OVERLAP_GROUP_SIZE,
                        "left_group_n": len(left_keys),
                        "right_group_n": len(right_keys),
                        "overlap_n": len(overlap),
                        "overlap_rate_left": len(overlap) / len(left_keys),
                        "overlap_rate_right": len(overlap) / len(right_keys),
                        "jaccard": len(overlap) / union_n if union_n else 0.0,
                        "overlap_keys": json.dumps(
                            [
                                {TEAM_SEMESTER_KEYS[0]: team, TEAM_SEMESTER_KEYS[1]: semester}
                                for team, semester in overlap
                            ],
                            sort_keys=True,
                        ),
                        "contract_version": CROSS_EVIDENCE_EXTREME_OVERLAP_CONTRACT_VERSION,
                    }
                )
    return pd.DataFrame(rows)


def write_extreme_case_overlap(
    overlap: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist extreme-case overlap results and sidecar."""
    required = {
        "overlap_id",
        "left_variable",
        "left_extreme",
        "right_variable",
        "right_extreme",
        "group_rule",
        "overlap_n",
        "overlap_rate_left",
        "overlap_rate_right",
        "jaccard",
        "overlap_keys",
        "contract_version",
    }
    missing = required - set(overlap.columns)
    if missing:
        raise ValueError(f"extreme_case_overlap output missing columns: {sorted(missing)}")
    if overlap.empty:
        raise ValueError("extreme_case_overlap output is empty")
    if overlap["overlap_id"].duplicated().any():
        raise ValueError("extreme_case_overlap has duplicate overlap_id rows")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    overlap.to_csv(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=CROSS_EVIDENCE_EXTREME_OVERLAP_CONTRACT_VERSION,
        options=options,
    )


def build_extreme_case_overlap(
    *,
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load extreme-case overlap results."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["extreme_case_overlap"]["path"]))
    panel_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_panel"]["path"]))
    _require_success_sidecar(panel_path)
    panel_sidecar = panel_path.with_name(f"{panel_path.name}.metadata.json")
    options = {
        "stage": "extreme_case_overlap",
        "contract_version": CROSS_EVIDENCE_EXTREME_OVERLAP_CONTRACT_VERSION,
        "variables": list(CROSS_EVIDENCE_EXTREME_OVERLAP_VARIABLES),
        "group_rule": "top_bottom_fixed_n",
        "group_size": CROSS_EVIDENCE_EXTREME_OVERLAP_GROUP_SIZE,
        "modes": list(CROSS_EVIDENCE_EXTREME_OVERLAP_MODES),
        "tie_policy": "sort_by_value_then_ID_Equipe_then_Semestre",
        "privacy_policy": "persist_anonymized_team_semester_keys_only",
    }
    checksum = input_checksum([panel_path, panel_sidecar], options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Extreme-case overlap artifact is current: %s", output_path)
        return pd.read_csv(output_path)

    overlap = compute_extreme_case_overlap(pd.read_parquet(panel_path))
    invalidate_stale_artifact(output_path, checksum)
    write_extreme_case_overlap(overlap, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s extreme-case overlap rows", len(overlap))
    return overlap


def _semester_stratification_class(
    global_result: dict[str, object],
    semester_results: list[dict[str, object]],
    expected_direction: str,
) -> str:
    """Classify global versus semester-specific support without overstating replication."""
    global_verdict = str(global_result["verdict"])
    semester_verdicts = [str(result["verdict"]) for result in semester_results]
    coefficients = [result["coefficient"] for result in semester_results if result["coefficient"] is not None]
    signs = {1 if float(coefficient) > 0 else -1 for coefficient in coefficients if float(coefficient) != 0}
    expected_sign = -1 if expected_direction == "negative" else 1
    if len(signs) > 1:
        return "direction_mixed"
    if global_verdict == "supports" and "supports" in semester_verdicts:
        return "global_supported_semester_supported"
    if global_verdict == "supports":
        return "global_supported_semester_inconclusive"
    if global_verdict == "inconclusive" and semester_verdicts and all(verdict == "inconclusive" for verdict in semester_verdicts) and signs == {expected_sign}:
        return "direction_consistent_inconclusive"
    if global_verdict == "inconclusive":
        return "global_inconclusive"
    return "direction_mixed"


def _semester_correlation_result(
    frame: pd.DataFrame,
    *,
    analysis_id: str,
    spec: dict[str, Any],
    stratum: str,
    semester: str | None,
) -> dict[str, object]:
    """Compute one global or semester-stratified Spearman result."""
    x_name = str(spec["x"])
    y_name = str(spec["y"])
    pair = frame[[x_name, y_name]].apply(pd.to_numeric, errors="coerce")
    values = pair.dropna()
    n_total = int(len(pair))
    n_valid = int(len(values))
    warning: str | None = None
    if n_valid < 6:
        warning = "very_small_sample_n_lt_6"
    elif n_valid < 10:
        warning = "small_sample_n_lt_10"
    row: dict[str, object] = {
        "analysis_id": analysis_id,
        "unit_of_analysis": "team_semester",
        "stratum": stratum,
        "semester": semester,
        "test": "spearman",
        "priority": spec["priority"],
        "x": x_name,
        "y": y_name,
        "expected_direction": spec["expected_direction"],
        "narrative_acts": json.dumps(spec["narrative_acts"]),
        "n_total": n_total,
        "n_valid": n_valid,
        "n_missing": n_total - n_valid,
        "coefficient": pd.NA,
        "p_value": pd.NA,
        "status": "unavailable",
        "reason": None,
        "warning": warning,
        "verdict": "unavailable",
        "stratification_class": None,
        "contract_version": CROSS_EVIDENCE_SEMESTER_STRATIFIED_CONTRACT_VERSION,
    }
    if n_valid < 3:
        row["reason"] = "insufficient_n"
    elif values[x_name].nunique() < 2 or values[y_name].nunique() < 2:
        row["reason"] = "zero_variance"
    else:
        coefficient, p_value = spearmanr(values[x_name], values[y_name])
        row["coefficient"] = float(coefficient)
        row["p_value"] = float(p_value)
        row["status"] = "success"
        row["verdict"] = _correlation_verdict(float(coefficient), float(p_value), str(spec["expected_direction"]))
    return row


def compute_semester_stratified_results(panel: pd.DataFrame) -> pd.DataFrame:
    """Repeat declared cross-evidence correlations globally and by semester."""
    required = set(TEAM_SEMESTER_KEYS) | {
        str(spec["x"]) for spec in CROSS_EVIDENCE_CORRELATION_REGISTRY.values()
    } | {str(spec["y"]) for spec in CROSS_EVIDENCE_CORRELATION_REGISTRY.values()}
    missing = required - set(panel.columns)
    if missing:
        raise ValueError(f"cross_evidence_panel missing columns: {sorted(missing)}")
    if panel[TEAM_SEMESTER_KEYS].isna().any().any():
        raise ValueError("cross_evidence_panel team-semester keys must be non-null")

    rows: list[dict[str, object]] = []
    for analysis_id, spec in CROSS_EVIDENCE_CORRELATION_REGISTRY.items():
        global_result = _semester_correlation_result(
            panel,
            analysis_id=analysis_id,
            spec=spec,
            stratum="global",
            semester=None,
        )
        semester_results = [
            _semester_correlation_result(
                group,
                analysis_id=analysis_id,
                spec=spec,
                stratum="semester",
                semester=str(semester),
            )
            for semester, group in sorted(panel.groupby("Semestre", dropna=False), key=lambda item: str(item[0]))
        ]
        classification = _semester_stratification_class(
            global_result,
            semester_results,
            str(spec["expected_direction"]),
        )
        global_result["stratification_class"] = classification
        rows.append(global_result)
        for result in semester_results:
            result["stratification_class"] = classification
            rows.append(result)
    return pd.DataFrame(rows)


def write_semester_stratified_results(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist semester-stratified results and sidecar."""
    required = {
        "analysis_id",
        "stratum",
        "semester",
        "n_total",
        "n_valid",
        "coefficient",
        "p_value",
        "status",
        "warning",
        "verdict",
        "stratification_class",
        "contract_version",
    }
    missing = required - set(results.columns)
    if missing:
        raise ValueError(f"semester_stratified_results output missing columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("semester_stratified_results output is empty")
    if results.duplicated(["analysis_id", "stratum", "semester"]).any():
        raise ValueError("semester_stratified_results has duplicate analysis strata")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=CROSS_EVIDENCE_SEMESTER_STRATIFIED_CONTRACT_VERSION,
        options=options,
    )


def build_semester_stratified_results(
    *,
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load global and semester-stratified correlation results."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["semester_stratified_results"]["path"]))
    panel_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_panel"]["path"]))
    _require_success_sidecar(panel_path)
    panel_sidecar = panel_path.with_name(f"{panel_path.name}.metadata.json")
    options = {
        "stage": "semester_stratified_results",
        "contract_version": CROSS_EVIDENCE_SEMESTER_STRATIFIED_CONTRACT_VERSION,
        "registry": CROSS_EVIDENCE_CORRELATION_REGISTRY,
        "strata": ["global", "observed_semester"],
        "support_rule": "p_lt_0_05_and_expected_direction",
        "warning_policy": {"small_sample": "n_lt_10", "very_small_sample": "n_lt_6"},
    }
    checksum = input_checksum([panel_path, panel_sidecar], options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Semester-stratified results artifact is current: %s", output_path)
        return pd.read_csv(output_path)

    results = compute_semester_stratified_results(pd.read_parquet(panel_path))
    invalidate_stale_artifact(output_path, checksum)
    write_semester_stratified_results(results, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s semester-stratified result rows", len(results))
    return results


def _narrative_acts(value: object) -> str:
    """Normalize a persisted narrative-act value for the priority matrix."""
    if isinstance(value, str):
        return value
    return json.dumps(value if value is not None else [])


def _priority_row(
    *,
    evidence_id: str,
    source_artifact: str,
    source_row_key: str,
    evidence_tier: str,
    evidence_scope: str,
    narrative_acts: object,
    publication_readiness: str,
    recommended_use: str,
    summary: str,
    metric_columns: dict[str, object],
) -> dict[str, object]:
    """Build one normalized evidence-priority row."""
    row: dict[str, object] = {
        "evidence_id": evidence_id,
        "source_artifact": source_artifact,
        "source_row_key": source_row_key,
        "evidence_tier": evidence_tier,
        "evidence_scope": evidence_scope,
        "narrative_acts": _narrative_acts(narrative_acts),
        "publication_readiness": publication_readiness,
        "recommended_use": recommended_use,
        "summary": summary,
        "contract_version": CROSS_EVIDENCE_PRIORITY_MATRIX_CONTRACT_VERSION,
    }
    row.update(metric_columns)
    return row


def _correlation_priority_row(
    row: pd.Series,
    loo_by_analysis: dict[str, pd.Series],
) -> dict[str, object]:
    """Classify one global correlation using its leave-one-out context."""
    analysis_id = str(row["analysis_id"])
    loo = loo_by_analysis.get(analysis_id)
    robustness = str(loo["robustness_class"]) if loo is not None else "unavailable"
    supports = str(row["verdict"]) == "supports"
    robust = robustness in {"robust_all", "robust_most"}
    if supports and robust:
        tier, readiness, use = "A", "candidate_primary", "anchor_narrative_claim"
        summary = "Supported global correlation with leave-one-out robustness."
    elif supports:
        tier, readiness, use = "B", "candidate_secondary", "support_narrative_claim"
        summary = "Supported global correlation without strong robustness confirmation."
    else:
        tier, readiness, use = "C", "exploratory_only", "do_not_generalize"
        summary = "Global correlation is inconclusive or does not support the expected direction."
    return _priority_row(
        evidence_id=f"correlation__{analysis_id}",
        source_artifact="cross_evidence_correlations",
        source_row_key=analysis_id,
        evidence_tier=tier,
        evidence_scope="global_cross_evidence",
        narrative_acts=row["narrative_acts"],
        publication_readiness=readiness,
        recommended_use=use,
        summary=summary,
        metric_columns={
            "analysis_id": analysis_id,
            "stratum": "global",
            "semester": pd.NA,
            "priority": row["priority"],
            "x": row["x"],
            "y": row["y"],
            "coefficient": row["coefficient"],
            "p_value": row["p_value"],
            "verdict": row["verdict"],
            "robustness_class": robustness,
            "overlap_n": pd.NA,
            "jaccard": pd.NA,
        },
    )


def compute_evidence_priority_matrix(
    correlations: pd.DataFrame,
    contrasts: pd.DataFrame,
    leave_one_out: pd.DataFrame,
    overlap: pd.DataFrame,
    semester_stratified: pd.DataFrame,
) -> pd.DataFrame:
    """Consolidate CE-3.1 through CE-3.5 into an evidence-priority matrix."""
    required_inputs = {
        "cross_evidence_correlations": {"analysis_id", "narrative_acts", "priority", "x", "y", "coefficient", "p_value", "verdict"},
        "best_worst_project_contrasts": {"contrast_id", "score_variable", "outcome_variable", "p_value", "status", "interpretation"},
        "leave_one_out_sensitivity": {"analysis_id", "robustness_class", "loo_supports_n", "loo_tested_n"},
        "extreme_case_overlap": {"overlap_id", "left_variable", "left_extreme", "right_variable", "right_extreme", "overlap_n", "jaccard"},
        "semester_stratified_results": {"analysis_id", "stratum", "semester", "n_valid", "coefficient", "p_value", "verdict", "stratification_class", "warning"},
    }
    frames = {
        "cross_evidence_correlations": correlations,
        "best_worst_project_contrasts": contrasts,
        "leave_one_out_sensitivity": leave_one_out,
        "extreme_case_overlap": overlap,
        "semester_stratified_results": semester_stratified,
    }
    for artifact, required in required_inputs.items():
        missing = required - set(frames[artifact].columns)
        if missing:
            raise ValueError(f"{artifact} missing columns: {sorted(missing)}")
        if frames[artifact].empty:
            raise ValueError(f"{artifact} input is empty")

    loo_by_analysis = leave_one_out.set_index("analysis_id").to_dict("index")
    rows: list[dict[str, object]] = []
    for _, source_row in correlations.iterrows():
        rows.append(_correlation_priority_row(source_row, {key: pd.Series(value) for key, value in loo_by_analysis.items()}))

    for _, source_row in contrasts.iterrows():
        significant = source_row["status"] == "success" and pd.notna(source_row["p_value"]) and float(source_row["p_value"]) < 0.05
        rows.append(
            _priority_row(
                evidence_id=f"contrast__{source_row['contrast_id']}",
                source_artifact="best_worst_project_contrasts",
                source_row_key=str(source_row["contrast_id"]),
                evidence_tier="B",
                evidence_scope="top_bottom_exploratory_contrast",
                narrative_acts="[3]",
                publication_readiness="candidate_secondary" if significant else "exploratory_only",
                recommended_use="support_narrative_claim" if significant else "do_not_generalize",
                summary="Best/worst contrast provides exploratory group-level support." if significant else "Best/worst contrast is exploratory and not statistically supported.",
                metric_columns={
                    "analysis_id": source_row["contrast_id"],
                    "stratum": "top_bottom",
                    "semester": pd.NA,
                    "priority": pd.NA,
                    "x": source_row["score_variable"],
                    "y": source_row["outcome_variable"],
                    "coefficient": pd.NA,
                    "p_value": source_row["p_value"],
                    "verdict": "supports" if significant else "inconclusive",
                    "robustness_class": pd.NA,
                    "overlap_n": pd.NA,
                    "jaccard": pd.NA,
                },
            )
        )

    for _, source_row in leave_one_out.iterrows():
        robust = source_row["robustness_class"] in {"robust_all", "robust_most"}
        rows.append(
            _priority_row(
                evidence_id=f"leave_one_out__{source_row['analysis_id']}",
                source_artifact="leave_one_out_sensitivity",
                source_row_key=str(source_row["analysis_id"]),
                evidence_tier="A" if robust else "C",
                evidence_scope="robustness_diagnostic",
                narrative_acts="[2, 3]",
                publication_readiness="candidate_secondary" if robust else "exploratory_only",
                recommended_use="guide_refactoring" if robust else "report_methodological_limitation",
                summary="Leave-one-out analysis confirms stability." if robust else "Leave-one-out analysis indicates fragile or unsupported evidence.",
                metric_columns={
                    "analysis_id": source_row["analysis_id"],
                    "stratum": "leave_one_out",
                    "semester": pd.NA,
                    "priority": pd.NA,
                    "x": pd.NA,
                    "y": pd.NA,
                    "coefficient": source_row.get("original_coefficient", pd.NA),
                    "p_value": source_row.get("original_p_value", pd.NA),
                    "verdict": source_row.get("original_verdict", pd.NA),
                    "robustness_class": source_row["robustness_class"],
                    "overlap_n": pd.NA,
                    "jaccard": pd.NA,
                },
            )
        )

    for _, source_row in overlap.iterrows():
        meaningful = int(source_row["overlap_n"]) >= 2
        rows.append(
            _priority_row(
                evidence_id=f"overlap__{source_row['overlap_id']}",
                source_artifact="extreme_case_overlap",
                source_row_key=str(source_row["overlap_id"]),
                evidence_tier="B",
                evidence_scope="ranked_extreme_case_overlap",
                narrative_acts="[2, 3]",
                publication_readiness="candidate_secondary" if meaningful else "exploratory_only",
                recommended_use="describe_tail_convergence" if meaningful else "do_not_generalize",
                summary="Extreme-case overlap supports convergence of tails." if meaningful else "Extreme-case overlap is weak and should remain descriptive.",
                metric_columns={
                    "analysis_id": source_row["overlap_id"],
                    "stratum": f"{source_row['left_extreme']}_{source_row['right_extreme']}",
                    "semester": pd.NA,
                    "priority": pd.NA,
                    "x": source_row["left_variable"],
                    "y": source_row["right_variable"],
                    "coefficient": pd.NA,
                    "p_value": pd.NA,
                    "verdict": "supports" if meaningful else "inconclusive",
                    "robustness_class": pd.NA,
                    "overlap_n": source_row["overlap_n"],
                    "jaccard": source_row["jaccard"],
                },
            )
        )

    for _, source_row in semester_stratified.iterrows():
        small_sample = pd.notna(source_row["warning"])
        supports = source_row["verdict"] == "supports"
        rows.append(
            _priority_row(
                evidence_id=f"semester__{source_row['analysis_id']}__{source_row['stratum']}__{source_row['semester'] if pd.notna(source_row['semester']) else 'global'}",
                source_artifact="semester_stratified_results",
                source_row_key=f"{source_row['analysis_id']}__{source_row['stratum']}__{source_row['semester']}",
                evidence_tier="C",
                evidence_scope="semester_stratified_methodological_warning",
                narrative_acts=source_row["narrative_acts"],
                publication_readiness="exploratory_only",
                recommended_use="report_methodological_limitation" if small_sample else ("support_narrative_claim" if supports else "do_not_generalize"),
                summary="Semester-stratified result requires contextualized interpretation." if small_sample else "Global/semester comparison provides contextual evidence.",
                metric_columns={
                    "analysis_id": source_row["analysis_id"],
                    "stratum": source_row["stratum"],
                    "semester": source_row["semester"],
                    "priority": source_row["priority"],
                    "x": source_row["x"],
                    "y": source_row["y"],
                    "coefficient": source_row["coefficient"],
                    "p_value": source_row["p_value"],
                    "verdict": source_row["verdict"],
                    "robustness_class": source_row["stratification_class"],
                    "overlap_n": pd.NA,
                    "jaccard": pd.NA,
                },
            )
        )
    return pd.DataFrame(rows)


def write_evidence_priority_matrix(
    matrix: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist the evidence-priority matrix and sidecar."""
    required = {
        "evidence_id",
        "source_artifact",
        "evidence_tier",
        "evidence_scope",
        "narrative_acts",
        "publication_readiness",
        "recommended_use",
        "summary",
        "contract_version",
    }
    missing = required - set(matrix.columns)
    if missing:
        raise ValueError(f"evidence_priority_matrix output missing columns: {sorted(missing)}")
    if matrix.empty:
        raise ValueError("evidence_priority_matrix output is empty")
    if matrix["evidence_id"].duplicated().any():
        raise ValueError("evidence_priority_matrix has duplicate evidence_id rows")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=CROSS_EVIDENCE_PRIORITY_MATRIX_CONTRACT_VERSION,
        options=options,
    )


def build_evidence_priority_matrix(
    *,
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the consolidated evidence-priority matrix."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["evidence_priority_matrix"]["path"]))
    input_paths: list[Path] = []
    for artifact in EVIDENCE_PRIORITY_SOURCE_ARTIFACTS:
        source_path = Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY[artifact]["path"]))
        _require_success_sidecar(source_path)
        input_paths.extend([source_path, source_path.with_name(f"{source_path.name}.metadata.json")])
    options = {
        "stage": "evidence_priority_matrix",
        "contract_version": CROSS_EVIDENCE_PRIORITY_MATRIX_CONTRACT_VERSION,
        "source_artifacts": list(EVIDENCE_PRIORITY_SOURCE_ARTIFACTS),
        "granularity": "one_row_per_atomic_evidence_result",
        "tier_policy": "A_primary_robust_support_B_secondary_exploratory_C_limitation_or_inconclusive",
        "publication_readiness_values": ["candidate_primary", "candidate_secondary", "exploratory_only"],
    }
    checksum = input_checksum(input_paths, options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Evidence-priority matrix artifact is current: %s", output_path)
        return pd.read_csv(output_path)

    source_frames = {
        artifact: pd.read_csv(Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY[artifact]["path"])))
        for artifact in EVIDENCE_PRIORITY_SOURCE_ARTIFACTS
    }
    matrix = compute_evidence_priority_matrix(
        source_frames["cross_evidence_correlations"],
        source_frames["best_worst_project_contrasts"],
        source_frames["leave_one_out_sensitivity"],
        source_frames["extreme_case_overlap"],
        source_frames["semester_stratified_results"],
    )
    invalidate_stale_artifact(output_path, checksum)
    write_evidence_priority_matrix(matrix, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s evidence-priority matrix rows", len(matrix))
    return matrix


def compute_file_category_churn_metrics(files: pd.DataFrame) -> pd.DataFrame:
    """Aggregate Git file events by team, semester, cut, and file category."""
    missing = FILE_CATEGORY_CHURN_REQUIRED_COLUMNS - set(files.columns)
    if missing:
        raise ValueError(f"git_files missing columns: {sorted(missing)}")
    if files[["ID_Equipe", "Semestre", "temporal_marker"]].isna().any().any():
        raise ValueError("git_files team-semester-cut keys must be non-null")

    working = files.copy()
    classifications = [
        classify_file_category(
            row.file_path,
            row.file_extension,
            row.change_status,
            row.file_path_old,
        )
        for row in working[["file_path", "file_extension", "change_status", "file_path_old"]].itertuples(index=False)
    ]
    classified = pd.concat([working.reset_index(drop=True), pd.DataFrame(classifications)], axis=1)
    classified["lines_added_missing"] = classified["lines_added"].isna()
    classified["lines_deleted_missing"] = classified["lines_deleted"].isna()
    classified["lines_added_observed"] = pd.to_numeric(classified["lines_added"], errors="coerce").fillna(0)
    classified["lines_deleted_observed"] = pd.to_numeric(classified["lines_deleted"], errors="coerce").fillna(0)
    if (classified["lines_added_observed"] < 0).any() or (classified["lines_deleted_observed"] < 0).any():
        raise ValueError("git_files line counts must not be negative")
    classified["churn_lines"] = classified["lines_added_observed"] + classified["lines_deleted_observed"]
    classified["category_warning_present"] = classified["category_warning"].notna()
    classified["is_binary_bool"] = classified["is_binary"].fillna(False).astype(bool)

    grouped = classified.groupby(FILE_CATEGORY_CHURN_GROUP_COLUMNS, dropna=False)
    result = grouped.agg(
        event_n=("file_path", "size"),
        added_event_n=("change_status", lambda values: int((values == "added").sum())),
        deleted_event_n=("change_status", lambda values: int((values == "deleted").sum())),
        modified_event_n=("change_status", lambda values: int((values == "modified").sum())),
        renamed_event_n=("change_status", lambda values: int((values == "renamed").sum())),
        copied_event_n=("change_status", lambda values: int((values == "copied").sum())),
        binary_event_n=("is_binary_bool", "sum"),
        lines_added=("lines_added_observed", "sum"),
        lines_deleted=("lines_deleted_observed", "sum"),
        churn_lines=("churn_lines", "sum"),
        line_count_missing_event_n=("lines_added_missing", "sum"),
        category_warning_event_n=("category_warning_present", "sum"),
        category_confidence_mean=("category_confidence", "mean"),
    ).reset_index()

    denominators = result.groupby(["ID_Equipe", "Semestre", "temporal_marker"], dropna=False).agg(
        total_event_n=("event_n", "sum"),
        total_churn_lines=("churn_lines", "sum"),
    ).reset_index()
    result = result.merge(denominators, on=["ID_Equipe", "Semestre", "temporal_marker"], validate="many_to_one")
    result["category_event_share"] = result["event_n"] / result["total_event_n"]
    result["category_churn_share"] = result["churn_lines"] / result["total_churn_lines"].where(result["total_churn_lines"] != 0)
    result["category_churn_share"] = result["category_churn_share"].fillna(0)
    result["file_category_definition_version"] = FILE_CATEGORY_DEFINITION_VERSION
    result["contract_version"] = FILE_CATEGORY_CHURN_CONTRACT_VERSION
    return result.sort_values(FILE_CATEGORY_CHURN_GROUP_COLUMNS).reset_index(drop=True)


def write_file_category_churn_metrics(
    metrics: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist file-category churn metrics and their sidecar."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=FILE_CATEGORY_CHURN_CONTRACT_VERSION,
        options=options,
    )


def build_file_category_churn_metrics(
    *,
    lake_dir: Path = Path("data/lake"),
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the persisted file-category churn metrics artifact."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["file_category_churn_metrics"]["path"]))
    git_files_input = CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY["lake.git_files"]
    git_files_path = lake_dir / Path(str(git_files_input["path"])).name
    git_files_sidecar = lake_dir / Path(str(git_files_input["metadata_path"])).name
    _require_success_sidecar(git_files_path)
    options = {
        "stage": "file_category_churn_metrics",
        "contract_version": FILE_CATEGORY_CHURN_CONTRACT_VERSION,
        "file_category_definition_version": FILE_CATEGORY_DEFINITION_VERSION,
        "line_count_missing_policy": "fill_zero_and_count_missing_events",
        "share_denominator": "team_semester_cut",
        "materialize_unobserved_categories": False,
    }
    checksum = input_checksum([git_files_path, git_files_sidecar], options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("File-category churn metrics artifact is current: %s", output_path)
        return pd.read_parquet(output_path)

    files = pd.read_parquet(git_files_path)
    metrics = compute_file_category_churn_metrics(files)
    invalidate_stale_artifact(output_path, checksum)
    write_file_category_churn_metrics(metrics, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s file-category churn observations", len(metrics))
    return metrics


def _affected_key_sample(frame: pd.DataFrame, *, limit: int = EXCLUSIONS_AFFECTED_KEY_SAMPLE_LIMIT) -> list[dict[str, object]]:
    """Return a bounded stable sample of affected anonymized observation keys."""
    key_columns = ["ID_Equipe", "Semestre", "temporal_marker", "file_category"]
    if frame.empty:
        return []
    return [
        {column: row[column] for column in key_columns}
        for row in frame[key_columns].drop_duplicates().sort_values(key_columns).head(limit).to_dict("records")
    ]


def build_file_category_exclusions_payload(metrics: pd.DataFrame, *, source_checksum: str) -> dict[str, Any]:
    """Build the CE-1.4 exclusions/warnings payload from aggregate metrics."""
    unknown_rows = metrics.loc[metrics["file_category"] == "unknown"]
    missing_line_rows = metrics.loc[metrics["line_count_missing_event_n"] > 0]
    warning_rows = metrics.loc[metrics["category_warning_event_n"] > 0]
    low_confidence_rows = metrics.loc[metrics["category_confidence_mean"] < NORMAL_CONFIDENCE]
    sections = [
        (
            "unknown_file_category",
            unknown_rows,
            "event_n",
            "File events classified as unknown by the versioned taxonomy.",
        ),
        (
            "missing_line_counts",
            missing_line_rows,
            "line_count_missing_event_n",
            "File events whose line counts were missing and treated as zero for churn aggregation.",
        ),
        (
            "category_warnings",
            warning_rows,
            "category_warning_event_n",
            "File events classified with a taxonomy warning.",
        ),
        (
            "low_confidence_categories",
            low_confidence_rows,
            "event_n",
            "Aggregate categories whose mean classification confidence is below 1.0.",
        ),
    ]
    exclusions: list[dict[str, object]] = []
    for reason, frame, count_column, description in sections:
        n_affected_rows = int(len(frame))
        n_affected_events = int(frame[count_column].sum()) if n_affected_rows else 0
        exclusions.append(
            {
                "dataset": "file_category_churn_metrics",
                "reason": reason,
                "description": description,
                "unit_of_analysis": "team_semester_cut_category",
                "n_affected_rows": n_affected_rows,
                "n_affected_events": n_affected_events,
                "affected_keys_sample_limit": EXCLUSIONS_AFFECTED_KEY_SAMPLE_LIMIT,
                "affected_keys_sample": _affected_key_sample(frame),
            }
        )

    categories = metrics.groupby("file_category", dropna=False).agg(
        rows=("file_category", "size"),
        events=("event_n", "sum"),
        churn_lines=("churn_lines", "sum"),
        line_count_missing_events=("line_count_missing_event_n", "sum"),
        warning_events=("category_warning_event_n", "sum"),
    ).reset_index().sort_values("file_category")
    summary = {
        "rows": int(len(metrics)),
        "event_n": int(metrics["event_n"].sum()),
        "line_count_missing_event_n": int(metrics["line_count_missing_event_n"].sum()),
        "category_warning_event_n": int(metrics["category_warning_event_n"].sum()),
        "unknown_event_n": int(unknown_rows["event_n"].sum()) if not unknown_rows.empty else 0,
        "exclusion_reasons": {
            item["reason"]: item["n_affected_events"]
            for item in exclusions
        },
    }
    return {
        "status": "success",
        "contract_version": FILE_CATEGORY_EXCLUSIONS_CONTRACT_VERSION,
        "schema_version": FILE_CATEGORY_EXCLUSIONS_SCHEMA_VERSION,
        "input_checksum": source_checksum,
        "scope": "cross_evidence_file_category_taxonomy",
        "file_category_definition_version": FILE_CATEGORY_DEFINITION_VERSION,
        "summary": summary,
        "options": {
            "stage": "file_category_exclusions",
            "source_artifact": "file_category_churn_metrics",
            "schema_version": FILE_CATEGORY_EXCLUSIONS_SCHEMA_VERSION,
            "affected_key_sample_limit": EXCLUSIONS_AFFECTED_KEY_SAMPLE_LIMIT,
            "raw_text_policy": "no_raw_text_fields_read_or_persisted",
        },
        "sources": {
            "file_category_churn_metrics": {
                "rows": summary["rows"],
                "event_n": summary["event_n"],
                "line_count_missing_event_n": summary["line_count_missing_event_n"],
                "category_warning_event_n": summary["category_warning_event_n"],
                "unknown_event_n": summary["unknown_event_n"],
                "categories": categories.to_dict("records"),
            }
        },
        "exclusions": exclusions,
    }


def write_json_artifact(payload: dict[str, Any], output_path: Path, *, source_checksum: str, options: dict[str, Any]) -> None:
    """Persist a JSON artifact with a success sidecar."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=str(payload.get("contract_version", CROSS_EVIDENCE_CONTRACT_VERSION)),
        options=options,
    )


def build_file_category_exclusions_report(
    *,
    metrics_path: Path | None = None,
    output_path: Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Build or load the CE-1.4 exclusions/warnings report."""
    metrics_path = metrics_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["file_category_churn_metrics"]["path"]))
    output_path = output_path or Path(CROSS_EVIDENCE_EXCLUSIONS_PATH)
    metrics_sidecar = metrics_path.with_name(f"{metrics_path.name}.metadata.json")
    _require_success_sidecar(metrics_path)
    options = {
        "stage": "file_category_exclusions",
        "contract_version": FILE_CATEGORY_EXCLUSIONS_CONTRACT_VERSION,
        "schema_version": FILE_CATEGORY_EXCLUSIONS_SCHEMA_VERSION,
        "file_category_definition_version": FILE_CATEGORY_DEFINITION_VERSION,
        "source_artifact": metrics_path.as_posix(),
        "affected_key_sample_limit": EXCLUSIONS_AFFECTED_KEY_SAMPLE_LIMIT,
    }
    checksum = input_checksum([metrics_path, metrics_sidecar], options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("File-category exclusions report is current: %s", output_path)
        return json.loads(output_path.read_text(encoding="utf-8"))

    metrics = pd.read_parquet(metrics_path)
    payload = build_file_category_exclusions_payload(metrics, source_checksum=checksum)
    invalidate_stale_artifact(output_path, checksum)
    write_json_artifact(payload, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote file-category exclusions report: %s", output_path)
    return payload


def build_cross_evidence_manifest(
    *,
    output_path: Path | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Persist an auditable inventory of the engine-owned cross-evidence outputs."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["cross_evidence_manifest"]["path"]))
    engine_entries = {
        artifact_id: entry
        for artifact_id, entry in CROSS_EVIDENCE_ARTIFACT_REGISTRY.items()
        if entry.get("producer_script") == "08_cross_evidence_engine.py"
        and artifact_id != "cross_evidence_manifest"
    }
    inventory: dict[str, dict[str, Any]] = {}
    source_paths: list[Path] = []
    missing_artifacts: list[str] = []
    for artifact_id, entry in engine_entries.items():
        artifact_path = Path(str(entry["path"]))
        record: dict[str, Any] = {
            "artifact_id": artifact_id,
            "kind": entry.get("kind"),
            "path": artifact_path.as_posix(),
            "contract_version": entry.get("contract_version"),
            "unit_of_analysis": entry.get("unit_of_analysis"),
            "evidence_scope": entry.get("evidence_scope"),
            "evidence_type": entry.get("evidence_type"),
            "status": "success" if artifact_path.exists() else "missing",
        }
        if artifact_path.is_file():
            sidecar_path = artifact_path.with_name(f"{artifact_path.name}.metadata.json")
            record["checksum"] = file_checksum(artifact_path)
            record["sidecar_path"] = sidecar_path.as_posix()
            record["sidecar_status"] = "missing"
            if sidecar_path.is_file():
                sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
                record["sidecar_status"] = sidecar.get("status")
                record["sidecar_contract_version"] = sidecar.get("contract_version")
                source_paths.extend([artifact_path, sidecar_path])
            else:
                record["status"] = "invalid"
        elif artifact_path.is_dir():
            files = sorted(path for path in artifact_path.rglob("*") if path.is_file())
            record["file_count"] = len(files)
            record["files"] = [path.as_posix() for path in files]
            source_paths.extend(files)
        else:
            missing_artifacts.append(artifact_id)
        if record["status"] != "success":
            missing_artifacts.append(artifact_id)
        inventory[artifact_id] = record

    options = {
        "stage": "cross_evidence_manifest",
        "manifest_version": CROSS_EVIDENCE_MANIFEST_VERSION,
        "engine_script": "08_cross_evidence_engine.py",
        "artifact_count": len(engine_entries),
    }
    checksum = input_checksum(source_paths, options)
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Cross-evidence manifest is current: %s", output_path)
        return json.loads(output_path.read_text(encoding="utf-8"))
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")

    payload = {
        "status": "success" if not missing_artifacts else "partial",
        "contract_version": CROSS_EVIDENCE_MANIFEST_VERSION,
        "manifest_version": CROSS_EVIDENCE_MANIFEST_VERSION,
        "scope": "secondary_exploratory_evidence",
        "producer_script": "08_cross_evidence_engine.py",
        "input_checksum": checksum,
        "missing_artifacts": sorted(set(missing_artifacts)),
        "artifacts": inventory,
    }
    write_json_artifact(payload, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote cross-evidence manifest: %s", output_path)
    return payload


def main() -> None:
    """Run the currently implemented cross-evidence artifact builders."""
    parser = argparse.ArgumentParser(description="Build cross-evidence extension artifacts")
    parser.add_argument("--lake-dir", type=Path, default=Path("data/lake"))
    parser.add_argument("--analysis-dir", type=Path, default=Path("data/analysis"))
    parser.add_argument("--evaluator-outcome-output", type=Path, default=None)
    parser.add_argument("--author-pressure-output", type=Path, default=None)
    parser.add_argument("--temporal-escalation-output", type=Path, default=None)
    parser.add_argument("--late-instability-output", type=Path, default=None)
    parser.add_argument("--cross-evidence-panel-output", type=Path, default=None)
    parser.add_argument("--cross-evidence-correlations-output", type=Path, default=None)
    parser.add_argument("--best-worst-contrasts-output", type=Path, default=None)
    parser.add_argument("--leave-one-out-sensitivity-output", type=Path, default=None)
    parser.add_argument("--extreme-case-overlap-output", type=Path, default=None)
    parser.add_argument("--semester-stratified-output", type=Path, default=None)
    parser.add_argument("--evidence-priority-matrix-output", type=Path, default=None)
    parser.add_argument("--scope-vs-late-instability-data-output", type=Path, default=None)
    parser.add_argument("--source-churn-vs-planning-rework-data-output", type=Path, default=None)
    parser.add_argument("--temporal-escalation-data-output", type=Path, default=None)
    parser.add_argument("--file-category-churn-data-output", type=Path, default=None)
    parser.add_argument("--author-pressure-vs-churn-data-output", type=Path, default=None)
    parser.add_argument("--pareto-extreme-cases-data-output", type=Path, default=None)
    parser.add_argument("--leave-one-out-robustness-data-output", type=Path, default=None)
    parser.add_argument("--file-category-churn-output", type=Path, default=None)
    parser.add_argument("--file-category-exclusions-output", type=Path, default=None)
    parser.add_argument("--manifest-output", type=Path, default=None)
    parser.add_argument(
        "--only",
        choices=[
            "evaluator_outcome_metrics",
            "author_pressure_metrics",
            "temporal_escalation_metrics",
            "late_instability_metrics",
            "cross_evidence_panel",
            "cross_evidence_correlations",
            "best_worst_project_contrasts",
            "leave_one_out_sensitivity",
            "extreme_case_overlap",
            "semester_stratified_results",
            "evidence_priority_matrix",
            "scope_vs_late_instability",
            "source_churn_vs_planning_rework",
            "temporal_escalation_panel",
            "file_category_churn_by_cut",
            "author_pressure_vs_churn",
            "pareto_extreme_cases",
            "leave_one_out_robustness",
            "file_category_churn_metrics",
            "file_category_exclusions",
            "cross_evidence_manifest",
        ],
        nargs="+",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    selected = set(args.only or [
        "evaluator_outcome_metrics",
        "author_pressure_metrics",
        "temporal_escalation_metrics",
        "late_instability_metrics",
        "cross_evidence_panel",
        "cross_evidence_correlations",
        "best_worst_project_contrasts",
        "leave_one_out_sensitivity",
        "extreme_case_overlap",
        "semester_stratified_results",
        "evidence_priority_matrix",
        "scope_vs_late_instability",
        "source_churn_vs_planning_rework",
        "temporal_escalation_panel",
        "file_category_churn_by_cut",
        "author_pressure_vs_churn",
        "pareto_extreme_cases",
        "leave_one_out_robustness",
        "file_category_churn_metrics",
        "file_category_exclusions",
        "cross_evidence_manifest",
    ])
    _configure_runtime_paths(analysis_dir=args.analysis_dir, lake_dir=args.lake_dir)
    metrics_path = args.file_category_churn_output
    if "evaluator_outcome_metrics" in selected:
        build_evaluator_outcome_metrics(
            lake_dir=args.lake_dir,
            output_path=args.evaluator_outcome_output,
            force=args.force,
        )
    if "author_pressure_metrics" in selected:
        build_author_pressure_metrics(
            lake_dir=args.lake_dir,
            output_path=args.author_pressure_output,
            force=args.force,
        )
    if "temporal_escalation_metrics" in selected:
        build_temporal_escalation_metrics(
            analysis_dir=args.analysis_dir,
            output_path=args.temporal_escalation_output,
            force=args.force,
        )
    if "late_instability_metrics" in selected:
        build_late_instability_metrics(
            analysis_dir=args.analysis_dir,
            output_path=args.late_instability_output,
            force=args.force,
        )
    if "cross_evidence_panel" in selected:
        build_cross_evidence_panel(
            output_path=args.cross_evidence_panel_output,
            force=args.force,
        )
    if "cross_evidence_correlations" in selected:
        build_cross_evidence_correlations(
            output_path=args.cross_evidence_correlations_output,
            force=args.force,
        )
    if "best_worst_project_contrasts" in selected:
        build_best_worst_project_contrasts(
            output_path=args.best_worst_contrasts_output,
            force=args.force,
        )
    if "leave_one_out_sensitivity" in selected:
        build_leave_one_out_sensitivity(
            output_path=args.leave_one_out_sensitivity_output,
            force=args.force,
        )
    if "extreme_case_overlap" in selected:
        build_extreme_case_overlap(
            output_path=args.extreme_case_overlap_output,
            force=args.force,
        )
    if "semester_stratified_results" in selected:
        build_semester_stratified_results(
            output_path=args.semester_stratified_output,
            force=args.force,
        )
    if "evidence_priority_matrix" in selected:
        build_evidence_priority_matrix(
            output_path=args.evidence_priority_matrix_output,
            force=args.force,
        )
    if "scope_vs_late_instability" in selected:
        build_scope_vs_late_instability_figure(
            output_data_path=args.scope_vs_late_instability_data_output,
            force=args.force,
        )
    if "source_churn_vs_planning_rework" in selected:
        build_source_churn_vs_planning_rework_figure(
            output_data_path=args.source_churn_vs_planning_rework_data_output,
            force=args.force,
        )
    if "temporal_escalation_panel" in selected:
        build_temporal_escalation_figure(
            output_data_path=args.temporal_escalation_data_output,
            force=args.force,
        )
    if "file_category_churn_by_cut" in selected:
        build_file_category_churn_figure(
            output_data_path=args.file_category_churn_data_output,
            force=args.force,
        )
    if "author_pressure_vs_churn" in selected:
        build_author_pressure_vs_churn_figure(
            output_data_path=args.author_pressure_vs_churn_data_output,
            force=args.force,
        )
    if "pareto_extreme_cases" in selected:
        build_pareto_extreme_cases_figure(
            output_data_path=args.pareto_extreme_cases_data_output,
            force=args.force,
        )
    if "leave_one_out_robustness" in selected:
        build_leave_one_out_robustness_figure(
            output_data_path=args.leave_one_out_robustness_data_output,
            force=args.force,
        )
    if "file_category_churn_metrics" in selected:
        build_file_category_churn_metrics(
            lake_dir=args.lake_dir,
            output_path=args.file_category_churn_output,
            force=args.force,
        )
    if "file_category_exclusions" in selected:
        build_file_category_exclusions_report(
            metrics_path=metrics_path,
            output_path=args.file_category_exclusions_output,
            force=args.force,
        )
    if "cross_evidence_manifest" in selected:
        build_cross_evidence_manifest(
            output_path=args.manifest_output,
            force=args.force,
        )


if __name__ == "__main__":
    main()
