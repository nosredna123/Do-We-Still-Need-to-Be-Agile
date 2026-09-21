# Act 3: Human factor, AI concentration, and coordination boundaries

## Role in the manuscript

- Target sections: Results; Discussion; Threats to Validity.
- Claim level: descriptive and interpretive, with explicit sparse-data boundaries.
- Core claims: CLAIM-04, CLAIM-05, CLAIM-06.

## Claims and evidence

- [CLAIM-04 in the argument matrix](../../argument_matrix.csv): AI author concentration is measurable in the available subset, but too sparse for a positive relationship claim.
- [CLAIM-05 in the argument matrix](../../argument_matrix.csv): transcript-based coordination friction is unavailable or too sparse for a substantive claim.
- [CLAIM-06 in the argument matrix](../../argument_matrix.csv): cross-evidence candidate support remains secondary and exploratory.
- [Data book](../../data_book.md): integration friction, cut-context, transcript, author-pressure, and cross-evidence entries.
- [Phase 3 evidence inventory](../../phase3_evidence_inventory.md)

## Statistical rows and availability

- [Primary correlation results](../../../correlation_results.csv): `ai_vs_cc_primary` has `n_valid = 7`, `n_missing = 7`, and `p = 0.6445115810207203`; `context_ie_temporal_primary` is unavailable because of zero variance.
- [Integration friction source](../../../integration_friction_metrics.parquet)
- [Cut-context source](../../../cut_context_metrics.parquet)
- [Transcript NLP source](../../../transcript_nlp.parquet)
- [Leave-one-out sensitivity](../../../cross_evidence/results/leave_one_out_sensitivity.csv)

## Figures and captions

- `author_pressure_vs_churn`: paper candidate only as an exploratory, non-causal association; caption must state team-semester unit and sample limitation.
- `scope_vs_late_instability`: secondary exploratory visual that can bridge planning and human-factor discussion.
- `leave_one_out_robustness`: qualification visual for fragility.
- [Plot book](../../plot_book.md)
- [Selected figures](../../selected_figures.json)

## Report chain

1. [Phase 2.5 integration-friction report](../../../artifact_reports/integration_friction_metrics.md)
2. [Phase 2.5 human-factor act report](../../../artifact_reports/act_3_human_factor.md)
3. [Phase 2.5 cut-context report](../../../artifact_reports/cut_context_metrics.md)
4. [Phase 2.5 consolidated audit](../../../artifact_reports/00_consolidated_audit.md)
5. [Cross-evidence human-factor act report](../../../cross_evidence/reports/act_reports/act_3_human_factor.md)
6. [Cross-evidence author-pressure report](../../../cross_evidence/reports/artifact_reports/author_pressure_vs_churn_data.md)
7. [Cross-evidence consolidated report](../../../cross_evidence/reports/00_cross_evidence_consolidated_report.md)

## References

- `chen_2021_evaluating_code_llms`
- `miller_2023_coordination_ai_teams`
- `demarco_lister_1987_peopleware`
- `brooks_1975_mythical_man_month`
- [Literature map](../../../../../docs/phase3/literature-map.md)

## Synthesis

Author concentration is an observable proxy in a seven-complete-case subset, not a complete measure of AI use or its quality. Transcript coordination friction is unavailable for substantive inference because the primary measure has zero variance and incomplete pairing. The act can motivate teaching coordination and AI-process literacy, but it cannot establish a human-factor mechanism or causal relationship with churn.
