# Paper V9 Figure Inventory

This inventory began as the exploratory output of
`paper_v9/scripts/results/generate_figure_candidates.py`, but it is now an
editorial figure inventory synchronized with
[`ARTIFACT_USAGE_CATALOG.md`](ARTIFACT_USAGE_CATALOG.md). The catalog remains
the authoritative control plane for artifact status, limitations, and
section-level decisions; this file summarizes figure families and their
strengths/limitations for fast review.

Status labels mirror the catalog taxonomy: `main_text`, `appendix`,
`response_letter`, `diagnostic_only`, and `candidate`. Figures promoted during
Fase 10 should be rendered in full text width when visually dense.

## Current editorial figure families

| Family / artifact | Primary figure(s) | Status | Strength | Limitation / caution |
|---|---|---|---|---|
| `rq2_score_delta_vs_final7_concentration` | `rq2_score_delta_vs_final7_commit_concentration.{pdf,svg,png}`; `rq2_score_delta_vs_final7_clean_churn_concentration.{pdf,svg,png}` | `replication_package` after page-budget refactor | Separates final-week concentration with evaluator-score gain from final-week concentration without gain; directly mitigates the simple student-syndrome interpretation. | Descriptive small-n bins; score delta is a composite evaluator-score change, not a causal outcome model. |
| `rq2_planning_concentration_quadrants` | `rq2_planning_vs_final7_commit_concentration.{pdf,svg,png}`; `rq2_planning_vs_final7_clean_churn_concentration.{pdf,svg,png}` | `main_text` for commit variant; `replication_package` for clean-churn variant | Crosses repository-visible planning scope, final concentration, T3 score, and score-change magnitude. | Planning scope is structural and repository-visible; it is not semantic planning quality. |
| `rq2_nonoverlapping_phase_activity` | `rq2_phase_commit_share_by_score_trajectory.{pdf,svg,png}`; `rq2_phase_clean_churn_share_by_score_trajectory.{pdf,svg,png}` | `replication_package` after page-budget refactor | Tests whether late concentration remains visible under mutually exclusive project phases instead of overlapping rolling windows. | `pre_t1` duration is variable; Git activity does not observe work outside repositories. |
| `rq2_m5_2025_triangulation` | `rq2_m5_2025_triangulation_panel.{pdf,svg,png}` | `replication_package` after page-budget refactor | Makes M5 transcript coverage explicit and triangulates 2025.2 M5 density with clean churn, evaluator score, and T3 rework context. | M5 is global transcript-corpus evidence, not team-level; 2026.1 is unavailable and must not be zero-filled. |
| `rq2_operational_regularity` | `rq2_regularity_vs_final_concentration.{pdf,svg,png}`; `rq2_regularity_vs_score_delta.{pdf,svg,png}`; `rq2_regularity_profile_heatmap.{pdf,svg,png}` | `replication_package` / `appendix` after page-budget refactor | Contextualizes process heterogeneity with repository-visible temporal/author regularity. | Descriptive Git proxy only; not a validated measure of agile adherence, productivity, or process quality. |
| `rq3_complexity_profile` | `rq3_technical_complexity_vs_rework.{pdf,svg,png}`; `rq3_planning_rework_complexity_overlay.{pdf,svg,png}`; `rq3_complexity_vs_final_concentration.{pdf,svg,png}` | `main_text` | Makes technical complexity visible as a concurrent explanation for rework and concentration. | Complexity profiles are sensitivity/context views, not causal adjustments. |
| `rq3_influence_map` | `rq3_influence_map.{pdf,svg,png}` | `replication_package` after page-budget refactor | Exposes leave-one-out sensitivity across registered RQ2/RQ3 relationships. | Influence cells are descriptive diagnostics, not confidence intervals or confirmatory tests. |
| `team_semester_evidence_panel` | `team_semester_evidence_panel.csv` | `appendix` | Consolidates team-semester coverage, grains, and unavailable states for auditability. | Not a narrative figure; too wide for compact main-text tabulation. |
| `rq2_student_syndrome_reviewer_response` | `rq2_student_syndrome_*` and full-period tier plots | `response_letter` | Directly supports the reviewer-response thread about student syndrome. | Should not be promoted wholesale if newer Results figures already cover the same argument more cleanly. |
| `candidate_figure_inventory` | `candidate_rq1_*`, `candidate_rq2_*`, `candidate_rq3_*` | `diagnostic_only` | Original exploratory inventory remains useful for provenance and fallback comparison. | Superseded for most editorial purposes by the Fase 1--8 artifact families above. |

## Legacy exploratory candidates

## Candidate RQ1: separated perception panel

- Data: `paper_v9/figures/candidate_rq1_perception_panel_data.csv`
- Figure: `candidate_rq1_perception_panel.{pdf,svg,png}`
- Strength: preserves perception families and semester strata without a composite index.
- Limitation: dense family labels; usage distributions remain separate from perception.

## Candidate RQ2: temporal dynamics

- Data: `paper_v9/figures/candidate_rq2_temporal_dynamics_data.csv`
- Figure: `candidate_rq2_temporal_dynamics.{pdf,svg,png}`
- Strength: places M3, M4, and M5 on a temporal candidate view while retaining explicit units.
- Limitation: the measures have incompatible grains and scales; the figure must not be read as a correlation or common y-axis effect.

## Candidate RQ3: planning and clean rework profile

- Data: `paper_v9/figures/candidate_rq3_planning_rework_profile_data.csv`
- Figure: `candidate_rq3_planning_rework_profile.{pdf,svg,png}`
- Strength: shows structural T1 scope against M8a and marks baseline eligibility.
- Limitation: small sample and path-provenance interpretation; M6b structured content is not shown as a composite score.

## Candidate RQ3: leave-one-out association ranges

- Data: `paper_v9/figures/candidate_rq3_associations_leave_one_out_data.csv`
- Figure: `candidate_rq3_associations_leave_one_out.{pdf,svg,png}`
- Strength: exposes influence and sensitivity rather than hiding dominant cases.
- Limitation: ranges are descriptive diagnostics, not confidence intervals or significance evidence.

## Deferred selection decision

The original candidate figures were approved for carrying into a first LaTeX
version, but they are no longer a closed menu. Fase 10 promoted newer,
purpose-built robustness figures where they better serve the Results,
Discussion, and Threats narratives. Any future ad hoc result must have
traceable data, an explicit analytical grain, validation, and documented
limitations. Figures and prose should continue to be reviewed together. All
candidate or promoted figures must preserve unavailable states, analytical
grains, denominators, and the non-causal interpretation boundary.