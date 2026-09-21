# Phase 3 Evidence Inventory

Generated at `2026-09-21T12:24:16.532980+00:00` by `phase3/build_evidence_inventory.py`.

## Interpretation Policy

The Phase 2.5 Markdown reports are the primary interpretive layer for Phase 3. Their artifact, act, and consolidated reports define the current narrative reading. Parquets, CSVs, JSON manifests, sidecars, and figures are used to verify, quantify, and visually support those interpretations. Cross-evidence remains secondary and exploratory; supporting, inconclusive, fragile, and methodological-warning results must remain distinguishable.

## Persisted Inventory

- Analysis tree: 248 files (.csv: 27, .json: 132, .md: 72, .parquet: 17).
- Cross-evidence tree: 113 files (.csv: 13, .json: 62, .md: 32, .parquet: 6).
- Figure assets: 88 files (.html: 19, .json: 19, .pdf: 12, .png: 19, .svg: 19).
- Phase 2.5 artifact reports: 23 Markdown files.
- Cross-evidence reports: 32 Markdown files.

## Phase 2.5 Report Layer

These reports are the starting point for claim extraction. Each claim must be traced from a report to its source artifact before entering the paper.

### `data/analysis/artifact_reports/00_consolidated_audit.md`
- Lines: 46
- Headings: ## Index | ## Evidence table | ## Verdict | ## Remediation options if not a clean go
- Evidence text: | analysis_id                              | unit_of_analysis | n_valid | coefficient_or_statistic | p_value                | status      |
- Evidence text: | context_ie_temporal_primary              | cut_context      | 3       | null                     | null                   | unavailable  |
- Evidence text: | context_ie_high_vs_low_rework_primary    | cut_context      | 3       | null                     | null                   | unavailable  |
- Evidence text: ## Verdict
- Evidence text: The verdict is conditional-go because there were no significant results found across the analyses (count_supports = 0) despite testing 5 analyses (count_tested = 5). The team has a sufficient number of semesters (team_semester_n = 14) to consider reframing the findings as exploratory.

### `data/analysis/artifact_reports/act_1_evolutionary_ceiling.md`
- Lines: 9
- Headings: ## Act summary | ## Artifacts bound to this act | ## Empirical status
- Evidence text: **Verdict:** descriptive_infrastructure
- Evidence text: ## Empirical status
- Evidence text: The aggregate act status is "not_yet_tested" because there is only one verdict, which is classified as descriptive infrastructure. This indicates that the act has not been empirically tested or validated.

### `data/analysis/artifact_reports/act_2_planning_debt.md`
- Lines: 19
- Headings: ## Act summary | ## Artifacts bound to this act | ## Empirical status
- Evidence text: - **team_metrics**: inconclusive
- Evidence text: - **correlation_results**: inconclusive
- Evidence text: - **hypothesis_results**: inconclusive
- Evidence text: - **figure_pi_vs_cc**: inconclusive
- Evidence text: - **figure_delta_dt_by_team_semester**: inconclusive

### `data/analysis/artifact_reports/act_3_human_factor.md`
- Lines: 21
- Headings: ## Act summary | ## Artifacts bound to this act | ## Empirical status
- Evidence text: - **cut_context_metrics**: unavailable
- Evidence text: - **team_metrics**: inconclusive
- Evidence text: - **correlation_results**: inconclusive
- Evidence text: - **hypothesis_results**: inconclusive
- Evidence text: - **figure_delta_dt_by_team_semester**: inconclusive

### `data/analysis/artifact_reports/act_4_value_inversion.md`
- Lines: 9
- Headings: ## Act summary | ## Artifacts bound to this act | ## Empirical status
- Evidence text: **Verdict:** descriptive_infrastructure
- Evidence text: ## Empirical status
- Evidence text: The aggregate act status is "not_yet_tested" because there is only one verdict, which is classified as descriptive infrastructure.

### `data/analysis/artifact_reports/code_churn_metrics.md`
- Lines: 26
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 2, which is meant to support or falsify the claim titled "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)."
- Evidence text: - cc_binary_file_events_t2: mean = 5.714285714285714, n_valid = 14
- Evidence text: - cc_commit_churn_n_missing_t3: mean = 0.0, n_valid = 14
- Evidence text: - cc_commit_churn_n_total_t3: mean = 33.714285714285715, n_valid = 14
- Evidence text: - cc_commit_churn_n_valid_t3: mean = 33.714285714285715, n_valid = 14

### `data/analysis/artifact_reports/correlation_results.md`
- Lines: 22
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts are 2 and 3. They are meant to support or falsify the claims in "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)" and "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".
- Evidence text: - For the analysis "pi_vs_cc_primary": n = 14, p-value = 0.9816838660605892, coefficient = -0.0067666495245095, missingness = 0.
- Evidence text: - For the analysis "pi_vs_delta_dt_primary": n = 14, p-value = 0.960194880594909, coefficient = -0.0147096475119091, missingness = 0.
- Evidence text: - For the analysis "ai_vs_cc_primary": n = 7, p-value = 0.6445115810207203, coefficient = 0.2142857142857143, missingness = 7.
- Evidence text: - For the analysis "context_ie_temporal_primary": n = 6, p-value = null, coefficient = null, missingness = 3.

### `data/analysis/artifact_reports/cut_context_metrics.md`
- Lines: 18
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 3, which is meant to support or falsify the claim associated with "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".
- Evidence text: The dataset contains 6 rows, with the following missingness: 3 missing values for the columns "ie_transcript_coordination_friction_score_iqr", "ie_transcript_coordination_friction_score_mean", "ie_transcript_coordination_friction_score_median", and others. The overall verdict from the analysis is "unavailable", with specific tests also yielding "unavailable" results.
- Evidence text: The deterministic verdict is "unavailable". This is justified as all analyses conducted on the dataset returned results that were classified as "unavailable".
- Evidence text: ## Known limitations
- Evidence text: - All analyses returned "unavailable" results.

### `data/analysis/artifact_reports/figure_ai_before_t3.md`
- Lines: 17
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 3, which supports the claim related to "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)."
- Evidence text: The current data shows a total of 7 valid observations with no missing data (n_missing: 0). The analyses conducted were inconclusive, with p-values and coefficients not specified, leading to an overall verdict of inconclusive.
- Evidence text: The deterministic verdict is "inconclusive." This is justified as both analyses (ai_vs_cc_primary and ai_high_vs_low_cc_primary) returned inconclusive results, indicating that no definitive conclusions can be drawn from the data.
- Evidence text: ## Known limitations

### `data/analysis/artifact_reports/figure_cc_by_temporal_cut.md`
- Lines: 17
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 2, which supports the claim titled "A Anatomia da Divida de Planejamento (Diagnosis)."
- Evidence text: The current data shows a total of 42 observations, with 11 missing values, resulting in 31 valid observations. There are no statistical tests reported, and thus no p-values or coefficients are available.
- Evidence text: The deterministic verdict is "descriptive_infrastructure." This is justified as there are no tests conducted, and the data primarily serves to describe the infrastructure without providing inferential statistics.
- Evidence text: ## Known limitations

### `data/analysis/artifact_reports/figure_delta_dt_by_team_semester.md`
- Lines: 18
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts associated with this artifact are 2 and 3. Act 2 supports the claim regarding the diagnosis of planning debt, while Act 3 provides evidence related to the human factor and the illusion of progress.
- Evidence text: The current data shows a total of 42 observations with no missing data (n_missing: 0). The analysis conducted was a correlation (analysis_id: "pi_vs_delta_dt_primary") which resulted in an inconclusive verdict (overall: "inconclusive").
- Evidence text: The deterministic verdict for this analysis is "inconclusive". This is justified by the fact that the correlation analysis did not yield significant results, as indicated by the overall verdict.
- Evidence text: ## Known limitations
- Evidence text: The known limitations include:

### `data/analysis/artifact_reports/figure_ie_by_cut_or_corpus.md`
- Lines: 17
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 3, which is intended to support the claim related to "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".
- Evidence text: The current data shows a total of 18 observations, with 9 valid observations and 9 missing. There are three complete transcript-score observations for the primary pair. All analyses conducted resulted in verdicts that are unavailable, with no significant p-values or coefficients reported.
- Evidence text: The deterministic verdict is "unavailable". This is justified as all analyses conducted, including correlation and hypothesis tests, returned verdicts of "unavailable".
- Evidence text: ## Known limitations

### `data/analysis/artifact_reports/figure_pi_vs_cc.md`
- Lines: 17
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 2, which corresponds to "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)." This act is intended to support or falsify the claims related to the analysis of the relationship between the two variables.
- Evidence text: The current data shows a total of 14 valid observations (n = 14) with no missing data (n_missing = 0). The results of the analyses are inconclusive, with no significant findings reported. The p-values and coefficients are not provided, indicating a lack of statistical significance.
- Evidence text: The overall verdict of the analysis is "inconclusive." This is justified by the fact that both primary correlation and hypothesis tests yielded inconclusive results, with no significant relationships identified in the data.
- Evidence text: ## Known limitations
- Evidence text: - Observational association; n=14.

### `data/analysis/artifact_reports/hypothesis_results.md`
- Lines: 21
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts are 2 and 3. They are meant to support or falsify the claims related to "A Anatomia da Divida de Planejamento (Diagnosis)" and "O Fator Humano e a Ilusao do Progresso (Evidence)".
- Evidence text: - For the analysis "pi_high_vs_low_cc_primary": n = 14, p-value = 0.7103729603729605, U statistic = 21.0, n_missing = 0.
- Evidence text: - For the analysis "ai_high_vs_low_cc_primary": n = 14, p-value = 1.0, U statistic = 6.0, n_missing = 7.
- Evidence text: - For the analysis "context_ie_high_vs_low_rework_primary": n = 6, p-value = null, U statistic = null, n_missing = 3.
- Evidence text: The deterministic verdict is "inconclusive". This is justified as all tests resulted in inconclusive outcomes: "pi_high_vs_low_cc_primary" and "ai_high_vs_low_cc_primary" both returned inconclusive verdicts, while "context_ie_high_vs_low_rework_primary" was unavailable due to insufficient group size.

### `data/analysis/artifact_reports/integration_friction_metrics.md`
- Lines: 27
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 3, which is meant to support the claim titled "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)."
- Evidence text: - ai_author_n_before_t3_window: n = 14, mean = 1.8571428571428572, median = 1.0, min = 0.0, max = 5.0
- Evidence text: - ai_author_share_n_missing_t2: n = 14, mean = 0.0, median = 0.0, min = 0.0, max = 0.0
- Evidence text: - ai_author_share_n_missing_t3: n = 14, mean = 0.0, median = 0.0, min = 0.0, max = 0.0
- Evidence text: - ai_author_share_n_valid_before_t3_window: n = 14, mean = 1.8571428571428572, median = 1.0, min = 0.0, max = 5.0

### `data/analysis/artifact_reports/phase2_contract_report.md`
- Lines: 28
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts included are 1, 2, and 3. They are meant to support or falsify the following claims:
- Evidence text: The deterministic verdict is "descriptive_infrastructure." This is justified as there are no tests conducted, indicating that the analysis primarily serves to describe the existing data infrastructure without inferential claims.
- Evidence text: ## Known limitations

### `data/analysis/artifact_reports/planning_metrics.md`
- Lines: 29
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 2, which is meant to support or falsify the claim titled "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)."
- Evidence text: - `pi_binary_event_count_t3`: n = 14, mean = 4.0, p-value = unavailable
- Evidence text: - `pi_deleted_count_t3`: n = 14, mean = 12.857142857142858, p-value = unavailable
- Evidence text: - `pi_file_count_t1`: n = 14, mean = 2.5714285714285716, p-value = unavailable
- Evidence text: - `pi_line_delta_t1`: n = 14, mean = 60.142857142857146, p-value = unavailable

### `data/analysis/artifact_reports/statistical_dataset_manifest.md`
- Lines: 31
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts associated with this dataset are 2, 3, and 4. These acts are intended to support or falsify claims regarding the anatomy of planning debt, the human factor in progress perception, and the inversion of values in the era of AI.
- Evidence text: - p-values: Not applicable
- Evidence text: The deterministic verdict is "descriptive_infrastructure". This is justified as the dataset provides a foundational overview of the metrics without significant inferential testing or results.
- Evidence text: ## Known limitations
- Evidence text: The limitations include:

### `data/analysis/artifact_reports/student_nlp.md`
- Lines: 18
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts associated with this artifact are 2 and 3. Act 2 supports the claim regarding the anatomy of planning debt, while Act 3 provides evidence related to the human factor and the illusion of progress.
- Evidence text: The deterministic verdict is "descriptive_infrastructure". This is justified as there are no tests conducted, and the dataset serves primarily as a descriptive resource without inferential claims.
- Evidence text: ## Known limitations

### `data/analysis/artifact_reports/team_metrics.md`
- Lines: 26
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts associated with this dataset are 2 and 3. Act 2 supports the claim regarding the anatomy of planning debt, while Act 3 addresses the human factor and the illusion of progress.
- Evidence text: The dataset contains 14 rows, with no missing values for key variables such as "ID_Equipe" and "Semestre". However, the analysis results are inconclusive, with all tests yielding non-significant outcomes:
- Evidence text: - pi_vs_cc_primary: inconclusive
- Evidence text: - pi_vs_delta_dt_primary: inconclusive
- Evidence text: - ai_vs_cc_primary: inconclusive

### `data/analysis/artifact_reports/technical_degradation_metrics.md`
- Lines: 27
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts associated with this artifact are 2 and 3. Act 2 supports the claim regarding the diagnosis of planning debt, while Act 3 provides evidence related to the human factor and the illusion of progress.
- Evidence text: - For `delta_dt_t1_t2`: n_total = 14, n_valid = 14, mean = -0.014880952380952392, p-value = unavailable.
- Evidence text: - For `delta_dt_t2_t3`: n_total = 14, n_valid = 14, mean = 0.22619047619047622, p-value = unavailable.
- Evidence text: - For `technical_complexity_mean_t1`: n_total = 14, n_valid = 14, mean = 1.625, p-value = unavailable.
- Evidence text: - For `technical_complexity_mean_t2`: n_total = 14, n_valid = 14, mean = 1.6101190476190477, p-value = unavailable.

### `data/analysis/artifact_reports/textual_cut_signals.md`
- Lines: 27
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 3, which is meant to support the claim titled "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)."
- Evidence text: - For `student_career_expectation_ai_dependency_score_iqr`: n_total = 6, n_valid = 6, mean = 0.0, median = 0.0, min = 0.0, max = 0.0.
- Evidence text: - For `student_career_expectation_ai_dependency_score_mode`: n_total = 6, n_valid = 6, mean = 0.0, median = 0.0, min = 0.0, max = 0.0.
- Evidence text: - For `student_career_expectation_ai_dependency_score_mode_n`: n_total = 6, n_valid = 6, mean = 31.166666666666668, median = 31.0, min = 18.0, max = 46.0.
- Evidence text: - For `student_career_expectation_ai_dependency_score_mode_share`: n_total = 6, n_valid = 6, mean = 1.0, median = 1.0, min = 1.0, max = 1.0.

### `data/analysis/artifact_reports/transcript_nlp.md`
- Lines: 19
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act number is 3, which is meant to support or falsify the claim associated with "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".
- Evidence text: The current data shows a total of 100 rows with no missing values across all variables. There are no statistical tests reported, and thus no p-values or coefficients are available.
- Evidence text: The deterministic verdict is "descriptive_infrastructure". This is justified as there are no statistical tests conducted, indicating that the data serves primarily as a descriptive resource rather than providing inferential insights.
- Evidence text: ## Known limitations
- Evidence text: - No p-values or coefficients are available.

## Cross-Evidence Report Layer

Cross-evidence is a secondary exploratory layer for Acts 2 and 3, with contextual or methodological relevance to Acts 1 and 4. It cannot override the Phase 2.5 consolidated audit. Its positive results require checks for sample size, multiple comparisons, exclusions, and leave-one-out stability.

### `data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md`
- Lines: 101
- Headings: ## Index | ## Evidence matrix | ## Verdict | ## Limitations and interpretation
- Evidence text: | artifact_id                     | group_name              | unit_of_analysis | n_valid | principal_result                                                       | status      |
- Evidence text: | cross_evidence_correlations      | source_churn           | global           | null    | Global correlation is inconclusive or does not support the expected direction. | inconclusive |
- Evidence text: | cross_evidence_correlations      | source_churn           | global           | null    | Global correlation is inconclusive or does not support the expected direction. | inconclusive |
- Evidence text: | cross_evidence_correlations      | temporal_escalation    | global           | null    | Supported global correlation with leave-one-out robustness.           | supports    |
- Evidence text: | cross_evidence_correlations      | evaluator_crossing     | global           | null    | Supported global correlation with leave-one-out robustness.           | supports    |

### `data/analysis/cross_evidence/reports/act_reports/act_1_evolutionary_ceiling.md`
- Lines: 11
- Headings: ## Act summary | ## Bound artifacts | ## Empirical status | ## Narrative interpretation
- Evidence text: ## Empirical status
- Evidence text: The aggregate status is classified as "limits." This is justified by the absence of support, tested, and weak evidence, as indicated by the artifact count being zero.
- Evidence text: The act is merely contextualized, as there is no supporting evidence or artifacts to substantiate its claims.

### `data/analysis/cross_evidence/reports/act_reports/act_2_planning_debt.md`
- Lines: 46
- Headings: ## Act summary | ## Bound artifacts | ## Empirical status | ## Narrative interpretation
- Evidence text: - **scope_vs_source_churn_t3**: inconclusive
- Evidence text: - **scope_vs_source_events_t3**: inconclusive
- Evidence text: - **scope_vs_pi_line_delta_t3**: supports
- Evidence text: - **scope_vs_planning_artifact_activity_t3**: supports
- Evidence text: - **scope_vs_planning_rework_t2_t3**: inconclusive

### `data/analysis/cross_evidence/reports/act_reports/act_3_human_factor.md`
- Lines: 87
- Headings: ## Act summary | ## Bound artifacts | ## Empirical status | ## Narrative interpretation
- Evidence text: - **scope_vs_source_churn_t3**: inconclusive
- Evidence text: - **scope_vs_source_events_t3**: inconclusive
- Evidence text: - **scope_vs_pi_line_delta_t3**: supports
- Evidence text: - **scope_vs_planning_artifact_activity_t3**: supports
- Evidence text: - **scope_vs_planning_rework_t2_t3**: inconclusive

### `data/analysis/cross_evidence/reports/act_reports/act_4_value_inversion.md`
- Lines: 11
- Headings: ## Act summary | ## Bound artifacts | ## Empirical status | ## Narrative interpretation
- Evidence text: Act 4, titled "Ato 4 - A Inversao de Valores na Era da IA (Conclusion)," reframes the thesis toward cognitive clarity, explicit specifications, and sustainable AI-supported delivery.
- Evidence text: ## Empirical status
- Evidence text: The aggregate status is classified as "limits." This is justified by the absence of support, tested, and weak evidence, as indicated by the artifact count being zero.
- Evidence text: The act is merely contextualized, as there are no supporting artifacts to substantiate its claims.

### `data/analysis/cross_evidence/reports/artifact_reports/author_pressure_metrics.md`
- Lines: 28
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act present is 3, which is meant to support or qualify claims regarding author pressure metrics in software development.
- Evidence text: - **Author N**: Mean = 4.15, Max = 10.0, Min = 1.0, n_valid = 33
- Evidence text: - **Churn Lines**: Mean = 418034.67, Max = 11762127.0, Min = 2.0, n_valid = 33
- Evidence text: - **Commit Gini**: Mean = 0.28, Max = 0.53, Min = 0.0, n_valid = 33
- Evidence text: - **Commit N**: Mean = 24.61, Max = 164.0, Min = 1.0, n_valid = 33

### `data/analysis/cross_evidence/reports/artifact_reports/author_pressure_vs_churn_data.md`
- Lines: 47
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act present is 3, which is meant to support or qualify claims regarding the relationship between author pressure and churn.
- Evidence text: The verdict on the contribution of this artifact is that it provides exploratory evidence regarding the relationship between author pressure and churn. This is justified by the presence of a complete dataset with 42 valid entries across multiple metrics.
- Evidence text: ## Known limitations
- Evidence text: - No specific limitations were listed in the fact sheet.

### `data/analysis/cross_evidence/reports/artifact_reports/best_worst_project_contrasts.md`
- Lines: 28
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: - **Claim or Caution Supported/Qualified**: The narrative acts are intended to support or qualify the interpretation of the results regarding the contrasts between project outcomes.
- Evidence text: - **p-values**: Not specified
- Evidence text: The verdict on the contribution of this artifact is unclear due to the lack of specific effect sizes and p-values. While the data provides a valid sample size of 24, the absence of detailed statistical significance limits the ability to draw strong conclusions.
- Evidence text: ## Known limitations
- Evidence text: - No specific effect sizes or p-values are provided.

### `data/analysis/cross_evidence/reports/artifact_reports/cross_evidence_correlations.md`
- Lines: 37
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2, 3, and 4. These acts are intended to support or qualify specific claims or cautions related to the findings of the correlations among the analysis results.
- Evidence text: - **P-values**:
- Evidence text: The verdict is not explicitly stated in the fact sheet. However, the data indicates a range of correlation coefficients and p-values, suggesting varying degrees of relationship strength and significance among the analysis results.
- Evidence text: ## Known limitations
- Evidence text: - No specific limitations are listed in the fact sheet.

### `data/analysis/cross_evidence/reports/artifact_reports/cross_evidence_manifest.md`
- Lines: 26
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 1, 2, 3, and 4. These acts are intended to support or qualify various claims or cautions, although specific claims or cautions are not detailed in the fact sheet.
- Evidence text: - **p-values**: Not specified
- Evidence text: The verdict on the contribution of this artifact is that it is partial. This is justified by the status being labeled as "partial" in the fact sheet.
- Evidence text: ## Known limitations
- Evidence text: - Limitations are not specified in the fact sheet.

### `data/analysis/cross_evidence/reports/artifact_reports/cross_evidence_manifest_exclusions.md`
- Lines: 30
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: 1. Act 1: Supports the need for caution in interpreting exploratory evidence.
- Evidence text: - **P-values**: Not specified
- Evidence text: The verdict on the contribution of this artifact is unclear due to the lack of specific quantitative data such as effect sizes, p-values, and valid sample sizes. The absence of these metrics limits the ability to assess the impact or significance of the findings.
- Evidence text: ## Known limitations
- Evidence text: - Limitations are not specified in the fact sheet.

### `data/analysis/cross_evidence/reports/artifact_reports/cross_evidence_panel.md`
- Lines: 28
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2, 3, and 4. These acts are intended to support or qualify claims regarding the performance and engagement of teams over time, as well as the relationship between technical complexity and project outcomes.
- Evidence text: - **cc_per_source_loc_t3**: Mean = 75.03, n_valid = 14
- Evidence text: - **cc_total_t3**: Mean = 964437.93, n_valid = 14
- Evidence text: - **commits_per_author_t3**: Mean = 7.57, n_valid = 14
- Evidence text: - **pi_line_delta_t3**: Mean = 10164.57, n_valid = 14

### `data/analysis/cross_evidence/reports/artifact_reports/evaluator_outcome_metrics.md`
- Lines: 29
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: - **Claim or Caution Supported/Qualified**: The specific claim or caution is not detailed in the fact sheet.
- Evidence text: - **Engagement Participation Mean (t1)**: Mean = 1.6875, n_valid = 14
- Evidence text: - **Scope Applicability Mean Delta (t1 to t2)**: Mean = 0.0565, n_valid = 14
- Evidence text: - **Scope Applicability Mean Delta (t1 to t3)**: Mean = 0.1607, n_valid = 14
- Evidence text: - **Scope Applicability Mean Delta (t2 to t3)**: Mean = 0.1042, n_valid = 14

### `data/analysis/cross_evidence/reports/artifact_reports/evidence_priority_matrix.md`
- Lines: 28
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts include 1, 2, 3, and 4. These acts are intended to support or qualify claims regarding the significance and applicability of the evidence presented in the matrix.
- Evidence text: - **Coefficient**: Mean = -0.5365907760412248, Median = -0.5544826240669376, Min = -0.7854963073359155, Max = -0.0594088525786004, n_valid = 35
- Evidence text: - **p-value**: Mean = 0.20694046832180646, Median = 0.1212991257224558, Min = 0.0031279384351483, Max = 0.8857142857142857, n_valid = 59
- Evidence text: - **Jaccard**: Mean = 0.2164021164021164, Median = 0.1428571428571428, Min = 0.0, Max = 0.6, n_valid = 18
- Evidence text: - **Overlap_n**: Mean = 1.2222222222222223, Median = 1.0, Min = 0.0, Max = 3.0, n_valid = 18

### `data/analysis/cross_evidence/reports/artifact_reports/extreme_case_overlap.md`
- Lines: 30
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2 and 3. These acts are meant to support or qualify claims regarding the relationships and overlaps between the defined groups in the analysis.
- Evidence text: - Jaccard: Mean = 0.2164, Max = 0.6, Median = 0.1429
- Evidence text: - Overlap N: Mean = 1.2222, Max = 3.0, Median = 1.0
- Evidence text: - Overlap Rate Left: Mean = 0.3056, Max = 0.75, Median = 0.25
- Evidence text: - Overlap Rate Right: Mean = 0.3056, Max = 0.75, Median = 0.25

### `data/analysis/cross_evidence/reports/artifact_reports/file_category_churn_by_cut_data.md`
- Lines: 70
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2 and 3. These acts are meant to support or qualify claims regarding the methodological warnings associated with the evidence presented in this artifact.
- Evidence text: The verdict on the contribution of this artifact is that it provides valuable exploratory evidence regarding file category churn. The data includes a range of metrics that can inform understanding of usage patterns, although it is categorized as secondary exploratory evidence.
- Evidence text: ## Known limitations

### `data/analysis/cross_evidence/reports/artifact_reports/file_category_churn_metrics.md`
- Lines: 30
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: - These acts are meant to support or qualify claims regarding the dynamics of file category churn and the associated metrics.
- Evidence text: - **Category Confidence Mean**: Mean = 0.901, n_valid = 158
- Evidence text: - **Category Event Share**: Mean = 0.209, n_valid = 158
- Evidence text: - **Category Warning Event N**: Mean = 66.861, n_valid = 158
- Evidence text: - **Churn Lines**: Mean = 87311.038, n_valid = 158

### `data/analysis/cross_evidence/reports/artifact_reports/late_instability_metrics.md`
- Lines: 29
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2, 3, and 4. These acts are intended to support or qualify claims regarding the relationship between planning rework signals, source churn, and overall team performance metrics.
- Evidence text: - **Commits per Author (Rank Percent)**: Mean = 0.5357, n_valid = 14
- Evidence text: - **Delta DT (Rank Percent)**: Mean = 0.5357, n_valid = 14
- Evidence text: - **Late Instability Component Available**: Mean = 7.0, n_valid = 14
- Evidence text: - **Late Instability Component Missing**: Mean = 0.0, n_valid = 14

### `data/analysis/cross_evidence/reports/artifact_reports/leave_one_out_robustness_data.md`
- Lines: 28
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2 and 3. These acts are intended to support or qualify claims regarding the robustness of the analysis results and the reliability of the coefficients derived from the data.
- Evidence text: - **Original Coefficient**: Mean = -0.5207027851032128, Max = -0.2647382010005621, Min = -0.7284815485795703, n_valid = 7
- Evidence text: - **Coefficient Min**: Mean = -0.6725534806053813, Max = -0.5699124492412846, Min = -0.7810117949610702, n_valid = 7
- Evidence text: - **Coefficient Max**: Mean = -0.43426754742467366, Max = -0.174630713288139, Min = -0.6725037594933305, n_valid = 7
- Evidence text: - **P-value Max**: Mean = 0.19260818765647383, Max = 0.5682629857514974, Min = 0.0117870367777658, n_valid = 7

### `data/analysis/cross_evidence/reports/artifact_reports/leave_one_out_sensitivity.md`
- Lines: 29
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The artifact was constructed using a script that processes cross-evidence data, specifically focusing on leave-one-out sensitivity analysis. It aggregates results from multiple analyses, capturing various metrics such as coefficients and p-values across a total of 7 rows of data.
- Evidence text: The narrative acts identified are 2 and 3. These acts are meant to support or qualify claims regarding the robustness and reliability of the analysis results.
- Evidence text: - **Original Coefficient**: Mean = -0.5207027851032128, Median = -0.5207396621025063, Min = -0.7284815485795703, Max = -0.2647382010005621
- Evidence text: - **Original P-Value**: Mean = 0.10340406311635783, Median = 0.056231526062027, Min = 0.0031279384351483, Max = 0.3603606340812801
- Evidence text: - **Leave-One-Out Unavailable N (loo_unavailable_n)**: 0

### `data/analysis/cross_evidence/reports/artifact_reports/pareto_extreme_cases_data.md`
- Lines: 28
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2 and 3. These acts are intended to support or qualify claims regarding the relationships between team performance metrics and their overlap in extreme cases.
- Evidence text: - **Group Size Requested**: Mean = 4.0, n_valid = 18
- Evidence text: - **Jaccard**: Mean = 0.2164, n_valid = 18
- Evidence text: - **Overlap N**: Mean = 1.2222, n_valid = 18
- Evidence text: - **Overlap Rate Left**: Mean = 0.3056, n_valid = 18

### `data/analysis/cross_evidence/reports/artifact_reports/scope_vs_late_instability_data.md`
- Lines: 28
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act present is 3, which is meant to support or qualify a specific claim or caution related to the evidence scope of secondary exploratory evidence.
- Evidence text: - **p-values**: Not specified
- Evidence text: The verdict on the contribution of this artifact is unclear due to the lack of specific effect sizes, p-values, and cross-evidence labels. The data provides a numeric summary but does not include sufficient statistical evidence to draw definitive conclusions.
- Evidence text: ## Known limitations
- Evidence text: - No p-values provided

### `data/analysis/cross_evidence/reports/artifact_reports/semester_stratified_results.md`
- Lines: 34
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2 and 3. These acts are meant to support or qualify claims regarding the methodological warnings associated with the evidence presented.
- Evidence text: - **p-values**:
- Evidence text: The verdict is not explicitly stated in the fact sheet. However, the data indicates a range of effect sizes and p-values, suggesting variability in the results. The presence of methodological warnings implies caution in interpreting the findings.
- Evidence text: ## Known limitations
- Evidence text: - No specific limitations were listed in the fact sheet.

### `data/analysis/cross_evidence/reports/artifact_reports/source_churn_vs_planning_rework_data.md`
- Lines: 27
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative act present is 2, which is meant to support or qualify claims regarding the relationship between source churn and planning rework.
- Evidence text: - **p-values**: Not specified
- Evidence text: The verdict on the contribution of this artifact is unclear due to the lack of specific effect sizes and p-values. While the dataset is complete with 14 valid entries, the absence of statistical significance measures limits the ability to draw definitive conclusions.
- Evidence text: ## Known limitations
- Evidence text: - No effect sizes or p-values provided.

### `data/analysis/cross_evidence/reports/artifact_reports/temporal_escalation_metrics.md`
- Lines: 29
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2, 3, and 4. These acts are intended to support or qualify claims regarding the temporal escalation of metrics over time.
- Evidence text: - **P-values**: Not provided.
- Evidence text: The verdict on the contribution of this artifact is unclear due to the lack of p-values and specific cross-evidence labels. The available data provides some effect sizes, but without statistical significance, the implications of these findings remain uncertain.
- Evidence text: ## Known limitations
- Evidence text: - No p-values are provided, limiting the ability to assess statistical significance.

### `data/analysis/cross_evidence/reports/artifact_reports/temporal_escalation_panel_data.md`
- Lines: 28
- Headings: ## What it is | ## How it was built | ## Narrative binding | ## What the current data actually shows | ## Contribution assessment | ## Known limitations
- Evidence text: The narrative acts identified are 2 and 3. These acts are meant to support or qualify claims regarding the exploratory nature of the evidence and its relevance as a primary candidate for further analysis.
- Evidence text: - **Baseline T1**: Mean = 684.30, Median = 3.62, Min = 1.58, Max = 6360.00, n_valid = 54
- Evidence text: - **n_valid**: Mean = 9.33, Median = 9.00, Min = 5.00, Max = 14.00, n_valid = 54
- Evidence text: - **Semester**: Mean = 2025.65, Median = 2025.65, Min = 2025.20, Max = 2026.10, n_valid = 36
- Evidence text: - **Value Raw**: Mean = 47606.23, Median = 16.88, Min = 1.53, Max = 1485854.33, n_valid = 54

### `data/analysis/cross_evidence/reports/group_reports/author_pressure.md`
- Lines: 13
- Headings: ## Group summary | ## Member artifacts | ## Evidence status | ## Role in the narrative
- Evidence text: - **Status**: Candidate Secondary
- Evidence text: - **Contribution**: Provides exploratory group-level support through a best/worst contrast analysis, indicating a relationship between author pressure and project instability.
- Evidence text: ## Evidence status
- Evidence text: The group mainly supports the narrative, as indicated by the aggregate numbers showing 1 supporting verdict and no limiting or contextualizing evidence.
- Evidence text: The evidence strengthens the act-level argument by providing supportive insights into how author pressure can affect software project outcomes, thereby reinforcing the overall thesis.

### `data/analysis/cross_evidence/reports/group_reports/evaluator_crossing.md`
- Lines: 117
- Headings: ## Group summary | ## Member artifacts | ## Evidence status | ## Role in the narrative
- Evidence text: - **Status**: Supports
- Evidence text: - **Status**: Supports
- Evidence text: - **Status**: Inconclusive
- Evidence text: - **Contribution**: Indicates a fragile correlation that does not support the expected direction.
- Evidence text: - **Status**: Inconclusive

### `data/analysis/cross_evidence/reports/group_reports/methodological_warnings.md`
- Lines: 17
- Headings: ## Group summary | ## Member artifacts | ## Evidence status | ## Role in the narrative
- Evidence text: The 'methodological_warnings' group measures the potential limitations and considerations in the methodologies used within the research. It focuses on identifying aspects that may affect the reliability and validity of the findings, providing insights into the robustness of the conclusions drawn.
- Evidence text: - **Status:** supports
- Evidence text: - **Contribution:** Provides exploratory group-level support through a best/worst contrast analysis.
- Evidence text: - **Status:** supports
- Evidence text: - **Contribution:** Also provides exploratory group-level support via a best/worst contrast analysis.

### `data/analysis/cross_evidence/reports/group_reports/robustness.md`
- Lines: 11
- Headings: ## Group summary | ## Member artifacts | ## Evidence status | ## Role in the narrative
- Evidence text: ## Evidence status
- Evidence text: The group mainly limits the narrative, as there are no artifacts or evidence to support claims regarding robustness.

### `data/analysis/cross_evidence/reports/group_reports/source_churn.md`
- Lines: 73
- Headings: ## Group summary | ## Member artifacts | ## Evidence status | ## Role in the narrative
- Evidence text: The 'source_churn' group measures the relationship between source code churn and various software engineering metrics. It aims to explore how changes in the source code correlate with project outcomes, but the evidence gathered is primarily exploratory and inconclusive.
- Evidence text: - **Status**: Inconclusive
- Evidence text: - **Contribution**: Indicates a fragile correlation that does not support the expected direction.
- Evidence text: - **Status**: Inconclusive
- Evidence text: - **Contribution**: Suggests a fragile correlation that does not support the expected direction.

### `data/analysis/cross_evidence/reports/group_reports/temporal_escalation.md`
- Lines: 109
- Headings: ## Group summary | ## Member artifacts | ## Evidence status | ## Role in the narrative
- Evidence text: - **Status**: Supports
- Evidence text: - **Status**: Inconclusive
- Evidence text: - **Contribution**: Suggests a potential relationship between scope and planning rework, but the evidence is fragile and inconclusive.
- Evidence text: - **Status**: Inconclusive
- Evidence text: - **Contribution**: Offers an exploratory contrast that lacks statistical support.

## Cross-Evidence Structured Checks

### `data/analysis/cross_evidence/cross_evidence_manifest.json`
- Manifest artifacts: 27
- Keys: artifacts, contract_version, input_checksum, manifest_version, missing_artifacts, producer_script, scope, status

### `data/analysis/cross_evidence/cross_evidence_manifest.json.metadata.json`
- Keys: contract_version, input_checksum, options, status

### `data/analysis/cross_evidence/cross_evidence_manifest_exclusions.json`
- Exclusion: `{'dataset': 'file_category_churn_metrics', 'reason': 'unknown_file_category', 'n_affected_events': 1436, 'n_affected_rows': 30}`
- Exclusion: `{'dataset': 'file_category_churn_metrics', 'reason': 'missing_line_counts', 'n_affected_events': 14287, 'n_affected_rows': 67}`
- Exclusion: `{'dataset': 'file_category_churn_metrics', 'reason': 'category_warnings', 'n_affected_events': 10564, 'n_affected_rows': 33}`
- Exclusion: `{'dataset': 'file_category_churn_metrics', 'reason': 'low_confidence_categories', 'n_affected_events': 26567, 'n_affected_rows': 35}`
- Keys: contract_version, exclusions, file_category_definition_version, input_checksum, options, schema_version, scope, sources, status, summary

### `data/analysis/cross_evidence/cross_evidence_manifest_exclusions.json.metadata.json`
- Keys: contract_version, input_checksum, options, status

### `data/analysis/cross_evidence/figure_data/author_pressure_vs_churn.manifest.json`
- Keys: anonymization_policy, category, checksums, data_metadata_path, data_path, dimensions, export_formats, figure_id, interactive_path, limitations, n_missing, n_total, n_valid, plotly_trace_n, priority, scale_notes, source, static_paths, status, theme, transformations, unit_of_analysis, variables, visual_spec_version

### `data/analysis/cross_evidence/figure_data/file_category_churn_by_cut.manifest.json`
- Keys: anonymization_policy, category, checksums, data_metadata_path, data_path, dimensions, export_formats, figure_id, interactive_path, limitations, n_missing, n_total, n_valid, plotly_trace_n, priority, scale_notes, source, static_paths, status, theme, transformations, unit_of_analysis, variables, visual_spec_version

### `data/analysis/cross_evidence/figure_data/leave_one_out_robustness.manifest.json`
- Keys: anonymization_policy, category, checksums, data_metadata_path, data_path, dimensions, export_formats, figure_id, interactive_path, limitations, n_missing, n_total, n_valid, plotly_trace_n, priority, scale_notes, source, static_paths, status, theme, transformations, unit_of_analysis, variables, visual_spec_version

### `data/analysis/cross_evidence/figure_data/pareto_extreme_cases.manifest.json`
- Keys: anonymization_policy, category, checksums, data_metadata_path, data_path, dimensions, export_formats, figure_id, interactive_path, limitations, n_missing, n_total, n_valid, plotly_trace_n, priority, scale_notes, source, static_paths, status, theme, transformations, unit_of_analysis, variables, visual_spec_version

### `data/analysis/cross_evidence/figure_data/scope_vs_late_instability.manifest.json`
- Keys: anonymization_policy, category, checksums, data_metadata_path, data_path, dimensions, export_formats, figure_id, interactive_path, limitations, n_missing, n_total, n_valid, plotly_trace_n, priority, scale_notes, source, static_paths, status, theme, transformations, unit_of_analysis, variables, visual_spec_version

### `data/analysis/cross_evidence/figure_data/source_churn_vs_planning_rework.manifest.json`
- Keys: anonymization_policy, category, checksums, data_metadata_path, data_path, dimensions, export_formats, figure_id, interactive_path, limitations, n_missing, n_total, n_valid, plotly_trace_n, priority, scale_notes, source, static_paths, status, theme, transformations, unit_of_analysis, variables, visual_spec_version

### `data/analysis/cross_evidence/figure_data/temporal_escalation_panel.manifest.json`
- Keys: anonymization_policy, category, checksums, data_metadata_path, data_path, dimensions, export_formats, figure_id, interactive_path, limitations, n_missing, n_total, n_valid, plotly_trace_n, priority, scale_notes, source, static_paths, status, theme, transformations, unit_of_analysis, variables, visual_spec_version

### `data/analysis/cross_evidence/reports/artifact_reports/cross_evidence_manifest.md.metadata.json`
- Keys: contract_version, input_checksum, options, status

### `data/analysis/cross_evidence/reports/artifact_reports/cross_evidence_manifest_exclusions.md.metadata.json`
- Keys: contract_version, input_checksum, options, status

### `data/analysis/cross_evidence/results/best_worst_project_contrasts.csv`
- Rows: 24
- status: `{'success': 24}`
- reason: `{'<empty>': 24}`
- p-values: scope_applicability_mean_t3__planning_rework_signal_t2_t3__top_bottom_4: 0.19126698687886878, scope_applicability_mean_t3__planning_artifact_activity_t3__top_bottom_4: 0.19126698687886878, scope_applicability_mean_t3__pi_line_delta_t3__top_bottom_4: 0.05714285714285714, scope_applicability_mean_t3__source_churn_t3__top_bottom_4: 0.6857142857142857, scope_applicability_mean_t3__source_events_t3__top_bottom_4: 0.4857142857142857, scope_applicability_mean_t3__commits_per_author_t3__top_bottom_4: 0.02857142857142857, scope_applicability_mean_t3__late_instability_index__top_bottom_4: 0.34285714285714286, scope_applicability_mean_t3__scope_applicability_mean_t3__top_bottom_4: 0.020208004239389277, project_progress_mean_t3__planning_rework_signal_t2_t3__top_bottom_4: 0.8857142857142857, project_progress_mean_t3__planning_artifact_activity_t3__top_bottom_4: 0.6857142857142857, project_progress_mean_t3__pi_line_delta_t3__top_bottom_4: 0.11428571428571428, project_progress_mean_t3__source_churn_t3__top_bottom_4: 0.8857142857142857, project_progress_mean_t3__source_events_t3__top_bottom_4: 0.6857142857142857, project_progress_mean_t3__commits_per_author_t3__top_bottom_4: 0.05714285714285714, project_progress_mean_t3__late_instability_index__top_bottom_4: 0.6857142857142857, project_progress_mean_t3__scope_applicability_mean_t3__top_bottom_4: 0.020208004239389277, late_instability_index__planning_rework_signal_t2_t3__top_bottom_4: 0.02857142857142857, late_instability_index__planning_artifact_activity_t3__top_bottom_4: 0.02857142857142857, late_instability_index__pi_line_delta_t3__top_bottom_4: 0.02857142857142857, late_instability_index__source_churn_t3__top_bottom_4: 0.02857142857142857, late_instability_index__source_events_t3__top_bottom_4: 0.02857142857142857, late_instability_index__commits_per_author_t3__top_bottom_4: 0.029401048190339642, late_instability_index__late_instability_index__top_bottom_4: 0.02857142857142857, late_instability_index__scope_applicability_mean_t3__top_bottom_4: 0.18587673236587587

### `data/analysis/cross_evidence/results/cross_evidence_correlations.csv`
- Rows: 7
- status: `{'success': 7}`
- verdict: `{'inconclusive': 4, 'supports': 3}`
- priority: `{'primary_candidate': 6, 'secondary_support': 1}`
- reason: `{'<empty>': 7}`
- p-values: scope_vs_source_churn_t3: 0.36036063408128016, scope_vs_source_events_t3: 0.20814701862164176, scope_vs_pi_line_delta_t3: 0.00826262593762888, scope_vs_planning_artifact_activity_t3: 0.0286037847926583, scope_vs_planning_rework_t2_t3: 0.056231526062027005, scope_vs_commits_per_author_t3: 0.0031279384351483347, scope_vs_late_instability_index: 0.05909491388412068

### `data/analysis/cross_evidence/results/evidence_priority_matrix.csv`
- Rows: 77
- verdict: `{'inconclusive': 49, 'supports': 28}`
- priority: `{'primary_candidate': 24, 'secondary_support': 4, '<empty>': 49}`
- p-values: scope_vs_source_churn_t3: 0.3603606340812801, scope_vs_source_events_t3: 0.2081470186216417, scope_vs_pi_line_delta_t3: 0.0082626259376288, scope_vs_planning_artifact_activity_t3: 0.0286037847926583, scope_vs_planning_rework_t2_t3: 0.056231526062027, scope_vs_commits_per_author_t3: 0.0031279384351483, scope_vs_late_instability_index: 0.0590949138841206, scope_applicability_mean_t3__planning_rework_signal_t2_t3__top_bottom_4: 0.1912669868788687, scope_applicability_mean_t3__planning_artifact_activity_t3__top_bottom_4: 0.1912669868788687, scope_applicability_mean_t3__pi_line_delta_t3__top_bottom_4: 0.0571428571428571, scope_applicability_mean_t3__source_churn_t3__top_bottom_4: 0.6857142857142857, scope_applicability_mean_t3__source_events_t3__top_bottom_4: 0.4857142857142857, scope_applicability_mean_t3__commits_per_author_t3__top_bottom_4: 0.0285714285714285, scope_applicability_mean_t3__late_instability_index__top_bottom_4: 0.3428571428571428, scope_applicability_mean_t3__scope_applicability_mean_t3__top_bottom_4: 0.0202080042393892, project_progress_mean_t3__planning_rework_signal_t2_t3__top_bottom_4: 0.8857142857142857, project_progress_mean_t3__planning_artifact_activity_t3__top_bottom_4: 0.6857142857142857, project_progress_mean_t3__pi_line_delta_t3__top_bottom_4: 0.1142857142857142, project_progress_mean_t3__source_churn_t3__top_bottom_4: 0.8857142857142857, project_progress_mean_t3__source_events_t3__top_bottom_4: 0.6857142857142857, project_progress_mean_t3__commits_per_author_t3__top_bottom_4: 0.0571428571428571, project_progress_mean_t3__late_instability_index__top_bottom_4: 0.6857142857142857, project_progress_mean_t3__scope_applicability_mean_t3__top_bottom_4: 0.0202080042393892, late_instability_index__planning_rework_signal_t2_t3__top_bottom_4: 0.0285714285714285, late_instability_index__planning_artifact_activity_t3__top_bottom_4: 0.0285714285714285, late_instability_index__pi_line_delta_t3__top_bottom_4: 0.0285714285714285, late_instability_index__source_churn_t3__top_bottom_4: 0.0285714285714285, late_instability_index__source_events_t3__top_bottom_4: 0.0285714285714285, late_instability_index__commits_per_author_t3__top_bottom_4: 0.0294010481903396, late_instability_index__late_instability_index__top_bottom_4: 0.0285714285714285, late_instability_index__scope_applicability_mean_t3__top_bottom_4: 0.1858767323658758, scope_vs_source_churn_t3: 0.3603606340812801, scope_vs_source_events_t3: 0.2081470186216417, scope_vs_pi_line_delta_t3: 0.0082626259376288, scope_vs_planning_artifact_activity_t3: 0.0286037847926583, scope_vs_planning_rework_t2_t3: 0.056231526062027, scope_vs_commits_per_author_t3: 0.0031279384351483, scope_vs_late_instability_index: 0.0590949138841206, scope_vs_source_churn_t3: 0.3603606340812801, scope_vs_source_churn_t3: 0.8793286751743332, scope_vs_source_churn_t3: 0.1816901138162092, scope_vs_source_events_t3: 0.2081470186216417, scope_vs_source_events_t3: 0.4701450823117139, scope_vs_source_events_t3: 0.1816901138162092, scope_vs_pi_line_delta_t3: 0.0082626259376288, scope_vs_pi_line_delta_t3: 0.1212991257224558, scope_vs_pi_line_delta_t3: 0.1816901138162092, scope_vs_planning_artifact_activity_t3: 0.0286037847926583, scope_vs_planning_artifact_activity_t3: 0.1468958994862416, scope_vs_planning_artifact_activity_t3: 0.1816901138162092, scope_vs_planning_rework_t2_t3: 0.056231526062027, scope_vs_planning_rework_t2_t3: 0.289117458517315, scope_vs_planning_rework_t2_t3: 0.1816901138162092, scope_vs_commits_per_author_t3: 0.0031279384351483, scope_vs_commits_per_author_t3: 0.0121154159883211, scope_vs_commits_per_author_t3: 0.1816901138162092, scope_vs_late_instability_index: 0.0590949138841206, scope_vs_late_instability_index: 0.4376135174079198, scope_vs_late_instability_index: 0.1816901138162092

### `data/analysis/cross_evidence/results/extreme_case_overlap.csv`
- Rows: 18

### `data/analysis/cross_evidence/results/leave_one_out_sensitivity.csv`
- Rows: 7
- priority: `{'primary_candidate': 6, 'secondary_support': 1}`

### `data/analysis/cross_evidence/results/semester_stratified_results.csv`
- Rows: 21
- status: `{'success': 21}`
- verdict: `{'inconclusive': 17, 'supports': 4}`
- priority: `{'primary_candidate': 18, 'secondary_support': 3}`
- reason: `{'<empty>': 21}`
- p-values: scope_vs_source_churn_t3: 0.36036063408128016, scope_vs_source_churn_t3: 0.8793286751743332, scope_vs_source_churn_t3: 0.18169011381620928, scope_vs_source_events_t3: 0.20814701862164176, scope_vs_source_events_t3: 0.4701450823117139, scope_vs_source_events_t3: 0.18169011381620928, scope_vs_pi_line_delta_t3: 0.00826262593762888, scope_vs_pi_line_delta_t3: 0.12129912572245584, scope_vs_pi_line_delta_t3: 0.18169011381620928, scope_vs_planning_artifact_activity_t3: 0.0286037847926583, scope_vs_planning_artifact_activity_t3: 0.14689589948624163, scope_vs_planning_artifact_activity_t3: 0.18169011381620928, scope_vs_planning_rework_t2_t3: 0.056231526062027005, scope_vs_planning_rework_t2_t3: 0.289117458517315, scope_vs_planning_rework_t2_t3: 0.18169011381620928, scope_vs_commits_per_author_t3: 0.0031279384351483347, scope_vs_commits_per_author_t3: 0.012115415988321164, scope_vs_commits_per_author_t3: 0.18169011381620928, scope_vs_late_instability_index: 0.05909491388412068, scope_vs_late_instability_index: 0.43761351740791987, scope_vs_late_instability_index: 0.18169011381620928

## Parquet Verification Index

- `data/analysis/.private/llm_call_ledger.parquet`: rows=392; key columns=call_id, observation_id; columns=25.
- `data/analysis/.private/student_prompt_catalog.parquet`: rows=1122; key columns=student_response_id, Semestre, temporal_marker, question_id; columns=11.
- `data/analysis/code_churn_metrics.parquet`: rows=14; key columns=ID_Equipe, Semestre; columns=73.
- `data/analysis/cross_evidence/datasets/author_pressure_metrics.parquet`: rows=33; key columns=ID_Equipe, Semestre, temporal_marker; columns=19.
- `data/analysis/cross_evidence/datasets/cross_evidence_panel.parquet`: rows=14; key columns=ID_Equipe, Semestre; columns=47.
- `data/analysis/cross_evidence/datasets/evaluator_outcome_metrics.parquet`: rows=14; key columns=ID_Equipe, Semestre; columns=84.
- `data/analysis/cross_evidence/datasets/file_category_churn_metrics.parquet`: rows=158; key columns=ID_Equipe, Semestre, temporal_marker; columns=23.
- `data/analysis/cross_evidence/datasets/late_instability_metrics.parquet`: rows=14; key columns=ID_Equipe, Semestre; columns=27.
- `data/analysis/cross_evidence/datasets/temporal_escalation_metrics.parquet`: rows=5; key columns=metric_id, unit_of_analysis; columns=62.
- `data/analysis/cut_context_metrics.parquet`: rows=6; key columns=Semestre, temporal_marker, unit_of_analysis; columns=355.
- `data/analysis/integration_friction_metrics.parquet`: rows=14; key columns=ID_Equipe, Semestre; columns=61.
- `data/analysis/planning_metrics.parquet`: rows=14; key columns=ID_Equipe, Semestre; columns=28.
- `data/analysis/student_nlp.parquet`: rows=1122; key columns=student_response_id, Semestre, temporal_marker, question_id, unit_of_analysis; columns=15.
- `data/analysis/team_metrics.parquet`: rows=14; key columns=ID_Equipe, Semestre, unit_of_analysis; columns=183.
- `data/analysis/technical_degradation_metrics.parquet`: rows=14; key columns=ID_Equipe, Semestre; columns=24.
- `data/analysis/textual_cut_signals.parquet`: rows=6; key columns=Semestre, temporal_marker, unit_of_analysis; columns=349.
- `data/analysis/transcript_nlp.parquet`: rows=100; key columns=session_id, Semestre, temporal_marker, unit_of_analysis; columns=16.

## Required Reconciliations for Paper Writing

1. Treat the Phase 2.5 artifact, act, and consolidated reports as the authoritative interpretive index, while checking every quoted number against its persisted source.
2. Keep the current Phase 2.5 boundary visible: team-semester n=14, five tested primary analyses, no significant primary result, and conditional-go.
3. Treat cross-evidence supporting results as exploratory candidates, not confirmation. Record inconclusive results, fragile leave-one-out behavior, and methodological warnings next to every favorable claim.
4. Do not merge team-semester, team-semester-cut, category, student-response, and transcript-session units into one denominator.
5. Do not infer causality or SDD superiority from plots, correlations, contrasts, or extreme-case overlap.
6. Preserve unknown-file-category exclusions and any privacy/anonymization constraints in the data book and threats-to-validity record.
7. Any new derived analysis must be isolated in a separate script, documented, and explicitly authorized before execution; Phase 2 artifacts remain unchanged.

## Intended Phase 3 Use

This inventory feeds the data book, argument matrix, plot book, four act packages, literature map, threats-to-validity record, and IMRaD manuscript outline. It is an inventory and reconciliation aid, not a replacement for the canonical artifacts or the Phase 2.5 narrative reports.
