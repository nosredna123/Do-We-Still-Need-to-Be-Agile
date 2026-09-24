# M8 V8 to V9 Analysis

## V8 baseline

The V8 M8 artifact republishes `rework_churn_t3` and `deferred_churn_t3`, then
computes a total and ratio. The V8 analysis identifies a weaker exclusion policy
and a collapse of magnitude, proportion, baseline eligibility, and temporal
dynamics into one result.

## V9 decision

M8 v9 reuses the M4 `code-churn-metrics-v2` / `cc-v2-clean-paths` policy and
publishes four distinct views:

- M8a: clean rework churn in paths first observed at T1 or T2;
- M8b: clean rework ratio at T3, retained only as a descriptive ratio and not
  interpreted for baseline-ineligible teams or zero clean T3 churn;
- M8c: clean rework churn and reworked paths in 29 overlapping windows from
  -21 through +7 days relative to the last T3 evaluator vote;
- M8d: prior clean-path count and baseline eligibility.

Path provenance is a proxy for prior observation, not semantic destructive-rework
or defect validation. Binary-file null churn values are treated as zero only when
both line fields are null and the canonical `is_binary` flag is true; unexplained
nulls fail fast.

## V8 to V9 traceability matrix

| v8_recommendation | v9_decision | status | evidence | limitation_or_approval |
|---|---|---|---|---|
| Separate magnitude from ratio. | Publish M8a and M8b as distinct fields/files. | applied | M8 magnitude and participation CSVs | Ratio remains descriptive. |
| Condition ratio on baseline eligibility. | Publish prior path count and explicit eligibility; do not impute ineligible teams. | applied | M8d CSV and metadata | Absence of baseline is not stability. |
| Add late-stage rolling dynamics. | Publish 29 T3-relative seven-day windows per team-semester. | applied | M8c trajectory CSV | Windows overlap. |
| Use the M4 clean-path policy. | Fail fast on stale contract and use central `is_clean_path`. | applied | Producer and metadata | Classification is policy-based. |
| Do not call provenance a defect. | Use clean rework/path provenance terminology only. | applied | Producer, notebook, limitations | No semantic defect claim. |
