"""Compute the headline numbers cited in the Results section (sec:results).

This script performs no new metric computation; it only derives simple,
transparent summary statistics (deltas, fold-changes, pooled means, ranked
extremes) directly from the M1--M9 CSVs already produced by
`paper_v8/scripts/metrics/`. Every number quoted in the Results section text
must trace back to a value in the JSON this script writes, so the section is
independently auditable.

Source artifacts (read-only)
-----------------------------
    paper_v8/data/m1_ai_dependency_trajectory.csv
    paper_v8/data/m2_role_disruption_risk.csv
    paper_v8/data/m3_author_concentration_density.csv
    paper_v8/data/m4_repo_activity_density.csv
    paper_v8/data/m5_coordination_friction_trajectory.csv
    paper_v8/data/m6_t1_planning_quality.csv
    paper_v8/data/m7_planning_omission_rate.csv
    paper_v8/data/m8_rework_severity_ratio.csv
    paper_v8/data/m9_planning_vs_rework_association.csv
    paper_v8/data/m9_planning_vs_rework_association_group_contrast.csv

Output
------
    paper_v8/data/results/results_summary.json
"""

from __future__ import annotations

import json

import pandas as pd
from _paths import DATA_DIR, ensure_results_output_dir

OUTPUT_PATH = ensure_results_output_dir() / "results_summary.json"


def summarize_rq1() -> dict[str, object]:
    """AI-dependency trajectory (M1) and role-disruption risk (M2)."""
    m1 = pd.read_csv(DATA_DIR / "m1_ai_dependency_trajectory.csv")
    m2 = pd.read_csv(DATA_DIR / "m2_role_disruption_risk.csv")

    trajectory = {}
    for semestre, group in m1.groupby("Semestre"):
        group = group.set_index("temporal_marker")["ai_dependency_composite_mean"]
        trajectory[semestre] = {
            "T1": round(float(group["T1"]), 3),
            "T2": round(float(group["T2"]), 3),
            "T3": round(float(group["T3"]), 3),
            "delta_t1_t3": round(float(group["T3"] - group["T1"]), 3),
        }

    role_pooled = (
        m2.groupby("role")
        .apply(lambda g: (g["mean"] * g["n_valid"]).sum() / g["n_valid"].sum())
        .sort_values(ascending=False)
    )
    role_by_cut = (
        m2.groupby(["role", "temporal_marker"])
        .apply(lambda g: (g["mean"] * g["n_valid"]).sum() / g["n_valid"].sum())
        .unstack("temporal_marker")[["T1", "T2", "T3"]]
        .reindex(role_pooled.index)
    )

    return {
        "m1_ai_dependency_trajectory_by_semester": trajectory,
        "m2_role_pooled_mean_ranked": {role: round(float(v), 3) for role, v in role_pooled.items()},
        "m2_role_pooled_mean_by_cut": {
            role: {cut: round(float(value), 3) for cut, value in row.items()}
            for role, row in role_by_cut.iterrows()
        },
        "m2_highest_risk_role": role_pooled.index[0],
        "m2_lowest_risk_role": role_pooled.index[-1],
    }


def summarize_rq2() -> dict[str, object]:
    """Repository activity density (M4) vs. coordination friction (M5), plus author concentration (M3)."""
    m3 = pd.read_csv(DATA_DIR / "m3_author_concentration_density.csv")
    m4 = pd.read_csv(DATA_DIR / "m4_repo_activity_density.csv")
    m5 = pd.read_csv(DATA_DIR / "m5_coordination_friction_trajectory.csv")

    pooled_cc_total = m4[(m4["Semestre"] == "all") & (m4["metric"] == "cc_total")].set_index("cut")["mean"]
    activity_fold_increase = float(pooled_cc_total["T3"] / pooled_cc_total["T1"])

    friction = m5.set_index("temporal_marker")["coordination_friction"]

    pre_t3 = m3[(m3["cut"] == "T3") & (m3["commit_n"] > 0)]

    return {
        "m4_pooled_cc_total_mean_by_cut": {cut: round(float(value), 1) for cut, value in pooled_cc_total.items()},
        "m4_activity_density_fold_increase_t1_to_t3": round(activity_fold_increase, 1),
        "m5_coordination_friction_by_cut": {cut: int(value) for cut, value in friction.items()},
        "m5_friction_range_t1_to_t3": int(friction.max() - friction.min()),
        "m3_pre_t3_author_share_median_of_medians": round(float(pre_t3["author_share_median"].median()), 3),
        "m3_pre_t3_author_gini_median": round(float(pre_t3["author_gini"].median()), 3),
        "m3_n_team_semesters_with_t3_commits": int(len(pre_t3)),
    }


def summarize_rq3() -> dict[str, object]:
    """Planning quality (M6), omission (M7), rework (M8), and their association (M9)."""
    m6 = pd.read_csv(DATA_DIR / "m6_t1_planning_quality.csv")
    m7 = pd.read_csv(DATA_DIR / "m7_planning_omission_rate.csv")
    m8 = pd.read_csv(DATA_DIR / "m8_rework_severity_ratio.csv")
    m9_corr = pd.read_csv(DATA_DIR / "m9_planning_vs_rework_association.csv")
    m9_group = pd.read_csv(DATA_DIR / "m9_planning_vs_rework_association_group_contrast.csv")

    omission = m7.set_index("Semestre")[["n_teams", "n_omitted", "omission_rate"]].to_dict("index")

    rework_extreme = m8.sort_values("rework_churn_t3", ascending=False).iloc[0]

    group_rework = m9_group[m9_group["outcome"] == "rework_churn_t3"].set_index("planning_group")["mean"]
    group_progress = m9_group[m9_group["outcome"] == "project_progress_mean_t3"].set_index("planning_group")["mean"]

    return {
        "m6_planning_score_scored_n": int(m6["t1_planning_score"].notna().sum()),
        "m6_planning_score_mean_scored": round(float(m6["t1_planning_score"].mean()), 2),
        "m7_omission_by_semester": {
            semestre: {k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items()}
            for semestre, row in omission.items()
        },
        "m8_max_rework_team": f"{rework_extreme['ID_Equipe']}|{rework_extreme['Semestre']}",
        "m8_max_rework_churn_t3": float(rework_extreme["rework_churn_t3"]),
        "m9_correlations": m9_corr.set_index("outcome")[["n", "spearman_rho", "spearman_p"]].round(3).to_dict("index"),
        "m9_group_contrast_rework_churn_t3_mean": {
            "low": round(float(group_rework["low"]), 1),
            "high": round(float(group_rework["high"]), 1),
            "low_over_high_ratio": round(float(group_rework["low"] / group_rework["high"]), 2),
        },
        "m9_group_contrast_project_progress_mean_t3": {
            "low": round(float(group_progress["low"]), 3),
            "high": round(float(group_progress["high"]), 3),
        },
    }


def main() -> None:
    summary = {
        "rq1": summarize_rq1(),
        "rq2": summarize_rq2(),
        "rq3": summarize_rq3(),
    }
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
