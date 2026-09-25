"""Generate coverage-aware M5 triangulation artifacts for 2025.2."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "rq2-m5-2025-triangulation-v1"
STEM = "rq2_m5_2025_triangulation"
PANEL_STEM = "rq2_m5_2025_triangulation_panel"
TEAM_KEY = ["ID_Equipe", "Semestre"]
CHECKPOINTS = ("T1", "T2", "T3")
OBSERVED_SEMESTER = "2025.2"
UNAVAILABLE_SEMESTERS = ("2026.1",)
EVALUATOR_SCORE_COLUMNS = [
    "project_progress_mean",
    "scope_applicability_mean",
    "technical_complexity_mean",
    "engagement_participation_mean",
]
REQUIRED_M5_COLUMNS = [
    "temporal_marker",
    "transcript_chunk_n",
    "source_session_n",
    "character_n",
    "token_n",
    "friction_marker_n",
    "alignment",
    "handoff",
    "integration",
    "blocker",
    "rework",
    "friction_marker_density_per_1k_tokens",
    "analysis_level",
    "measurement_status",
]
REQUIRED_M4_COLUMNS = [
    *TEAM_KEY,
    "temporal_marker",
    "clean_churn",
    "all_churn",
    "clean_unique_file_n",
    "clean_touching_commit_n",
    "measurement_status",
]
REQUIRED_REWORK_COLUMNS = [
    *TEAM_KEY,
    "clean_rework_churn_t3",
    "clean_deferred_churn_t3",
    "prior_clean_path_n",
    "clean_total_churn_t3",
    "baseline_eligible_for_rework_t3",
    "clean_rework_ratio_t3",
    "measurement_status",
]
REQUIRED_EVALUATOR_COLUMNS = [
    *TEAM_KEY,
    "temporal_marker",
    *EVALUATOR_SCORE_COLUMNS,
    "git_match_status",
]
REQUIRED_PLANNING_COLUMNS = [
    *TEAM_KEY,
    "planning_artifact_present_t1",
    "planning_scope_log1p_t1",
    "measurement_status",
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


def _load_m5_marker_density(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    _require_columns(frame, REQUIRED_M5_COLUMNS, path)
    frame = frame.copy()
    frame["temporal_marker"] = frame["temporal_marker"].astype(str)
    unexpected = sorted(set(frame["temporal_marker"]) - set(CHECKPOINTS))
    if unexpected:
        raise ValueError(f"Unexpected M5 temporal markers: {unexpected}")
    if frame["temporal_marker"].duplicated().any():
        duplicates = frame.loc[frame["temporal_marker"].duplicated(keep=False), "temporal_marker"].tolist()
        raise ValueError(f"Duplicate M5 temporal marker rows: {duplicates}")
    for column in [
        "transcript_chunk_n",
        "source_session_n",
        "character_n",
        "token_n",
        "friction_marker_n",
        "alignment",
        "handoff",
        "integration",
        "blocker",
        "rework",
        "friction_marker_density_per_1k_tokens",
    ]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return (
        frame.rename(
            columns={
                "measurement_status": "m5_measurement_status",
                "analysis_level": "m5_analysis_level",
            }
        )
        .sort_values("temporal_marker")
        .reset_index(drop=True)
    )


def _load_m4_churn(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    _require_columns(frame, REQUIRED_M4_COLUMNS, path)
    frame = frame.loc[frame["Semestre"].eq(OBSERVED_SEMESTER)].copy()
    for column in ["clean_churn", "all_churn", "clean_unique_file_n", "clean_touching_commit_n"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    _assert_team_checkpoint_rows(frame, path)
    return frame.rename(columns={"measurement_status": "m4_measurement_status"})


def _load_rework(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    _require_columns(frame, REQUIRED_REWORK_COLUMNS, path)
    frame = frame.loc[frame["Semestre"].eq(OBSERVED_SEMESTER)].copy()
    duplicate_keys = frame.duplicated(TEAM_KEY, keep=False)
    if duplicate_keys.any():
        duplicates = frame.loc[duplicate_keys, TEAM_KEY].to_dict("records")
        raise ValueError(f"Duplicate rework team-semester rows found: {duplicates}")
    for column in [
        "clean_rework_churn_t3",
        "clean_deferred_churn_t3",
        "prior_clean_path_n",
        "clean_total_churn_t3",
        "clean_rework_ratio_t3",
    ]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    frame["baseline_eligible_for_rework_t3"] = frame["baseline_eligible_for_rework_t3"].astype(bool)
    return frame.rename(columns={"measurement_status": "m8_measurement_status"})


def _load_evaluator_scores(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    _require_columns(frame, REQUIRED_EVALUATOR_COLUMNS, path)
    frame = frame.copy()
    frame["Semestre"] = frame["Semestre"].astype(str)
    frame = frame.loc[frame["Semestre"].eq(OBSERVED_SEMESTER)].copy()
    for column in EVALUATOR_SCORE_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    frame["evaluator_score_composite"] = frame[EVALUATOR_SCORE_COLUMNS].mean(axis=1)
    _assert_team_checkpoint_rows(frame, path)
    return frame[
        [*TEAM_KEY, "temporal_marker", "evaluator_score_composite", *EVALUATOR_SCORE_COLUMNS, "git_match_status"]
    ].rename(columns={"git_match_status": "evaluator_git_match_status"})


def _load_planning(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    _require_columns(frame, REQUIRED_PLANNING_COLUMNS, path)
    frame = frame.loc[frame["Semestre"].eq(OBSERVED_SEMESTER)].copy()
    duplicate_keys = frame.duplicated(TEAM_KEY, keep=False)
    if duplicate_keys.any():
        duplicates = frame.loc[duplicate_keys, TEAM_KEY].to_dict("records")
        raise ValueError(f"Duplicate planning team-semester rows found: {duplicates}")
    frame["planning_artifact_present_t1"] = frame["planning_artifact_present_t1"].astype(bool)
    frame["planning_scope_log1p_t1"] = pd.to_numeric(frame["planning_scope_log1p_t1"], errors="raise")
    return frame[[*TEAM_KEY, "planning_artifact_present_t1", "planning_scope_log1p_t1", "measurement_status"]].rename(
        columns={"measurement_status": "m6a_measurement_status"}
    )


def _assert_team_checkpoint_rows(frame: pd.DataFrame, source: Path) -> None:
    duplicate_keys = frame.duplicated([*TEAM_KEY, "temporal_marker"], keep=False)
    if duplicate_keys.any():
        duplicates = frame.loc[duplicate_keys, [*TEAM_KEY, "temporal_marker"]].to_dict("records")
        raise ValueError(f"Duplicate checkpoint rows in {source}: {duplicates}")
    unexpected = sorted(set(frame["temporal_marker"].dropna()) - set(CHECKPOINTS))
    if unexpected:
        raise ValueError(f"Unexpected temporal markers in {source}: {unexpected}")
    team_n = frame[TEAM_KEY].drop_duplicates().shape[0]
    expected_rows = team_n * len(CHECKPOINTS)
    if len(frame) != expected_rows:
        raise ValueError(f"Expected {expected_rows} team-checkpoint rows in {source}, got {len(frame)}")


def _build_triangulation_data(
    *,
    m5: pd.DataFrame,
    churn: pd.DataFrame,
    rework: pd.DataFrame,
    evaluator: pd.DataFrame,
    planning: pd.DataFrame,
) -> pd.DataFrame:
    data = evaluator.merge(churn, on=[*TEAM_KEY, "temporal_marker"], how="left", validate="one_to_one")
    data = data.merge(rework, on=TEAM_KEY, how="left", validate="many_to_one", suffixes=("", "_rework"))
    data = data.merge(planning, on=TEAM_KEY, how="left", validate="many_to_one", suffixes=("", "_planning"))
    data = data.merge(m5, on="temporal_marker", how="left", validate="many_to_one", suffixes=("", "_m5"))

    missing = data.loc[
        data[
            [
                "clean_churn",
                "clean_rework_churn_t3",
                "planning_scope_log1p_t1",
                "friction_marker_density_per_1k_tokens",
            ]
        ].isna().any(axis=1),
        [*TEAM_KEY, "temporal_marker"],
    ]
    if not missing.empty:
        raise ValueError(f"Missing triangulation joins: {missing.to_dict('records')}")

    data["m5_semester_coverage_status"] = "available_transcript_corpus_2025_2"
    data["m5_observed_semester"] = OBSERVED_SEMESTER
    data["m5_unavailable_semesters"] = ",".join(
        f"{semester}=unavailable_not_measured" for semester in UNAVAILABLE_SEMESTERS
    )
    data["m5_analysis_scope_note"] = (
        "M5 is global transcript-corpus evidence by temporal marker for 2025.2; "
        "it is not a team-level measure."
    )

    ordered_columns = [
        *TEAM_KEY,
        "temporal_marker",
        "m5_semester_coverage_status",
        "m5_observed_semester",
        "m5_unavailable_semesters",
        "m5_analysis_scope_note",
        "friction_marker_density_per_1k_tokens",
        "friction_marker_n",
        "token_n",
        "transcript_chunk_n",
        "source_session_n",
        "alignment",
        "handoff",
        "integration",
        "blocker",
        "rework",
        "clean_churn",
        "all_churn",
        "clean_unique_file_n",
        "clean_touching_commit_n",
        "evaluator_score_composite",
        *EVALUATOR_SCORE_COLUMNS,
        "clean_rework_churn_t3",
        "clean_deferred_churn_t3",
        "clean_total_churn_t3",
        "baseline_eligible_for_rework_t3",
        "clean_rework_ratio_t3",
        "prior_clean_path_n",
        "planning_artifact_present_t1",
        "planning_scope_log1p_t1",
        "evaluator_git_match_status",
        "m4_measurement_status",
        "m8_measurement_status",
        "m6a_measurement_status",
        "m5_measurement_status",
        "m5_analysis_level",
    ]
    return data[ordered_columns].sort_values([*TEAM_KEY, "temporal_marker"]).reset_index(drop=True)


def _summary(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for marker in CHECKPOINTS:
        subset = data.loc[data["temporal_marker"].eq(marker)]
        rows.append(
            {
                "temporal_marker": marker,
                "team_n": int(subset[TEAM_KEY].drop_duplicates().shape[0]),
                "m5_friction_marker_density_per_1k_tokens": float(
                    subset["friction_marker_density_per_1k_tokens"].iloc[0]
                ),
                "m5_friction_marker_n": int(subset["friction_marker_n"].iloc[0]),
                "m5_token_n": int(subset["token_n"].iloc[0]),
                "median_clean_churn": float(subset["clean_churn"].median()),
                "mean_clean_churn": float(subset["clean_churn"].mean()),
                "median_evaluator_score_composite": float(subset["evaluator_score_composite"].median()),
                "mean_evaluator_score_composite": float(subset["evaluator_score_composite"].mean()),
                "baseline_eligible_rework_team_n": int(
                    subset.loc[subset["baseline_eligible_for_rework_t3"], TEAM_KEY].drop_duplicates().shape[0]
                ),
                "median_clean_rework_churn_t3": float(
                    subset.drop_duplicates(TEAM_KEY)["clean_rework_churn_t3"].median()
                ),
                "median_clean_rework_ratio_t3_baseline_eligible": float(
                    subset.drop_duplicates(TEAM_KEY)
                    .loc[lambda frame: frame["baseline_eligible_for_rework_t3"], "clean_rework_ratio_t3"]
                    .median()
                ),
            }
        )
    return pd.DataFrame(rows)


def _build_panel(data: pd.DataFrame, summary: pd.DataFrame) -> go.Figure:
    marker_order = list(CHECKPOINTS)
    figure = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "M5 global friction-marker density",
            "M4 clean churn by team",
            "Evaluator composite score by team",
            "M8 T3 clean rework by team",
        ),
        vertical_spacing=0.16,
        horizontal_spacing=0.12,
    )

    figure.add_trace(
        go.Scatter(
            x=summary["temporal_marker"],
            y=summary["m5_friction_marker_density_per_1k_tokens"],
            mode="lines+markers",
            line={"color": "#7c3aed", "width": 3},
            marker={"size": 10},
            name="M5 markers / 1k tokens",
            hovertemplate=(
                "Checkpoint=%{x}<br>Density=%{y:.2f}<br>"
                "Markers=%{customdata[0]}<br>Tokens=%{customdata[1]}<extra></extra>"
            ),
            customdata=summary[["m5_friction_marker_n", "m5_token_n"]],
        ),
        row=1,
        col=1,
    )

    for marker in marker_order:
        subset = data.loc[data["temporal_marker"].eq(marker)]
        figure.add_trace(
            go.Box(
                x=[marker] * len(subset),
                y=subset["clean_churn"],
                boxpoints="all",
                jitter=0.35,
                marker={"color": "#2563eb", "size": 7},
                line={"color": "#1d4ed8"},
                name=f"M4 {marker}",
                showlegend=False,
                text=subset["ID_Equipe"],
                hovertemplate="Team=%{text}<br>Checkpoint=%{x}<br>Clean churn=%{y:.0f}<extra></extra>",
            ),
            row=1,
            col=2,
        )

    for marker in marker_order:
        subset = data.loc[data["temporal_marker"].eq(marker)]
        figure.add_trace(
            go.Box(
                x=[marker] * len(subset),
                y=subset["evaluator_score_composite"],
                boxpoints="all",
                jitter=0.35,
                marker={"color": "#16a34a", "size": 7},
                line={"color": "#15803d"},
                name=f"Score {marker}",
                showlegend=False,
                text=subset["ID_Equipe"],
                hovertemplate="Team=%{text}<br>Checkpoint=%{x}<br>Evaluator score=%{y:.2f}<extra></extra>",
            ),
            row=2,
            col=1,
        )

    rework = data.drop_duplicates(TEAM_KEY).sort_values("clean_rework_churn_t3")
    figure.add_trace(
        go.Bar(
            x=rework["ID_Equipe"],
            y=rework["clean_rework_churn_t3"],
            marker={
                "color": rework["baseline_eligible_for_rework_t3"].map({True: "#f97316", False: "#94a3b8"}),
                "line": {"color": "#334155", "width": 0.8},
            },
            text=rework["baseline_eligible_for_rework_t3"].map({True: "baseline", False: "no baseline"}),
            hovertemplate=(
                "Team=%{x}<br>T3 clean rework=%{y:.0f}<br>"
                "%{text}<extra></extra>"
            ),
            name="M8 clean rework T3",
        ),
        row=2,
        col=2,
    )

    figure.update_xaxes(categoryorder="array", categoryarray=marker_order, row=1, col=1)
    figure.update_xaxes(categoryorder="array", categoryarray=marker_order, row=1, col=2)
    figure.update_xaxes(categoryorder="array", categoryarray=marker_order, row=2, col=1)
    figure.update_yaxes(title_text="Markers per 1k tokens", row=1, col=1)
    figure.update_yaxes(title_text="Clean changed lines", row=1, col=2)
    figure.update_yaxes(title_text="Composite score", row=2, col=1)
    figure.update_yaxes(title_text="Clean rework lines", row=2, col=2)
    figure.update_layout(
        title={
            "text": "Coverage-aware M5 triangulation for 2025.2",
            "x": 0.02,
            "xanchor": "left",
        },
        template="plotly_white",
        width=1200,
        height=820,
        margin={"l": 70, "r": 35, "t": 115, "b": 100},
        font={"family": "Arial", "size": 13},
        showlegend=False,
        annotations=[
            *figure.layout.annotations,
            {
                "text": (
                    "M5 is measured only in the 2025.2 global transcript corpus; "
                    "2026.1 is unavailable/not measured and is not plotted as zero."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.13,
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#475569"},
            },
        ],
    )
    return figure


def generate() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[3]
    metrics_dir = resolve_metrics_dir()
    figures_dir = resolve_figures_dir()
    paths = {
        "m5_marker_density": metrics_dir / "m5_marker_density.csv",
        "m5_corpus_coverage": metrics_dir / "m5_corpus_coverage.csv",
        "m4_churn_magnitude": metrics_dir / "m4_churn_magnitude.csv",
        "m8_rework_magnitude": metrics_dir / "m8_rework_magnitude.csv",
        "evaluator_team_cuts": repo_root / "data" / "lake" / "evaluator_team_cuts.parquet",
        "m6a_structural_planning": metrics_dir / "m6a_structural_planning.csv",
    }
    output_paths = {
        "data": figures_dir / f"{STEM}_data.csv",
        "summary": figures_dir / f"{STEM}_summary.csv",
        "metadata": figures_dir / f"{STEM}.metadata.json",
    }

    m5 = _load_m5_marker_density(paths["m5_marker_density"])
    churn = _load_m4_churn(paths["m4_churn_magnitude"])
    rework = _load_rework(paths["m8_rework_magnitude"])
    evaluator = _load_evaluator_scores(paths["evaluator_team_cuts"])
    planning = _load_planning(paths["m6a_structural_planning"])
    data = _build_triangulation_data(
        m5=m5,
        churn=churn,
        rework=rework,
        evaluator=evaluator,
        planning=planning,
    )
    summary = _summary(data)

    expected_rows = data[TEAM_KEY].drop_duplicates().shape[0] * len(CHECKPOINTS)
    if len(data) != expected_rows:
        raise ValueError(f"Expected {expected_rows} triangulation rows, got {len(data)}")

    _atomic_csv(data, output_paths["data"])
    _atomic_csv(summary, output_paths["summary"])
    _write_figure(_build_panel(data, summary), PANEL_STEM, figures_dir)

    figure_paths = {
        PANEL_STEM: {extension: figures_dir / f"{PANEL_STEM}.{extension}" for extension in ("png", "svg", "pdf")}
    }
    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_id": STEM,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {name: str(path.relative_to(repo_root)) for name, path in paths.items()},
        "input_sha256": {name: compute_sha256(path) for name, path in paths.items()},
        "outputs": {name: str(path.relative_to(repo_root)) for name, path in output_paths.items() if name != "metadata"},
        "output_sha256": {name: compute_sha256(path) for name, path in output_paths.items() if name != "metadata"},
        "figure_outputs": {
            stem: {extension: str(path.relative_to(repo_root)) for extension, path in extension_paths.items()}
            for stem, extension_paths in figure_paths.items()
        },
        "figure_output_sha256": {
            stem: {extension: compute_sha256(path) for extension, path in extension_paths.items()}
            for stem, extension_paths in figure_paths.items()
        },
        "coverage": {
            "observed_semester": OBSERVED_SEMESTER,
            "unavailable_semesters": {
                semester: "unavailable_not_measured" for semester in UNAVAILABLE_SEMESTERS
            },
            "team_semesters": int(data[TEAM_KEY].drop_duplicates().shape[0]),
            "team_checkpoint_rows": int(len(data)),
            "temporal_markers": list(CHECKPOINTS),
            "m5_analysis_level": "global_transcript_corpus_by_temporal_marker",
            "m5_team_level_measure": False,
            "m5_zero_filled_unavailable_semesters": False,
        },
        "metrics": {
            "m5_friction_marker_density_per_1k_tokens": (
                "Global transcript-corpus friction markers per 1k tokens by temporal marker."
            ),
            "clean_churn": "M4 clean changed lines by team-semester/checkpoint.",
            "evaluator_score_composite": (
                "Unweighted mean of project_progress, scope_applicability, technical_complexity "
                "and engagement_participation evaluator dimensions."
            ),
            "clean_rework_churn_t3": "M8 T3 clean changed lines touching paths observed before T3.",
        },
        "visualization_contract": {
            PANEL_STEM: {
                "source_data": str(output_paths["data"].relative_to(repo_root)),
                "source_summary": str(output_paths["summary"].relative_to(repo_root)),
                "panels": [
                    "M5 global friction-marker density by temporal marker",
                    "M4 clean churn distribution by team/checkpoint",
                    "Evaluator composite score distribution by team/checkpoint",
                    "M8 T3 clean rework churn by team",
                ],
                "coverage_note": (
                    "Panel is intentionally restricted to 2025.2 because M5 transcript evidence is "
                    "not measured for 2026.1."
                ),
            }
        },
        "inference": "descriptive_coverage_aware_triangulation_not_causal",
        "limitations": [
            "M5 is a global transcript-corpus measure by temporal marker, not a team-level measurement.",
            "The triangulation is restricted to 2025.2; 2026.1 is unavailable/not measured and is not zero-filled.",
            "M8 rework is observed at T3 only and should not be interpreted as semantic defect validation.",
            "Evaluator score is a descriptive unweighted composite used for triangulation consistency.",
        ],
    }
    _atomic_json(metadata, output_paths["metadata"])
    return {
        "status": "generated",
        "data": str(output_paths["data"]),
        "summary": str(output_paths["summary"]),
        "metadata": str(output_paths["metadata"]),
        "figure": str(figures_dir / f"{PANEL_STEM}.png"),
        "coverage": metadata["coverage"],
    }


def main() -> None:
    print(json.dumps(generate(), indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
