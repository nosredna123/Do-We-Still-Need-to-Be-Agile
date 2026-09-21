# Act 2: Planning debt and observable rework signals

## Role in the manuscript

- Target sections: Method; Results; Discussion; Threats to Validity.
- Claim level: descriptive null findings, bounded exploratory interpretation, and methodological qualification.
- Core claims: CLAIM-02, CLAIM-03, CLAIM-06, CLAIM-07.

## Claims and evidence

- [CLAIM-02 in the argument matrix](../../argument_matrix.csv): initial planning intensity and later code churn are not statistically supported as related in the current team-semester dataset.
- [CLAIM-03 in the argument matrix](../../argument_matrix.csv): planning activity and technical degradation are not statistically supported as related.
- [CLAIM-06 in the argument matrix](../../argument_matrix.csv): cross-evidence supplies candidate support only and cannot replace the conditional-go verdict.
- [CLAIM-07 in the argument matrix](../../argument_matrix.csv): file-category churn is exclusion-sensitive and cannot be treated as a robust outcome without denominator disclosure.
- [Data book](../../data_book.md): team metrics, planning metrics, code churn, technical degradation, cross-evidence, and exclusion entries.
- [Phase 3 evidence inventory](../../phase3_evidence_inventory.md)

## Statistical rows and exclusions

- [Primary correlation results](../../../correlation_results.csv)
- [Semester-stratified results](../../../cross_evidence/results/semester_stratified_results.csv)
- [Leave-one-out sensitivity](../../../cross_evidence/results/leave_one_out_sensitivity.csv)
- [Statistical dataset exclusions](../../../statistical_dataset_manifest_exclusions.json)
- [Team metrics exclusions](../../../team_metrics_exclusions.json)
- Exclusion classes: unknown file category `1,436 events / 30 rows`; missing line counts `14,287 events / 67 rows`; category warnings `10,564 events / 33 rows`; low-confidence categories `26,567 events / 35 rows`.

## Figures and captions

- `temporal_escalation_panel`: main descriptive candidate; caption must state temporal aggregation, unit, and `n`.
- `scope_vs_late_instability`: exploratory candidate; present as secondary and non-causal.
- `pi_vs_cc`: supplementary null-descriptive visual.
- `leave_one_out_robustness`: supplementary qualification visual, never positive evidence.
- `file_category_churn_by_cut`: supplementary methodological warning with exclusion burden beside it.
- [Plot book](../../plot_book.md)
- [Selected figures](../../selected_figures.json)

## Report chain

1. [Phase 2.5 planning artifact report](../../../artifact_reports/planning_metrics.md)
2. [Phase 2.5 planning act report](../../../artifact_reports/act_2_planning_debt.md)
3. [Phase 2.5 consolidated audit](../../../artifact_reports/00_consolidated_audit.md)
4. [Cross-evidence planning act report](../../../cross_evidence/reports/act_reports/act_2_planning_debt.md)
5. [Cross-evidence scope report](../../../cross_evidence/reports/artifact_reports/scope_vs_late_instability_data.md)
6. [Cross-evidence temporal report](../../../cross_evidence/reports/artifact_reports/temporal_escalation_panel_data.md)
7. [Cross-evidence exclusion report](../../../cross_evidence/reports/artifact_reports/file_category_churn_by_cut_data.md)
8. [Cross-evidence consolidated report](../../../cross_evidence/reports/00_cross_evidence_consolidated_report.md)

## References

- `cunningham_1992_technical_debt`
- `li_2015_technical_debt_mapping`
- `perez_2022_planning_and_rework`
- [Literature map](../../../../../docs/phase3/literature-map.md)

## Synthesis

The observed data supports descriptive discussion of planning artifacts, churn, and temporal escalation, but the primary tests remain null or inconclusive. Cross-evidence is exploratory, multiplicity and leave-one-out behavior limit confidence, and category exclusions alter denominators. Act 2 therefore supports an evidence-bounded planning-debt question, not a causal claim that planning debt caused churn or that SDD/BDUF is superior.
