"""Generate article-ready RQ2 figures from official V9 M3-M5 artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir


def _write_figure(figure: go.Figure, stem: str, figures_dir: Path) -> None:
    for extension in ("pdf", "svg", "png"):
        figure.write_image(
            figures_dir / f"{stem}.{extension}",
            scale=2 if extension == "png" else 1,
        )


def generate() -> None:
    metrics = resolve_metrics_dir()
    figures = resolve_figures_dir()
    m3 = pd.read_csv(metrics / "m3_activity_rolling_7day_pooled.csv")
    m4 = pd.read_csv(metrics / "m4_churn_magnitude_pooled.csv")
    m5 = pd.read_csv(metrics / "m5_marker_density.csv")

    m3.to_csv(figures / "rq2_m3_activity_pooled_data.csv", index=False)
    m4.to_csv(figures / "rq2_m4_m5_checkpoint_data.csv", index=False)
    m5.to_csv(figures / "rq2_m5_density_data.csv", index=False)

    m3_figure = go.Figure(
        go.Scatter(
            x=m3["window_end_day"],
            y=m3["total_commit_n"],
            mode="lines+markers",
            line={"color": "#4f6bed", "width": 3},
            marker={"size": 7},
            hovertemplate="Day %{x} relative to T3<br>Commits=%{y}<extra></extra>",
        )
    )
    m3_figure.add_vline(x=0, line_dash="dash", line_color="#333333")
    m3_figure.add_annotation(x=1, y=302, text="Peak: 302", showarrow=True, arrowhead=2, ax=55, ay=-32)
    m3_figure.update_layout(
        template="simple_white",
        width=1200,
        height=420,
        margin={"l": 75, "r": 30, "t": 25, "b": 55},
        font={"size": 15},
        xaxis={"title": "Window end relative to T3 anchor (days)", "tickfont": {"size": 14}, "title_font": {"size": 16}},
        yaxis={"title": "Commits across all team-semesters", "tickfont": {"size": 14}, "title_font": {"size": 16}},
    )
    _write_figure(m3_figure, "rq2_m3_activity_pooled", figures)

    m4_figure = go.Figure(
        go.Bar(
            x=m4["temporal_marker"],
            y=m4["total_clean_churn"],
            marker_color="#e76f51",
            hovertemplate="Checkpoint %{x}<br>Clean churn=%{y:,} lines<extra></extra>",
        )
    )
    m4_figure.update_layout(
        template="simple_white",
        title="M4 clean source/test churn",
        yaxis_title="Clean churn (lines)",
    )

    m5_figure = go.Figure(
        go.Scatter(
            x=m5["temporal_marker"],
            y=m5["friction_marker_density_per_1k_tokens"],
            mode="lines+markers",
            line={"color": "#2a9d8f", "width": 3},
            marker={"size": 8},
            hovertemplate="Checkpoint %{x}<br>Markers=%{y:.3f} per 1,000 tokens<extra></extra>",
        )
    )
    m5_figure.update_layout(
        template="simple_white",
        title="M5 lexical marker density",
        yaxis_title="Candidate markers per 1,000 tokens",
    )

    combined = make_subplots(rows=1, cols=2, subplot_titles=("M4 clean churn", "M5 marker density"), horizontal_spacing=0.1)
    for trace in m4_figure.data:
        combined.add_trace(trace, row=1, col=1)
    for trace in m5_figure.data:
        combined.add_trace(trace, row=1, col=2)
    combined.update_layout(
        template="simple_white",
        width=1200,
        height=400,
        margin={"l": 70, "r": 30, "t": 45, "b": 50},
        showlegend=False,
        font={"size": 14},
    )
    combined.update_xaxes(title="Checkpoint", tickfont={"size": 13})
    combined.update_yaxes(title="Clean churn (lines)", tickfont={"size": 13}, row=1, col=1)
    combined.update_yaxes(title="Markers per 1,000 tokens", tickfont={"size": 13}, row=1, col=2)
    _write_figure(combined, "rq2_m4_m5_checkpoint_panels", figures)

    print("Generated RQ2 M3, M4, and M5 figures and derived data")


if __name__ == "__main__":
    generate()
