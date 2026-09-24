# M6 V8 to V9 Analysis

## V8 baseline

The V8 M6 artifact is `paper_v8/data/m6_t1_planning_quality.csv`, which republishes `t1_planning_score` from the legacy team-level signals. The score is an opaque LLM-derived 1--10 assessment of T1 commit-subject text. It is missing for five team-semesters without scored T1 commit text: missingness is not a low planning score.

The V8 analysis separates three concepts that must not be collapsed:

- M6a: observable T1 planning-artifact presence and structural scope;
- M6b: declarative planning content in T1 commit subjects, requiring structured LLM reprocessing;
- M6c: concordance between structural and textual evidence, never a composite quality score.

## V8 ambiguities and decisions

- The legacy score cannot by itself establish architectural or planning quality.
- A repository artifact count or line delta is observable scope, not semantic quality.
- No T1 artifact is distinct from an observed low score; the output preserves availability and absence states.
- Planning may occur outside the repository, so repository absence is not proof of planning absence.
- M6a is deterministic and requires no new LLM call. M6b was executed under the approved protocol and human review was approved on 2026-09-24.

## V9 decision

M6a consumes `data/analysis/planning_metrics.parquet` at `team_semester` grain and publishes one row for each of the 14 observed team-semesters. It retains the canonical `pi-v1` definition and reports:

- T1 artifact presence;
- T1 file count and line delta;
- renamed, deleted, and binary event counts;
- logarithmic structural scope `log(1 + pi_line_delta_t1)` for descriptive visualization;
- explicit availability, reason, measurement status, observation unit, and definition version.

The official M6a output intentionally excludes `t1_planning_score`. The V8 score remains an audit reference in the verification notebook only.

## V8 to V9 traceability matrix

| v8_recommendation | v9_decision | status | evidence | limitation_or_approval |
|---|---|---|---|---|
| Preserve the T1 planning metric at team-semester grain. | Publish one deterministic M6a row per team-semester from `planning_metrics.parquet`. | applied | `m6a_structural_planning.csv` | Structural observation, not semantic quality. |
| Separate structural presence/scope from textual content. | M6a contains structural fields; approved M6b publishes separate validated textual categories. | applied | M6a/M6b outputs and M9 structured associations | No composite M6b score; five cases remain unavailable. |
| Preserve missingness rather than assigning a low score. | Retain `pi_available`, `pi_unavailable_reason`, and `measurement_status`; do not impute a score floor. | applied | M6a schema and metadata | Repository absence does not prove absence of off-repository planning. |
| Do not treat the opaque legacy score as architectural quality. | Exclude `t1_planning_score` from official M6a output and compare it only for audit. | applied | `verify_m6.ipynb`, M6a schema | Legacy score remains a frozen V8 reference. |

## Validation evidence

- `paper_v9/tests/test_m6.py`: focused real-contract and resume tests.
- `paper_v9/verification_notebooks/verify_m6.ipynb`: executed end-to-end; validates RQ3 linkage, schema, ranges, keys, absence policy, traceability, legacy comparison, figures, and preliminary analysis.
- Article-ready M6a figures are generated from official CSV outputs in HTML, PDF, SVG, and PNG formats.

## Interpretation boundary

M6a is an exploratory structural baseline for RQ3. It describes whether T1 planning artifacts were observed and their repository-visible scope. It does not measure architectural quality, planning intent, effort, project success, or causality. M6b is approved for exploratory use through separate structured fields for nine observed team-semesters; five remain `unavailable_not_measured`, and no composite score is produced.
