# M9 V8 to V9 Analysis

## V8 baseline

The V8 M9 used the opaque `t1_planning_score`, legacy rework fields, evaluator
outcomes, and an invalid floor-imputation sensitivity that assigned score 1 to
missing planning evidence. The V8 analysis rejects that imputation because Git
absence does not prove planning absence.

## V9 decision

M9 v9 computes descriptive Spearman associations using separate M6a predictors:
`pi_file_count_t1` and `planning_scope_log1p_t1`. M8a clean rework magnitude is
analyzed across all 14 team-semesters. M8b clean rework ratio is analyzed only
among the 12 baseline-eligible team-semesters. T3 evaluator outcomes are joined
from the canonical evaluator cuts. Leave-one-out rows expose influence and
small-denominator sensitivity.

M7 is excluded as a predictor. Human review approved M6b on 2026-09-24; its
structured fields now enter a separate M9 association output for the nine
observed team-semesters. The five unavailable M6b cases remain excluded
pairwise, and no composite M6b score is created.

## V8 to V9 traceability matrix

| v8_recommendation | v9_decision | status | evidence | limitation_or_approval |
|---|---|---|---|---|
| Associate planning with clean rework magnitude. | Use M6a structural predictors and M8a across all 14 team-semesters. | applied | M9a CSV | Descriptive, small n. |
| Stratify rework ratio by baseline eligibility. | Restrict M8b associations to 12 eligible cases without imputing others. | applied | M9b CSV and metadata | Eligibility is path provenance. |
| Include independent T3 evaluator outcomes. | Join canonical T3 evaluator cuts and publish separate outcomes. | applied | M9c CSV | No causal inference. |
| Diagnose influence. | Publish leave-one-out Spearman rows for each association. | applied | M9 leave-one-out CSV | Sensitivity, not significance. |
| Do not impute a floor or use M7 independently. | Preserve missingness, exclude M7 as predictor, and use approved M6b fields separately without a composite score. | applied | M6b/M9 metadata and notebook | Five M6b cases remain unavailable. |
