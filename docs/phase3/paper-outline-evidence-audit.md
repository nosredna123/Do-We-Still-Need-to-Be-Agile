# Paper Outline Evidence Audit

**Audit date:** 2026-09-22  
**Scope:** persisted analysis outputs, reports, figure data, figure manifests, and the existing Phase 3 literature map. Phase 2 artifacts were not rerun or modified.

## Executive assessment

The attached outline is rhetorically coherent, but its central empirical claims are stronger than the current repository evidence permits. The persisted Phase 2.5 audit reports 14 team-semester observations, five primary analyses, no significant primary result, and a `conditional-go` verdict. The paper should therefore be presented as a descriptive and exploratory case study, not as confirmation that omitted BDUF causes planning debt, rework, or a hero-developer bottleneck.

The repository does contain a useful descriptive pattern: planning activity, planning-line delta, churn, and commit counts rise across T1, T2, and T3. It also contains secondary cross-evidence associations involving scope applicability. These are suitable for motivating hypotheses and showing temporal structure, but they do not establish causality or validate SDD/BDUF as superior to Agile.

## Direct reconciliation with the attached outline

| Outline claim | Repository finding | Allowed manuscript treatment |
| --- | --- | --- |
| Planning activity escalates from T1 to T3 with median delta +9.5 and `p = 0.0006` | The persisted temporal panel is descriptive and contains no valid primary test with `p = 0.0006`. The primary audit reports five tested analyses and no significant result. | Replace the inferential claim with descriptive escalation, or identify and document the missing analysis before publication. |
| Planning debt produces later code churn | `pi_vs_cc_primary`: Spearman rho = -0.0068, `p = 0.9817`, n = 14, complete. | Say the selected planning-intensity proxy was not associated with later churn in this cohort. |
| Planning debt produces technical degradation | `pi_vs_delta_dt_primary`: rho = -0.0147, `p = 0.9602`, n = 14, complete. | Say no statistically reliable association was detected; temporal complexity still rose modestly from T2 to T3 descriptively. |
| AI author concentration creates a hero-developer bottleneck | `ai_vs_cc_primary`: rho = +0.2143, `p = 0.6445`, n = 7 valid of 14. The coefficient is opposite to the proposed direction and has 50% missingness. | Treat author concentration as a sparse exploratory signal, not evidence of a bottleneck mechanism. |
| Transcript evidence demonstrates coordination collapse | The cut-context analysis is unavailable: 3 complete observations of 6 and zero variance. | Move this from evidence to limitations and measurement-boundary discussion. |
| SDD/BDUF is required by the findings | No SDD or BDUF intervention was tested. | Present SDD/BDUF as a proposed educational and methodological direction. |

## Strongest additional evidence and visualizations

### 1. Temporal escalation panel

Source: `assets/figures/cross_evidence/prioritarias/temporal_escalation_panel.png` and `data/analysis/cross_evidence/figure_data/temporal_escalation_panel.csv`.

At the global descriptive level, planning artifact activity increases from 2.57 at T1 to 61.07 at T2 and 89.29 at T3. Planning-line delta increases from 60.14 to 1,467.71 and then 10,164.57. Total churn increases from 3,615.29 to 17,314.21 and then 964,437.93. Commit count increases from 7.93 to 16.36 and then 33.71. These are metric-family summaries normalized to the T1 baseline, not 54 independent observations and not an inferential test.

Use this as the principal results figure with a caption stating that it is descriptive, baseline-normalized, and non-causal. It supports the weaker statement that late-stage activity is concentrated in the observed trajectories; it does not prove planning debt or explain why the trajectories changed.

### 2. Scope versus planning line delta and planning activity

Source: `data/analysis/cross_evidence/results/cross_evidence_correlations.csv` and `data/analysis/cross_evidence/results/leave_one_out_sensitivity.csv`.

- Scope applicability versus T3 planning-line delta: rho = -0.6736, `p = 0.0083`, n = 14; all 14 leave-one-out iterations preserve the expected direction.
- Scope applicability versus T3 planning artifact activity: rho = -0.5832, `p = 0.0286`, n = 14; 13 of 14 leave-one-out iterations preserve the direction.
- Scope applicability versus T3 commits per author: rho = -0.7285, `p = 0.0031`, n = 14; all 14 leave-one-out iterations preserve the direction.

These are the strongest additional numeric signals in the repository, but they are secondary exploratory analyses with multiple comparisons. Their direction also does not support the simple hero-developer story: higher scope applicability is associated with lower author pressure in this dataset. Use them as candidate relationships in a discussion or exploratory-results panel, not as confirmation of the attached causal narrative.

Recommended figure: `assets/figures/cross_evidence/prioritarias/scope_vs_late_instability.png`. The panel must display the individual p-values and the fragile status of the late-instability subplot. The late-instability association itself is inconclusive: rho = -0.5157, `p = 0.0591`, with only 2 of 14 leave-one-out iterations supporting the direction.

### 3. Author pressure versus churn

Source: `assets/figures/cross_evidence/prioritarias/author_pressure_vs_churn.png` and its figure-data manifest.

This figure is useful for showing a candidate pattern involving commits per author, source churn, planning rework, and planning activity. Its long-format figure data contain 42 rows, but the inferential unit remains team-semester and the cohort boundary remains n = 14. It should not be described as 42 independent observations. Keep it in the discussion or supplement, with a non-causal caption.

### 4. Robustness and exclusion visuals

Use `assets/figures/cross_evidence/prioritarias/leave_one_out_robustness.png` as a qualification visual, not as positive evidence. It makes the difference between robust scope associations and fragile late-instability/rework associations visible.

Use `assets/figures/cross_evidence/prioritarias/file_category_churn_by_cut.png` only beside the exclusion disclosure. The relevant exclusion classes are unknown file category (1,436 events / 30 rows), missing line counts (14,287 / 67 rows), category warnings (10,564 / 33 rows), and low-confidence categories (26,567 / 35 rows). These exclusions make category-level churn a methodological warning rather than an unqualified outcome.

## Recommended revised narrative

1. **Act 1:** retain as contextual framing. The Agile Manifesto establishes the historical value hierarchy; the AI-era argument is a motivation, not a tested result.
2. **Act 2:** replace “proves planning debt” with “documents late-stage concentration of planning and change activity, while the tested planning-intensity relationships are null.” Define planning debt as a proposed construct whose quality-sensitive operationalization remains open.
3. **Act 3:** replace “hero developer bottleneck confirmed” with “author pressure and concentration are measurable but only partly observed; secondary scope associations are exploratory and point in mixed directions.” Treat transcript coordination as unavailable evidence.
4. **Act 4:** frame SDD/BDUF as a design hypothesis for future comparative educational research. Do not claim that the current study demonstrates Agile obsolescence or the superiority of front-loaded design.

## Threats that must appear beside the results

- n = 14 team-semesters, from two semesters and one educational setting.
- Observational design: no intervention, randomization, or identified causal direction.
- The planning proxy measures artifact volume/activity, not specification quality.
- Churn may include productive iteration as well as rework.
- AI author concentration is incomplete and has 7 missing values of 14.
- Transcript coordination metrics have 3 complete values and zero variance.
- Cross-evidence includes multiple exploratory families, semester-stratified analyses, contrasts, overlap tests, and sensitivity analyses.
- Figure-data row counts must not replace the underlying unit-specific denominators.

## Literature use

The existing literature map is appropriate for bounded framing: the Agile Manifesto for historical context; Cunningham and the technical-debt mapping study for the debt metaphor and measurement caution; Brooks and Peopleware as coordination counterpoints; and the AI/software-engineering-education references for setting and motivation. Fowler's technical-debt discussion is also useful as a practitioner explanation of rework interest, but it should not be treated as empirical validation of this cohort.

Before submission, verify the authoritative publication records for all recent AI, education, coordination, and planning references already listed in `docs/phase3/references.bib`. The repository's own review checklist correctly marks this bibliography verification as pending.

## Bottom line

The repository supports a publishable, evidence-constrained paper about what can and cannot be learned from planning, churn, technical-degradation, and coordination signals in AI-assisted student projects. It does not currently support the attached outline's strongest causal or confirmatory wording. The highest-value paper revision is to make the descriptive T1-to-T3 escalation the central visual result, report the primary nulls explicitly, use scope associations as exploratory triangulation, and present SDD/BDUF as a testable proposal rather than a demonstrated conclusion.

## Traceability

- [Phase 2.5 consolidated audit](../../data/analysis/artifact_reports/00_consolidated_audit.md)
- [Primary claim matrix](../../data/analysis/paper_support/argument_matrix.csv)
- [Plot book](../../data/analysis/paper_support/plot_book.md)
- [Cross-evidence correlations](../../data/analysis/cross_evidence/results/cross_evidence_correlations.csv)
- [Leave-one-out sensitivity](../../data/analysis/cross_evidence/results/leave_one_out_sensitivity.csv)
- [Temporal panel data](../../data/analysis/cross_evidence/figure_data/temporal_escalation_panel.csv)
- [Draft results](manuscript-results.md)
- [Draft discussion and validity section](manuscript-discussion.md)
- [Literature map](literature-map.md)
