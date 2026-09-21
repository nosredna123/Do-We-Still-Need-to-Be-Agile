# Claim-Evidence Matrix

This companion document records the paper-facing evidence logic for the Phase 3 manuscript. It is meant to keep the writing disciplined: no claim enters the manuscript without an identifiable source, a bounded strength label, and a traceable denominator or limitation.

## Control principles

- Phase 2.5 reports are the interpretive starting point.
- Cross-evidence supports are secondary and exploratory.
- The core boundary remains the conditional-go verdict: team-semester n = 14, five primary analyses, no significant primary result.
- A claim is eligible for main Results only when its source, n, denominator, and limitation are known.
- Figures may illustrate a pattern but cannot substitute for an inferential claim when the underlying test is unavailable or null.

## Claim matrix summary

| claim_id | section | claim type | status | decision | confidence |
| --- | --- | --- | --- | --- | --- |
| CLAIM-01 | Introduction / Act 1 | contextual | observed/contextual | retain | high |
| CLAIM-02 | Results / Act 2 | descriptive | null / inconclusive | retain | high |
| CLAIM-03 | Results / Act 2 | descriptive | null / inconclusive | retain | high |
| CLAIM-04 | Results / Act 3 | descriptive | fragile / small-sample | qualify | moderate |
| CLAIM-05 | Results / Act 3 | descriptive | unavailable | move_to_limitations | high |
| CLAIM-06 | Discussion / Act 2 and 3 | interpretive | exploratory candidate support | qualify | exploratory |
| CLAIM-07 | Discussion / Method | methodological | denominator/validity warning | retain | high |

## Claim details

### CLAIM-01

- Claim text: Generative-AI-supported software engineering education creates a planning environment in which explicit specification and coordination become more consequential than in conventional course settings.
- Strength: contextual only; no direct statistical test exists.
- Interpretive authority: [../../data/analysis/artifact_reports/act_1_evolutionary_ceiling.md](../../data/analysis/artifact_reports/act_1_evolutionary_ceiling.md)
- Source verification: [../../data/analysis/statistical_dataset_manifest.json](../../data/analysis/statistical_dataset_manifest.json)
- Decision: retain as contextual framing; do not present as a demonstrated result.

### CLAIM-02

- Claim text: At the team-semester level, the observed relationship between initial planning intensity and later code churn is not statistically supported in the current dataset.
- Source path: [../../data/analysis/correlation_results.csv](../../data/analysis/correlation_results.csv)
- Exact result: `pi_vs_cc_primary` — coefficient = -0.006766649524509584, p = 0.9816838660605893, n = 14, n_valid = 14, n_missing = 0.
- Report chain: [../../data/analysis/artifact_reports/figure_pi_vs_cc.md](../../data/analysis/artifact_reports/figure_pi_vs_cc.md) and [../../data/analysis/artifact_reports/planning_metrics.md](../../data/analysis/artifact_reports/planning_metrics.md)
- Decision: retain as a null finding; no causal phrasing.

### CLAIM-03

- Claim text: The current evidence does not support a statistically reliable association between planning activity and technical degradation as measured in the team-semester dataset.
- Source path: [../../data/analysis/correlation_results.csv](../../data/analysis/correlation_results.csv)
- Exact result: `pi_vs_delta_dt_primary` — coefficient = -0.014709647511909141, p = 0.960194880594909, n = 14.
- Report chain: [../../data/analysis/artifact_reports/figure_delta_dt_by_team_semester.md](../../data/analysis/artifact_reports/figure_delta_dt_by_team_semester.md)
- Decision: retain as a null finding; the descriptive temporal figure remains descriptive only.

### CLAIM-04

- Claim text: AI author concentration before T3 is measurable in the available subset, but the evidence remains too sparse to support a positive claim about its relationship to churn or other outcomes.
- Source path: [../../data/analysis/correlation_results.csv](../../data/analysis/correlation_results.csv)
- Exact result: `ai_vs_cc_primary` — coefficient = 0.21428571428571433, p = 0.6445115810207203, n_total = 14, n_valid = 7, n_missing = 7; `warning = small_sample_n_lt_10`.
- Report chain: [../../data/analysis/artifact_reports/integration_friction_metrics.md](../../data/analysis/artifact_reports/integration_friction_metrics.md) and [../../data/analysis/artifact_reports/figure_ai_before_t3.md](../../data/analysis/artifact_reports/figure_ai_before_t3.md)
- Decision: qualify; keep this as a small-sample exploratory pattern only.

### CLAIM-05

- Claim text: Transcript-based coordination friction and rework signals are unavailable or too sparse to support a substantive coordination claim in the current dataset.
- Source path: [../../data/analysis/correlation_results.csv](../../data/analysis/correlation_results.csv) and [../../data/analysis/cut_context_metrics.parquet](../../data/analysis/cut_context_metrics.parquet)
- Exact result: `context_ie_temporal_primary` — status = unavailable, reason = zero_variance, n_total = 6, n_valid = 3, n_missing = 3.
- Report chain: [../../data/analysis/artifact_reports/cut_context_metrics.md](../../data/analysis/artifact_reports/cut_context_metrics.md)
- Decision: move to limitations; the visual is descriptive only.

### CLAIM-06

- Claim text: Cross-evidence suggests exploratory candidate support for scope versus PI line delta and planning-artifact activity, but this remains secondary evidence and cannot replace the Phase 2.5 conditional-go verdict.
- Source path: [../../data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md](../../data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md)
- Report chain: [../../data/analysis/cross_evidence/reports/act_reports/act_2_planning_debt.md](../../data/analysis/cross_evidence/reports/act_reports/act_2_planning_debt.md)
- Decision: qualify as exploratory candidate support only; not a confirmatory result.

### CLAIM-07

- Claim text: File-category churn cannot be used as a robust outcome measure without explicit treatment of the exclusion burden, which is substantial for unknown, missing, warning, and low-confidence categories.
- Source path: [../../data/analysis/statistical_dataset_manifest_exclusions.json](../../data/analysis/statistical_dataset_manifest_exclusions.json) and [../../data/analysis/team_metrics_exclusions.json](../../data/analysis/team_metrics_exclusions.json)
- Exact exclusions: unknown category = 1,436 events / 30 rows; missing line counts = 14,287 events / 67 rows; category warnings = 10,564 events / 33 rows; low-confidence categories = 26,567 events / 35 rows.
- Decision: retain as a validity and method warning; must be reported if category-based churn is discussed.

## Evidence roles

- `candidate_support`: used when the claim is exploratory but not confirmatory.
- `methodological_warning`: used when the claim is about validity, denominator, or exclusion burdens.
- `context`: used when the claim is contextual rather than statistical.
- `not_used`: used when a visual or table is descriptive but not used as positive evidence.

## Writing caution

The matrix intentionally prevents narrative drift. A favorable-looking plot, a sign-positive coefficient, or an exploratory cross-evidence row is not enough to convert the paper into a confirmatory thesis. The project boundary is explicit: the current evidence is conditional-go, not proof.
