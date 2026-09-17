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
| analysis_id                              | unit_of_analysis | n_valid | coefficient_or_statistic | p_value                | status      |
|------------------------------------------|------------------|---------|--------------------------|------------------------|-------------|
| pi_vs_cc_primary                        | team_semester    | 14      | -0.0067666495245095      | 0.9816838660605892     | success     |
| pi_vs_delta_dt_primary                  | team_semester    | 14      | -0.0147096475119091      | 0.960194880594909      | success     |
| ai_vs_cc_primary                        | team_semester    | 7       | 0.2142857142857143       | 0.6445115810207203     | success     |
| context_ie_temporal_primary             | cut_context      | 3       | null                     | null                   | unavailable  |
| pi_high_vs_low_cc_primary               | team_semester    | 14      | 21.0                     | 0.7103729603729605     | success     |
| ai_high_vs_low_cc_primary               | team_semester    | 7       | 6.0                      | 1.0                    | success     |
| context_ie_high_vs_low_rework_primary   | cut_context      | 3       | null                     | null                   | unavailable  |

## Verdict
conditional-go  
no_significant_result_and_small_sample_reframe_as_exploratory  

The verdict is a conditional-go because there were no significant results found across the analyses (count_supports = 0) despite testing 5 analyses (count_tested = 5). The team has a sufficient number of semesters (team_semester_n = 14) to consider reframing the findings as exploratory.

## Remediation options if not a clean go
- Collect additional semesters/teams to raise team_semester n toward the configured sufficiency threshold.
- Reframe Phase 3/4 claims as exploratory/descriptive case-study findings rather than confirmatory results.
- Expand qualitative triangulation (transcripts, open-ended responses) to compensate for low quantitative power.
- Add repository-level covariates (team size, prior experience) to explain variance beyond the current primary pairs.
