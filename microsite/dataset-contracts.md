# Public dataset contracts

This document is generated from the frozen [public catalog](data/catalog.json).
It describes public fields only, not private source-column mappings or input
fingerprints. The catalog remains authoritative for exact definitions, filters,
coverage, eligibility, figure mappings, and fixed statistical populations.
The original privately approved preparation contract is retained outside the
publication directory. This public documentation does not replace or extend that
approval. Changed data or metadata require renewed review.

There are 49 datasets and 510 column descriptors. JSON and CSV preserve the same
ordered rows and columns, exact numeric values, boolean states, and nulls.
Team identity is always cohort plus team; surveys and global transcript aggregates
must not be joined to teams. No verbatim excerpts are included. Small cells and
approved cohort/team labels retain residual linkage risk; human directory and
actual-host approval remain separate publication gates.

## m1-perceptions: Coded perceptions

**Grain:** Cohort / checkpoint / perception family

**Key:** ["cohort", "checkpoint", "perception_family"]

**Definition:** Six separately coded 0-4 perception families; retain mean, standard deviation, quantiles, and coverage.

**Denominator:** Observed family responses / all observed cohort-checkpoint responses.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / checkpoint / perception family", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "perception_family", "label": "Perception family", "fields": ["perception_family"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Self-report is not AI-use telemetry. Standard deviation is not a confidence interval.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m1-perceptions.json) / [Full CSV](data/downloads/m1-perceptions.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| perception_family | Perception family | string | false | label | Perception family in the stated row grain; use this dataset's denominator and temporal scope. |  |
| perception_group | Perception group | string | false | label | Perception group in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean | Mean | number | false | coded score points (0-4) | Mean in the stated row grain; use this dataset's denominator and temporal scope. |  |
| std | Standard deviation | number | true | coded score points (0-4) | Observed score standard deviation in the dataset's scale, not a confidence interval. |  |
| median | Median | number | false | coded score points (0-4) | Median in the stated row grain; use this dataset's denominator and temporal scope. |  |
| q1 | First quartile | number | false | coded score points (0-4) | First quartile in the stated row grain; use this dataset's denominator and temporal scope. |  |
| q3 | Third quartile | number | false | coded score points (0-4) | Third quartile in the stated row grain; use this dataset's denominator and temporal scope. |  |
| iqr | Interquartile range | number | false | coded score points (0-4) | Interquartile range in the stated row grain; use this dataset's denominator and temporal scope. |  |
| response_n | Response count | integer | false | responses | Observed responses for this measure/role/family and cell, not total enrollment. |  |
| cohort_response_n | Cohort response count | integer | false | responses | All observed responses in the same cohort-checkpoint cell. |  |
| coverage | Coverage | number | false | fraction (0-1) | Observed family responses divided by observed cohort-checkpoint responses. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |

## m1-frequency: AI-use frequency

**Grain:** Cohort / checkpoint / measure / category

**Key:** ["cohort", "checkpoint", "measure", "category"]

**Definition:** General and software-related AI-use frequency distributions.

**Denominator:** Category count / observed respondents for that measure and cell.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / checkpoint / measure / category", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "measure", "label": "Measure", "fields": ["measure"], "mode": "multi_select"}, {"id": "category", "label": "Category", "fields": ["category"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Observed answers are not course enrollment; categories remain ordered labels.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m1-frequency.json) / [Full CSV](data/downloads/m1-frequency.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| measure | Measure | string | false | label | Measure in the stated row grain; use this dataset's denominator and temporal scope. |  |
| category | Category | string | false | label | Category in the stated row grain; use this dataset's denominator and temporal scope. |  |
| count | Count | integer | false | responses | Count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| respondent_n | Respondent count | integer | false | responses | Observed respondents answering the row's measure; multi-select shares may overlap. |  |
| share | Share | number | false | fraction (0-1) | Category count divided by observed respondent count in the same measure/cell; multi-select categories can overlap. |  |

## m1-tasks: AI-use tasks

**Grain:** Cohort / checkpoint / measure / category

**Key:** ["cohort", "checkpoint", "measure", "category"]

**Definition:** Multi-select AI-assisted task categories.

**Denominator:** Respondents selecting the task / respondents in that cell.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / checkpoint / measure / category", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "measure", "label": "Measure", "fields": ["measure"], "mode": "multi_select"}, {"id": "category", "label": "Category", "fields": ["category"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Shares need not sum to one; self-report is not telemetry.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m1-tasks.json) / [Full CSV](data/downloads/m1-tasks.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| measure | Measure | string | false | label | Measure in the stated row grain; use this dataset's denominator and temporal scope. |  |
| category | Category | string | false | label | Category in the stated row grain; use this dataset's denominator and temporal scope. |  |
| count | Count | integer | false | responses | Count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| respondent_n | Respondent count | integer | false | responses | Observed respondents answering the row's measure; multi-select shares may overlap. |  |
| share | Share | number | false | fraction (0-1) | Category count divided by observed respondent count in the same measure/cell; multi-select categories can overlap. |  |

## m1-tools: Reported AI tools

**Grain:** Cohort / checkpoint / measure / category

**Key:** ["cohort", "checkpoint", "measure", "category"]

**Definition:** Multi-select tool categories, retaining the approved source vocabulary.

**Denominator:** Respondents selecting the tool / respondents in that cell.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / checkpoint / measure / category", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "measure", "label": "Measure", "fields": ["measure"], "mode": "multi_select"}, {"id": "category", "label": "Category", "fields": ["category"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Shares need not sum to one. Similar spellings are not silently merged.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m1-tools.json) / [Full CSV](data/downloads/m1-tools.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| measure | Measure | string | false | label | Measure in the stated row grain; use this dataset's denominator and temporal scope. |  |
| category | Category | string | false | label | Category in the stated row grain; use this dataset's denominator and temporal scope. |  |
| count | Count | integer | false | responses | Count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| respondent_n | Respondent count | integer | false | responses | Observed respondents answering the row's measure; multi-select shares may overlap. |  |
| share | Share | number | false | fraction (0-1) | Category count divided by observed respondent count in the same measure/cell; multi-select categories can overlap. |  |

## m1-prior-experience: Prior AI project experience

**Grain:** Cohort / checkpoint / measure / category

**Key:** ["cohort", "checkpoint", "measure", "category"]

**Definition:** Prior AI-assisted project experience.

**Denominator:** Category count / observed answers.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / checkpoint / measure / category", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "measure", "label": "Measure", "fields": ["measure"], "mode": "multi_select"}, {"id": "category", "label": "Category", "fields": ["category"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Not a count of all enrolled students or observed tool usage.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m1-prior-experience.json) / [Full CSV](data/downloads/m1-prior-experience.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| measure | Measure | string | false | label | Measure in the stated row grain; use this dataset's denominator and temporal scope. |  |
| category | Category | string | false | label | Category in the stated row grain; use this dataset's denominator and temporal scope. |  |
| count | Count | integer | false | responses | Count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| respondent_n | Respondent count | integer | false | responses | Observed respondents answering the row's measure; multi-select shares may overlap. |  |
| share | Share | number | false | fraction (0-1) | Category count divided by observed respondent count in the same measure/cell; multi-select categories can overlap. |  |

## m1-autonomy: Autonomy and tool balance

**Grain:** Cohort / checkpoint / measure / integer category

**Key:** ["cohort", "checkpoint", "measure", "category"]

**Definition:** Distribution of the raw 1-5 autonomy item.

**Denominator:** Category count / observed answers.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / checkpoint / measure / integer category", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "measure", "label": "Measure", "fields": ["measure"], "mode": "multi_select"}, {"id": "category", "label": "Category", "fields": ["category"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["This is not the coded 0-4 autonomy perception family; do not rescale or combine them.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m1-autonomy.json) / [Full CSV](data/downloads/m1-autonomy.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| measure | Measure | string | false | label | Measure in the stated row grain; use this dataset's denominator and temporal scope. |  |
| category | Category | integer | false | Likert points (1-5) | Category in the stated row grain; use this dataset's denominator and temporal scope. |  |
| count | Count | integer | false | responses | Count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| respondent_n | Respondent count | integer | false | responses | Observed respondents answering the row's measure; multi-select shares may overlap. |  |
| share | Share | number | false | fraction (0-1) | Category count divided by observed respondent count in the same measure/cell; multi-select categories can overlap. |  |

## m1-career-topics: Exploratory career-impact topics

**Grain:** Cohort / checkpoint / topic

**Key:** ["cohort", "checkpoint", "topic"]

**Definition:** Rule-based supplementary topic coding.

**Denominator:** Topic assignments in the category / all topic assignments in that cell, not respondents.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / checkpoint / topic", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "topic", "label": "Topic", "fields": ["topic"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Unvalidated exploratory coding; no respondent-prevalence or confirmatory interpretation.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m1-career-topics.json) / [Full CSV](data/downloads/m1-career-topics.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| topic | Topic | string | false | label | Topic in the stated row grain; use this dataset's denominator and temporal scope. |  |
| count | Count | integer | false | topic assignments | Count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| topic_assignment_n | Topic assignment count | integer | false | topic assignments | Total topic assignments in the cell, not distinct respondents. |  |
| share_of_topic_assignments | Share of topic assignments | number | false | fraction (0-1) | Category topic assignments / all topic assignments, not respondent prevalence. |  |
| coding_status | Coding status | string | false | label | Coding status in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m2-role-distributions: Role transformation: agreement distributions

**Grain:** Cohort / checkpoint / role / Likert score

**Key:** ["cohort", "checkpoint", "role", "score"]

**Definition:** 1-5 Likert agreement about role extinction or severe transformation.

**Denominator:** Score-category responses / observed responses for that role and cell.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / checkpoint / role / Likert score", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "role", "label": "Role", "fields": ["role"], "mode": "multi_select"}, {"id": "score", "label": "Score", "fields": ["score"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["The prompt combines extinction and transformation. There is no team identifier.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m2-role-distributions.json) / [Full CSV](data/downloads/m2-role-distributions.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| role | Role | string | false | label | Role in the stated row grain; use this dataset's denominator and temporal scope. |  |
| score | Score | integer | false | Likert points (1-5) | Score in the stated row grain; use this dataset's denominator and temporal scope. |  |
| count | Count | integer | false | responses | Count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| respondent_n | Respondent count | integer | false | responses | Observed respondents answering the row's measure; multi-select shares may overlap. |  |
| share | Share | number | false | fraction (0-1) | Category count divided by observed respondent count in the same measure/cell; multi-select categories can overlap. |  |

## m2-role-summaries: Role transformation: summaries

**Grain:** Cohort / checkpoint / role

**Key:** ["cohort", "checkpoint", "role"]

**Definition:** Summary scores and response shares on the original 1-5 scale.

**Denominator:** Observed role-specific responses; disagreement 1-2, neutral 3, agreement 4-5.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / checkpoint / role", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "role", "label": "Role", "fields": ["role"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Survey summaries cannot be attached to teams; no inferred team filter.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m2-role-summaries.json) / [Full CSV](data/downloads/m2-role-summaries.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| role | Role | string | false | label | Role in the stated row grain; use this dataset's denominator and temporal scope. |  |
| response_n | Response count | integer | false | responses | Observed responses for this measure/role/family and cell, not total enrollment. |  |
| mean | Mean | number | false | Likert points (1-5) | Mean in the stated row grain; use this dataset's denominator and temporal scope. |  |
| std | Standard deviation | number | true | Likert points (1-5) | Observed score standard deviation in the dataset's scale, not a confidence interval. |  |
| median | Median | number | false | Likert points (1-5) | Median in the stated row grain; use this dataset's denominator and temporal scope. |  |
| q1 | First quartile | number | false | Likert points (1-5) | First quartile in the stated row grain; use this dataset's denominator and temporal scope. |  |
| q3 | Third quartile | number | false | Likert points (1-5) | Third quartile in the stated row grain; use this dataset's denominator and temporal scope. |  |
| iqr | Interquartile range | number | false | Likert points (1-5) | Interquartile range in the stated row grain; use this dataset's denominator and temporal scope. |  |
| disagreement_share | Disagreement share | number | false | fraction (0-1) | Disagreement share in the stated row grain; use this dataset's denominator and temporal scope. |  |
| neutral_share | Neutral share | number | false | fraction (0-1) | Neutral share in the stated row grain; use this dataset's denominator and temporal scope. |  |
| agreement_share | Agreement share | number | false | fraction (0-1) | Agreement share in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m2-paired-sensitivity: Role transformation: paired sensitivity

**Grain:** Cohort / role / observed T1-T3 pairs

**Key:** ["cohort", "role"]

**Definition:** T3 minus T1 changes among respondents observed at both checkpoints.

**Denominator:** Observed paired respondents for each cohort and role.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / role / observed T1-T3 pairs", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "role", "label": "Role", "fields": ["role"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Sensitivity evidence, not a longitudinal census. No respondent or team keys are public.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m2-paired-sensitivity.json) / [Full CSV](data/downloads/m2-paired-sensitivity.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| role | Role | string | false | label | Role in the stated row grain; use this dataset's denominator and temporal scope. |  |
| pair_n | Pair count | integer | false | paired respondents | Observed paired T1-T3 respondents for this cohort and role. |  |
| mean_t1 | T1 mean | number | false | Likert points (1-5) | T1 mean in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_t3 | T3 mean | number | false | Likert points (1-5) | T3 mean in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_change | Mean change | number | false | Likert points (1-5) | Mean observed within-person T3-minus-T1 Likert change among observed pairs. |  |
| median_change | Median change | number | false | Likert points (1-5) | Median observed within-person T3-minus-T1 Likert change among observed pairs. |  |
| increased_share | Increased share | number | false | fraction (0-1) | Increased share in the stated row grain; use this dataset's denominator and temporal scope. |  |
| unchanged_share | Unchanged share | number | false | fraction (0-1) | Unchanged share in the stated row grain; use this dataset's denominator and temporal scope. |  |
| decreased_share | Decreased share | number | false | fraction (0-1) | Decreased share in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m3-participation: Repository activity around T3

**Grain:** Team-semester

**Key:** ["cohort", "team_id"]

**Definition:** T3 +/- 7 days (14 days): pre [T3-7d,T3), post [T3,T3+7d); final window is their union.

**Denominator:** Pre/post/final-window commits / all observed history before T3+7 days.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["This is not the separate final-seven concentration measure. Counts do not measure coordination quality.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m3-participation.json) / [Full CSV](data/downloads/m3-participation.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| total_commit_n | Total commit count | integer | false | commits | Total commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| pre_commit_n | Pre commit count | integer | false | commits | Pre commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| post_commit_n | Post commit count | integer | false | commits | Post commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| final_window_commit_n | Final window commit count | integer | false | commits | Final window commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| pre_share | Pre share | number | true | fraction (0-1) | Pre share in the stated row grain; use this dataset's denominator and temporal scope. |  |
| post_share | Post share | number | true | fraction (0-1) | Post share in the stated row grain; use this dataset's denominator and temporal scope. |  |
| final_window_share | Final window share | number | true | fraction (0-1) | Commits in the 14-day union around T3 / observed history before T3+7 days. |  |
| small_denominator_lt_10 | Small denominator lt 10 | boolean | false | boolean | Small denominator lt 10 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |

## m3-author-concentration: Author concentration around T3

**Grain:** Team-semester / pre or post phase

**Key:** ["cohort", "team_id", "phase"]

**Definition:** Author activity in the seven-day pre-T3 and seven-day post-T3 windows.

**Denominator:** Maximum local-author commits / phase commits; Gini uses observed local-author activity.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester / pre or post phase", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load.", "no_observed_activity": "Observed zero counts; max_author_share and author_gini are null."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "phase", "label": "Phase", "fields": ["phase"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["No activity gives zero counts but null concentration, not perfect equality or zero concentration.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m3-author-concentration.json) / [Full CSV](data/downloads/m3-author-concentration.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| phase | Phase | string | false | label | Phase in the stated row grain; use this dataset's denominator and temporal scope. |  |
| commit_n | Commit count | integer | false | commits | Commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| active_days | Active days | integer | false | days | Active days in the stated row grain; use this dataset's denominator and temporal scope. |  |
| author_n | Author count | integer | false | authors | Author count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| max_author_share | Max author share | number | true | fraction (0-1) | Max author share in the stated row grain; use this dataset's denominator and temporal scope. |  |
| author_gini | Author gini | number | true | Gini (0-1) | Author gini in the stated row grain; use this dataset's denominator and temporal scope. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |

## m3-rolling: Seven-day rolling activity

**Grain:** Team-semester / relative window-end day

**Key:** ["cohort", "team_id", "window_end_day"]

**Definition:** 29 overlapping seven-day windows per team-semester.

**Denominator:** Concentration uses commits within [offset-7,offset), relative to T3.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester / relative window-end day", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load.", "no_observed_activity": "Observed zero counts; max_author_share and author_gini are null."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "window_end_day", "label": "Window end day", "fields": ["window_end_day"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Windows overlap and are not independent project observations.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m3-rolling.json) / [Full CSV](data/downloads/m3-rolling.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| window_end_day | Window end day | integer | false | days relative to T3 | Window end day in the stated row grain; use this dataset's denominator and temporal scope. |  |
| commit_n | Commit count | integer | false | commits | Commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| active_days | Active days | integer | false | days | Active days in the stated row grain; use this dataset's denominator and temporal scope. |  |
| author_n | Author count | integer | false | authors | Author count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| max_author_share | Max author share | number | true | fraction (0-1) | Max author share in the stated row grain; use this dataset's denominator and temporal scope. |  |
| author_gini | Author gini | number | true | Gini (0-1) | Author gini in the stated row grain; use this dataset's denominator and temporal scope. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |

## m3-rolling-pooled: Pooled seven-day activity

**Grain:** Relative window-end day / fixed pooled population

**Key:** ["window_end_day"]

**Definition:** Fixed pooled rolling summaries across cohorts, not a selected-team estimate.

**Denominator:** Active team-semesters / all team-semesters; concentration medians exclude unavailable values.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Relative window-end day / fixed pooled population", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "window_end_day", "label": "Window end day", "fields": ["window_end_day"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["No cohort/team filter or recomputation of the pooled medians.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m3-rolling-pooled.json) / [Full CSV](data/downloads/m3-rolling-pooled.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| window_end_day | Window end day | integer | false | days relative to T3 | Window end day in the stated row grain; use this dataset's denominator and temporal scope. |  |
| team_semester_n | Team semester count | integer | false | team-semesters | Team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| active_team_semester_n | Active team semester count | integer | false | team-semesters | Active team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| total_commit_n | Total commit count | integer | false | commits | Total commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_commit_n | Mean commit count | number | false | commits | Mean commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_commit_n | Median commit count | number | false | commits | Median commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| max_commit_n | Max commit count | integer | false | commits | Max commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_active_days | Median active days | number | false | days | Median active days in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_max_author_share | Median max author share | number | true | fraction (0-1) | Median max author share in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_author_gini | Median author gini | number | true | Gini (0-1) | Median author gini in the stated row grain; use this dataset's denominator and temporal scope. |  |
| active_team_semester_share | Active team semester share | number | false | fraction (0-1) | Active team semester share in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m4-checkpoint-churn: Clean changed lines by checkpoint

**Grain:** Team-semester / checkpoint

**Key:** ["cohort", "team_id", "checkpoint"]

**Definition:** Clean source/test path activity, separate from all-path churn and file/commit counts.

**Denominator:** Clean changed lines / all changed lines; commit summaries use clean-touching commits.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester / checkpoint", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load.", "no_clean_change_observed": "Observed team; undefined ratios and commit summaries are null."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Clean-path provenance is not semantic defect validation; no clean change is not a missing team.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m4-checkpoint-churn.json) / [Full CSV](data/downloads/m4-checkpoint-churn.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| clean_churn | Clean churn | integer | false | changed lines | Clean churn in the stated row grain; use this dataset's denominator and temporal scope. |  |
| all_churn | All churn | integer | false | changed lines | All churn in the stated row grain; use this dataset's denominator and temporal scope. |  |
| clean_unique_file_n | Clean unique file count | integer | false | clean files | Clean unique file count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| clean_touching_commit_n | Clean touching commit count | integer | false | commits | Clean touching commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_clean_churn_per_touching_commit | Median clean churn per touching commit | number | true | changed lines | Median clean churn per touching commit in the stated row grain; use this dataset's denominator and temporal scope. |  |
| max_clean_churn_per_touching_commit | Max clean churn per touching commit | integer | true | changed lines | Max clean churn per touching commit in the stated row grain; use this dataset's denominator and temporal scope. |  |
| clean_share_of_all_churn | Clean share of all churn | number | true | fraction (0-1) | Clean changed lines divided by all-path changed lines in the same row scope. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |

## m4-checkpoint-pooled: Pooled clean changed lines

**Grain:** Checkpoint / fixed pooled population

**Key:** ["checkpoint"]

**Definition:** Original pooled sums and medians; observed-clean coverage is 7, 10, and 14 at T1, T2, and T3.

**Denominator:** Total clean changed lines / total all-path changed lines.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Checkpoint / fixed pooled population", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["No cohort/team filtering or new medians of a selected subset.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m4-checkpoint-pooled.json) / [Full CSV](data/downloads/m4-checkpoint-pooled.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| team_semester_n | Team semester count | integer | false | team-semesters | Team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| observed_clean_team_semester_n | Observed clean team semester count | integer | false | team-semesters | Observed clean team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| total_clean_churn | Total clean churn | integer | false | changed lines | Total clean churn in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_clean_churn | Median clean churn | number | false | changed lines | Median clean churn in the stated row grain; use this dataset's denominator and temporal scope. |  |
| total_all_churn | Total all churn | integer | false | changed lines | Total all churn in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_clean_unique_file_n | Median clean unique file count | number | false | clean files | Median clean unique file count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| clean_share_of_all_churn | Clean share of all churn | number | true | fraction (0-1) | Clean changed lines divided by all-path changed lines in the same row scope. |  |

## m4-path-composition: Pooled path-category composition

**Grain:** Checkpoint / file category

**Key:** ["checkpoint", "file_category"]

**Definition:** Separate clean-path inclusion flags, file events, distinct files, and changed lines.

**Denominator:** Category changed lines / all category changed lines, including excluded paths.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Checkpoint / file category", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "file_category", "label": "File category", "fields": ["file_category"], "mode": "multi_select"}, {"id": "included_in_m4", "label": "Included in M4", "fields": ["included_in_m4"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Pooled event and distinct-file counts are different units; do not reconstruct identities.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m4-path-composition.json) / [Full CSV](data/downloads/m4-path-composition.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| file_category | File category | string | false | label | File category in the stated row grain; use this dataset's denominator and temporal scope. |  |
| included_in_m4 | Included in M4 | boolean | false | boolean | Included in M4 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| team_semester_n | Team semester count | integer | false | team-semesters | Team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| file_event_n | File event count | integer | false | file events | File event count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| unique_file_n | Unique file count | integer | false | files | Unique file count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| churn_lines | Churn lines | integer | false | changed lines | Churn lines in the stated row grain; use this dataset's denominator and temporal scope. |  |
| churn_share | Churn share | number | true | fraction (0-1) | Category changed lines / all category changed lines, including clean-policy exclusions. |  |

## m5-marker-density: Transcript lexical density

**Grain:** Checkpoint / one global 2025.2 corpus

**Key:** ["checkpoint"]

**Definition:** Lexical counts and density in the measured global transcript corpus.

**Denominator:** Friction-marker matches / tokens * 1000.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Checkpoint / one global 2025.2 corpus", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "cohorts": ["2025.2"], "team_attribution": false}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Candidate textual markers, not diagnoses. No team attribution or 2026.1 observations.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m5-marker-density.json) / [Full CSV](data/downloads/m5-marker-density.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| transcript_chunk_n | Transcript chunk count | integer | false | transcript chunks | Transcript chunk count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| source_session_n | Source session count | integer | false | source sessions | Source session count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| character_n | Character count | integer | false | characters | Character count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| token_n | Token count | integer | false | tokens | Token count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| friction_marker_n | Friction marker count | integer | false | lexical matches | Friction marker count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| alignment | Alignment | integer | false | lexical matches | Alignment in the stated row grain; use this dataset's denominator and temporal scope. |  |
| handoff | Handoff | integer | false | lexical matches | Handoff in the stated row grain; use this dataset's denominator and temporal scope. |  |
| integration | Integration | integer | false | lexical matches | Integration in the stated row grain; use this dataset's denominator and temporal scope. |  |
| blocker | Blocker | integer | false | lexical matches | Blocker in the stated row grain; use this dataset's denominator and temporal scope. |  |
| rework | Rework | integer | false | lexical matches | Rework in the stated row grain; use this dataset's denominator and temporal scope. |  |
| friction_marker_density_per_1k_tokens | Friction marker density per 1k tokens | number | false | lexical matches per 1000 tokens | All friction-marker matches / corpus tokens * 1000. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |

## m5-marker-composition: Transcript lexical composition

**Grain:** Checkpoint / lexical subtype / one global corpus

**Key:** ["checkpoint", "friction_subtype"]

**Definition:** Five lexical subtypes; composition is distinct from density per token.

**Denominator:** Subtype matches / all friction-marker matches at that checkpoint.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Checkpoint / lexical subtype / one global corpus", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "cohorts": ["2025.2"], "team_attribution": false}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}, {"id": "friction_subtype", "label": "Friction subtype", "fields": ["friction_subtype"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Chunks and sessions are not independent team observations; no team filter.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m5-marker-composition.json) / [Full CSV](data/downloads/m5-marker-composition.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| friction_subtype | Friction subtype | string | false | label | Friction subtype in the stated row grain; use this dataset's denominator and temporal scope. |  |
| friction_marker_n | Friction marker count | integer | false | lexical matches | Friction marker count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| marker_n | Marker count | integer | false | lexical matches | Marker count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| marker_share | Marker share | number | false | fraction (0-1) | Lexical subtype matches / all friction-marker matches at this checkpoint. |  |

## m5-corpus-coverage: Transcript corpus coverage

**Grain:** Checkpoint / one global 2025.2 corpus

**Key:** ["checkpoint"]

**Definition:** 35, 37, and 28 chunks at T1, T2, and T3, with session, token, and character counts.

**Denominator:** Coverage counts, not a response-rate denominator.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Checkpoint / one global 2025.2 corpus", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "cohorts": ["2025.2"], "team_attribution": false, "chunks_by_checkpoint": {"T1": 35, "T2": 37, "T3": 28}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Only one measured cohort; never synthesize missing-cohort rows.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m5-corpus-coverage.json) / [Full CSV](data/downloads/m5-corpus-coverage.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| transcript_chunk_n | Transcript chunk count | integer | false | transcript chunks | Transcript chunk count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| source_session_n | Source session count | integer | false | source sessions | Source session count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| character_n | Character count | integer | false | characters | Character count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| token_n | Token count | integer | false | tokens | Token count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| friction_marker_n | Friction marker count | integer | false | lexical matches | Friction marker count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| observed_semester_n | Observed semester count | integer | false | observed cohorts | Observed semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m6a-structural-planning: Structural planning evidence

**Grain:** Team-semester / T1

**Key:** ["cohort", "team_id"]

**Definition:** Repository artifact presence and log(1+changed-line scope) at T1; artifact activity is an event count.

**Denominator:** Not applicable: observed artifact counts, presence, and line scope.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester / T1", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Presence and scope are not planning quality. No repository artifact does not prove no off-repository planning.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m6a-structural-planning.json) / [Full CSV](data/downloads/m6a-structural-planning.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| pi_available | Structural artifact available | boolean | false | boolean | Structural planning evidence measurement availability, distinct from artifact presence. |  |
| pi_file_count_t1 | T1 artifact file count | integer | false | files | Observed T1 structural planning artifact files. |  |
| pi_line_delta_t1 | T1 artifact changed-line scope | integer | false | changed lines | Observed T1 structural artifact additions plus deletions, in changed lines. |  |
| pi_renamed_count_t1 | Artifact renamed count T1 | integer | false | file events | Artifact renamed count T1 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| pi_deleted_count_t1 | Artifact deleted count T1 | integer | false | file events | Artifact deleted count T1 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| pi_binary_event_count_t1 | Artifact binary event count T1 | integer | false | file events | Artifact binary event count T1 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| planning_artifact_activity_t1 | Planning artifact activity T1 | integer | false | artifact events | Integer number of structural artifact events at T1, not a boolean. |  |
| planning_artifact_present_t1 | Planning artifact present T1 | boolean | false | boolean | Repository structural artifact presence at T1, not planning quality. |  |
| planning_scope_log1p_t1 | Planning scope log(1 + scope) T1 | number | false | natural log(1 + changed lines) | Natural logarithm of one plus T1 artifact changed-line scope. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |

## m7-checkpoint-inactivity: Checkpoint repository inactivity

**Grain:** Team-semester / checkpoint

**Key:** ["cohort", "team_id", "checkpoint"]

**Definition:** Checkpoint-specific seven-day inactivity flags and observed commit counts.

**Denominator:** Commit count in seven days before that checkpoint's evaluator anchor.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester / checkpoint", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Inactivity does not identify planning omission or off-repository work; not an M9 planning predictor.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m7-checkpoint-inactivity.json) / [Full CSV](data/downloads/m7-checkpoint-inactivity.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| commit_n_7d | Commit count 7d | integer | false | commits | Commit count 7d in the stated row grain; use this dataset's denominator and temporal scope. |  |
| repository_inactive_7d | Repository inactive 7d | boolean | false | boolean | Repository inactive 7d in the stated row grain; use this dataset's denominator and temporal scope. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |

## m8-rework-magnitude: Clean rework magnitude and eligibility

**Grain:** Team-semester / T3

**Key:** ["cohort", "team_id"]

**Definition:** Path-provenance rework/deferred magnitudes with baseline eligibility and explicit ratio status.

**Denominator:** Rework changed lines / total clean T3 changed lines, only with observed baseline and positive total.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester / T3", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}, "baseline_eligible": 12, "baseline_not_observed": 2}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load.", "ratio_status": ["available", "baseline_not_observed", "zero_clean_churn"], "precedence": "baseline_not_observed before zero_clean_churn"}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "baseline_eligible_for_rework_t3", "label": "Baseline eligible for rework T3", "fields": ["baseline_eligible_for_rework_t3"], "mode": "multi_select"}, {"id": "ratio_status", "label": "Ratio status", "fields": ["ratio_status"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Not verified defects. Ineligible and zero-denominator ratios are null, even if a source cell was numeric.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m8-rework-magnitude.json) / [Full CSV](data/downloads/m8-rework-magnitude.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| clean_rework_churn_t3 | Clean rework churn T3 | integer | false | changed lines | Clean T3 changed lines on paths observed in the prior baseline; path provenance, not verified defects. |  |
| clean_deferred_churn_t3 | Clean deferred churn T3 | integer | false | changed lines | Clean T3 changed lines on paths not observed in the prior baseline. |  |
| prior_clean_path_n | Prior clean path count | integer | false | clean files | Distinct prior observed clean paths used to establish the rework baseline. |  |
| clean_total_churn_t3 | Clean total churn T3 | integer | false | changed lines | All clean changed lines at T3, the ratio denominator. |  |
| baseline_eligible_for_rework_t3 | Baseline eligible for rework T3 | boolean | false | boolean | True exactly when prior observed clean-path count is greater than zero. |  |
| clean_rework_ratio_t3 | Clean rework ratio T3 | number | true | fraction (0-1) | Clean T3 rework lines divided by total clean T3 lines; null unless baseline eligible and total positive. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |
| ratio_status | Ratio status | string | false | label | available, baseline_not_observed, or zero_clean_churn; baseline absence takes precedence. |  |

## m8-baseline-eligibility: Rework baseline eligibility

**Grain:** Team-semester / T3

**Key:** ["cohort", "team_id"]

**Definition:** Prior clean paths and observed baseline status for interpreting rework ratios.

**Denominator:** Eligibility is prior clean-path count > 0; 12 of 14 cases are baseline eligible.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester / T3", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}, "baseline_eligible": 12, "baseline_not_observed": 2}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "baseline_eligible_for_rework_t3", "label": "Baseline eligible for rework T3", "fields": ["baseline_eligible_for_rework_t3"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Baseline not observed is not proof that no prior work existed.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m8-baseline-eligibility.json) / [Full CSV](data/downloads/m8-baseline-eligibility.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| prior_clean_path_n | Prior clean path count | integer | false | clean files | Distinct prior observed clean paths used to establish the rework baseline. |  |
| baseline_eligible_for_rework_t3 | Baseline eligible for rework T3 | boolean | false | boolean | True exactly when prior observed clean-path count is greater than zero. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |

## m9-structural-rework-magnitude: Structural planning / rework magnitude associations

**Grain:** Fixed analysis / predictor / outcome

**Key:** ["analysis_id", "predictor", "outcome"]

**Definition:** Spearman associations in the all-team-semesters stratum.

**Denominator:** Pairwise measured team-semesters; original sample_n (14 in this snapshot).

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Fixed analysis / predictor / outcome", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "analysis_id", "label": "Analysis identifier", "fields": ["analysis_id"], "mode": "multi_select"}, {"id": "predictor", "label": "Predictor", "fields": ["predictor"], "mode": "multi_select"}, {"id": "outcome", "label": "Outcome", "fields": ["outcome"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Exploratory, non-causal, no subset recomputation or confirmatory p-value claims.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m9-structural-rework-magnitude.json) / [Full CSV](data/downloads/m9-structural-rework-magnitude.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| analysis_id | Analysis identifier | string | false | label | Analysis identifier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| predictor | Predictor | string | false | label | Predictor in the stated row grain; use this dataset's denominator and temporal scope. |  |
| outcome | Outcome | string | false | label | Outcome in the stated row grain; use this dataset's denominator and temporal scope. |  |
| sample_n | Sample count | integer | false | eligible pairs | Original pairwise sample size for this fixed association; never recomputed on filtered rows. |  |
| spearman_rho | Spearman rho | number | true | Spearman rho (-1 to 1) | Spearman rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| spearman_p_exploratory | Exploratory Spearman p-value | number | true | exploratory p-value (0-1) | Exploratory Spearman p-value in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m9-structural-rework-ratio: Structural planning / eligible rework ratio associations

**Grain:** Fixed analysis / predictor / outcome

**Key:** ["analysis_id", "predictor", "outcome"]

**Definition:** Spearman associations in the baseline-eligible-only stratum.

**Denominator:** Baseline-eligible cases with a defined ratio; original sample_n (12 in this snapshot).

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Fixed analysis / predictor / outcome", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "analysis_id", "label": "Analysis identifier", "fields": ["analysis_id"], "mode": "multi_select"}, {"id": "predictor", "label": "Predictor", "fields": ["predictor"], "mode": "multi_select"}, {"id": "outcome", "label": "Outcome", "fields": ["outcome"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Eligibility restrictions survive filtering; exploratory and non-causal.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m9-structural-rework-ratio.json) / [Full CSV](data/downloads/m9-structural-rework-ratio.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| analysis_id | Analysis identifier | string | false | label | Analysis identifier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| predictor | Predictor | string | false | label | Predictor in the stated row grain; use this dataset's denominator and temporal scope. |  |
| outcome | Outcome | string | false | label | Outcome in the stated row grain; use this dataset's denominator and temporal scope. |  |
| sample_n | Sample count | integer | false | eligible pairs | Original pairwise sample size for this fixed association; never recomputed on filtered rows. |  |
| spearman_rho | Spearman rho | number | true | Spearman rho (-1 to 1) | Spearman rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| spearman_p_exploratory | Exploratory Spearman p-value | number | true | exploratory p-value (0-1) | Exploratory Spearman p-value in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m9-structural-outcomes: Structural planning / evaluator outcomes

**Grain:** Fixed analysis / predictor / outcome

**Key:** ["analysis_id", "predictor", "outcome"]

**Definition:** Separate evaluator dimensions and structural planning predictors.

**Denominator:** Observed pairwise T3 dimension scores; original sample_n.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Fixed analysis / predictor / outcome", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "analysis_id", "label": "Analysis identifier", "fields": ["analysis_id"], "mode": "multi_select"}, {"id": "predictor", "label": "Predictor", "fields": ["predictor"], "mode": "multi_select"}, {"id": "outcome", "label": "Outcome", "fields": ["outcome"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Do not treat separate dimensions as an official global quality score or recalculate correlations.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m9-structural-outcomes.json) / [Full CSV](data/downloads/m9-structural-outcomes.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| analysis_id | Analysis identifier | string | false | label | Analysis identifier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| predictor | Predictor | string | false | label | Predictor in the stated row grain; use this dataset's denominator and temporal scope. |  |
| outcome | Outcome | string | false | label | Outcome in the stated row grain; use this dataset's denominator and temporal scope. |  |
| sample_n | Sample count | integer | false | eligible pairs | Original pairwise sample size for this fixed association; never recomputed on filtered rows. |  |
| spearman_rho | Spearman rho | number | true | Spearman rho (-1 to 1) | Spearman rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| spearman_p_exploratory | Exploratory Spearman p-value | number | true | exploratory p-value (0-1) | Exploratory Spearman p-value in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m9-content-outcomes: Planning-content / evaluator outcomes

**Grain:** Fixed analysis / predictor / outcome

**Key:** ["analysis_id", "predictor", "outcome"]

**Definition:** Separate exploratory associations for structured planning-content predictors.

**Denominator:** Successful measured content cases with observed outcome, at most nine; original sample_n.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Fixed analysis / predictor / outcome", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "analysis_id", "label": "Analysis identifier", "fields": ["analysis_id"], "mode": "multi_select"}, {"id": "predictor", "label": "Predictor", "fields": ["predictor"], "mode": "multi_select"}, {"id": "outcome", "label": "Outcome", "fields": ["outcome"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Unmeasured content is excluded, not zero. No combined content-quality score.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m9-content-outcomes.json) / [Full CSV](data/downloads/m9-content-outcomes.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| analysis_id | Analysis identifier | string | false | label | Analysis identifier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| predictor | Predictor | string | false | label | Predictor in the stated row grain; use this dataset's denominator and temporal scope. |  |
| outcome | Outcome | string | false | label | Outcome in the stated row grain; use this dataset's denominator and temporal scope. |  |
| sample_n | Sample count | integer | false | eligible pairs | Original pairwise sample size for this fixed association; never recomputed on filtered rows. |  |
| spearman_rho | Spearman rho | number | true | Spearman rho (-1 to 1) | Spearman rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| spearman_p_exploratory | Exploratory Spearman p-value | number | true | exploratory p-value (0-1) | Exploratory Spearman p-value in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m9-leave-one-out: Leave-one-out association sensitivity

**Grain:** Analysis / predictor / outcome / omitted team-semester

**Key:** ["analysis_id", "predictor", "outcome", "omitted_cohort", "omitted_team_id"]

**Definition:** Existing omission estimates for the registered associations.

**Denominator:** remaining_sample_n after omission under the original eligibility rule.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Analysis / predictor / outcome / omitted team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "analysis_id", "label": "Analysis identifier", "fields": ["analysis_id"], "mode": "multi_select"}, {"id": "predictor", "label": "Predictor", "fields": ["predictor"], "mode": "multi_select"}, {"id": "outcome", "label": "Outcome", "fields": ["outcome"], "mode": "multi_select"}, {"id": "omitted_cohort", "label": "Omitted cohort", "fields": ["omitted_cohort"], "mode": "multi_select"}, {"id": "omitted_case", "label": "Omitted team-semester", "fields": ["omitted_cohort", "omitted_team_id"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["These ranges are not confidence intervals. Constant or insufficient pairs give null estimates.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m9-leave-one-out.json) / [Full CSV](data/downloads/m9-leave-one-out.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| analysis_id | Analysis identifier | string | false | label | Analysis identifier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| predictor | Predictor | string | false | label | Predictor in the stated row grain; use this dataset's denominator and temporal scope. |  |
| outcome | Outcome | string | false | label | Outcome in the stated row grain; use this dataset's denominator and temporal scope. |  |
| omitted_cohort | Omitted cohort | string | false | label | Omitted cohort in the stated row grain; use this dataset's denominator and temporal scope. |  |
| omitted_team_id | Omitted team within cohort | string | false | label | Omitted team within cohort in the stated row grain; use this dataset's denominator and temporal scope. |  |
| remaining_sample_n | Remaining sample count | integer | false | eligible pairs | Original eligible pair count after the named omitted case. |  |
| spearman_rho | Spearman rho | number | true | Spearman rho (-1 to 1) | Spearman rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| spearman_p_exploratory | Exploratory Spearman p-value | number | true | exploratory p-value (0-1) | Exploratory Spearman p-value in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m6a-presence-by-cohort: Artifact presence by cohort

**Grain:** Cohort / evidence state

**Key:** ["cohort", "evidence_state"]

**Definition:** Two observed artifact-presence states per cohort.

**Denominator:** team_semester_count within state; team_semester_n is the whole cohort denominator.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Cohort / evidence state", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "evidence_state", "label": "Evidence state", "fields": ["evidence_state"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["No new presence percentage or semantic quality score is required.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m6a-presence-by-cohort.json) / [Full CSV](data/downloads/m6a-presence-by-cohort.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| evidence_state | Evidence state | string | false | label | Evidence state in the stated row grain; use this dataset's denominator and temporal scope. |  |
| team_semester_n | Team semester count | integer | false | team-semesters | Team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| team_semester_count | Team semester count | integer | false | team-semesters | Team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |

## planning-rework-profile: Planning scope and rework profile

**Grain:** Team-semester

**Key:** ["cohort", "team_id"]

**Definition:** T1 structural planning fields alongside T3 path-provenance rework and baseline eligibility.

**Denominator:** Not applicable: planning scope and clean T3 rework magnitude, not a ratio.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Planning measurement_status refers to structural evidence, not rework eligibility; log axes cannot show zero.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/planning-rework-profile.json) / [Full CSV](data/downloads/planning-rework-profile.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| pi_file_count_t1 | T1 artifact file count | integer | false | files | Observed T1 structural planning artifact files. |  |
| pi_line_delta_t1 | T1 artifact changed-line scope | integer | false | changed lines | Observed T1 structural artifact additions plus deletions, in changed lines. |  |
| planning_artifact_present_t1 | Planning artifact present T1 | boolean | false | boolean | Repository structural artifact presence at T1, not planning quality. |  |
| planning_scope_log1p_t1 | Planning scope log(1 + scope) T1 | number | false | natural log(1 + changed lines) | Natural logarithm of one plus T1 artifact changed-line scope. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |
| clean_rework_churn_t3 | Clean rework churn T3 | integer | false | changed lines | Clean T3 changed lines on paths observed in the prior baseline; path provenance, not verified defects. |  |
| baseline_eligible_for_rework_t3 | Baseline eligible for rework T3 | boolean | false | boolean | True exactly when prior observed clean-path count is greater than zero. |  |

## complexity-rework-figure: Evaluated complexity and rework

**Grain:** Team-semester

**Key:** ["cohort", "team_id"]

**Definition:** T3 evaluator-rated complexity and clean rework magnitude with fixed planning tiers.

**Denominator:** Rework ratio uses eligible positive-total cases only; magnitude remains available for all cases.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load.", "ratio_status": ["available", "baseline_not_observed", "zero_clean_churn"], "precedence": "baseline_not_observed before zero_clean_churn"}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "planning_scope_tier", "label": "Planning scope tier", "fields": ["planning_scope_tier"], "mode": "multi_select"}, {"id": "baseline_eligible_for_rework_t3", "label": "Baseline eligible for rework T3", "fields": ["baseline_eligible_for_rework_t3"], "mode": "multi_select"}, {"id": "ratio_status", "label": "Ratio status", "fields": ["ratio_status"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Descriptive co-variation, not causal adjustment. Evaluated and repository structural complexity differ.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/complexity-rework-figure.json) / [Full CSV](data/downloads/complexity-rework-figure.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| technical_complexity_mean_t3 | Technical complexity mean T3 | number | false | evaluator score points | Mean evaluator technical-complexity score at T3, not repository structural inference. |  |
| clean_rework_churn_t3 | Clean rework churn T3 | integer | false | changed lines | Clean T3 changed lines on paths observed in the prior baseline; path provenance, not verified defects. |  |
| clean_rework_ratio_t3 | Clean rework ratio T3 | number | true | fraction (0-1) | Clean T3 rework lines divided by total clean T3 lines; null unless baseline eligible and total positive. |  |
| planning_scope_tier | Planning scope tier | string | false | label | Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median. |  |
| planning_scope_log1p_t1 | Planning scope log(1 + scope) T1 | number | false | natural log(1 + changed lines) | Natural logarithm of one plus T1 artifact changed-line scope. |  |
| score_trajectory_group | Score trajectory group | string | false | label | Existing improved/stable/declined grouping under the registered adaptive signed 0.125 threshold. |  |
| final7_commit_share_pct | Final7 commit share (%) | number | false | percentage points (0-100) | Final-seven commits / all observed project commits strictly before T3 * 100. |  |
| final7_clean_churn_share_pct | Final7 clean churn share (%) | number | false | percentage points (0-100) | Final-seven clean changed lines / all observed project clean changed lines strictly before T3 * 100. |  |
| baseline_eligible_for_rework_t3 | Baseline eligible for rework T3 | boolean | false | boolean | True exactly when prior observed clean-path count is greater than zero. |  |
| ratio_status | Ratio status | string | false | label | available, baseline_not_observed, or zero_clean_churn; baseline absence takes precedence. |  |

## phase-activity: Non-overlapping phase activity

**Grain:** Team-semester / phase

**Key:** ["cohort", "team_id", "phase"]

**Definition:** Four mutually exclusive phases; the final phase is seven days before T3, not after T3.

**Denominator:** Phase commits or clean changed lines / corresponding observed team total * 100.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester / phase", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "phase", "label": "Phase", "fields": ["phase"], "mode": "multi_select"}, {"id": "score_trajectory_group", "label": "Score trajectory group", "fields": ["score_trajectory_group"], "mode": "multi_select"}, {"id": "planning_scope_tier", "label": "Planning scope tier", "fields": ["planning_scope_tier"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Pre-T1 duration varies; phase order is not a duration. Do not pool overlapping M3 windows into phases.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/phase-activity.json) / [Full CSV](data/downloads/phase-activity.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| phase | Phase | string | false | label | Phase in the stated row grain; use this dataset's denominator and temporal scope. |  |
| phase_order | Phase order | integer | false | ordinal | Phase order in the stated row grain; use this dataset's denominator and temporal scope. |  |
| commit_n | Commit count | integer | false | commits | Commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| clean_churn | Clean churn | integer | false | changed lines | Clean churn in the stated row grain; use this dataset's denominator and temporal scope. |  |
| active_day_n | Active day count | integer | false | days | Active day count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| active_author_n | Active author count | integer | false | authors | Active author count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| score_trajectory_group | Score trajectory group | string | false | label | Existing improved/stable/declined grouping under the registered adaptive signed 0.125 threshold. |  |
| planning_scope_tier | Planning scope tier | string | false | label | Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median. |  |
| evaluator_score_t3 | Evaluator score T3 | number | false | evaluator score points | Unweighted mean of the four evaluator dimension means at T3; descriptive, not official quality. |  |
| delta_score_t3_minus_t1 | Delta score T3 minus T1 | number | false | evaluator score points | Descriptive evaluator composite at T3 minus T1 in original score points. |  |
| team_total_commit_n | Team total commit count | integer | false | commits | Team total commit count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| team_total_clean_churn | Team total clean churn | integer | false | changed lines | Team total clean churn in the stated row grain; use this dataset's denominator and temporal scope. |  |
| commit_share_pct | Commit share (%) | number | false | percentage points (0-100) | Commit share (%) in the stated row grain; use this dataset's denominator and temporal scope. |  |
| clean_churn_share_pct | Clean churn share (%) | number | false | percentage points (0-100) | Clean churn share (%) in the stated row grain; use this dataset's denominator and temporal scope. |  |

## phase-activity-summary: Fixed phase summaries by trajectory

**Grain:** Trajectory group / phase

**Key:** ["score_trajectory_group", "phase"]

**Definition:** Original means and medians for four non-overlapping phases across three trajectory groups.

**Denominator:** Original team_semester_n in each fixed trajectory group.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Trajectory group / phase", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "score_trajectory_group", "label": "Score trajectory group", "fields": ["score_trajectory_group"], "mode": "multi_select"}, {"id": "phase", "label": "Phase", "fields": ["phase"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["No cohort/team filtering, trajectory reclassification, or filter-time estimates.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/phase-activity-summary.json) / [Full CSV](data/downloads/phase-activity-summary.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| score_trajectory_group | Score trajectory group | string | false | label | Existing improved/stable/declined grouping under the registered adaptive signed 0.125 threshold. |  |
| phase | Phase | string | false | label | Phase in the stated row grain; use this dataset's denominator and temporal scope. |  |
| phase_order | Phase order | integer | false | ordinal | Phase order in the stated row grain; use this dataset's denominator and temporal scope. |  |
| team_semester_n | Team semester count | integer | false | team-semesters | Team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_commit_share_pct | Mean commit share (%) | number | false | percentage points (0-100) | Mean commit share (%) in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_commit_share_pct | Median commit share (%) | number | false | percentage points (0-100) | Median commit share (%) in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_clean_churn_share_pct | Mean clean churn share (%) | number | false | percentage points (0-100) | Mean clean churn share (%) in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_clean_churn_share_pct | Median clean churn share (%) | number | false | percentage points (0-100) | Median clean churn share (%) in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_active_day_n | Mean active day count | number | false | days | Mean active day count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_active_author_n | Mean active author count | number | false | authors | Mean active author count in the stated row grain; use this dataset's denominator and temporal scope. |  |

## score-final7-commits: Score change and final-seven commit concentration

**Grain:** Team-semester

**Key:** ["cohort", "team_id"]

**Definition:** Final-seven concentration strictly before T3, with score changes and fixed median quadrants.

**Denominator:** Commits in [T3-7d,T3) / all observed project commits before T3 * 100.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "score_trajectory_group", "label": "Score trajectory group", "fields": ["score_trajectory_group"], "mode": "multi_select"}, {"id": "final7_concentration_tier", "label": "Final7 concentration tier", "fields": ["final7_concentration_tier"], "mode": "multi_select"}, {"id": "quadrant", "label": "Quadrant", "fields": ["quadrant"], "mode": "multi_select"}, {"id": "planning_scope_tier", "label": "Planning scope tier", "fields": ["planning_scope_tier"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Excludes post-T3 activity. Positive delta uses >0.125, not >0; frozen cuts are not recalculated.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/score-final7-commits.json) / [Full CSV](data/downloads/score-final7-commits.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| evaluator_score_t1 | Evaluator score T1 | number | false | evaluator score points | Unweighted mean of the four evaluator dimension means at T1; descriptive, not official quality. |  |
| evaluator_score_t3 | Evaluator score T3 | number | false | evaluator score points | Unweighted mean of the four evaluator dimension means at T3; descriptive, not official quality. |  |
| delta_score_t3_minus_t1 | Delta score T3 minus T1 | number | false | evaluator score points | Descriptive evaluator composite at T3 minus T1 in original score points. |  |
| score_trajectory_group | Score trajectory group | string | false | label | Existing improved/stable/declined grouping under the registered adaptive signed 0.125 threshold. |  |
| planning_scope_tier | Planning scope tier | string | false | label | Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median. |  |
| final7_share_pct | Final7 share (%) | number | false | percentage points (0-100) | Final-seven metric activity / full observed project activity strictly before T3 * 100; metric is explicitly labeled. |  |
| activity_metric | Activity metric | string | false | label | Activity metric in the stated row grain; use this dataset's denominator and temporal scope. |  |
| final7_concentration_tier | Final7 concentration tier | string | false | label | Final7 concentration tier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| delta_direction | Delta direction | string | false | label | Existing classification using a positive change threshold strictly greater than 0.125. |  |
| quadrant | Quadrant | string | false | label | Quadrant in the stated row grain; use this dataset's denominator and temporal scope. |  |

## score-final7-clean-churn: Score change and final-seven clean-churn concentration

**Grain:** Team-semester

**Key:** ["cohort", "team_id"]

**Definition:** Clean-churn concentration strictly before T3, separate from commit concentration.

**Denominator:** Clean changed lines in [T3-7d,T3) / all observed clean changed lines before T3 * 100.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "score_trajectory_group", "label": "Score trajectory group", "fields": ["score_trajectory_group"], "mode": "multi_select"}, {"id": "final7_concentration_tier", "label": "Final7 concentration tier", "fields": ["final7_concentration_tier"], "mode": "multi_select"}, {"id": "quadrant", "label": "Quadrant", "fields": ["quadrant"], "mode": "multi_select"}, {"id": "planning_scope_tier", "label": "Planning scope tier", "fields": ["planning_scope_tier"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Excludes post-T3 activity. Original clean-churn median and delta threshold remain fixed.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/score-final7-clean-churn.json) / [Full CSV](data/downloads/score-final7-clean-churn.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| evaluator_score_t1 | Evaluator score T1 | number | false | evaluator score points | Unweighted mean of the four evaluator dimension means at T1; descriptive, not official quality. |  |
| evaluator_score_t3 | Evaluator score T3 | number | false | evaluator score points | Unweighted mean of the four evaluator dimension means at T3; descriptive, not official quality. |  |
| delta_score_t3_minus_t1 | Delta score T3 minus T1 | number | false | evaluator score points | Descriptive evaluator composite at T3 minus T1 in original score points. |  |
| score_trajectory_group | Score trajectory group | string | false | label | Existing improved/stable/declined grouping under the registered adaptive signed 0.125 threshold. |  |
| planning_scope_tier | Planning scope tier | string | false | label | Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median. |  |
| final7_share_pct | Final7 share (%) | number | false | percentage points (0-100) | Final-seven metric activity / full observed project activity strictly before T3 * 100; metric is explicitly labeled. |  |
| activity_metric | Activity metric | string | false | label | Activity metric in the stated row grain; use this dataset's denominator and temporal scope. |  |
| final7_concentration_tier | Final7 concentration tier | string | false | label | Final7 concentration tier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| delta_direction | Delta direction | string | false | label | Existing classification using a positive change threshold strictly greater than 0.125. |  |
| quadrant | Quadrant | string | false | label | Quadrant in the stated row grain; use this dataset's denominator and temporal scope. |  |

## score-final7-quadrants: Fixed score/concentration quadrant summaries

**Grain:** Activity metric / quadrant / planning tier

**Key:** ["activity_metric", "quadrant", "planning_scope_tier"]

**Definition:** Existing counts and medians under the registered score-change rule.

**Denominator:** Original within-cell team_semester_n, with fixed full-sample median cut.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Activity metric / quadrant / planning tier", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "activity_metric", "label": "Activity metric", "fields": ["activity_metric"], "mode": "multi_select"}, {"id": "quadrant", "label": "Quadrant", "fields": ["quadrant"], "mode": "multi_select"}, {"id": "planning_scope_tier", "label": "Planning scope tier", "fields": ["planning_scope_tier"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["No team list is published; small cells do not justify causal or confirmatory claims.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/score-final7-quadrants.json) / [Full CSV](data/downloads/score-final7-quadrants.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| activity_metric | Activity metric | string | false | label | Activity metric in the stated row grain; use this dataset's denominator and temporal scope. |  |
| quadrant | Quadrant | string | false | label | Quadrant in the stated row grain; use this dataset's denominator and temporal scope. |  |
| planning_scope_tier | Planning scope tier | string | false | label | Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median. |  |
| final7_concentration_cut | Final7 concentration cut | string | false | label | Final7 concentration cut in the stated row grain; use this dataset's denominator and temporal scope. |  |
| final7_concentration_median_pct | Final7 concentration median (%) | number | false | percentage points (0-100) | Final7 concentration median (%) in the stated row grain; use this dataset's denominator and temporal scope. |  |
| delta_threshold | Delta threshold | number | false | evaluator score points | Delta threshold in the stated row grain; use this dataset's denominator and temporal scope. |  |
| team_semester_n | Team semester count | integer | false | team-semesters | Team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_final7_share_pct | Median final7 share (%) | number | true | percentage points (0-100) | Median final7 share (%) in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_delta_score_t3_minus_t1 | Median delta score T3 minus T1 | number | true | evaluator score points | Median delta score T3 minus T1 in the stated row grain; use this dataset's denominator and temporal scope. |  |

## planning-final7-commits: Planning scope and final-seven commits

**Grain:** Team-semester

**Key:** ["cohort", "team_id"]

**Definition:** T1 scope versus final-seven concentration before T3; fixed quadrants, T3 score color, absolute score-change size.

**Denominator:** Final-seven commits / all observed project commits strictly before T3 * 100.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "planning_scope_tier", "label": "Planning scope tier", "fields": ["planning_scope_tier"], "mode": "multi_select"}, {"id": "planning_concentration_quadrant", "label": "Planning concentration quadrant", "fields": ["planning_concentration_quadrant"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Frozen median quadrants are descriptive. Marker size is a rendering value, not an extra scientific measure.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/planning-final7-commits.json) / [Full CSV](data/downloads/planning-final7-commits.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| planning_scope_log1p_t1 | Planning scope log(1 + scope) T1 | number | false | natural log(1 + changed lines) | Natural logarithm of one plus T1 artifact changed-line scope. |  |
| planning_scope_tier | Planning scope tier | string | false | label | Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median. |  |
| evaluator_score_t3 | Evaluator score T3 | number | false | evaluator score points | Unweighted mean of the four evaluator dimension means at T3; descriptive, not official quality. |  |
| delta_score_t3_minus_t1 | Delta score T3 minus T1 | number | false | evaluator score points | Descriptive evaluator composite at T3 minus T1 in original score points. |  |
| clean_rework_churn_t3 | Clean rework churn T3 | integer | false | changed lines | Clean T3 changed lines on paths observed in the prior baseline; path provenance, not verified defects. |  |
| final7_share_pct | Final7 share (%) | number | false | percentage points (0-100) | Final-seven metric activity / full observed project activity strictly before T3 * 100; metric is explicitly labeled. |  |
| activity_metric | Activity metric | string | false | label | Activity metric in the stated row grain; use this dataset's denominator and temporal scope. |  |
| final7_concentration_tier | Final7 concentration tier | string | false | label | Final7 concentration tier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| planning_concentration_quadrant | Planning concentration quadrant | string | false | label | Planning concentration quadrant in the stated row grain; use this dataset's denominator and temporal scope. |  |
| abs_delta_score_t3_minus_t1 | Abs delta score T3 minus T1 | number | false | evaluator score points | Absolute T3-minus-T1 composite change used for saved marker-size encoding. |  |
| marker_size | Marker size | number | false | rendering size | Saved plotting size used for fidelity; absolute score change is available separately. |  |

## planning-final7-clean-churn: Planning scope and final-seven clean churn

**Grain:** Team-semester

**Key:** ["cohort", "team_id"]

**Definition:** Clean-churn variant of the planning/concentration comparison, excluding post-T3 activity.

**Denominator:** Final-seven clean changed lines / all observed clean changed lines before T3 * 100.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "planning_scope_tier", "label": "Planning scope tier", "fields": ["planning_scope_tier"], "mode": "multi_select"}, {"id": "planning_concentration_quadrant", "label": "Planning concentration quadrant", "fields": ["planning_concentration_quadrant"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Use the clean-churn median, not the commit median; no recomputation after filters.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/planning-final7-clean-churn.json) / [Full CSV](data/downloads/planning-final7-clean-churn.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| planning_scope_log1p_t1 | Planning scope log(1 + scope) T1 | number | false | natural log(1 + changed lines) | Natural logarithm of one plus T1 artifact changed-line scope. |  |
| planning_scope_tier | Planning scope tier | string | false | label | Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median. |  |
| evaluator_score_t3 | Evaluator score T3 | number | false | evaluator score points | Unweighted mean of the four evaluator dimension means at T3; descriptive, not official quality. |  |
| delta_score_t3_minus_t1 | Delta score T3 minus T1 | number | false | evaluator score points | Descriptive evaluator composite at T3 minus T1 in original score points. |  |
| clean_rework_churn_t3 | Clean rework churn T3 | integer | false | changed lines | Clean T3 changed lines on paths observed in the prior baseline; path provenance, not verified defects. |  |
| final7_share_pct | Final7 share (%) | number | false | percentage points (0-100) | Final-seven metric activity / full observed project activity strictly before T3 * 100; metric is explicitly labeled. |  |
| activity_metric | Activity metric | string | false | label | Activity metric in the stated row grain; use this dataset's denominator and temporal scope. |  |
| final7_concentration_tier | Final7 concentration tier | string | false | label | Final7 concentration tier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| planning_concentration_quadrant | Planning concentration quadrant | string | false | label | Planning concentration quadrant in the stated row grain; use this dataset's denominator and temporal scope. |  |
| abs_delta_score_t3_minus_t1 | Abs delta score T3 minus T1 | number | false | evaluator score points | Absolute T3-minus-T1 composite change used for saved marker-size encoding. |  |
| marker_size | Marker size | number | false | rendering size | Saved plotting size used for fidelity; absolute score change is available separately. |  |

## planning-final7-quadrants: Fixed planning/concentration quadrant summaries

**Grain:** Activity metric / quadrant

**Key:** ["activity_metric", "quadrant"]

**Definition:** Original T3 score, score-change, and rework summaries with small-N flags.

**Denominator:** Cell team_semester_n and full-population team_semester_denominator are separate.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Activity metric / quadrant", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "activity_metric", "label": "Activity metric", "fields": ["activity_metric"], "mode": "multi_select"}, {"id": "quadrant", "label": "Quadrant", "fields": ["quadrant"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["No inferred project membership or recalculated cell estimates.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/planning-final7-quadrants.json) / [Full CSV](data/downloads/planning-final7-quadrants.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| activity_metric | Activity metric | string | false | label | Activity metric in the stated row grain; use this dataset's denominator and temporal scope. |  |
| quadrant | Quadrant | string | false | label | Quadrant in the stated row grain; use this dataset's denominator and temporal scope. |  |
| team_semester_n | Team semester count | integer | false | team-semesters | Team semester count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| team_semester_denominator | Team semester denominator | integer | false | team-semesters | Team semester denominator in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_t3_score | Mean T3 score | number | true | evaluator score points | Mean T3 score in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_t3_score | Median T3 score | number | true | evaluator score points | Median T3 score in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_delta_score | Mean delta score | number | true | evaluator score points | Mean delta score in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_delta_score | Median delta score | number | true | evaluator score points | Median delta score in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_clean_rework_churn_t3 | Mean clean rework churn T3 | number | true | changed lines | Mean clean rework churn T3 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| small_n_flag | Small count flag | boolean | false | boolean | Small count flag in the stated row grain; use this dataset's denominator and temporal scope. |  |

## operational-regularity: Descriptive operational regularity

**Grain:** Team-semester

**Key:** ["cohort", "team_id"]

**Definition:** Daily activity from first commit through T3 anchor inclusive; mean of eight fixed normalized components.

**Denominator:** Active days / project span; M7 inactive windows / 71 overlapping windows.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "score_trajectory_group", "label": "Score trajectory group", "fields": ["score_trajectory_group"], "mode": "multi_select"}, {"id": "planning_scope_tier", "label": "Planning scope tier", "fields": ["planning_scope_tier"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Not a validated Agile score. Author metrics use the pre-T3 seven days, not the full timeline; normalization stays fixed.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/operational-regularity.json) / [Full CSV](data/downloads/operational-regularity.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| delta_score_t3_minus_t1 | Delta score T3 minus T1 | number | false | evaluator score points | Descriptive evaluator composite at T3 minus T1 in original score points. |  |
| score_trajectory_group | Score trajectory group | string | false | label | Existing improved/stable/declined grouping under the registered adaptive signed 0.125 threshold. |  |
| planning_scope_tier | Planning scope tier | string | false | label | Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median. |  |
| final7_commit_share_pct | Final7 commit share (%) | number | false | percentage points (0-100) | Final-seven commits / all observed project commits strictly before T3 * 100. |  |
| final7_clean_churn_share_pct | Final7 clean churn share (%) | number | false | percentage points (0-100) | Final-seven clean changed lines / all observed project clean changed lines strictly before T3 * 100. |  |
| active_day_count | Active day count | integer | false | days | Active day count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| project_span_days | Project span days | integer | false | days | First observed commit day through T3 anchor day inclusive. |  |
| active_day_share | Active day share | number | false | fraction (0-1) | Days with a commit / observed project-span days. |  |
| max_inactivity_gap_days | Max inactivity gap days | integer | false | days | Longest zero-commit run within the observed daily series. |  |
| median_inactivity_gap_days | Median inactivity gap days | number | false | days | Median zero-commit run length within the observed daily series. |  |
| commit_weekly_cv | Commit weekly CV | number | false | coefficient of variation (nonnegative) | Population coefficient of variation of weekly commits, including zero weeks in the observed period. |  |
| clean_churn_weekly_cv | Clean churn weekly CV | number | false | coefficient of variation (nonnegative) | Population coefficient of variation of weekly clean changed lines, including observed-period zero weeks. |  |
| temporal_entropy_commits | Temporal entropy commits | number | false | normalized Shannon entropy (0-1) | Daily commit Shannon entropy normalized by log(project_span_days). |  |
| temporal_entropy_clean_churn | Temporal entropy clean churn | number | false | normalized Shannon entropy (0-1) | Daily clean-churn Shannon entropy normalized by log(project_span_days). |  |
| author_count | Author count | integer | false | authors | Author count in the stated row grain; use this dataset's denominator and temporal scope. | pre_T3_seven_days |
| max_author_share | Max author share | number | true | fraction (0-1) | Max author share in the stated row grain; use this dataset's denominator and temporal scope. | pre_T3_seven_days |
| author_gini | Author gini | number | true | Gini (0-1) | Author gini in the stated row grain; use this dataset's denominator and temporal scope. | pre_T3_seven_days |
| m7_window_count | M7 window count | integer | false | overlapping windows | M7 window count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| m7_inactive_window_share | M7 inactive window share | number | false | fraction (0-1) | Inactive M7 windows / original overlapping window count. |  |
| regularity_index | Regularity index | number | false | normalized component/index (0-1) | Mean of eight fixed normalized activity-distribution components; not a validated Agile score. |  |
| regularity_active_day_share_component | Regularity active day share component | number | false | normalized component/index (0-1) | Original fixed normalized Regularity active day share component; see the eight-component regularity definition. Never renormalize filtered rows. |  |
| regularity_commit_entropy_component | Regularity commit entropy component | number | false | normalized component/index (0-1) | Original fixed normalized Regularity commit entropy component; see the eight-component regularity definition. Never renormalize filtered rows. |  |
| regularity_clean_churn_entropy_component | Regularity clean churn entropy component | number | false | normalized component/index (0-1) | Original fixed normalized Regularity clean churn entropy component; see the eight-component regularity definition. Never renormalize filtered rows. |  |
| regularity_commit_weekly_cv_component | Regularity commit weekly CV component | number | false | normalized component/index (0-1) | Original fixed normalized Regularity commit weekly CV component; see the eight-component regularity definition. Never renormalize filtered rows. |  |
| regularity_clean_churn_weekly_cv_component | Regularity clean churn weekly CV component | number | false | normalized component/index (0-1) | Original fixed normalized Regularity clean churn weekly CV component; see the eight-component regularity definition. Never renormalize filtered rows. |  |
| regularity_m7_activity_component | Regularity M7 activity component | number | false | normalized component/index (0-1) | Original fixed normalized Regularity M7 activity component; see the eight-component regularity definition. Never renormalize filtered rows. |  |
| regularity_commit_distribution_component | Regularity commit distribution component | number | false | normalized component/index (0-1) | Original fixed normalized Regularity commit distribution component; see the eight-component regularity definition. Never renormalize filtered rows. |  |
| regularity_clean_churn_distribution_component | Regularity clean churn distribution component | number | false | normalized component/index (0-1) | Original fixed normalized Regularity clean churn distribution component; see the eight-component regularity definition. Never renormalize filtered rows. |  |

## transcript-context-2025: Transcript and repository context: 2025.2

**Grain:** Checkpoint / one global corpus and cohort-level context

**Key:** ["checkpoint"]

**Definition:** Global transcript density beside descriptive repository/evaluator summaries; fixed T3 rework context repeats on every row.

**Denominator:** Lexical matches / tokens * 1000; team_n for repository/score context; eligible cases for T3 ratio context.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Checkpoint / one global corpus and cohort-level context", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "cohorts": ["2025.2"], "team_attribution": false}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "checkpoint", "label": "Checkpoint", "fields": ["checkpoint"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Do not plot repeated T3 context as checkpoint-varying or treat one M5 corpus as nine team observations.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/transcript-context-2025.json) / [Full CSV](data/downloads/transcript-context-2025.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| checkpoint | Checkpoint | string | false | label | Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition. |  |
| team_n | Team count | integer | false | team-semesters | Team count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| m5_friction_marker_density_per_1k_tokens | M5 friction marker density per 1k tokens | number | false | lexical matches per 1000 tokens | M5 friction marker density per 1k tokens in the stated row grain; use this dataset's denominator and temporal scope. |  |
| m5_friction_marker_n | M5 friction marker count | integer | false | lexical matches | M5 friction marker count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| m5_token_n | M5 token count | integer | false | tokens | M5 token count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_clean_churn | Median clean churn | number | false | changed lines | Median clean churn in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_clean_churn | Mean clean churn | number | false | changed lines | Mean clean churn in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_evaluator_score_composite | Median evaluator score composite | number | false | evaluator score points | Median evaluator score composite in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_evaluator_score_composite | Mean evaluator score composite | number | false | evaluator score points | Mean evaluator score composite in the stated row grain; use this dataset's denominator and temporal scope. |  |
| baseline_eligible_rework_team_n | Baseline eligible rework team count | integer | false | team-semesters | Baseline eligible rework team count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| median_clean_rework_churn_t3 | Median clean rework churn T3 | number | false | changed lines | Fixed T3 rework context repeated on every checkpoint row, not checkpoint-varying evidence. | fixed_T3 |
| median_clean_rework_ratio_t3_baseline_eligible | Median clean rework ratio T3 baseline eligible | number | false | fraction (0-1) | Fixed T3 rework context repeated on every checkpoint row, not checkpoint-varying evidence. | fixed_T3 |

## complexity-profile: Evaluated and repository structural complexity

**Grain:** Team-semester

**Key:** ["cohort", "team_id"]

**Definition:** Separate evaluator scores, path-based counts, file-event shares, planning, and rework context.

**Denominator:** Frontend/backend shares use all classified and unclassified clean file events; eligible ratio uses M8 policy.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load.", "ratio_status": ["available", "baseline_not_observed", "zero_clean_churn"], "precedence": "baseline_not_observed before zero_clean_churn"}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}, {"id": "planning_scope_tier", "label": "Planning scope tier", "fields": ["planning_scope_tier"], "mode": "multi_select"}, {"id": "score_trajectory_group", "label": "Score trajectory group", "fields": ["score_trajectory_group"], "mode": "multi_select"}, {"id": "baseline_eligible_for_rework_t3", "label": "Baseline eligible for rework T3", "fields": ["baseline_eligible_for_rework_t3"], "mode": "multi_select"}, {"id": "ratio_status", "label": "Ratio status", "fields": ["ratio_status"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Path heuristics are not manual architecture or GenAI classifications; magnitudes and file counts differ.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/complexity-profile.json) / [Full CSV](data/downloads/complexity-profile.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| technical_complexity_mean_t1 | Technical complexity mean T1 | number | false | evaluator score points | Mean evaluator technical-complexity score at T1, not repository structural inference. |  |
| technical_complexity_mean_t2 | Technical complexity mean T2 | number | false | evaluator score points | Mean evaluator technical-complexity score at T2, not repository structural inference. |  |
| technical_complexity_mean_t3 | Technical complexity mean T3 | number | false | evaluator score points | Mean evaluator technical-complexity score at T3, not repository structural inference. |  |
| delta_technical_complexity_t3_minus_t1 | Delta technical complexity T3 minus T1 | number | false | evaluator score points | Evaluator technical-complexity mean at T3 minus T1, in original score points. |  |
| clean_distinct_file_n | Clean distinct file count | integer | false | clean files | Distinct clean-path files touched in observed file events. |  |
| clean_distinct_directory_n | Clean distinct directory count | integer | false | clean directories | Distinct normalized parent directories among clean-path file events. |  |
| clean_max_path_depth | Clean max path depth | integer | false | path segments | Maximum count of normalized path segments among clean-path file events. |  |
| clean_extension_n | Clean extension count | integer | false | file extensions | Distinct clean-path file extensions; missing extensions use the paper's '(none)' category. |  |
| clean_touching_commit_n_inferred | Clean touching commit count inferred | integer | false | commits | Distinct observed commits touching at least one clean path. |  |
| clean_total_churn_inferred | Clean total churn inferred | integer | false | changed lines | Observed clean-path additions plus deletions, not distinct files or defects. |  |
| frontend_clean_file_event_n | Frontend clean file event count | integer | false | file events | Frontend clean file event count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| backend_clean_file_event_n | Backend clean file event count | integer | false | file events | Backend clean file event count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mixed_clean_file_event_n | Mixed clean file event count | integer | false | file events | Mixed clean file event count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| unclassified_clean_file_event_n | Unclassified clean file event count | integer | false | file events | Unclassified clean file event count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| mean_clean_files_per_commit | Mean clean files per commit | number | false | clean files per commit | Mean distinct clean files per clean-touching commit. |  |
| frontend_clean_file_event_share | Frontend clean file event share | number | false | fraction (0-1) | Frontend-matching clean file events / all classified and unclassified clean file events. |  |
| backend_clean_file_event_share | Backend clean file event share | number | false | fraction (0-1) | Backend-matching clean file events / all classified and unclassified clean file events. |  |
| clean_churn_t3 | Clean churn T3 | integer | false | changed lines | Clean churn T3 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| all_churn_t3 | All churn T3 | integer | false | changed lines | All churn T3 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| m4_clean_unique_file_n_t3 | M4 clean unique file count T3 | integer | false | clean files | M4 clean unique file count T3 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| m4_clean_touching_commit_n_t3 | M4 clean touching commit count T3 | integer | false | commits | M4 clean touching commit count T3 in the stated row grain; use this dataset's denominator and temporal scope. |  |
| clean_rework_churn_t3 | Clean rework churn T3 | integer | false | changed lines | Clean T3 changed lines on paths observed in the prior baseline; path provenance, not verified defects. |  |
| clean_rework_ratio_t3 | Clean rework ratio T3 | number | true | fraction (0-1) | Clean T3 rework lines divided by total clean T3 lines; null unless baseline eligible and total positive. |  |
| baseline_eligible_for_rework_t3 | Baseline eligible for rework T3 | boolean | false | boolean | True exactly when prior observed clean-path count is greater than zero. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |
| planning_artifact_present_t1 | Planning artifact present T1 | boolean | false | boolean | Repository structural artifact presence at T1, not planning quality. |  |
| planning_scope_log1p_t1 | Planning scope log(1 + scope) T1 | number | false | natural log(1 + changed lines) | Natural logarithm of one plus T1 artifact changed-line scope. |  |
| pi_file_count_t1 | T1 artifact file count | integer | false | files | Observed T1 structural planning artifact files. |  |
| pi_line_delta_t1 | T1 artifact changed-line scope | integer | false | changed lines | Observed T1 structural artifact additions plus deletions, in changed lines. |  |
| score_trajectory_group | Score trajectory group | string | false | label | Existing improved/stable/declined grouping under the registered adaptive signed 0.125 threshold. |  |
| planning_scope_tier | Planning scope tier | string | false | label | Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median. |  |
| final7_commit_share_pct | Final7 commit share (%) | number | false | percentage points (0-100) | Final-seven commits / all observed project commits strictly before T3 * 100. |  |
| final7_clean_churn_share_pct | Final7 clean churn share (%) | number | false | percentage points (0-100) | Final-seven clean changed lines / all observed project clean changed lines strictly before T3 * 100. |  |
| ratio_status | Ratio status | string | false | label | available, baseline_not_observed, or zero_clean_churn; baseline absence takes precedence. |  |

## complexity-stratified-associations: Complexity-stratified association sensitivity

**Grain:** Fixed relationship

**Key:** ["relationship"]

**Definition:** Existing full-sample Spearman rho and fixed median-split strata at 1.875 evaluator score points.

**Denominator:** Separate N for full, low-complexity, and high-complexity estimates; minimum N is four.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Fixed relationship", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "relationship", "label": "Relationship", "fields": ["relationship"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Low <= median, high > median. Small-N descriptive sensitivity, not causal confounding control.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/complexity-stratified-associations.json) / [Full CSV](data/downloads/complexity-stratified-associations.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| relationship | Relationship | string | false | label | Relationship in the stated row grain; use this dataset's denominator and temporal scope. |  |
| relationship_label | Relationship label | string | false | label | Relationship label in the stated row grain; use this dataset's denominator and temporal scope. |  |
| predictor | Predictor | string | false | label | Predictor in the stated row grain; use this dataset's denominator and temporal scope. |  |
| outcome | Outcome | string | false | label | Outcome in the stated row grain; use this dataset's denominator and temporal scope. |  |
| rho_without_complexity_stratification | Rho without complexity stratification | number | true | Spearman rho (-1 to 1) | Rho without complexity stratification in the stated row grain; use this dataset's denominator and temporal scope. |  |
| rho_within_low_complexity | Rho within low complexity | number | true | Spearman rho (-1 to 1) | Rho within low complexity in the stated row grain; use this dataset's denominator and temporal scope. |  |
| rho_within_high_complexity | Rho within high complexity | number | true | Spearman rho (-1 to 1) | Rho within high complexity in the stated row grain; use this dataset's denominator and temporal scope. |  |
| complexity_stratification_variable | Complexity stratification variable | string | false | label | Complexity stratification variable in the stated row grain; use this dataset's denominator and temporal scope. |  |
| complexity_median | Complexity median | number | false | evaluator score points | Complexity median in the stated row grain; use this dataset's denominator and temporal scope. |  |
| low_complexity_rule | Low complexity rule | string | false | label | Low complexity rule in the stated row grain; use this dataset's denominator and temporal scope. |  |
| high_complexity_rule | High complexity rule | string | false | label | High complexity rule in the stated row grain; use this dataset's denominator and temporal scope. |  |
| n_without_complexity_stratification | Count without complexity stratification | integer | false | team-semesters | Count without complexity stratification in the stated row grain; use this dataset's denominator and temporal scope. |  |
| n_within_low_complexity | Count within low complexity | integer | false | team-semesters | Count within low complexity in the stated row grain; use this dataset's denominator and temporal scope. |  |
| n_within_high_complexity | Count within high complexity | integer | false | team-semesters | Count within high complexity in the stated row grain; use this dataset's denominator and temporal scope. |  |
| minimum_n_for_rho | Minimum count for rho | integer | false | Spearman rho (-1 to 1) | Minimum eligible pair count of four for the registered diagnostic rho calculation. |  |

## influence-cases: Omitted-case influence

**Grain:** Relationship / omitted team-semester

**Key:** ["relationship_id", "omitted_cohort", "omitted_team_id"]

**Definition:** 13 relationships by 14 omissions; rho_delta_from_full is the omission estimate minus full-sample rho.

**Denominator:** Original eligible full_sample_n and loo_n; omitting an ineligible case need not reduce N.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Relationship / omitted team-semester", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "relationship_id", "label": "Relationship identifier", "fields": ["relationship_id"], "mode": "multi_select"}, {"id": "omitted_cohort", "label": "Omitted cohort", "fields": ["omitted_cohort"], "mode": "multi_select"}, {"id": "omitted_case", "label": "Omitted team-semester", "fields": ["omitted_cohort", "omitted_team_id"], "mode": "multi_select"}, {"id": "availability_status", "label": "Availability status", "fields": ["availability_status"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Not a confidence interval; preserve availability status and original eligibility.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/influence-cases.json) / [Full CSV](data/downloads/influence-cases.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| relationship_id | Relationship identifier | string | false | label | Relationship identifier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| omitted_cohort | Omitted cohort | string | false | label | Omitted cohort in the stated row grain; use this dataset's denominator and temporal scope. |  |
| omitted_team_id | Omitted team within cohort | string | false | label | Omitted team within cohort in the stated row grain; use this dataset's denominator and temporal scope. |  |
| relationship_label | Relationship label | string | false | label | Relationship label in the stated row grain; use this dataset's denominator and temporal scope. |  |
| predictor | Predictor | string | false | label | Predictor in the stated row grain; use this dataset's denominator and temporal scope. |  |
| outcome | Outcome | string | false | label | Outcome in the stated row grain; use this dataset's denominator and temporal scope. |  |
| full_sample_n | Full sample count | integer | false | team-semesters | Full sample count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| loo_n | Leave-one-out count | integer | false | team-semesters | Leave-one-out count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| full_sample_rho | Full sample rho | number | true | Spearman rho (-1 to 1) | Full sample rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| loo_rho | Leave-one-out rho | number | true | Spearman rho (-1 to 1) | Leave-one-out rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| rho_delta_from_full | Rho delta from full | number | true | rho difference (-2 to 2) | Leave-one-out rho minus full-sample rho, not a confidence interval. |  |
| abs_rho_delta_from_full | Abs rho delta from full | number | true | rho difference (-2 to 2) | Abs rho delta from full in the stated row grain; use this dataset's denominator and temporal scope. |  |
| full_sample_sign | Full sample sign | string | false | label | Full sample sign in the stated row grain; use this dataset's denominator and temporal scope. |  |
| loo_sign | Leave-one-out sign | string | false | label | Leave-one-out sign in the stated row grain; use this dataset's denominator and temporal scope. |  |
| sign_changed | Sign changed | boolean | false | boolean | Whether the available omission estimate's sign differs from the original full-sample sign. |  |
| availability_status | Availability status | string | false | label | Original association/omission availability; unavailable estimates remain null. |  |

## influence-relations: Influence relationship definitions and ranges

**Grain:** Fixed relationship

**Key:** ["relationship_id"]

**Definition:** Original relationship estimates, omission counts, ranges, and availability.

**Denominator:** Sign-preservation share divides by available omissions, not assumed total omissions.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Fixed relationship", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "relationship_id", "label": "Relationship identifier", "fields": ["relationship_id"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Minimum eligible pair N is four. Leave-one-out ranges are not confidence intervals.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/influence-relations.json) / [Full CSV](data/downloads/influence-relations.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| relationship_id | Relationship identifier | string | false | label | Relationship identifier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| relationship_label | Relationship label | string | false | label | Relationship label in the stated row grain; use this dataset's denominator and temporal scope. |  |
| predictor | Predictor | string | false | label | Predictor in the stated row grain; use this dataset's denominator and temporal scope. |  |
| outcome | Outcome | string | false | label | Outcome in the stated row grain; use this dataset's denominator and temporal scope. |  |
| full_sample_n | Full sample count | integer | false | team-semesters | Full sample count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| leave_one_out_rows | Leave one out rows | integer | false | omission rows | Leave one out rows in the stated row grain; use this dataset's denominator and temporal scope. |  |
| available_leave_one_out_rows | Available leave one out rows | integer | false | omission rows | Available leave one out rows in the stated row grain; use this dataset's denominator and temporal scope. |  |
| full_sample_rho | Full sample rho | number | true | Spearman rho (-1 to 1) | Full sample rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| full_sample_sign | Full sample sign | string | false | label | Full sample sign in the stated row grain; use this dataset's denominator and temporal scope. |  |
| loo_min_rho | Leave-one-out min rho | number | true | Spearman rho (-1 to 1) | Leave-one-out min rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| loo_max_rho | Leave-one-out max rho | number | true | Spearman rho (-1 to 1) | Leave-one-out max rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| max_abs_rho_delta_from_full | Max abs rho delta from full | number | true | rho difference (-2 to 2) | Max abs rho delta from full in the stated row grain; use this dataset's denominator and temporal scope. |  |
| sign_preservation_share | Sign preservation share | number | true | fraction (0-1) | Available omissions preserving the full-sample sign / available omissions. |  |
| availability_status | Availability status | string | false | label | Original association/omission availability; unavailable estimates remain null. |  |

## influence-summary: Directional robustness summary

**Grain:** Fixed relationship

**Key:** ["relationship_id"]

**Definition:** Original ranges, sign preservation, unstable-sensitivity flag, and approved influential-case label.

**Denominator:** available_leave_one_out_rows versus total_leave_one_out_rows; sign share uses available rows.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Fixed relationship", "sample_sizes": "Original per-row denominator fields, not filtered row counts."}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "relationship_id", "label": "Relationship identifier", "fields": ["relationship_id"], "mode": "multi_select"}, {"id": "unstable_sensitivity_flag", "label": "Unstable sensitivity flag", "fields": ["unstable_sensitivity_flag"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Descriptive diagnostic, not causal robustness or inferential uncertainty.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/influence-summary.json) / [Full CSV](data/downloads/influence-summary.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| relationship_id | Relationship identifier | string | false | label | Relationship identifier in the stated row grain; use this dataset's denominator and temporal scope. |  |
| full_sample_rho | Full sample rho | number | true | Spearman rho (-1 to 1) | Full sample rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| loo_min_rho | Leave-one-out min rho | number | true | Spearman rho (-1 to 1) | Leave-one-out min rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| loo_max_rho | Leave-one-out max rho | number | true | Spearman rho (-1 to 1) | Leave-one-out max rho in the stated row grain; use this dataset's denominator and temporal scope. |  |
| sign_preservation_share | Sign preservation share | number | true | fraction (0-1) | Available omissions preserving the full-sample sign / available omissions. |  |
| most_influential_case | Most influential case | string | false | label | Approved cohort/team label for the strongest observed omission effect; not an original repository identity. |  |
| max_abs_rho_delta_from_full | Max abs rho delta from full | number | true | rho difference (-2 to 2) | Max abs rho delta from full in the stated row grain; use this dataset's denominator and temporal scope. |  |
| available_leave_one_out_rows | Available leave one out rows | integer | false | omission rows | Available leave one out rows in the stated row grain; use this dataset's denominator and temporal scope. |  |
| total_leave_one_out_rows | Total leave one out rows | integer | false | omission rows | Total leave one out rows in the stated row grain; use this dataset's denominator and temporal scope. |  |
| unstable_sensitivity_flag | Unstable sensitivity flag | boolean | false | boolean | Original diagnostic sensitivity flag; not a confirmatory statistical test. |  |

## m5-lexicon: Lexical marker definitions

**Grain:** Lexicon version / subtype

**Key:** ["lexicon_version", "subtype"]

**Definition:** Five regex definitions for Portuguese lexical matching.

**Denominator:** Not applicable: definition rows.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Lexicon version / subtype", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "cohorts": ["2025.2"], "team_attribution": false}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load."}

**Filters:** [{"id": "lexicon_version", "label": "Lexicon version", "fields": ["lexicon_version"], "mode": "multi_select"}, {"id": "subtype", "label": "Subtype", "fields": ["subtype"], "mode": "multi_select"}]

**Filter effect:** select_rows_only

**Limitations:** ["Patterns are displayed as text, never executed on user input; no quoted transcript evidence.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m5-lexicon.json) / [Full CSV](data/downloads/m5-lexicon.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| lexicon_version | Lexicon version | string | false | label | Lexicon version in the stated row grain; use this dataset's denominator and temporal scope. |  |
| subtype | Subtype | string | false | label | Subtype in the stated row grain; use this dataset's denominator and temporal scope. |  |
| pattern | Pattern | string | false | label | Approved regex definition displayed as text; not executed on user input. |  |
| language | Language | string | false | label | Language in the stated row grain; use this dataset's denominator and temporal scope. |  |
| counting_rule | Counting rule | string | false | label | Counting rule in the stated row grain; use this dataset's denominator and temporal scope. |  |

## m6b-planning-content: Structured planning-content evidence

**Grain:** Team-semester / T1

**Key:** ["cohort", "team_id"]

**Definition:** Reviewed exploratory planning presence and separate evidence-item counts; no source text.

**Denominator:** Evidence-item array lengths only for the nine successful extractions.

**Estimation population:** Original published population and N remain fixed when rows are selected.

**Coverage:** {"scope": "Team-semester / T1", "sample_sizes": "Original per-row denominator fields, not filtered row counts.", "team_semesters": 14, "cohort_counts": {"2025.2": 9, "2026.1": 5}, "measured": 9, "unmeasured": 5}

**Missingness:** {"null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.", "absent_row": "Not synthesized as zero.", "load_error": "A failed or malformed file must display an error, not an empty-success dataset.", "empty_filter": "No matching public rows, distinct from a failed load.", "measurement_status": {"success": "Observed: empty evidence arrays count as zero.", "unavailable_not_measured": "All six presence/count outputs null, not zero."}}

**Filters:** [{"id": "cohort", "label": "Cohort", "fields": ["cohort"], "mode": "multi_select"}, {"id": "team_semester", "label": "Team-semester", "fields": ["cohort", "team_id"], "mode": "multi_select"}]

**Filter effect:** select_observations

**Limitations:** ["Five unmeasured cases are null, not zero. Successful empty lists are zero; no composite planning score.", "Descriptive or exploratory; no causal inference or new browser-side estimates."]

[Full JSON](data/datasets/m6b-planning-content.json) / [Full CSV](data/downloads/m6b-planning-content.csv).

| Column | Label | Type | Nullable | Unit | Definition | Time scope |
|---|---|---|---|---|---|---|
| cohort | Cohort | string | false | label | Approved cohort label, stored as a string, not a decimal year. |  |
| team_id | Team within cohort | string | false | label | Approved team label scoped by cohort; never a global team identifier. |  |
| measurement_status | Measurement status | string | false | label | Measurement-specific availability/state, distinct from a load error or an empty filter result. |  |
| planning_evidence_present | Planning evidence present | boolean | true | boolean | Reviewed extraction's boolean planning-presence field; null when unmeasured. |  |
| goals_n | Goals count | integer | true | evidence items | Goals count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| architecture_or_design_n | Architecture or design count | integer | true | evidence items | Architecture or design count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| task_decomposition_n | Task decomposition count | integer | true | evidence items | Task decomposition count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| risk_or_dependency_n | Risk or dependency count | integer | true | evidence items | Risk or dependency count in the stated row grain; use this dataset's denominator and temporal scope. |  |
| evidence_quotes_n | Evidence quotes count | integer | true | evidence items | Number of evidence items, without any quotation text; no publication permission for the text. |  |
