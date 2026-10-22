"""Explicit projections for the approved paper snapshot (no source observations)."""

from __future__ import annotations

from dataclasses import dataclass

CONTRACT_SHA256 = "5cb0534f36bcee75eb08d56fda403f6ef443c826400ca790c727223972e52c68"
INDEX_SHA256 = "f0fe56c09d02104593e86da7e5f3d4e63b11cf782282988e99ec4019256c6fff"
SUPPLEMENT_SHA256 = "e721a33801a1e01be8d7cdd05aa2f7bdfd95bfb5d03ef856e7e8c34264a7d5a0"
SUPPLEMENT = (
    "rq1_m1_perception_with_sd_data.csv", "rq2_m3_activity_pooled_data.csv",
    "rq2_m4_m5_checkpoint_data.csv", "rq2_m5_density_data.csv",
    "rq2_nonoverlapping_weekly_bin_contract.csv", "rq2_score_trajectory_base_data.csv",
    "rq3_architectural_artifact_presence_data.csv", "rq3_architecture_rework_profile_data.csv",
)

KEYS = {
    "C": "Semestre",
    "CP": "Semestre temporal_marker",
    "T": "Semestre ID_Equipe",
    "TP": "Semestre ID_Equipe temporal_marker",
    "P": "temporal_marker",
    "W": "window_end_day",
}
RENAMES = {
    "Semestre": "cohort", "ID_Equipe": "team_id", "temporal_marker": "checkpoint",
    "removed_Semestre": "omitted_cohort", "removed_ID_Equipe": "omitted_team_id",
    "most_influential_team_semester": "most_influential_case",
}


@dataclass(frozen=True)
class Table:
    source: str
    dataset_id: str
    keys: tuple[str, ...]
    fields: tuple[tuple[str, str], ...]
    definition: bool = False


def table(source: str, dataset_id: str, keys: str, fields: str, *,
          definition: bool = False) -> Table:
    key_fields = tuple(KEYS.get(keys.split()[0], keys.split()[0]).split()) + tuple(keys.split()[1:])
    pairs = []
    for field in (*key_fields, *fields.split()):
        source_name, _, target = field.partition(":")
        pairs.append((source_name, target or RENAMES.get(source_name, source_name)))
    return Table(source, dataset_id, key_fields, tuple(pairs), definition)


SUMMARY = "mean std median q1 q3 iqr"
DISTRIBUTION = "count respondent_n share"
CONCENTRATION = "commit_n active_days author_n max_author_share author_gini measurement_status"
SCORE_FINAL7 = (
    "evaluator_score_t1 evaluator_score_t3 delta_score_t3_minus_t1 score_trajectory_group "
    "planning_scope_tier final7_share_pct activity_metric final7_concentration_tier delta_direction quadrant"
)
PLANNING_FINAL7 = (
    "planning_scope_log1p_t1 planning_scope_tier evaluator_score_t3 delta_score_t3_minus_t1 "
    "clean_rework_churn_t3 final7_share_pct activity_metric final7_concentration_tier "
    "planning_concentration_quadrant abs_delta_score_t3_minus_t1 marker_size"
)
COMPONENTS = (
    "regularity_active_day_share_component regularity_commit_entropy_component "
    "regularity_clean_churn_entropy_component regularity_commit_weekly_cv_component "
    "regularity_clean_churn_weekly_cv_component regularity_m7_activity_component "
    "regularity_commit_distribution_component regularity_clean_churn_distribution_component"
)
COMPLEXITY = (
    "technical_complexity_mean_t1 technical_complexity_mean_t2 technical_complexity_mean_t3 "
    "delta_technical_complexity_t3_minus_t1 clean_distinct_file_n clean_distinct_directory_n "
    "clean_max_path_depth clean_extension_n clean_touching_commit_n_inferred clean_total_churn_inferred "
    "frontend_clean_file_event_n backend_clean_file_event_n mixed_clean_file_event_n "
    "unclassified_clean_file_event_n mean_clean_files_per_commit frontend_clean_file_event_share "
    "backend_clean_file_event_share clean_churn_t3 all_churn_t3 m4_clean_unique_file_n_t3 "
    "m4_clean_touching_commit_n_t3 clean_rework_churn_t3 clean_rework_ratio_t3 "
    "baseline_eligible_for_rework_t3 measurement_status planning_artifact_present_t1 "
    "planning_scope_log1p_t1 pi_file_count_t1 pi_line_delta_t1 score_trajectory_group planning_scope_tier "
    "final7_commit_share_pct final7_clean_churn_share_pct"
)
TABLES = (
    table("m1_rq1_perception_panel_long.csv", "m1-perceptions", "CP perception_family",
          f"perception_group {SUMMARY} n:response_n student_n:cohort_response_n coverage measurement_status"),
    *(table(source, public, "CP measure category", DISTRIBUTION) for source, public in (
        ("m1_rq1_usage_frequency.csv", "m1-frequency"),
        ("m1_rq1_usage_tasks.csv", "m1-tasks"),
        ("m1_rq1_usage_tools.csv", "m1-tools"),
        ("m1_rq1_prior_ai_project_experience.csv", "m1-prior-experience"),
        ("m1_rq1_autonomy_tool_balance.csv", "m1-autonomy"),
    )),
    table("m1_rq1_career_impact_topics_exploratory.csv", "m1-career-topics", "CP topic",
          "count respondent_n:topic_assignment_n share_of_topic_assignments coding_status"),
    table("m2_role_perception_distributions.csv", "m2-role-distributions", "CP role score", DISTRIBUTION),
    table("m2_role_perception_by_team_semester.csv", "m2-role-summaries", "CP role",
          f"n:response_n {SUMMARY} disagreement_share neutral_share agreement_share"),
    table("m2_role_perception_paired_t1_t3.csv", "m2-paired-sensitivity", "C role",
          "pairs:pair_n mean_T1:mean_t1 mean_T3:mean_t3 mean_change median_change "
          "increased_share unchanged_share decreased_share"),
    table("m3_author_activity_participation.csv", "m3-participation", "T",
          "total_commit_n pre_commit_n post_commit_n final_window_commit_n pre_share post_share "
          "final_window_share small_denominator_lt_10 measurement_status"),
    table("m3_author_concentration.csv", "m3-author-concentration", "T phase", CONCENTRATION),
    table("m3_activity_rolling_7day.csv", "m3-rolling", "T window_end_day", CONCENTRATION),
    table("m3_activity_rolling_7day_pooled.csv", "m3-rolling-pooled", "W",
          "team_semester_n active_team_semester_n total_commit_n mean_commit_n median_commit_n "
          "max_commit_n median_active_days median_max_author_share median_author_gini active_team_semester_share"),
    table("m4_churn_magnitude.csv", "m4-checkpoint-churn", "TP",
          "clean_churn all_churn clean_unique_file_n clean_touching_commit_n "
          "median_clean_churn_per_touching_commit max_clean_churn_per_touching_commit "
          "clean_share_of_all_churn measurement_status"),
    table("m4_churn_magnitude_pooled.csv", "m4-checkpoint-pooled", "P",
          "team_semester_n observed_clean_team_semester_n total_clean_churn median_clean_churn "
          "total_all_churn median_clean_unique_file_n clean_share_of_all_churn"),
    table("m4_artifact_composition_pooled.csv", "m4-path-composition", "P file_category",
          "included_in_m4 team_semester_n file_event_n unique_file_n churn_lines churn_share"),
    table("m5_marker_density.csv", "m5-marker-density", "P",
          "transcript_chunk_n source_session_n character_n token_n friction_marker_n alignment handoff "
          "integration blocker rework friction_marker_density_per_1k_tokens measurement_status"),
    table("m5_marker_composition.csv", "m5-marker-composition", "P friction_subtype",
          "friction_marker_n marker_n marker_share"),
    table("m5_corpus_coverage.csv", "m5-corpus-coverage", "P",
          "transcript_chunk_n source_session_n character_n token_n friction_marker_n observed_semester_n"),
    table("m6a_structural_planning.csv", "m6a-structural-planning", "T",
          "pi_available pi_file_count_t1 pi_line_delta_t1 pi_renamed_count_t1 pi_deleted_count_t1 "
          "pi_binary_event_count_t1 planning_artifact_activity_t1 planning_artifact_present_t1 "
          "planning_scope_log1p_t1 measurement_status"),
    table("m7_checkpoint_inactivity.csv", "m7-checkpoint-inactivity", "TP",
          "commit_n_7d repository_inactive_7d measurement_status"),
    table("m8_rework_magnitude.csv", "m8-rework-magnitude", "T",
          "clean_rework_churn_t3 clean_deferred_churn_t3 prior_clean_path_n clean_total_churn_t3 "
          "baseline_eligible_for_rework_t3 clean_rework_ratio_t3 measurement_status"),
    table("m8_baseline_eligibility.csv", "m8-baseline-eligibility", "T",
          "prior_clean_path_n baseline_eligible_for_rework_t3 measurement_status"),
    *(table(source, public, "analysis_id predictor outcome",
            "n:sample_n spearman_rho spearman_p_exploratory") for source, public in (
        ("m9_planning_vs_rework_m6a_m8a.csv", "m9-structural-rework-magnitude"),
        ("m9_planning_vs_rework_m6a_m8b_eligible_stratum.csv", "m9-structural-rework-ratio"),
        ("m9_planning_vs_outcomes_m6a_t3.csv", "m9-structural-outcomes"),
        ("m9_planning_vs_outcomes_m6b_t3_if_approved.csv", "m9-content-outcomes"),
    )),
    table("m9_leave_one_out_intervals.csv", "m9-leave-one-out",
          "analysis_id predictor outcome removed_Semestre removed_ID_Equipe",
          "n_remaining:remaining_sample_n spearman_rho spearman_p_exploratory"),
    table("rq3_architectural_artifact_presence_data.csv", "m6a-presence-by-cohort", "C evidence_state",
          "team_semester_n team_semester_count"),
    table("rq3_architecture_rework_profile_data.csv", "planning-rework-profile", "T",
          "pi_file_count_t1 pi_line_delta_t1 planning_artifact_present_t1 planning_scope_log1p_t1 "
          "measurement_status clean_rework_churn_t3 baseline_eligible_for_rework_t3"),
    table("rq3_technical_complexity_vs_rework_data.csv", "complexity-rework-figure", "T",
          "technical_complexity_mean_t3 clean_rework_churn_t3 clean_rework_ratio_t3 planning_scope_tier "
          "planning_scope_log1p_t1 score_trajectory_group final7_commit_share_pct final7_clean_churn_share_pct"),
    table("rq2_phase_activity_share_data.csv", "phase-activity", "T phase",
          "phase_order commit_n clean_churn active_day_n active_author_n score_trajectory_group "
          "planning_scope_tier evaluator_score_t3 delta_score_t3_minus_t1 team_total_commit_n "
          "team_total_clean_churn commit_share_pct clean_churn_share_pct"),
    table("rq2_phase_activity_share_summary.csv", "phase-activity-summary", "score_trajectory_group phase",
          "phase_order team_semester_n mean_commit_share_pct median_commit_share_pct mean_clean_churn_share_pct "
          "median_clean_churn_share_pct mean_active_day_n mean_active_author_n"),
    table("rq2_score_delta_vs_final7_commit_concentration_data.csv", "score-final7-commits", "T", SCORE_FINAL7),
    table("rq2_score_delta_vs_final7_clean_churn_concentration_data.csv", "score-final7-clean-churn", "T", SCORE_FINAL7),
    table("rq2_score_delta_final7_quadrants.csv", "score-final7-quadrants",
          "activity_metric quadrant planning_scope_tier",
          "final7_concentration_cut final7_concentration_median_pct delta_threshold team_semester_n "
          "median_final7_share_pct median_delta_score_t3_minus_t1"),
    table("rq2_planning_vs_final7_commit_concentration_data.csv", "planning-final7-commits", "T", PLANNING_FINAL7),
    table("rq2_planning_vs_final7_clean_churn_concentration_data.csv", "planning-final7-clean-churn", "T", PLANNING_FINAL7),
    table("rq2_planning_concentration_quadrant_summary.csv", "planning-final7-quadrants", "activity_metric quadrant",
          "team_semester_n team_semester_denominator mean_t3_score median_t3_score mean_delta_score "
          "median_delta_score mean_clean_rework_churn_t3 small_n_flag"),
    table("rq2_operational_regularity_data.csv", "operational-regularity", "T",
          "delta_score_t3_minus_t1 score_trajectory_group planning_scope_tier final7_commit_share_pct "
          "final7_clean_churn_share_pct active_day_count project_span_days active_day_share "
          "max_inactivity_gap_days median_inactivity_gap_days commit_weekly_cv clean_churn_weekly_cv "
          "temporal_entropy_commits temporal_entropy_clean_churn author_count max_author_share author_gini "
          f"m7_window_count m7_inactive_window_share regularity_index {COMPONENTS}"),
    table("rq2_m5_2025_triangulation_summary.csv", "transcript-context-2025", "P",
          "team_n m5_friction_marker_density_per_1k_tokens m5_friction_marker_n m5_token_n median_clean_churn "
          "mean_clean_churn median_evaluator_score_composite mean_evaluator_score_composite "
          "baseline_eligible_rework_team_n median_clean_rework_churn_t3 "
          "median_clean_rework_ratio_t3_baseline_eligible"),
    table("rq3_complexity_profile_data.csv", "complexity-profile", "T", COMPLEXITY),
    table("rq3_complexity_confounding_summary.csv", "complexity-stratified-associations", "relationship",
          "relationship_label predictor outcome rho_without_complexity_stratification rho_within_low_complexity "
          "rho_within_high_complexity complexity_stratification_variable complexity_median low_complexity_rule "
          "high_complexity_rule n_without_complexity_stratification n_within_low_complexity "
          "n_within_high_complexity minimum_n_for_rho"),
    table("rq3_influence_map_data.csv", "influence-cases",
          "relationship_id removed_Semestre removed_ID_Equipe",
          "relationship_label predictor outcome full_sample_n loo_n full_sample_rho loo_rho rho_delta_from_full "
          "abs_rho_delta_from_full full_sample_sign loo_sign sign_changed availability_status"),
    table("rq3_influence_relationship_contract.csv", "influence-relations", "relationship_id",
          "relationship_label predictor outcome full_sample_n leave_one_out_rows available_leave_one_out_rows "
          "full_sample_rho full_sample_sign loo_min_rho loo_max_rho max_abs_rho_delta_from_full "
          "sign_preservation_share availability_status"),
    table("rq3_directional_robustness_summary.csv", "influence-summary", "relationship_id",
          "full_sample_rho loo_min_rho loo_max_rho sign_preservation_share most_influential_team_semester "
          "max_abs_rho_delta_from_full available_leave_one_out_rows total_leave_one_out_rows unstable_sensitivity_flag"),
    table("rq2_nonoverlapping_weekly_bin_contract.csv", "weekly-bin-definitions", "week_bin",
          "week_bin_order start_day_relative_to_t3 end_day_relative_to_t3 interval_notation "
          "assignment_policy rolling_window_used", definition=True),
    table("rq3_complexity_metrics_contract.csv", "complexity-definitions", "metric",
          "construct_family definition heuristic_or_policy manual_genai_architecture_classification", definition=True),
)

ALIASES = {
    "rq1_m1_perception_with_sd_data.csv": "m1_rq1_perception_panel_long.csv",
    "rq2_m3_activity_pooled_data.csv": "m3_activity_rolling_7day_pooled.csv",
    "rq2_m4_m5_checkpoint_data.csv": "m4_churn_magnitude_pooled.csv",
    "rq2_m5_density_data.csv": "m5_marker_density.csv",
    "m8_rework_participation.csv": "m8_rework_magnitude.csv",
}
VERIFICATION = ("rq3_influence_heatmap_matrix.csv", "rq2_score_trajectory_base_data.csv")
JSON_SOURCES = ("m5_lexicon.json", "m6b_llm_planning_content.json")

TEXT_FIELDS = set((
    "cohort team_id checkpoint omitted_cohort omitted_team_id perception_family perception_group measure "
    "category topic role coding_status measurement_status phase file_category friction_subtype analysis_id "
    "predictor outcome evidence_state score_trajectory_group planning_scope_tier activity_metric "
    "final7_concentration_tier delta_direction quadrant final7_concentration_cut planning_concentration_quadrant "
    "relationship relationship_id relationship_label complexity_stratification_variable low_complexity_rule "
    "high_complexity_rule full_sample_sign loo_sign availability_status most_influential_case week_bin "
    "interval_notation assignment_policy metric construct_family definition heuristic_or_policy"
).split())
BOOLEAN_FIELDS = set((
    "small_denominator_lt_10 included_in_m4 pi_available planning_artifact_present_t1 repository_inactive_7d "
    "baseline_eligible_for_rework_t3 small_n_flag sign_changed unstable_sensitivity_flag rolling_window_used "
    "manual_genai_architecture_classification"
).split())
INTEGER_FIELDS = set((
    "response_n cohort_response_n count respondent_n topic_assignment_n score pair_n total_commit_n pre_commit_n "
    "post_commit_n final_window_commit_n commit_n active_days author_n window_end_day team_semester_n "
    "active_team_semester_n max_commit_n clean_churn all_churn clean_unique_file_n clean_touching_commit_n "
    "max_clean_churn_per_touching_commit observed_clean_team_semester_n total_clean_churn total_all_churn "
    "file_event_n unique_file_n churn_lines transcript_chunk_n source_session_n character_n token_n "
    "friction_marker_n alignment handoff integration blocker rework marker_n observed_semester_n "
    "pi_file_count_t1 pi_line_delta_t1 pi_renamed_count_t1 pi_deleted_count_t1 pi_binary_event_count_t1 "
    "planning_artifact_activity_t1 commit_n_7d clean_rework_churn_t3 clean_deferred_churn_t3 prior_clean_path_n "
    "clean_total_churn_t3 sample_n remaining_sample_n team_semester_count phase_order active_day_n active_author_n "
    "team_total_commit_n team_total_clean_churn team_semester_denominator active_day_count project_span_days "
    "max_inactivity_gap_days author_count m7_window_count team_n m5_friction_marker_n m5_token_n "
    "baseline_eligible_rework_team_n clean_distinct_file_n clean_distinct_directory_n clean_max_path_depth "
    "clean_extension_n clean_touching_commit_n_inferred clean_total_churn_inferred frontend_clean_file_event_n "
    "backend_clean_file_event_n mixed_clean_file_event_n unclassified_clean_file_event_n clean_churn_t3 all_churn_t3 "
    "m4_clean_unique_file_n_t3 m4_clean_touching_commit_n_t3 n_without_complexity_stratification "
    "n_within_low_complexity n_within_high_complexity minimum_n_for_rho full_sample_n loo_n leave_one_out_rows "
    "available_leave_one_out_rows total_leave_one_out_rows week_bin_order start_day_relative_to_t3 end_day_relative_to_t3"
).split())

# Only these measures have documented undefined/unavailable scalar states.
NULLABLE_FIELDS = set((
    "std max_author_share author_gini median_max_author_share median_author_gini pre_share post_share "
    "final_window_share median_clean_churn_per_touching_commit max_clean_churn_per_touching_commit "
    "clean_share_of_all_churn churn_share clean_rework_ratio_t3 spearman_rho spearman_p_exploratory "
    "rho_without_complexity_stratification rho_within_low_complexity rho_within_high_complexity full_sample_rho "
    "loo_rho rho_delta_from_full abs_rho_delta_from_full loo_min_rho loo_max_rho max_abs_rho_delta_from_full "
    "sign_preservation_share median_final7_share_pct median_delta_score_t3_minus_t1 mean_t3_score "
    "median_t3_score mean_delta_score median_delta_score mean_clean_rework_churn_t3"
).split())
