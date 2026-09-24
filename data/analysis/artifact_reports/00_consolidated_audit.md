## Index
- data/analysis/artifact_reports/act_1_evolutionary_ceiling.md
- data/analysis/artifact_reports/act_2_planning_debt.md
- data/analysis/artifact_reports/act_3_human_factor.md
- data/analysis/artifact_reports/act_4_value_inversion.md
- data/analysis/artifact_reports/code_churn_metrics.md
- data/analysis/artifact_reports/correlation_results.md
- data/analysis/artifact_reports/cut_context_metrics.md
- data/analysis/artifact_reports/figure_ai_before_t3.md
- data/analysis/artifact_reports/figure_cc_by_temporal_cut.md
- data/analysis/artifact_reports/figure_delta_dt_by_team_semester.md
- data/analysis/artifact_reports/figure_ie_by_cut_or_corpus.md
- data/analysis/artifact_reports/figure_pi_vs_cc.md
- data/analysis/artifact_reports/hypothesis_results.md
- data/analysis/artifact_reports/integration_friction_metrics.md
- data/analysis/artifact_reports/phase2_contract_report.md
- data/analysis/artifact_reports/planning_metrics.md
- data/analysis/artifact_reports/statistical_dataset_manifest.md
- data/analysis/artifact_reports/student_nlp.md
- data/analysis/artifact_reports/team_metrics.md
- data/analysis/artifact_reports/technical_degradation_metrics.md
- data/analysis/artifact_reports/textual_cut_signals.md
- data/analysis/artifact_reports/transcript_nlp.md

## Evidence table
| analysis_id                              | unit_of_analysis | n_valid | coefficient_or_statistic | p_value | status     |
|------------------------------------------|------------------|---------|--------------------------|---------|------------|
| pi_vs_cc_primary                         | team_semester    | 14      | -0.1556329390637204      | 0.5952  | success    |
| pi_vs_delta_dt_primary                   | team_semester    | 14      | -0.0147096475119091      | 0.9602  | success    |
| ai_vs_cc_primary                         | team_semester    | 7       | -0.1071428571428571      | 0.8192  | success    |
| context_ie_temporal_primary              | cut_context      | 3       | 1.0                      | 0.0     | success    |
| pi_high_vs_low_cc_primary                | team_semester    | 14      | 29.0                     | 0.6200  | success    |
| ai_high_vs_low_cc_primary                | team_semester    | 7       | 7.0                      | 0.8571  | success    |
| context_ie_high_vs_low_rework_primary    | cut_context      | 3       | null                     | null    | unavailable |

## Verdict
conditional-go  
significant_result_but_small_sample  

The verdict is a conditional-go because there is 1 supporting result out of 6 tested, and the team_semester_n is 14, which is below the configured sufficiency threshold.

## Remediation options if not a clean go
- Collect additional semesters/teams to raise team_semester n toward the configured sufficiency threshold.
- Reframe Phase 3/4 claims as exploratory/descriptive case-study findings rather than confirmatory results.
- Expand qualitative triangulation (transcripts, open-ended responses) to compensate for low quantitative power.
- Add repository-level covariates (team size, prior experience) to explain variance beyond the current primary pairs.
