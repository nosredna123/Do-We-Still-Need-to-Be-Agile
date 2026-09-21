# Manuscript Draft: Method

## 3. Method

### 3.1 Study design and evidence hierarchy

We conducted a retrospective, observational study of software engineering education artifacts collected across two semesters, 2025.2 and 2026.1. The study was designed to characterize planning, code-change, technical-degradation, AI-associated author-concentration, and transcript/context signals at the granularities supported by their sources. It was not an intervention study and did not assign teams to Agile, BDUF, SDD, or any alternative process.

The analysis followed a report-first evidence protocol. Phase 2.5 artifact reports, act reports, and the consolidated audit provided the primary interpretive layer. Cross-evidence reports were treated as a secondary exploratory layer. Parquet, CSV, JSON, metadata sidecars, and figure manifests were used to verify row counts, observation keys, variables, transformations, missingness, exclusions, and statistical status. The Phase 3 package was assembled from persisted artifacts; it did not regenerate or replace Phase 2 outputs.

The primary inferential unit was the team-semester. The canonical team-level table contained 14 team-semester observations: nine observations from 2025.2 and five from 2026.1. Team-level temporal measures were organized around three evaluation markers, T1, T2, and T3. Sources without a reliable team key were retained at their native granularity and were not assigned to teams by inference.

### 3.2 Data sources and units of analysis

The study used the following persisted sources:

- `team_metrics.parquet`, with one row per team-semester keyed by `ID_Equipe` and `Semestre`, for integrated planning, churn, degradation, and AI-related variables;
- `planning_metrics.parquet`, with planning-activity and planning-artifact measures at team-semester level;
- `code_churn_metrics.parquet`, with temporal code-change and event measures at team-semester level;
- `technical_degradation_metrics.parquet`, with temporal complexity and degradation measures at team-semester level;
- `integration_friction_metrics.parquet`, with team-semester AI author-concentration signals and the configured pre-T3 AI window;
- `cut_context_metrics.parquet`, keyed by `Semestre` and `temporal_marker`, with six semester-cut observations for transcript/context signals;
- `student_nlp.parquet`, which preserves student-response granularity;
- `transcript_nlp.parquet`, which preserves transcript-session or corpus granularity; and
- evaluator, Git, statistical, manifest, and figure artifacts used to verify the derived measures and their provenance.

Team-semester metrics were used for the primary correlations and median-split comparisons. Team-semester-cut data supported temporal descriptions when the team key was present. Student responses and transcript sessions were not converted to team observations when their source keys did not support that operation. Transcript/context evidence was therefore analyzed by semester and temporal marker or corpus, not as a paired team-level predictor.

### 3.3 Temporal structure and aggregation

The evaluation schedule was represented by T1, T2, and T3. Evaluator records were keyed by `ID_Equipe`, `Semestre`, and `temporal_marker`; the persisted contract reports nine team rows per cut for 2025.2 and five team rows per cut for 2026.1. The analysis used these markers to construct initial, intermediate, and later-window variables without treating the two dates used for a distributed evaluation as separate conceptual cuts.

Planning variables were summarized over the configured planning windows. Code churn was summarized over temporal windows and retained the project’s binary-file policy: binary-file changes were counted as events but were not included in line-churn counts. Technical-degradation variables represented temporal values and deltas such as `technical_complexity_mean_t1` and `delta_dt_t1_t3`. The exact variable and window used for each claim were recorded in the data book and statistical manifest.

Aggregation was source-constrained. Team-level means, counts, deltas, and author shares were computed only where the source supplied the relevant team key. Cut-context means and medians remained cut-context quantities. Student and transcript NLP outputs remained at student-response and transcript-session/corpus granularity. No denominator was shared across these units.

### 3.4 Operational measures

The analysis used operational proxies rather than direct observations of the theoretical constructs.

- **Planning intensity (PI):** observable planning-artifact activity, including variables such as `pi_file_count_t1`, `pi_binary_event_count_t3`, `pi_deleted_count_t3`, and planning line deltas. PI represents artifact volume or activity under the project’s versioned definition; it is not a direct measure of planning quality, completeness, or design adequacy.
- **Code churn (CC):** code-change events and line-based churn measures, including `cc_per_source_loc_t3`, `cc_total_t3`, and temporal churn counts. Binary files were counted as events but excluded from line-churn counts. CC is therefore a repository-change signal, not an isolated measure of waste or rework.
- **Technical degradation (DeltaDT):** temporal complexity and related change measures, including `delta_dt_t1_t3` and intermediate deltas. These measures provide a bounded operational view of technical change rather than a complete measurement of technical debt.
- **AI-associated author concentration (AI):** Git-derived author-share measures within the configured 72-hour pre-T3 window, including `ai_max_author_share_before_t3_window` and related share distributions. This is a proxy for concentration in the available Git signal, not a complete measure of AI tool use, generated-code volume, or assistance quality.
- **Integration friction (IE):** transcript/context and related integration signals, including `ie_transcript_coordination_friction_score_mean` and `ie_transcript_rework_signal_score_mean`. These measures were retained at cut-context granularity where team pairing was unavailable. The primary transcript/context correlation was unavailable because of zero variance and sparse complete observations.

### 3.5 Statistical analyses

The primary statistical artifact was `correlation_results.csv`, governed by the persisted `spearman-correlation-results-v1` contract. It contained four persisted primary rows:

1. `pi_vs_cc_primary`, relating `pi_file_count_t1` to `cc_per_source_loc_t3` at team-semester level;
2. `pi_vs_delta_dt_primary`, relating `pi_file_count_t1` to `delta_dt_t1_t3` at team-semester level;
3. `ai_vs_cc_primary`, relating `ai_max_author_share_before_t3_window` to `cc_total_t3` at team-semester level; and
4. `context_ie_temporal_primary`, relating the two transcript/context signals at cut-context level.

Spearman correlations used complete available pairs. The first two analyses had 14 valid observations and no missing pair values. The AI analysis had seven valid observations out of 14 and was marked with a small-sample warning. The transcript/context analysis had three valid observations out of six and was marked unavailable because of zero variance. No confidence intervals or multi-test correction were reported in the persisted primary contract; the manuscript therefore does not add inferential claims beyond those recorded in the source.

`hypothesis_results.csv` contained three median-split comparisons: planning intensity versus code churn, AI concentration versus code churn, and transcript/context signal versus rework. These comparisons were treated as primary supporting checks, not as treatment effects. Small group sizes and insufficient group size were retained as explicit statuses.

Secondary cross-evidence analyses were reported separately from the primary family. They included global correlations, semester-stratified results, best/worst contrasts, leave-one-out sensitivity, extreme-case overlap, and category-level churn analyses. These outputs were used to identify candidate hypotheses and methodological warnings. Their multiplicity and mixed support/inconclusive statuses prevented them from being treated as independent confirmatory tests.

### 3.6 Missingness, exclusions, and unavailable results

Missingness was recorded at the source and analysis level rather than silently removed from the narrative. The primary AI analysis had seven missing AI-window observations. The transcript/context analysis had three missing observations and zero variance in the primary pair, so it was classified as unavailable rather than as a positive or negative result. The data book and statistical manifest record `n_total`, `n_valid`, `n_missing`, warnings, reasons, and status for each primary row.

File-category churn was subject to four documented exclusion classes: unknown file category (`1,436 events / 30 rows`), missing line counts (`14,287 events / 67 rows`), category warnings (`10,564 events / 33 rows`), and low-confidence categories (`26,567 events / 35 rows`). Category-based results were consequently treated as exclusion-sensitive methodological evidence, with the exclusion burden reported beside any related visual or claim.

The analysis did not impute unavailable transcript/context measures, invent team identifiers, or combine student-response, transcript-session, file-category, and team-semester denominators. These decisions preserve the distinction between an unavailable analysis and a null result.

### 3.7 Privacy, reproducibility, and artifact lineage

The paper-facing evidence package reports aggregate or anonymized outputs only. Raw prompts, raw transcripts, student identifiers, repository identities, private analytical Parquets, and identifying URLs are excluded from the public manuscript package. Transcript and student NLP artifacts remain restricted where their content or granularity could expose sensitive information.

Reproducibility is provided through persisted aggregate artifacts, producer contracts, metadata sidecars, exclusion manifests, statistical manifests, figure manifests, Phase 2.5 reports, and the Phase 3 data book. The report-first protocol makes the interpretive source visible, while the structured artifacts permit verification of the quoted values and denominators. Phase 3 did not rerun the pipeline or mutate the Phase 2 analytical artifacts.

## Method traceability controls

- Evidence register: [Phase 3 data book](../../data/analysis/paper_support/data_book.md).
- Statistical manifest: [statistical dataset manifest](../../data/analysis/statistical_dataset_manifest.json).
- Contract report: [Phase 2 contract report](../../data/analysis/phase2_contract_report.json).
- Claim control: [argument matrix](../../data/analysis/paper_support/argument_matrix.csv).
- Validity boundaries: [threats to validity](threats_to_validity.md).
- Manuscript placement: Sections 3.1--3.6 of the [manuscript outline](manuscript-outline.md).
- Status: draft for Task 4.2; exact prose, equations, and IEEE formatting require integration with the Results section and final venue template.
