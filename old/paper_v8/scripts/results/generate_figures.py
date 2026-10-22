"""Generate the two Results-section figures from the M1--M9 CSVs.

Uses `plotly` + `kaleido`, consistent with this repository's existing figure
convention in `08_cross_evidence_engine.py` (no new plotting dependency is
introduced; both packages are already pinned in requirements.txt).

Figures
-------
1. rq2_activity_density_vs_friction: repository activity density (M4,
   log-scale line) against qualitative coordination friction (M5, secondary
   axis), across T1-T3, pooled across both cohorts.
2. rq3_rework_by_planning_group: T3 rework-churn volume (M8) for teams
    with omitted, low, and high T1 planning evidence, log-scale strip/box plot.

Source artifacts (read-only)
-----------------------------
    paper_v8/data/m4_repo_activity_density.csv
    paper_v8/data/m5_coordination_friction_trajectory.csv
    paper_v8/data/m6_t1_planning_quality.csv
    paper_v8/data/m8_rework_severity_ratio.csv

Output
------
    paper_v8/figures/rq2_activity_density_vs_friction.png
    paper_v8/figures/rq3_rework_by_planning_group.png
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from _paths import DATA_DIR, ensure_figures_dir

FIGURE_WIDTH = 900
FIGURE_HEIGHT = 550
CUT_ORDER = ["T1", "T2", "T3"]


def build_rq2_figure() -> go.Figure:
    """Repository activity density (log scale) vs. coordination friction, T1-T3."""
    m4 = pd.read_csv(DATA_DIR / "m4_repo_activity_density.csv")
    m5 = pd.read_csv(DATA_DIR / "m5_coordination_friction_trajectory.csv")

    cc_total = (
        m4[(m4["Semestre"] == "all") & (m4["metric"] == "cc_total")]
        .set_index("cut")["mean"]
        .reindex(CUT_ORDER)
    )
    friction = m5.set_index("temporal_marker")["coordination_friction"].reindex(CUT_ORDER)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=CUT_ORDER,
            y=cc_total.values,
            name="Repository activity density (mean total churn, log scale)",
            mode="lines+markers",
            yaxis="y1",
            line={"color": "#1f77b4"},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=CUT_ORDER,
            y=friction.values,
            name="Coordination-friction score (1-10)",
            mode="lines+markers",
            yaxis="y2",
            line={"color": "#d62728", "dash": "dash"},
        )
    )
    figure.update_layout(
        title="RQ2: Repository activity spikes late; coordination friction is flat from the start",
        xaxis={"title": "Temporal checkpoint"},
        yaxis={"title": "Mean total churn (lines, log scale)", "type": "log"},
        yaxis2={"title": "Coordination friction (1-10)", "overlaying": "y", "side": "right", "range": [0, 10]},
        legend={"orientation": "h", "y": -0.2},
        width=FIGURE_WIDTH,
        height=FIGURE_HEIGHT,
        template="plotly_white",
    )
    return figure


def build_rq3_figure() -> go.Figure:
    """T3 rework churn for omitted, low, and high T1 planning evidence."""
    m6 = pd.read_csv(DATA_DIR / "m6_t1_planning_quality.csv")
    m8 = pd.read_csv(DATA_DIR / "m8_rework_severity_ratio.csv")

    joined = m8.merge(m6, on=["ID_Equipe", "Semestre"], how="left")
    scored = joined.dropna(subset=["t1_planning_score"]).copy()
    median_score = scored["t1_planning_score"].median()
    scored["planning_group"] = scored["t1_planning_score"].apply(
        lambda value: "Low planning quality (<= median)" if value <= median_score else "High planning quality (> median)"
    )
    omitted = joined[joined["t1_planning_score"].isna()].copy()
    omitted["planning_group"] = "No T1 repository activity"
    plotted = pd.concat([omitted, scored], ignore_index=True)

    figure = go.Figure()
    for group_name, color in (
        ("No T1 repository activity", "#7f7f7f"),
        ("Low planning quality (<= median)", "#d62728"),
        ("High planning quality (> median)", "#2ca02c"),
    ):
        group = plotted[plotted["planning_group"] == group_name]
        figure.add_trace(
            go.Box(
                y=group["rework_churn_t3"] + 1,
                name=group_name,
                boxpoints="all",
                jitter=0.4,
                marker={"color": color},
            )
        )
    figure.update_layout(
        title="RQ3: T3 rework varies across T1 planning-evidence groups",
        yaxis={"title": "T3 rework churn + 1 (lines, log scale)", "type": "log"},
        showlegend=False,
        width=FIGURE_WIDTH,
        height=FIGURE_HEIGHT,
        template="plotly_white",
    )
    return figure


def main() -> None:
    figures_dir = ensure_figures_dir()
    for name, builder in (
        ("rq2_activity_density_vs_friction", build_rq2_figure),
        ("rq3_rework_by_planning_group", build_rq3_figure),
    ):
        figure = builder()
        output_path = figures_dir / f"{name}.png"
        figure.write_image(output_path, scale=2)
        print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
