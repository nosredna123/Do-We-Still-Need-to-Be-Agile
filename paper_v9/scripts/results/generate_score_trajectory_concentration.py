"""Generate score-trajectory versus final-7-day concentration plots."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_figures_dir
from paper_v9.scripts.common.provenance import compute_sha256
from paper_v9.scripts.results.generate_score_trajectory_base import STEM as BASE_STEM

CONTRACT_VERSION = "rq2-score-trajectory-concentration-v1"
COMMIT_STEM = "rq2_score_delta_vs_final7_commit_concentration"
CHURN_STEM = "rq2_score_delta_vs_final7_clean_churn_concentration"
METADATA_STEM = "rq2_score_delta_vs_final7_concentration"
TEAM_KEY = ["ID_Equipe", "Semestre"]
DELTA_THRESHOLD = 0.125
PLANNING_TIER_COLORS = {
    "high_repository_visible_planning": "#2563eb",
    "lower_repository_visible_planning": "#f97316",
}
PLANNING_TIER_LABELS = {
    "high_repository_visible_planning": "High repository-visible planning",
    "lower_repository_visible_planning": "Lower repository-visible planning",
}
SEMESTER_SYMBOLS = {
    "2025.2": "circle",
    "2026.1": "diamond",
}
REQUIRED_BASE_COLUMNS = [
    *TEAM_KEY,
    "evaluator_score_t1",
    "evaluator_score_t3",
    "delta_score_t3_minus_t1",
    "score_trajectory_group",
    "planning_scope_tier",
    "final7_commit_share_pct",
    "final7_clean_churn_share_pct",
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


def _prepare_metric_data(base: pd.DataFrame, *, share_column: str, metric_label: str) -> pd.DataFrame:
    data = base[
        [
            *TEAM_KEY,
            "evaluator_score_t1",
            "evaluator_score_t3",
            "delta_score_t3_minus_t1",
            "score_trajectory_group",
            "planning_scope_tier",
            share_column,
        ]
    ].copy()
    data = data.rename(columns={share_column: "final7_share_pct"})
    data["activity_metric"] = metric_label
    if data[TEAM_KEY].drop_duplicates().shape[0] != 14:
        raise ValueError(f"Expected 14 team-semesters for {metric_label}")
    if not data["final7_share_pct"].between(0, 100).all():
        invalid = data.loc[~data["final7_share_pct"].between(0, 100), [*TEAM_KEY, "final7_share_pct"]]
        raise ValueError(f"final7_share_pct must be in [0, 100] for {metric_label}: {invalid.to_dict('records')}")
    data["final7_concentration_tier"] = "lower_final7_concentration"
    median_share = float(data["final7_share_pct"].median())
    data.loc[data["final7_share_pct"].ge(median_share), "final7_concentration_tier"] = "higher_final7_concentration"
    data["delta_direction"] = "negative_or_stable_delta"
    data.loc[data["delta_score_t3_minus_t1"].gt(DELTA_THRESHOLD), "delta_direction"] = "positive_delta"
    data["quadrant"] = data["final7_concentration_tier"] + "__" + data["delta_direction"]
    return data.sort_values(TEAM_KEY).reset_index(drop=True)


def _quadrant_counts(data: pd.DataFrame) -> list[dict[str, Any]]:
    counts = (
        data.groupby(["quadrant", "planning_scope_tier"], as_index=False)
        .agg(team_semester_n=("ID_Equipe", "size"))
        .sort_values(["quadrant", "planning_scope_tier"])
        .reset_index(drop=True)
    )
    return counts.to_dict("records")


def _build_scatter(data: pd.DataFrame, *, title: str, xaxis_title: str) -> go.Figure:
    median_share = float(data["final7_share_pct"].median())
    figure = go.Figure()
    for planning_tier in PLANNING_TIER_COLORS:
        for semester in sorted(data["Semestre"].unique()):
            subset = data.loc[data["planning_scope_tier"].eq(planning_tier) & data["Semestre"].eq(semester)]
            if subset.empty:
                continue
            figure.add_trace(
                go.Scatter(
                    x=subset["final7_share_pct"],
                    y=subset["delta_score_t3_minus_t1"],
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
                            "evaluator_score_t1",
                            "evaluator_score_t3",
                            "score_trajectory_group",
                            "quadrant",
                        ]
                    ],
                    hovertemplate=(
                        "Team=%{customdata[0]}<br>"
                        "Semester=%{customdata[1]}<br>"
                        "Final-7 share=%{x:.1f}%<br>"
                        "T3−T1 score delta=%{y:.3f}<br>"
                        "Score T1=%{customdata[2]:.3f}<br>"
                        "Score T3=%{customdata[3]:.3f}<br>"
                        "Trajectory=%{customdata[4]}<br>"
                        "Quadrant=%{customdata[5]}"
                        "<extra></extra>"
                    ),
                )
            )

    figure.add_hline(
        y=0,
        line_dash="dash",
        line_color="#3f3f46",
        annotation_text="No evaluator-score gain",
        annotation_position="bottom right",
    )
    figure.add_vline(
        x=median_share,
        line_dash="dot",
        line_color="#71717a",
        annotation_text=f"Median final-7 share: {median_share:.1f}%",
        annotation_position="top left",
    )
    figure.update_layout(
        template="simple_white",
        width=1100,
        height=680,
        margin={"l": 85, "r": 35, "t": 105, "b": 135},
        title={"text": title, "font": {"size": 22}},
        font={"size": 14, "family": "DejaVu Sans, Arial, sans-serif"},
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
            "font": {"size": 12},
        },
        xaxis={
            "title": xaxis_title,
            "range": [-4, 104],
            "ticksuffix": "%",
            "gridcolor": "#e5e7eb",
            "zeroline": False,
        },
        yaxis={
            "title": "Evaluator score delta (T3 − T1)",
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
                    "Quadrants are descriptive and use the final-7 median "
                    f"and delta threshold {DELTA_THRESHOLD:.3f}; team IDs are available in hover."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.22,
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#52525b"},
            },
        ],
    )
    return figure


def generate() -> dict[str, Any]:
    figures_dir = resolve_figures_dir()
    base_path = figures_dir / f"{BASE_STEM}_data.csv"
    metadata_path = figures_dir / f"{METADATA_STEM}.metadata.json"
    base = pd.read_csv(base_path, dtype={"Semestre": str})
    _require_columns(base, REQUIRED_BASE_COLUMNS, base_path)

    metric_specs = {
        COMMIT_STEM: {
            "share_column": "final7_commit_share_pct",
            "metric_label": "commits",
            "title": "Final-week commit concentration versus evaluator-score change",
            "xaxis_title": "Commits in final seven days before T3 (% of project commits)",
        },
        CHURN_STEM: {
            "share_column": "final7_clean_churn_share_pct",
            "metric_label": "clean_source_or_test_changed_lines",
            "title": "Final-week clean changed-line concentration versus evaluator-score change",
            "xaxis_title": "Clean changed lines in final seven days before T3 (% of project clean churn)",
        },
    }

    outputs: dict[str, Any] = {}
    for stem, spec in metric_specs.items():
        data = _prepare_metric_data(base, share_column=spec["share_column"], metric_label=spec["metric_label"])
        data_path = figures_dir / f"{stem}_data.csv"
        _atomic_csv(data, data_path)
        figure = _build_scatter(data, title=spec["title"], xaxis_title=spec["xaxis_title"])
        _write_figure(figure, stem, figures_dir)
        outputs[stem] = {
            "activity_metric": spec["metric_label"],
            "data_path": str(data_path),
            "data_sha256": compute_sha256(data_path),
            "median_final7_share_pct": float(data["final7_share_pct"].median()),
            "team_semesters": int(data[TEAM_KEY].drop_duplicates().shape[0]),
            "quadrant_counts_by_planning_tier": _quadrant_counts(data),
            "artifacts": [str(figures_dir / f"{stem}.{extension}") for extension in ("pdf", "svg", "png")]
            + [str(data_path)],
        }

    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_family": "score_trajectory_concentration",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "base_path": str(base_path.relative_to(figures_dir.parent.parent)),
        "base_sha256": compute_sha256(base_path),
        "metadata_path": str(metadata_path.relative_to(figures_dir.parent.parent)),
        "delta_threshold": DELTA_THRESHOLD,
        "quadrant_definition": {
            "higher_final7_concentration": "final7_share_pct >= metric-specific sample median",
            "positive_delta": f"delta_score_t3_minus_t1 > {DELTA_THRESHOLD}",
            "negative_or_stable_delta": f"delta_score_t3_minus_t1 <= {DELTA_THRESHOLD}",
        },
        "outputs": outputs,
        "unit_of_analysis": "team_semester",
        "inference": "descriptive_non_causal",
        "limitations": [
            "Final-seven-day concentration is a temporal activity proxy, not causal evidence.",
            "Evaluator-score deltas are descriptive and based on an unweighted composite score.",
            "Quadrants are small-n descriptive bins and should be interpreted as pattern-finding aids.",
        ],
    }
    _atomic_json(metadata, metadata_path)

    return {
        "status": "generated",
        "metadata_path": str(metadata_path),
        "outputs": outputs,
    }


def main() -> None:
    result = generate()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
