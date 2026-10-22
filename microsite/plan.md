# Anonymous Research Data Explorer: Implementation Plan

## 1. Purpose and agreed scope

Build a small, English-language companion to the submitted paper. Researchers
should be able to find the evidence behind a research question, inspect its
measures, compare compatible observations, and download approved data without
working directly with the research pipeline.

This document tracks implementation work; it does not approve any dataset for
release. Completed tasks are checked only after their stated scope is verified.

### Decisions agreed during clarification

- Use a fully static site: HTML, CSS, JavaScript, and bundled data.
- Keep this plan and every microsite source file inside `microsite/`.
- Make the entire directory independently deployable by copying it to an ordinary
  static web server, at either a domain root or a subdirectory.
- Require no backend, database, account, package installation, build step, or
  research pipeline at serving time.
- Cover the submitted paper's measures and supporting datasets, not every
  pipeline output or every exploratory artifact in the repository.
- Provide research-question navigation, evidence-source browsing, filtering,
  sorting, metric explanations, interactive paper figures, valid comparisons,
  and approved dataset/filtered-result downloads.
- Include qualitative excerpts only after individual human review. Omit that
  view if no excerpts are approved; retain approved aggregate qualitative data.
- Preserve strict double-blind author anonymity and participant confidentiality.
- Allow one locally bundled chart library if needed, with its license retained.
- Keep the interface simple and user-friendly rather than building an analysis
  workbench.

### Explicit non-goals

No live pipeline connection, user uploads, user accounts, server-side search,
arbitrary joins, new statistical analyses, AI assistant, telemetry, external
fonts, CDN requests, automated updates, or hosting-provider-specific deployment
machinery. No requirement to work through a `file://` URL: preview and deployment
use HTTP(S). No frontend framework, router, or package manager unless a later
requirement genuinely demands one.

## 2. Requirements

| ID | Requirement |
|---|---|
| REQ-001 | One self-contained, copyable directory with relative asset/data links and no runtime dependency outside it. |
| REQ-002 | Plain static implementation and a small, English, accessible interface. |
| REQ-003 | Browse the submitted paper by RQ1-RQ3, evidence source, and metric families M1-M9. |
| REQ-004 | Filter, sort, inspect, and compare data only at its documented analytical grain. |
| REQ-005 | Explain definitions, units, denominators, coverage, missingness, provenance, and interpretation limits. |
| REQ-006 | Offer interactive counterparts of the submitted paper's figures without changing their statistical meaning. |
| REQ-007 | Download approved full datasets and the currently filtered rows. |
| REQ-008 | Publish only explicitly approved fields and individually approved excerpts; protect participants and double-blind anonymity. |
| REQ-009 | Freeze a paper-aligned snapshot with reproducible public provenance and explicit release gates. |

## 3. Evidence boundaries established from the paper

Use the following as authoring inputs, not as directories to publish wholesale:

- `paper_v9/latex/sections/methodology.tex`: analytical grains and metric meanings.
- `paper_v9/latex/sections/results.tex`: claims, figures, and reported values.
- `paper_v9/data/results/results_summary.json`: metric artifact index and caveats.
- `paper_v9/data/metrics/`: candidate metric tables and metadata.
- `paper_v9/figures/`: candidate figure-data tables and figure contracts.
- `paper_v9/ARTIFACT_USAGE_CATALOG.md`: editorial eligibility and diagnostic status.
- `paper_v9/data/manifests/input_inventory.json`: internal input lineage only.

Editorial inclusion and publication permission are different decisions. A
`main_text` artifact still needs privacy review; a technically valid `candidate`
is not automatically within this site's scope. Do not copy existing HTML charts,
metadata files, or manifests without inspecting their embedded content.

| Evidence | Grain and candidate sources | Allowed exploration and critical limits |
|---|---|---|
| RQ1 / M1 | Cohort/checkpoint summaries; `m1_rq1_perception_panel_long.csv`, usage frequency/tasks/tools and related submitted-paper tables | Cohort, checkpoint, perception family, task, or tool. Keep original scales, respondent counts, and standard deviations. Self-report is not AI-use telemetry. |
| RQ1 / M2 | Cohort/checkpoint/role distributions; `m2_role_perception_distributions.csv`, `m2_role_perception_by_team_semester.csv`, approved paired summaries | Compare roles and cohorts. Despite its filename, the inspected `by_team_semester` table has no team key. Do not invent one or publish respondent hashes. Paired summaries remain separately labeled sensitivity evidence. |
| RQ2 / M3-M4 | Team-semester/checkpoint/window; activity, author concentration, clean-change tables and paper figure data | Cohort, anonymized team-semester, checkpoint, and explicitly labeled window. Preserve clean versus total churn and overlapping versus non-overlapping windows. Aggregate author measures do not require author identities. |
| RQ2 / M5 | Global 2025.2 transcript corpus/checkpoint; `m5_marker_density.csv`, `m5_marker_composition.csv`, `m5_corpus_coverage.csv` | Checkpoint and lexical category. No team attribution, no 2026.1 transcript values, and no team-level correlation with repository data. |
| RQ3 / M6-M8 | Team-semester structural evidence, reviewed planning fields, inactivity, and rework eligibility | Compare compatible team-semesters using a cohort-plus-team key. Missing M6b evidence is not a zero planning score; inactivity is not planning omission; rework is not a verified defect count. |
| RQ3 / M9 | Published association rows and strata, with existing leave-one-out diagnostics | Filter existing predictor/outcome/stratum rows. Show the original sample size and exploratory status. Do not recalculate correlations from a user's subset or present leave-one-out ranges as confidence intervals. |
| Paper robustness views | Selected phase bins, timing/outcome contrasts, regularity, complexity and influence figure-data tables | Include only views actually used to support the submitted paper. Keep their diagnostic role, eligibility, thresholds, and original sample sizes visible. |

Current paper reference checks include 14 team-semesters (9 and 5 across the two
cohorts), M6b availability for 9 cases, M8 baseline eligibility for 12 cases, and
M5 coverage restricted to the 2025.2 corpus. These are snapshot checks, not
hard-coded application constants; reconcile any discrepancy before release.

### T001 - Paper snapshot and bounded inventory

**Inventory baseline:** `paper-v9-2026-10-22-t001`, inspected on 2026-10-22.
The paper version is the current anonymous manuscript rooted at
`paper_v9/latex/main.tex`, titled *Do We Still Need to Be Agile? What Student
Projects Reveal About Coordination Skills in the GenAI Era*. This identifies
the available submission-target source, not a certified final submission or
approved public-data release. Any subsequent manuscript/data change requires
reconciliation against this baseline before preparing the public snapshot.

Content fingerprints below pin the inspected inputs without publishing a Git
commit or identifying repository URL:

| Input | SHA-256 |
|---|---|
| Manuscript source set: `latex/main.tex`, its eight directly included section files, and `latex/references.bib` | `db86b65f1394dc84985026c73fd09a9d6a369a9545fa7935570e2fd5ce837f32` |
| `data/results/results_summary.json` (reconciled 2026-10-22) | `f0fe56c09d02104593e86da7e5f3d4e63b11cf782282988e99ec4019256c6fff` |
| `ARTIFACT_USAGE_CATALOG.md` | `c41defcd12ec37b71a5f7b986048fb0ac0244c785bf4477e208037507efccf12` |
| Seven manuscript PNGs in the figure inventory below | `f0f92e8011ffa91b3b7d976aed98c164fccfeaa9bbae5ccab9d845ff9739cade` |

Paths in this inventory are relative to `paper_v9/`, unless explicitly stated
otherwise. For either source-set fingerprint, sort member paths lexicographically,
then concatenate `relative_path + NUL + lowercase_file_sha256 + LF` for each
member, encode as UTF-8, and SHA-256 the result. Individual file fingerprints
hash the file bytes. The metric index also pins its individual source artifacts;
the previously detected rendering/index drift and its resolution are recorded
below. This index correction does not constitute public-release approval.

#### Selected metric datasets

The following is the complete initial metric selection: 32 source datasets.
Numbers in parentheses are inspected record counts, excluding CSV headers.
All filenames in this table are under `data/metrics/`. Selection means
"needed for the paper companion," not permission to publish every source field.
Field mappings, filters, and anonymization are T002/T003 work.

| RQ / family | Selected source datasets | Manuscript use |
|---|---|---|
| RQ1 / M1 | `m1_rq1_perception_panel_long.csv` (36); `m1_rq1_usage_frequency.csv` (60); `m1_rq1_usage_tasks.csv` (58); `m1_rq1_usage_tools.csv` (62); `m1_rq1_prior_ai_project_experience.csv` (12); `m1_rq1_autonomy_tool_balance.csv` (26); `m1_rq1_career_impact_topics_exploratory.csv` (36) | Perception means/SDs, usage and experience; career topics explicitly remain an exploratory supplement. |
| RQ1 / M2 | `m2_role_perception_distributions.csv` (165); `m2_role_perception_by_team_semester.csv` (36); `m2_role_perception_paired_t1_t3.csv` (12) | Role-specific agreement and separately labeled paired sensitivity summaries, not team observations. |
| RQ2 / M3 | `m3_author_activity_participation.csv` (14); `m3_author_concentration.csv` (28); `m3_activity_rolling_7day.csv` (406); `m3_activity_rolling_7day_pooled.csv` (29) | Team-semester timing/participation and the pooled temporal figure/summary table. |
| RQ2 / M4 | `m4_churn_magnitude.csv` (42); `m4_churn_magnitude_pooled.csv` (3); `m4_artifact_composition_pooled.csv` (6) | Checkpoint clean churn, observed coverage, and clean versus all churn. |
| RQ2 / M5 | `m5_marker_density.csv` (3); `m5_marker_composition.csv` (15); `m5_corpus_coverage.csv` (3); `m5_lexicon.json` (versioned lexical definitions, not observation rows) | Global checkpoint density, marker counts/composition, corpus coverage, and coding definitions. No transcript audit text. |
| RQ3 / M6 | `m6a_structural_planning.csv` (14); `m6b_llm_planning_content.json` (14 records: 9 successful, 5 unavailable) | Structural T1 evidence and separate exploratory content categories. The JSON is a restricted authoring input; only approved structured fields may be exported. |
| RQ3 / M7 | `m7_checkpoint_inactivity.csv` (42) | Checkpoint timing/coverage diagnostic, not a planning-omission predictor. |
| RQ3 / M8 | `m8_rework_magnitude.csv` (14); `m8_rework_participation.csv` (14); `m8_baseline_eligibility.csv` (14) | Rework magnitude, ratio, and explicit eligibility for the 12 eligible cases. |
| RQ3 / M9 | `m9_planning_vs_rework_m6a_m8a.csv` (2); `m9_planning_vs_rework_m6a_m8b_eligible_stratum.csv` (2); `m9_planning_vs_outcomes_m6a_t3.csv` (8); `m9_planning_vs_outcomes_m6b_t3_if_approved.csv` (30); `m9_leave_one_out_intervals.csv` (52) | The 12-row primary association table, separate M6b exploratory associations, and leave-one-out sensitivity. Existing analytical approval is not public-release approval. |

Ten indexed metadata files are definition/eligibility references, not automatic
public downloads: `m1_rq1_perception_panel.metadata.json`,
`m2_role_perception.metadata.json`, `m3_author_activity_dynamics.metadata.json`,
`m4_clean_change_dynamics.metadata.json`, `m5_coordination_evidence.metadata.json`,
`m6_structural_planning.metadata.json`, `m6_llm_planning_content.metadata.json`,
`m7_repository_inactivity.metadata.json`, `m8_clean_rework.metadata.json`, and
`m9_structured_associations.metadata.json`, all under `data/metrics/`.

#### Exact manuscript figure inventory

The current manuscript includes seven figures, all in Results, in the order
below. Image paths are under `figures/`; listed CSVs are also under `figures/`.
Their interactive counterparts are the initial chart scope. Supporting diagnostic
datasets below do not imply additional mandatory charts.

| RQ / manuscript label | Current PNG | Exact figure-data CSVs (rows) |
|---|---|---|
| RQ1 / `fig:rq1-m1` | `rq1_m1_perception_with_sd.png` | `rq1_m1_perception_with_sd_data.csv` (36), from the M1 long panel. Preserve SD bars and family scales. |
| RQ2 / `fig:rq2-m3` | `rq2_m3_activity_pooled.png` | `rq2_m3_activity_pooled_data.csv` (29), from the M3 pooled rolling table. |
| RQ2 / `fig:rq2-planning-commit` | `rq2_planning_vs_final7_commit_concentration.png` | `rq2_planning_vs_final7_commit_concentration_data.csv` (14). Preserve median quadrants, T3 score color, and absolute score-change size. |
| RQ2 / `fig:rq2-m4-m5` | `rq2_m4_m5_checkpoint_panels.png` | **Two inputs:** `rq2_m4_m5_checkpoint_data.csv` (3, M4 only) and `rq2_m5_density_data.csv` (3, M5 only). There is no `rq2_m4_m5_checkpoint_panels_data.csv`; the generator confirms separate panels/units. |
| RQ3 / `fig:rq3-presence` | `rq3_architectural_artifact_presence.png` | `rq3_architectural_artifact_presence_data.csv` (4), derived from M6a. |
| RQ3 / `fig:rq3-profile` | `rq3_architecture_rework_profile.png` | `rq3_architecture_rework_profile_data.csv` (14), combining M6a scope and M8 magnitude/eligibility. |
| RQ3 / `fig:rq3-complexity-rework` | `rq3_technical_complexity_vs_rework.png` | `rq3_technical_complexity_vs_rework_data.csv` (14), from the complexity profile family. |

The three manuscript tables also have bounded sources: `tab:metrics_summary`
comes from the Methodology definitions; `tab:rq2-summary` uses the M3 pooled,
M4 pooled, and M5 density tables above; `tab:rq3-associations` concatenates the
2 + 2 + 8 primary M9 rows. No new statistical estimation is required.

#### Supporting robustness inventory and catalog reconciliation

The seven families below have catalog status `main_text`, but that status does
not mean every family image is included in the current manuscript. Follow actual
manuscript use: present non-included views as supporting diagnostics, not extra
paper figures. Files below are under `figures/`.

| RQ / catalog artifact ID | Selected supporting CSVs (rows) | Current manuscript role |
|---|---|---|
| RQ2 / `rq2_nonoverlapping_phase_activity` | `rq2_phase_activity_share_data.csv` (56); `rq2_phase_activity_share_summary.csv` (12); `rq2_nonoverlapping_weekly_bin_contract.csv` (182, definition/audit reference only) | Descriptive non-overlapping phase check; no phase/weekly image is currently included. |
| RQ2 / `rq2_score_delta_vs_final7_concentration` | `rq2_score_delta_vs_final7_commit_concentration_data.csv` (14); `rq2_score_delta_vs_final7_clean_churn_concentration_data.csv` (14); `rq2_score_delta_final7_quadrants.csv` (16) | Score-change/concentration contrast referenced in text; variants remain supporting replication evidence. |
| RQ2 / `rq2_planning_concentration_quadrants` | Commit figure data above; `rq2_planning_vs_final7_clean_churn_concentration_data.csv` (14); `rq2_planning_concentration_quadrant_summary.csv` (8) | Commit view is an included figure; clean-churn variant and quadrant summary support the narrative. |
| RQ2 / `rq2_operational_regularity` | `rq2_operational_regularity_data.csv` (14) | Textual process-heterogeneity check; no regularity figure is included. |
| RQ2 / `rq2_m5_2025_triangulation` | `rq2_m5_2025_triangulation_summary.csv` (3) | Supporting coverage-aware context, explicitly left in replication artifacts by the current text. Do not repeat a global M5 value as a team observation. |
| RQ3 / `rq3_complexity_profile` | `rq3_complexity_profile_data.csv` (14); `rq3_complexity_confounding_summary.csv` (6); `rq3_complexity_metrics_contract.csv` (13, definitions) | Included complexity/rework figure plus text-reported median split and stratified sensitivity. |
| RQ3 / `rq3_influence_map` | `rq3_influence_map_data.csv` (182); `rq3_influence_heatmap_matrix.csv` (14); `rq3_influence_relationship_contract.csv` (13, definitions); `rq3_directional_robustness_summary.csv` (13) | Text-referenced influence diagnostics, not an included figure or confidence interval. |

Consult the corresponding family metadata for definitions:
`rq2_nonoverlapping_phase_activity.metadata.json`,
`rq2_score_delta_vs_final7_concentration.metadata.json`,
`rq2_planning_concentration_quadrants.metadata.json`,
`rq2_operational_regularity.metadata.json`,
`rq2_m5_2025_triangulation.metadata.json`,
`rq3_complexity_profile.metadata.json`, and `rq3_influence_map.metadata.json`.
The catalog's `candidate` artifact `rq2_score_trajectory_base` supplies
`rq2_score_trajectory_base_data.csv` (14) and
`rq2_score_trajectory_base.metadata.json` as shared score/delta definitions and
derivation context, not an additional explorer view.
The manuscript mentions outcomes derived from `data/lake/evaluator_team_cuts.parquet`
(repository-root-relative); it remains an internal provenance input. Existing
score/profile/association tables supply the selected paper views; no raw lake
download is in scope.

#### Explicit exclusions and verification result

Of the 54 primary artifacts indexed by `results_summary.json`, 32 are selected
datasets and 10 are metadata references above. The other 12 are deliberately not
separate public datasets:

- Redundant/unused M1 views: `m1_rq1_perception_panel_wide.csv` and
  `m1_rq1_perception_distribution.csv`.
- M4 components not used by the current manuscript views:
  `m4_commit_intensity.csv`, `m4_artifact_composition.csv`,
  `m4_rolling_7day_trajectory.csv`, `m4_commit_intensity_pooled.csv`, and
  `m4_rolling_7day_trajectory_pooled.csv`.
- Restricted audit/review files: `m5_evidence_audit_trail.csv` and
  `m6b_llm_planning_sample_for_review.md`. Approval of structured planning fields
  does not approve source quotes or full transcripts.
- Finer-grained views unnecessary for the selected manuscript claims:
  `m7_inactivity_trajectory.csv`, `m7_inactivity_pattern.csv`, and
  `m8_rework_trajectory.csv`.

These excluded filenames are all under `data/metrics/`. Also exclude the
catalog's `diagnostic_only` candidate-figure inventory, `response_letter`
student-syndrome family, and `appendix` integrated team-semester evidence panel:
none is an included figure/table or required distinct view in this manuscript.
Keep the seven selected robustness families' unused images, full event-assignment
audits, and duplicate chart exports out of the initial site. No verbatim excerpts
are selected by T001; any later excerpt requires T004 approval.

**Verification performed for T001:**

- All 54 primary indexed files exist and match their recorded SHA-256 checksums;
  CSV row counts and columns match the index.
- All 38 CSVs in the robustness index match their indexed row/column contracts;
  their checksums match. The selected figure/source files and metadata exist.
- All seven manuscript figures and three tables have the explicit mappings above.
  Four M1/M3/M4/M5 figure-data exports were compared with their canonical metric
  inputs by semantic keys, not row position. They agree within an absolute
  `1e-12` serialization tolerance (observed maximum difference
  `8.881784197001252e-16`); this does not authorize rounding public source values.
- Coverage checks confirm 14 distinct team-semesters (9 + 5), 9 successful and 5
  unavailable M6b records, 12 M8-eligible cases, and M5 checkpoint chunk counts
  35 / 37 / 28.
- **Resolved 2026-10-22 - stale index:** the initial inventory detected 15
  non-CSV checksum mismatches. Seven belonged to
  `rq2_planning_concentration_quadrants` (family metadata and two PNG/SVG/PDF
  triplets); eight belonged to `rq3_complexity_profile` (family metadata,
  complexity/rework PNG/SVG/PDF, and two other SVG/PDF pairs). History traced
  the drift to later page-budget figure revisions without an index refresh.
  Current family metadata input/data hashes were verified; the complexity
  metadata's output hashes also match the rendered files. The planning metadata
  differs from its earlier version only in generation time.
- Rebuilt `data/results/results_summary.json` with the existing generator,
  without regenerating figures or data. The correction changes only 25
  checksum/byte-count fields across those 15 records. All 180 indexed records
  now match their files' hashes and sizes; metrics, CSVs, inventory membership,
  manuscript, catalog, and figure-set fingerprints remain unchanged. The initial
  index fingerprint was
  `eb303948170fddc3cfd9a7aff70e164da231ae09702e76a0b130b9c83f6bdbdd`;
  the table above records the reconciled fingerprint.
- A regression assertion in `paper_v9/tests/test_results_summary.py` compares
  the saved summary with a freshly built one. It failed on the stale index
  before the correction. After any intentional indexed-artifact change, review
  its scientific/visual impact, then run
  `.venv/bin/python -m paper_v9.scripts.results.build_results_summary` last and
  `.venv/bin/pytest -x -q paper_v9/tests/test_results_summary.py`. Verify the
  resulting diff and update this baseline fingerprint if it changes.

T001 is complete as a verified scope/inventory task. The identified checksum
blocker is resolved; privacy approval and figure-fidelity release checks remain
required. T002-T005 and the remaining implementation tasks are not completed by
this inventory or index correction.

### T002 - Dataset contracts and proposed public field mappings

The [dataset contract specification](dataset-contracts.md) defines each selected
source's analytical grain, unique keys, proposed public ID/columns, units,
filters, denominators, eligibility, and missingness rules. It also specifies
aliases and definition-only inputs so the explorer does not duplicate tables.
This is the design input to T003 and the future T007 catalog, not an early
publication approval or an actual public catalog/data export.

Verified on 2026-10-22:

- All 58 selected source files (32 primary and 26 figure/support inputs) have
  explicit dispositions; all 56 CSV keys are non-null and unique.
- Checked 298 explicit table field references and the expanded regularity and
  complexity projections against source schemas.
- Verified survey/topic, activity, lexical, rework, phase, and regularity
  denominators; JSON extraction shapes; four chart aliases; M8 projection
  equivalence; figure/profile joins; influence-pivot cells and sign-preservation
  shares; 13 distinct weekly definitions; and fixed threshold values.
- Resolved interpretation hazards in the contract: topic assignments are not
  respondents; M3's 14-day final window is not the final-seven concentration;
  ineligible M8 ratios need explicit null/status masking; artifact activity is
  an integer count, not a boolean; and repeated T3 rework context in the
  triangulation summary is not a checkpoint-varying measurement.
- No private pseudonym crosswalks, approved observations, excerpts, or runtime
  catalog were created. Actual identifier mappings and human release decisions
  remain outside the publishable directory under T003/T004.

T002 is complete as a specification task. Its field projections require T003
approval before public snapshot preparation; that approval is recorded below.

### T003 - Human-reviewed publication allowlist

**Completed 2026-10-22.** The authorized human approver explicitly attested to
reviewing every proposed field and actual value/category vocabulary in the
[T002 contract specification](dataset-contracts.md), and confirmed that applicable
consent, ethics, and data-use permissions cover the release. Approval is bound to
contract SHA-256
`5cb0534f36bcee75eb08d56fda403f6ef443c826400ca790c727223972e52c68`
and the reconciled source-index fingerprint recorded above.

The private review record incorporates the contract's enumerated keys, projected
fields, derived fields, aliases, and catalog-only definitions as an explicit
allowlist. Unlisted fields remain denied; verification/derivation-only inputs
are not additional public datasets. The private approval record and identifier
registry are stored outside this publishable directory and are not site assets.

Review decisions:

- Exact approved numeric values, including small positive cells, may be released
  without adding a new suppression threshold. The approver considered residual
  linkage risk from small cells and exact project-level profiles.
- Original cohort labels and existing TEAM labels are approved. A private
  identity registry explicitly covers both cohorts and all 14 cohort/team pairs,
  including omitted-case analyses. A team label alone is never a valid key.
- Free-text-derived category vocabularies and proposed definition fields were
  included in the human review. Raw text, source paths/URLs, commit subjects and
  hashes, respondent/author identifiers, model output, and private crosswalks
  remain excluded under the contract.
- No additional restrictions were requested. This is a recorded human
  authorization, not a cryptographic signature or an automated guarantee of
  non-identifiability.

The original small-cell and linkage findings are resolved by an explicit,
permission-confirming human release decision, not by claiming that renaming
eliminates linkage. Verify the approved projections against exported rows during
T006-T008. Any new fields, source values/vocabularies, datasets, or changed
identifier policy require renewed review of the affected scope; changed hashes
must not silently inherit approval.

T003 does not approve verbatim excerpts (T004), authorize copying internal
metadata wholesale, or replace whole-directory/host anonymity checks (T023/T025).
No public data was exported during this task.

### T004 - Excerpt disposition for this release

**Completed 2026-10-22.** The human approver explicitly chose to omit all verbatim
excerpts from this release. The approved-excerpt set is empty; this is a
deliberate release decision, not a failed extraction or evidence that no
qualitative material exists. The decision is recorded privately outside this
publishable directory.

- Do not create or ship `data/datasets/qualitative-excerpts.json`, even as an
  empty placeholder. Do not add an excerpt dataset descriptor, navigation item,
  search index, view, download, or hidden bundled quote payload.
- Approved lexical aggregates, coding definitions, and structured planning
  evidence counts remain in scope under T003. A quote count does not authorize
  publishing its text. Full transcripts, audit-trail text, and commit subjects
  remain excluded.
- T015 must implement the no-excerpt branch: no excerpt-specific UI or dataset
  request. It is not completed by this decision; verify that branch when the
  application is built. T007/T008 and the final release review must likewise
  ensure no excerpt descriptors or payloads are shipped.
- Adding excerpts later requires reopening T004 and obtaining individual human
  approval of each exact text and its public context, with renewed field/snapshot
  review where applicable. Generic prior approval cannot enable that feature.

Verification confirmed no excerpt file, runtime catalog, or public dataset
directory exists at this stage. No source transcripts or quotations were copied
into the microsite during T004.

### T005 - Public documentation and hosting boundaries

**Completed 2026-10-22.** The [public README](README.md) documents neutral
naming, approved cohort/team-key semantics, allowlisted projections, exclusions,
the empty-excerpt policy, and an anonymous-hosting checklist. It distinguishes
field approval from final directory/host approval and explicitly states that
the application and public snapshot are not yet implemented.

Verification confirmed valid relative documentation links, no private source
locations or reviewer identities in the README, unchanged approved contracts,
and no runtime/data scaffolding. All 11 hosting checklist items remain unchecked:
they describe later release obligations, not checks passed by writing this file.
T024 must still supply executable preview/copy/refresh instructions after the
application exists; T023/T025/T026 retain whole-directory review, actual-host
verification, and the verified public URL record.

### T006 - Deterministic snapshot preparation

**Completed 2026-10-22.** The standard-library-only
[preparation utility](tools/prepare_snapshot.py) and its explicit
[projection definitions](tools/snapshot_contracts.py) implement all 58 selected
source dispositions. Source root, human publication approval, cohort/team
registry, and no-excerpt decision are explicit authoring inputs. Nothing is
imported from the parent research pipeline; private inputs and lineage remain
outside the publishable directory. Usage and spreadsheet-safety policy are
documented in the [README](README.md).

The pinned results index covers 50 of these inputs. Eight already-selected
figure/support CSVs are outside that index; they now have a supplementary
source-set fingerprint
`e721a33801a1e01be8d7cdd05aa2f7bdfd95bfb5d03ef856e7e8c34264a7d5a0`.
This hashes sorted `basename + NUL + file_sha256 + LF` records for the eight
explicitly listed supplemental inputs. It closes a preparation-validation gap,
not a new dataset approval. Indexed and supplemental byte changes both block
preparation pending reconciliation/review.

Verification before completion:

- All 17 synthetic [unit tests](tools/test_prepare_snapshot.py) pass, including
  projection agreement with the reviewed contract, strict scalar/null parsing,
  unique composite keys, alias failures, approval rejection, definition
  deduplication, spreadsheet safety, and no-write-on-validation-failure.
- An isolated copy of the directory, supplied only explicit external inputs,
  validated all 58 sources and prepared 49 dataset pairs (1,674 rows) plus two
  definition-only JSON sets for later catalog assembly. Those definitions are
  not extra data-browser tabs.
- Two preparations produced 100 byte-identical public files. JSON/CSV column,
  row, value, boolean, and null parity was checked, along with M6b's 9 measured
  and 5 unmeasured cases, 12 eligible M8 ratios, two baseline-masked ratios,
  exact private pre-masking cells, and retained fixed T3 transcript context.
- Mutated index, indexed CSV, supplemental CSV, and contract; missing required
  input; invalid private output placement; and attempted overwrite all failed
  explicitly without installing a public snapshot. Symlink paths are rejected.
- Pylance syntax/diagnostic checks and whitespace validation pass. No dependency
  was installed, research input changed, or private record copied into this
  directory.

Candidate exports existed only in automatically removed verification directories.
No `data/` directory, catalog, or release manifest has been installed here:
T007-T009 remain pending. Whole-directory and actual-host approval also remain
separate release gates.

### T007 - Public catalog and interpretation metadata

**Completed 2026-10-22.** The [public catalog](data/catalog.json), schema version
`1.0`, describes all 49 non-duplicate public datasets, with 510 column
descriptors, English labels, analytical grains/keys, units, denominators,
coverage, permitted filters, null/status semantics, and interpretation limits.
It embeds the 13 relative weekly-bin definitions and 13 complexity definitions
as catalog-only metadata, not extra data-browser tabs. Neutral evidence-source
labels replace identifying provenance. No private source fingerprints, source
locations, approval records, observation rows, or excerpt feature are included.

The local [catalog authoring tool](tools/build_catalog.py) uses explicit public
contracts and needs no research-repository imports or private inputs. It checks
descriptor coverage, column/key projections, grain-specific filter choices,
composite team selections, figure fields/encodings, relationships, and relative
public paths. It refuses overwrites and can check saved bytes without writing.
The [README](README.md) documents the schema's site-root-relative path base,
candidate generation, and current metadata-only state.

Verification before completion:

- All 27 standard-library tests pass: 17 existing preparation tests plus 10
  [catalog tests](tools/test_catalog.py). The saved catalog matches regenerated
  bytes; malformed filters, figure mappings, columns, duplicate IDs, and
  non-local paths are rejected.
- All 49 descriptors were compared against approved in-memory preparation of
  the 58 selected sources: 17,046 scalar cells agree with the declared column
  order, types, nullability, and keys. All filter fields and seven paper-figure
  mappings resolve to approved fields.
- Surveys and global transcript data have no team filters; transcript
  observations have no cohort filter or fabricated unmeasured-cohort values.
  Team and omitted-case selections require cohort-plus-team identity.
- Fixed association populations, original Ns, M6b unmeasured-versus-zero
  semantics, M8 ratio status/precedence, and repeated fixed-T3 transcript
  rework context are explicit. Frozen thresholds and no-reestimation rules
  remain unchanged.
- Figure-generator checks confirmed M3 plots pooled total commits, M1 facets
  by cohort with perception-family series, and M1's display axis is 0-5 while
  coded score units remain 0-4. Separate M4/M5 panels, logarithmic rework
  zero handling, and planning/complexity encodings are recorded faithfully.
- Embedded definitions agree with the approved source keys and structural
  fields. An initial assumed weekly label was corrected to the canonical
  `final_7_days`; exact weekly-definition comparison now passes.
- An isolated copy generates byte-identical catalog metadata and passes all
  27 tests without access to the parent repository. Overwrite and stale-catalog
  checks fail explicitly. Pylance syntax/diagnostic and whitespace checks pass.

The catalog is 322,211 bytes; its SHA-256 is
`a4280a18705491ede48196b8f3968c131ceaef12a8fe35f70aa1e48bd3a0e98f`.
This records an actual metadata payload size, not a completed browser
performance check. Only the catalog exists under `data/`: its observation and
download paths intentionally remain pending T008. T009 release metadata,
application implementation, and final directory/host approval remain pending.

### T008 - Approved observation and download snapshot

**Completed 2026-10-22.** Installed all 49 approved
[observation JSON datasets](data/datasets/) and 49 matching
[CSV downloads](data/downloads/): 1,674 rows and 17,046 scalar cells per format.
The preparation utility read the pinned inputs and private human decisions,
validated a separate candidate, and installed only its dataset/download
directories. No source files were copied wholesale. The catalog now reports
`snapshot_prepared_release_pending`; its paths resolve to actual local files.
The [README](README.md) documents this state and candidate-installation boundaries.

Verification before completion:

- All 34 standard-library tests pass: 17 preparation, 10 catalog, and seven
  [public-snapshot tests](tools/test_public_snapshot.py). The new suite initially
  failed on absent data, then passed against the installed files. VS Code
  discovery cannot discover these standalone tests; explicit standard-library
  discovery executes them without requiring new dependencies.
- A second fresh preparation from all 58 approved source inputs reproduces
  every JSON/CSV byte. All 49 schemas match the catalog's 510 column descriptors,
  including column/row order, scalar types, finite numbers, nullable cells,
  unique composite keys, and lowercase boolean/empty-null CSV serialization.
- Coverage remains 14 team-semesters (9/5 by cohort), nine measured and five
  unmeasured M6b cases, 12 M8-baseline-eligible cases, and transcript chunks
  35/37/28. Unmeasured M6b fields remain null, successful empty evidence remains
  zero, and ineligible rework ratios remain null with explicit status. Fixed-T3
  transcript context stays fixed, and surveys/transcripts gain no team key.
- Cross-profile ratio checks initially assumed exact equality between distinct
  source tables. Ten cells differ by less than `1e-16` because of original
  source serialization precision. The check now uses the existing preparation
  contract's `1e-12` absolute comparison tolerance. No source or exported value
  was rounded or replaced; exact per-source byte reproduction still passes.
- A copied standalone directory passes all 34 tests without parent research
  inputs. Isolated mutations prove rejection of altered CSV, an exposed
  ineligible ratio, and an extra unapproved dataset file.
- The 42 pre-masking ratio lineage cells stay outside this directory with
  private permissions. No private records/paths/URLs, excerpt payloads,
  duplicate definition assets, symlinks, bytecode, or temporary candidates
  were installed. Embedded catalog definitions agree with the preparation.
- Catalog determinism, Pylance syntax/diagnostics, unchanged approval
  contract/index fingerprints, and whitespace checks pass.

The 98 observation/download files occupy 759,659 bytes. Their output-set SHA-256
is `522c7bd9f048389011d49b7642e58ade83e41ca0e3d978a5d5c1aa7d02f53f0c`
(sorted site-relative path, NUL, file SHA-256, LF, then SHA-256). The status-only
catalog update has SHA-256
`65fe835ca8326514ae99759900b8efe618fd018c8fbe9958eb7393159c421a7c`.
These are task-verification fingerprints, not T009 release metadata.
T009, the application, browser/host validation, and final human publication
approval remain pending; this snapshot is not a ready-to-publish site.

### Publication hazards already identified

- The input inventory contains repository directory names and internal lineage.
  It must not be served directly.
- `m5_evidence_audit_trail.csv` contains transcript text and source/session paths.
  It must not be copied as an explorer dataset.
- `m6b_llm_planning_content.json` includes commit hashes, exact subjects,
  timestamps, and model-extraction context. Export only approved structured fields
  and, separately, individually approved excerpts.
- Existing pseudonyms, combinations of project attributes, searchable quotes,
  absolute dates, and exact commit statistics can still enable re-identification.
  Review linkage risk, not only direct names.
- Keep the private source mapping and approval record outside this publishable
  directory. An unlinked file inside a static site is still public.

If confidentiality requires withholding a paper value, explain that limitation;
do not silently perturb values, fabricate substitutes, or imply complete coverage.

## 4. Smallest useful design

### Three views in one page

1. **Overview:** short orientation, RQ1-RQ3 cards, evidence coverage, and a visible
   explanation that these are descriptive/exploratory observations.
2. **Explore:** choose a research question and metric/evidence dataset; see a short
   explanation, applicable filters, an interactive figure where relevant, a
   sortable table, and download actions.
3. **Measures and methods:** searchable definitions, scales, eligibility,
   provenance, limitations, snapshot identifier, and download guidance.

Use native navigation links and HTML sections, not a client-side router. A small
URL fragment may preserve the selected research question and metric; complex
shareable query state is not required.

### Interaction rules

- Show only filters valid for the selected dataset. Reset incompatible filters
  when changing datasets and display the active filters and visible row count.
- Use select boxes/multiselects for cohort, checkpoint, role/category, and
  team-semester where applicable. Avoid a general-purpose query builder.
- Provide a clear reset action, understandable empty states, and visible data-load
  errors. Distinguish load failure, unavailable measurement, ineligible observation,
  and an empty filter result.
- Keep exact values in tables and downloads; round only presentation labels.
- Display units and denominators beside the relevant numbers, not only in a
  separate glossary. Missing values must not sort or render as numeric zero.
- Allow side-by-side comparison through the same table/chart with selected
  compatible cohorts or team-semesters, not a separate comparison subsystem.
- Apply filters to underlying observation charts and tables together. Published
  pooled summaries and association estimates retain their original population:
  do not make them appear recalculated for a selected subset.
- Show original Portuguese excerpts only when approved, with an English
  explanation. Any translation must be reviewed and labeled as a translation.
- Use semantic headings, labeled controls, keyboard navigation, visible focus,
  sufficient contrast, and a table alternative for every chart. Do not rely on
  hover or color alone to communicate values.
- Use a restrained layout with system fonts, a readable content width, and
  horizontally scrollable tables on narrow screens. No dashboard decoration.

### Technical approach

- One `index.html`, one stylesheet, and a small set of plain JavaScript files.
- Fetch only local, approved JSON; load the selected dataset on demand.
- Keep a small catalog describing available datasets, columns, filter dimensions,
  chart type, grain, and limitations. It is metadata, not a generic plugin system.
- Keep CSV downloads alongside JSON. Prepare both from the same approved rows
  before release. Generate filtered CSV in the browser from those same public rows.
- Prefer a locally bundled Plotly distribution, subject to a short fidelity/size
  check, because existing figures already use Plotly and require error bars,
  heatmaps, and scatterplots. Use only one library, pin its version, and retain
  its license. Do not load it from a CDN or embed unreviewed existing chart HTML.
- Render dataset text as text, never as trusted HTML. Use robust CSV quoting and
  a documented spreadsheet-safety policy for textual export cells.
- Do not compute new statistical estimates in the browser. Reuse the paper's
  vetted summaries, eligibility flags, and figure-data tables.
- An optional standard-library-only authoring utility may prepare snapshots.
  It must take explicit input paths and an approval configuration outside the
  publishable directory, never assume the parent repository is present. Its
  execution is not required to serve the site.

### Planned directory layout

```text
microsite/
  plan.md                       # This plan; itself safe to publish
  README.md                     # Preview, copy/deploy, refresh, and release checks
  index.html
  assets/
    styles.css
    app.js                      # Navigation, filters, tables, and downloads
    charts.js                   # Paper-aligned chart rendering
    vendor/
      plotly.min.js             # Only if required by the fidelity check
      plotly-LICENSE.txt
  data/
    catalog.json                # Public definitions and dataset descriptors
    release.json                # Snapshot version, public hashes and row counts
    datasets/
      <dataset-id>.json         # Approved public rows only
    downloads/
      <dataset-id>.csv          # The same approved public rows
  tools/
    prepare_snapshot.py         # Authoring only; no serving-time dependency
```

Create only files needed by the implementation; this is not a request to scaffold
empty files now. Do not add a second application source tree or a `dist/` directory.
All URLs use relative paths. No symlinks, parent-directory imports, external
assets, private approval files, hidden backups, or source maps with private paths.
Everything in the copied directory, including documentation and tools, must be
safe to publish.

## 5. Phases and tasks

Dependencies are sequential unless explicitly stated otherwise. Publication
approval is a blocking prerequisite for producing public data, not a final
cosmetic review.

### Phase 1 - Freeze scope and approve publication

**Plan 1.1:** Identify the submitted-paper snapshot and the exact supporting
datasets/figures. **Requirements:** REQ-003, REQ-006, REQ-009.

- [x] T001 [Plan:1.1] Record the paper/snapshot version and a concise RQ-to-dataset/figure inventory in `microsite/plan.md`, reconciling the manuscript, metric index, and artifact usage catalog. Verified in Section 3, "T001 - Paper snapshot and bounded inventory"; the identified stale-index checksum drift was resolved on 2026-10-22.
- [x] T002 [Plan:1.1] Specify each selected dataset's grain, key, units, filters, denominators, eligibility rules, and source-to-public field mapping for the future `microsite/data/catalog.json`; keep identifying source mappings in the private approval record instead. Verified in `microsite/dataset-contracts.md` and Section 3's T002 verification record; subsequent field-publication approval is recorded under T003.

**Plan 1.2:** Approve fields and anonymity boundaries.
**Requirements:** REQ-005, REQ-008, REQ-009.

- [x] T003 [Plan:1.2] Obtain an explicit human-reviewed allowlist for every field destined for `microsite/data/datasets/`, assessing direct identifiers, searchable values, small cells, linkage, and free text. Keep the signed/private review record outside `microsite/`. Explicit authorized human approval recorded privately on 2026-10-22; pinned field scope, identifier policy, and remaining gates are summarized in Section 3.
- [x] T004 [Plan:1.2] Individually approve any excerpts intended for `microsite/data/datasets/qualitative-excerpts.json`; omit this dataset/view if none are approved. Do not reuse the full transcript audit trail. Human decision on 2026-10-22: empty approved-excerpt set; omit all excerpt payloads and UI for this release, as recorded in Section 3.
- [x] T005 [Plan:1.2] Document public-safe naming, exclusions, excerpt policy, and the hosting anonymity checklist in `microsite/README.md`, without including private source locations or reviewer identities. Verified README scope, links, exclusions, unchanged contracts, and 11 unchecked future hosting gates; see Section 3.

**Exit:** A bounded dataset/figure inventory and explicit publication approval.
Unresolved privacy questions block the affected dataset, not an implicit release.

### Phase 2 - Prepare the self-contained public snapshot

**Plan 2.1:** Export approved data and public metadata.
**Requirements:** REQ-001, REQ-004, REQ-005, REQ-007, REQ-008, REQ-009.

- [x] T006 [Plan:2.1] Implement `microsite/tools/prepare_snapshot.py` with explicit source/approval inputs, schema/key validation, deterministic JSON/CSV output, and explicit rejection of unapproved fields or broken required contracts. Never copy source files wholesale. Verified 17 unit tests, all 58 source dispositions, isolated deterministic exports, JSON/CSV parity, and fail-closed rejection paths; see Section 3.
- [x] T007 [Plan:2.1] Produce `microsite/data/catalog.json` with English labels, source-grain definitions, valid filters, approved relationships, missingness states, figure mappings, and interpretation notes. Use neutral source labels rather than identifying URLs. Verified 49 descriptors, 510 columns, seven figure mappings, embedded definitions, all 17,046 prepared scalar cells, 27 passing tests, and isolated deterministic generation; see Section 3.
- [x] T008 [Plan:2.1] Write approved rows to `microsite/data/datasets/<dataset-id>.json` and matching `microsite/data/downloads/<dataset-id>.csv`; preserve scientific values and explicit unavailable/ineligible states. Verified all 49 pairs, 1,674 rows, 17,046 scalar cells, exact approved-source byte reproduction, 34 passing tests, standalone-copy checks, and corruption rejection; see Section 3.
- [ ] T009 [Plan:2.1] Write `microsite/data/release.json` with a neutral snapshot identifier, schema version, public artifact hashes, row counts, and coverage. Retain confidential source lineage only outside the directory.

**Exit:** Frozen public JSON/CSV that agrees with the paper and contains no private
fields. Preparation can depend on explicitly supplied research inputs; the
resulting directory cannot depend on them at runtime.

### Phase 3 - Implement navigation and the table explorer

**Plan 3.1:** Build the three-view shell.
**Requirements:** REQ-001, REQ-002, REQ-003, REQ-005.

- [ ] T010 [US1] [Plan:3.1] Build semantic overview, explore, and methods sections in `microsite/index.html`, with RQ cards and a visible evidence-grain explanation.
- [ ] T011 [US1] [Plan:3.1] Implement the responsive layout, system-font styling, accessible controls, focus states, and readable tables in `microsite/assets/styles.css`.
- [ ] T012 [US1] [Plan:3.1] Load the local catalog and implement RQ/metric navigation, definitions, snapshot details, and explicit loading/error states in `microsite/assets/app.js`.

**Plan 3.2:** Add compatible filtering, sorting, and comparisons.
**Requirements:** REQ-002, REQ-004, REQ-005.

- [ ] T013 [US2] [Plan:3.2] Implement dataset-specific filters, reset, active-filter summaries, visible counts, numeric/text sorting, missing-value display, and empty states in `microsite/assets/app.js`.
- [ ] T014 [US2] [Plan:3.2] Implement compatible multi-cohort/team-semester selections in `microsite/assets/app.js`, using cohort-plus-team keys and disabling unsupported team filters for surveys/transcripts.
- [ ] T015 [US2] [Plan:3.2] Render approved excerpts, if any, in `microsite/index.html` through `microsite/assets/app.js`, with checkpoint/source context and no fabricated team attribution.

**Exit:** A researcher can navigate from an RQ to exact values and understand what
is measured, what is missing, and which comparisons are valid.

### Phase 4 - Add paper figures and downloads

**Plan 4.1:** Recreate only the selected paper visualizations.
**Requirements:** REQ-002, REQ-004, REQ-005, REQ-006.

- [ ] T016 [US3] [Plan:4.1] Check representative error-bar, heatmap, and scatterplot fidelity; if needed, bundle the pinned chart library and license under `microsite/assets/vendor/`. Do not add a chart framework or second library.
- [ ] T017 [US3] [Plan:4.1] Implement selected RQ1-RQ3 figures in `microsite/assets/charts.js` from approved figure-data mappings, preserving units, uncertainty semantics, axes, zero handling, eligibility, and sample sizes.
- [ ] T018 [US3] [Plan:4.1] Connect permitted chart filtering to table selection in `microsite/assets/app.js`; label fixed pooled/association summaries and ensure unavailable values are not plotted as zero. Provide captions and table alternatives in `microsite/index.html`.

**Plan 4.2:** Make approved data easy to reuse.
**Requirements:** REQ-005, REQ-007, REQ-008, REQ-009.

- [ ] T019 [US4] [Plan:4.2] Add full-dataset links and filtered CSV export in `microsite/assets/app.js`, preserving public column definitions, filter scope, exact numeric values, and unambiguous missingness.
- [ ] T020 [US4] [Plan:4.2] Explain dataset selection, snapshot identity, units, download scope, spreadsheet handling, and scientific caveats in `microsite/index.html` and `microsite/README.md`.

**Exit:** Paper figures are inspectable without becoming a new statistical tool;
downloads faithfully represent the approved snapshot and the displayed filters.

### Phase 5 - Verify, approve, and publish anonymously

**Plan 5.1:** Verify scientific fidelity, usability, and directory independence.
**Requirements:** REQ-001 through REQ-009.

- [ ] T021 [Plan:5.1] Complete the acceptance checklist below and record pass/fail evidence in `microsite/README.md`, using neutral descriptions and no private screenshots or machine paths.
- [ ] T022 [Plan:5.1] Copy only `microsite/` to a separate location and serve it over HTTP at both `/` and a non-root prefix such as `/review/explorer/`; confirm all views/downloads work without the repository, pipeline, or internet asset requests.
- [ ] T023 [Plan:5.1] Review every file to be published, including `microsite/plan.md`, `microsite/README.md`, assets, downloads, metadata, and tools, against the privacy allowlist and double-blind requirements.

**Plan 5.2:** Release the frozen snapshot on a neutral host.
**Requirements:** REQ-001, REQ-008, REQ-009.

- [ ] T024 [Plan:5.2] Document a provider-neutral copy-and-serve procedure in `microsite/README.md`, including MIME types, disabled directory listing, HTTPS, neutral URL requirements, refresh procedure, and the fact that all shipped files are public.
- [ ] T025 [Plan:5.2] After human release approval, copy `microsite/` to the selected host, inspect its public URL/redirects/headers/error pages for identifying branding, and repeat the core browse/filter/download checks against the deployed snapshot.
- [ ] T026 [Plan:5.2] Record the neutral public URL and snapshot identifier in `microsite/README.md`; supply the verified explorer URL for the paper citation through a separate manuscript change.

**Exit:** A frozen, approved directory has been proven portable and the actual
anonymous deployment works. A local preview alone is not publication verification.

## 6. Acceptance and release checklist

These are release checks, not a request to introduce a heavyweight testing stack.
Use existing tooling where appropriate and a browser for the interaction checks.

### Scientific fidelity

- Every selected paper dataset/figure is mapped or has an explicit, approved
  exclusion reason.
- Public numeric fields agree with the frozen source values; tables and downloads
  preserve precision. Display rounding and any privacy redactions are documented.
- Coverage agrees with the selected manuscript version, including its 14
  team-semesters, 9 M6b-observed cases, and 12 M8-eligible cases where applicable.
- M2's misleading source filename does not result in a team filter.
- M5 has no fabricated 2026.1 values or team attribution.
- Unavailable M6b values and baseline-ineligible M8 ratios remain visibly distinct
  from measured zero.
- M1 standard-deviation bars are not labeled confidence intervals. M9 and
  leave-one-out summaries retain their original populations and meaning.
- Figure axes, log-scale zero handling, scales, and labels agree with the approved
  paper figures/contracts.

### Researcher journeys

- From the landing page, reach each RQ's supporting measures and definitions.
- Select a cohort/checkpoint, sort a numeric column, inspect exact values, and
  reset without stale filters.
- Compare two eligible team-semesters; attempt an unsupported survey/transcript
  team comparison and confirm that no such control is offered.
- Download a full dataset and filtered results; verify exported row counts,
  columns, values, quoting, and missingness against the displayed scope.
- If approved excerpts exist, inspect them with correct coverage/context; if
  none exist, confirm there is no empty or misleading excerpt feature.
- Simulate a missing/malformed required dataset and confirm a clear error rather
  than an empty-success table or fabricated default.

### Accessibility and portability

- Complete core journeys using the keyboard; check visible focus and labeled
  controls. Every chart's information is also available in a table.
- At a 360 px viewport, navigation and controls remain usable; wide tables scroll
  within their own container rather than forcing the whole page sideways.
- Check current Firefox and a Chromium-based browser.
- With the isolated directory served at both root and nested paths, all local
  asset/data/download requests succeed. There are no parent-directory requests,
  external asset requests, console errors, or dependencies on a build service.
- After initial page load, the browser fetches only the chosen datasets rather
  than the entire collection. Record actual payload sizes; if a view is slow,
  reduce unnecessary data/dependencies before adding infrastructure.

### Anonymous publication

- Inspect visible content, source, strings, JSON/CSV, filenames, chart metadata,
  license notices, URLs, redirects, and server-generated error pages.
- Exclude author/institution identifiers, source repository links, commit hashes,
  respondent hashes, raw transcripts, hidden private fields, secrets, source
  paths, prompts, and restricted extraction/audit records.
- Check searchable excerpts and combinations of public attributes for linkage
  risk. Human approval is required; automated string scanning is not proof.
- Do not add analytics, trackers, social widgets, public source-repository links,
  or author-attributed deployment badges. Preserve third-party license notices.
- Use a neutral host/domain/account presentation and HTTPS. `noindex` may reduce
  discovery but is not an anonymity or access-control mechanism.
- Approve the whole directory and verify the actual hosted files before updating
  the paper's explorer citation.

## 7. Requirement mapping

| Requirement | Plan items | Planned implementation evidence |
|---|---|---|
| REQ-001 | 2.1, 3.1, 5.1, 5.2 | Relative links in `index.html` and assets; isolated root/subdirectory deployment checks; `README.md`. |
| REQ-002 | 3.1, 3.2, 4.1, 5.1 | `index.html`, `assets/styles.css`, plain JavaScript, keyboard/mobile checks. |
| REQ-003 | 1.1, 3.1, 5.1 | Paper inventory, `data/catalog.json`, RQ/metric navigation. |
| REQ-004 | 2.1, 3.2, 4.1, 5.1 | Grain-aware catalog, compatible filters/comparisons, fixed-summary labels. |
| REQ-005 | 1.2, 2.1, 3.1, 3.2, 4.1, 4.2, 5.1 | Catalog definitions, captions, eligibility/missingness states, methods section. |
| REQ-006 | 1.1, 4.1, 5.1 | Selected figure mappings, `assets/charts.js`, paper-value/figure checks. |
| REQ-007 | 2.1, 4.2, 5.1 | Approved JSON/CSV pairs, full links and filtered exports. |
| REQ-008 | 1.2, 2.1, 4.2, 5.1, 5.2 | Private approval gate; allowlisted exports; whole-directory and host review. |
| REQ-009 | 1.1, 1.2, 2.1, 4.2, 5.1, 5.2 | Frozen inventory, `data/release.json`, reproducible snapshot preparation and release record. |

## 8. Simplicity and conventions check

- **KISS/DRY:** one static application and one approved snapshot; no backend,
  duplicated application tree, custom query language, or framework.
- **Fail explicitly:** reject invalid preparation inputs and display runtime data
  errors. Missing evidence never receives a silent numeric substitute.
- **Preserve evidence:** reuse vetted paper artifacts rather than introducing new
  estimators, composites, causal claims, or inferred identifiers.
- **Independent deployment:** authoring inputs may be external; serving inputs
  must all be contained here.
- **Related project conventions:** if Python is used for snapshot preparation,
  follow the project's typed/pathlib/logging conventions and use its virtual
  environment during development. Python is not required on the destination host.
- **Migration guidelines:** no framework migration or rewrite is involved; no
  migration-specific transformation rules are needed.
- **Scope control:** create the site only after this plan is accepted. Do not
  modify research outputs or the manuscript as part of the microsite implementation
  without a separate explicit need.
