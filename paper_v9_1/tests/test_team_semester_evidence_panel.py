from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.build_team_semester_evidence_panel import STEM, generate


def test_team_semester_evidence_panel_integrates_core_metrics_with_coverage_flags() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"]["team_semesters"] == 14
    assert result["coverage"]["m5_available_team_semesters"] == 9
    assert result["coverage"]["m5_unavailable_team_semesters"] == 5
    assert result["coverage"]["m6b_success_team_semesters"] == 9
    assert result["coverage"]["m6b_unavailable_team_semesters"] == 5

    figures = Path("paper_v9/figures")
    panel_path = figures / f"{STEM}.csv"
    metadata_path = figures / f"{STEM}.metadata.json"
    assert panel_path.is_file()
    assert metadata_path.is_file()

    panel = pd.read_csv(panel_path, dtype={"Semestre": str})
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert panel[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
    assert panel.shape[0] == 14
    assert sorted(panel["Semestre"].unique().tolist()) == ["2025.2", "2026.1"]

    required_columns = {
        "planning_present_t1",
        "planning_scope_log1p_t1",
        "planning_scope_tier",
        "evaluator_score_t1",
        "evaluator_score_t2",
        "evaluator_score_t3",
        "delta_score_t3_minus_t1",
        "score_trajectory_group",
        "team_total_commit_n",
        "active_day_count",
        "final7_commit_share_pct",
        "final7_clean_churn_share_pct",
        "regularity_index",
        "clean_rework_churn_t3",
        "clean_rework_ratio_t3",
        "baseline_eligible_for_rework_t3",
        "technical_complexity_mean_t3",
        "clean_distinct_file_n",
        "m5_coverage_status",
        "m5_team_level_measure",
        "m5_zero_filled_unavailable_semesters",
        "m6b_status",
        "panel_row_completeness_status",
        "coverage_fields_present",
    }
    assert required_columns.issubset(panel.columns)

    assert panel["regularity_index"].between(0, 1).all()
    assert panel["final7_commit_share_pct"].between(0, 100).all()
    assert panel["final7_clean_churn_share_pct"].between(0, 100).all()
    assert panel["m1_aggregation_level"].eq("semester_checkpoint_student_aggregate").all()
    assert panel["m2_aggregation_level"].eq("semester_checkpoint_role_aggregate").all()
    assert panel["m5_team_level_measure"].eq(False).all()
    assert panel["m5_zero_filled_unavailable_semesters"].eq(False).all()
    assert panel["panel_row_completeness_status"].eq("complete_core_metrics").all()
    assert panel["coverage_fields_present"].eq(True).all()

    m5_2025 = panel.loc[panel["Semestre"].eq("2025.2")]
    m5_2026 = panel.loc[panel["Semestre"].eq("2026.1")]
    assert m5_2025["m5_coverage_status"].eq("available_transcript_corpus_2025_2").all()
    assert m5_2026["m5_coverage_status"].eq("unavailable_not_measured").all()
    assert m5_2025["m5_global_friction_marker_density_per_1k_tokens_t1"].notna().all()
    assert m5_2026["m5_global_friction_marker_density_per_1k_tokens_t1"].isna().all()

    assert metadata["contract_version"] == "team-semester-evidence-panel-v1"
    assert metadata["grain_contract"]["row_unit"] == "team_semester"
    assert "m1_perception" in metadata["grain_contract"]["semester_checkpoint_aggregates_repeated_by_team_semester"]
    assert "m5_marker_density" in metadata["grain_contract"]["global_transcript_corpus_context_repeated_for_2025_2_only"]
    assert metadata["inference"] == "descriptive_integrated_evidence_panel_not_causal"
