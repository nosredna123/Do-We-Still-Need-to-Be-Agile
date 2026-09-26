"""Generate article-ready RQ1 figures from official V9 M1/M2 artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir


FAMILY_LABELS = {
    "ai_benefit": "AI benefit",
    "autonomy_tool_dependency": "Autonomy/tool balance",
    "ai_career_impact_5y": "Five-year career impact",
    "career_expectation": "Career expectation",
    "project_challenges": "Project challenges",
    "project_feeling": "Project feeling",
}


def _write_figure(figure: go.Figure, stem: str, figures_dir: Path) -> None:
    for extension in ("pdf", "svg", "png"):
        figure.write_image(
            figures_dir / f"{stem}.{extension}",
            scale=2 if extension == "png" else 1,
        )


def _m1_trajectory(metrics_dir: Path, figures_dir: Path) -> None:
    data = pd.read_csv(metrics_dir / "m1_rq1_perception_panel_long.csv")
    data["Semestre"] = data["Semestre"].astype(str)
    data["family_label"] = data["perception_family"].map(FAMILY_LABELS)
    data["checkpoint_order"] = data["temporal_marker"].map({"T1": 1, "T2": 2, "T3": 3})
    data = data.sort_values(["Semestre", "family_label", "checkpoint_order"])

    figure = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        subplot_titles=("2025.2", "2026.1"),
        horizontal_spacing=0.08,
    )
    colors = px.colors.qualitative.Set2
    for index, (family, family_data) in enumerate(data.groupby("family_label", sort=False)):
        for semester, semester_data in family_data.groupby("Semestre", sort=False):
            figure.add_trace(
                go.Scatter(
                    x=semester_data["temporal_marker"],
                    y=semester_data["mean"],
                    error_y={"type": "data", "array": semester_data["std"], "visible": True},
                    mode="lines+markers",
                    name=family,
                    legendgroup=family,
                    legendgrouptitle_text="Perception family" if index == 0 and semester == "2025.2" else None,
                    showlegend=semester == "2025.2",
                    line={"color": colors[index % len(colors)]},
                    marker={"size": 6},
                    hovertemplate=(
                        f"{family}<br>Semester={semester}<br>Checkpoint=%{{x}}"
                        "<br>Mean=%{y:.2f}<extra></extra>"
                    ),
                ),
                row=1,
                col=1 if semester == "2025.2" else 2,
            )
    figure.update_layout(
        template="simple_white",
        width=900,
        height=440,
        margin={"l": 55, "r": 25, "t": 35, "b": 40},
        font={"size": 14},
        legend_font={"size": 13},
    )
    figure.update_xaxes(categoryorder="array", categoryarray=["T1", "T2", "T3"], title="Checkpoint", title_font={"size": 15}, tickfont={"size": 13})
    figure.update_yaxes(title="Mean score (family scale)", range=[0, 5], row=1, col=1, title_font={"size": 15}, tickfont={"size": 13})
    figure.update_yaxes(showticklabels=False, range=[0, 5], row=1, col=2, tickfont={"size": 13})
    _write_figure(figure, "rq1_m1_perception_with_sd", figures_dir)
    data.to_csv(figures_dir / "rq1_m1_perception_with_sd_data.csv", index=False)


def _m2_heatmap(metrics_dir: Path, figures_dir: Path) -> None:
    data = pd.read_csv(metrics_dir / "m2_role_perception_by_team_semester.csv")
    data["Semestre"] = data["Semestre"].astype(str)
    data["role"] = pd.Categorical(
        data["role"],
        categories=["Project Manager", "Product Manager", "QA", "Backend", "Scrum Master", "Frontend"],
        ordered=True,
    )
    data["checkpoint_label"] = data["Semestre"].astype(str) + " / " + data["temporal_marker"]
    data["checkpoint_label"] = pd.Categorical(
        data["checkpoint_label"],
        categories=[f"{semester} / {checkpoint}" for semester in ["2025.2", "2026.1"] for checkpoint in ["T1", "T2", "T3"]],
        ordered=True,
    )
    matrix = data.pivot(index="role", columns="checkpoint_label", values="mean")
    figure = px.imshow(
        matrix,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="YlOrRd",
        zmin=1,
        zmax=5,
        labels={"color": "Mean agreement", "value": "Mean agreement", "x": "Cohort / checkpoint", "y": "Role"},
        title="M2 perceived role disruption agreement",
    )
    figure.update_layout(
        template="simple_white",
        width=900,
        height=430,
        margin={"l": 110, "r": 25, "t": 55, "b": 70},
        coloraxis_colorbar={"title": "Mean agreement", "ticks": "outside"},
        font={"size": 14},
        title_font={"size": 18},
    )
    figure.update_xaxes(title_font={"size": 15}, tickfont={"size": 12})
    figure.update_yaxes(title_font={"size": 15}, tickfont={"size": 13})
    figure.update_traces(textfont={"size": 13})
    _write_figure(figure, "rq1_m2_role_perception_heatmap", figures_dir)
    data.to_csv(figures_dir / "rq1_m2_role_perception_heatmap_data.csv", index=False)


def main() -> None:
    _m1_trajectory(resolve_metrics_dir(), resolve_figures_dir())
    _m2_heatmap(resolve_metrics_dir(), resolve_figures_dir())
    print("Generated RQ1 M1/M2 figures and derived data")


if __name__ == "__main__":
    main()
