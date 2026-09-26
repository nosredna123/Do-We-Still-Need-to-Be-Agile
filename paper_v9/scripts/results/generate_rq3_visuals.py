"""Generate article-ready RQ3 figures from official V9 artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir


def _write(figure: go.Figure, stem: str, figures: Path) -> None:
    for extension in ("pdf", "svg", "png"):
        figure.write_image(figures / f"{stem}.{extension}", scale=2 if extension == "png" else 1)


def generate() -> None:
    metrics = resolve_metrics_dir()
    figures = resolve_figures_dir()
    m6 = pd.read_csv(metrics / "m6a_structural_planning.csv", dtype={"Semestre": str})
    m8 = pd.read_csv(metrics / "m8_rework_magnitude.csv", dtype={"Semestre": str})
    loo = pd.read_csv(metrics / "m9_leave_one_out_intervals.csv", dtype={"removed_Semestre": str})

    profile = m6.merge(
        m8[["ID_Equipe", "Semestre", "clean_rework_churn_t3", "baseline_eligible_for_rework_t3"]],
        on=["ID_Equipe", "Semestre"],
        validate="one_to_one",
    )
    profile["cohort"] = profile["Semestre"]
    profile["eligibility_label"] = profile["baseline_eligible_for_rework_t3"].map({True: "Baseline eligible", False: "Baseline not observed"})
    profile.to_csv(figures / "rq3_architecture_rework_profile_data.csv", index=False)

    scatter = px.scatter(
        profile,
        x="planning_scope_log1p_t1",
        y="clean_rework_churn_t3",
        color="cohort",
        symbol="eligibility_label",
        hover_name="ID_Equipe",
        log_y=True,
        labels={
            "planning_scope_log1p_t1": "T1 architectural-artifact scope, log(1 + lines)",
            "clean_rework_churn_t3": "T3 clean-rework magnitude (lines)",
            "cohort": "Cohort",
            "eligibility_label": "Baseline status",
        },
        title="T1 architectural artifacts and T3 clean rework",
        color_discrete_sequence=["#4f6bed", "#e76f51"],
    )
    scatter.update_traces(marker={"size": 11, "line": {"width": 1, "color": "white"}})
    scatter.update_layout(template="simple_white", width=1200, height=560, font={"size": 15}, title_font={"size": 20}, margin={"l": 80, "r": 35, "t": 65, "b": 70})
    _write(scatter, "rq3_architecture_rework_profile", figures)

    presence = m6.groupby("Semestre", as_index=False).agg(
        team_semester_n=("ID_Equipe", "size"),
        architectural_artifact_observed_n=("planning_artifact_present_t1", "sum"),
    )
    presence["no_repository_artifact_observed_n"] = presence["team_semester_n"] - presence["architectural_artifact_observed_n"]
    presence_long = presence.melt(
        id_vars=["Semestre", "team_semester_n"],
        value_vars=["architectural_artifact_observed_n", "no_repository_artifact_observed_n"],
        var_name="evidence_state",
        value_name="team_semester_count",
    )
    presence_long["evidence_state"] = presence_long["evidence_state"].map({
        "architectural_artifact_observed_n": "Artifact observed",
        "no_repository_artifact_observed_n": "No repository artifact observed",
    })
    presence_long.to_csv(figures / "rq3_architectural_artifact_presence_data.csv", index=False)
    presence_long["evidence_state_display"] = presence_long["evidence_state"].map({
        "Artifact observed": "Artifact observed",
        "No repository artifact observed": "No repo artifact",
    })
    presence_figure = px.bar(
        presence_long,
        x="Semestre",
        y="team_semester_count",
        color="evidence_state_display",
        barmode="stack",
        text="team_semester_count",
        labels={"team_semester_count": "Team-semesters", "Semestre": "Cohort", "evidence_state_display": ""},
        color_discrete_map={"Artifact observed": "#4f6bed", "No repo artifact": "#b9c0cc"},
    )
    presence_figure.update_layout(
        template="simple_white",
        width=760,
        height=620,
        font={"size": 18},
        margin={"l": 80, "r": 25, "t": 25, "b": 95},
        legend={
            "orientation": "h",
            "yanchor": "top",
            "y": -0.18,
            "xanchor": "center",
            "x": 0.5,
            "title_text": "",
        },
    )
    presence_figure.update_traces(textposition="inside", textfont={"size": 18})
    _write(presence_figure, "rq3_architectural_artifact_presence", figures)

    associations = loo.groupby(["analysis_id", "predictor", "outcome"], as_index=False).agg(
        rho_min=("spearman_rho", "min"), rho_max=("spearman_rho", "max")
    )
    main = pd.concat([
        pd.read_csv(metrics / "m9_planning_vs_rework_m6a_m8a.csv"),
        pd.read_csv(metrics / "m9_planning_vs_rework_m6a_m8b_eligible_stratum.csv"),
    ], ignore_index=True)
    associations = associations.merge(main[["analysis_id", "predictor", "outcome", "spearman_rho", "n"]], on=["analysis_id", "predictor", "outcome"], how="left")
    associations["label"] = associations["predictor"].map({"pi_file_count_t1": "T1 artifact file count", "planning_scope_log1p_t1": "T1 artifact line scope"}) + " / " + associations["outcome"].map({"clean_rework_churn_t3": "T3 rework magnitude", "clean_rework_ratio_t3": "T3 rework ratio"})
    associations = associations.sort_values("label").reset_index(drop=True)
    associations.to_csv(figures / "rq3_association_sensitivity_data.csv", index=False)
    y = list(range(len(associations)))
    forest = go.Figure()
    for index, row in associations.iterrows():
        forest.add_trace(go.Scatter(x=[row.rho_min, row.rho_max], y=[index, index], mode="lines", line={"color": "#4f6bed", "width": 5}, showlegend=False, hoverinfo="skip"))
    forest.add_trace(go.Scatter(x=associations["spearman_rho"], y=y, mode="markers", marker={"size": 10, "color": "#e76f51"}, text=associations["label"], hovertemplate="%{text}<br>rho=%{x:.3f}<extra></extra>", name="Full analysis"))
    forest.add_vline(x=0, line_dash="dash", line_color="#555555")
    forest.update_layout(template="simple_white", width=1200, height=520, font={"size": 14}, title={"text": "RQ3 association sensitivity", "font": {"size": 20}}, margin={"l": 280, "r": 35, "t": 65, "b": 65}, xaxis={"title": "Spearman rho; line shows leave-one-out range", "range": [-0.55, 0.55], "title_font": {"size": 15}}, yaxis={"tickmode": "array", "tickvals": y, "ticktext": associations["label"], "autorange": "reversed", "title": ""})
    _write(forest, "rq3_association_sensitivity", figures)

    print("Generated RQ3 figures and derived data")


if __name__ == "__main__":
    generate()
