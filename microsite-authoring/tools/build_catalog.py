"""Build public metadata from explicit contracts, without reading private research inputs."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from prepare_snapshot import ContractError, json_bytes, require  # noqa: E402
from snapshot_contracts import (  # noqa: E402
    BOOLEAN_FIELDS, INTEGER_FIELDS, NULLABLE_FIELDS, RENAMES, TABLES, TEXT_FIELDS,
)

# Each entry gives the title, analytical grain, denominator, and interpretation.
DESCRIPTIONS = {
    "m1-perceptions": (
        "Coded perceptions", "Cohort / checkpoint / perception family",
        "Observed family responses / all observed cohort-checkpoint responses.",
        "Six separately coded 0-4 perception families; retain mean, standard deviation, quantiles, and coverage.",
        "Self-report is not AI-use telemetry. Standard deviation is not a confidence interval."),
    "m1-frequency": (
        "AI-use frequency", "Cohort / checkpoint / measure / category",
        "Category count / observed respondents for that measure and cell.",
        "General and software-related AI-use frequency distributions.",
        "Observed answers are not course enrollment; categories remain ordered labels."),
    "m1-tasks": (
        "AI-use tasks", "Cohort / checkpoint / measure / category",
        "Respondents selecting the task / respondents in that cell.",
        "Multi-select AI-assisted task categories.", "Shares need not sum to one; self-report is not telemetry."),
    "m1-tools": (
        "Reported AI tools", "Cohort / checkpoint / measure / category",
        "Respondents selecting the tool / respondents in that cell.",
        "Multi-select tool categories, retaining the approved source vocabulary.",
        "Shares need not sum to one. Similar spellings are not silently merged."),
    "m1-prior-experience": (
        "Prior AI project experience", "Cohort / checkpoint / measure / category",
        "Category count / observed answers.", "Prior AI-assisted project experience.",
        "Not a count of all enrolled students or observed tool usage."),
    "m1-autonomy": (
        "Autonomy and tool balance", "Cohort / checkpoint / measure / integer category",
        "Category count / observed answers.", "Distribution of the raw 1-5 autonomy item.",
        "This is not the coded 0-4 autonomy perception family; do not rescale or combine them."),
    "m1-career-topics": (
        "Exploratory career-impact topics", "Cohort / checkpoint / topic",
        "Topic assignments in the category / all topic assignments in that cell, not respondents.",
        "Rule-based supplementary topic coding.",
        "Unvalidated exploratory coding; no respondent-prevalence or confirmatory interpretation."),
    "m2-role-distributions": (
        "Role transformation: agreement distributions", "Cohort / checkpoint / role / Likert score",
        "Score-category responses / observed responses for that role and cell.",
        "1-5 Likert agreement about role extinction or severe transformation.",
        "The prompt combines extinction and transformation. There is no team identifier."),
    "m2-role-summaries": (
        "Role transformation: summaries", "Cohort / checkpoint / role",
        "Observed role-specific responses; disagreement 1-2, neutral 3, agreement 4-5.",
        "Summary scores and response shares on the original 1-5 scale.",
        "Survey summaries cannot be attached to teams; no inferred team filter."),
    "m2-paired-sensitivity": (
        "Role transformation: paired sensitivity", "Cohort / role / observed T1-T3 pairs",
        "Observed paired respondents for each cohort and role.",
        "T3 minus T1 changes among respondents observed at both checkpoints.",
        "Sensitivity evidence, not a longitudinal census. No respondent or team keys are public."),
    "m3-participation": (
        "Repository activity around T3", "Team-semester",
        "Pre/post/final-window commits / all observed history before T3+7 days.",
        "T3 +/- 7 days (14 days): pre [T3-7d,T3), post [T3,T3+7d); final window is their union.",
        "This is not the separate final-seven concentration measure. Counts do not measure coordination quality."),
    "m3-author-concentration": (
        "Author concentration around T3", "Team-semester / pre or post phase",
        "Maximum local-author commits / phase commits; Gini uses observed local-author activity.",
        "Author activity in the seven-day pre-T3 and seven-day post-T3 windows.",
        "No activity gives zero counts but null concentration, not perfect equality or zero concentration."),
    "m3-rolling": (
        "Seven-day rolling activity", "Team-semester / relative window-end day",
        "Concentration uses commits within [offset-7,offset), relative to T3.",
        "29 overlapping seven-day windows per team-semester.",
        "Windows overlap and are not independent project observations."),
    "m3-rolling-pooled": (
        "Pooled seven-day activity", "Relative window-end day / fixed pooled population",
        "Active team-semesters / all team-semesters; concentration medians exclude unavailable values.",
        "Fixed pooled rolling summaries across cohorts, not a selected-team estimate.",
        "No cohort/team filter or recomputation of the pooled medians."),
    "m4-checkpoint-churn": (
        "Clean changed lines by checkpoint", "Team-semester / checkpoint",
        "Clean changed lines / all changed lines; commit summaries use clean-touching commits.",
        "Clean source/test path activity, separate from all-path churn and file/commit counts.",
        "Clean-path provenance is not semantic defect validation; no clean change is not a missing team."),
    "m4-checkpoint-pooled": (
        "Pooled clean changed lines", "Checkpoint / fixed pooled population",
        "Total clean changed lines / total all-path changed lines.",
        "Original pooled sums and medians; observed-clean coverage is 7, 10, and 14 at T1, T2, and T3.",
        "No cohort/team filtering or new medians of a selected subset."),
    "m4-path-composition": (
        "Pooled path-category composition", "Checkpoint / file category",
        "Category changed lines / all category changed lines, including excluded paths.",
        "Separate clean-path inclusion flags, file events, distinct files, and changed lines.",
        "Pooled event and distinct-file counts are different units; do not reconstruct identities."),
    "m5-marker-density": (
        "Transcript lexical density", "Checkpoint / one global 2025.2 corpus",
        "Friction-marker matches / tokens * 1000.",
        "Lexical counts and density in the measured global transcript corpus.",
        "Candidate textual markers, not diagnoses. No team attribution or 2026.1 observations."),
    "m5-marker-composition": (
        "Transcript lexical composition", "Checkpoint / lexical subtype / one global corpus",
        "Subtype matches / all friction-marker matches at that checkpoint.",
        "Five lexical subtypes; composition is distinct from density per token.",
        "Chunks and sessions are not independent team observations; no team filter."),
    "m5-corpus-coverage": (
        "Transcript corpus coverage", "Checkpoint / one global 2025.2 corpus",
        "Coverage counts, not a response-rate denominator.",
        "35, 37, and 28 chunks at T1, T2, and T3, with session, token, and character counts.",
        "Only one measured cohort; never synthesize missing-cohort rows."),
    "m5-lexicon": (
        "Lexical marker definitions", "Lexicon version / subtype",
        "Not applicable: definition rows.", "Five regex definitions for Portuguese lexical matching.",
        "Patterns are displayed as text, never executed on user input; no quoted transcript evidence."),
    "m6a-structural-planning": (
        "Structural planning evidence", "Team-semester / T1",
        "Not applicable: observed artifact counts, presence, and line scope.",
        "Repository artifact presence and log(1+changed-line scope) at T1; artifact activity is an event count.",
        "Presence and scope are not planning quality. No repository artifact does not prove no off-repository planning."),
    "m6b-planning-content": (
        "Structured planning-content evidence", "Team-semester / T1",
        "Evidence-item array lengths only for the nine successful extractions.",
        "Reviewed exploratory planning presence and separate evidence-item counts; no source text.",
        "Five unmeasured cases are null, not zero. Successful empty lists are zero; no composite planning score."),
    "m7-checkpoint-inactivity": (
        "Checkpoint repository inactivity", "Team-semester / checkpoint",
        "Commit count in seven days before that checkpoint's evaluator anchor.",
        "Checkpoint-specific seven-day inactivity flags and observed commit counts.",
        "Inactivity does not identify planning omission or off-repository work; not an M9 planning predictor."),
    "m8-rework-magnitude": (
        "Clean rework magnitude and eligibility", "Team-semester / T3",
        "Rework changed lines / total clean T3 changed lines, only with observed baseline and positive total.",
        "Path-provenance rework/deferred magnitudes with baseline eligibility and explicit ratio status.",
        "Not verified defects. Ineligible and zero-denominator ratios are null, even if a source cell was numeric."),
    "m8-baseline-eligibility": (
        "Rework baseline eligibility", "Team-semester / T3",
        "Eligibility is prior clean-path count > 0; 12 of 14 cases are baseline eligible.",
        "Prior clean paths and observed baseline status for interpreting rework ratios.",
        "Baseline not observed is not proof that no prior work existed."),
    "m9-structural-rework-magnitude": (
        "Structural planning / rework magnitude associations", "Fixed analysis / predictor / outcome",
        "Pairwise measured team-semesters; original sample_n (14 in this snapshot).",
        "Spearman associations in the all-team-semesters stratum.",
        "Exploratory, non-causal, no subset recomputation or confirmatory p-value claims."),
    "m9-structural-rework-ratio": (
        "Structural planning / eligible rework ratio associations", "Fixed analysis / predictor / outcome",
        "Baseline-eligible cases with a defined ratio; original sample_n (12 in this snapshot).",
        "Spearman associations in the baseline-eligible-only stratum.",
        "Eligibility restrictions survive filtering; exploratory and non-causal."),
    "m9-structural-outcomes": (
        "Structural planning / evaluator outcomes", "Fixed analysis / predictor / outcome",
        "Observed pairwise T3 dimension scores; original sample_n.",
        "Separate evaluator dimensions and structural planning predictors.",
        "Do not treat separate dimensions as an official global quality score or recalculate correlations."),
    "m9-content-outcomes": (
        "Planning-content / evaluator outcomes", "Fixed analysis / predictor / outcome",
        "Successful measured content cases with observed outcome, at most nine; original sample_n.",
        "Separate exploratory associations for structured planning-content predictors.",
        "Unmeasured content is excluded, not zero. No combined content-quality score."),
    "m9-leave-one-out": (
        "Leave-one-out association sensitivity", "Analysis / predictor / outcome / omitted team-semester",
        "remaining_sample_n after omission under the original eligibility rule.",
        "Existing omission estimates for the registered associations.",
        "These ranges are not confidence intervals. Constant or insufficient pairs give null estimates."),
    "m6a-presence-by-cohort": (
        "Artifact presence by cohort", "Cohort / evidence state",
        "team_semester_count within state; team_semester_n is the whole cohort denominator.",
        "Two observed artifact-presence states per cohort.",
        "No new presence percentage or semantic quality score is required."),
    "planning-rework-profile": (
        "Planning scope and rework profile", "Team-semester",
        "Not applicable: planning scope and clean T3 rework magnitude, not a ratio.",
        "T1 structural planning fields alongside T3 path-provenance rework and baseline eligibility.",
        "Planning measurement_status refers to structural evidence, not rework eligibility; log axes cannot show zero."),
    "complexity-rework-figure": (
        "Evaluated complexity and rework", "Team-semester",
        "Rework ratio uses eligible positive-total cases only; magnitude remains available for all cases.",
        "T3 evaluator-rated complexity and clean rework magnitude with fixed planning tiers.",
        "Descriptive co-variation, not causal adjustment. Evaluated and repository structural complexity differ."),
    "phase-activity": (
        "Non-overlapping phase activity", "Team-semester / phase",
        "Phase commits or clean changed lines / corresponding observed team total * 100.",
        "Four mutually exclusive phases; the final phase is seven days before T3, not after T3.",
        "Pre-T1 duration varies; phase order is not a duration. Do not pool overlapping M3 windows into phases."),
    "phase-activity-summary": (
        "Fixed phase summaries by trajectory", "Trajectory group / phase",
        "Original team_semester_n in each fixed trajectory group.",
        "Original means and medians for four non-overlapping phases across three trajectory groups.",
        "No cohort/team filtering, trajectory reclassification, or filter-time estimates."),
    "score-final7-commits": (
        "Score change and final-seven commit concentration", "Team-semester",
        "Commits in [T3-7d,T3) / all observed project commits before T3 * 100.",
        "Final-seven concentration strictly before T3, with score changes and fixed median quadrants.",
        "Excludes post-T3 activity. Positive delta uses >0.125, not >0; frozen cuts are not recalculated."),
    "score-final7-clean-churn": (
        "Score change and final-seven clean-churn concentration", "Team-semester",
        "Clean changed lines in [T3-7d,T3) / all observed clean changed lines before T3 * 100.",
        "Clean-churn concentration strictly before T3, separate from commit concentration.",
        "Excludes post-T3 activity. Original clean-churn median and delta threshold remain fixed."),
    "score-final7-quadrants": (
        "Fixed score/concentration quadrant summaries", "Activity metric / quadrant / planning tier",
        "Original within-cell team_semester_n, with fixed full-sample median cut.",
        "Existing counts and medians under the registered score-change rule.",
        "No team list is published; small cells do not justify causal or confirmatory claims."),
    "planning-final7-commits": (
        "Planning scope and final-seven commits", "Team-semester",
        "Final-seven commits / all observed project commits strictly before T3 * 100.",
        "T1 scope versus final-seven concentration before T3; fixed quadrants, T3 score color, absolute score-change size.",
        "Frozen median quadrants are descriptive. Marker size is a rendering value, not an extra scientific measure."),
    "planning-final7-clean-churn": (
        "Planning scope and final-seven clean churn", "Team-semester",
        "Final-seven clean changed lines / all observed clean changed lines before T3 * 100.",
        "Clean-churn variant of the planning/concentration comparison, excluding post-T3 activity.",
        "Use the clean-churn median, not the commit median; no recomputation after filters."),
    "planning-final7-quadrants": (
        "Fixed planning/concentration quadrant summaries", "Activity metric / quadrant",
        "Cell team_semester_n and full-population team_semester_denominator are separate.",
        "Original T3 score, score-change, and rework summaries with small-N flags.",
        "No inferred project membership or recalculated cell estimates."),
    "operational-regularity": (
        "Descriptive operational regularity", "Team-semester",
        "Active days / project span; M7 inactive windows / 71 overlapping windows.",
        "Daily activity from first commit through T3 anchor inclusive; mean of eight fixed normalized components.",
        "Not a validated Agile score. Author metrics use the pre-T3 seven days, not the full timeline; normalization stays fixed."),
    "transcript-context-2025": (
        "Transcript and repository context: 2025.2", "Checkpoint / one global corpus and cohort-level context",
        "Lexical matches / tokens * 1000; team_n for repository/score context; eligible cases for T3 ratio context.",
        "Global transcript density beside descriptive repository/evaluator summaries; fixed T3 rework context repeats on every row.",
        "Do not plot repeated T3 context as checkpoint-varying or treat one M5 corpus as nine team observations."),
    "complexity-profile": (
        "Evaluated and repository structural complexity", "Team-semester",
        "Frontend/backend shares use all classified and unclassified clean file events; eligible ratio uses M8 policy.",
        "Separate evaluator scores, path-based counts, file-event shares, planning, and rework context.",
        "Path heuristics are not manual architecture or GenAI classifications; magnitudes and file counts differ."),
    "complexity-stratified-associations": (
        "Complexity-stratified association sensitivity", "Fixed relationship",
        "Separate N for full, low-complexity, and high-complexity estimates; minimum N is four.",
        "Existing full-sample Spearman rho and fixed median-split strata at 1.875 evaluator score points.",
        "Low <= median, high > median. Small-N descriptive sensitivity, not causal confounding control."),
    "influence-cases": (
        "Omitted-case influence", "Relationship / omitted team-semester",
        "Original eligible full_sample_n and loo_n; omitting an ineligible case need not reduce N.",
        "13 relationships by 14 omissions; rho_delta_from_full is the omission estimate minus full-sample rho.",
        "Not a confidence interval; preserve availability status and original eligibility."),
    "influence-relations": (
        "Influence relationship definitions and ranges", "Fixed relationship",
        "Sign-preservation share divides by available omissions, not assumed total omissions.",
        "Original relationship estimates, omission counts, ranges, and availability.",
        "Minimum eligible pair N is four. Leave-one-out ranges are not confidence intervals."),
    "influence-summary": (
        "Directional robustness summary", "Fixed relationship",
        "available_leave_one_out_rows versus total_leave_one_out_rows; sign share uses available rows.",
        "Original ranges, sign preservation, unstable-sensitivity flag, and approved influential-case label.",
        "Descriptive diagnostic, not causal robustness or inferential uncertainty."),
}

SOURCES = {
    "surveys": "Survey summaries",
    "repository": "Repository activity and artifact summaries",
    "transcript-aggregates": "Transcript lexical aggregates",
    "reviewed-planning": "Reviewed structured planning evidence",
    "paper-diagnostics": "Paper-derived descriptive diagnostics",
}
TEXT_LABELS = {
    "cohort": "Cohort", "team_id": "Team within cohort", "checkpoint": "Checkpoint",
    "omitted_team_id": "Omitted team within cohort", "omitted_cohort": "Omitted cohort",
    "std": "Standard deviation", "q1": "First quartile", "q3": "Third quartile", "iqr": "Interquartile range",
    "spearman_rho": "Spearman rho", "spearman_p_exploratory": "Exploratory Spearman p-value",
    "pi_available": "Structural artifact available", "pi_file_count_t1": "T1 artifact file count",
    "pi_line_delta_t1": "T1 artifact changed-line scope", "mean_t1": "T1 mean", "mean_t3": "T3 mean",
}
COUNT_UNITS = {
    "responses": "response_n cohort_response_n respondent_n",
    "paired respondents": "pair_n",
    "topic assignments": "topic_assignment_n",
    "commits": "total_commit_n pre_commit_n post_commit_n final_window_commit_n commit_n commit_n_7d "
               "max_commit_n mean_commit_n median_commit_n clean_touching_commit_n clean_touching_commit_n_inferred "
               "m4_clean_touching_commit_n_t3 team_total_commit_n",
    "days": "active_days active_day_count active_day_n median_active_days mean_active_day_n",
    "authors": "author_n author_count active_author_n mean_active_author_n",
    "team-semesters": "team_semester_n active_team_semester_n observed_clean_team_semester_n team_semester_count "
                      "team_semester_denominator team_n baseline_eligible_rework_team_n full_sample_n loo_n "
                      "n_without_complexity_stratification n_within_low_complexity n_within_high_complexity",
    "eligible pairs": "sample_n remaining_sample_n minimum_n_for_rho",
    "clean files": "clean_unique_file_n median_clean_unique_file_n clean_distinct_file_n "
                   "m4_clean_unique_file_n_t3 prior_clean_path_n",
    "files": "unique_file_n pi_file_count_t1",
    "file events": "file_event_n frontend_clean_file_event_n backend_clean_file_event_n mixed_clean_file_event_n "
                   "unclassified_clean_file_event_n pi_renamed_count_t1 pi_deleted_count_t1 pi_binary_event_count_t1",
    "artifact events": "planning_artifact_activity_t1",
    "clean directories": "clean_distinct_directory_n",
    "path segments": "clean_max_path_depth",
    "file extensions": "clean_extension_n",
    "clean files per commit": "mean_clean_files_per_commit",
    "lexical matches": "friction_marker_n m5_friction_marker_n marker_n alignment handoff integration blocker rework",
    "transcript chunks": "transcript_chunk_n",
    "source sessions": "source_session_n",
    "tokens": "token_n m5_token_n",
    "characters": "character_n",
    "observed cohorts": "observed_semester_n",
    "overlapping windows": "m7_window_count",
    "omission rows": "leave_one_out_rows available_leave_one_out_rows total_leave_one_out_rows",
    "evidence items": "goals_n architecture_or_design_n task_decomposition_n risk_or_dependency_n evidence_quotes_n",
}
UNIT_BY_FIELD = {field: unit for unit, fields in COUNT_UNITS.items() for field in fields.split()}

# Display labels are translations/expansions only; exported category values stay unchanged.
VALUE_LABELS = {
    "perception_family": {
        "ai_benefit": "AI benefit", "ai_career_impact_5y": "Five-year career impact",
        "autonomy_tool_dependency": "Autonomy/tool balance", "career_expectation": "Career expectation",
        "project_challenges": "Project challenges", "project_feeling": "Project feeling",
    },
    "category": {
        "Nunca": "Never", "Raramente": "Rarely", "Algumas vezes por m\u00eas": "A few times a month",
        "Semanalmente": "Weekly", "Diariamente": "Daily", "N\u00e3o": "No", "Sim": "Yes",
        "An\u00e1lise de requisitos": "Requirements analysis", "Brainstorming de ideias": "Idea brainstorming",
        "Depura\u00e7\u00e3o / debug": "Debugging", "Documenta\u00e7\u00e3o": "Documentation",
        "Escrita de testes": "Test writing", "Gera\u00e7\u00e3o de c\u00f3digo": "Code generation",
        "Organiza\u00e7\u00e3o de trabalhos acad\u00eamicos.": "Organizing academic work",
        "Pesquisa / Perguntas gerais / Uso anon_ccabe18c441c": "Research / general questions (reviewed category)",
        "Prototipa\u00e7\u00e3o": "Prototyping", "Refatora\u00e7\u00e3o": "Refactoring",
        "Tirar algum tipo de d\u00favida": "Clarifying a question", "entender alguma coisa": "Understanding something",
        "ter ideias": "Getting ideas",
    },
    "measure": {
        "general_frequency": "General AI-use frequency", "software_frequency": "Software-related AI-use frequency",
        "real_ai_use_tasks": "Reported AI-assisted tasks", "autonomy_tool_balance": "Autonomy/tool balance",
        "real_ai_use_tools": "Reported AI tools", "prior_ai_project_experience": "Prior AI-assisted project experience",
    },
    "topic": {
        "other_or_insufficient_evidence": "Other or insufficient evidence", "productivity_and_speed": "Productivity and speed",
        "replacement_or_job_risk": "Replacement or job risk", "skills_and_learning": "Skills and learning",
        "task_or_role_change": "Task or role change", "uncertainty_or_condition": "Uncertainty or conditions",
    },
    "phase": {
        "pre": "Seven days before T3", "post": "Seven days after T3",
        "pre_t1": "Before T1", "t1_to_t2": "T1 to T2",
        "t2_to_t3_excluding_final7": "T2 to T3, excluding final seven days", "final7_pre_t3": "Final seven days before T3",
    },
    "score_trajectory_group": {"improved": "Improved", "stable": "Stable", "declined": "Declined"},
    "ratio_status": {"available": "Ratio available", "baseline_not_observed": "Baseline not observed",
                     "zero_clean_churn": "Zero clean T3 churn"},
    "planning_scope_tier": {"high_repository_visible_planning": "High repository-visible planning",
                            "lower_repository_visible_planning": "Lower repository-visible planning"},
    "friction_subtype": {"alignment": "Alignment", "handoff": "Handoff", "integration": "Integration",
                         "blocker": "Blocker", "rework": "Rework"},
    "role": {"QA": "Quality assurance", "Backend": "Backend", "Frontend": "Frontend",
             "Project Manager": "Project manager", "Product Manager": "Product manager", "Scrum Master": "Scrum master"},
}


def label(field: str) -> str:
    if field in TEXT_LABELS:
        return TEXT_LABELS[field]
    words = {"n": "count", "pi": "artifact", "t1": "T1", "t2": "T2", "t3": "T3",
             "loo": "leave-one-out", "pct": "(%)", "cv": "CV", "m4": "M4", "m5": "M5", "m7": "M7",
             "id": "identifier", "log1p": "log(1 + scope)", "rho": "rho"}
    value = " ".join(words.get(part, part) for part in field.split("_"))
    return value[0].upper() + value[1:]


def public_schema() -> dict[str, tuple[list[str], list[str]]]:
    result = {}
    for spec in TABLES:
        if not spec.definition:
            columns = [target for _, target in spec.fields]
            if "clean_rework_ratio_t3" in columns:
                if "baseline_eligible_for_rework_t3" not in columns:
                    columns.append("baseline_eligible_for_rework_t3")
                columns.append("ratio_status")
            result[spec.dataset_id] = ([RENAMES.get(k, k) for k in spec.keys], columns)
    result["m5-lexicon"] = (["lexicon_version", "subtype"],
                            ["lexicon_version", "subtype", "pattern", "language", "counting_rule"])
    result["m6b-planning-content"] = (
        ["cohort", "team_id"], ["cohort", "team_id", "measurement_status", "planning_evidence_present",
                              "goals_n", "architecture_or_design_n", "task_decomposition_n",
                              "risk_or_dependency_n", "evidence_quotes_n"])
    return result


def column(field: str, dataset_id: str, key: list[str]) -> dict[str, object]:
    text_fields = TEXT_FIELDS | {"lexicon_version", "subtype", "pattern", "language", "counting_rule", "ratio_status"}
    boolean_fields = BOOLEAN_FIELDS | {"planning_evidence_present"}
    integer_fields = INTEGER_FIELDS | {"goals_n", "architecture_or_design_n", "task_decomposition_n",
                                      "risk_or_dependency_n", "evidence_quotes_n"}
    if field in boolean_fields:
        kind, unit = "boolean", "boolean"
    elif field in text_fields and not (dataset_id == "m1-autonomy" and field == "category"):
        kind, unit = "string", "label"
    elif field in integer_fields or (dataset_id == "m1-autonomy" and field == "category"):
        kind, unit = "integer", "count"
    else:
        kind, unit = "number", "dimensionless"
    unit = UNIT_BY_FIELD.get(field, unit)
    if field == "count":
        unit = "responses" if dataset_id != "m1-career-topics" else "topic assignments"
    if field in ("window_end_day", "start_day_relative_to_t3", "end_day_relative_to_t3"):
        unit = "days relative to T3"
    elif "gap_days" in field or field == "project_span_days":
        unit = "days"
    elif field.endswith("_pct") or field == "final7_share_pct":
        unit = "percentage points (0-100)"
    elif "log1p" in field:
        unit = "natural log(1 + changed lines)"
    elif field == "marker_size":
        unit = "rendering size"
    elif field in ("phase_order", "week_bin_order"):
        unit = "ordinal"
    elif field == "score" or (dataset_id == "m1-autonomy" and field == "category"):
        unit = "Likert points (1-5)"
    elif field in ("mean", "std", "median", "q1", "q3", "iqr", "mean_t1", "mean_t3", "mean_change", "median_change"):
        unit = "coded score points (0-4)" if dataset_id == "m1-perceptions" else "Likert points (1-5)"
    elif ("score" in field and kind != "string") or "technical_complexity" in field and kind != "string" \
            or field in ("complexity_median", "delta_threshold"):
        unit = "evaluator score points"
    elif ("churn" in field and "share" not in field and "cv" not in field and "entropy" not in field
          and "component" not in field and "ratio" not in field) or field == "pi_line_delta_t1":
        unit = "changed lines"
    elif field.endswith("_share") or field in ("share", "coverage", "share_of_topic_assignments",
                                               "clean_rework_ratio_t3", "clean_share_of_all_churn", "churn_share",
                                               "median_clean_rework_ratio_t3_baseline_eligible"):
        unit = "fraction (0-1)"
    elif field in ("author_gini", "median_author_gini"):
        unit = "Gini (0-1)"
    elif "rho" in field:
        unit = "rho difference (-2 to 2)" if "delta" in field else "Spearman rho (-1 to 1)"
    elif field == "spearman_p_exploratory":
        unit = "exploratory p-value (0-1)"
    elif field.endswith("_per_1k_tokens"):
        unit = "lexical matches per 1000 tokens"
    elif field.endswith("_component") or field == "regularity_index":
        unit = "normalized component/index (0-1)"
    elif field.startswith("temporal_entropy_"):
        unit = "normalized Shannon entropy (0-1)"
    elif field.endswith("_cv"):
        unit = "coefficient of variation (nonnegative)"
    nullable = field in NULLABLE_FIELDS or (dataset_id == "m6b-planning-content"
                                          and field not in ("cohort", "team_id", "measurement_status"))
    definitions = {
        "cohort": "Approved cohort label, stored as a string, not a decimal year.",
        "team_id": "Approved team label scoped by cohort; never a global team identifier.",
        "checkpoint": "Paper checkpoint T1, T2, or T3; anchors follow this dataset's temporal definition.",
        "std": "Observed score standard deviation in the dataset's scale, not a confidence interval.",
        "coverage": "Observed family responses divided by observed cohort-checkpoint responses.",
        "response_n": "Observed responses for this measure/role/family and cell, not total enrollment.",
        "cohort_response_n": "All observed responses in the same cohort-checkpoint cell.",
        "respondent_n": "Observed respondents answering the row's measure; multi-select shares may overlap.",
        "topic_assignment_n": "Total topic assignments in the cell, not distinct respondents.",
        "pair_n": "Observed paired T1-T3 respondents for this cohort and role.",
        "planning_artifact_activity_t1": "Integer number of structural artifact events at T1, not a boolean.",
        "planning_scope_log1p_t1": "Natural logarithm of one plus T1 artifact changed-line scope.",
        "planning_artifact_present_t1": "Repository structural artifact presence at T1, not planning quality.",
        "planning_evidence_present": "Reviewed extraction's boolean planning-presence field; null when unmeasured.",
        "evidence_quotes_n": "Number of evidence items, without any quotation text; no publication permission for the text.",
        "clean_rework_ratio_t3": "Clean T3 rework lines divided by total clean T3 lines; null unless baseline eligible and total positive.",
        "baseline_eligible_for_rework_t3": "True exactly when prior observed clean-path count is greater than zero.",
        "ratio_status": "available, baseline_not_observed, or zero_clean_churn; baseline absence takes precedence.",
        "measurement_status": "Measurement-specific availability/state, distinct from a load error or an empty filter result.",
        "sample_n": "Original pairwise sample size for this fixed association; never recomputed on filtered rows.",
        "remaining_sample_n": "Original eligible pair count after the named omitted case.",
        "rho_delta_from_full": "Leave-one-out rho minus full-sample rho, not a confidence interval.",
        "sign_preservation_share": "Available omissions preserving the full-sample sign / available omissions.",
        "regularity_index": "Mean of eight fixed normalized activity-distribution components; not a validated Agile score.",
        "active_day_share": "Days with a commit / observed project-span days.",
        "project_span_days": "First observed commit day through T3 anchor day inclusive.",
        "max_inactivity_gap_days": "Longest zero-commit run within the observed daily series.",
        "median_inactivity_gap_days": "Median zero-commit run length within the observed daily series.",
        "commit_weekly_cv": "Population coefficient of variation of weekly commits, including zero weeks in the observed period.",
        "clean_churn_weekly_cv": "Population coefficient of variation of weekly clean changed lines, including observed-period zero weeks.",
        "temporal_entropy_commits": "Daily commit Shannon entropy normalized by log(project_span_days).",
        "temporal_entropy_clean_churn": "Daily clean-churn Shannon entropy normalized by log(project_span_days).",
        "m7_inactive_window_share": "Inactive M7 windows / original overlapping window count.",
        "marker_size": "Saved plotting size used for fidelity; absolute score change is available separately.",
        "technical_complexity_mean_t3": "Mean evaluator technical-complexity score at T3, distinct from path-based structure.",
        "clean_max_path_depth": "Maximum count of normalized path segments among clean-path file events.",
        "clean_touching_commit_n_inferred": "Distinct observed commits touching at least one clean path.",
        "mean_clean_files_per_commit": "Mean distinct clean files per clean-touching commit.",
        "frontend_clean_file_event_share": "Frontend-matching clean file events / all classified and unclassified clean file events.",
        "backend_clean_file_event_share": "Backend-matching clean file events / all classified and unclassified clean file events.",
        "pattern": "Approved regex definition displayed as text; not executed on user input.",
        "planning_scope_tier": "Fixed T1 artifact-presence/log-scope tier; no quality ranking or filter-time median.",
        "score_trajectory_group": "Existing improved/stable/declined grouping under the registered adaptive signed 0.125 threshold.",
        "delta_direction": "Existing classification using a positive change threshold strictly greater than 0.125.",
        "clean_distinct_file_n": "Distinct clean-path files touched in observed file events.",
        "clean_distinct_directory_n": "Distinct normalized parent directories among clean-path file events.",
        "clean_extension_n": "Distinct clean-path file extensions; missing extensions use the paper's '(none)' category.",
        "clean_total_churn_inferred": "Observed clean-path additions plus deletions, not distinct files or defects.",
        "evaluator_score_t1": "Unweighted mean of the four evaluator dimension means at T1; descriptive, not official quality.",
        "evaluator_score_t3": "Unweighted mean of the four evaluator dimension means at T3; descriptive, not official quality.",
        "delta_score_t3_minus_t1": "Descriptive evaluator composite at T3 minus T1 in original score points.",
        "abs_delta_score_t3_minus_t1": "Absolute T3-minus-T1 composite change used for saved marker-size encoding.",
        "mean_change": "Mean observed within-person T3-minus-T1 Likert change among observed pairs.",
        "median_change": "Median observed within-person T3-minus-T1 Likert change among observed pairs.",
        "clean_rework_churn_t3": "Clean T3 changed lines on paths observed in the prior baseline; path provenance, not verified defects.",
        "clean_deferred_churn_t3": "Clean T3 changed lines on paths not observed in the prior baseline.",
        "prior_clean_path_n": "Distinct prior observed clean paths used to establish the rework baseline.",
        "clean_total_churn_t3": "All clean changed lines at T3, the ratio denominator.",
        "pi_file_count_t1": "Observed T1 structural planning artifact files.",
        "pi_line_delta_t1": "Observed T1 structural artifact additions plus deletions, in changed lines.",
        "pi_available": "Structural planning evidence measurement availability, distinct from artifact presence.",
        "clean_share_of_all_churn": "Clean changed lines divided by all-path changed lines in the same row scope.",
        "share": "Category count divided by observed respondent count in the same measure/cell; multi-select categories can overlap.",
        "share_of_topic_assignments": "Category topic assignments / all topic assignments, not respondent prevalence.",
        "churn_share": "Category changed lines / all category changed lines, including clean-policy exclusions.",
        "friction_marker_density_per_1k_tokens": "All friction-marker matches / corpus tokens * 1000.",
        "marker_share": "Lexical subtype matches / all friction-marker matches at this checkpoint.",
        "final_window_share": "Commits in the 14-day union around T3 / observed history before T3+7 days.",
        "final7_share_pct": "Final-seven metric activity / full observed project activity strictly before T3 * 100; metric is explicitly labeled.",
        "final7_commit_share_pct": "Final-seven commits / all observed project commits strictly before T3 * 100.",
        "final7_clean_churn_share_pct": "Final-seven clean changed lines / all observed project clean changed lines strictly before T3 * 100.",
        "most_influential_case": "Approved cohort/team label for the strongest observed omission effect; not an original repository identity.",
        "sign_changed": "Whether the available omission estimate's sign differs from the original full-sample sign.",
        "availability_status": "Original association/omission availability; unavailable estimates remain null.",
        "unstable_sensitivity_flag": "Original diagnostic sensitivity flag; not a confirmatory statistical test.",
        "minimum_n_for_rho": "Minimum eligible pair count of four for the registered diagnostic rho calculation.",
    }
    if field.startswith("technical_complexity_mean_t"):
        definitions[field] = f"Mean evaluator technical-complexity score at {field[-2:].upper()}, not repository structural inference."
    if field == "delta_technical_complexity_t3_minus_t1":
        definitions[field] = "Evaluator technical-complexity mean at T3 minus T1, in original score points."
    if field.startswith("regularity_") and field.endswith("_component"):
        definitions[field] = f"Original fixed normalized {label(field)}; see the eight-component regularity definition. Never renormalize filtered rows."
    definition = definitions.get(field, f"{label(field)} in the stated row grain; use this dataset's denominator and temporal scope.")
    descriptor: dict[str, object] = {
        "id": field, "label": label(field), "type": kind, "unit": unit, "nullable": nullable,
        "definition": definition, "role": "key" if field in key else "measure" if kind in ("integer", "number") else "context",
    }
    if dataset_id == "transcript-context-2025" and field in (
            "median_clean_rework_churn_t3", "median_clean_rework_ratio_t3_baseline_eligible"):
        descriptor["time_scope"] = "fixed_T3"
        descriptor["definition"] = "Fixed T3 rework context repeated on every checkpoint row, not checkpoint-varying evidence."
    if dataset_id == "operational-regularity" and field in ("author_count", "max_author_share", "author_gini"):
        descriptor["time_scope"] = "pre_T3_seven_days"
    if field in VALUE_LABELS:
        descriptor["value_labels"] = VALUE_LABELS[field]
    if field in ("cohort", "checkpoint", "omitted_cohort"):
        descriptor["value_order"] = ["T1", "T2", "T3"] if field == "checkpoint" else ["2025.2", "2026.1"]
    if dataset_id == "m1-frequency" and field == "category":
        descriptor["value_order"] = ["Nunca", "Raramente", "Algumas vezes por m\u00eas", "Semanalmente", "Diariamente"]
    return descriptor


def filters(dataset_id: str, key: list[str], columns: list[str]) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for field in key:
        if field in ("team_id", "omitted_team_id"):
            cohort = "cohort" if field == "team_id" else "omitted_cohort"
            result.append({"id": "team_semester" if field == "team_id" else "omitted_case",
                           "label": "Team-semester" if field == "team_id" else "Omitted team-semester",
                           "fields": [cohort, field], "mode": "multi_select"})
        else:
            result.append({"id": field, "label": label(field), "fields": [field], "mode": "multi_select"})
    additions = {
        "m4-path-composition": ["included_in_m4"],
        "m8-rework-magnitude": ["baseline_eligible_for_rework_t3", "ratio_status"],
        "m8-baseline-eligibility": ["baseline_eligible_for_rework_t3"],
        "complexity-rework-figure": ["planning_scope_tier", "baseline_eligible_for_rework_t3", "ratio_status"],
        "phase-activity": ["score_trajectory_group", "planning_scope_tier"],
        "score-final7-commits": ["score_trajectory_group", "final7_concentration_tier", "quadrant", "planning_scope_tier"],
        "score-final7-clean-churn": ["score_trajectory_group", "final7_concentration_tier", "quadrant", "planning_scope_tier"],
        "planning-final7-commits": ["planning_scope_tier", "planning_concentration_quadrant"],
        "planning-final7-clean-churn": ["planning_scope_tier", "planning_concentration_quadrant"],
        "operational-regularity": ["score_trajectory_group", "planning_scope_tier"],
        "complexity-profile": ["planning_scope_tier", "score_trajectory_group", "baseline_eligible_for_rework_t3", "ratio_status"],
        "influence-cases": ["availability_status"],
        "influence-summary": ["unstable_sensitivity_flag"],
    }
    for field in additions.get(dataset_id, []):
        require(field in columns, "Filter references an unapproved field")
        result.append({"id": field, "label": label(field), "fields": [field], "mode": "multi_select"})
    return result


def source_and_rq(dataset_id: str) -> tuple[str, str, list[str]]:
    if dataset_id.startswith(("m1-", "m2-")):
        return "surveys", "RQ1", [dataset_id[:2].upper()]
    if dataset_id.startswith("m5-"):
        return "transcript-aggregates", "RQ2", ["M5"]
    if dataset_id == "m6b-planning-content":
        return "reviewed-planning", "RQ3", ["M6"]
    if dataset_id.startswith(("m3-", "m4-")):
        return "repository", "RQ2", [dataset_id[:2].upper()]
    if dataset_id.startswith(("m6a-", "m7-", "m8-")):
        return "repository", "RQ3", ["M6" if dataset_id.startswith("m6a") else dataset_id[:2].upper()]
    if dataset_id.startswith("m9-"):
        return "paper-diagnostics", "RQ3", ["M9"]
    metrics = {
        "planning-rework-profile": ["M6", "M8"], "complexity-rework-figure": ["M6", "M8"],
        "phase-activity": ["M3", "M4"], "phase-activity-summary": ["M3", "M4"],
        "score-final7-commits": ["M3"], "score-final7-clean-churn": ["M4"],
        "score-final7-quadrants": ["M3", "M4"],
        "planning-final7-commits": ["M3", "M6"], "planning-final7-clean-churn": ["M4", "M6"],
        "planning-final7-quadrants": ["M3", "M4", "M6"],
        "operational-regularity": ["M3", "M4", "M7"],
        "transcript-context-2025": ["M4", "M5", "M8"],
        "complexity-profile": ["M6", "M8"], "complexity-stratified-associations": ["M9"],
        "influence-cases": ["M9"], "influence-relations": ["M9"], "influence-summary": ["M9"],
    }
    rq = "RQ2" if dataset_id.startswith(("phase-", "score-", "planning-final7", "operational-", "transcript-")) else "RQ3"
    require(dataset_id in metrics, "Unknown dataset navigation mapping")
    return "paper-diagnostics", rq, metrics[dataset_id]


def figures() -> list[dict[str, object]]:
    def panel(dataset: str, kind: str, fields: str, **options: object) -> dict[str, object]:
        return {"dataset": dataset, "kind": kind, "fields": fields.split(), **options}

    return [
        {"id": "rq1-perceptions", "paper_label": "fig:rq1-m1", "title": "Coded perceptions with standard deviations",
         "rq": "RQ1", "filter_effect": "select_observations",
         "panels": [panel("m1-perceptions", "error_bar", "checkpoint mean std perception_family cohort response_n",
                          x="checkpoint", y="mean", error_y="std", facet="cohort", color="perception_family",
                          y_range=[0, 5], score_range=[0, 4], uncertainty="standard_deviation_not_confidence_interval")],
         "notes": "Separate perception families; original scales and response counts. Table alternative required."},
        {"id": "rq2-pooled-activity", "paper_label": "fig:rq2-m3", "title": "Pooled seven-day activity",
         "rq": "RQ2", "filter_effect": "select_rows_only",
         "panels": [panel("m3-rolling-pooled", "line", "window_end_day total_commit_n team_semester_n",
                          x="window_end_day", y="total_commit_n")],
         "notes": "Overlapping windows and fixed pooled population; never a selected-cohort estimate."},
        {"id": "rq2-planning-final7", "paper_label": "fig:rq2-planning-commit",
         "title": "Planning scope and final-seven commit concentration", "rq": "RQ2",
         "filter_effect": "select_observations",
         "panels": [panel("planning-final7-commits", "scatter",
                          "cohort team_id planning_scope_log1p_t1 final7_share_pct evaluator_score_t3 marker_size abs_delta_score_t3_minus_t1 planning_scope_tier",
                          x="planning_scope_log1p_t1", y="final7_share_pct", color="evaluator_score_t3",
                          size="marker_size", size_meaning="absolute_score_change", frozen_median_guides=True)],
         "notes": "Median cuts remain fixed; clean-churn variant is supporting evidence, not another included figure."},
        {"id": "rq2-churn-and-lexical-density", "paper_label": "fig:rq2-m4-m5",
         "title": "Clean churn and global lexical density", "rq": "RQ2", "filter_effect": "select_rows_only",
         "panels": [panel("m4-checkpoint-pooled", "bar", "checkpoint total_clean_churn team_semester_n",
                          x="checkpoint", y="total_clean_churn"),
                    panel("m5-marker-density", "line", "checkpoint friction_marker_density_per_1k_tokens token_n",
                          x="checkpoint", y="friction_marker_density_per_1k_tokens")],
         "notes": "Independent panels with different grains and units. Never join global transcript values onto teams."},
        {"id": "rq3-artifact-presence", "paper_label": "fig:rq3-presence", "title": "Artifact presence by cohort",
         "rq": "RQ3", "filter_effect": "select_observations",
         "panels": [panel("m6a-presence-by-cohort", "stacked_bar", "cohort evidence_state team_semester_count team_semester_n",
                          x="cohort", y="team_semester_count", color="evidence_state")],
         "notes": "Counts of observed artifact states, not a planning-quality score."},
        {"id": "rq3-planning-rework", "paper_label": "fig:rq3-profile", "title": "Planning and rework profile",
         "rq": "RQ3", "filter_effect": "select_observations",
         "panels": [panel("planning-rework-profile", "scatter",
                          "cohort team_id planning_scope_log1p_t1 clean_rework_churn_t3 baseline_eligible_for_rework_t3",
                          x="planning_scope_log1p_t1", y="clean_rework_churn_t3", color="cohort", y_scale="log",
                          zero_policy="exclude_zero_from_log_plot_explain_and_retain_in_table")],
         "notes": "Stored zero remains zero. Do not substitute one for zero or treat magnitude as an eligible ratio."},
        {"id": "rq3-complexity-rework", "paper_label": "fig:rq3-complexity-rework",
         "title": "Evaluated complexity and rework", "rq": "RQ3", "filter_effect": "select_observations",
         "panels": [panel("complexity-rework-figure", "scatter",
                          "cohort team_id technical_complexity_mean_t3 clean_rework_churn_t3 planning_scope_tier",
                          x="technical_complexity_mean_t3", y="clean_rework_churn_t3",
                          color="planning_scope_tier", symbol="cohort", frozen_median_guides=True)],
         "notes": "Evaluator score points versus changed lines, not causal adjustment or repository structural complexity."},
    ]


def definition_sets() -> list[dict[str, object]]:
    complexity_fields = (
        "technical_complexity_mean_t1 technical_complexity_mean_t2 technical_complexity_mean_t3 "
        "delta_technical_complexity_t3_minus_t1 clean_distinct_file_n clean_distinct_directory_n "
        "clean_max_path_depth clean_extension_n frontend_clean_file_event_share backend_clean_file_event_share "
        "clean_touching_commit_n_inferred mean_clean_files_per_commit clean_total_churn_inferred"
    ).split()
    return [
        {"id": "weekly-bin-definitions", "role": "catalog_only", "key": ["week_bin"],
         "definition": "Relative intervals without team identifiers or absolute dates; start inclusive, end exclusive.",
         "rows": [
             {"week_bin": f"week_{index - 12}" if index < 12 else "final_7_days", "week_bin_order": index + 1,
              "start_day_relative_to_t3": -91 + index * 7, "end_day_relative_to_t3": -84 + index * 7,
              "interval_notation": "[period_start, period_end)",
              "assignment_policy": "nonoverlapping_fixed_interval_relative_to_team_t3", "rolling_window_used": False}
             for index in range(13)
         ]},
        {"id": "complexity-definitions", "role": "catalog_only", "key": ["metric"],
         "definition": "Evaluated and path-inferred constructs are separate; no manual GenAI architecture classification.",
         "rows": [
             {"metric": field,
              "construct_family": "evaluated_complexity" if "technical_complexity" in field else "repository_structural_complexity",
              "definition": column(field, "complexity-profile", [])["definition"],
              "heuristic_or_policy": "Evaluator means, not repository inference." if "technical_complexity" in field
              else "Fixed clean-path filtering and normalized paths; frontend/backend markers are heuristics, not manual classification.",
              "manual_genai_architecture_classification": False}
             for field in complexity_fields
         ]},
    ]


def build_catalog() -> dict[str, object]:
    schema = public_schema()
    require(schema.keys() == DESCRIPTIONS.keys(), "Every dataset needs an explicit description")
    datasets = []
    for dataset_id, (key, fields) in schema.items():
        title, grain, denominator, definition, limitation = DESCRIPTIONS[dataset_id]
        source, rq, metrics = source_and_rq(dataset_id)
        pooled = "team_id" not in key
        corpus = source == "transcript-aggregates" or dataset_id == "transcript-context-2025"
        missingness: dict[str, object] = {
            "null": "Unavailable or undefined, never numeric zero; see measurement/eligibility fields and dataset notes.",
            "absent_row": "Not synthesized as zero.",
            "load_error": "A failed or malformed file must display an error, not an empty-success dataset.",
            "empty_filter": "No matching public rows, distinct from a failed load.",
        }
        if "ratio_status" in fields:
            missingness["ratio_status"] = ["available", "baseline_not_observed", "zero_clean_churn"]
            missingness["precedence"] = "baseline_not_observed before zero_clean_churn"
        if dataset_id == "m6b-planning-content":
            missingness["measurement_status"] = {
                "success": "Observed: empty evidence arrays count as zero.",
                "unavailable_not_measured": "All six presence/count outputs null, not zero.",
            }
        if dataset_id in ("m3-author-concentration", "m3-rolling"):
            missingness["no_observed_activity"] = "Observed zero counts; max_author_share and author_gini are null."
        if dataset_id == "m4-checkpoint-churn":
            missingness["no_clean_change_observed"] = "Observed team; undefined ratios and commit summaries are null."
        coverage: dict[str, object] = {"scope": grain, "sample_sizes": "Original per-row denominator fields, not filtered row counts."}
        if corpus:
            coverage["cohorts"] = ["2025.2"]
            coverage["team_attribution"] = False
        if "team_id" in key:
            coverage["team_semesters"] = 14
            coverage["cohort_counts"] = {"2025.2": 9, "2026.1": 5}
        if dataset_id == "m6b-planning-content":
            coverage.update({"measured": 9, "unmeasured": 5})
        if dataset_id in ("m8-rework-magnitude", "m8-baseline-eligibility"):
            coverage.update({"baseline_eligible": 12, "baseline_not_observed": 2})
        if dataset_id == "m5-corpus-coverage":
            coverage["chunks_by_checkpoint"] = {"T1": 35, "T2": 37, "T3": 28}
        descriptor = {
            "id": dataset_id, "title": title, "rq": rq, "metrics": metrics, "source": source,
            "grain": grain, "key": key, "definition": definition, "denominator": denominator,
            "coverage": coverage, "limitations": [limitation, "Descriptive or exploratory; no causal inference or new browser-side estimates."],
            "filter_effect": "select_rows_only" if pooled else "select_observations",
            "estimation_population": "Original published population and N remain fixed when rows are selected.",
            "paths": {"json": f"data/datasets/{dataset_id}.json", "csv": f"data/downloads/{dataset_id}.csv"},
            "columns": [column(field, dataset_id, key) for field in fields],
            "filters": filters(dataset_id, key, fields), "missingness": missingness,
        }
        strata = {
            "m9-structural-rework-magnitude": "all_team_semesters",
            "m9-structural-rework-ratio": "baseline_eligible_only",
            "m9-structural-outcomes": "all_team_semesters",
            "m9-content-outcomes": "m6b_structured_content",
            "m9-leave-one-out": "original_analysis_eligibility_after_omission",
        }
        if dataset_id in strata:
            descriptor["stratum"] = strata[dataset_id]
        datasets.append(descriptor)
    catalog: dict[str, object] = {
        "schema_version": "1.0", "language": "en",
        "title": "Research Data Explorer", "path_base": "site_root",
        "status": "snapshot_prepared_release_pending",
        "excerpt_policy": "omitted_by_human_decision",
        "research_questions": [
            {"id": "RQ1", "title": "Self-report and coded perceptions", "metrics": ["M1", "M2"]},
            {"id": "RQ2", "title": "Repository activity and transcript evidence", "metrics": ["M3", "M4", "M5"]},
            {"id": "RQ3", "title": "Planning artifacts, inactivity, rework, and associations", "metrics": ["M6", "M7", "M8", "M9"]},
        ],
        "sources": [{"id": key, "label": value} for key, value in SOURCES.items()],
        "datasets": datasets,
        "dataset_aliases": {"m8-rework-participation": "m8-rework-magnitude"},
        "figures": figures(),
        "methods": {
            "precision": "Preserve exact public scalars in tables/downloads; round only display labels.",
            "text": "Render all values as text, not HTML. Regex definitions are not run on user input.",
            "composite": "Unweighted mean of project progress, scope/applicability, technical complexity, and engagement/participation evaluator dimensions; descriptive, not official quality.",
            "clean_paths": "The paper's fixed clean source/test path policy separates measurement code from excluded artifacts; changed lines are additions plus deletions, not defects.",
            "final_seven": "Numerator [T3-7d,T3); denominator all observed project activity strictly before T3. No post-T3 activity.",
            "planning_high_tier": {"artifact_required": True, "log_scope_minimum_inclusive": 1.791759469228055},
            "concentration_medians_pct": {"commits": 43.743509865005194, "clean_churn": 34.99461573513386,
                                          "higher_rule": ">= original median"},
            "score_trajectory": {"threshold": 0.125, "positive_delta_rule": "> 0.125",
                                 "rule": "Registered adaptive signed threshold; improved/stable/declined labels remain fixed, no reclassification."},
            "complexity_strata": {"median": 1.875, "low_rule": "<= median", "high_rule": "> median", "minimum_n_for_rho": 4},
            "phase_order": ["pre_t1", "t1_to_t2", "t2_to_t3_excluding_final7", "final7_pre_t3"],
            "phase_intervals": {
                "pre_t1": "Observed pre-T3 repository start up to T1; variable duration.",
                "t1_to_t2": "[T1,T2)",
                "t2_to_t3_excluding_final7": "[T2,T3-7d)",
                "final7_pre_t3": "[T3-7d,T3)",
                "assignment": "Every observed pre-T3 event belongs to exactly one phase.",
            },
            "weekly_bins": "13 exclusive seven-day [start,end) bins over the 91 days before T3; not independent teams.",
            "regularity": "Mean of eight original normalized components: active-day share, commit/clean-churn entropy, inverted min-max weekly commit/clean-churn CV, inverted M7 inactivity, inverted final-seven commit/clean-churn shares. Never renormalize after filtering.",
            "uncertainty": "M1 bars are standard deviations; leave-one-out ranges are sensitivity diagnostics, not confidence intervals. No confirmatory significance.",
            "definition_sets": definition_sets(),
        },
        "paper_tables": [
            {"paper_label": "tab:metrics_summary", "role": "definitions", "datasets": [],
             "note": "Measures and analytical-grain definitions, not a separate observation table."},
            {"paper_label": "tab:rq2-summary", "role": "fixed_summaries",
             "datasets": ["m3-rolling-pooled", "m4-checkpoint-pooled", "m5-marker-density"],
             "note": "Separate source grains and units; no cross-grain estimate."},
            {"paper_label": "tab:rq3-associations", "role": "fixed_associations",
             "datasets": ["m9-structural-rework-magnitude", "m9-structural-rework-ratio", "m9-structural-outcomes"],
             "note": "Original 2 + 2 + 8 rows; keep each row's sample size and stratum."},
        ],
        "relationships": {
            "arbitrary_joins": False,
            "team_profiles": {"datasets": ["m6a-structural-planning", "m6b-planning-content", "m8-rework-magnitude",
                                          "planning-rework-profile", "complexity-profile", "complexity-rework-figure"],
                              "key": ["cohort", "team_id"], "cardinality": "one_to_one",
                              "purpose": "Authoring verification/eligibility, not arbitrary UI joins; require equal key coverage."},
            "survey_alignment": {"key": ["cohort", "checkpoint"], "purpose": "Side-by-side only at matching grain; retain role/family keys and denominators. Paired summaries remain separate."},
            "transcript_alignment": {"datasets": ["m5-marker-density", "m5-marker-composition", "m5-corpus-coverage"],
                                     "key": ["checkpoint"], "purpose": "One measured corpus only; no attribution to teams."},
            "checkpoint_profiles": {"key": ["cohort", "team_id", "checkpoint"],
                                    "purpose": "Checkpoint-specific verification must retain checkpoint; no best-effort joins."},
        },
    }
    validate_catalog(catalog)
    return catalog


def validate_catalog(catalog: dict[str, object]) -> None:
    from prepare_snapshot import array, obj, text

    require(catalog.get("schema_version") == "1.0" and catalog.get("language") == "en",
            "Unsupported catalog schema/language")
    descriptors = [obj(value) for value in array(catalog.get("datasets"))]
    ids = [text(d.get("id")) for d in descriptors]
    require(len(ids) == len(set(ids)) and set(ids) == set(public_schema()), "Catalog dataset coverage differs")
    schemas = public_schema()
    for descriptor in descriptors:
        dataset_id = text(descriptor.get("id"))
        key, expected = schemas[dataset_id]
        columns = [obj(c) for c in array(descriptor.get("columns"))]
        require([c.get("id") for c in columns] == expected and descriptor.get("key") == key,
                "Catalog public column/key projection differs")
        for name in ("title", "grain", "definition", "denominator", "estimation_population"):
            text(descriptor.get(name))
        require(descriptor.get("source") in SOURCES and descriptor.get("rq") in ("RQ1", "RQ2", "RQ3"),
                "Unknown navigation source or research question")
        for field in columns:
            text(field.get("label"))
            text(field.get("definition"))
            text(field.get("unit"))
            require(field.get("type") in ("string", "integer", "number", "boolean")
                    and isinstance(field.get("nullable"), bool), "Invalid column type/nullability")
        filter_ids = []
        for selection in array(descriptor.get("filters")):
            selection = obj(selection)
            filter_ids.append(text(selection.get("id")))
            selection_fields = [text(f) for f in array(selection.get("fields"))]
            require(bool(selection_fields) and set(selection_fields) <= set(expected), "Unknown filter field")
            if "team_id" in selection_fields:
                require(selection_fields == ["cohort", "team_id"], "Team selections need cohort-plus-team keys")
            if "omitted_team_id" in selection_fields:
                require(selection_fields == ["omitted_cohort", "omitted_team_id"], "Omission selections need composite keys")
        require(len(filter_ids) == len(set(filter_ids)), "Duplicate filter identifier")
        require(descriptor.get("filters") == filters(dataset_id, key, expected),
                "Catalog filters differ from the approved grain-specific choices")
        paths = obj(descriptor.get("paths"))
        require(paths == {"json": f"data/datasets/{dataset_id}.json", "csv": f"data/downloads/{dataset_id}.csv"},
                "Catalog paths must be relative public paths")
    columns_by_id = {text(d["id"]): set(schemas[text(d["id"])][1]) for d in descriptors}
    paper_figures = [obj(f) for f in array(catalog.get("figures"))]
    require(len(paper_figures) == 7 and len({text(f.get("id")) for f in paper_figures}) == 7,
            "Exactly seven distinct paper figure mappings required")
    for figure in paper_figures:
        for panel in array(figure.get("panels")):
            panel = obj(panel)
            dataset_id = text(panel.get("dataset"))
            panel_fields = {text(f) for f in array(panel.get("fields"))}
            require(dataset_id in columns_by_id and panel_fields <= columns_by_id[dataset_id],
                    "Figure mapping references unknown data")
            for encoding in ("x", "y", "error_y", "facet", "color", "size", "symbol"):
                if encoding in panel:
                    require(text(panel[encoding]) in panel_fields, "Figure encoding not in declared fields")
    for table in array(catalog.get("paper_tables")):
        require(all(text(d) in columns_by_id for d in array(obj(table).get("datasets"))),
                "Paper table references unknown data")
    relations = obj(catalog.get("relationships"))
    require(relations.get("arbitrary_joins") is False, "Arbitrary joins are not permitted")
    for relation_id in ("team_profiles", "transcript_alignment"):
        relation = obj(relations.get(relation_id))
        require(all(text(d) in columns_by_id for d in array(relation.get("datasets"))),
                "Relationship references unknown data")
    require(catalog.get("dataset_aliases") == {"m8-rework-participation": "m8-rework-magnitude"},
            "Dataset aliases differ from the approved redundant projection")
    require(catalog.get("excerpt_policy") == "omitted_by_human_decision", "Excerpt policy differs")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="Check existing bytes without writing")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        content = json_bytes(build_catalog())
        if args.check:
            require(args.output.read_bytes() == content, "Saved catalog differs; regenerate and review")
        else:
            require(not args.output.exists(), "Refusing to overwrite an existing catalog")
            require(args.output.parent.is_dir(), "Catalog parent directory must exist")
            with args.output.open("xb") as handle:
                handle.write(content)
        logging.info("Validated catalog: 49 dataset descriptors and seven paper figures; no observations or excerpts.")
    except (ContractError, OSError, ValueError, KeyError, TypeError) as exc:
        logging.error("Catalog preparation failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
