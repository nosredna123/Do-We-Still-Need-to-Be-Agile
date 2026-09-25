"""Generate planning-scope versus final-7-day concentration quadrant plots."""

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

from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir
from paper_v9.scripts.common.provenance import compute_sha256
from paper_v9.scripts.results.generate_score_trajectory_base import STEM as BASE_STEM

CONTRACT_VERSION = "rq2-planning-concentration-quadrants-v1"
COMMIT_STEM = "rq2_planning_vs_final7_commit_concentration"
CHURN_STEM = "rq2_planning_vs_final7_clean_churn_concentration"
SUMMARY_STEM = "rq2_planning_concentration_quadrant_summary"
METADATA_STEM = "rq2_planning_concentration_quadrants"
TEAM_KEY = ["ID_Equipe", "Semestre"]
SEMESTER_SYMBOLS = {
    "2025.2": "circle",
    "2026.1": "diamond",
}
QUADRANT_INTERPRETATIONS = {
    "high_repository_visible_planning__lower_final7_concentration": (
        "High planning scope with distributed activity"
    ),
    "high_repository_visible_planning__higher_final7_concentration": (
        "High planning scope with late concentration"
    ),
    "lower_repository_visible_planning__lower_final7_concentration": (
        "Lower planning scope with distributed or low final concentration"
    ),
    "lower_repository_visible_planning__higher_final7_concentration": (
        "Lower planning scope with late concentration"
    ),
}
REQUIRED_BASE_COLUMNS = [
    *TEAM_KEY,
    "planning_scope_log1p_t1",
    "planning_scope_tier",
    "evaluator_score_t3",
    "delta_score_t3_minus_t1",
    "final7_commit_share_pct",
    "final7_clean_churn_share_pct",
]
REWORK_COLUMNS = [*TEAM_KEY, "clean_rework_churn_t3"]


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


def _load_base(figures_dir: Path, metrics_dir: Path) -> tuple[pd.DataFrame, Path, Path | None]:
    base_path = figures_dir / f"{BASE_STEM}_data.csv"
    base = pd.read_csv(base_path, dtype={"Semestre": str})
    _require_columns(base, REQUIRED_BASE_COLUMNS, base_path)

    rework_path = metrics_dir / "m8_rework_magnitude.csv"
    if rework_path.is_file():
        rework = pd.read_csv(rework_path, dtype={"Semestre": str})
        _require_columns(rework, REWORK_COLUMNS, rework_path)
        base = base.merge(rework[REWORK_COLUMNS], on=TEAM_KEY, how="left", validate="one_to_one")
    else:
        base["clean_rework_churn_t3"] = pd.NA
        rework_path = None
    return base, base_path, rework_path


def _prepare_metric_data(base: pd.DataFrame, *, share_column: str, metric_label: str) -> pd.DataFrame:
    data = base[
        [
            *TEAM_KEY,
            "planning_scope_log1p_t1",
            "planning_scope_tier",
            "evaluator_score_t3",
            "delta_score_t3_minus_t1",
            "clean_rework_churn_t3",
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

    final7_median = float(data["final7_share_pct"].median())
    data["final7_concentration_tier"] = "lower_final7_concentration"
    data.loc[data["final7_share_pct"].ge(final7_median), "final7_concentration_tier"] = (
        "higher_final7_concentration"
    )
    data["planning_concentration_quadrant"] = (
        data["planning_scope_tier"] + "__" + data["final7_concentration_tier"]
    )
    data["abs_delta_score_t3_minus_t1"] = data["delta_score_t3_minus_t1"].abs()
    max_abs_delta = float(data["abs_delta_score_t3_minus_t1"].max())
    if max_abs_delta > 0:
        data["marker_size"] = 11 + 20 * data["abs_delta_score_t3_minus_t1"] / max_abs_delta
    else:
        data["marker_size"] = 14
    return data.sort_values(TEAM_KEY).reset_index(drop=True)


def _build_quadrant_plot(data: pd.DataFrame, *, title: str, yaxis_title: str) -> go.Figure:
    planning_median = float(data["planning_scope_log1p_t1"].median())
    final7_median = float(data["final7_share_pct"].median())
    figure = go.Figure()
    for semester in sorted(data["Semestre"].unique()):
        subset = data.loc[data["Semestre"].eq(semester)]
        figure.add_trace(
            go.Scatter(
                x=subset["planning_scope_log1p_t1"],
                y=subset["final7_share_pct"],
                mode="markers",
                marker={
                    "color": subset["evaluator_score_t3"],
                    "colorscale": "Viridis",
                    "cmin": float(data["evaluator_score_t3"].min()),
                    "cmax": float(data["evaluator_score_t3"].max()),
                    "coloraxis": "coloraxis",
                    "symbol": SEMESTER_SYMBOLS.get(semester, "circle"),
                    "size": subset["marker_size"],
                    "sizemode": "diameter",
                    "line": {"color": "white", "width": 1.4},
                },
                name=semester,
                customdata=subset[
                    [
                        "ID_Equipe",
                        "Semestre",
                        "evaluator_score_t3",
                        "delta_score_t3_minus_t1",
                        "planning_scope_tier",
                        "planning_concentration_quadrant",
                        "clean_rework_churn_t3",
                    ]
                ],
                hovertemplate=(
                    "Team=%{customdata[0]}<br>"
                    "Semester=%{customdata[1]}<br>"
                    "Planning scope log1p=%{x:.3f}<br>"
                    "Final-7 share=%{y:.1f}%<br>"
                    "T3 evaluator score=%{customdata[2]:.3f}<br>"
                    "T3−T1 score delta=%{customdata[3]:.3f}<br>"
                    "Planning tier=%{customdata[4]}<br>"
                    "Quadrant=%{customdata[5]}<br>"
                    "Clean rework churn T3=%{customdata[6]:,.0f}"
                    "<extra></extra>"
                ),
            )
        )

    figure.add_vline(
        x=planning_median,
        line_dash="dash",
        line_color="#52525b",
        annotation_text=f"Median planning scope: {planning_median:.2f}",
        annotation_position="top left",
    )
    figure.add_hline(
        y=final7_median,
        line_dash="dot",
        line_color="#71717a",
        annotation_text=f"Median final-7 share: {final7_median:.1f}%",
        annotation_position="bottom right",
    )
    figure.update_layout(
        template="simple_white",
        width=1100,
        height=680,
        margin={"l": 85, "r": 35, "t": 95, "b": 130},
        title={"text": title, "font": {"size": 22}},
        font={"size": 14, "family": "DejaVu Sans, Arial, sans-serif"},
        legend={
            "title": "Semester",
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        coloraxis={
            "colorscale": "Viridis",
            "colorbar": {"title": "T3 evaluator<br>score"},
        },
        xaxis={
            "title": "Repository-visible T1 planning scope (log1p changed lines)",
            "gridcolor": "#e5e7eb",
            "zeroline": False,
        },
        yaxis={
            "title": yaxis_title,
            "ticksuffix": "%",
            "range": [-4, 104],
            "gridcolor": "#e5e7eb",
            "zeroline": False,
        },
        annotations=[
            *figure.layout.annotations,
            {
                "text": (
                    "Points are team-semesters. Color encodes T3 evaluator score; "
                    "marker area encodes absolute T3−T1 score delta.<br>"
                    "Planning is repository-visible T1 scope, not semantic planning quality."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.2,
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#52525b"},
            },
        ],
    )
    return figure


def _quadrant_summary(data_by_metric: dict[str, pd.DataFrame]) -> pd.DataFrame:
    quadrant_order = list(QUADRANT_INTERPRETATIONS)
    rows: list[dict[str, Any]] = []
    for metric, data in data_by_metric.items():
        total_n = int(data[TEAM_KEY].drop_duplicates().shape[0])
        data = data.copy()
        data["team_semester_label"] = data["ID_Equipe"].astype(str) + "/" + data["Semestre"].astype(str)
        for quadrant in quadrant_order:
            group = data.loc[data["planning_concentration_quadrant"].eq(quadrant)]
            rows.append(
                {
                    "activity_metric": metric,
                    "quadrant": quadrant,
                    "team_semester_n": int(len(group)),
                    "team_semester_denominator": total_n,
                    "mean_t3_score": group["evaluator_score_t3"].mean(),
                    "median_t3_score": group["evaluator_score_t3"].median(),
                    "mean_delta_score": group["delta_score_t3_minus_t1"].mean(),
                    "median_delta_score": group["delta_score_t3_minus_t1"].median(),
                    "mean_clean_rework_churn_t3": group["clean_rework_churn_t3"].mean(),
                    "small_n_flag": int(len(group)) <= 1,
                    "interpretation": QUADRANT_INTERPRETATIONS[quadrant],
                    "team_semesters": ";".join(group["team_semester_label"].astype(str)),
                }
            )
    return pd.DataFrame(rows)


def generate() -> dict[str, Any]:
    figures_dir = resolve_figures_dir()
    metrics_dir = resolve_metrics_dir()
    base, base_path, rework_path = _load_base(figures_dir, metrics_dir)

    metric_specs = {
        COMMIT_STEM: {
            "share_column": "final7_commit_share_pct",
            "metric_label": "commits",
            "title": "Repository-visible planning scope versus final-week commit concentration",
            "yaxis_title": "Final-7 commits (% of project commits)",
        },
        CHURN_STEM: {
            "share_column": "final7_clean_churn_share_pct",
            "metric_label": "clean_source_or_test_changed_lines",
            "title": "Repository-visible planning scope versus final-week clean changed-line concentration",
            "yaxis_title": "Final-7 clean churn (% of project clean churn)",
        },
    }

    outputs: dict[str, Any] = {}
    data_by_metric: dict[str, pd.DataFrame] = {}
    for stem, spec in metric_specs.items():
        data = _prepare_metric_data(base, share_column=spec["share_column"], metric_label=spec["metric_label"])
        data_by_metric[spec["metric_label"]] = data
        data_path = figures_dir / f"{stem}_data.csv"
        _atomic_csv(data, data_path)
        figure = _build_quadrant_plot(data, title=spec["title"], yaxis_title=spec["yaxis_title"])
        _write_figure(figure, stem, figures_dir)
        outputs[stem] = {
            "activity_metric": spec["metric_label"],
            "data_path": str(data_path),
            "data_sha256": compute_sha256(data_path),
            "team_semesters": int(data[TEAM_KEY].drop_duplicates().shape[0]),
            "planning_scope_log1p_t1_median": float(data["planning_scope_log1p_t1"].median()),
            "final7_share_pct_median": float(data["final7_share_pct"].median()),
            "quadrant_counts": data["planning_concentration_quadrant"].value_counts().sort_index().to_dict(),
            "artifacts": [str(figures_dir / f"{stem}.{extension}") for extension in ("pdf", "svg", "png")]
            + [str(data_path)],
        }

    summary = _quadrant_summary(data_by_metric)
    summary_path = figures_dir / f"{SUMMARY_STEM}.csv"
    _atomic_csv(summary, summary_path)

    metadata_path = figures_dir / f"{METADATA_STEM}.metadata.json"
    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_family": "planning_concentration_quadrants",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "base_path": str(base_path.relative_to(figures_dir.parent.parent)),
        "base_sha256": compute_sha256(base_path),
        "rework_path": str(rework_path.relative_to(figures_dir.parent.parent)) if rework_path else None,
        "rework_sha256": compute_sha256(rework_path) if rework_path else None,
        "summary_path": str(summary_path.relative_to(figures_dir.parent.parent)),
        "summary_sha256": compute_sha256(summary_path),
        "metadata_path": str(metadata_path.relative_to(figures_dir.parent.parent)),
        "quadrant_definition": {
            "planning_cut": "planning_scope_tier from phase 0, based on repository-visible T1 planning scope median",
            "final7_cut": "metric-specific median final7_share_pct",
            "interpretations": QUADRANT_INTERPRETATIONS,
        },
        "outputs": outputs,
        "unit_of_analysis": "team_semester",
        "inference": "descriptive_non_causal",
        "limitations": [
            "Planning scope is repository-visible structural evidence, not semantic planning quality.",
            "Final-seven-day concentration is a temporal activity proxy, not causal evidence.",
            "Quadrants are descriptive small-n bins and are not statistical significance tests.",
            "M8 clean rework is included only as a provenance-based churn proxy when summarized.",
        ],
    }
    _atomic_json(metadata, metadata_path)

    return {
        "status": "generated",
        "metadata_path": str(metadata_path),
        "summary_path": str(summary_path),
        "outputs": outputs,
    }


def main() -> None:
    result = generate()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
