"""Generate team-semester complexity profiles for confounding analysis."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.artifact_policy import CURRENT_POLICY_VERSION, is_clean_path
from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "rq3-complexity-profile-v1"
STEM = "rq3_complexity_profile"
METRICS_CONTRACT_STEM = "rq3_complexity_metrics_contract"
TECH_REWORK_STEM = "rq3_technical_complexity_vs_rework"
FINAL_CONCENTRATION_STEM = "rq3_complexity_vs_final_concentration"
PLANNING_REWORK_OVERLAY_STEM = "rq3_planning_rework_complexity_overlay"
CONFOUNDING_SUMMARY_STEM = "rq3_complexity_confounding_summary"
TEAM_KEY = ["ID_Equipe", "Semestre"]
MIN_STRATUM_N = 4
TECHNICAL_COMPLEXITY_COLUMN = "technical_complexity_mean"
REQUIRED_EVALUATOR_COLUMNS = [
    *TEAM_KEY,
    "temporal_marker",
    TECHNICAL_COMPLEXITY_COLUMN,
]
REQUIRED_FILES_COLUMNS = [
    *TEAM_KEY,
    "commit_hash",
    "file_path",
    "file_extension",
    "lines_added",
    "lines_deleted",
    "is_binary",
]
REQUIRED_CHURN_COLUMNS = [
    *TEAM_KEY,
    "temporal_marker",
    "clean_churn",
    "all_churn",
    "clean_unique_file_n",
    "clean_touching_commit_n",
]
REQUIRED_REWORK_COLUMNS = [
    *TEAM_KEY,
    "clean_rework_churn_t3",
    "clean_rework_ratio_t3",
    "baseline_eligible_for_rework_t3",
    "measurement_status",
]
REQUIRED_PLANNING_COLUMNS = [
    *TEAM_KEY,
    "planning_artifact_present_t1",
    "planning_scope_log1p_t1",
    "pi_file_count_t1",
    "pi_line_delta_t1",
]
REQUIRED_BASE_COLUMNS = [
    *TEAM_KEY,
    "score_trajectory_group",
    "planning_scope_tier",
    "final7_commit_share_pct",
    "final7_clean_churn_share_pct",
]
FRONTEND_PATH_MARKERS = frozenset(
    {
        "frontend",
        "front-end",
        "client",
        "web",
        "ui",
        "pages",
        "components",
        "views",
    }
)
BACKEND_PATH_MARKERS = frozenset(
    {
        "backend",
        "back-end",
        "server",
        "api",
        "apis",
        "services",
        "controllers",
        "routes",
        "models",
        "repositories",
    }
)
PLANNING_TIER_COLORS = {
    "high_repository_visible_planning": "#2563eb",
    "lower_repository_visible_planning": "#f97316",
}
PLANNING_TIER_LABELS = {
    "high_repository_visible_planning": "High repository-visible planning",
    "lower_repository_visible_planning": "Lower repository-visible planning",
}
SCORE_GROUP_COLORS = {
    "improved": "#16a34a",
    "stable": "#64748b",
    "declined": "#dc2626",
}
SCORE_GROUP_LABELS = {
    "improved": "Improved",
    "stable": "Stable",
    "declined": "Declined",
}
SEMESTER_SYMBOLS = {
    "2025.2": "circle",
    "2026.1": "diamond",
}
BASELINE_ELIGIBILITY_SYMBOLS = {
    "Baseline eligible": "circle",
    "Baseline not observed": "x",
}
CONFOUNDING_RELATIONSHIPS = [
    {
        "relationship": "planning_scope_to_clean_rework_churn",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "clean_rework_churn_t3",
        "label": "Planning scope T1 -> clean rework churn T3",
    },
    {
        "relationship": "planning_scope_to_clean_rework_ratio",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "clean_rework_ratio_t3",
        "label": "Planning scope T1 -> clean rework ratio T3",
        "filter_column": "baseline_eligible_for_rework_t3",
    },
    {
        "relationship": "planning_scope_to_final7_commit_concentration",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "final7_commit_share_pct",
        "label": "Planning scope T1 -> final-7 commit concentration",
    },
    {
        "relationship": "planning_scope_to_final7_clean_churn_concentration",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "final7_clean_churn_share_pct",
        "label": "Planning scope T1 -> final-7 clean churn concentration",
    },
    {
        "relationship": "final7_commit_concentration_to_clean_rework_churn",
        "predictor": "final7_commit_share_pct",
        "outcome": "clean_rework_churn_t3",
        "label": "Final-7 commit concentration -> clean rework churn T3",
    },
    {
        "relationship": "final7_clean_churn_concentration_to_clean_rework_churn",
        "predictor": "final7_clean_churn_share_pct",
        "outcome": "clean_rework_churn_t3",
        "label": "Final-7 clean churn concentration -> clean rework churn T3",
    },
]


EVALUATED_COMPLEXITY_COLUMNS = [
    "technical_complexity_mean_t1",
    "technical_complexity_mean_t2",
    "technical_complexity_mean_t3",
    "delta_technical_complexity_t3_minus_t1",
]
STRUCTURAL_COMPLEXITY_COLUMNS = [
    "clean_distinct_file_n",
    "clean_distinct_directory_n",
    "clean_max_path_depth",
    "clean_extension_n",
    "clean_touching_commit_n_inferred",
    "mean_clean_files_per_commit",
    "clean_total_churn_inferred",
    "frontend_clean_file_event_share",
    "backend_clean_file_event_share",
]


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def _atomic_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _require_columns(frame: pd.DataFrame, columns: list[str], source: Path) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def _write_figure(figure: go.Figure, stem: str, figures_dir: Path) -> None:
    for extension in ("pdf", "svg", "png"):
        figure.write_image(
            figures_dir / f"{stem}.{extension}",
            scale=2 if extension == "png" else 1,
        )


def _safe_path_parts(file_path: str | None) -> tuple[str, ...]:
    if file_path is None or pd.isna(file_path):
        return tuple()
    return tuple(part for part in PurePosixPath(str(file_path).replace("\\", "/")).parts if part not in {"", "."})


def _path_depth(file_path: str | None) -> int:
    return len(_safe_path_parts(file_path))


def _directory_key(file_path: str | None) -> str:
    parts = _safe_path_parts(file_path)
    if len(parts) <= 1:
        return "."
    return "/".join(parts[:-1])


def _architecture_layer(file_path: str | None) -> str:
    markers = {part.lower() for part in _safe_path_parts(file_path)}
    has_frontend = bool(markers & FRONTEND_PATH_MARKERS)
    has_backend = bool(markers & BACKEND_PATH_MARKERS)
    if has_frontend and has_backend:
        return "mixed"
    if has_frontend:
        return "frontend"
    if has_backend:
        return "backend"
    return "other_or_unclassified"


def _technical_complexity(evaluator: pd.DataFrame) -> pd.DataFrame:
    technical = evaluator[[*TEAM_KEY, "temporal_marker", TECHNICAL_COMPLEXITY_COLUMN]].copy()
    pivot = technical.pivot(index=TEAM_KEY, columns="temporal_marker", values=TECHNICAL_COMPLEXITY_COLUMN)
    pivot = pivot.rename(
        columns={
            "T1": "technical_complexity_mean_t1",
            "T2": "technical_complexity_mean_t2",
            "T3": "technical_complexity_mean_t3",
        }
    )
    pivot = pivot.reset_index()
    for column in [
        "technical_complexity_mean_t1",
        "technical_complexity_mean_t2",
        "technical_complexity_mean_t3",
    ]:
        if column not in pivot.columns:
            pivot[column] = pd.NA
    pivot["delta_technical_complexity_t3_minus_t1"] = (
        pivot["technical_complexity_mean_t3"] - pivot["technical_complexity_mean_t1"]
    )
    return pivot[[*TEAM_KEY, "technical_complexity_mean_t1", "technical_complexity_mean_t2", "technical_complexity_mean_t3", "delta_technical_complexity_t3_minus_t1"]]


def _structural_complexity(files: pd.DataFrame) -> pd.DataFrame:
    files = files.copy()
    files["Semestre"] = files["Semestre"].astype(str)
    files["lines_added"] = pd.to_numeric(files["lines_added"], errors="coerce").fillna(0)
    files["lines_deleted"] = pd.to_numeric(files["lines_deleted"], errors="coerce").fillna(0)
    files["clean_churn"] = files["lines_added"] + files["lines_deleted"]
    files["is_clean_path"] = files["file_path"].map(is_clean_path)
    files = files.loc[files["is_clean_path"] & ~files["is_binary"].fillna(False)].copy()
    files["directory"] = files["file_path"].map(_directory_key)
    files["path_depth"] = files["file_path"].map(_path_depth)
    files["architecture_layer"] = files["file_path"].map(_architecture_layer)
    files["file_extension_clean"] = files["file_extension"].fillna("").replace("", "(none)")

    per_commit = (
        files.groupby([*TEAM_KEY, "commit_hash"], as_index=False)
        .agg(clean_files_touched=("file_path", "nunique"))
    )
    per_team = (
        files.groupby(TEAM_KEY, as_index=False)
        .agg(
            clean_distinct_file_n=("file_path", "nunique"),
            clean_distinct_directory_n=("directory", "nunique"),
            clean_max_path_depth=("path_depth", "max"),
            clean_extension_n=("file_extension_clean", "nunique"),
            clean_touching_commit_n_inferred=("commit_hash", "nunique"),
            clean_total_churn_inferred=("clean_churn", "sum"),
            frontend_clean_file_event_n=("architecture_layer", lambda values: int((values == "frontend").sum())),
            backend_clean_file_event_n=("architecture_layer", lambda values: int((values == "backend").sum())),
            mixed_clean_file_event_n=("architecture_layer", lambda values: int((values == "mixed").sum())),
            unclassified_clean_file_event_n=(
                "architecture_layer",
                lambda values: int((values == "other_or_unclassified").sum()),
            ),
        )
    )
    commit_diversity = (
        per_commit.groupby(TEAM_KEY, as_index=False)
        .agg(mean_clean_files_per_commit=("clean_files_touched", "mean"))
    )
    per_team = per_team.merge(commit_diversity, on=TEAM_KEY, how="left", validate="one_to_one")
    total_events = (
        per_team["frontend_clean_file_event_n"]
        + per_team["backend_clean_file_event_n"]
        + per_team["mixed_clean_file_event_n"]
        + per_team["unclassified_clean_file_event_n"]
    )
    per_team["frontend_clean_file_event_share"] = per_team["frontend_clean_file_event_n"] / total_events
    per_team["backend_clean_file_event_share"] = per_team["backend_clean_file_event_n"] / total_events
    return per_team


def _churn_t3(churn: pd.DataFrame) -> pd.DataFrame:
    t3 = churn.loc[churn["temporal_marker"].eq("T3")].copy()
    return t3[
        [
            *TEAM_KEY,
            "clean_churn",
            "all_churn",
            "clean_unique_file_n",
            "clean_touching_commit_n",
        ]
    ].rename(
        columns={
            "clean_churn": "clean_churn_t3",
            "all_churn": "all_churn_t3",
            "clean_unique_file_n": "m4_clean_unique_file_n_t3",
            "clean_touching_commit_n": "m4_clean_touching_commit_n_t3",
        }
    )


def _metrics_contract() -> pd.DataFrame:
    rows = [
        {
            "metric": "technical_complexity_mean_t1",
            "construct_family": "evaluated_complexity",
            "plan_requirement": "technical_complexity_mean_t1",
            "source": "data/lake/evaluator_team_cuts.parquet",
            "definition": "Mean evaluator technical-complexity score at temporal marker T1.",
            "heuristic_or_policy": "Evaluator-derived; not repository structural inference.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "technical_complexity_mean_t2",
            "construct_family": "evaluated_complexity",
            "plan_requirement": "technical_complexity_mean_t2",
            "source": "data/lake/evaluator_team_cuts.parquet",
            "definition": "Mean evaluator technical-complexity score at temporal marker T2.",
            "heuristic_or_policy": "Evaluator-derived; not repository structural inference.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "technical_complexity_mean_t3",
            "construct_family": "evaluated_complexity",
            "plan_requirement": "technical_complexity_mean_t3",
            "source": "data/lake/evaluator_team_cuts.parquet",
            "definition": "Mean evaluator technical-complexity score at temporal marker T3.",
            "heuristic_or_policy": "Evaluator-derived; not repository structural inference.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "delta_technical_complexity_t3_minus_t1",
            "construct_family": "evaluated_complexity",
            "plan_requirement": "delta_technical_complexity_t3_minus_t1",
            "source": "data/lake/evaluator_team_cuts.parquet",
            "definition": "technical_complexity_mean_t3 minus technical_complexity_mean_t1.",
            "heuristic_or_policy": "Derived from evaluator technical-complexity means.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_distinct_file_n",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "número de arquivos limpos distintos",
            "source": "data/lake/git_files.parquet",
            "definition": "Number of distinct clean-path files touched in observed Git file events.",
            "heuristic_or_policy": CURRENT_POLICY_VERSION,
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_distinct_directory_n",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "número de diretórios distintos",
            "source": "data/lake/git_files.parquet",
            "definition": "Number of distinct parent directories among clean-path file events.",
            "heuristic_or_policy": "Directory is derived from normalized POSIX-style file paths after clean-path filtering.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_max_path_depth",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "profundidade máxima de caminho",
            "source": "data/lake/git_files.parquet",
            "definition": "Maximum normalized path depth among clean-path file events.",
            "heuristic_or_policy": "Depth counts normalized path segments after clean-path filtering.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_extension_n",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "número de extensões",
            "source": "data/lake/git_files.parquet",
            "definition": "Number of distinct file extensions among clean-path file events.",
            "heuristic_or_policy": "Missing/empty extensions are represented as (none).",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "frontend_clean_file_event_share",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "proporção backend/frontend, se inferível por path",
            "source": "data/lake/git_files.parquet",
            "definition": "Share of clean file events whose path segments match frontend markers.",
            "heuristic_or_policy": "Path segment markers only; no manual architecture or GenAI integration classification.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "backend_clean_file_event_share",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "proporção backend/frontend, se inferível por path",
            "source": "data/lake/git_files.parquet",
            "definition": "Share of clean file events whose path segments match backend markers.",
            "heuristic_or_policy": "Path segment markers only; no manual architecture or GenAI integration classification.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_touching_commit_n_inferred",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "número de commits tocando clean paths",
            "source": "data/lake/git_files.parquet",
            "definition": "Number of distinct commits touching at least one clean-path file.",
            "heuristic_or_policy": CURRENT_POLICY_VERSION,
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "mean_clean_files_per_commit",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "diversidade de arquivos por commit",
            "source": "data/lake/git_files.parquet",
            "definition": "Mean number of distinct clean-path files touched per clean-touching commit.",
            "heuristic_or_policy": CURRENT_POLICY_VERSION,
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_total_churn_inferred",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "churn total limpo",
            "source": "data/lake/git_files.parquet",
            "definition": "Total clean-path changed lines, computed as lines_added plus lines_deleted.",
            "heuristic_or_policy": CURRENT_POLICY_VERSION,
            "manual_genai_architecture_classification": False,
        },
    ]
    return pd.DataFrame(rows)


def _analysis_profile_data(profile: pd.DataFrame) -> pd.DataFrame:
    data = profile.copy()
    data["baseline_eligibility_label"] = data["baseline_eligible_for_rework_t3"].map(
        {
            True: "Baseline eligible",
            False: "Baseline not observed",
        }
    )
    return data


def _technical_complexity_rework_data(profile: pd.DataFrame) -> pd.DataFrame:
    return _analysis_profile_data(profile)[
        [
            *TEAM_KEY,
            "technical_complexity_mean_t3",
            "clean_rework_churn_t3",
            "clean_rework_ratio_t3",
            "baseline_eligibility_label",
            "planning_scope_tier",
            "planning_scope_log1p_t1",
            "score_trajectory_group",
            "final7_commit_share_pct",
            "final7_clean_churn_share_pct",
        ]
    ].copy()


def _final_concentration_data(profile: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for metric_label, column in {
        "Final-7 commits": "final7_commit_share_pct",
        "Final-7 clean churn": "final7_clean_churn_share_pct",
    }.items():
        metric_data = _analysis_profile_data(profile)[
            [
                *TEAM_KEY,
                "technical_complexity_mean_t3",
                column,
                "score_trajectory_group",
                "planning_scope_tier",
                "clean_rework_churn_t3",
                "baseline_eligibility_label",
            ]
        ].rename(columns={column: "final7_share_pct"})
        metric_data["activity_metric"] = metric_label
        rows.extend(metric_data.to_dict("records"))
    return pd.DataFrame(rows)


def _planning_rework_overlay_data(profile: pd.DataFrame) -> pd.DataFrame:
    return _analysis_profile_data(profile)[
        [
            *TEAM_KEY,
            "planning_scope_log1p_t1",
            "clean_rework_churn_t3",
            "clean_rework_ratio_t3",
            "technical_complexity_mean_t3",
            "baseline_eligibility_label",
            "planning_scope_tier",
            "score_trajectory_group",
            "final7_commit_share_pct",
            "final7_clean_churn_share_pct",
        ]
    ].copy()


def _spearman(frame: pd.DataFrame, predictor: str, outcome: str) -> tuple[float | None, int, str | None]:
    subset = frame[[predictor, outcome]].dropna()
    n = int(len(subset))
    if n < MIN_STRATUM_N:
        return None, n, f"n<{MIN_STRATUM_N}"
    if subset[predictor].nunique(dropna=True) < 2:
        return None, n, "constant predictor"
    if subset[outcome].nunique(dropna=True) < 2:
        return None, n, "constant outcome"
    rho = subset[predictor].corr(subset[outcome], method="spearman")
    if pd.isna(rho):
        return None, n, "undefined rho"
    return float(rho), n, None


def _format_rho(rho: float | None) -> str:
    if rho is None:
        return "unavailable"
    return f"{rho:+.2f}"


def _direction(rho: float | None) -> str:
    if rho is None:
        return "unavailable"
    if rho > 0:
        return "positive"
    if rho < 0:
        return "negative"
    return "zero"


def _confounding_note(
    *,
    low_rho: float | None,
    high_rho: float | None,
    low_issue: str | None,
    high_issue: str | None,
    filter_note: str | None,
) -> str:
    notes: list[str] = []
    if filter_note:
        notes.append(filter_note)
    if low_issue:
        notes.append(f"Low-complexity stratum unavailable ({low_issue}).")
    if high_issue:
        notes.append(f"High-complexity stratum unavailable ({high_issue}).")
    if low_rho is not None and high_rho is not None:
        low_direction = _direction(low_rho)
        high_direction = _direction(high_rho)
        if low_direction != high_direction:
            notes.append(
                "Direction differs after median technical-complexity stratification "
                f"(low={_format_rho(low_rho)}, high={_format_rho(high_rho)})."
            )
        else:
            delta = abs(low_rho - high_rho)
            notes.append(
                "Direction is preserved across median technical-complexity strata "
                f"(low={_format_rho(low_rho)}, high={_format_rho(high_rho)}, |delta|={delta:.2f})."
            )
    notes.append("Descriptive small-n sensitivity summary; no regression or causal adjustment.")
    return " ".join(notes)


def _confounding_summary(profile: pd.DataFrame) -> pd.DataFrame:
    complexity_median = float(profile["technical_complexity_mean_t3"].median())
    profile = profile.copy()
    profile["technical_complexity_stratum"] = "low_or_median_complexity"
    profile.loc[profile["technical_complexity_mean_t3"].gt(complexity_median), "technical_complexity_stratum"] = (
        "high_complexity"
    )

    rows: list[dict[str, Any]] = []
    for relationship in CONFOUNDING_RELATIONSHIPS:
        relationship_frame = profile.copy()
        filter_note = None
        filter_column = relationship.get("filter_column")
        if filter_column:
            relationship_frame = relationship_frame.loc[relationship_frame[filter_column].fillna(False)].copy()
            filter_note = f"Restricted to {filter_column}=True cases."

        predictor = relationship["predictor"]
        outcome = relationship["outcome"]
        full_rho, full_n, full_issue = _spearman(relationship_frame, predictor, outcome)
        low_frame = relationship_frame.loc[
            relationship_frame["technical_complexity_stratum"].eq("low_or_median_complexity")
        ]
        high_frame = relationship_frame.loc[relationship_frame["technical_complexity_stratum"].eq("high_complexity")]
        low_rho, low_n, low_issue = _spearman(low_frame, predictor, outcome)
        high_rho, high_n, high_issue = _spearman(high_frame, predictor, outcome)
        issue_notes = [issue for issue in [full_issue] if issue]
        interpretation_note = _confounding_note(
            low_rho=low_rho,
            high_rho=high_rho,
            low_issue=low_issue,
            high_issue=high_issue,
            filter_note=filter_note,
        )
        if issue_notes:
            interpretation_note = f"Overall association unavailable ({'; '.join(issue_notes)}). {interpretation_note}"

        rows.append(
            {
                "relationship": relationship["relationship"],
                "rho_without_complexity_stratification": full_rho,
                "rho_within_low_complexity": low_rho,
                "rho_within_high_complexity": high_rho,
                "interpretation_note": interpretation_note,
                "relationship_label": relationship["label"],
                "predictor": predictor,
                "outcome": outcome,
                "complexity_stratification_variable": "technical_complexity_mean_t3",
                "complexity_median": complexity_median,
                "low_complexity_rule": "technical_complexity_mean_t3 <= median",
                "high_complexity_rule": "technical_complexity_mean_t3 > median",
                "n_without_complexity_stratification": full_n,
                "n_within_low_complexity": low_n,
                "n_within_high_complexity": high_n,
                "filter_column": filter_column or "",
                "method": "spearman_rho_with_median_stratification",
                "minimum_n_for_rho": MIN_STRATUM_N,
            }
        )
    return pd.DataFrame(rows)


def _build_technical_complexity_vs_rework(data: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    for planning_tier in PLANNING_TIER_COLORS:
        for semester in sorted(data["Semestre"].unique()):
            subset = data.loc[data["planning_scope_tier"].eq(planning_tier) & data["Semestre"].eq(semester)]
            if subset.empty:
                continue
            figure.add_trace(
                go.Scatter(
                    x=subset["technical_complexity_mean_t3"],
                    y=subset["clean_rework_churn_t3"],
                    mode="markers",
                    marker={
                        "color": PLANNING_TIER_COLORS[planning_tier],
                        "symbol": SEMESTER_SYMBOLS.get(semester, "circle"),
                        "size": 15,
                        "line": {"color": "white", "width": 1.6},
                    },
                    name=f"{PLANNING_TIER_LABELS[planning_tier]} · {semester}",
                    customdata=subset[
                        [
                            "ID_Equipe",
                            "Semestre",
                            "clean_rework_ratio_t3",
                            "baseline_eligibility_label",
                            "planning_scope_log1p_t1",
                            "score_trajectory_group",
                            "final7_commit_share_pct",
                            "final7_clean_churn_share_pct",
                        ]
                    ],
                    hovertemplate=(
                        "Team=%{customdata[0]}<br>"
                        "Semester=%{customdata[1]}<br>"
                        "Technical complexity T3=%{x:.3f}<br>"
                        "Clean rework T3=%{y:,.0f} lines<br>"
                        "Clean rework ratio T3=%{customdata[2]:.3f}<br>"
                        "Baseline status=%{customdata[3]}<br>"
                        "Planning scope T1 log1p=%{customdata[4]:.3f}<br>"
                        "Score trajectory=%{customdata[5]}<br>"
                        "Final-7 commits=%{customdata[6]:.1f}%<br>"
                        "Final-7 clean churn=%{customdata[7]:.1f}%"
                        "<extra></extra>"
                    ),
                )
            )

    complexity_median = float(data["technical_complexity_mean_t3"].median())
    rework_median = float(data["clean_rework_churn_t3"].median())
    figure.add_vline(
        x=complexity_median,
        line_dash="dot",
        line_color="#71717a",
        annotation_text=f"Median T3 complexity: {complexity_median:.2f}",
        annotation_position="top left",
    )
    figure.add_hline(
        y=rework_median,
        line_dash="dash",
        line_color="#71717a",
        annotation_text=f"Median rework: {rework_median:,.0f}",
        annotation_position="bottom right",
    )
    figure.update_layout(
        template="simple_white",
        width=1100,
        height=680,
        margin={"l": 90, "r": 35, "t": 135, "b": 155},
        title={
            "text": "Technical complexity and T3 clean rework",
            "font": {"size": 22},
            "y": 0.98,
        },
        font={"size": 14, "family": "DejaVu Sans, Arial, sans-serif"},
        legend={
            "title": "Planning tier · semester",
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.03,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 12},
        },
        xaxis={
            "title": "Evaluator technical complexity at T3",
            "gridcolor": "#e5e7eb",
            "zeroline": False,
        },
        yaxis={
            "title": "T3 clean rework magnitude (changed lines)",
            "gridcolor": "#e5e7eb",
            "zeroline": True,
            "zerolinecolor": "#cbd5e1",
        },
        annotations=[
            *figure.layout.annotations,
            {
                "text": (
                    "Points are team-semesters. Color encodes repository-visible T1 planning tier; "
                    "shape encodes semester.<br>"
                    "The panel is descriptive: rework can reflect project complexity as well as planning or AI-use dynamics."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.22,
                "xanchor": "left",
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#52525b"},
            }
        ],
    )
    return figure


def _build_complexity_vs_final_concentration(long_data: pd.DataFrame) -> go.Figure:
    figure = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Commit concentration", "Clean changed-line concentration"),
        shared_yaxes=True,
        horizontal_spacing=0.08,
    )
    metric_columns = {
        "Final-7 commits": 1,
        "Final-7 clean churn": 2,
    }
    for metric_label, column in metric_columns.items():
        metric_data = long_data.loc[long_data["activity_metric"].eq(metric_label)]
        for score_group in ["improved", "stable", "declined"]:
            subset = metric_data.loc[metric_data["score_trajectory_group"].eq(score_group)]
            if subset.empty:
                continue
            figure.add_trace(
                go.Scatter(
                    x=subset["technical_complexity_mean_t3"],
                    y=subset["final7_share_pct"],
                    mode="markers",
                    marker={
                        "color": SCORE_GROUP_COLORS.get(score_group, "#64748b"),
                        "size": 15,
                        "line": {"color": "white", "width": 1.6},
                    },
                    name=SCORE_GROUP_LABELS.get(score_group, score_group),
                    legendgroup=score_group,
                    showlegend=column == 1,
                    customdata=subset[
                        [
                            "ID_Equipe",
                            "Semestre",
                            "activity_metric",
                            "planning_scope_tier",
                            "clean_rework_churn_t3",
                            "baseline_eligibility_label",
                        ]
                    ],
                    hovertemplate=(
                        "Team=%{customdata[0]}<br>"
                        "Semester=%{customdata[1]}<br>"
                        "Metric=%{customdata[2]}<br>"
                        "Technical complexity T3=%{x:.3f}<br>"
                        "Final-7 share=%{y:.1f}%<br>"
                        "Planning tier=%{customdata[3]}<br>"
                        "Clean rework T3=%{customdata[4]:,.0f} lines<br>"
                        "Baseline status=%{customdata[5]}"
                        "<extra></extra>"
                    ),
                ),
                row=1,
                col=column,
            )

    complexity_median = float(long_data["technical_complexity_mean_t3"].median())
    concentration_median = float(long_data["final7_share_pct"].median())
    for column in [1, 2]:
        figure.add_vline(
            x=complexity_median,
            line_dash="dot",
            line_color="#71717a",
            row=1,
            col=column,
        )
        figure.add_hline(
            y=concentration_median,
            line_dash="dash",
            line_color="#71717a",
            row=1,
            col=column,
        )

    figure.update_layout(
        template="simple_white",
        width=1200,
        height=680,
        margin={"l": 85, "r": 35, "t": 125, "b": 155},
        title={
            "text": "Technical complexity versus final-week concentration",
            "font": {"size": 22},
            "y": 0.98,
        },
        font={"size": 14, "family": "DejaVu Sans, Arial, sans-serif"},
        legend={
            "title": "Score trajectory",
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        annotations=[
            *figure.layout.annotations,
            {
                "text": (
                    "Points are team-semesters. Color encodes evaluator-score trajectory group. "
                    f"Dashed guides show median concentration ({concentration_median:.1f}%) and "
                    f"median T3 complexity ({complexity_median:.2f}).<br>"
                    "Final-week concentration is a temporal activity proxy, not direct evidence of procrastination or causality."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.22,
                "xanchor": "left",
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#52525b"},
            },
        ],
    )
    figure.update_xaxes(title="Evaluator technical complexity at T3", gridcolor="#e5e7eb", zeroline=False)
    figure.update_yaxes(
        title="Final-7-day activity share",
        ticksuffix="%",
        range=[-4, 104],
        gridcolor="#e5e7eb",
        zeroline=False,
    )
    return figure


def _build_planning_rework_complexity_overlay(data: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    for baseline_label, symbol in BASELINE_ELIGIBILITY_SYMBOLS.items():
        subset = data.loc[data["baseline_eligibility_label"].eq(baseline_label)]
        if subset.empty:
            continue
        figure.add_trace(
            go.Scatter(
                x=subset["planning_scope_log1p_t1"],
                y=subset["clean_rework_churn_t3"],
                mode="markers",
                marker={
                    "color": subset["technical_complexity_mean_t3"],
                    "colorscale": "Viridis",
                    "cmin": float(data["technical_complexity_mean_t3"].min()),
                    "cmax": float(data["technical_complexity_mean_t3"].max()),
                    "coloraxis": "coloraxis",
                    "symbol": symbol,
                    "size": 16,
                    "line": {"color": "white", "width": 1.6},
                },
                name=baseline_label,
                customdata=subset[
                    [
                        "ID_Equipe",
                        "Semestre",
                        "technical_complexity_mean_t3",
                        "clean_rework_ratio_t3",
                        "planning_scope_tier",
                        "score_trajectory_group",
                        "final7_commit_share_pct",
                        "final7_clean_churn_share_pct",
                    ]
                ],
                hovertemplate=(
                    "Team=%{customdata[0]}<br>"
                    "Semester=%{customdata[1]}<br>"
                    "Planning scope T1 log1p=%{x:.3f}<br>"
                    "Clean rework T3=%{y:,.0f} lines<br>"
                    "Technical complexity T3=%{customdata[2]:.3f}<br>"
                    "Clean rework ratio T3=%{customdata[3]:.3f}<br>"
                    "Planning tier=%{customdata[4]}<br>"
                    "Score trajectory=%{customdata[5]}<br>"
                    "Final-7 commits=%{customdata[6]:.1f}%<br>"
                    "Final-7 clean churn=%{customdata[7]:.1f}%"
                    "<extra></extra>"
                ),
            )
        )

    planning_median = float(data["planning_scope_log1p_t1"].median())
    rework_median = float(data["clean_rework_churn_t3"].median())
    figure.add_vline(
        x=planning_median,
        line_dash="dot",
        line_color="#71717a",
        annotation_text=f"Median planning scope: {planning_median:.2f}",
        annotation_position="top left",
    )
    figure.add_hline(
        y=rework_median,
        line_dash="dash",
        line_color="#71717a",
        annotation_text=f"Median rework: {rework_median:,.0f}",
        annotation_position="bottom right",
    )
    figure.update_layout(
        template="simple_white",
        width=1100,
        height=680,
        margin={"l": 90, "r": 35, "t": 125, "b": 160},
        title={
            "text": "Planning, rework and technical complexity overlay",
            "font": {"size": 22},
            "y": 0.98,
        },
        font={"size": 14, "family": "DejaVu Sans, Arial, sans-serif"},
        legend={
            "title": "T3 rework baseline status",
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        coloraxis={
            "colorscale": "Viridis",
            "colorbar": {"title": "T3 technical<br>complexity"},
        },
        xaxis={
            "title": "Repository-visible T1 planning scope (log1p changed lines)",
            "gridcolor": "#e5e7eb",
            "zeroline": False,
        },
        yaxis={
            "title": "T3 clean rework magnitude (changed lines)",
            "gridcolor": "#e5e7eb",
            "zeroline": True,
            "zerolinecolor": "#cbd5e1",
        },
        annotations=[
            *figure.layout.annotations,
            {
                "text": (
                    "Points are team-semesters. Color encodes evaluator technical complexity at T3; "
                    "shape encodes whether a T3 rework baseline was observed.<br>"
                    "This overlay supports a confounding/sensitivity reading, not a causal adjustment model."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.23,
                "xanchor": "left",
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#52525b"},
            }
        ],
    )
    return figure


def generate() -> dict[str, Any]:
    paper_v9 = resolve_paper_v9_dir()
    repo_root = paper_v9.parent
    figures_dir = resolve_figures_dir()
    metrics_dir = resolve_metrics_dir()
    paths = {
        "evaluator": repo_root / "data" / "lake" / "evaluator_team_cuts.parquet",
        "git_files": repo_root / "data" / "lake" / "git_files.parquet",
        "m4_churn": metrics_dir / "m4_churn_magnitude.csv",
        "m8_rework": metrics_dir / "m8_rework_magnitude.csv",
        "m6a_planning": metrics_dir / "m6a_structural_planning.csv",
        "score_base": figures_dir / "rq2_score_trajectory_base_data.csv",
    }

    evaluator = pd.read_parquet(paths["evaluator"])
    files = pd.read_parquet(paths["git_files"])
    churn = pd.read_csv(paths["m4_churn"], dtype={"Semestre": str})
    rework = pd.read_csv(paths["m8_rework"], dtype={"Semestre": str})
    planning = pd.read_csv(paths["m6a_planning"], dtype={"Semestre": str})
    score_base = pd.read_csv(paths["score_base"], dtype={"Semestre": str})

    _require_columns(evaluator, REQUIRED_EVALUATOR_COLUMNS, paths["evaluator"])
    _require_columns(files, REQUIRED_FILES_COLUMNS, paths["git_files"])
    _require_columns(churn, REQUIRED_CHURN_COLUMNS, paths["m4_churn"])
    _require_columns(rework, REQUIRED_REWORK_COLUMNS, paths["m8_rework"])
    _require_columns(planning, REQUIRED_PLANNING_COLUMNS, paths["m6a_planning"])
    _require_columns(score_base, REQUIRED_BASE_COLUMNS, paths["score_base"])

    technical = _technical_complexity(evaluator)
    structural = _structural_complexity(files)
    churn_t3 = _churn_t3(churn)

    profile = (
        technical.merge(structural, on=TEAM_KEY, how="left", validate="one_to_one")
        .merge(churn_t3, on=TEAM_KEY, how="left", validate="one_to_one")
        .merge(rework[REQUIRED_REWORK_COLUMNS], on=TEAM_KEY, how="left", validate="one_to_one")
        .merge(planning[REQUIRED_PLANNING_COLUMNS], on=TEAM_KEY, how="left", validate="one_to_one")
        .merge(score_base[REQUIRED_BASE_COLUMNS], on=TEAM_KEY, how="left", validate="one_to_one")
        .sort_values(TEAM_KEY)
        .reset_index(drop=True)
    )
    if len(profile) != 14:
        raise ValueError(f"Expected 14 team-semesters, got {len(profile)}")

    for column in STRUCTURAL_COMPLEXITY_COLUMNS:
        if profile[column].isna().any():
            profile[column] = profile[column].fillna(0)

    data_path = figures_dir / f"{STEM}_data.csv"
    metrics_contract_path = figures_dir / f"{METRICS_CONTRACT_STEM}.csv"
    metadata_path = figures_dir / f"{STEM}.metadata.json"
    confounding_summary_path = figures_dir / f"{CONFOUNDING_SUMMARY_STEM}.csv"
    figure_stems = [
        TECH_REWORK_STEM,
        FINAL_CONCENTRATION_STEM,
        PLANNING_REWORK_OVERLAY_STEM,
    ]
    figure_data_paths = {
        TECH_REWORK_STEM: figures_dir / f"{TECH_REWORK_STEM}_data.csv",
        FINAL_CONCENTRATION_STEM: figures_dir / f"{FINAL_CONCENTRATION_STEM}_data.csv",
        PLANNING_REWORK_OVERLAY_STEM: figures_dir / f"{PLANNING_REWORK_OVERLAY_STEM}_data.csv",
    }
    _atomic_csv(profile, data_path)
    metrics_contract = _metrics_contract()
    _atomic_csv(metrics_contract, metrics_contract_path)
    confounding_summary = _confounding_summary(profile)
    _atomic_csv(confounding_summary, confounding_summary_path)
    technical_rework_data = _technical_complexity_rework_data(profile)
    final_concentration_data = _final_concentration_data(profile)
    planning_overlay_data = _planning_rework_overlay_data(profile)
    figure_data = {
        TECH_REWORK_STEM: technical_rework_data,
        FINAL_CONCENTRATION_STEM: final_concentration_data,
        PLANNING_REWORK_OVERLAY_STEM: planning_overlay_data,
    }
    for stem, frame in figure_data.items():
        _atomic_csv(frame, figure_data_paths[stem])

    figures = {
        TECH_REWORK_STEM: _build_technical_complexity_vs_rework(technical_rework_data),
        FINAL_CONCENTRATION_STEM: _build_complexity_vs_final_concentration(final_concentration_data),
        PLANNING_REWORK_OVERLAY_STEM: _build_planning_rework_complexity_overlay(planning_overlay_data),
    }
    for stem, figure in figures.items():
        _write_figure(figure, stem, figures_dir)

    figure_output_paths = {
        stem: {extension: figures_dir / f"{stem}.{extension}" for extension in ("png", "svg", "pdf")}
        for stem in figure_stems
    }

    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_id": STEM,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "data_path": str(data_path.relative_to(repo_root)),
        "data_sha256": compute_sha256(data_path),
        "metrics_contract_path": str(metrics_contract_path.relative_to(repo_root)),
        "metrics_contract_sha256": compute_sha256(metrics_contract_path),
        "confounding_summary_path": str(confounding_summary_path.relative_to(repo_root)),
        "confounding_summary_sha256": compute_sha256(confounding_summary_path),
        "figure_data_paths": {
            stem: str(path.relative_to(repo_root)) for stem, path in figure_data_paths.items()
        },
        "figure_data_sha256": {
            stem: compute_sha256(path) for stem, path in figure_data_paths.items()
        },
        "figure_outputs": {
            stem: {
                extension: str(path.relative_to(repo_root))
                for extension, path in extension_paths.items()
            }
            for stem, extension_paths in figure_output_paths.items()
        },
        "figure_output_sha256": {
            stem: {
                extension: compute_sha256(path)
                for extension, path in extension_paths.items()
            }
            for stem, extension_paths in figure_output_paths.items()
        },
        "inputs": {name: str(path.relative_to(repo_root)) for name, path in paths.items()},
        "input_sha256": {name: compute_sha256(path) for name, path in paths.items()},
        "coverage": {
            "team_semesters": int(len(profile)),
            "baseline_eligible_for_rework_t3": int(profile["baseline_eligible_for_rework_t3"].fillna(False).sum()),
        },
        "construct_separation": {
            "evaluated_complexity": EVALUATED_COMPLEXITY_COLUMNS,
            "repository_structural_complexity": STRUCTURAL_COMPLEXITY_COLUMNS,
        },
        "metric_contract_summary": {
            "evaluated_complexity_metrics": int(
                metrics_contract["construct_family"].eq("evaluated_complexity").sum()
            ),
            "repository_structural_complexity_metrics": int(
                metrics_contract["construct_family"].eq("repository_structural_complexity").sum()
            ),
            "manual_genai_architecture_classification_used": bool(
                metrics_contract["manual_genai_architecture_classification"].any()
            ),
        },
        "visualization_contract": {
            TECH_REWORK_STEM: {
                "x": "technical_complexity_mean_t3",
                "y": "clean_rework_churn_t3",
                "color": "planning_scope_tier",
                "shape": "Semestre",
                "purpose": "Assess whether T3 rework magnitude may co-vary with evaluator-rated technical complexity.",
            },
            FINAL_CONCENTRATION_STEM: {
                "x": "technical_complexity_mean_t3",
                "y": "final7_share_pct",
                "color": "score_trajectory_group",
                "panels": ["final7_commit_share_pct", "final7_clean_churn_share_pct"],
                "purpose": "Inspect whether final-week concentration patterns are separable from project technical complexity.",
            },
            PLANNING_REWORK_OVERLAY_STEM: {
                "x": "planning_scope_log1p_t1",
                "y": "clean_rework_churn_t3",
                "color": "technical_complexity_mean_t3",
                "shape": "baseline_eligibility_label",
                "purpose": "Overlay planning, rework and complexity to support descriptive confounding discussion.",
            },
        },
        "confounding_summary_contract": {
            "output": str(confounding_summary_path.relative_to(repo_root)),
            "stratification_variable": "technical_complexity_mean_t3",
            "stratification_policy": "median split with low_or_median <= median and high > median",
            "method": "Spearman rho within full sample and median technical-complexity strata",
            "minimum_n_for_rho": MIN_STRATUM_N,
            "relationship_count": int(len(confounding_summary)),
            "low_complexity_n_range": [
                int(confounding_summary["n_within_low_complexity"].min()),
                int(confounding_summary["n_within_low_complexity"].max()),
            ],
            "high_complexity_n_range": [
                int(confounding_summary["n_within_high_complexity"].min()),
                int(confounding_summary["n_within_high_complexity"].max()),
            ],
        },
        "path_heuristics": {
            "clean_path_policy": CURRENT_POLICY_VERSION,
            "frontend_markers": sorted(FRONTEND_PATH_MARKERS),
            "backend_markers": sorted(BACKEND_PATH_MARKERS),
            "architecture_layer_rule": (
                "Path segment markers classify clean file events as frontend, backend, mixed, or other_or_unclassified; "
                "this is a coarse repository-structure heuristic, not manual GenAI architecture classification."
            ),
        },
        "inference": "descriptive_confounding_profile_not_causal",
        "limitations": [
            "Evaluator technical complexity is a human assessment dimension, not inferred repository structure.",
            "Structural complexity metrics are Git/path heuristics over clean paths and do not classify architecture semantics.",
            "Frontend/backend shares depend on path names and can under-detect unconventional project layouts.",
            "The profile supports confounding/sensitivity discussion and is not a causal adjustment model.",
        ],
    }
    _atomic_json(metadata, metadata_path)
    return {
        "status": "generated",
        "data_path": str(data_path),
        "metrics_contract_path": str(metrics_contract_path),
        "confounding_summary_path": str(confounding_summary_path),
        "figure_data_paths": {stem: str(path) for stem, path in figure_data_paths.items()},
        "figure_outputs": {
            stem: {extension: str(path) for extension, path in extension_paths.items()}
            for stem, extension_paths in figure_output_paths.items()
        },
        "metadata_path": str(metadata_path),
        "coverage": metadata["coverage"],
    }


def main() -> None:
    result = generate()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
