"""Generate full-period student-syndrome robustness plots for RQ2."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.artifact_policy import is_clean_path
from paper_v9.scripts.common.paths import (
    resolve_figures_dir,
    resolve_metrics_dir,
    resolve_paper_v9_dir,
)
from paper_v9.scripts.common.provenance import compute_sha256
from paper_v9.scripts.results.generate_student_syndrome_plot import (
    BOOTSTRAP_SAMPLES,
    BOOTSTRAP_SEED,
    EVALUATOR_SCORE_COLUMNS,
    HIGH_TIER,
    LOWER_TIER,
    TEAM_KEY,
    TIER_COLORS,
    _atomic_csv,
    _atomic_json,
    _bootstrap_interval,
    _hex_to_rgba,
    _load_tier_frame,
    _require_columns,
    _write_figure,
)

CONTRACT_VERSION = "rq2-student-syndrome-full-period-v1"
COMMIT_STEM = "rq2_student_syndrome_full_period_commits_by_tier"
CHURN_STEM = "rq2_student_syndrome_full_period_clean_churn_by_tier"
CONCENTRATION_STEM = "rq2_student_syndrome_final7_concentration_by_tier"
CHECKPOINTS = ("T1", "T2", "T3")


def _load_checkpoint_anchors(repository_root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    group_column = "To which group do these scores refer?"
    timestamp_column = "Timestamp"
    for semester in ("2025.2", "2026.1"):
        path = repository_root / "data" / "processed" / "forms" / semester / "avaliadores.csv"
        frame = pd.read_csv(path)
        _require_columns(frame, [timestamp_column, group_column], path)
        frame["ID_Equipe"] = (
            frame[group_column]
            .astype(str)
            .str.extract(r"Group\s+(\d+)", expand=False)
            .map(lambda value: f"TEAM_{int(value):02d}" if pd.notna(value) else None)
        )
        frame["vote_at"] = (
            pd.to_datetime(frame[timestamp_column], format="mixed")
            .dt.tz_localize("America/Fortaleza")
            .dt.tz_convert("UTC")
        )
        frame = frame.dropna(subset=["ID_Equipe", "vote_at"])

        dates = sorted(frame["vote_at"].dt.date.unique())
        if len(dates) % len(CHECKPOINTS) != 0:
            raise ValueError(f"Cannot partition evaluator dates into T1/T2/T3 for {semester}: {dates}")
        date_to_checkpoint: dict[Any, str] = {}
        dates_per_checkpoint = len(dates) // len(CHECKPOINTS)
        for index, checkpoint in enumerate(CHECKPOINTS):
            for date in dates[index * dates_per_checkpoint : (index + 1) * dates_per_checkpoint]:
                date_to_checkpoint[date] = checkpoint

        frame["checkpoint"] = frame["vote_at"].dt.date.map(date_to_checkpoint)
        anchors = frame.groupby(["ID_Equipe", "checkpoint"], as_index=False)["vote_at"].max()
        anchors["Semestre"] = semester
        rows.extend(anchors.to_dict("records"))

    anchors = pd.DataFrame(rows)
    wide = anchors.pivot(index=TEAM_KEY, columns="checkpoint", values="vote_at").reset_index()
    _require_columns(wide, [*TEAM_KEY, *CHECKPOINTS], Path("checkpoint_anchors"))
    if len(wide) != 14:
        raise ValueError(f"Expected checkpoint anchors for 14 team-semesters, got {len(wide)}")
    return wide


def _checkpoint_stats(anchors: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    t3 = pd.to_datetime(anchors["T3"], utc=True)
    for checkpoint in CHECKPOINTS:
        values = (pd.to_datetime(anchors[checkpoint], utc=True) - t3).dt.total_seconds() / 86400
        rows.append(
            {
                "checkpoint": checkpoint,
                "median_day_relative_to_t3": float(values.median()),
                "min_day_relative_to_t3": float(values.min()),
                "max_day_relative_to_t3": float(values.max()),
            }
        )
    return pd.DataFrame(rows)


def _commit_events(commits: pd.DataFrame, anchors: pd.DataFrame) -> pd.DataFrame:
    _require_columns(commits, [*TEAM_KEY, "commit_hash", "timestamp"], Path("git_commits.parquet"))
    events = commits[[*TEAM_KEY, "commit_hash", "timestamp"]].drop_duplicates().copy()
    events["timestamp"] = pd.to_datetime(events["timestamp"], utc=True)
    events["metric_value"] = 1.0
    return _with_relative_days(events, anchors)


def _clean_churn_events(files: pd.DataFrame, anchors: pd.DataFrame) -> pd.DataFrame:
    _require_columns(
        files,
        [*TEAM_KEY, "commit_hash", "timestamp", "file_path", "lines_added", "lines_deleted"],
        Path("git_files.parquet"),
    )
    events = files.copy()
    events["timestamp"] = pd.to_datetime(events["timestamp"], utc=True)
    events["lines_added"] = pd.to_numeric(events["lines_added"], errors="coerce").fillna(0)
    events["lines_deleted"] = pd.to_numeric(events["lines_deleted"], errors="coerce").fillna(0)
    events["metric_value"] = events["lines_added"] + events["lines_deleted"]
    events = events.loc[events["file_path"].map(is_clean_path), [*TEAM_KEY, "commit_hash", "timestamp", "metric_value"]]
    return _with_relative_days(events, anchors)


def _with_relative_days(events: pd.DataFrame, anchors: pd.DataFrame) -> pd.DataFrame:
    result = events.merge(anchors[[*TEAM_KEY, "T3"]], on=TEAM_KEY, validate="many_to_one")
    result["T3"] = pd.to_datetime(result["T3"], utc=True)
    result["day_relative_to_t3"] = (result["timestamp"] - result["T3"]).dt.total_seconds() / 86400
    return result.loc[result["day_relative_to_t3"].lt(0)].copy()


def _rolling_windows(events: pd.DataFrame, tiers: pd.DataFrame, *, metric_label: str) -> pd.DataFrame:
    if events.empty:
        raise ValueError(f"No pre-T3 events available for {metric_label}")
    start_day = math.floor(float(events["day_relative_to_t3"].min())) + 1
    window_days = list(range(start_day, 1))
    rows: list[dict[str, Any]] = []
    for key, group in events.groupby(TEAM_KEY, sort=False):
        relative_days = group["day_relative_to_t3"].to_numpy(dtype=float)
        values = group["metric_value"].to_numpy(dtype=float)
        for window_end_day in window_days:
            mask = (relative_days >= window_end_day - 7) & (relative_days < window_end_day)
            rows.append(
                {
                    "ID_Equipe": key[0],
                    "Semestre": key[1],
                    "window_end_day": window_end_day,
                    "rolling_7d_value": float(values[mask].sum()),
                }
            )

    rolling = pd.DataFrame(rows).merge(
        tiers[[*TEAM_KEY, "tier", "evaluator_score_t3", "planning_artifact_present_t1", "planning_scope_log1p_t1"]],
        on=TEAM_KEY,
        validate="many_to_one",
    )
    rolling["team_full_period_rolling_max"] = rolling.groupby(TEAM_KEY)["rolling_7d_value"].transform("max")
    zero = rolling.loc[rolling["team_full_period_rolling_max"].eq(0), TEAM_KEY].drop_duplicates()
    if not zero.empty:
        raise ValueError(f"Cannot normalize zero-activity full-period series for {metric_label}: {zero.to_dict('records')}")
    rolling["team_full_period_rolling_intensity_pct"] = (
        100 * rolling["rolling_7d_value"] / rolling["team_full_period_rolling_max"]
    )
    rolling["activity_metric"] = metric_label
    return rolling


def _summarize_rolling(rolling: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for tier, group in rolling.groupby("tier", sort=False):
        matrix_frame = group.pivot(
            index=TEAM_KEY,
            columns="window_end_day",
            values="team_full_period_rolling_intensity_pct",
        ).sort_index(axis=1)
        matrix = matrix_frame.to_numpy(dtype=float)
        lower, upper = _bootstrap_interval(matrix)
        mean = matrix.mean(axis=0)
        median = np.median(matrix, axis=0)
        for index, window_end_day in enumerate(matrix_frame.columns.tolist()):
            rows.append(
                {
                    "tier": tier,
                    "window_end_day": int(window_end_day),
                    "team_semester_n": matrix.shape[0],
                    "mean_team_full_period_rolling_intensity_pct": mean[index],
                    "median_team_full_period_rolling_intensity_pct": median[index],
                    "ci95_lower": lower[index],
                    "ci95_upper": upper[index],
                }
            )
    return pd.DataFrame(rows)


def _add_checkpoint_markers(figure: go.Figure, checkpoint_stats: pd.DataFrame) -> None:
    for row in checkpoint_stats.to_dict("records"):
        checkpoint = row["checkpoint"]
        median_day = row["median_day_relative_to_t3"]
        if checkpoint != "T3":
            figure.add_vrect(
                x0=row["min_day_relative_to_t3"],
                x1=row["max_day_relative_to_t3"],
                fillcolor="#71717a",
                opacity=0.08,
                layer="below",
                line_width=0,
            )
        figure.add_vline(
            x=median_day,
            line_dash="dash" if checkpoint == "T3" else "dot",
            line_color="#3f3f46",
            line_width=1.3,
        )
        figure.add_annotation(
            x=median_day,
            y=1.04,
            xref="x",
            yref="paper",
            text=checkpoint,
            showarrow=False,
            font={"size": 13, "color": "#3f3f46"},
        )


def _build_full_period_figure(
    rolling: pd.DataFrame,
    summary: pd.DataFrame,
    checkpoint_stats: pd.DataFrame,
    *,
    title: str,
    yaxis_title: str,
) -> go.Figure:
    figure = go.Figure()
    for tier in (HIGH_TIER, LOWER_TIER):
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
            fillcolor=_hex_to_rgba(color, 0.12),
            line={"color": "rgba(255,255,255,0)"},
            hoverinfo="skip",
            showlegend=False,
        )
        individuals = rolling.loc[rolling["tier"].eq(tier)]
        for _, team in individuals.groupby(TEAM_KEY):
            team = team.sort_values("window_end_day")
            figure.add_trace(
                go.Scatter(
                    x=team["window_end_day"],
                    y=team["team_full_period_rolling_intensity_pct"],
                    mode="lines",
                    line={"color": color, "width": 0.85},
                    opacity=0.14,
                    hoverinfo="skip",
                    showlegend=False,
                )
            )
        team_count = int(tier_summary["team_semester_n"].iloc[0])
        figure.add_trace(
            go.Scatter(
                x=tier_summary["window_end_day"],
                y=tier_summary["mean_team_full_period_rolling_intensity_pct"],
                mode="lines+markers",
                line={"color": color, "width": 3.2},
                marker={"size": 7, "line": {"width": 1.2, "color": "white"}},
                name=f"{tier} (n={team_count})",
                customdata=np.stack(
                    [
                        tier_summary["median_team_full_period_rolling_intensity_pct"],
                        tier_summary["ci95_lower"],
                        tier_summary["ci95_upper"],
                    ],
                    axis=-1,
                ),
                hovertemplate=(
                    "Window ending D%{x}<br>"
                    "Mean rolling intensity=%{y:.2f}%<br>"
                    "Median rolling intensity=%{customdata[0]:.2f}%<br>"
                    "95% interval=%{customdata[1]:.2f}%–%{customdata[2]:.2f}%"
                    "<extra></extra>"
                ),
            )
        )

    _add_checkpoint_markers(figure, checkpoint_stats)
    figure.update_layout(
        template="simple_white",
        width=1300,
        height=680,
        margin={"l": 95, "r": 45, "t": 95, "b": 120},
        title={"text": title, "font": {"size": 24}},
        font={"size": 15, "family": "DejaVu Sans, Arial, sans-serif"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
        xaxis={
            "title": "Trailing 7-day window ending at day relative to each team's T3 anchor",
            "showgrid": False,
            "zeroline": False,
            "title_font": {"size": 16},
        },
        yaxis={
            "title": yaxis_title,
            "range": [0, 105],
            "gridcolor": "#e5e7eb",
            "zeroline": True,
            "zerolinecolor": "#cbd5e1",
            "title_font": {"size": 16},
        },
        annotations=[
            *figure.layout.annotations,
            {
                "text": (
                    "Thin lines show individual team-semesters; bold lines show tier means. "
                    "Checkpoint lines mark median T1/T2/T3 positions; gray bands show T1/T2 min–max ranges."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.2,
                "showarrow": False,
                "align": "left",
                "font": {"size": 13, "color": "#52525b"},
            },
        ],
    )
    return figure


def _final7_concentration(events: pd.DataFrame, tiers: pd.DataFrame, *, metric: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, group in events.groupby(TEAM_KEY, sort=False):
        total = float(group["metric_value"].sum())
        final = float(group.loc[group["day_relative_to_t3"].ge(-7), "metric_value"].sum())
        if total == 0:
            continue
        rows.append(
            {
                "ID_Equipe": key[0],
                "Semestre": key[1],
                "activity_metric": metric,
                "project_total": total,
                "final7_total": final,
                "final7_share_pct": 100 * final / total,
            }
        )
    return pd.DataFrame(rows).merge(tiers[[*TEAM_KEY, "tier", "evaluator_score_t3"]], on=TEAM_KEY, validate="many_to_one")


def _build_concentration_figure(concentration: pd.DataFrame) -> go.Figure:
    figure = make_subplots(
        rows=1,
        cols=2,
        horizontal_spacing=0.13,
    )
    metric_order = ["commits", "clean_source_or_test_changed_lines"]
    for column, metric in enumerate(metric_order, start=1):
        metric_data = concentration.loc[concentration["activity_metric"].eq(metric)]
        for tier in (HIGH_TIER, LOWER_TIER):
            tier_data = metric_data.loc[metric_data["tier"].eq(tier)]
            figure.add_trace(
                go.Box(
                    x=[tier] * len(tier_data),
                    y=tier_data["final7_share_pct"],
                    name=tier,
                    marker_color=TIER_COLORS[tier],
                    boxpoints="all",
                    jitter=0.45,
                    pointpos=0,
                    boxmean=True,
                    showlegend=column == 1,
                    hovertext=tier_data["ID_Equipe"] + " / " + tier_data["Semestre"].astype(str),
                    hovertemplate="%{hovertext}<br>Final-7 share=%{y:.2f}%<extra></extra>",
                ),
                row=1,
                col=column,
            )
        figure.update_xaxes(title="", showticklabels=False, row=1, col=column)
        figure.update_yaxes(range=[0, 105], row=1, col=column)
    figure.update_yaxes(title="Share of pre-T3 project activity in final 7 days (%)", row=1, col=1)
    figure.add_annotation(x=0.225, y=1.0, xref="paper", yref="paper", text="Commits", showarrow=False, font={"size": 17})
    figure.add_annotation(x=0.775, y=1.0, xref="paper", yref="paper", text="Clean changed lines", showarrow=False, font={"size": 17})
    figure.update_layout(
        template="simple_white",
        width=1200,
        height=560,
        margin={"l": 80, "r": 35, "t": 120, "b": 75},
        title={"text": "Final-7-day activity concentration by evaluator/planning tier", "font": {"size": 22}, "y": 0.98},
        font={"size": 14, "family": "DejaVu Sans, Arial, sans-serif"},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.08, "xanchor": "left", "x": 0},
    )
    return figure


def _write_full_period_outputs(
    rolling: pd.DataFrame,
    checkpoint_stats: pd.DataFrame,
    figures: Path,
    *,
    stem: str,
    title: str,
    yaxis_title: str,
) -> list[str]:
    summary = _summarize_rolling(rolling)
    _atomic_csv(rolling.sort_values([*TEAM_KEY, "window_end_day"]), figures / f"{stem}_data.csv")
    _atomic_csv(summary.sort_values(["tier", "window_end_day"]), figures / f"{stem}_summary.csv")
    figure = _build_full_period_figure(
        rolling,
        summary,
        checkpoint_stats,
        title=title,
        yaxis_title=yaxis_title,
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
        "commits": repository_root / "data" / "lake" / "git_commits.parquet",
        "files": repository_root / "data" / "lake" / "git_files.parquet",
        "planning": metrics / "m6a_structural_planning.csv",
        "evaluator": repository_root / "data" / "lake" / "evaluator_team_cuts.parquet",
        "evaluator_forms_2025_2": repository_root / "data" / "processed" / "forms" / "2025.2" / "avaliadores.csv",
        "evaluator_forms_2026_1": repository_root / "data" / "processed" / "forms" / "2026.1" / "avaliadores.csv",
    }
    commits = pd.read_parquet(paths["commits"])
    files = pd.read_parquet(paths["files"])
    planning = pd.read_csv(paths["planning"], dtype={"Semestre": str})
    evaluator = pd.read_parquet(paths["evaluator"])
    _require_columns(planning, [*TEAM_KEY, "planning_artifact_present_t1", "planning_scope_log1p_t1"], paths["planning"])
    _require_columns(evaluator, [*TEAM_KEY, "temporal_marker", *EVALUATOR_SCORE_COLUMNS], paths["evaluator"])

    tiers, evaluator_median, planning_median = _load_tier_frame(planning, evaluator)
    anchors = _load_checkpoint_anchors(repository_root)
    checkpoint_stats = _checkpoint_stats(anchors)
    commit_events = _commit_events(commits, anchors)
    churn_events = _clean_churn_events(files, anchors)

    commit_rolling = _rolling_windows(commit_events, tiers, metric_label="commits")
    churn_rolling = _rolling_windows(churn_events, tiers, metric_label="clean_source_or_test_changed_lines")
    concentration = pd.concat(
        [
            _final7_concentration(commit_events, tiers, metric="commits"),
            _final7_concentration(churn_events, tiers, metric="clean_source_or_test_changed_lines"),
        ],
        ignore_index=True,
    )

    commit_artifacts = _write_full_period_outputs(
        commit_rolling,
        checkpoint_stats,
        figures,
        stem=COMMIT_STEM,
        title="Full-period rolling commit activity by evaluator/planning tier",
        yaxis_title="Mean rolling commits (% of each team-semester's maximum)",
    )
    churn_artifacts = _write_full_period_outputs(
        churn_rolling,
        checkpoint_stats,
        figures,
        stem=CHURN_STEM,
        title="Full-period rolling clean changed lines by evaluator/planning tier",
        yaxis_title="Mean rolling clean changed lines (% of each team-semester's maximum)",
    )
    _atomic_csv(concentration.sort_values(["activity_metric", "tier", *TEAM_KEY]), figures / f"{CONCENTRATION_STEM}_data.csv")
    concentration_figure = _build_concentration_figure(concentration)
    _write_figure(concentration_figure, CONCENTRATION_STEM, figures)
    concentration_artifacts = [
        f"figures/{CONCENTRATION_STEM}.pdf",
        f"figures/{CONCENTRATION_STEM}.svg",
        f"figures/{CONCENTRATION_STEM}.png",
        f"figures/{CONCENTRATION_STEM}_data.csv",
        f"figures/{CONCENTRATION_STEM}.metadata.json",
    ]

    config = {
        "contract_version": CONTRACT_VERSION,
        "rolling_window_days": 7,
        "rolling_normalization": "Each team-semester's rolling series is scaled so its maximum pre-T3 rolling value equals 100%.",
        "timeline": "days_relative_to_team_specific_t3_anchor",
        "checkpoint_markers": "median T1/T2/T3 relative positions with T1/T2 min-max bands",
        "tier_rule": (
            "High tier requires T3 evaluator composite >= sample median, "
            "T1 planning scope >= sample median, and an observed T1 planning artifact; "
            "all other team-semesters are assigned to the lower/weaker-planning tier."
        ),
        "evaluator_score_columns": EVALUATOR_SCORE_COLUMNS,
        "bootstrap_samples": BOOTSTRAP_SAMPLES,
        "bootstrap_seed": BOOTSTRAP_SEED,
    }
    input_sha256 = hashlib.sha256("".join(compute_sha256(path) for path in paths.values()).encode()).hexdigest()
    config_sha256 = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    base_metadata: dict[str, Any] = {
        "status": "success",
        "contract_version": CONTRACT_VERSION,
        "rq": "RQ2",
        "unit_of_analysis": "team_semester_trailing_7_day_window",
        "input_sha256": input_sha256,
        "config_sha256": config_sha256,
        "inputs": {name: str(path.relative_to(repository_root)) for name, path in paths.items()},
        "thresholds": {
            "evaluator_score_t3_median": evaluator_median,
            "planning_scope_log1p_t1_median": planning_median,
        },
        "coverage": {
            "team_semesters": 14,
            "high_evaluator_good_planning_n": int(tiers["tier"].eq(HIGH_TIER).sum()),
            "lower_or_weaker_planning_n": int(tiers["tier"].eq(LOWER_TIER).sum()),
            "commit_windows": int(commit_rolling["window_end_day"].nunique()),
            "clean_churn_windows": int(churn_rolling["window_end_day"].nunique()),
        },
        "checkpoint_stats": checkpoint_stats.to_dict("records"),
        "config": config,
        "inference": "descriptive_non_causal",
        "limitations": [
            "The full-period trajectories compare observed repository activity patterns and do not causally identify student syndrome.",
            "Rolling seven-day windows overlap and should be read as trajectory visualization rather than independent observations.",
            "Checkpoint markers are team-specific evaluator anchors summarized as median relative positions; the T1/T2 bands show their observed ranges.",
            "The high tier combines evaluator outcomes with repository-visible T1 planning artifacts; off-repository planning remains unobserved.",
        ],
    }
    _atomic_json({**base_metadata, "activity_metric": "commits", "artifacts": commit_artifacts}, figures / f"{COMMIT_STEM}.metadata.json")
    _atomic_json(
        {
            **base_metadata,
            "activity_metric": "clean_source_or_test_changed_lines",
            "artifacts": churn_artifacts,
            "limitations": [
                *base_metadata["limitations"],
                "Clean changed lines use path-based source/test provenance and are not semantic defect validation.",
            ],
        },
        figures / f"{CHURN_STEM}.metadata.json",
    )
    _atomic_json(
        {
            **base_metadata,
            "activity_metric": "final7_concentration",
            "artifacts": concentration_artifacts,
            "definition": "Share of each team-semester's pre-T3 project activity occurring in the final seven days before T3.",
        },
        figures / f"{CONCENTRATION_STEM}.metadata.json",
    )
    return {
        "status": "generated",
        "artifacts": [*commit_artifacts, *churn_artifacts, *concentration_artifacts],
        "coverage": base_metadata["coverage"],
    }


def main() -> None:
    print(json.dumps(generate(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
