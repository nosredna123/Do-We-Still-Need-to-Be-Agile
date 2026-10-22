"""Generate non-overlapping weekly and phase activity bins for RQ2."""

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

from paper_v9.scripts.common.artifact_policy import CURRENT_POLICY_VERSION, is_clean_path
from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "rq2-nonoverlapping-phase-activity-v1"
STEM = "rq2_nonoverlapping_phase_activity"
WEEKLY_STEM = "rq2_nonoverlapping_weekly_activity"
PHASE_STEM = "rq2_phase_activity_share"
WEEKLY_BIN_CONTRACT_STEM = "rq2_nonoverlapping_weekly_bin_contract"
WEEKLY_ASSIGNMENT_AUDIT_STEM = "rq2_nonoverlapping_weekly_assignment_audit"
WEEKLY_OVERVIEW_STEM = "rq2_nonoverlapping_weekly_activity_overview"
PHASE_OVERVIEW_STEM = "rq2_phase_activity_share_overview"
PHASE_COMMIT_SHARE_STEM = "rq2_phase_commit_share_by_score_trajectory"
PHASE_CLEAN_CHURN_SHARE_STEM = "rq2_phase_clean_churn_share_by_score_trajectory"
TEAM_KEY = ["ID_Equipe", "Semestre"]
CHECKPOINTS = ("T1", "T2", "T3")
WEEK_BIN_LABELS = [f"week_{index}" for index in range(-12, 0)] + ["final_7_days"]
PHASE_LABELS = ["pre_t1", "t1_to_t2", "t2_to_t3_excluding_final7", "final7_pre_t3"]
PHASE_DISPLAY_LABELS = {
    "pre_t1": "Pre-T1",
    "t1_to_t2": "T1-T2",
    "t2_to_t3_excluding_final7": "T2-T3 excl. final 7",
    "final7_pre_t3": "Final 7 pre-T3",
}
SCORE_GROUP_COLORS = {
    "improved": "#16a34a",
    "stable": "#64748b",
    "declined": "#dc2626",
}
REQUIRED_COMMITS_COLUMNS = [*TEAM_KEY, "commit_hash", "timestamp", "ID_Autor_Local"]
REQUIRED_FILES_COLUMNS = [*TEAM_KEY, "commit_hash", "timestamp", "file_path", "lines_added", "lines_deleted"]
REQUIRED_SCORE_COLUMNS = [
    *TEAM_KEY,
    "score_trajectory_group",
    "planning_scope_tier",
    "evaluator_score_t3",
    "delta_score_t3_minus_t1",
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
    return wide.sort_values(TEAM_KEY).reset_index(drop=True)


def _prepare_commit_events(commits: pd.DataFrame) -> pd.DataFrame:
    events = commits[REQUIRED_COMMITS_COLUMNS].drop_duplicates().copy()
    events["timestamp"] = pd.to_datetime(events["timestamp"], utc=True)
    events["ID_Autor_Local"] = events["ID_Autor_Local"].fillna("unknown_author")
    return events


def _prepare_clean_churn_events(files: pd.DataFrame) -> pd.DataFrame:
    events = files[REQUIRED_FILES_COLUMNS].copy()
    events["timestamp"] = pd.to_datetime(events["timestamp"], utc=True)
    events["lines_added"] = pd.to_numeric(events["lines_added"], errors="coerce").fillna(0)
    events["lines_deleted"] = pd.to_numeric(events["lines_deleted"], errors="coerce").fillna(0)
    events["clean_churn"] = events["lines_added"] + events["lines_deleted"]
    events = events.loc[events["file_path"].map(is_clean_path), [*TEAM_KEY, "commit_hash", "timestamp", "clean_churn"]]
    return events


def _week_specs(t3_anchor: pd.Timestamp) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for position, week_index in enumerate(range(-12, 0), start=1):
        start_days = (week_index - 1) * 7
        end_days = week_index * 7
        specs.append(
            {
                "week_bin": f"week_{week_index}",
                "week_bin_order": position,
                "period_start": t3_anchor + pd.Timedelta(days=start_days),
                "period_end": t3_anchor + pd.Timedelta(days=end_days),
                "start_day_relative_to_t3": start_days,
                "end_day_relative_to_t3": end_days,
            }
        )
    specs.append(
        {
            "week_bin": "final_7_days",
            "week_bin_order": len(specs) + 1,
            "period_start": t3_anchor - pd.Timedelta(days=7),
            "period_end": t3_anchor,
            "start_day_relative_to_t3": -7,
            "end_day_relative_to_t3": 0,
        }
    )
    return specs


def _weekly_bin_contract(anchors: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for anchor in anchors.to_dict("records"):
        for spec in _week_specs(pd.Timestamp(anchor["T3"])):
            rows.append(
                {
                    "ID_Equipe": anchor["ID_Equipe"],
                    "Semestre": anchor["Semestre"],
                    "week_bin": spec["week_bin"],
                    "week_bin_order": spec["week_bin_order"],
                    "period_start": spec["period_start"],
                    "period_end": spec["period_end"],
                    "start_day_relative_to_t3": spec["start_day_relative_to_t3"],
                    "end_day_relative_to_t3": spec["end_day_relative_to_t3"],
                    "interval_notation": "[period_start, period_end)",
                    "assignment_policy": "nonoverlapping_fixed_interval_relative_to_team_t3",
                    "rolling_window_used": False,
                }
            )
    contract = pd.DataFrame(rows)
    if len(contract) != 14 * len(WEEK_BIN_LABELS):
        raise ValueError(f"Expected {14 * len(WEEK_BIN_LABELS)} weekly bin contract rows, got {len(contract)}")
    return contract.sort_values([*TEAM_KEY, "week_bin_order"]).reset_index(drop=True)


def _phase_specs(anchor: pd.Series, observed_start: pd.Timestamp | None) -> list[dict[str, Any]]:
    t1 = pd.Timestamp(anchor["T1"])
    t2 = pd.Timestamp(anchor["T2"])
    t3 = pd.Timestamp(anchor["T3"])
    final7_start = t3 - pd.Timedelta(days=7)
    pre_t1_start = (
        observed_start
        if observed_start is not None and pd.notna(observed_start) and observed_start < t1
        else pd.NaT
    )
    return [
        {
            "phase": "pre_t1",
            "phase_order": 1,
            "period_start": pre_t1_start,
            "period_end": t1,
            "start_inclusive": False,
            "end_exclusive": True,
        },
        {
            "phase": "t1_to_t2",
            "phase_order": 2,
            "period_start": t1,
            "period_end": t2,
            "start_inclusive": True,
            "end_exclusive": True,
        },
        {
            "phase": "t2_to_t3_excluding_final7",
            "phase_order": 3,
            "period_start": t2,
            "period_end": final7_start,
            "start_inclusive": True,
            "end_exclusive": True,
        },
        {
            "phase": "final7_pre_t3",
            "phase_order": 4,
            "period_start": final7_start,
            "period_end": t3,
            "start_inclusive": True,
            "end_exclusive": True,
        },
    ]


def _events_in_period(events: pd.DataFrame, start: pd.Timestamp | pd.NaT, end: pd.Timestamp) -> pd.DataFrame:
    if pd.isna(start):
        return events.loc[events["timestamp"].lt(end)]
    return events.loc[events["timestamp"].ge(start) & events["timestamp"].lt(end)]


def _activity_metrics(commits: pd.DataFrame, clean_churn: pd.DataFrame) -> dict[str, Any]:
    return {
        "commit_n": int(commits["commit_hash"].nunique()) if not commits.empty else 0,
        "clean_churn": float(clean_churn["clean_churn"].sum()) if not clean_churn.empty else 0.0,
        "active_day_n": int(commits["timestamp"].dt.floor("D").nunique()) if not commits.empty else 0,
        "active_author_n": int(commits["ID_Autor_Local"].nunique()) if not commits.empty else 0,
    }


def _weekly_activity(
    commits: pd.DataFrame,
    clean_churn: pd.DataFrame,
    anchors: pd.DataFrame,
    score_base: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for anchor in anchors.to_dict("records"):
        key_filter = commits["ID_Equipe"].eq(anchor["ID_Equipe"]) & commits["Semestre"].eq(anchor["Semestre"])
        team_commits = commits.loc[key_filter]
        churn_filter = clean_churn["ID_Equipe"].eq(anchor["ID_Equipe"]) & clean_churn["Semestre"].eq(anchor["Semestre"])
        team_churn = clean_churn.loc[churn_filter]
        for spec in _week_specs(pd.Timestamp(anchor["T3"])):
            period_commits = _events_in_period(team_commits, spec["period_start"], spec["period_end"])
            period_churn = _events_in_period(team_churn, spec["period_start"], spec["period_end"])
            rows.append(
                {
                    "ID_Equipe": anchor["ID_Equipe"],
                    "Semestre": anchor["Semestre"],
                    **{key: spec[key] for key in ["week_bin", "week_bin_order", "period_start", "period_end"]},
                    "start_day_relative_to_t3": spec["start_day_relative_to_t3"],
                    "end_day_relative_to_t3": spec["end_day_relative_to_t3"],
                    **_activity_metrics(period_commits, period_churn),
                }
            )
    weekly = pd.DataFrame(rows).merge(score_base[REQUIRED_SCORE_COLUMNS], on=TEAM_KEY, validate="many_to_one")
    if len(weekly) != 14 * len(WEEK_BIN_LABELS):
        raise ValueError(f"Expected {14 * len(WEEK_BIN_LABELS)} weekly rows, got {len(weekly)}")
    return weekly.sort_values([*TEAM_KEY, "week_bin_order"]).reset_index(drop=True)


def _weekly_assignment_audit(
    commits: pd.DataFrame,
    clean_churn: pd.DataFrame,
    anchors: pd.DataFrame,
    weekly: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    weekly_index = weekly.set_index([*TEAM_KEY, "week_bin"])
    metric_configs = [
        {
            "activity_metric": "commits",
            "events": commits,
            "event_count_column": "commit_n",
            "value_column": None,
        },
        {
            "activity_metric": "clean_file_events",
            "events": clean_churn,
            "event_count_column": None,
            "value_column": "clean_churn",
        },
    ]
    for anchor in anchors.to_dict("records"):
        specs = _week_specs(pd.Timestamp(anchor["T3"]))
        covered_start = min(spec["period_start"] for spec in specs)
        covered_end = max(spec["period_end"] for spec in specs)
        for config in metric_configs:
            events = config["events"]
            team_events = events.loc[
                events["ID_Equipe"].eq(anchor["ID_Equipe"])
                & events["Semestre"].eq(anchor["Semestre"])
                & events["timestamp"].ge(covered_start)
                & events["timestamp"].lt(covered_end)
            ].reset_index(drop=True)
            assignment_counts = pd.Series(0, index=team_events.index, dtype=int)
            assigned_event_rows = 0
            assigned_value = 0.0
            for spec in specs:
                in_bin = team_events["timestamp"].ge(spec["period_start"]) & team_events["timestamp"].lt(spec["period_end"])
                assignment_counts.loc[in_bin] = assignment_counts.loc[in_bin] + 1
                assigned_event_rows += int(in_bin.sum())
                if config["value_column"]:
                    assigned_value += float(team_events.loc[in_bin, config["value_column"]].sum())
            duplicate_assignment_rows = int(assignment_counts.gt(1).sum())
            unassigned_event_rows = int(assignment_counts.eq(0).sum())
            expected_value: float | int
            if config["event_count_column"]:
                expected_value = int(
                    weekly_index.loc[
                        (anchor["ID_Equipe"], anchor["Semestre"]),
                        config["event_count_column"],
                    ].sum()
                )
                observed_value = assigned_event_rows
            else:
                expected_value = float(
                    weekly_index.loc[
                        (anchor["ID_Equipe"], anchor["Semestre"]),
                        config["value_column"],
                    ].sum()
                )
                observed_value = assigned_value
            rows.append(
                {
                    "ID_Equipe": anchor["ID_Equipe"],
                    "Semestre": anchor["Semestre"],
                    "activity_metric": config["activity_metric"],
                    "covered_period_start": covered_start,
                    "covered_period_end": covered_end,
                    "covered_event_rows": int(len(team_events)),
                    "assigned_event_rows": assigned_event_rows,
                    "unassigned_event_rows": unassigned_event_rows,
                    "duplicate_assignment_rows": duplicate_assignment_rows,
                    "observed_weekly_metric_total": observed_value,
                    "weekly_data_metric_total": expected_value,
                    "assignment_status": (
                        "pass"
                        if unassigned_event_rows == 0
                        and duplicate_assignment_rows == 0
                        and abs(float(observed_value) - float(expected_value)) < 1e-9
                        else "fail"
                    ),
                }
            )
    audit = pd.DataFrame(rows).sort_values([*TEAM_KEY, "activity_metric"]).reset_index(drop=True)
    failed = audit.loc[audit["assignment_status"].ne("pass")]
    if not failed.empty:
        raise ValueError(f"Weekly assignment audit failed: {failed.to_dict('records')}")
    return audit


def _observed_start(
    team_commits: pd.DataFrame,
    team_churn: pd.DataFrame,
    t3_anchor: pd.Timestamp,
) -> pd.Timestamp | None:
    timestamps = pd.concat(
        [
            team_commits.loc[team_commits["timestamp"].lt(t3_anchor), "timestamp"],
            team_churn.loc[team_churn["timestamp"].lt(t3_anchor), "timestamp"],
        ],
        ignore_index=True,
    )
    if timestamps.empty:
        return None
    return pd.Timestamp(timestamps.min())


def _phase_activity(
    commits: pd.DataFrame,
    clean_churn: pd.DataFrame,
    anchors: pd.DataFrame,
    score_base: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for anchor in anchors.to_dict("records"):
        key_filter = commits["ID_Equipe"].eq(anchor["ID_Equipe"]) & commits["Semestre"].eq(anchor["Semestre"])
        team_commits = commits.loc[key_filter]
        churn_filter = clean_churn["ID_Equipe"].eq(anchor["ID_Equipe"]) & clean_churn["Semestre"].eq(anchor["Semestre"])
        team_churn = clean_churn.loc[churn_filter]
        observed_start = _observed_start(team_commits, team_churn, pd.Timestamp(anchor["T3"]))
        for spec in _phase_specs(pd.Series(anchor), observed_start):
            period_commits = _events_in_period(team_commits, spec["period_start"], spec["period_end"])
            period_churn = _events_in_period(team_churn, spec["period_start"], spec["period_end"])
            rows.append(
                {
                    "ID_Equipe": anchor["ID_Equipe"],
                    "Semestre": anchor["Semestre"],
                    **{key: spec[key] for key in ["phase", "phase_order", "period_start", "period_end"]},
                    **_activity_metrics(period_commits, period_churn),
                }
            )
    phase = pd.DataFrame(rows).merge(score_base[REQUIRED_SCORE_COLUMNS], on=TEAM_KEY, validate="many_to_one")
    if len(phase) != 14 * len(PHASE_LABELS):
        raise ValueError(f"Expected {14 * len(PHASE_LABELS)} phase rows, got {len(phase)}")
    phase["team_total_commit_n"] = phase.groupby(TEAM_KEY)["commit_n"].transform("sum")
    phase["team_total_clean_churn"] = phase.groupby(TEAM_KEY)["clean_churn"].transform("sum")
    phase["commit_share_pct"] = 100 * phase["commit_n"] / phase["team_total_commit_n"].replace(0, pd.NA)
    phase["clean_churn_share_pct"] = 100 * phase["clean_churn"] / phase["team_total_clean_churn"].replace(0, pd.NA)
    phase["commit_share_pct"] = phase["commit_share_pct"].fillna(0)
    phase["clean_churn_share_pct"] = phase["clean_churn_share_pct"].fillna(0)
    return phase.sort_values([*TEAM_KEY, "phase_order"]).reset_index(drop=True)


def _weekly_summary(weekly: pd.DataFrame) -> pd.DataFrame:
    return (
        weekly.groupby(["score_trajectory_group", "week_bin", "week_bin_order"], as_index=False)
        .agg(
            team_semester_n=("ID_Equipe", "size"),
            mean_commit_n=("commit_n", "mean"),
            median_commit_n=("commit_n", "median"),
            mean_clean_churn=("clean_churn", "mean"),
            median_clean_churn=("clean_churn", "median"),
            mean_active_day_n=("active_day_n", "mean"),
            mean_active_author_n=("active_author_n", "mean"),
        )
        .sort_values(["score_trajectory_group", "week_bin_order"])
        .reset_index(drop=True)
    )


def _phase_summary(phase: pd.DataFrame) -> pd.DataFrame:
    return (
        phase.groupby(["score_trajectory_group", "phase", "phase_order"], as_index=False)
        .agg(
            team_semester_n=("ID_Equipe", "size"),
            mean_commit_share_pct=("commit_share_pct", "mean"),
            median_commit_share_pct=("commit_share_pct", "median"),
            mean_clean_churn_share_pct=("clean_churn_share_pct", "mean"),
            median_clean_churn_share_pct=("clean_churn_share_pct", "median"),
            mean_active_day_n=("active_day_n", "mean"),
            mean_active_author_n=("active_author_n", "mean"),
        )
        .sort_values(["score_trajectory_group", "phase_order"])
        .reset_index(drop=True)
    )


def _build_weekly_overview(summary: pd.DataFrame) -> go.Figure:
    figure = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.12,
        subplot_titles=("Mean commits per non-overlapping bin", "Mean clean changed lines per non-overlapping bin"),
    )
    for score_group in ["improved", "stable", "declined"]:
        subset = summary.loc[summary["score_trajectory_group"].eq(score_group)]
        if subset.empty:
            continue
        figure.add_trace(
            go.Scatter(
                x=subset["week_bin"],
                y=subset["mean_commit_n"],
                mode="lines+markers",
                name=score_group,
                legendgroup=score_group,
                marker={"color": SCORE_GROUP_COLORS.get(score_group, "#64748b"), "size": 8},
                line={"color": SCORE_GROUP_COLORS.get(score_group, "#64748b"), "width": 2.5},
                customdata=subset[["team_semester_n", "median_commit_n", "mean_active_day_n"]],
                hovertemplate=(
                    "Bin=%{x}<br>"
                    "Mean commits=%{y:.2f}<br>"
                    "Median commits=%{customdata[1]:.2f}<br>"
                    "Mean active days=%{customdata[2]:.2f}<br>"
                    "n=%{customdata[0]}<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )
        figure.add_trace(
            go.Scatter(
                x=subset["week_bin"],
                y=subset["mean_clean_churn"],
                mode="lines+markers",
                name=score_group,
                legendgroup=score_group,
                showlegend=False,
                marker={"color": SCORE_GROUP_COLORS.get(score_group, "#64748b"), "size": 8},
                line={"color": SCORE_GROUP_COLORS.get(score_group, "#64748b"), "width": 2.5},
                customdata=subset[["team_semester_n", "median_clean_churn"]],
                hovertemplate=(
                    "Bin=%{x}<br>"
                    "Mean clean churn=%{y:,.1f}<br>"
                    "Median clean churn=%{customdata[1]:,.1f}<br>"
                    "n=%{customdata[0]}<extra></extra>"
                ),
            ),
            row=2,
            col=1,
        )
    figure.update_layout(
        template="simple_white",
        width=1200,
        height=780,
        margin={"l": 85, "r": 35, "t": 110, "b": 150},
        title={"text": "Non-overlapping weekly activity before T3", "font": {"size": 22}},
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
                    "Bins are mutually exclusive. week_-1 covers days [-14,-7) and final_7_days covers [-7,0) "
                    "relative to each team's T3 anchor; empty bins are retained as zeros."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.16,
                "xanchor": "left",
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#52525b"},
            }
        ],
    )
    figure.update_xaxes(categoryorder="array", categoryarray=WEEK_BIN_LABELS, tickangle=35, gridcolor="#e5e7eb")
    figure.update_yaxes(title="Commits", gridcolor="#e5e7eb", zeroline=True, row=1, col=1)
    figure.update_yaxes(title="Clean changed lines", gridcolor="#e5e7eb", zeroline=True, row=2, col=1)
    return figure


def _build_phase_overview(summary: pd.DataFrame) -> go.Figure:
    plot_data = summary.copy()
    plot_data["phase_display"] = plot_data["phase"].map(PHASE_DISPLAY_LABELS)
    figure = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Commit share by phase", "Clean changed-line share by phase"),
        shared_yaxes=True,
        horizontal_spacing=0.08,
    )
    metrics = {
        "mean_commit_share_pct": 1,
        "mean_clean_churn_share_pct": 2,
    }
    for metric, column in metrics.items():
        for score_group in ["improved", "stable", "declined"]:
            subset = plot_data.loc[plot_data["score_trajectory_group"].eq(score_group)]
            if subset.empty:
                continue
            figure.add_trace(
                go.Bar(
                    x=subset["phase_display"],
                    y=subset[metric],
                    name=score_group,
                    legendgroup=score_group,
                    showlegend=column == 1,
                    marker={"color": SCORE_GROUP_COLORS.get(score_group, "#64748b")},
                    customdata=subset[["phase", "team_semester_n"]],
                    hovertemplate=(
                        "Phase=%{customdata[0]}<br>"
                        "Mean share=%{y:.1f}%<br>"
                        "n=%{customdata[1]}<extra></extra>"
                    ),
                ),
                row=1,
                col=column,
            )
    figure.update_layout(
        template="simple_white",
        width=1200,
        height=660,
        barmode="group",
        margin={"l": 85, "r": 35, "t": 105, "b": 165},
        title={"text": "Activity share by non-overlapping project phase", "font": {"size": 22}},
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
                    "Phases are assigned by team-specific evaluator anchors. final7_pre_t3 is excluded from "
                    "t2_to_t3_excluding_final7 to avoid overlap."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.24,
                "xanchor": "left",
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#52525b"},
            }
        ],
    )
    figure.update_xaxes(
        categoryorder="array",
        categoryarray=[PHASE_DISPLAY_LABELS[label] for label in PHASE_LABELS],
        tickangle=0,
        gridcolor="#e5e7eb",
    )
    figure.update_yaxes(title="Mean team-semester activity share", ticksuffix="%", range=[0, 104], gridcolor="#e5e7eb")
    return figure


def _build_phase_share_figure(
    summary: pd.DataFrame,
    *,
    value_column: str,
    median_column: str,
    title: str,
    yaxis_title: str,
    note: str,
) -> go.Figure:
    plot_data = summary.copy()
    plot_data["phase_display"] = plot_data["phase"].map(PHASE_DISPLAY_LABELS)
    figure = go.Figure()
    for score_group in ["improved", "stable", "declined"]:
        subset = plot_data.loc[plot_data["score_trajectory_group"].eq(score_group)]
        if subset.empty:
            continue
        figure.add_trace(
            go.Bar(
                x=subset["phase_display"],
                y=subset[value_column],
                name=score_group,
                marker={"color": SCORE_GROUP_COLORS.get(score_group, "#64748b")},
                customdata=subset[["phase", "team_semester_n", median_column, "mean_active_day_n", "mean_active_author_n"]],
                hovertemplate=(
                    "Phase=%{customdata[0]}<br>"
                    "Mean share=%{y:.1f}%<br>"
                    "Median share=%{customdata[2]:.1f}%<br>"
                    "Mean active days=%{customdata[3]:.2f}<br>"
                    "Mean active authors=%{customdata[4]:.2f}<br>"
                    "n=%{customdata[1]}<extra></extra>"
                ),
            )
        )
    figure.update_layout(
        template="simple_white",
        width=1100,
        height=660,
        barmode="group",
        margin={"l": 85, "r": 35, "t": 110, "b": 165},
        title={"text": title, "font": {"size": 22}},
        font={"size": 14, "family": "DejaVu Sans, Arial, sans-serif"},
        legend={
            "title": "Score trajectory",
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        xaxis={
            "title": "Non-overlapping project phase",
            "categoryorder": "array",
            "categoryarray": [PHASE_DISPLAY_LABELS[label] for label in PHASE_LABELS],
            "gridcolor": "#e5e7eb",
        },
        yaxis={
            "title": yaxis_title,
            "ticksuffix": "%",
            "range": [0, 104],
            "gridcolor": "#e5e7eb",
            "zeroline": True,
            "zerolinecolor": "#cbd5e1",
        },
        annotations=[
            {
                "text": note,
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


def generate() -> dict[str, Any]:
    paper_v9 = resolve_paper_v9_dir()
    repo_root = paper_v9.parent
    figures_dir = resolve_figures_dir()
    paths = {
        "commits": repo_root / "data" / "lake" / "git_commits.parquet",
        "files": repo_root / "data" / "lake" / "git_files.parquet",
        "score_base": figures_dir / "rq2_score_trajectory_base_data.csv",
        "evaluator_forms_2025_2": repo_root / "data" / "processed" / "forms" / "2025.2" / "avaliadores.csv",
        "evaluator_forms_2026_1": repo_root / "data" / "processed" / "forms" / "2026.1" / "avaliadores.csv",
    }
    commits = pd.read_parquet(paths["commits"])
    files = pd.read_parquet(paths["files"])
    score_base = pd.read_csv(paths["score_base"], dtype={"Semestre": str})

    _require_columns(commits, REQUIRED_COMMITS_COLUMNS, paths["commits"])
    _require_columns(files, REQUIRED_FILES_COLUMNS, paths["files"])
    _require_columns(score_base, REQUIRED_SCORE_COLUMNS, paths["score_base"])

    anchors = _load_checkpoint_anchors(repo_root)
    commit_events = _prepare_commit_events(commits)
    clean_churn_events = _prepare_clean_churn_events(files)
    weekly = _weekly_activity(commit_events, clean_churn_events, anchors, score_base)
    phase = _phase_activity(commit_events, clean_churn_events, anchors, score_base)
    weekly_bin_contract = _weekly_bin_contract(anchors)
    weekly_assignment_audit = _weekly_assignment_audit(commit_events, clean_churn_events, anchors, weekly)
    weekly_summary = _weekly_summary(weekly)
    phase_summary = _phase_summary(phase)

    output_paths = {
        "weekly_data": figures_dir / f"{WEEKLY_STEM}_data.csv",
        "weekly_bin_contract": figures_dir / f"{WEEKLY_BIN_CONTRACT_STEM}.csv",
        "weekly_assignment_audit": figures_dir / f"{WEEKLY_ASSIGNMENT_AUDIT_STEM}.csv",
        "phase_data": figures_dir / f"{PHASE_STEM}_data.csv",
        "weekly_summary": figures_dir / f"{WEEKLY_STEM}_summary.csv",
        "phase_summary": figures_dir / f"{PHASE_STEM}_summary.csv",
        "metadata": figures_dir / f"{STEM}.metadata.json",
    }
    _atomic_csv(weekly, output_paths["weekly_data"])
    _atomic_csv(weekly_bin_contract, output_paths["weekly_bin_contract"])
    _atomic_csv(weekly_assignment_audit, output_paths["weekly_assignment_audit"])
    _atomic_csv(phase, output_paths["phase_data"])
    _atomic_csv(weekly_summary, output_paths["weekly_summary"])
    _atomic_csv(phase_summary, output_paths["phase_summary"])
    _write_figure(_build_weekly_overview(weekly_summary), WEEKLY_OVERVIEW_STEM, figures_dir)
    _write_figure(_build_phase_overview(phase_summary), PHASE_OVERVIEW_STEM, figures_dir)
    _write_figure(
        _build_phase_share_figure(
            phase_summary,
            value_column="mean_commit_share_pct",
            median_column="median_commit_share_pct",
            title="Commit share by non-overlapping project phase",
            yaxis_title="Mean team-semester commit share",
            note=(
                "Bars average team-semester shares within each score-trajectory group. "
                "Phases are mutually exclusive and final7_pre_t3 is excluded from t2_to_t3_excluding_final7."
            ),
        ),
        PHASE_COMMIT_SHARE_STEM,
        figures_dir,
    )
    _write_figure(
        _build_phase_share_figure(
            phase_summary,
            value_column="mean_clean_churn_share_pct",
            median_column="median_clean_churn_share_pct",
            title="Clean changed-line share by non-overlapping project phase",
            yaxis_title="Mean team-semester clean changed-line share",
            note=(
                "Bars average team-semester clean-churn shares within each score-trajectory group. "
                f"Clean churn uses the {CURRENT_POLICY_VERSION} clean-path policy."
            ),
        ),
        PHASE_CLEAN_CHURN_SHARE_STEM,
        figures_dir,
    )

    figure_paths = {
        WEEKLY_OVERVIEW_STEM: {extension: figures_dir / f"{WEEKLY_OVERVIEW_STEM}.{extension}" for extension in ("png", "svg", "pdf")},
        PHASE_OVERVIEW_STEM: {extension: figures_dir / f"{PHASE_OVERVIEW_STEM}.{extension}" for extension in ("png", "svg", "pdf")},
        PHASE_COMMIT_SHARE_STEM: {extension: figures_dir / f"{PHASE_COMMIT_SHARE_STEM}.{extension}" for extension in ("png", "svg", "pdf")},
        PHASE_CLEAN_CHURN_SHARE_STEM: {extension: figures_dir / f"{PHASE_CLEAN_CHURN_SHARE_STEM}.{extension}" for extension in ("png", "svg", "pdf")},
    }
    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_id": STEM,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {name: str(path.relative_to(repo_root)) for name, path in paths.items()},
        "input_sha256": {name: compute_sha256(path) for name, path in paths.items()},
        "outputs": {
            name: str(path.relative_to(repo_root)) for name, path in output_paths.items() if name != "metadata"
        },
        "output_sha256": {
            name: compute_sha256(path) for name, path in output_paths.items() if name != "metadata"
        },
        "figure_outputs": {
            stem: {extension: str(path.relative_to(repo_root)) for extension, path in extension_paths.items()}
            for stem, extension_paths in figure_paths.items()
        },
        "figure_output_sha256": {
            stem: {extension: compute_sha256(path) for extension, path in extension_paths.items()}
            for stem, extension_paths in figure_paths.items()
        },
        "coverage": {
            "team_semesters": int(anchors[TEAM_KEY].drop_duplicates().shape[0]),
            "weekly_rows": int(len(weekly)),
            "weekly_bin_contract_rows": int(len(weekly_bin_contract)),
            "weekly_assignment_audit_rows": int(len(weekly_assignment_audit)),
            "phase_rows": int(len(phase)),
            "weekly_empty_commit_bin_rows": int(weekly["commit_n"].eq(0).sum()),
            "weekly_empty_clean_churn_bin_rows": int(weekly["clean_churn"].eq(0).sum()),
            "weekly_fully_empty_bin_rows": int(weekly["commit_n"].eq(0).mul(weekly["clean_churn"].eq(0)).sum()),
            "phase_empty_rows": int(phase["commit_n"].eq(0).sum()),
        },
        "weekly_bin_contract": {
            "bin_labels": WEEK_BIN_LABELS,
            "policy": (
                "Non-overlapping bins relative to team-specific T3 anchors. "
                "week_-12 covers [-91,-84), week_-1 covers [-14,-7), and final_7_days covers [-7,0)."
            ),
            "event_assignment": "Each pre-T3 event inside the covered 91-day weekly window belongs to exactly one bin.",
            "empty_bins": "Retained as zero rows for every team-semester/bin combination.",
            "audit_output": str(output_paths["weekly_assignment_audit"].relative_to(repo_root)),
            "assignment_audit_status": (
                "pass" if weekly_assignment_audit["assignment_status"].eq("pass").all() else "fail"
            ),
            "rolling_window_used": False,
        },
        "phase_contract": {
            "phase_labels": PHASE_LABELS,
            "policy": (
                "pre_t1 uses the observed pre-T3 repository start; t1_to_t2 is [T1,T2); "
                "t2_to_t3_excluding_final7 is [T2,T3-7d); final7_pre_t3 is [T3-7d,T3)."
            ),
            "event_assignment": "Each observed pre-T3 event belongs to exactly one phase.",
        },
        "phase_visualization_contract": {
            PHASE_COMMIT_SHARE_STEM: {
                "source": str(output_paths["phase_summary"].relative_to(repo_root)),
                "x": "phase",
                "y": "mean_commit_share_pct",
                "color": "score_trajectory_group",
                "unit": "mean team-semester share within score-trajectory group",
            },
            PHASE_CLEAN_CHURN_SHARE_STEM: {
                "source": str(output_paths["phase_summary"].relative_to(repo_root)),
                "x": "phase",
                "y": "mean_clean_churn_share_pct",
                "color": "score_trajectory_group",
                "unit": "mean team-semester share within score-trajectory group",
            },
        },
        "metrics": {
            "commit_n": "Distinct commits from git_commits.parquet.",
            "clean_churn": f"lines_added + lines_deleted over clean paths using {CURRENT_POLICY_VERSION}.",
            "active_day_n": "Distinct UTC commit days in the bin or phase.",
            "active_author_n": "Distinct local commit authors in the bin or phase.",
        },
        "inference": "descriptive_nonoverlapping_activity_bins_not_causal",
        "limitations": [
            "Repository activity does not observe off-repository work.",
            "pre_t1 has variable duration because it starts at each team-semester's first observed pre-T3 repository event.",
            "Weekly bins cover the final 91 days before T3 and intentionally exclude earlier activity.",
            "Clean churn depends on the current clean-path artifact policy.",
        ],
    }
    _atomic_json(metadata, output_paths["metadata"])
    return {
        "status": "generated",
        "weekly_data": str(output_paths["weekly_data"]),
        "weekly_bin_contract": str(output_paths["weekly_bin_contract"]),
        "weekly_assignment_audit": str(output_paths["weekly_assignment_audit"]),
        "phase_data": str(output_paths["phase_data"]),
        "metadata": str(output_paths["metadata"]),
        "coverage": metadata["coverage"],
    }


def main() -> None:
    print(json.dumps(generate(), indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
