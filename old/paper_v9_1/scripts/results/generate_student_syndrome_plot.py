"""Generate the RQ2 student-syndrome stratified activity plot."""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import (
    resolve_figures_dir,
    resolve_metrics_dir,
    resolve_paper_v9_dir,
)
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "rq2-student-syndrome-tier-plot-v1"
TEAM_KEY = ["ID_Equipe", "Semestre"]
EVALUATOR_SCORE_COLUMNS = [
    "project_progress_mean",
    "scope_applicability_mean",
    "technical_complexity_mean",
    "engagement_participation_mean",
]
WINDOW_END_DAYS = tuple(range(-6, 1))
BOOTSTRAP_SAMPLES = 10_000
BOOTSTRAP_SEED = 20260925
STEM = "rq2_student_syndrome_by_evaluator_planning_tier"
CHURN_STEM = "rq2_student_syndrome_by_evaluator_planning_tier_clean_churn"
HIGH_TIER = "High evaluator score + good planning"
LOWER_TIER = "Lower evaluator score / weaker planning"
TIER_COLORS = {
    HIGH_TIER: "#2563eb",
    LOWER_TIER: "#f97316",
}


def _hex_to_rgba(color: str, alpha: float) -> str:
    channels = tuple(int(color.lstrip("#")[index : index + 2], 16) for index in (0, 2, 4))
    return f"rgba({channels[0]}, {channels[1]}, {channels[2]}, {alpha})"


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


def _bootstrap_interval(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    team_count = matrix.shape[0]
    resample_indices = rng.integers(
        0,
        team_count,
        size=(BOOTSTRAP_SAMPLES, team_count),
    )
    means = matrix[resample_indices].mean(axis=1)
    return (
        np.percentile(means, 2.5, axis=0),
        np.percentile(means, 97.5, axis=0),
    )


def _load_tier_frame(
    planning: pd.DataFrame,
    evaluator: pd.DataFrame,
) -> tuple[pd.DataFrame, float, float]:
    t3 = evaluator.loc[evaluator["temporal_marker"].eq("T3")].copy()
    _require_columns(t3, [*TEAM_KEY, *EVALUATOR_SCORE_COLUMNS], Path("evaluator_team_cuts.parquet"))
    t3["evaluator_score_t3"] = t3[EVALUATOR_SCORE_COLUMNS].mean(axis=1)

    frame = planning.merge(
        t3[[*TEAM_KEY, "evaluator_score_t3", *EVALUATOR_SCORE_COLUMNS]],
        on=TEAM_KEY,
        validate="one_to_one",
    )
    if len(frame) != 14:
        raise ValueError(f"Expected 14 team-semesters after tier join, got {len(frame)}")

    evaluator_median = float(frame["evaluator_score_t3"].median())
    planning_median = float(frame["planning_scope_log1p_t1"].median())
    frame["tier"] = np.where(
        (frame["evaluator_score_t3"] >= evaluator_median)
        & (frame["planning_scope_log1p_t1"] >= planning_median)
        & frame["planning_artifact_present_t1"].astype(bool),
        HIGH_TIER,
        LOWER_TIER,
    )
    return frame, evaluator_median, planning_median


def _summarize_plot_data(
    plot_data: pd.DataFrame,
    *,
    normalized_column: str,
    summary_prefix: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for tier, group in plot_data.groupby("tier", sort=False):
        matrix_frame = group.pivot(
            index=TEAM_KEY,
            columns="window_end_day",
            values=normalized_column,
        ).reindex(columns=WINDOW_END_DAYS)
        if matrix_frame.isna().any().any():
            raise ValueError(f"Incomplete window data for tier {tier}")

        matrix = matrix_frame.to_numpy(dtype=float)
        lower, upper = _bootstrap_interval(matrix)
        mean = matrix.mean(axis=0)
        median = np.median(matrix, axis=0)
        team_count = matrix.shape[0]
        for index, day in enumerate(WINDOW_END_DAYS):
            rows.append(
                {
                    "tier": tier,
                    "window_end_day": day,
                    "team_semester_n": team_count,
                    f"mean_{summary_prefix}_share_pct": mean[index],
                    f"median_{summary_prefix}_share_pct": median[index],
                    "ci95_lower": lower[index],
                    "ci95_upper": upper[index],
                }
            )
    return pd.DataFrame(rows)


def _build_figure(
    plot_data: pd.DataFrame,
    summary: pd.DataFrame,
    *,
    normalized_column: str,
    summary_prefix: str,
    title: str,
    yaxis_title: str,
    note: str,
) -> go.Figure:
    figure = go.Figure()
    for tier in [HIGH_TIER, LOWER_TIER]:
        tier_summary = summary.loc[summary["tier"].eq(tier)].sort_values("window_end_day")
        if tier_summary.empty:
            continue
        color = TIER_COLORS[tier]

        x = tier_summary["window_end_day"].tolist()
        upper = tier_summary["ci95_upper"].tolist()
        lower = tier_summary["ci95_lower"].tolist()
        figure.add_scatter(
            x=x + x[::-1],
            y=upper + lower[::-1],
            fill="toself",
            fillcolor=_hex_to_rgba(color, 0.13),
            line={"color": "rgba(255,255,255,0)"},
            hoverinfo="skip",
            showlegend=False,
        )

        individuals = plot_data.loc[plot_data["tier"].eq(tier)]
        for _, team in individuals.groupby(TEAM_KEY):
            team = team.sort_values("window_end_day")
            figure.add_trace(
                go.Scatter(
                    x=team["window_end_day"],
                    y=team[normalized_column],
                    mode="lines",
                    line={"color": color, "width": 1},
                    opacity=0.18,
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

        team_count = int(tier_summary["team_semester_n"].iloc[0])
        figure.add_trace(
            go.Scatter(
                x=tier_summary["window_end_day"],
                y=tier_summary[f"mean_{summary_prefix}_share_pct"],
                mode="lines+markers",
                line={"color": color, "width": 4},
                marker={"size": 10, "line": {"width": 1.4, "color": "white"}},
                name=f"{tier} (n={team_count})",
                customdata=np.stack(
                    [
                        tier_summary[f"median_{summary_prefix}_share_pct"],
                        tier_summary["ci95_lower"],
                        tier_summary["ci95_upper"],
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "Window ending D%{x}<br>"
                    "Mean timing share=%{y:.2f}%<br>"
                    "Median timing share=%{customdata[0]:.2f}%<br>"
                    "95% interval=%{customdata[1]:.2f}%–%{customdata[2]:.2f}%"
                    "<extra></extra>"
                ),
            )
        )

    figure.add_vline(x=0, line_dash="dash", line_color="#3f3f46", line_width=1.4)
    figure.add_annotation(
        x=0,
        y=1.04,
        xref="x",
        yref="paper",
        text="T3 anchor",
        showarrow=False,
        font={"size": 14, "color": "#3f3f46"},
    )
    figure.update_layout(
        template="simple_white",
        width=1200,
        height=650,
        margin={"l": 90, "r": 45, "t": 90, "b": 115},
        title={
            "text": title,
            "font": {"size": 24},
        },
        font={"size": 15, "family": "DejaVu Sans, Arial, sans-serif"},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 14},
        },
        xaxis={
            "title": "Trailing 7-day window ending at day relative to T3 anchor",
            "tickmode": "array",
            "tickvals": list(WINDOW_END_DAYS),
            "ticktext": [f"D{day}" if day else "D0" for day in WINDOW_END_DAYS],
            "showgrid": False,
            "zeroline": False,
            "title_font": {"size": 17},
        },
        yaxis={
            "title": yaxis_title,
            "range": [0, max(50, float(summary["ci95_upper"].max()) * 1.12)],
            "gridcolor": "#e5e7eb",
            "zeroline": True,
            "zerolinecolor": "#cbd5e1",
            "title_font": {"size": 17},
        },
        annotations=[
            *figure.layout.annotations,
            {
                "text": note,
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.19,
                "showarrow": False,
                "align": "left",
                "font": {"size": 13, "color": "#52525b"},
            },
        ],
    )
    return figure


def _prepare_plot_data(
    source: pd.DataFrame,
    tiers: pd.DataFrame,
    *,
    value_column: str,
    total_column: str,
    share_column: str,
    exclude_zero_totals: bool = False,
) -> pd.DataFrame:
    activity_window = source.loc[source["window_end_day"].isin(WINDOW_END_DAYS)].copy()
    plot_data = activity_window.merge(
        tiers[
            [
                *TEAM_KEY,
                "tier",
                "evaluator_score_t3",
                "planning_artifact_present_t1",
                "planning_scope_log1p_t1",
            ]
        ],
        on=TEAM_KEY,
        validate="many_to_one",
    )
    if plot_data[TEAM_KEY].drop_duplicates().shape[0] != 14:
        raise ValueError("Expected 14 team-semesters in the final plot data")
    plot_data[total_column] = plot_data.groupby(TEAM_KEY)[value_column].transform("sum")
    excluded_zero_activity: list[dict[str, Any]] = []
    if plot_data[total_column].eq(0).any():
        zero_activity = plot_data.loc[plot_data[total_column].eq(0), TEAM_KEY].drop_duplicates()
        excluded_zero_activity = zero_activity.to_dict("records")
        if not exclude_zero_totals:
            raise ValueError(f"Cannot normalize zero-activity team-semesters: {excluded_zero_activity}")
        plot_data = plot_data.loc[plot_data[total_column].gt(0)].copy()
    plot_data[share_column] = 100 * plot_data[value_column] / plot_data[total_column]
    plot_data.attrs["excluded_zero_activity"] = excluded_zero_activity
    return plot_data


def _generate_metric_plot(
    *,
    plot_data: pd.DataFrame,
    stem: str,
    figures: Path,
    normalized_column: str,
    summary_prefix: str,
    title: str,
    yaxis_title: str,
    note: str,
) -> list[str]:
    summary = _summarize_plot_data(
        plot_data,
        normalized_column=normalized_column,
        summary_prefix=summary_prefix,
    )
    _atomic_csv(plot_data.sort_values([*TEAM_KEY, "window_end_day"]), figures / f"{stem}_data.csv")
    _atomic_csv(summary.sort_values(["tier", "window_end_day"]), figures / f"{stem}_summary.csv")

    figure = _build_figure(
        plot_data,
        summary,
        normalized_column=normalized_column,
        summary_prefix=summary_prefix,
        title=title,
        yaxis_title=yaxis_title,
        note=note,
    )
    _write_figure(figure, stem, figures)
    return [
        f"figures/{stem}.pdf",
        f"figures/{stem}.svg",
        f"figures/{stem}.png",
        f"figures/{stem}_data.csv",
        f"figures/{stem}_summary.csv",
        f"figures/{stem}.metadata.json",
    ]


def generate() -> dict[str, Any]:
    paper_v9 = resolve_paper_v9_dir()
    repository_root = paper_v9.parent
    metrics = resolve_metrics_dir()
    figures = resolve_figures_dir()

    paths = {
        "activity": metrics / "m3_activity_rolling_7day.csv",
        "clean_churn": metrics / "m4_rolling_7day_trajectory.csv",
        "planning": metrics / "m6a_structural_planning.csv",
        "evaluator": repository_root / "data" / "lake" / "evaluator_team_cuts.parquet",
    }
    activity = pd.read_csv(paths["activity"], dtype={"Semestre": str})
    clean_churn = pd.read_csv(paths["clean_churn"], dtype={"Semestre": str})
    planning = pd.read_csv(paths["planning"], dtype={"Semestre": str})
    evaluator = pd.read_parquet(paths["evaluator"])

    _require_columns(activity, [*TEAM_KEY, "window_end_day", "commit_n"], paths["activity"])
    _require_columns(clean_churn, [*TEAM_KEY, "window_end_day", "clean_churn_7d"], paths["clean_churn"])
    _require_columns(
        planning,
        [
            *TEAM_KEY,
            "planning_artifact_present_t1",
            "planning_scope_log1p_t1",
        ],
        paths["planning"],
    )
    _require_columns(evaluator, [*TEAM_KEY, "temporal_marker", *EVALUATOR_SCORE_COLUMNS], paths["evaluator"])

    tiers, evaluator_median, planning_median = _load_tier_frame(planning, evaluator)
    plot_data = _prepare_plot_data(
        activity,
        tiers,
        value_column="commit_n",
        total_column="team_window_commit_total",
        share_column="team_window_commit_share_pct",
    )
    clean_churn_plot_data = _prepare_plot_data(
        clean_churn,
        tiers,
        value_column="clean_churn_7d",
        total_column="team_window_clean_churn_total",
        share_column="team_window_clean_churn_share_pct",
        exclude_zero_totals=True,
    )

    config = {
        "contract_version": CONTRACT_VERSION,
        "window_end_days": list(WINDOW_END_DAYS),
        "tier_rule": (
            "High tier requires T3 evaluator composite >= sample median, "
            "T1 planning scope >= sample median, and an observed T1 planning artifact; "
            "all other team-semesters are assigned to the lower/weaker-planning tier."
        ),
        "evaluator_score_columns": EVALUATOR_SCORE_COLUMNS,
        "bootstrap_samples": BOOTSTRAP_SAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
    }
    commit_artifacts = _generate_metric_plot(
        plot_data=plot_data,
        stem=STEM,
        figures=figures,
        normalized_column="team_window_commit_share_pct",
        summary_prefix="team_window_commit",
        title="Late-stage repository activity by evaluator/planning tier",
        yaxis_title="Mean share of each team-semester's D-6..D0 commits (%)",
        note=(
            "Thin lines show individual team-semesters; bold lines show "
            "team-normalized mean commit timing shares with bootstrap 95% intervals."
        ),
    )
    clean_churn_artifacts = _generate_metric_plot(
        plot_data=clean_churn_plot_data,
        stem=CHURN_STEM,
        figures=figures,
        normalized_column="team_window_clean_churn_share_pct",
        summary_prefix="team_window_clean_churn",
        title="Late-stage changed lines by evaluator/planning tier",
        yaxis_title="Mean share of each team-semester's D-6..D0 clean changed lines (%)",
        note=(
            "Thin lines show individual team-semesters; bold lines show team-normalized "
            "mean clean changed-line timing shares with bootstrap 95% intervals."
        ),
    )
    metadata = {
        "status": "success",
        "contract_version": CONTRACT_VERSION,
        "rq": "RQ2",
        "unit_of_analysis": "team_semester_trailing_7_day_window",
        "input_sha256": hashlib.sha256(
            "".join(compute_sha256(path) for path in paths.values()).encode()
        ).hexdigest(),
        "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
        "inputs": {name: str(path.relative_to(repository_root)) for name, path in paths.items()},
        "artifacts": commit_artifacts,
        "coverage": {
            "team_semesters": int(plot_data[TEAM_KEY].drop_duplicates().shape[0]),
            "high_evaluator_good_planning_n": int(tiers["tier"].eq(HIGH_TIER).sum()),
            "lower_or_weaker_planning_n": int(tiers["tier"].eq(LOWER_TIER).sum()),
            "window_count": len(WINDOW_END_DAYS),
        },
        "activity_normalization": "Each team-semester sums to 100% across the displayed D-6..D0 trailing-window points before tier aggregation.",
        "thresholds": {
            "evaluator_score_t3_median": evaluator_median,
            "planning_scope_log1p_t1_median": planning_median,
        },
        "inference": "descriptive_non_causal",
        "limitations": [
            "The figure compares observed repository activity patterns and does not causally identify student syndrome.",
            "The high tier combines evaluator outcomes with repository-visible T1 planning artifacts; off-repository planning remains unobserved.",
            "Rolling seven-day windows overlap and should be read as a trajectory visualization rather than independent observations.",
        ],
        "config": config,
    }
    _atomic_json(metadata, figures / f"{STEM}.metadata.json")
    clean_churn_metadata = {
        **metadata,
        "artifacts": clean_churn_artifacts,
        "activity_metric": "clean_source_or_test_changed_lines",
        "activity_column": "clean_churn_7d",
        "activity_normalization": "Each team-semester sums to 100% across the displayed D-6..D0 clean changed-line windows before tier aggregation.",
        "coverage": {
            **metadata["coverage"],
            "team_semesters": int(clean_churn_plot_data[TEAM_KEY].drop_duplicates().shape[0]),
            "included_high_evaluator_good_planning_n": int(
                clean_churn_plot_data.loc[clean_churn_plot_data["tier"].eq(HIGH_TIER), TEAM_KEY]
                .drop_duplicates()
                .shape[0]
            ),
            "included_lower_or_weaker_planning_n": int(
                clean_churn_plot_data.loc[clean_churn_plot_data["tier"].eq(LOWER_TIER), TEAM_KEY]
                .drop_duplicates()
                .shape[0]
            ),
            "excluded_zero_clean_churn_team_semesters": clean_churn_plot_data.attrs["excluded_zero_activity"],
        },
        "limitations": [
            *metadata["limitations"],
            "M4 clean changed lines use path-based source/test provenance and are not semantic defect validation.",
        ],
    }
    _atomic_json(clean_churn_metadata, figures / f"{CHURN_STEM}.metadata.json")
    return {
        "status": "generated",
        "artifacts": [*commit_artifacts, *clean_churn_artifacts],
        "coverage": metadata["coverage"],
    }


def main() -> None:
    print(json.dumps(generate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
