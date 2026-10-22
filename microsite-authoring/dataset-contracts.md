# Dataset contracts for the paper companion

## Status and scope

This is the T002 specification for the future `data/catalog.json`, not the
catalog itself or approval to publish data. It consumes the T001 inventory in
[the implementation plan](plan.md). All proposed fields require the T003
publication allowlist. No research observations, private identifier mappings,
approval signatures, raw excerpts, or identifying source URLs belong here.

The tables below exhaust the T001 selection: 32 primary datasets, eight
figure-data inputs, and the supporting robustness inputs. Shared definitions
avoid publishing duplicate datasets. Descriptive summaries are frozen results,
not browser-side estimators.

Source filenames are neutral authoring references, not serving-time paths.
Primary files are under the paper's metric directory; figure/support files are
under its figure directory. Absolute source locations, original repositories,
participant hashes, and private pseudonym crosswalks stay outside this directory.

## 1. Mapping and validation conventions

### Public columns and data types

`source -> target` means rename; a bare name means retain that column unchanged.
Column lists below are explicit projections, not "copy everything" instructions.
Keys are included in every projection even when not repeated in its field list.
Every column not listed is excluded. New/missing source columns require review:
do not automatically include new columns or silently substitute missing ones.

Common key mappings:

| Source | Proposed public column | Type and meaning |
|---|---|---|
| `Semestre` | `cohort` | String cohort label; preserve the reviewed label exactly, never parse as a decimal year. |
| `temporal_marker` | `checkpoint` | Enum `T1`, `T2`, `T3`; never infer a missing checkpoint. |
| `ID_Equipe` | `team_id` | String from an explicitly approved private pseudonym registry, scoped by cohort. No original-to-public lookup is shipped. |
| `removed_Semestre` | `omitted_cohort` | Same cohort-label policy, for an omitted influence-analysis case. |
| `removed_ID_Equipe` | `omitted_team_id` | Same private registry as `team_id`, not a fresh influence-specific identity. |

The public team-semester key is the pair `(cohort, team_id)`, never `team_id`
alone. Public labels for encoded team-semester strings must be resolved with
that same private registry. Missing or ambiguous registry entries are blocking
errors, not permission to infer identifiers.

### Units and formatting shared by the tables

- Counts are nonnegative integers unless explicitly described as a mean/median.
  Units follow the named object: respondents, pairs, topic assignments, teams,
  commits, authors, files, file events, directories, extensions, tokens, characters,
  chunks, sessions, or lexical matches. Medians/means of counts may be fractional.
- `mean`, `std`, `median`, `q1`, `q3`, `iqr` retain the selected instrument's
  score units. M1 coded perception scores are 0-4, not M2's 1-5 Likert agreement.
  M1's raw autonomy distribution is a separate 1-5 item. No rescaling or
  cross-family composite is permitted.
- Churn, rework, and line-scope fields are changed lines under the paper's clean
  path policy, not defects. File counts and inferred structural metrics have
  separate units; do not conflate file events with distinct files.
- Shares, coverage, Gini coefficients, entropy, and normalized components are
  dimensionless. Shares and Gini are 0-1; fields ending `_pct` are 0-100 percentage
  points. Presentation may format fractions as percentages without changing
  downloadable values. CV is a nonnegative ratio, not restricted to 0-1.
- `planning_scope_log1p_t1` is the natural logarithm of one plus T1 changed-line
  scope, not raw lines. `window_end_day` is signed days relative to the T3 anchor.
  Durations/gaps are days; relative interval endpoints are signed days.
- Evaluator dimension means and descriptive composite means are score points on
  the original scorecard scale. Deltas are signed score-point differences, not
  percentages. The composite is the unweighted mean of four evaluator dimensions,
  not an official global quality score. Do not infer a new score range or
  normalize these values from the observed minimum/maximum.
- `spearman_rho`, other rho values, and rho deltas are dimensionless signed
  coefficients/differences. Rho is -1 to 1; a difference between two rho values
  can be -2 to 2. Exploratory p-values are 0-1 and never confirmatory significance.
- Boolean fields must become JSON booleans, accepting only documented source
  encodings (`True`/`False` in CSV). Enums/labels/definitions/regex patterns are
  strings. Numeric CSV categories require explicit parsing only where specified.
  Text must never be interpreted as HTML.
- Keys must be present, non-null, and unique at the stated grain. Validate counts,
  schemas, finite numeric values, and documented null states before export.
  JSON uses `null`, never `NaN`, an empty string, or an invented numeric value.
  Filtered CSV uses an empty numeric cell plus its explicit status/eligibility.
- Native data precision is retained. Permitted public transformations are
  renaming, approved pseudonym replacement, strict scalar parsing, documented
  JSON flattening, and explicitly flagged eligibility masking. No imputation,
  value perturbation, implicit pooling, or new statistical estimation is allowed.

### Keys, filters, and coverage shorthand

| Code | Public key / grain | Permitted filters |
|---|---|---|
| `C` | `cohort` | Cohort |
| `CP` | `cohort, checkpoint` | Cohort, checkpoint |
| `T` | `cohort, team_id` (team-semester) | Cohort, team-semester |
| `TP` | `cohort, team_id, checkpoint` | Cohort, team-semester, checkpoint |
| `P` | `checkpoint` (fixed pooled population) | Checkpoint only; no cohort/team filter |
| `W` | `window_end_day` (fixed pooled population) | Relative day only; no cohort/team filter |

Additional key dimensions in the tables are also permitted categorical filters
unless expressly prohibited. Numeric sorting is allowed for measures, but sorting
does not change eligibility or denominators. No freeform cross-dataset joins.

At this snapshot, `CP` spans two cohorts and three checkpoints; `T` has 14
team-semesters (9 + 5); `TP` has 42 cells. Smaller sample sizes must remain attached
to the specific measure. Missing category rows are not automatically synthesized
as zero. Survey distributions and paired summaries never acquire team filters.

## 2. Primary metric contracts

The public dataset IDs below also determine future JSON/CSV basenames.
The source column `n` is renamed contextually to avoid ambiguous denominators.

### RQ1 - Self-report and coded perceptions

| Source | Public ID | Key / grain | Proposed fields beyond keys | Denominator / eligibility |
|---|---|---|---|---|
| `m1_rq1_perception_panel_long.csv` | `m1-perceptions` | `CP + perception_family` | `perception_group, mean, std, median, q1, q3, iqr, n -> response_n, student_n -> cohort_response_n, coverage, measurement_status` | `response_n / cohort_response_n` for the same cohort/checkpoint/family. Available observations only; 36 rows. Six coded 0-4 families retain separate interpretations. |
| `m1_rq1_usage_frequency.csv` | `m1-frequency` | `CP + measure + category` | `count, respondent_n, share` | `count / respondent_n` within cohort/checkpoint/measure. Frequency categories remain ordered labels. |
| `m1_rq1_usage_tasks.csv` | `m1-tasks` | `CP + measure + category` | `count, respondent_n, share` | Respondents selecting a task divided by respondents in the cell. Multi-select: category shares need not sum to one. |
| `m1_rq1_usage_tools.csv` | `m1-tools` | `CP + measure + category` | `count, respondent_n, share` | Same multi-select rule as tasks. Review free-text-derived tool category labels under T003. |
| `m1_rq1_prior_ai_project_experience.csv` | `m1-prior-experience` | `CP + measure + category` | `count, respondent_n, share` | `count / respondent_n` for observed answers; not total course enrollment. |
| `m1_rq1_autonomy_tool_balance.csv` | `m1-autonomy` | `CP + measure + category` | `count, respondent_n, share` | Raw 1-5 autonomy item, with `category` a strictly parsed integer. Not the coded 0-4 perception family. |
| `m1_rq1_career_impact_topics_exploratory.csv` | `m1-career-topics` | `CP + topic` | `count, respondent_n -> topic_assignment_n, share_of_topic_assignments, coding_status` | The source `respondent_n` is actually total topic assignments, as verified in the producer. `count / topic_assignment_n`, not respondent prevalence. Unvalidated rule-based supplement, with the warning always visible. |
| `m2_role_perception_distributions.csv` | `m2-role-distributions` | `CP + role + score` | `count, respondent_n, share` | Count at a 1-5 Likert score divided by role-specific observed responses. Score is an integer filter; retain observed categories without filling absent categories. |
| `m2_role_perception_by_team_semester.csv` | `m2-role-summaries` | `CP + role` | `n -> response_n, mean, std, median, q1, q3, iqr, disagreement_share, neutral_share, agreement_share` | Each share uses `response_n`; disagreement is scores 1-2, neutral 3, agreement 4-5. The filename is misleading: this is not team-level data. |
| `m2_role_perception_paired_t1_t3.csv` | `m2-paired-sensitivity` | `C + role` | `pairs -> pair_n, mean_T1 -> mean_t1, mean_T3 -> mean_t3, mean_change, median_change, increased_share, unchanged_share, decreased_share` | Only observed T1/T3 pairs for that cohort/role. Shares divide by `pair_n`; change is T3 minus T1, in Likert points. No checkpoint/team/respondent filter or respondent hashes. |

`perception_family`, `measure`, `category`, `topic`, `role`, and `score` are keys
when shown after `+`, and must be in the public output. English display labels
belong in the catalog; source category tokens remain stable in downloads.
Codebook translations must not invent new categories.

### RQ2 - Repository and global transcript evidence

| Source | Public ID | Key / grain | Proposed fields beyond keys | Denominator / eligibility |
|---|---|---|---|---|
| `m3_author_activity_participation.csv` | `m3-participation` | `T` | `total_commit_n, pre_commit_n, post_commit_n, final_window_commit_n, pre_share, post_share, final_window_share, small_denominator_lt_10, measurement_status` | Each share divides by `total_commit_n`. Pre is `[T3-7d,T3)`, post `[T3,T3+7d)`, final window is their **14-day union**. Total is history observed before T3+7d. Ratios are null if total is zero; flag totals below 10. Exclude `repository` and `presentation_anchor`. |
| `m3_author_concentration.csv` | `m3-author-concentration` | `T + phase` | `commit_n, active_days, author_n, max_author_share, author_gini, measurement_status` | `phase` is pre/post as above. Max-author share divides by phase commit count. No-activity counts are observed zeros, but concentration statistics remain null and status is `no_observed_activity`. |
| `m3_activity_rolling_7day.csv` | `m3-rolling` | `T + window_end_day` | `commit_n, active_days, author_n, max_author_share, author_gini, measurement_status` | Window `[offset-7,offset)` relative to T3; 29 offsets per team, overlapping, not independent cases. Exclude absolute `window_start`, `window_end`, and constant `phase`. Relative day is a filter. |
| `m3_activity_rolling_7day_pooled.csv` | `m3-rolling-pooled` | `W` | `team_semester_n, active_team_semester_n, total_commit_n, mean_commit_n, median_commit_n, max_commit_n, median_active_days, median_max_author_share, median_author_gini, active_team_semester_share` | Active share divides by `team_semester_n`; concentration medians exclude unavailable statistics as in the producer. Keep fixed pooled grain in catalog; never filter by cohort or recompute a selected-team estimate. |
| `m4_churn_magnitude.csv` | `m4-checkpoint-churn` | `TP` | `clean_churn, all_churn, clean_unique_file_n, clean_touching_commit_n, median_clean_churn_per_touching_commit, max_clean_churn_per_touching_commit, clean_share_of_all_churn, measurement_status` | Clean/all share divides by `all_churn`. Commit statistics use clean-touching commits only. `no_clean_change_observed` is not a missing team; undefined ratios/commit summaries stay null. |
| `m4_churn_magnitude_pooled.csv` | `m4-checkpoint-pooled` | `P` | `team_semester_n, observed_clean_team_semester_n, total_clean_churn, median_clean_churn, total_all_churn, median_clean_unique_file_n, clean_share_of_all_churn` | Fixed cohort-pooled checkpoint results. Share is pooled clean/all lines; observed-clean coverage is 7 / 10 / 14. Retain medians from the producer, not a new median of a filtered population. |
| `m4_artifact_composition_pooled.csv` | `m4-path-composition` | `P + file_category` | `included_in_m4, team_semester_n, file_event_n, unique_file_n, churn_lines, churn_share` | Churn share uses all category churn at the checkpoint, including excluded paths. `included_in_m4` is boolean and an additional valid filter. Counts remain pooled distinct/event definitions, not reconstructed unique identities. |
| `m5_marker_density.csv` | `m5-marker-density` | `P` (2025.2 global corpus only) | `transcript_chunk_n, source_session_n, character_n, token_n, friction_marker_n, alignment, handoff, integration, blocker, rework, friction_marker_density_per_1k_tokens, measurement_status` | Density is lexical matches / `token_n` * 1000. Category fields are match counts, not people or teams. Exclude constant `analysis_level` from rows and declare it in catalog. |
| `m5_marker_composition.csv` | `m5-marker-composition` | `P + friction_subtype` | `friction_marker_n, marker_n, marker_share` | `marker_n / friction_marker_n` for that checkpoint, not per token. Five subtypes; no team or cohort selection. |
| `m5_corpus_coverage.csv` | `m5-corpus-coverage` | `P` (2025.2 global corpus only) | `transcript_chunk_n, source_session_n, character_n, token_n, friction_marker_n, observed_semester_n` | Counts describe corpus coverage. Reviewed cohort scope is a catalog constant from `observed_semesters`, not a team join dimension. Do not synthesize 2026.1 rows. |
| `m5_lexicon.json` | `m5-lexicon` | `lexicon_version + subtype` (definition rows) | `version -> lexicon_version; patterns.<subtype> -> pattern; patterns key -> subtype; language; counting_rule` | Flatten five pattern entries; duplicate `version`, `language`, `counting_rule` into each definition row. Pattern is a regex string, never executed on user input. No denominator; filters subtype/version only. |

The M3 participation final window must be labeled "T3 +/- 7 days (14 days)".
The separate concentration support datasets below use their existing final-seven
policy. Preserve that distinction even where the manuscript uses informal
"final-window" terminology.

### RQ3 - Artifacts, rework, and associations

| Source | Public ID | Key / grain | Proposed fields beyond keys | Denominator / eligibility |
|---|---|---|---|---|
| `m6a_structural_planning.csv` | `m6a-structural-planning` | `T` (T1 evidence) | `pi_available, pi_file_count_t1, pi_line_delta_t1, pi_renamed_count_t1, pi_deleted_count_t1, pi_binary_event_count_t1, planning_artifact_activity_t1, planning_artifact_present_t1, planning_scope_log1p_t1, measurement_status` | No ratio denominator. Presence/availability are booleans; `planning_artifact_activity_t1` is an artifact-event count, not a boolean. Scope/counts are separate structural evidence, not quality. Publish a reviewed unavailability reason only if one exists, as described below. |
| `m6b_llm_planning_content.json` | `m6b-planning-content` | `T` (T1 evidence) | Derived fields specified below; never copy JSON records. | 9 successful extractions; 5 `unavailable_not_measured`. Successful empty lists are measured zero; unavailable fields are null, not zero. |
| `m7_checkpoint_inactivity.csv` | `m7-checkpoint-inactivity` | `TP` | `commit_n_7d, repository_inactive_7d, measurement_status` | Seven days before each team's checkpoint-specific evaluator anchor, not universally the T3 anchor. Inactivity is a boolean timing observation, not evidence of absent planning. Exclude anchors and absolute window dates. |
| `m8_rework_magnitude.csv` | `m8-rework-magnitude` | `T` (T3) | `clean_rework_churn_t3, clean_deferred_churn_t3, prior_clean_path_n, clean_total_churn_t3, baseline_eligible_for_rework_t3, clean_rework_ratio_t3, measurement_status` | Ratio = rework / total clean T3 lines; interpret only if baseline eligible and total > 0. Keep magnitudes for all cases but apply the ratio policy below. |
| `m8_rework_participation.csv` | `m8-rework-participation` | Alias of `m8-rework-magnitude`, same `T` | Same mapped fields except `prior_clean_path_n` | Verify equality with the magnitude projection; do not load/download a duplicate dataset. |
| `m8_baseline_eligibility.csv` | `m8-baseline-eligibility` | `T` | `prior_clean_path_n, baseline_eligible_for_rework_t3, measurement_status` | Eligibility is `prior_clean_path_n > 0`; 12 eligible and 2 baseline-not-observed. Additional boolean eligibility filter is permitted. |
| `m9_planning_vs_rework_m6a_m8a.csv` | `m9-structural-rework-magnitude` | `analysis_id + predictor + outcome` (fixed association) | `n -> sample_n, spearman_rho, spearman_p_exploratory` | Pairwise measured cases; 14 in the current magnitude analysis. Metadata stratum `all_team_semesters`; no team/cohort filter. |
| `m9_planning_vs_rework_m6a_m8b_eligible_stratum.csv` | `m9-structural-rework-ratio` | `analysis_id + predictor + outcome` | `n -> sample_n, spearman_rho, spearman_p_exploratory` | Baseline-eligible, defined ratio pairs only; 12 currently. Stratum `baseline_eligible_only`. |
| `m9_planning_vs_outcomes_m6a_t3.csv` | `m9-structural-outcomes` | `analysis_id + predictor + outcome` | `n -> sample_n, spearman_rho, spearman_p_exploratory` | Pairwise observed independent T3 dimension scores; 14 currently. Stratum `all_team_semesters`. |
| `m9_planning_vs_outcomes_m6b_t3_if_approved.csv` | `m9-content-outcomes` | `analysis_id + predictor + outcome` | `n -> sample_n, spearman_rho, spearman_p_exploratory` | Only successful reviewed M6b cases with observed outcome, at most 9. Stratum `m6b_structured_content`; review-gated, exploratory, separate predictors. |
| `m9_leave_one_out_intervals.csv` | `m9-leave-one-out` | `analysis_id + predictor + outcome + omitted_cohort + omitted_team_id` | `n_remaining -> remaining_sample_n, spearman_rho, spearman_p_exploratory` | Use private mapping for removed identifiers. Original eligibility restrictions survive each omission. Estimates may be null for constant variables/insufficient pairs; no inferred zero or invented p-value. Not confidence intervals. |

For M9, `analysis_id`, `predictor`, and `outcome` are reviewed enum strings with
English descriptions in the catalog, not private provenance paths. Permit
predictor/outcome selection and catalog-declared stratum selection, not per-team
re-estimation. An omitted-case filter selects existing leave-one-out rows only.

**M6a optional reason:** `pi_unavailable_reason` may map to
`unavailable_reason_code` only through a reviewed enum dictionary, not arbitrary
text. The inspected snapshot has no unavailable M6a cases. Exclude that column
if the dictionary is empty; do not create a success-shaped default reason.
Definition version, observation unit, and analysis level belong in catalog metadata.

**M6b flattening:** retain the common key mappings and map `status` to
`measurement_status`. For successful records, map
`parsed_response.planning_evidence_present` to `planning_evidence_present`
(boolean); the array lengths of `parsed_response.goals`,
`architecture_or_design`, `task_decomposition`, `risk_or_dependency`, and
`evidence_quotes` map to `goals_n`, `architecture_or_design_n`,
`task_decomposition_n`, `risk_or_dependency_n`, and `evidence_quotes_n`
(nonnegative evidence-item counts). Counted quotes are not themselves published.
For unavailable records, these six values are null; verify the unavailable status
instead of dereferencing absent parsed content. Exclude all list elements,
input subjects, commit hashes, raw responses, model/prompt details, timestamps,
and free-text reasons. No composite planning-quality score.

**M8 ratio policy:** preserve the canonical source cell in private provenance,
but export/display `clean_rework_ratio_t3 = null` when baseline ineligible or total
clean T3 churn is zero. Add `ratio_status` with exactly `available`,
`baseline_not_observed`, or `zero_clean_churn` (baseline-not-observed takes
precedence). A numeric source ratio in an ineligible case is not a publishable
estimate. Document this semantic masking in catalog/download guidance; do not
alter eligible numeric ratios. Apply the same policy to any selected figure/profile
ratio and verify eligibility through the cohort-plus-team join.

## 3. Figures: aliases and genuinely distinct datasets

Aliases specify verified equivalence, not a blind choice between files. Compare
shared fields by semantic keys before export. Small floating-point serialization
differences already identified by T001 do not authorize source-value rounding:
use the canonical metric table for aliases and derive only display labels.

| Figure-data source | Public dataset / projection | Contract |
|---|---|---|
| `rq1_m1_perception_with_sd_data.csv` | Alias `m1-perceptions` | Same CP/family key and fields. `family_label`, `checkpoint_order` are catalog display/order metadata, not extra measures. |
| `rq2_m3_activity_pooled_data.csv` | Alias `m3-rolling-pooled` | Same W key/units; no cohort dimension. |
| `rq2_m4_m5_checkpoint_data.csv` | Alias `m4-checkpoint-pooled` | M4-only data, despite the filename. |
| `rq2_m5_density_data.csv` | Alias `m5-marker-density` | Separate M5 panel; never a team-level join to M4. |
| `rq3_architectural_artifact_presence_data.csv` | `m6a-presence-by-cohort` | Key C + `evidence_state`; retain `team_semester_n, team_semester_count` as denominator/count. Two states per cohort; filters cohort/state. No new presence percentages needed. |
| `rq3_architecture_rework_profile_data.csv` | `planning-rework-profile` | Key T; project `pi_file_count_t1, pi_line_delta_t1, planning_artifact_present_t1, planning_scope_log1p_t1, measurement_status, clean_rework_churn_t3, baseline_eligible_for_rework_t3`. Count/lines/log units as above; no ratio. Exclude duplicate `cohort`, source `eligibility_label`, and unused artifact-detail fields. Compare with M6a/M8 by T before export. |
| `rq3_technical_complexity_vs_rework_data.csv` | `complexity-rework-figure` | Key T; project `technical_complexity_mean_t3, clean_rework_churn_t3, clean_rework_ratio_t3, planning_scope_tier, planning_scope_log1p_t1, score_trajectory_group, final7_commit_share_pct, final7_clean_churn_share_pct`. Add approved baseline eligibility and `ratio_status` from M8 by T; discard ambiguous source eligibility label after validation. Filters T/planning tier/eligibility; original scale and fixed bins. |
| `rq2_planning_vs_final7_commit_concentration_data.csv` | `planning-final7-commits` | Contract in Section 4; this is also the included planning/concentration figure. |

Figure definitions in the future catalog map the seven T001 figures to the IDs
above, with the M4/M5 figure referencing two independent datasets. Every plotted
value remains available in a table. Logarithmic rework axes must explain handling
of zero without replacing the stored zero.

## 4. Supporting robustness contracts

All bins, thresholds, strata, normalization, sample sizes, and coefficients are
the existing paper results; filters select rows, never recompute them.

| Source | Public ID | Key / grain | Proposed fields beyond keys | Denominator / eligibility / additional filters |
|---|---|---|---|---|
| `rq2_phase_activity_share_data.csv` | `phase-activity` | `T + phase` | `phase_order, commit_n, clean_churn, active_day_n, active_author_n, score_trajectory_group, planning_scope_tier, evaluator_score_t3, delta_score_t3_minus_t1, team_total_commit_n, team_total_clean_churn, commit_share_pct, clean_churn_share_pct` | Phase activity / team's total activity * 100, by metric. Four mutually exclusive phases; periods defined in metadata. Exclude absolute `period_start, period_end`. Filters phase/trajectory/planning tier/T. Phase order is an integer ordinal, not a duration. |
| `rq2_phase_activity_share_summary.csv` | `phase-activity-summary` | `score_trajectory_group + phase` | `phase_order, team_semester_n, mean_commit_share_pct, median_commit_share_pct, mean_clean_churn_share_pct, median_clean_churn_share_pct, mean_active_day_n, mean_active_author_n` | Fixed trajectory-group summary; 12 rows. Original group N and percentage units; no cohort/team filter or rebinned trajectory. |
| `rq2_score_delta_vs_final7_commit_concentration_data.csv` | `score-final7-commits` | `T` | `evaluator_score_t1, evaluator_score_t3, delta_score_t3_minus_t1, score_trajectory_group, planning_scope_tier, final7_share_pct, activity_metric, final7_concentration_tier, delta_direction, quadrant` | Final-seven commit count / full observed project commit count * 100. Existing project-period policy, not M3's 14-day final window. Filter T/trajectory/tier/quadrant; threshold notes below. |
| `rq2_score_delta_vs_final7_clean_churn_concentration_data.csv` | `score-final7-clean-churn` | `T` | Same fields as `score-final7-commits` | Same temporal policy but clean changed-line numerator/denominator. Retain activity metric label so the measures cannot be confused. |
| `rq2_score_delta_final7_quadrants.csv` | `score-final7-quadrants` | `activity_metric + quadrant + planning_scope_tier` | `final7_concentration_cut, final7_concentration_median_pct, delta_threshold, team_semester_n, median_final7_share_pct, median_delta_score_t3_minus_t1` | Fixed full-sample cut and within-cell N. Exclude `team_semesters` and prose `interpretation`; provide reviewed English meaning in catalog. No team/cohort filter. |
| `rq2_planning_vs_final7_commit_concentration_data.csv` | `planning-final7-commits` | `T` | `planning_scope_log1p_t1, planning_scope_tier, evaluator_score_t3, delta_score_t3_minus_t1, clean_rework_churn_t3, final7_share_pct, activity_metric, final7_concentration_tier, planning_concentration_quadrant, abs_delta_score_t3_minus_t1, marker_size` | Same commit-based final-seven policy as above. Preserve `marker_size` (rendering-size units) for figure fidelity; absolute delta is score points. Filters T/tier/quadrant; no recalculated median. |
| `rq2_planning_vs_final7_clean_churn_concentration_data.csv` | `planning-final7-clean-churn` | `T` | Same fields as `planning-final7-commits` | Same contract using clean changed lines. |
| `rq2_planning_concentration_quadrant_summary.csv` | `planning-final7-quadrants` | `activity_metric + quadrant` | `team_semester_n, team_semester_denominator, mean_t3_score, median_t3_score, mean_delta_score, median_delta_score, mean_clean_rework_churn_t3, small_n_flag` | Cell count and fixed full-population denominator are separate. Score points versus mean changed lines. Exclude `team_semesters, interpretation`; retain boolean small-N warning. |
| `rq2_operational_regularity_data.csv` | `operational-regularity` | `T` | `delta_score_t3_minus_t1, score_trajectory_group, planning_scope_tier, final7_commit_share_pct, final7_clean_churn_share_pct, active_day_count, project_span_days, active_day_share, max_inactivity_gap_days, median_inactivity_gap_days, commit_weekly_cv, clean_churn_weekly_cv, temporal_entropy_commits, temporal_entropy_clean_churn, author_count, max_author_share, author_gini, m7_window_count, m7_inactive_window_share, regularity_index` plus the eight components below | `active_day_share = active_day_count / project_span_days`; M7 inactive share divides by `m7_window_count`. Index/components/entropy dimensionless; time gaps in days; CV dimensionless. Filters T/trajectory/planning tier. Fixed full-sample normalization, no filter-time min-max. |
| `rq2_m5_2025_triangulation_summary.csv` | `transcript-context-2025` | `P` (2025.2 only) | `team_n, m5_friction_marker_density_per_1k_tokens, m5_friction_marker_n, m5_token_n, median_clean_churn, mean_clean_churn, median_evaluator_score_composite, mean_evaluator_score_composite, baseline_eligible_rework_team_n, median_clean_rework_churn_t3, median_clean_rework_ratio_t3_baseline_eligible` | Contextual repository/score summaries across `team_n`, alongside one global corpus density (matches / tokens * 1000). The source repeats fixed T3 rework context on every checkpoint row: retain those values, label their field time scope as T3, and never plot them as checkpoint-varying measurements. Ratio uses eligible cases only. Never interpret M5 as nine team observations. |
| `rq3_complexity_profile_data.csv` | `complexity-profile` | `T` | Explicit projection below | Distinguish evaluator score points from structural counts, inferred file/commit means, and file-event shares. Use M8 ratio policy. Filters T/planning tier/trajectory/eligibility. |
| `rq3_complexity_confounding_summary.csv` | `complexity-stratified-associations` | `relationship` | `relationship_label, predictor, outcome, rho_without_complexity_stratification, rho_within_low_complexity, rho_within_high_complexity, complexity_stratification_variable, complexity_median, low_complexity_rule, high_complexity_rule, n_without_complexity_stratification, n_within_low_complexity, n_within_high_complexity, minimum_n_for_rho` | Each rho keeps its own N. Median 1.875 score points, low <= median, high > median; minimum N 4. Ratio relationships retain baseline eligibility. `filter_column` and method become reviewed catalog definitions, not executable field expressions. Filter relationship only. |
| `rq3_influence_map_data.csv` | `influence-cases` | `relationship_id + omitted_cohort + omitted_team_id` | `relationship_label, predictor, outcome, full_sample_n, loo_n, full_sample_rho, loo_rho, rho_delta_from_full, abs_rho_delta_from_full, full_sample_sign, loo_sign, sign_changed, availability_status` | 13 relations x 14 omitted cases (182 rows); some omissions are ineligible and need not reduce eligible N. Preserve `availability_status` and null rho values. Filters relationship/omitted case/status, no re-estimation. |
| `rq3_influence_relationship_contract.csv` | `influence-relations` | `relationship_id` | `relationship_label, predictor, outcome, full_sample_n, leave_one_out_rows, available_leave_one_out_rows, full_sample_rho, full_sample_sign, loo_min_rho, loo_max_rho, max_abs_rho_delta_from_full, sign_preservation_share, availability_status` | Sign-preservation share denominator is available omissions, not assumed 14; preserve producer counts. Minimum eligible pair N is 4. Exclude task references, source `filter_column`, and prose; declare eligibility/method in catalog. |
| `rq3_directional_robustness_summary.csv` | `influence-summary` | `relationship_id` | `full_sample_rho, loo_min_rho, loo_max_rho, sign_preservation_share, most_influential_team_semester -> most_influential_case, max_abs_rho_delta_from_full, available_leave_one_out_rows, total_leave_one_out_rows, unstable_sensitivity_flag` | Resolve combined most-influential label through the private registry, never string-pass it through. Same relation eligibility/sign-preservation semantics. Filters relationship/unstable flag; counts distinguish unavailable omissions. |

The eight retained regularity components are
`regularity_active_day_share_component`, `regularity_commit_entropy_component`,
`regularity_clean_churn_entropy_component`,
`regularity_commit_weekly_cv_component`,
`regularity_clean_churn_weekly_cv_component`, `regularity_m7_activity_component`,
`regularity_commit_distribution_component`, and
`regularity_clean_churn_distribution_component`. Each is a 0-1 number; the
existing `regularity_index` averages these components and is not a validated
Agile-process scale. The daily timeline spans first observed commit day through
the T3 anchor day inclusively; weekly zeros exist only inside that observed
period. Regularity's author count/share/Gini come from M3's pre-T3 seven-day
window, not the entire daily timeline. M7 inactivity uses its 71 overlapping
windows per team, not 71 independent projects.

The `complexity-profile` projection is
`technical_complexity_mean_t1, technical_complexity_mean_t2,
technical_complexity_mean_t3, delta_technical_complexity_t3_minus_t1,
clean_distinct_file_n, clean_distinct_directory_n, clean_max_path_depth,
clean_extension_n, clean_touching_commit_n_inferred, clean_total_churn_inferred,
frontend_clean_file_event_n, backend_clean_file_event_n, mixed_clean_file_event_n,
unclassified_clean_file_event_n, mean_clean_files_per_commit,
frontend_clean_file_event_share, backend_clean_file_event_share,
clean_churn_t3, all_churn_t3, m4_clean_unique_file_n_t3,
m4_clean_touching_commit_n_t3, clean_rework_churn_t3, clean_rework_ratio_t3,
baseline_eligible_for_rework_t3, measurement_status, planning_artifact_present_t1,
planning_scope_log1p_t1, pi_file_count_t1, pi_line_delta_t1, score_trajectory_group,
planning_scope_tier, final7_commit_share_pct, final7_clean_churn_share_pct`.
Add `ratio_status` under the M8 policy. `clean_max_path_depth` is an integer path
depth; inferred touching commits count distinct observed commits touching clean
paths. Frontend/backend event shares divide by all classified and unclassified
clean file events; they do not imply a manually assessed architecture.

### Definition-only and redundant supporting inputs

These inputs still receive a contract, but not a duplicate data-browser tab:

| Source | Disposition and source-to-public mapping | Key / eligibility / units |
|---|---|---|
| `rq2_nonoverlapping_weekly_bin_contract.csv` | Catalog-only `weekly-bin-definitions`: project `week_bin, week_bin_order, start_day_relative_to_t3, end_day_relative_to_t3, interval_notation, assignment_policy, rolling_window_used`; deduplicate identical definitions across private team keys. Exclude team identifiers and absolute dates. | Key `week_bin`; verify 13 distinct definitions across 182 source rows, `[start,end)` notation, non-rolling flag. Endpoints in signed days, order integer, policy text. No denominator or team filter. |
| `rq3_complexity_metrics_contract.csv` | Catalog-only `complexity-definitions`: `metric, construct_family, definition, heuristic_or_policy, manual_genai_architecture_classification`. Exclude `source, plan_requirement`; review all free text for private paths before release. | Key `metric` (13 definitions); family/metric filters, no observation denominator. Definition/policy strings and boolean classification flag. |
| `rq3_influence_heatmap_matrix.csv` | Verification-only pivot of `influence-cases`, not a second public estimate table. `removed_team_semester` resolves to omitted cohort/team through private registry; each relation-label column resolves to `relationship_id` using the relation contract. Cells represent `rho_delta_from_full`. | Source key `removed_team_semester`; public long key is relation/omitted case. Verify every corresponding cell, including nulls, against the long table; never expose embedded original identifiers in headers/rows. |
| `rq2_score_trajectory_base_data.csv` | Derivation context only: project common T keys, `evaluator_score_t1, evaluator_score_t2, evaluator_score_t3, delta_score_t3_minus_t1, delta_score_t2_minus_t1, delta_score_t3_minus_t2, score_trajectory_group, planning_present_t1, planning_scope_log1p_t1, planning_scope_tier, final7_commit_share_pct, final7_clean_churn_share_pct`. Map `planning_present_t1` to catalog's `planning_artifact_present_t1` definition. | Key T; validate agreement with selected figures/profiles. Score-point/delta, boolean presence, log scope, percent concentration. No new public view or raw evaluator download. |

### Frozen thresholds and interval definitions

- Planning high tier requires an observed artifact and scope >= the original
  sample median `1.791759469228055`; this is not a quality threshold.
- Higher final-seven concentration is >= the original activity-specific median:
  commits `43.743509865005194%`, clean churn `34.99461573513386%`. Never recalculate
  after filtering. Numerators include `[T3-7d,T3)` events; denominators include
  all observed project events strictly before T3. They exclude post-T3 activity,
  unlike M3 participation's total. This existing full-period policy must
  accompany the catalog definition.
- `delta_direction` uses delta **> 0.125**, not simply > 0. Existing trajectory
  groups use the registered adaptive signed threshold, now fixed at 0.125.
  Preserve source labels and explain this descriptive rule rather than
  reclassifying observations in the explorer.
- Four phase-share intervals are `pre_t1`, `t1_to_t2`,
  `t2_to_t3_excluding_final7`, and `final7_pre_t3`. Last phase is the seven days
  before T3, not a post-T3 window; `pre_t1` can vary in duration. Catalog definitions
  explain the paper's boundaries without publishing absolute timestamps.
- Weekly definition intervals cover the last 91 days before T3 in 13 exclusive
  seven-day bins. They are not additional independent team-semesters.

## 5. Allowed relationships and publication rules

1. Join approved M6a/M6b/M8 and paper-derived team-semester profiles only on
   `(cohort, team_id)` with an explicit one-to-one check; checkpoint tables require
   the checkpoint key as well. Require matching cohort/team coverage; no best-effort
   joins. Use this for field/eligibility verification, not arbitrary UI joins.
2. Align cohort/checkpoint survey summaries side by side only at that grain.
   Never attach them to individual teams, multiply their denominators by team
   count, or join the paired sensitivity summaries to respondents.
3. M5 density/composition/coverage can align by checkpoint within its one corpus.
   Side-by-side repository context is descriptive. Do not assign global M5 values
   to teams or infer observations for the unmeasured cohort.
4. Fixed pooled tables, group summaries, associations, medians, and influence
   diagnostics are immutable rows with their own sample sizes. Display active
   row filters, but clearly label the unchanged estimation population.
5. Review every categorical/prose field, definition, regex, downloadable header,
   and chart label under T003. Strip identifying paths/URLs and replace only
   through explicit approved dictionaries, not generic ad hoc text replacement.
   No suppression threshold, cohort relabeling, or private crosswalk is assumed
   to be approved by this document.
6. No full transcripts, exact commit subjects/hashes, respondent/author identities,
   raw evaluation votes, model output, source filenames carrying identities, or
   list-valued provenance fields are proposed. Excerpts remain a separate T004
   process; counts of quotes do not authorize showing their text.
7. Definitions from the ten primary metadata files and seven robustness metadata
   files named in the plan are extracted selectively into the public catalog.
   Do not publish those internal metadata files or their absolute paths/hashes
   wholesale. Public release hashes describe public exports, not private sources.

## 6. T002 verification and implementation handoff

Before marking T002 complete, check all selected sources exist, source projections
and key columns match real schemas, keys are unique/non-null, all special
denominators/eligibility states above match producers, and every T001 selected
source has a disposition here. Verify definition-only and alias contracts as well
as the datasets that receive public IDs.

T003 must approve or narrow these projections; T006 implements strict preparation
and validation; T007 turns the approved descriptors into `data/catalog.json`.
T008 produces public rows/downloads only after those gates. This specification
creates no runtime dependency, no new analysis, and no approval bypass.
