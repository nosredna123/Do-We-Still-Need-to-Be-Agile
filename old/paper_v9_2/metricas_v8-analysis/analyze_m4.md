# M4 V8 Analysis and V9 Decision

## V8 findings

The v8 review assigns M4 to RQ2 and identifies raw churn contamination and
commit-count duplication with M3. The revised M4 must use the current
`code-churn-metrics-v2` / `cc-v2-clean-paths` policy, separate clean source/test
magnitude from intensity and artifact composition, and use seven-day rolling
windows around the team-specific last T3 evaluator vote.

## V9 outputs

- `m4_churn_magnitude.csv`: clean and all churn, clean-file counts, and clean
  share by team-semester and checkpoint.
- `m4_commit_intensity.csv`: touching-commit counts, median/max clean churn per
  touching commit, and clean-file amplitude. Commit count is contextual, not the
  primary outcome.
- `m4_artifact_composition.csv`: clean source/test events versus excluded or
  non-measurement events under the central policy.
- `m4_rolling_7day_trajectory.csv`: clean churn, clean paths, and event counts
  in 71 overlapping windows from -63 through +7 days relative to T3.
- `m4_churn_magnitude_pooled.csv`, `m4_commit_intensity_pooled.csv`,
  `m4_artifact_composition_pooled.csv`, and
  `m4_rolling_7day_trajectory_pooled.csv`: secondary views aggregated across
  semesters by checkpoint or relative T3 window, without a `Semestre` dimension.

The producer fails fast on a stale or missing code-churn contract and uses the
central `is_measurement_code_path` policy without copying its blacklist.

## V8-to-V9 traceability

| V8 recommendation | V9 decision | Status | Evidence | Limitation |
|---|---|---|---|---|
| Keep M4 in RQ2 and separate it from M3 | Use clean-change outputs without author/activity outcomes | `applied` | Metadata and output contracts | M4 remains descriptive |
| Exclude dependencies and generated paths | Require current v2 contract and central clean-path predicate | `applied` | Producer fail-fast validation | Classification is policy-based |
| Report clean source/test magnitude | Persist clean churn and clean-file counts | `applied` | Magnitude CSV | Provenance is not semantic defect validation |
| Report intensity and path amplitude | Persist per-touching-commit median/max and unique clean paths | `applied` | Intensity CSV | Small denominators remain sensitive |
| Report artifact composition | Persist included versus excluded composition | `applied` | Composition CSV | Excluded categories are grouped for this first contract |
| Add rolling seven-day clean trajectory | Persist 71 overlapping T3-relative windows | `applied` | Rolling CSV | Windows are autocorrelated |
| Do not use commit count as primary M4 result | Keep commit counts contextual in intensity/trajectory | `applied` | Output schemas | M3 remains the activity-count owner |

## Gate status

M4 is implemented for descriptive verification and remains pending manual
approval after its verification notebook is executed end-to-end.
