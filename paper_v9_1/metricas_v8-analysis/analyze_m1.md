# M1 V8 Analysis and V9 Decision

## V8 computation

The v8 M1 consumes `data/analysis/student_nlp.parquet`, not Git, transcripts,
or evaluator data. It contains 1,122 scored rows: 187 student responses for
each of six questions at six semester/checkpoint cohorts. Each
`ai_dependency_score` is an integer from 0 to 4. For each `Semestre`,
`temporal_marker`, and question, v8 computes the arithmetic mean. It then
averages the six question means into `ai_dependency_composite_mean`:

`M1(s,c) = mean(question_mean(s,c,q), q = 1..6)`.

The published v8 CSV has six rows and reports six available question families
for every row. The v8 notebook independently reproduced both the question
means and the composite without missing scores or duplicate
student-response/question keys.

## V8 questions and V9 grouping

The six scored questions are preserved as separate M1 families:

| Question | V9 conceptual group | Interpretation |
|---|---|---|
| `ai_benefit` | `ai_benefit` | Perceived benefit of AI |
| `autonomy_tool_dependency` | `autonomy_tool_balance` | Declared autonomy/tool balance preference |
| `ai_career_impact_5y` | `career_impact` | Perceived five-year career impact |
| `career_expectation` | `project_expectations` | Project/career expectation signal |
| `project_challenges` | `project_expectations` | Expected project challenges |
| `project_feeling` | `project_expectations` | Project feeling |

The three `project_expectations` questions remain separate. V9 does not average
heterogeneous questions into a new group score; `perception_family` is the
question id, while `perception_group` is a descriptive taxonomy only.

## Real-data examples

The generated v9 long panel has complete coverage for every item. Examples
(mean, sample standard deviation, n) are:

- `2025.2/T1`: `ai_benefit` 2.1304, 1.0024, 46; `autonomy_tool_dependency`
  3.0870, 0.8901, 46; `project_feeling` 0.1087, 0.4335, 46.
- `2025.2/T3`: `ai_benefit` 2.2500, 0.8987, 40; `ai_career_impact_5y`
  1.3250, 0.8286, 40; `project_feeling` 0.3500, 0.7696, 40.
- `2026.1/T1`: `ai_benefit` 2.0000, 1.0690, 22; `autonomy_tool_dependency`
  2.6364, 0.8477, 22; `project_challenges` 0.1364, 0.3513, 22.

These are cohort summaries, not individual longitudinal changes. The source
has no team-semester key and does not provide a valid respondent panel across
T1--T3.

## V8 comparison and limitations

The v9 producer recomputes the v8 composite only as an audit comparison. Its
maximum absolute difference from the published v8 composite is `2.22e-16`.
The v9 primary output does not publish that composite as a perception result.

The persisted NLP artifact used by M1 does not contain normalized frequency,
task, or tool-use measures. However, the raw student survey does contain
direct self-reported fields for general and software-project AI-use frequency,
AI-use tasks, AI tools used, and prior AI-project experience. These fields are
available evidence for a separate usage/adoption metric, but they are not
included in the M1 v1 perception panel and must not be silently inferred from
`ai_dependency_score`.

The M1 v1 output therefore declares actual-use fields as
`available_but_not_included_in_m1_v1`, rather than
`unavailable_not_measured`. An individual T1--T3 panel and team-semester M1
values remain `unavailable_not_measured` because the current source contracts
do not provide those valid keys or respondent linkage. Existing score labels
are retained for descriptive continuity, not interpreted as validated
dependence or telemetry.

## V8-to-V9 recommendation traceability

This table is the required gate record. It makes clear which v8 analysis
recommendations are already implemented and which remain open.

| V8 recommendation | V9 decision | Status | Evidence | Limitation / approval |
|---|---|---|---|---|
| Replace the single six-question composite with separate indicators | Preserve six question families and use the legacy composite only for audit comparison | `applied` | `m1_rq1_perception_panel_long.csv`; v8 comparison cell | None for the structural split |
| Separate real AI use from perceptions | Extract raw frequency/task/tool fields and prior project experience by `Semestre × temporal_marker` | `applied` | `m1_rq1_usage_*.csv`; M1 metadata | These are self-reports, not telemetry; interpretation remains descriptive |
| Do not call autonomy preference actual dependence | Produce a separate `autonomy_tool_balance` distribution and qualify interpretation | `applied` | `m1_rq1_autonomy_tool_balance.csv` and notebook | The inherited NLP family name remains in the legacy-compatible panel |
| Recategorize career impact into productivity, skills, substitution, risk, and uncertainty | Apply transparent keyword topic coding to the raw career text | `partially_applied` | `m1_rq1_career_impact_topics_exploratory.csv` | Requires human coding and agreement validation before confirmatory use |
| Keep project expectations separate from AI dependence | Keep career expectation, project challenges, and project feeling as separate rows | `applied` | Long and wide M1 outputs | No composite is published |
| Use indicator-specific anchored categories | Add raw categorical distributions for usage and autonomy; retain legacy NLP scores | `partially_applied` | Usage/autonomy CSVs and `score_scale_version=v1` | The NLP rubric still requires redesign and human/LLM agreement study |
| Report proportions, median, IQR, mean, std, and n | Perception, usage, autonomy, and score-distribution outputs publish these summaries where the source supports them | `applied` | M1 output family including `m1_rq1_perception_distribution.csv` | Textual topic proportions remain exploratory and require coding validation |
| Distinguish cohort differences from individual longitudinal change | Report `Semestre × temporal_marker`; mark individual panel unavailable | `applied` | Metadata and temporal-only aggregate | No stable respondent linkage for individual T1--T3 change |
| Regenerate NLP and dependent artifacts after rubric changes | Reuse v8 NLP scores for the legacy-compatible perception panel and add deterministic raw-survey outputs | `partially_applied` | M1 metadata has both input checksums | Reprocessing NLP remains blocked until rubric approval |
| Preserve legacy M1 as sensitivity/baseline analysis | Preserve v8 CSV and compare with maximum error `2.22e-16` | `applied` | Producer and verification notebook | Legacy composite is not the primary v9 result |

### Gate decision

M1 v2 is **APPROVED for the descriptive v9 scope** on 2026-09-24. The approval
covers the separated perception panel, raw self-reported usage distributions,
autonomy distribution, descriptive score distributions, provenance, and
article-ready verification artifacts. The exploratory career-topic coding and
the inherited NLP rubric remain explicitly limited and must not be presented
as validated confirmatory measures.