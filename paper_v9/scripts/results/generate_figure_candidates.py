"""Generate approved-scope visualization candidates for the Paper V9 workshop."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir, resolve_paper_v9_dir


def _write_figure(figure, stem: str, figures_dir: Path, metrics_dir: Path) -> None:
    figure.write_html(metrics_dir / f"{stem}.html", include_plotlyjs="cdn")
    for extension in ("pdf", "svg", "png"):
        figure.write_image(figures_dir / f"{stem}.{extension}", scale=2 if extension == "png" else 1)


def generate() -> dict[str, object]:
    root = resolve_paper_v9_dir()
    metrics = resolve_metrics_dir()
    figures = resolve_figures_dir()
    m1 = pd.read_csv(metrics / "m1_rq1_perception_panel_long.csv")
    m2 = pd.read_csv(metrics / "m2_role_perception_distributions.csv")
    m3 = pd.read_csv(metrics / "m3_activity_rolling_7day_pooled.csv")
    m4 = pd.read_csv(metrics / "m4_rolling_7day_trajectory_pooled.csv")
    m5 = pd.read_csv(metrics / "m5_marker_density.csv")
    m6 = pd.read_csv(metrics / "m6a_structural_planning.csv", dtype={"Semestre": str})
    m8 = pd.read_csv(metrics / "m8_rework_magnitude.csv", dtype={"Semestre": str})
    m9 = pd.read_csv(metrics / "m9_leave_one_out_intervals.csv", dtype={"removed_Semestre": str})

    candidates: dict[str, object] = {}

    rq1_data = m1.groupby(["Semestre", "temporal_marker", "perception_family"], as_index=False)["mean"].mean()
    rq1_data.to_csv(figures / "candidate_rq1_perception_panel_data.csv", index=False)
    rq1_figure = px.line(rq1_data, x="temporal_marker", y="mean", color="perception_family", facet_col="Semestre", markers=True, title="RQ1 candidate: separated perception families")
    _write_figure(rq1_figure, "candidate_rq1_perception_panel", figures, metrics)
    candidates["rq1"] = {"data": "candidate_rq1_perception_panel_data.csv", "figure": "candidate_rq1_perception_panel"}

    rq2_parts = [
        m3.rename(columns={"window_end_day": "temporal_position", "total_commit_n": "value"})[["temporal_position", "value"]].assign(metric="M3 pooled activity", unit="commit events"),
        m4.rename(columns={"window_end_day": "temporal_position", "total_clean_churn_7d": "value"})[["temporal_position", "value"]].assign(metric="M4 pooled clean churn", unit="clean churn lines"),
    ]
    m5_part = m5.assign(temporal_position=m5["temporal_marker"].map({"T1": -1, "T2": 0, "T3": 1}), value=m5["friction_marker_density_per_1k_tokens"], metric="M5 transcript evidence density", unit="candidate markers per 1,000 tokens")[["temporal_position", "value", "metric", "unit"]]
    rq2_data = pd.concat(rq2_parts + [m5_part], ignore_index=True)
    rq2_data.to_csv(figures / "candidate_rq2_temporal_dynamics_data.csv", index=False)
    rq2_figure = px.line(rq2_data, x="temporal_position", y="value", color="metric", markers=True, facet_row="unit", title="RQ2 candidate: temporal dynamics with explicit units")
    _write_figure(rq2_figure, "candidate_rq2_temporal_dynamics", figures, metrics)
    candidates["rq2"] = {"data": "candidate_rq2_temporal_dynamics_data.csv", "figure": "candidate_rq2_temporal_dynamics"}

    profile = m6.merge(m8[["ID_Equipe", "Semestre", "clean_rework_churn_t3", "clean_rework_ratio_t3", "baseline_eligible_for_rework_t3"]], on=["ID_Equipe", "Semestre"], validate="one_to_one")
    profile.to_csv(figures / "candidate_rq3_planning_rework_profile_data.csv", index=False)
    rq3_figure = px.scatter(profile, x="planning_scope_log1p_t1", y="clean_rework_churn_t3", color="Semestre", symbol="baseline_eligible_for_rework_t3", hover_name="ID_Equipe", title="RQ3 candidate: structural planning scope and clean rework")
    _write_figure(rq3_figure, "candidate_rq3_planning_rework_profile", figures, metrics)
    candidates["rq3_profile"] = {"data": "candidate_rq3_planning_rework_profile_data.csv", "figure": "candidate_rq3_planning_rework_profile"}

    loo_data = m9.copy()
    loo_data.to_csv(figures / "candidate_rq3_associations_leave_one_out_data.csv", index=False)
    loo_summary = loo_data.groupby(["analysis_id", "predictor", "outcome"], as_index=False).agg(rho_min=("spearman_rho", "min"), rho_max=("spearman_rho", "max"))
    loo_figure = px.scatter(loo_summary, x="rho_min", y="rho_max", color="analysis_id", hover_data=["predictor", "outcome"], title="RQ3 candidate: leave-one-out association ranges")
    _write_figure(loo_figure, "candidate_rq3_associations_leave_one_out", figures, metrics)
    candidates["rq3_loo"] = {"data": "candidate_rq3_associations_leave_one_out_data.csv", "figure": "candidate_rq3_associations_leave_one_out"}

    return {"status": "generated", "candidates": candidates}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Paper V9 figure candidates")
    parser.parse_args()
    print(generate())


if __name__ == "__main__":
    main()
