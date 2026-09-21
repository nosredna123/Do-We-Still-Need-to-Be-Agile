# Manuscript Draft: Results

## 4. Results

### 4.1 Descriptive dataset profile

The primary team-level dataset contains 14 team-semester observations across the 2025.2 and 2026.1 semesters. Planning, code-change, technical-degradation, and AI-associated author-concentration measures are represented at this level when the source provides a team key. The cut-context dataset contains six observations keyed by semester and temporal marker, with three temporal cuts in each semester. Student-response and transcript-session/corpus artifacts retain their native granularities and are not treated as team-semester observations.

The planning artifact dataset contains 14 observations and no reported missingness for the variables used in its descriptive summary. It records planning activity through measures such as initial planning-file count, planning event counts, deleted planning artifacts, line deltas, and later planning rework signals. The technical-degradation dataset also contains 14 team-semester observations, with temporal complexity and delta measures available across the reported windows. These artifacts are descriptive infrastructure: they establish what was measured and how it varies, but they do not themselves provide inferential evidence.

The integration-friction dataset contains 14 team-semester rows for AI-related author-concentration signals. The transcript/context dataset is smaller and structurally different: it contains six semester-cut observations, with missingness in the primary transcript-derived signals. This difference in coverage is central to the interpretation of the human-factor results.

### 4.2 Report-first evidence map

The Phase 2.5 reports describe planning, code churn, technical degradation, and integration signals as available analytical infrastructure rather than as established mechanisms. The consolidated audit reports a team-semester `n = 14`, five tested primary analyses, no significant primary result, and a `conditional-go` verdict. This result governs the interpretation of the sections that follow.

At the artifact level, planning activity is observable and complete for the summarized team-semester variables, but no planning metric is itself a test of planning quality. Technical-degradation measures describe temporal complexity and deltas, but their descriptive changes cannot be attributed to planning debt. The integration-friction report provides observable author-share and concentration variables, while the cut-context report marks the transcript-derived coordination analysis as unavailable. The Results section therefore separates descriptive patterns from tested relationships and treats unavailable evidence as an evidence boundary rather than as a negative finding.

### 4.3 Planning activity, code churn, and technical degradation

The primary association between initial planning intensity and later code churn was not statistically supported. The Spearman analysis `pi_vs_cc_primary`, using `pi_file_count_t1` and `cc_per_source_loc_t3` at the team-semester level, had `n_total = 14`, `n_valid = 14`, and `n_missing = 0`; its coefficient was `-0.006766649524509584` with `p = 0.9816838660605893`.

The corresponding relationship between initial planning intensity and technical degradation was also not statistically supported. For `pi_vs_delta_dt_primary`, relating `pi_file_count_t1` to `delta_dt_t1_t3`, the analysis had `n_total = 14` and `n_valid = 14`, with coefficient `-0.014709647511909141` and `p = 0.960194880594909`.

These results do not establish that planning is irrelevant, nor do they establish that planning debt is absent. They indicate that the selected planning-intensity proxy did not provide statistically reliable evidence for the tested relationships in this cohort. The proxy measures artifact activity or volume, not the quality or adequacy of a team’s design reasoning. Likewise, code churn and technical-degradation variables are observable repository and metric signals, not direct causal measures of waste or debt.

The descriptive planning artifact summary shows that all 14 team-semester rows were available for the reported planning variables. For example, the mean initial planning-file count was 2.57, the mean initial planning line delta was 60.14, and the mean later planning line delta was 10,164.57. These values describe the observed artifact distribution; they do not convert the distribution into evidence of an effect. The technical-degradation summary similarly reports complete descriptive values for the 14 team-semester rows, including mean temporal deltas of `-0.0149` from T1 to T2 and `0.2262` from T2 to T3. These temporal summaries are descriptive and should not be read as evidence that under-planning caused deterioration.

**Figure placement.** The `pi_vs_cc` scatter is retained as a supplementary null-descriptive visual. The `temporal_escalation_panel` is a main-figure candidate for describing relative temporal changes, provided its caption identifies the metric-family aggregation and does not imply a team-semester inferential test. Both figures are interpreted through the report chain and the data book.

### 4.4 AI-associated author concentration and transcript/context evidence

AI-associated author concentration was measurable in the available Git-derived signals, but the tested relationship with code churn was not statistically supported. The `ai_vs_cc_primary` analysis related `ai_max_author_share_before_t3_window` to `cc_total_t3`. It had `n_total = 14`, `n_valid = 7`, and `n_missing = 7`; the coefficient was `0.21428571428571433` with `p = 0.6445115810207203` and a small-sample warning.

The integration-friction artifact provides descriptive variation in the available team-semester signals. The mean number of authors observed before the T3 window was 1.86, the mean pre-T3 churn value was 5,150.57, and the mean T3 author-concentration Gini value was 0.2473. These summaries describe the available Git signal and do not establish that concentration caused churn, that concentration represents AI use completely, or that a "hero developer" mechanism was confirmed.

The transcript/context analysis did not produce a usable inferential result. The `context_ie_temporal_primary` row is keyed by `cut_context`, with `n_total = 6`, `n_valid = 3`, and `n_missing = 3`; it has no coefficient or p-value because the result is classified as unavailable due to zero variance. Consequently, the current data cannot support a substantive claim that transcript-based coordination friction predicts rework or divergent progress. The associated `ie_by_cut_or_corpus` visual remains descriptive, with `n_total = 18`, `n_valid = 9`, and `n_missing = 9` in its figure-data record; this figure-data count must not be treated as 18 independent team observations.

**Figure placement.** `author_pressure_vs_churn` is retained as an exploratory candidate. Its figure-data artifact contains 42 rows, but those rows represent the chart’s long-format visual data rather than 42 independent team-semester observations. The underlying team-semester boundary and the seven-complete-case primary analysis remain controlling. The figure caption must state the unit, available subset, and exploratory status.

### 4.5 Secondary cross-evidence candidates

The cross-evidence layer was examined as secondary exploratory triangulation. Its results do not replace the Phase 2.5 primary verdict. The consolidated cross-evidence report labels an aggregate `supports` outcome, but it also contains inconclusive rows, fragile or unsupported leave-one-out results, semester-stratified variation, and exclusion-sensitive category analyses. These outputs were therefore used to identify candidate relationships and methodological warnings rather than to claim confirmation.

The `scope_vs_late_instability` figure-data artifact contains 56 rows and is bound to a team-semester-oriented visual family, but the figure-data row count is not itself a new sample of 56 independent teams or semesters. The figure can illustrate candidate associations among scope applicability, late instability, churn, planning activity, and author-related signals; it cannot establish their direction or causality. The `author_pressure_vs_churn` family similarly contains 42 figure-data rows for a long-format visual representation, while the inferential team-semester boundary remains `n = 14` and the AI primary complete-case count remains `n_valid = 7`.

The `temporal_escalation_panel` contains 54 metric-family-cut rows and expresses values relative to a T1 baseline. It is useful for describing temporal escalation across metric families, but its `metric_family_cut` unit and varying valid counts mean that it must not be presented as 54 independent team-semester tests. The panel is descriptive and exploratory, not causal.

Robustness checks qualify rather than strengthen the positive narrative. The leave-one-out artifact contains seven analysis-result rows. It reports a mean original coefficient of `-0.5207`, a mean leave-one-out coefficient minimum of `-0.6726`, a mean maximum of `-0.4343`, and a mean support share of approximately `0.4796`. These values show that sensitivity behavior varies across the candidate analyses; the leave-one-out figure is consequently used as a qualification visual, not as positive evidence.

Category-level churn is treated as a methodological warning. Unknown file categories, missing line counts, category warnings, and low-confidence categories remove substantial events or rows from the relevant denominators. The `file_category_churn_by_cut` visual can show how the retained category summaries are distributed, but it cannot support a robust category-based outcome claim without those exclusions beside the result.

### 4.6 Primary and secondary result summary

| result family | unit | n / denominator | status | interpretation |
| --- | --- | --- | --- | --- |
| `pi_vs_cc_primary` | team-semester | 14 / 14 valid | non-significant | no statistically supported planning-intensity/code-churn association |
| `pi_vs_delta_dt_primary` | team-semester | 14 / 14 valid | non-significant | no statistically supported planning-intensity/technical-degradation association |
| `ai_vs_cc_primary` | team-semester | 14 total / 7 valid | non-significant, small-sample | AI concentration is measurable in a sparse subset; no positive relationship claim |
| `context_ie_temporal_primary` | cut-context | 6 total / 3 valid | unavailable, zero variance | no substantive transcript-coordination inference |
| cross-evidence candidates | family-specific | family-specific; not pooled | exploratory/mixed | candidate hypotheses and methodological warnings only |
| leave-one-out sensitivity | analysis-result | 7 rows | qualification | robustness is mixed and must qualify candidate support |
| file-category churn | category/event or category-row | exclusion-sensitive | methodological warning | denominator burden prevents an unqualified outcome claim |

Together, these results answer the empirical part of the paper cautiously. The persisted artifacts provide descriptive evidence about planning activity, temporal changes, repository churn, and available author-concentration signals. They do not provide statistically reliable primary support for the central planning-debt relationships, and they do not provide an inferential coordination result from the sparse transcript/context data. Secondary cross-evidence identifies patterns worth testing in larger or better-paired studies, but it does not alter the conditional-go conclusion.

## Results traceability controls

- Primary numerical verification: [correlation results](../../data/analysis/correlation_results.csv), [hypothesis results](../../data/analysis/hypothesis_results.csv), and [statistical dataset manifest](../../data/analysis/statistical_dataset_manifest.json).
- Report-first interpretation: [Phase 2.5 consolidated audit](../../data/analysis/artifact_reports/00_consolidated_audit.md), planning, technical-degradation, integration-friction, and cut-context reports.
- Cross-evidence verification: [consolidated cross-evidence report](../../data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md), [plot book](../../data/analysis/paper_support/plot_book.md), and [selected figures](../../data/analysis/paper_support/selected_figures.json).
- Claim control: [argument matrix](../../data/analysis/paper_support/argument_matrix.csv).
- Status: draft for Task 4.3; figure captions, table formatting, and exact venue style remain for the integration review.
