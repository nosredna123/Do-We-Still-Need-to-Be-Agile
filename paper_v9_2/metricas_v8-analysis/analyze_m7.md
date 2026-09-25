# M7 V8 to V9 Analysis

## V8 baseline

The V8 M7 artifact `paper_v8/data/m7_planning_omission_rate.csv` counts missing
`t1_planning_score` values. The V8 analysis shows that this is a deterministic
duplicate of the absence of observed T1 repository activity and cannot identify
planning omission outside Git.

## V9 decision

Retire the planning-omission interpretation. M7 v9 measures recent repository
inactivity using seven-day retrospective windows anchored to the last evaluator
vote at each checkpoint and to T3 for the daily trajectory. It publishes:

- checkpoint-level inactivity for T1, T2, and T3;
- 71 daily windows from -63 through +7 relative to T3 for each team-semester;
- persistence patterns across checkpoint windows.

M7 is a descriptive repository-coverage and timing diagnostic. It is not a
planning-quality score, is not an independent M9 predictor, and does not observe
off-repository work.

## V8 to V9 traceability matrix

| v8_recommendation | v9_decision | status | evidence | limitation_or_approval |
|---|---|---|---|---|
| Do not interpret missing T1 score as planning omission. | Replace the legacy omission rate with `repository_inactivity` outputs. | applied | `m7_repository_inactivity.metadata.json` | Git cannot observe planning outside the repository. |
| Measure inactivity dynamically around evaluation checkpoints. | Use seven-day retrospective windows anchored to evaluator votes. | applied | `m7_checkpoint_inactivity.csv` | Windows overlap. |
| Distinguish persistent from temporary inactivity. | Publish checkpoint pattern categories and T3-relative daily trajectory. | applied | `m7_inactivity_pattern.csv`, `m7_inactivity_trajectory.csv` | Categories describe Git activity only. |
| Do not duplicate M6a as a planning predictor. | Exclude M7 from M9 predictor inputs. | applied | metadata limitation and `verify_m7.ipynb` | Secondary diagnostic only. |

## Validation evidence

- `paper_v9/tests/test_m7.py`: real-contract coverage and resume tests.
- `paper_v9/verification_notebooks/verify_m7.ipynb`: end-to-end schema, anchor,
  coverage, artifact, and descriptive RQ3 checks.
