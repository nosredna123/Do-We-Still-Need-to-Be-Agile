# Phase 3 Data Book

This document is the paper-facing evidence register for Phase 3. It treats [phase3_evidence_inventory.md](phase3_evidence_inventory.md) as the initial inventory and verifies each claim against the persisted Phase 2.5 reports, the canonical structured sources, and the relevant figure manifests before it is allowed to support writing.

## Scope and use

- Source-of-truth policy: Phase 2.5 Markdown reports remain the primary interpretive layer; they are not the only evidence layer.
- Verification policy: every number used in the manuscript must be traceable from this data book to a persisted Parquet/CSV/JSON/manifest and, when relevant, to the Phase 2.5 report that frames it.
- Writing boundary: the dataset supports descriptive and exploratory claims. It does not provide confirmatory support for a causal superiority claim, and it does not establish SDD/BDUF as experimentally proven.

## Canonical evidence inventory

- Phase 2.5 audit: [../artifact_reports/00_consolidated_audit.md](../artifact_reports/00_consolidated_audit.md)
- Phase 3 inventory: [phase3_evidence_inventory.md](phase3_evidence_inventory.md)
- Statistical manifest: [../statistical_dataset_manifest.json](../statistical_dataset_manifest.json)
- Figure manifest: [../figure_manifest.json](../figure_manifest.json)
- Cross-evidence consolidated report: [../cross_evidence/reports/00_cross_evidence_consolidated_report.md](../cross_evidence/reports/00_cross_evidence_consolidated_report.md)

## Entry schema used below

For each evidence object, the table records:

- artifact path and sidecar path;
- producer script / contract version;
- unit of analysis and observation key;
- row count, unique-key count, coverage, and missingness;
- exact variables and transformations used in the paper;
- numerator/denominator and aggregation rule where applicable;
- relevant exclusions and unavailable reasons;
- the supported narrative act and paper section;
- the strongest statement the artifact permits;
- the statement it does not permit;
- status and evidence layer;
- reconciliation status.

---

## 1) Dataset entries

### Entry 1: team_metrics.parquet

- Artifact path: [../team_metrics.parquet](../team_metrics.parquet)
- Sidecar path: [../team_metrics.parquet.metadata.json](../team_metrics.parquet.metadata.json)
- Producer contract: `team-metrics-v1` (metadata: `contract_version: team-metrics-v1`)
- Unit of analysis: `team_semester`
- Observation key: `ID_Equipe` + `Semestre`
- Row count / unique-key count: 14 rows, 14 unique keys (n = 14)
- Coverage: semesters observed in both `2025.2` and `2026.1`; cross-cut metrics recorded across T1/T2/T3
- Missingness: metadata indicates no missing values for primary team key variables; IE was excluded from team metrics and sourced from the cut-context dataset (`ie_policy: excluded_from_team_metrics; source_is_cut_context`)
- Exact variables for paper use: `pi_file_count_t1`, `cc_per_source_loc_t3`, `delta_dt_t1_t3`, `ai_max_author_share_before_t3_window`, `cc_total_t3`, `ai_gini`, etc.
- Numerator / denominator / aggregation rule: complete-case pair analyses; no causal aggregation beyond cross-cut observational summaries
- Exclusions / unavailable reasons: IE variables intentionally excluded from this dataset; source-of-truth for IE remains `cut_context_metrics.parquet`
- Supported act and section: Act 2 (planning debt) and Act 3 (human factor), especially Results and Discussion
- Strongest permitted statement: "At the team-semester level, the currently observed correlations and group comparisons are non-significant or inconclusive, with conditional-go status rather than proof of a strong planning-debt effect."
- Not permitted: "There is a confirmed relationship between planning activity and churn/technical degradation." or "AI author concentration caused later churn."
- Status: `observed` / `interpretive` (dataset is observed; interpretation is bounded by test results)
- Evidence layer: `structured_source`
- Reconciliation status: `qualified`

### Entry 2: planning_metrics.parquet

- Artifact path: [../planning_metrics.parquet](../planning_metrics.parquet)
- Sidecar path: [../planning_metrics.parquet.metadata.json](../planning_metrics.parquet.metadata.json)
- Producer contract: `planning-metrics-v1`
- Unit of analysis: `team_semester`
- Observation key: `ID_Equipe` + `Semestre` or equivalent temporal team observation
- Row count / unique-key count: available in persisted metadata; the paper-facing reading is based on 14 team-semester observations in the primary analyses
- Coverage: planning activity metrics across the configured planning file extensions and path patterns; `pi_definition_version: pi-v1`
- Missingness: no primary missingness signal in the article-level audit; exact missing patterns should be checked in the source before quoting
- Exact variables for paper use: `pi_binary_event_count_t3`, `pi_deleted_count_t3`, `pi_file_count_t1`, `pi_line_delta_t1`, and related planning-status counts
- Numerator / denominator / aggregation rule: planning artifact counts and deltas by team-semester and temporal windows; no inferential claim is licensed without the exact test and denominators
- Exclusions / unavailable reasons: no primary test result supports a confirmatory statement; any planning metrics can only support descriptive characterization
- Supported act and section: Act 2, Results / planning debt
- Strongest permitted statement: "Planning artifacts are available as a descriptive indicator of planning activity, but the current evidence does not show a statistically supported effect in the primary tests."
- Not permitted: "High planning intensity causes lower technical degradation, lower churn, or better outcomes."
- Status: `observed`
- Evidence layer: `structured_source`
- Reconciliation status: `qualified`

### Entry 3: code_churn_metrics.parquet

- Artifact path: [../code_churn_metrics.parquet](../code_churn_metrics.parquet)
- Sidecar path: [../code_churn_metrics.parquet.metadata.json](../code_churn_metrics.parquet.metadata.json)
- Producer contract: `code-churn-metrics-v1`
- Unit of analysis: `team_semester` (with temporal windows and event counts)
- Observation key: team-semester and temporal marker / change windows
- Row count / unique-key count: the persisted artifact is a structured source that is read via the report chain; exact counts must be confirmed in source before use in prose
- Coverage: `cc_definition_version: cc-v1`; binary file events counted as events, but not included in line churn counts
- Missingness: code-churn definitions include `cc_binary_policy: excluded_from_line_churn_counted_as_events`
- Exact variables for paper use: `cc_binary_file_events_t2`, `cc_commit_churn_n_missing_t3`, `cc_commit_churn_n_total_t3`, `cc_commit_churn_n_valid_t3`, and related churn totals after temporal aggregation
- Numerator / denominator / aggregation rule: churn volumes are observed as event counts and normalized counts by team-semester; the exact denominator should be used once the relevant source frame is selected
- Exclusions / unavailable reasons: binary-file events are counted as events but not treated as line-churn; keep this distinct from report summaries that may conflate the two
- Supported act and section: Act 2, Results / planning debt and rework
- Strongest permitted statement: "Churn is observable in the team-semester dataset and can be described by the coding-time window, but the present evidence does not provide significant support for a directionally specific planning-debt claim."
- Not permitted: "The churn distribution itself confirms planning debt or causal rework."
- Status: `observed`
- Evidence layer: `structured_source`
- Reconciliation status: `qualified`

### Entry 4: technical_degradation_metrics.parquet

- Artifact path: [../technical_degradation_metrics.parquet](../technical_degradation_metrics.parquet)
- Sidecar path: [../technical_degradation_metrics.parquet.metadata.json](../technical_degradation_metrics.parquet.metadata.json)
- Producer contract: `technical-degradation-metrics-v1`
- Unit of analysis: `team_semester`
- Observation key: team-semester and temporal cut
- Row count / unique-key count: 14 primary team-semester observations across reported windows
- Coverage: `technical_complexity_mean`, `delta_dt_t1_t2`, `delta_dt_t2_t3`, etc.
- Missingness: `availability_policy: fail_if_any_cut_missing`
- Exact variables for paper use: `delta_dt_t1_t3`, `technical_complexity_mean_t1`, `technical_complexity_mean_t2`, etc.
- Numerator / denominator / aggregation rule: temporal delta and complexity measures computed by team-semester time-slices; descriptive summaries only unless separate inferential claims are verified
- Exclusions / unavailable reasons: no primary inferential support from the audit; descriptive time patterns can be shown but not causalized
- Supported act and section: Act 2, Results / planning debt and rework
- Strongest permitted statement: "The technical-degradation metrics provide a descriptive profile of complexity and change across the observed windows, but no primary significant association is supported in this dataset."
- Not permitted: "Technical degradation is proven to escalate because of planning debt."
- Status: `observed`
- Evidence layer: `structured_source`
- Reconciliation status: `qualified`

### Entry 5: integration_friction_metrics.parquet

- Artifact path: [../integration_friction_metrics.parquet](../integration_friction_metrics.parquet)
- Sidecar path: [../integration_friction_metrics.parquet.metadata.json](../integration_friction_metrics.parquet.metadata.json)
- Producer contract: `integration-friction-metrics-v1`
- Unit of analysis: `team_semester` and review-window based AI author concentration signals
- Observation key: team-semester window + author-share decomposition
- Row count / unique-key count: 14 team-semester observations in the primary AI author concentration analysis
- Coverage: AI author share distribution across `ai_author_share_*` metrics; `ai_t3_window_hours: 72`
- Missingness: values can be absent in the pre-T3 window when AI-activity data is unavailable; the metadata explicitly notes the `ai_ref_required_fields` contract
- Exact variables for paper use: `ai_author_n_before_t3_window`, `ai_author_share_n_missing_t2`, `ai_author_share_n_missing_t3`, `ai_author_share_n_valid_before_t3_window`, and associated share distributions
- Numerator / denominator / aggregation rule: per-author commit share measured within the AI window; the expected denominator is commit share, not repository- or transcript-level volume
- Exclusions / unavailable reasons: available AI-window observations only; partial missingness matters to interpretation and figure caption wording
- Supported act and section: Act 3, Results / human factor and integration friction
- Strongest permitted statement: "AI author concentration is a measurable operational signal in the available subset, but the observed dataset does not establish a significant relationship to the tested outcomes."
- Not permitted: "Author concentration is the causal driver of churn or degradation."
- Status: `observed`
- Evidence layer: `structured_source`
- Reconciliation status: `qualified`

### Entry 6: cut_context_metrics.parquet

- Artifact path: [../cut_context_metrics.parquet](../cut_context_metrics.parquet)
- Sidecar path: [../cut_context_metrics.parquet.metadata.json](../cut_context_metrics.parquet.metadata.json)
- Producer contract: `cut-context-metrics-v1` (from the project’s analysis contract; exact version to be checked in metadata before use)
- Unit of analysis: `cut_context`
- Observation key: `Semestre` + `temporal_marker`
- Row count / unique-key count: 6 rows, 6 unique keys
- Coverage: semesters `2025.2` and `2026.1` across temporal markers T1/T2/T3; transcript/context observations are sparse
- Missingness: strong missingness on transcript coordination/rework signals; 3 of 6 rows are effectively unavailable for the primary coordination test
- Exact variables for paper use: `ie_transcript_coordination_friction_score_mean`, `ie_transcript_rework_signal_score_mean`, and related transcript-based IE scores
- Numerator / denominator / aggregation rule: transcript-based score means and medians for the available cut-context observations; no combined denominator with team-semester metrics
- Exclusions / unavailable reasons: explicit `zero_variance` and `insufficient_group_n` conditions; `context_ie_temporal_primary` is unavailable due to zero variance / low valid n
- Supported act and section: Act 3, Results / integration and human factor evidence
- Strongest permitted statement: "The cut-context transcript evidence is sparse and partially unavailable; the current dataset permits only cautious descriptive reporting and cannot support a confirmatory coordination-stress claim."
- Not permitted: "Transcript coordination friction strongly predicts rework or divergent progress."
- Status: `observed`
- Evidence layer: `structured_source`
- Reconciliation status: `qualified`

### Entry 7: correlation_results.csv

- Artifact path: [../correlation_results.csv](../correlation_results.csv)
- Sidecar path: [../correlation_results.csv.metadata.json](../correlation_results.csv.metadata.json)
- Producer contract: `spearman-correlation-results-v1`
- Unit of analysis: `team_semester` or `cut_context` depending on row
- Observation key: `analysis_id`
- Row count / unique-key count: 4 rows (primary analyses only)
- Coverage: `pi_vs_cc_primary`, `pi_vs_delta_dt_primary`, `ai_vs_cc_primary`, `context_ie_temporal_primary`
- Missingness: `ai_vs_cc_primary` has 7 valid observations out of 14; `context_ie_temporal_primary` is unavailable due to zero variance and 3 missing rows
- Exact variables for paper use: `analysis_id`, `unit_of_analysis`, `x`, `y`, `test`, `n_total`, `n_valid`, `n_missing`, `coefficient`, `p_value`, `status`, `reason`, `warning`
- Numerator / denominator / aggregation rule: pairwise Spearman correlations by complete-case available pairs; no multi-test correction is reported for the primary family
- Exclusions / unavailable reasons: `warning: small_sample_n_lt_10`, `reason: zero_variance`, `status: unavailable`
- Supported act and section: Act 2 and Act 3, Results / observed relationships and null findings
- Strongest permitted statement: "All primary correlations are either non-significant or unavailable; the current evidence does not warrant a positive association claim."
- Not permitted: "The observed coefficient sign is evidence of a meaningful effect." or "The positively signed AI relation is confirmed."
- Status: `observed`
- Evidence layer: `structured_source`
- Reconciliation status: `consistent`

### Entry 8: hypothesis_results.csv

- Artifact path: [../hypothesis_results.csv](../hypothesis_results.csv)
- Sidecar path: [../hypothesis_results.csv.metadata.json](../hypothesis_results.csv.metadata.json)
- Producer contract: `mann-whitney-u-results-v1`
- Unit of analysis: `team_semester` or `cut_context`
- Observation key: `analysis_id`
- Row count / unique-key count: 3 rows
- Coverage: `pi_high_vs_low_cc_primary`, `ai_high_vs_low_cc_primary`, `context_ie_high_vs_low_rework_primary`
- Missingness: `ai_high_vs_low_cc_primary` has 7 valid observations out of 14; `context_ie_high_vs_low_rework_primary` is unavailable due to insufficient group n
- Exact variables for paper use: `u_statistic`, `p_value`, `n_group_low`, `n_group_high`, `n_valid`, `status`, `reason`, `interpretation`
- Numerator / denominator / aggregation rule: median-split comparisons by `split_median`; group labels are based on the observed variable split for high vs low conditions
- Exclusions / unavailable reasons: small-n warning and `insufficient_group_n` for the IE-related test
- Supported act and section: Act 2 and Act 3, Results / null and unavailable findings
- Strongest permitted statement: "The primary median-split comparisons remain inconclusive or unavailable; no treatment claim is supported by the current evidence."
- Not permitted: "A high-versus-low split demonstrates meaningful rework or churn differences."
- Status: `observed`
- Evidence layer: `structured_source`
- Reconciliation status: `consistent`

### Entry 9: statistical_dataset_manifest.json

- Artifact path: [../statistical_dataset_manifest.json](../statistical_dataset_manifest.json)
- Sidecar path: [../statistical_dataset_manifest_exclusions.json](../statistical_dataset_manifest_exclusions.json)
- Producer contract: `statistical-dataset-manifest-v1`
- Unit of analysis: multiple dataset-specific units (team-semester / cut-context)
- Observation key: dataset-specific observation keys, including team or cut context identifiers
- Row count / unique-key count: dataset manifest not a row table; it describes the canonical source datasets and their contracts
- Coverage: includes all primary statistical datasets and their manifest metadata; supports traceability and prevention of denominator drift
- Missingness: not a metric table; used to record `n_rows`, `n_unique_keys`, coverage, and variable-level missing counts
- Exact variables for paper use: dataset names, contract version, coverage flags, variable-level missing counts, and exclusion metadata
- Numerator / denominator / aggregation rule: descriptive manifest metadata only; not an inferential object
- Exclusions / unavailable reasons: includes exclusion classes and dataset-level metadata required for paper validity checks
- Supported act and section: all acts through method and the validity checks
- Strongest permitted statement: "The manifest verifies the data contracts, missingness, and dataset boundaries that govern the valid denominators in the paper."
- Not permitted: "The manifest itself proves a result or establishes effect size."
- Status: `observed`
- Evidence layer: `structured_source`
- Reconciliation status: `qualified`

### Entry 10: figure_manifest.json

- Artifact path: [../figure_manifest.json](../figure_manifest.json)
- Sidecar path: all per-figure metadata files in [../figure_data](../figure_data)
- Producer contract: figure-generation manifest and metadata files, including static and interactive outputs
- Unit of analysis: chart-specific, typically `team_semester` or `cut_context`
- Observation key: figure-specific keys stated in each metadata file
- Row count / unique-key count: dependent on figure; use the manifest and data CSV metadata for exact counts
- Coverage: all figure assets under [../../../assets/figures](../../../assets/figures)
- Missingness: figure-level `n_total`, `n_valid`, `n_missing` are explicitly recorded in the manifest
- Exact variables for paper use: figure-specific variables, transformations, and data source columns
- Numerator / denominator / aggregation rule: figure-specific; transformation notes are explicit in the manifest (`complete_case_pair`, `melt_T1_T2_T3`, `log_y`, etc.)
- Exclusions / unavailable reasons: figure limitations are explicitly recorded, e.g., small sample / observational / no trend line / availability summary not a metric
- Supported act and section: Acts 2 and 3, with some contextual Acts 1 and 4 figures as needed
- Strongest permitted statement: "A figure can support a descriptive or exploratory visual question only when its data source, n, denominator, and limitations are recorded and consistent with the report chain."
- Not permitted: "A figure without a valid denominator or with a known small sample can be used as evidence of confirmation."
- Status: `observed`
- Evidence layer: `figure_manifest`
- Reconciliation status: `qualified`

---

## 2) Report entries

### Entry 11: 00_consolidated_audit.md

- Artifact path: [../artifact_reports/00_consolidated_audit.md](../artifact_reports/00_consolidated_audit.md)
- Producer: Phase 2.5 artifact audit
- Unit of analysis: dataset-specific, as listed in the evidence table
- Key fact: `team_semester_n = 14`, five primary analyses tested, no significant result, and verdict = `conditional-go`
- Strongest permitted statement: "The present evidence is bounded by a conditional-go verdict and should be framed as exploratory and interpretive rather than confirmatory."
- Not permitted: "The current evidence confirms the planning-debt thesis."
- Status: `observed`
- Evidence layer: `phase2.5_consolidated`
- Reconciliation status: `consistent`

### Entry 12: act_2_planning_debt.md

- Artifact path: [../artifact_reports/act_2_planning_debt.md](../artifact_reports/act_2_planning_debt.md)
- Producer: Phase 2.5 act report
- Supported act: Act 2
- Main claim framing: diagnostic planning-debt act, with metrics and signals in the artifact report chain
- Strongest permitted statement: "Act 2 provides a descriptive diagnosis of planning and rework, but the current primary evidence remains inconclusive."
- Not permitted: "Act 2 proves the plan-vs-churn relationship."
- Status: `observed`
- Evidence layer: `phase2.5_act_report`
- Reconciliation status: `qualified`

### Entry 13: act_3_human_factor.md

- Artifact path: [../artifact_reports/act_3_human_factor.md](../artifact_reports/act_3_human_factor.md)
- Producer: Phase 2.5 act report
- Supported act: Act 3
- Main claim framing: human-factor and integration-friction evidence, with transcript and cut-context observations
- Strongest permitted statement: "The Act 3 evidence is primarily descriptive and interpretive because the supporting tests are sparse, unavailable, or inconclusive."
- Not permitted: "The human-factor evidence establishes a statistically robust mechanism for planning debt or progress friction."
- Status: `observed`
- Evidence layer: `phase2.5_act_report`
- Reconciliation status: `qualified`

---

## 3) Figure entries selected for paper reading

### Entry 14: pi_vs_cc

- Artifact path: [../figure_data/prioritarias/pi_vs_cc.csv](../figure_data/prioritarias/pi_vs_cc.csv)
- Figure output: [../../../assets/figures/prioritarias/pi_vs_cc.png](../../../assets/figures/prioritarias/pi_vs_cc.png)
- Source: [../team_metrics.parquet](../team_metrics.parquet)
- Manifest record: [../figure_manifest.json](../figure_manifest.json)
- Unit of analysis: `team_semester`
- n / denominator: `n_total = 14`, `n_valid = 14`, `n_missing = 0`
- Variables: `pi_file_count_t1` vs `cc_per_source_loc_t3`
- Transformation: `complete_case_pair`, `dynamic_log_y_when_range_exceeds_100`
- Strongest permitted statement: "This is a descriptive scatter plot of a complete-case pair with no significant inferential support; it cannot be used as causal evidence."
- Not permitted: "The visual pattern confirms a substantive planning-debt relationship."
- Status: `observed`
- Evidence layer: `figure_manifest`
- Reconciliation status: `consistent`

### Entry 15: delta_dt_by_team_semester

- Artifact path: [../figure_data/prioritarias/delta_dt_by_team_semester.csv](../figure_data/prioritarias/delta_dt_by_team_semester.csv)
- Figure output: [../../../assets/figures/prioritarias/delta_dt_by_team_semester.png](../../../assets/figures/prioritarias/delta_dt_by_team_semester.png)
- Source: [../team_metrics.parquet](../team_metrics.parquet)
- Manifest record: [../figure_manifest.json](../figure_manifest.json)
- Unit of analysis: `team_semester`
- n / denominator: `n_total = 42`, `n_valid = 42`, `n_missing = 0`
- Variables: `technical_complexity` across T1/T2/T3
- Transformation: `melt_T1_T2_T3`, `no_interpolation`
- Strongest permitted statement: "The figure is descriptive of temporal patterns in the observed team-semester distribution and must be read as a bounded descriptive summary rather than as proof of cause or effect."
- Not permitted: "The temporal pattern demonstrates deterioration caused by under-planning."
- Status: `observed`
- Evidence layer: `figure_manifest`
- Reconciliation status: `qualified`

### Entry 16: ai_before_t3

- Artifact path: [../figure_data/prioritarias/ai_before_t3.csv](../figure_data/prioritarias/ai_before_t3.csv)
- Figure output: [../../../assets/figures/prioritarias/ai_before_t3.png](../../../assets/figures/prioritarias/ai_before_t3.png)
- Source: [../team_metrics.parquet](../team_metrics.parquet)
- Manifest record: [../figure_manifest.json](../figure_manifest.json)
- Unit of analysis: `team_semester`
- n / denominator: `n_total = 14`, `n_valid = 7`, `n_missing = 0` for the observed pair, with missing AI-window observations outside the available subset
- Variables: `ai_max_author_share_before_t3_window` vs `ai_churn_before_t3_window`
- Transformation: `complete_case_pair`, `size_by_commit_count`
- Strongest permitted statement: "This is a descriptive visual for the available AI-window subset, but the small subsample and partial availability limit any inferential interpretation."
- Not permitted: "The scatter implies that AI before T3 drives churn across the full cohort."
- Status: `observed`
- Evidence layer: `figure_manifest`
- Reconciliation status: `qualified`

### Entry 17: ie_by_cut_or_corpus

- Artifact path: [../figure_data/prioritarias/ie_by_cut_or_corpus.csv](../figure_data/prioritarias/ie_by_cut_or_corpus.csv)
- Figure output: [../../../assets/figures/prioritarias/ie_by_cut_or_corpus.png](../../../assets/figures/prioritarias/ie_by_cut_or_corpus.png)
- Source: [../cut_context_metrics.parquet](../cut_context_metrics.parquet)
- Manifest record: [../figure_manifest.json](../figure_manifest.json)
- Unit of analysis: `cut_context`
- n / denominator: `n_total = 18`, `n_valid = 9`, `n_missing = 9`; only `3` complete transcript-score observations exist for the primary pair
- Variables: `score` across cut-context signals
- Transformation: `melt_context_signals`, `gaps_preserved`, `no_interpolation`
- Strongest permitted statement: "The figure is descriptive only; it documents sparse transcript-based scores and does not support a substantive inferential claim."
- Not permitted: "The visible pattern demonstrates coordination friction or rework at a statistically reliable level."
- Status: `observed`
- Evidence layer: `figure_manifest`
- Reconciliation status: `qualified`

---

## 4) Cross-evidence entries and caveats

The cross-evidence layer is explicitly secondary and exploratory. It can refine the paper’s interpretation but cannot override the Phase 2.5 consolidated audit or the conditional-go boundary.

### Entry 18: cross_evidence consolidated report

- Artifact path: [../cross_evidence/reports/00_cross_evidence_consolidated_report.md](../cross_evidence/reports/00_cross_evidence_consolidated_report.md)
- Unit of analysis: cross-evidence structure, mainly by group and analytic family
- Key fact: the consolidated cross-evidence result is a secondary exploratory signal set, not a replacement for the primary test verdict
- Strongest permitted statement: "Cross-evidence identifies candidate patterns for future testing, while the current primary verdict remains conditional-go."
- Not permitted: "The cross-evidence aggregate verdict supersedes the Phase 2.5 audit."
- Status: `observed`
- Evidence layer: `cross_evidence_report`
- Reconciliation status: `qualified`

Key exclusion and fragility facts that must be retained in the manuscript’s validity discussion:

- the cross-evidence aggregate includes both `supports` and `inconclusive` rows;
- the Phase 2.5 boundary remains active even when exploratory support appears;
- leave-one-out stability and category exclusions are part of the validity record, not optional framing details;
- category classification exclusions are material and must be tracked when file-category churn is discussed.

### Entry 19: prioritized cross-evidence visual families

The cross-evidence inventory contains 27 manifest artifacts, six Parquet datasets, 13 CSV results, 32 Markdown reports, and seven prioritized visual families. The families below are all represented in the paper-facing inventory, even when a family is not selected for the main paper figure set.

| family | source/report chain | paper-facing status | permitted use |
| --- | --- | --- | --- |
| `author_pressure_vs_churn` | [author-pressure figure-data report](../cross_evidence/reports/artifact_reports/author_pressure_vs_churn_data.md) | selected exploratory candidate | descriptive association only; team-semester denominator and caveats required |
| `file_category_churn_by_cut` | [category-churn figure-data report](../cross_evidence/reports/artifact_reports/file_category_churn_by_cut_data.md) | supplementary warning | exclusion-sensitive methodological warning only |
| `leave_one_out_robustness` | [leave-one-out report](../cross_evidence/reports/artifact_reports/leave_one_out_robustness_data.md) | supplementary qualification | fragility/sensitivity check, never positive evidence |
| `pareto_extreme_cases` | [Pareto figure-data report](../cross_evidence/reports/artifact_reports/pareto_extreme_cases_data.md) | reviewed, not selected | descriptive extreme-case exploration only |
| `scope_vs_late_instability` | [scope figure-data report](../cross_evidence/reports/artifact_reports/scope_vs_late_instability_data.md) | selected exploratory candidate | candidate association only; no causal direction |
| `source_churn_vs_planning_rework` | [source-churn/rework report](../cross_evidence/reports/artifact_reports/source_churn_vs_planning_rework_data.md) | reviewed, not selected | exploratory triangulation only; do not treat as primary evidence |
| `temporal_escalation_panel` | [temporal-escalation figure-data report](../cross_evidence/reports/artifact_reports/temporal_escalation_panel_data.md) | selected descriptive candidate | aggregate temporal description with unit and n in caption |

- Manifest index: [cross-evidence manifest](../cross_evidence/reports/artifact_reports/cross_evidence_manifest.md)
- Figure selection record: [selected_figures.json](selected_figures.json)
- Full visual decisions and caveats: [plot_book.md](plot_book.md)
- Cross-evidence interpretation authority: [consolidated report](../cross_evidence/reports/00_cross_evidence_consolidated_report.md)
- Reconciliation status: `qualified` for every family because the layer is secondary, exploratory, and subject to multiplicity, robustness, semester, and exclusion caveats.

---

## 5) Exclusion classes that must accompany any category-based claim

The file-category churn signal cannot be treated as a clean denominator without explicitly recording the exclusions. As the project explicitly records:

- unknown file category: 1,436 events / 30 rows
- missing line counts: 14,287 events / 67 rows
- category warnings: 10,564 events / 33 rows
- low-confidence categories: 26,567 events / 35 rows

These exclusions are not incidental. They change the denominator and the interpretation of any file-category claim. Any manuscript claim that uses a category-based churn variable must cite these exclusion counts and treat the result as fragile, conditional, or exploratory.

---

## 6) Data-book writing rules for the manuscript

Every manuscript claim should be mapped to one entry above. If the claim is based on a dataset or test, it must include:

1. the Phase 2.5 report as its interpretive starting point;
2. the structured source path and exact n / denominator;
3. the relevant exclusion or small-sample note;
4. the phrase that limits the claim to the appropriate level: observed, interpretive, or proposed.

This ensures that the final paper follows the project’s doctrine: descriptive and exploratory evidence remains visible, but the causal and methodological proposals remain explicitly bounded.
