# Phase 3 Plot Book

This document records the figure set that may support the paper, with a strict rule that visual appeal is never enough to justify a positive claim. Every figure is traced to its source artifact, report-first interpretation path, and validity caveat before it is accepted for the manuscript.

## Selection principle

The candidate figure set is filtered by the project’s evidence hierarchy:

- Phase 2.5 artifact, act, and consolidated reports define the canonical interpretation path.
- Cross-evidence figures remain secondary and exploratory unless the underlying result is explicitly labeled as descriptive or qualification-only.
- A figure can enter the manuscript set only after its source, n, unit of analysis, exclusions, and interpretation caveat are known.
- Any plot that implies causality, hides small samples, mixes units of analysis, or converts an inconclusive or unavailable result into a positive claim is rejected or downgraded.

## Default paper candidates

- scope_vs_late_instability — paper candidate
- temporal_escalation_panel — paper candidate
- author_pressure_vs_churn — paper candidate
- leave_one_out_robustness — qualification/supplementary visual, not positive evidence
- file_category_churn_by_cut — conditional supplementary; requires explicit exclusion treatment

## Entry 1: scope_vs_late_instability

- Figure identifier: `scope_vs_late_instability`
- Source artifact: `data/analysis/cross_evidence/datasets/cross_evidence_panel.parquet`
- Physical path: `assets/figures/cross_evidence/prioritarias/scope_vs_late_instability.png`
- Manifest: `data/analysis/cross_evidence/figure_data/scope_vs_late_instability.manifest.json`
- Intended paper section: Results and Discussion
- Narrative act: Act 2 and Act 3
- Visual question answered: How do scope applicability and late instability relate to source churn, planning activity, and author concentration at the team-semester level?
- x/y variables and transformations: `scope_applicability_mean_t3` on x; `late_instability_index`, `source_churn_t3`, `planning_artifact_activity_t3`, `commits_per_author_t3` on y; transformations = `complete_case_pair`, `anonymize_team_id`, `four_subplot_panel`, `log_y_source_churn_and_planning_activity`
- n, denominator, and missing observations: `n_total = 56`, `n_valid = 56`, `n_missing = 0`; team-semester observations; the manifest notes `semester 2026.1 has n=5`
- Visual type: descriptive + exploratory association plot
- Caption draft: "Descriptive cross-evidence panel showing the relation between scope applicability and late-instability-related team-semester signals; no causal direction is inferred."
- Limitations and exclusions: observational association; team-semester sample n = 14; 2026.1 subset is small; results remain exploratory and do not replace the conditional-go verdict
- Accessibility/readability check: four-subplot panel is acceptable only if the paper uses a two-column figure with legible axis labels and no overloaded annotation; otherwise reduce to a single key panel or supplementary figure
- Double-anonymous metadata check: team IDs are anonymized and no raw repository labels are present in the visual
- Decision: `paper`
- Report-first interpretation path: `data/analysis/cross_evidence/reports/act_reports/act_2_planning_debt.md` -> `data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md` -> `data/analysis/cross_evidence/results/cross_evidence_correlations.csv`
- Agreement with consolidated audit: yes, but as secondary exploratory support only; the global correlation is inconclusive (`p = 0.05909491388412068` for `scope_vs_late_instability_index`), so the plot should be framed as a candidate association, not a confirmed result
- Relevant robustness note: the corresponding leave-one-out analysis is fragile (`robustness_class = fragile`)

## Entry 2: temporal_escalation_panel

- Figure identifier: `temporal_escalation_panel`
- Source artifact: `data/analysis/cross_evidence/datasets/cross_evidence_panel.parquet`
- Physical path: `assets/figures/cross_evidence/prioritarias/temporal_escalation_panel.png`
- Manifest: `data/analysis/cross_evidence/figure_data/temporal_escalation_panel.manifest.json`
- Intended paper section: Results
- Narrative act: Act 2
- Visual question answered: How do planning activity, planning line delta, and churn evolve by temporal marker T1/T2/T3 across the observed cohort?
- x/y variables and transformations: `temporal_marker` on x; `planning_artifact_activity`, `pi_line_delta`, `cc_total`, `cc_commit_n` on y; transformation = `relative_to_t1_baseline`
- n, denominator, and missing observations: `n_total = 14` at the global group level; within-semester means are available for 2025.2 and 2026.1; missingness is not a metric issue but a small-group interpretation issue
- Visual type: descriptive panel with temporal baseline framing
- Caption draft: "Normalized temporal escalation of planning activity, planning line delta, and churn across the observed team-semester series; values are shown relative to T1 and are not used to infer causality."
- Limitations and exclusions: descriptive, baseline-normalized panel; not inferential; semester-level variation is visible but small-group composition remains limited
- Accessibility/readability check: good for a paper panel if the panel uses a large enough font and the legend stays compact; otherwise keep as supplementary figure in a single column
- Double-anonymous metadata check: no identifying metadata; the plot is aggregate at team-semester scale
- Decision: `paper`
- Report-first interpretation path: `data/analysis/artifact_reports/planning_metrics.md` and `data/analysis/artifact_reports/technical_degradation_metrics.md` -> cross-evidence temporal escalation report and manifest
- Agreement with consolidated audit: yes, as descriptive infrastructure; it supports the narrative of temporal escalation but not a causal or confirmatory claim

## Entry 3: author_pressure_vs_churn

- Figure identifier: `author_pressure_vs_churn`
- Source artifact: `data/analysis/cross_evidence/datasets/cross_evidence_panel.parquet`
- Physical path: `assets/figures/cross_evidence/prioritarias/author_pressure_vs_churn.png`
- Manifest: `data/analysis/cross_evidence/figure_data/author_pressure_vs_churn.manifest.json`
- Intended paper section: Results / Discussion
- Narrative act: Act 3
- Visual question answered: Does higher author pressure or concentration appear associated with higher source churn or planning rework in the available team-semester observations?
- x/y variables and transformations: x = `commits_per_author_t3`; y = `source_churn_t3`, `planning_rework_signal_t2_t3`, `planning_artifact_activity_t3`; transformation = `complete_case_pair`, `source_category_only_t3_for_churn`, `log_y_outcomes`
- n, denominator, and missing observations: `n_total = 42`, `n_valid = 42`, `n_missing = 0`; however the cross-evidence manifest describes the pattern as observational with team-semester sample n = 14 and no confirmatory inferential support
- Visual type: descriptive + exploratory scatter panel
- Caption draft: "Exploratory team-semester association between author pressure and source churn/rework signals; the figure illustrates a candidate pattern and does not support causal inference."
- Limitations and exclusions: observational association, team-semester sample n = 14, Gini and pressure status are supporting metadata, not the primary evidence dimension
- Accessibility/readability check: acceptable for the paper after limiting to the key panel and avoiding overly dense legend entries; consider use in supplementary if the page budget is tight
- Double-anonymous metadata check: anonymized team IDs; no direct repository or author identity leakage
- Decision: `paper`
- Report-first interpretation path: `data/analysis/cross_evidence/reports/group_reports/author_pressure_vs_churn.md` -> `data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md` -> `data/analysis/cross_evidence/results/cross_evidence_correlations.csv`
- Agreement with consolidated audit: the figure is compatible with exploratory triangulation, but it is not a replacement for the conditional-go verdict; it should be treated as a candidate pattern only

## Entry 4: leave_one_out_robustness

- Figure identifier: `leave_one_out_robustness`
- Source artifact: `data/analysis/cross_evidence/results/leave_one_out_sensitivity.csv`
- Physical path: `assets/figures/cross_evidence/prioritarias/leave_one_out_robustness.png`
- Manifest: `data/analysis/cross_evidence/figure_data/leave_one_out_robustness.manifest.json`
- Intended paper section: Results or Discussion as a qualification panel
- Narrative act: Act 2 and Act 3
- Visual question answered: How stable are the candidate cross-evidence associations when each observation is removed one by one?
- x/y variables and transformations: x = sensitivity iteration; y = coefficient bounds from `coefficient_min` to `coefficient_max`; transformation = `coefficient_interval_with_original_point`, `aggregate_only`
- n, denominator, and missing observations: `n_total = 7`, `n_valid = 7`, `n_missing = 0`; this is a per-analysis robustness view, not a raw data panel
- Visual type: qualification / robustness diagnostic
- Caption draft: "Sensitivity check showing the coefficient range under leave-one-out removal; the selected support patterns are not treated as confirmatory evidence when robustness is mixed or fragile."
- Limitations and exclusions: sensitivity evidence, not causal validation; individual removed observations are not displayed; it is intended to qualify support, not create it
- Accessibility/readability check: strong candidate for a supplementary panel or a one-column qualification figure; should not be used as main positive evidence
- Double-anonymous metadata check: no raw participant or repository identity in the sensitivity table
- Decision: `supplementary`
- Report-first interpretation path: `data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md` -> `data/analysis/cross_evidence/results/leave_one_out_sensitivity.csv`
- Agreement with consolidated audit: strong agreement with the fragility interpretation; it should not be narrated as positive evidence, only as a check on candidate support

## Entry 5: file_category_churn_by_cut

- Figure identifier: `file_category_churn_by_cut`
- Source artifact: `data/analysis/cross_evidence/datasets/file_category_churn_metrics.parquet`
- Physical path: `assets/figures/cross_evidence/prioritarias/file_category_churn_by_cut.png`
- Manifest: `data/analysis/cross_evidence/figure_data/file_category_churn_by_cut.manifest.json`
- Intended paper section: Discussion / Threats to Validity
- Narrative act: Act 2 methodological warning
- Visual question answered: How are churn volumes distributed across file categories by temporal cut, and how much of the observed pattern is driven by excluded or low-confidence categories?
- x/y variables and transformations: x = `temporal_marker`; y = `churn_lines` and `category_churn_share`; transformation = `category_complete_grid`, `zero_fill_missing_category_cut`, `absolute_log_panel`, `relative_100_percent_panel`
- n, denominator, and missing observations: `n_total = 24`, `n_valid = 24`, `n_missing = 0`; however the exclusion burden is material and must be reported alongside any interpretation
- Visual type: descriptive / methodological warning plot
- Caption draft: "Descriptive file-category churn distribution by temporal cut; category-level denominators are sensitive to exclusions and are therefore treated as a validity warning rather than a confirmatory measure."
- Limitations and exclusions: unknown category retained; absolute churn volume-sensitive; observational descriptive figure; must be interpreted with the explicit exclusion burden from the project
- Accessibility/readability check: high density; should be a supplementary or threat-visual only, not a main evidence figure
- Double-anonymous metadata check: anonymized and aggregate-only
- Decision: `supplementary`
- Report-first interpretation path: `data/analysis/cross_evidence/reports/artifact_reports/file_category_churn_by_cut_data.md` -> `data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md`
- Agreement with consolidated audit: compatible with a methodological warning; the plot cannot be used as a positive result without explicitly reporting the four exclusion classes and their effects on the denominator
- Relevant exclusion classes: unknown file category (1,436 events / 30 rows), missing line counts (14,287 events / 67 rows), category warnings (10,564 events / 33 rows), low-confidence categories (26,567 events / 35 rows)

## Entry 6: pi_vs_cc (primary figure retention)

- Figure identifier: `pi_vs_cc`
- Source artifact: `data/analysis/team_metrics.parquet`
- Physical path: `assets/figures/prioritarias/pi_vs_cc.png`
- Manifest: `data/analysis/figure_manifest.json`
- Intended paper section: Results / planning debt
- Narrative act: Act 2
- Visual question answered: How does the observed planning-intensity signal relate to code churn in the available team-semester data?
- x/y variables and transformations: `pi_file_count_t1` vs `cc_per_source_loc_t3`; `complete_case_pair`, `dynamic_log_y_when_range_exceeds_100`
- n, denominator, and missing observations: `n_total = 14`, `n_valid = 14`, `n_missing = 0`
- Visual type: descriptive scatter
- Caption draft: "Complete-case team-semester scatter of planning intensity and code churn; no significant relationship is supported in the current sample and the figure is used descriptively only."
- Decision: `supplementary`
- Report-first interpretation path: `data/analysis/artifact_reports/figure_pi_vs_cc.md` -> `data/analysis/artifact_reports/00_consolidated_audit.md`
- Agreement with consolidated audit: consistent with the null result; do not use as positive evidence

## Plot-book decision summary

| figure_id | decision | reason |
| --- | --- | --- |
| scope_vs_late_instability | paper | strongest secondary visual candidate when presented as exploratory and bounded |
| temporal_escalation_panel | paper | clear descriptive temporal pattern with no causal claim |
| author_pressure_vs_churn | paper | useful exploratory pattern, but must remain candidate-level |
| leave_one_out_robustness | supplementary | qualifies the evidence and explicitly documents fragility |
| file_category_churn_by_cut | supplementary | valid only with clear exclusion treatment and a methodological warning |
| pi_vs_cc | supplementary | null primary result, low inferential value |

## Rejection rules

The plot book explicitly rejects any figure that:

- implies causal direction without an inferential design;
- hides a small or partially missing sample;
- mixes units of analysis, such as event counts and team-semester summaries;
- presents availability or exclusion structure as if it were a real effect;
- overstates a secondary exploratory result as if it were a confirmatory claim.

A paper may include a figure because it narrates the evidence honestly, not because it is visually compelling alone.
