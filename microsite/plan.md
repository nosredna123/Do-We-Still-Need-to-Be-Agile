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
  request. This decision alone did not complete T015; its runtime verification
  is recorded below. T007/T008 and the final release review must likewise
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

### T009 - Reproducible public release metadata

**Completed 2026-10-22.** The [release manifest](data/release.json), schema
version `1.0`, identifies the snapshot neutrally as `research-data-001`.
It records SHA-256 hashes and byte lengths for the public catalog and all 98
observation/download files (99 artifacts), row counts for each JSON/CSV,
per-dataset column counts and coverage, and totals of 49 datasets, 1,674 rows,
and 17,046 scalar cells. Totals count JSON observations once, not again for CSV;
exported row counts are not independent participant/sample sizes.

The local [release authoring tool](tools/build_release.py) reads only public
files inside an explicitly selected site directory. It reuses the strict JSON
reader, public serializers, catalog validation, scalar types, and schema/key
contracts. It rejects malformed columns/types/nulls/keys, JSON/CSV disagreement,
missing/extra data artifacts, symlinks, stale saved metadata, and overwrites.
No private source inputs, source hashes, Git identifiers, authoring timestamps,
reviewer/approval records, or confidential lineage enter the public manifest.
The existing private T008 lineage remains outside this directory.

Coverage combines catalog-declared scope with observed row fields: cohort and
checkpoint lists where present, distinct composite team-semester counts only
for team-keyed data, measurement and ratio-status counts, baseline eligibility,
and corpus chunks. Original denominator fields and analytical grains remain
authoritative. No team attribution or unmeasured transcript cohort is invented.

Verification before completion:

- All 43 standard-library tests pass: 34 prior tests plus nine
  [release tests](tools/test_release.py). Tests were added first and failed
  before the implementation existed. VS Code still reports no discovered tests;
  explicit standard-library discovery executes the complete suite successfully.
- Independent verification recomputed every public artifact hash and byte
  length, every JSON/CSV row count, all per-dataset column counts, totals,
  status counts, and distinct team coverage from the persisted files.
- An isolated copied directory checks and regenerates byte-identical release
  metadata and passes all 43 tests without parent research files, dependencies,
  or private lineage.
- Negative tests reject a missing CSV, extra data file, changed CSV, extra JSON
  column, incorrect boolean-for-integer type, duplicate key, symlink, altered
  manifest hash, and output overwrite. Invalid input creates no new manifest.
- Existing catalog and all 98 T008 data files remain byte-for-byte unchanged,
  as do the approved contract/index fingerprints. Pylance syntax/diagnostics
  and whitespace checks pass; temporary copies and bytecode are absent.

The manifest is 45,542 bytes, SHA-256
`c5dbf7fc800c639cc584f90961000156f6c60c2a3c1491982d6e75834dd7c603`.
It excludes its own hash to avoid circularity and explicitly covers data
artifacts only, not documentation/tools/application assets or whole-site
approval. Hashes detect byte changes, not anonymity or authenticity if both
the manifest and data are replaced. The [README](README.md) documents check,
candidate generation, stale-hash diagnosis, and reviewed snapshot refresh.

Phase 2's data-export tasks are complete. The manifest deliberately retains
`snapshot_prepared_release_pending`: application implementation (T010 onward),
whole-directory privacy review, human release authorization, and actual-host
validation remain pending. No deployment URL or publication approval is claimed.

### T010 - Semantic three-section page shell

**Completed 2026-10-22.** The [entry page](index.html) provides semantic overview,
explore, and measures/methods sections in one English-language HTML document.
Native main-navigation links and three RQ cards target visible sections without
a router or JavaScript. The explore section has RQ1-RQ3 guides covering M1-M9,
with no inert dataset controls or simulated loading state.

The overview visibly distinguishes survey aggregates, composite cohort-plus-team
repository observations, one global measured transcript corpus, and fixed
published summaries. Methods explain scales, null-versus-zero semantics, baseline
eligibility, exact values, original denominators, and exploratory interpretation.
All catalog, release-manifest, and documentation links are local and relative.
There are no external assets, source identities, excerpt features, or missing
script/stylesheet references. The page explicitly labels its development state
and pending publication approval; T011 styling and T012 interactive navigation
are not claimed complete. The [README](README.md) describes these boundaries.

Verification before completion:

- Five new [shell tests](tools/test_page.py) were added before the page and
  initially failed on the missing HTML. All 48 standard-library tests now pass
  locally and in an isolated directory. They check landmarks, English language,
  headings/section labels, unique IDs, fragment targets, all local link paths,
  RQ/metric coverage, evidence grains, scientific caveats, and absence of
  unapproved features/external assets.
- A browser check confirmed the page title, a single top-level heading, visible
  methods content, and RQ1/RQ2/RQ3 fragment navigation. Keyboard activation of
  the visible skip link moves focus to the main landmark. No external resources
  were requested. These are shell checks, not full accessibility sign-off.
- An independently copied directory served identical HTML over HTTP both at
  `/` and `/review/explorer/`. All local links returned their expected bytes,
  and fragment targets resolved without the parent research repository.
- Saved catalog and release checks pass; every existing data artifact remains
  byte-for-byte unchanged. Pylance syntax/diagnostics and whitespace checks pass.
  Temporary servers/copies were stopped/removed; no bytecode was installed.

VS Code still cannot discover the standalone unittest files; explicit
standard-library discovery runs all 48 successfully without new dependencies.
One initial browser-verification snippet used an unavailable `URL` global in
the tool's execution context, not in the page. Replacing that check with plain
string fragment comparisons allowed the same browser actions to pass.

The shell is deliberately unstyled and the interactive explorer remains
unimplemented. Continue with T011 and T012; later chart, export, accessibility,
privacy, human release, and actual-host gates remain unchecked.

### T011 - Responsive accessible presentation

**Completed 2026-10-22.** The [local stylesheet](assets/styles.css) is linked
once from the [entry page](index.html). It provides system fonts, bounded
readable content, wrapping navigation, three-column RQ cards that stack below
52 rem, clear section spacing, underlined links, and offset keyboard-focus
outlines. No content is hidden to solve overflow, and no external assets,
fonts, framework, script, or build dependency is introduced.

Reusable native control rules cover labels, fieldsets, inputs, selects,
buttons, and disabled states without opacity-based loss of contrast. Table
rules provide captions, readable headers, right-aligned tabular numeric cells,
and local horizontal scrolling via `.table-scroll`. The [README](README.md)
specifies that future table wrappers need keyboard focus and an accessible
region name, and that future controls still need real labels and semantics.
No placeholder controls/tables were added to the shipped page; actual catalog
loading, filters, tables, and sorting remain in subsequent tasks.

Verification before completion:

- Four new [stylesheet tests](tools/test_styles.py) initially failed before
  the stylesheet existed. All 52 standard-library tests now pass locally and
  in an isolated copied directory. Tests check single local stylesheet wiring,
  system fonts, no network/hidden-content rules, contrast, focus and table styles.
- Measured text contrast is 14.76:1 for body text, 7.64:1 for muted text,
  8.50:1 for links on white, 7.75:1 for links on the soft panel background, and
  8.50:1 for button text. Focus contrast is at least 8.45:1 against page/panel
  backgrounds; control borders are 4.02:1 against white.
- Browser checks at 1280, 768, 360, and 320 px found no whole-page horizontal
  overflow. Cards use three columns on desktop and one on narrow screens.
  At 360 px with 200% root text sizing, content still fits horizontally.
- Real keyboard Tab navigation shows the solid offset focus ring, and Enter
  on the skip link focuses main. A programmatic focus check after pointer
  input did not activate `:focus-visible`, as expected; actual keyboard input
  was used to verify the keyboard-specific style rather than weakening it.
- A temporary browser-only fixture verified a 44 px select, a 46 px button,
  keyboard focus traversal, and a wide numeric table scrolling within its
  wrapper without widening the page. ArrowRight scrolls the focused wrapper;
  numeric cells use tabular numerals. The fixture was removed, not shipped.
- Browser inspection found no external resource requests. An isolated HTTP
  copy serves identical HTML/CSS at `/` and `/review/explorer/` with the correct
  MIME types; public release verification still passes.
- All data/catalog/manifest bytes remain unchanged. Pylance syntax/diagnostics
  and whitespace checks pass; temporary servers/copies were cleaned and no
  bytecode was installed.

VS Code still reports no discovered standalone unittest tests; explicit
standard-library discovery successfully executes all 52. Responsive/contrast
checks are scoped to this shell and temporary control/table examples, not a
full application accessibility certification. T012 data loading, later table
interactions, final human review, and host validation remain pending.

### T012 - Catalog navigation, definitions, and metadata states

**Completed 2026-10-22.** The local [application script](assets/app.js), loaded
with `defer`, fetches only the public catalog and release manifest. It validates
supported versions/policies, dataset schemas and local paths, RQ/metric/source
references, and matching public inventories/counts before enabling controls.
This is structural metadata validation, not runtime verification of file hashes
or a new publication authorization.

Researchers can select RQ, metric, evidence source, and any of the 49 dataset
descriptors. Downstream choices remain compatible; changing RQ resets metric
and source, and changing metric resets source. RQ cards select the corresponding
catalog scope and focus its control; native guide links and RQ fragments remain
available, including initial fragments and later hash changes. No router,
general query builder, or full filter-state URL persistence was introduced.

The selected dataset shows its definition, grain/key, denominator, coverage,
missingness/status semantics, fixed population, limitations, and expandable
column definitions, units, nullability, and category labels/order. Methods adds
literal case-insensitive search over all dataset definitions and the two embedded
codebooks, plus expandable frozen policies/thresholds. Snapshot identity, schema,
counts, coverage guidance, and hash scope come from the manifest. Metadata is
rendered via text nodes, never trusted HTML.

Loading disables navigation/search and announces progress. HTTP/JSON failures,
unsupported/inconsistent metadata, and the 15-second request timeout produce
an explicit logged alert, clear derived content, keep controls disabled, and
offer retry. Empty definition search is a separate, non-error state. Static
guides and local metadata/documentation links remain with a no-JavaScript
explanation. No excerpt feature/payload/request or fabricated observations
were added. The [README](README.md) documents behavior and both test commands.

Verification before completion:

- Nine new [JavaScript tests](tools/test_app.cjs) use only Node's built-in
  runner and public fixtures. They failed before the implementation existed;
  all nine now pass, along with all 52 Python authoring/static tests locally
  and in an isolated copied site. No package manifest, dependency installation,
  bundling, or server-side JavaScript requirement was introduced.
- Testing caught an overly restrictive draft assumption that all dataset
  metrics must belong to its primary RQ. Five existing supporting datasets
  correctly span metric families from other RQs. The validator now checks
  each declared metric against the complete approved metric vocabulary, and
  navigation preserves those actual mappings. RQ2/M6 planning/activity is
  explicitly regression-tested.
- Browser DOM checks rendered all 49 selected descriptors, including field
  definitions/units. They verified RQ scope changes, incompatible-choice reset,
  M5 corpus coverage, M8 ineligibility statuses, snapshot identity, RQ fragment
  initialization/hash changes, metric/field/codebook search, and no-match search.
- Browser fault injection verified loading/busy/disabled state, explicit 404,
  malformed JSON and unsupported snapshot errors, retry recovery, and timeout.
  HTML/script-like metadata stayed literal text without creating elements.
  Unit tests also reject invalid local paths, columns, keys, counts and hashes,
  and confirm requests are limited to the two metadata files.
- An independently copied site passes all 61 tests and HTTP checks at root and
  `/review/explorer/`. Nested browser navigation loads only local CSS, JS,
  catalog, and manifest under that prefix; no observation/excerpt or external
  requests occur. All data/catalog/manifest bytes remain unchanged.
- New controls remain at least 44 px high without horizontal page overflow at
  320/360/1280 px; 200% text sizing at narrow width also fits. JavaScript syntax,
  updated HTML semantic/label checks, Pylance diagnostics for the Python test,
  release verification, and whitespace checks pass.

The hidden shared browser tab stalled pointer stability and animation-frame
polling; browser event/state checks used dispatched DOM events and timer
polling instead. An attempted interception using the tool's route-fetch helper
also stalled; fulfilling an already-read public fixture verified inert rendering
without that helper. These verification-tool issues do not imply full keyboard/
pointer accessibility sign-off; that remains part of later application checks.
VS Code still cannot discover the standalone Python tests; explicit
standard-library discovery executes all 52, and Node executes the nine JS tests.

Temporary fixtures, copied previews, and servers were removed/stopped; no
bytecode or private artifacts were installed. Observation loading, row filters,
sorting/counts, comparisons, figures, and exports remain T013 onward, explicitly
marked pending in the UI. Human release and actual-host gates remain unchecked.

### T013 - Observation filters, counts, sorting, and table states

**Completed 2026-10-22.** The [application script](assets/app.js) now loads the
selected public JSON dataset, checks its exact column order, scalar types,
nullability, unique analytical keys, and release row count, and renders every
observation without rounding. Only the selected dataset is fetched; no parent
repository, private input, backend, package, or build is needed at hosting time.
Structural validation does not authenticate downloaded bytes; the existing
release-manifest verification remains the authoring-time integrity check.

The table exposes only catalog-approved filters and their actual typed values,
including composite cohort/team and omitted-case identities. Filter choices
retain the complete vocabulary; selections intersect, with explicit empty
results rather than implicit filter changes or fabricated zeros. Active filters,
visible/total counts, reset, a caption with grain, units in headers, and the
fixed-population notice explain scope. Reset restores the original rows and
source order while retaining the dataset. Changing datasets clears incompatible
filters, sort state, and the prior table. Surveys and global transcript datasets
never acquire unsupported team filters.

At T013 completion, each filter allowed one value or All. The catalog's allowed
multi-select capability was intentionally staged; compatible multi-cohort/
team-semester selection is implemented in T014 below. Filters select
existing observations or published estimates only; denominators, estimator Ns,
thresholds, populations, and scientific values are never recalculated.

Column buttons toggle stable typed ascending/descending sorting, announce
`aria-sort`, and retain focus after rendering. Nulls remain last in either
direction and display **Unavailable**, distinct from zero/false and empty
results. Existing status columns and missingness definitions explain unavailable
measurements and ineligible observations. All cell text is literal and numeric
precision is preserved. Wide tables stay inside the named focusable scroll
region; the whole page does not widen at narrow widths.

Loading clears old rows and disables row controls. HTTP/JSON/schema/count/key
failures and a 15-second timeout produce explicit logged errors and retry.
Changing selection cancels the old request; a version guard prevents stale
responses or errors from overwriting newer selections. Metadata failure also
clears the observation UI. Static no-JavaScript guidance remains available.

Verification before completion:

- Twelve new [row tests](tools/test_rows.cjs), alongside the nine existing
  [metadata tests](tools/test_app.cjs), pass using Node's built-in runner.
  The new tests initially failed before row helpers existed. They cover every
  approved dataset/filter choice, composite identity, intersections/reset,
  schema/type/key/count rejection, stable numeric/text/boolean/null sorting,
  all 510 shipped columns in both directions, precision, fixed estimates, and
  fetch failure/timeout/cancellation. All 52 Python tests also pass.
- Browser DOM checks compared all 49 rendered tables and all 17,046 scalar
  cells to their source values: null becomes `Unavailable`, otherwise exact
  string conversion. Filtering M1 to one cohort/team yields six family rows;
  reset restores 36. Incompatible cohort/team selection is explicitly empty.
  M8 unavailable ratios stay last on descending sort; changing to M5 clears
  unsupported team filters. Fixed summary populations remain visibly fixed.
- Injected 404 and malformed-schema responses clear the table, disable row
  controls, and expose an explicit error; retry recovers. A delayed request
  is aborted when selecting another dataset and cannot overwrite the newer
  table. HTML-like observation text creates no elements.
- Browser checks at 1280/360/320 px and 200% text at 320 px show no page
  overflow; the 406-row rolling dataset scrolls locally at narrow widths.
  Sorting retains the header-button focus. As in T012, the hidden browser
  uses dispatched DOM events and timer polling: real pointer/keyboard journey
  sign-off remains a later accessibility gate.
- An independent copied directory passes all 73 tests, JavaScript syntax,
  release integrity, and byte-identical HTTP delivery of assets, metadata,
  and all 49 dataset files at root and `/review/explorer/`. Nested browser
  navigation renders observations with requests confined to that prefix.
  All public data/catalog/release bytes remain unchanged.

The [README](README.md) describes the implemented behavior and test commands.
Explicit standard-library discovery is still needed because the editor does
not discover these standalone Python tests. No dependencies were installed;
temporary previews/fixtures were removed and servers stopped. Only T013 is
completed here: multi-case selection, figures, exports, full accessibility,
human release review, and actual-host publication gates remain pending.

### T014 - Compatible multi-cohort and team-semester selection

**Completed 2026-10-22.** The [application script](assets/app.js) now supports
multiple cohort/team-semester selections directly in the existing observation
table, without a separate comparison subsystem, cross-dataset joins, or new
estimates. The same mechanism applies to approved omitted-cohort/omitted-case
diagnostic filters: these select existing fixed leave-one-out rows, not newly
computed exclusions.

Catalog-approved cohort and composite case filters use native checkbox groups
with legends, explicit instructions, and clickable labels. Checkbox-based
multiselects avoid modifier-key gestures and work with the existing native-control
styles. None checked means all; one or more checked choices use OR within that
group. Different filters use AND. Other approved filters retain their existing
one-value-or-All selector. Reset clears every checkbox, selector, and sort;
navigation to another dataset clears incompatible state. Sorting retains selected
cases. Active summaries and counts update with the table, and conflicting
selections remain visible as explicit empty results rather than disappearing.

Team and omitted-case tokens/labels always include both cohort and team:
repeated team names cannot merge. Survey aggregates offer only their approved
cohort/category filters; global transcript aggregates offer no team or unmeasured
cohort choice. A scope notice explicitly identifies datasets without a
team-semester observation filter. All filters select existing rows at the
documented grain and preserve original values, missingness, populations, sample
sizes, denominators, and estimates. Unknown, duplicate, unapproved, or wrongly
typed selection tokens are rejected explicitly.

Verification before completion:

- Five new [row regression tests](tools/test_rows.cjs) cover cross-cohort repeated
  team labels, OR-within/AND-across every approved filter, empty/all selections,
  invalid inputs, fixed omitted-case rows, and unsupported team filters. The
  initial test-first run failed before the selection-array implementation;
  all 17 row tests and nine metadata tests now pass, along with all 52 Python
  authoring/static tests: **78 passed, zero failed/skipped**. No package,
  dependency, build, or backend requirement was introduced.
- Browser DOM checks exercised all 49 datasets, 51 checkbox groups across
  31 datasets, and their combination with single-value selectors. All
  17,046 unfiltered scalar cells match the approved source exactly; filtered
  tables match OR/AND predicates, counts, and complete reset behavior.
- Two baseline-eligible `TEAM_01` observations, one per cohort, display as two
  distinct cases with both composite labels in the active summary. Cohort
  intersection reduces this to one; selecting both cohorts restores two.
  Incompatible cohort/team choices give an explicit empty state; unchecking
  the last choice restores all. Sorting preserves selection.
- Changing from selected teams to a survey clears checks and sort, offers
  cohort comparison but no team filter, and retains the fixed-population
  notice. Global transcript coverage offers neither team nor cohort groups.
  An injected dataset 404 clears all stale groups/rows, disables row controls,
  and exposes a logged error; retry restores all cases unchecked.
- Checkbox labels remain at least 44 px high, lists scroll locally, and the
  page fits at 1280/360/320 px and 200% text at 320 px. Fieldsets/legends,
  label association, hints, native checkbox focus, and label activation pass.
  The hidden shared browser did not deliver Space activation to the focused
  checkbox. DOM events verify behavior, but real keyboard/pointer journeys
  remain open for the later accessibility gate; this is not full sign-off.
- An independent copied directory passes all 78 tests, JavaScript syntax,
  the 99-artifact release integrity check, and byte-identical HTTP delivery
  of assets/metadata/all 49 datasets at root and `/review/explorer/`. Browser
  comparison checks run against that nested independent copy. All frozen
  public data/catalog/release bytes remain unchanged.

The [README](README.md) documents selection semantics and scientific limits.
Temporary previews were stopped and removed; no private artifacts or bytecode
were added to the site. T015 and all later tasks remain open. Excerpt omission
is unchanged, and all 11 human/actual-host publication gates remain unchecked.

### T015 - Verified no-excerpt branch

**Completed 2026-10-22 through the T004 omission decision.** The approved-excerpt
set is empty, so no excerpt renderer, navigation, placeholder, search index,
download, payload, or request is added. The existing [page](index.html) and
[application](assets/app.js) already implement that branch. Adding a dormant
renderer or feature switch would conflict with the explicit omission boundary
and introduce unnecessary code. No production HTML/JavaScript/CSS or public
data changes were needed for this task.

Three new [JavaScript regressions](tools/test_app.cjs) verify that the shipped
catalog/release/data inventory contains no excerpt descriptor or placeholder;
missing or changed omission policy fails before observation requests; and
approved lexical aggregates/definitions and structured planning counts remain
valid while added quotation fields fail exact-schema validation. A new
[page test](tools/test_page.py) checks absence of quote markup, excerpt controls,
links and misleading empty-feature messages. These are regression tests for an
already implemented branch, not a new renderer developed through a failing
implementation test.

Verification before completion:

- All **53 Python and 29 JavaScript tests pass** (82 total, zero failed/skipped),
  including the preparation allowlist, deterministic catalog, public snapshot,
  exact-schema and new omission checks. JavaScript syntax, release verification
  of 99 artifact hashes, and whitespace checks pass.
- Browser navigation visits all 49 datasets in an independent nested copy:
  no excerpt UI, quote markup or excerpt request appears. Searching for the
  omitted dataset identifier yields the normal no-match definition state,
  not an excerpt view or placeholder. All observed requests stay within the
  local copied site.
- Approved transcript coverage still displays three checkpoint rows and
  structured planning still displays 14 cases, including its approved
  evidence-quote count column without source quotations.
- Injecting an enabled excerpt policy causes an explicit logged publication-
  policy error, disables navigation, clears rows, and makes no observation
  request. Restoring the catalog and retrying recovers all 49 choices and
  the initial 36-row table without any excerpt feature.
- The same independent-copy verifier used for T014 passes all current tests
  and byte-identical root/nested HTTP delivery of assets, metadata and all
  49 datasets. Production runtime assets, HTML and frozen data remain
  byte-for-byte unchanged from T014.

The [README](README.md) documents the omission branch and its limits. Structural
checks are not a classifier for unapproved prose disguised inside an existing
field: allowlisted generation, frozen hashes and final human review remain
required. No real quotations or private approval records were used as fixtures.
Temporary previews were stopped and removed; no dependencies were installed.
Adding excerpts later requires reopening T004 and approving exact text/context.
T016 onward and all 11 human/actual-host publication gates remain pending.

### T016 - Chart fidelity/size gate and pinned local vendor

**Completed 2026-10-22.** Selected the official **Plotly.js Cartesian 4.1.2**
distribution, vendored unchanged as
[plotly-cartesian-4.1.2.min.js](assets/vendor/plotly-cartesian-4.1.2.min.js), with
the upstream [MIT license](assets/vendor/LICENSE-plotly-4.1.2.txt) and in-bundle
notices retained. The npm registry's package version/license and archive SHA-512
integrity were checked before extracting only those two files. No package
manager, dependency installation, build, CDN, chart framework, second library,
or pre-existing chart HTML was introduced.

The Cartesian subset covers the requested error bars, heatmaps, scatter/line/bar
traces, colors/symbols/marker sizes, logarithmic axes, and zoom without the full
distribution's geospatial/3D weight. The smaller basic bundle does not provide
heatmaps. Hand-building scale/error-bar geometry, hit testing, heatmaps and zoom
would add unnecessary custom code, so the plan's preferred single local Plotly
renderer is retained. The measured tradeoff is explicit: **1,507,990 bytes raw**,
**499,721 bytes with gzip level 9**, versus about 6.17 MB for the full published
package unpacked. Compression is optional hosting configuration; no gzip copy
or hosting-time build is required. No prior transfer budget was specified.

The [README](README.md) records provenance, exact bundle/license hashes, size,
upgrade precautions and integration boundaries. Three new
[vendor tests](tools/test_vendor.cjs) failed on the missing vendor files before
installation, then passed. They pin the exact raw bytes/version, retained
license/notices, raw size, approximate compressed-size guard, single-library
inventory, and local existing script references. Compressed output can differ
slightly between zlib versions; raw SHA-256 is the exact integrity check.

Representative fidelity verification used a **private temporary prototype** in
an isolated copied site, built from approved public data and compared against
the reference figure scripts and images:

- M1: all 36 mean/SD points across two cohort facets, original checkpoint order,
  shared 0-5 displayed axes, and explicit SD-not-CI semantics. All 36 rendered
  SVG error-bar endpoint pairs agree with the axis projection of mean plus/minus
  the original SD to within 0.011 px (SVG coordinate rounding).
- M2: all 36 role/cohort-checkpoint means in the reference 6-by-6 orientation,
  role order, reversed vertical display, fixed 1-5 color scale and two-decimal
  cell labels. A synthetic missing cell removes its label instead of appearing
  as zero. This heatmap is a capability check only: it is not an eighth included
  manuscript figure or approval to expand the seven-figure scope.
- Planning/concentration: all 14 exact x/y values, original stored marker
  diameters, T3 score colors, cohort symbols, and original frozen median guides.
  Composite cohort/team identity is available in hover. Programmatic zoom and
  reset leave scientific arrays unchanged.
- Log-axis planning/rework: the 11 positive magnitudes plot at original values;
  three original zeros remain in the exact source table and are not replaced
  by one or plotted on a logarithmic axis. Original eligibility stays separate.
- All four specifications pass Plotly validation without warnings. Browser
  requests are confined to the copied site: the local library, private probe,
  and four approved JSON files; no font, cloud, map, MathJax or other external
  request occurs. Plot mark/label counts remain correct at 1280/360/320 px
  with local horizontal scrolling for the temporary narrow prototype.

The hidden browser made screenshot/stability capture unreliable. An attempted
inspection of an internal circular Plotly calculation object also exceeded
the tool response timeout; bounded scalar/geometry reads then succeeded.
A first endpoint probe mistakenly indexed traces independently of their subplot;
using Plotly's actual trace index verified all 36 bars. These are verification
tool/probe issues, not plot failures. The evidence is semantic/geometry fidelity,
not pixel-perfect image equivalence or real pointer/keyboard accessibility
sign-off. Final styling, interactions and table/caption alternatives remain
T017/T018 and the later accessibility gate.

All **53 Python and 32 JavaScript tests pass** (85 total, zero failed/skipped),
both in the repository and an independent directory copy. JavaScript syntax,
the 99-artifact data-manifest verification, whitespace, and root/nested HTTP
checks pass, including byte-identical vendor and license delivery. Data-manifest
hashes intentionally exclude application/vendor assets; exact vendor hashes
are separately pinned by the new tests.

The entry page still loads no chart library and displays its original 49-dataset,
36-row initial table. Production HTML, application code/styles and all frozen
data are unchanged. Only the vendor files, tests and documentation are added;
no prototype or fixture is shipped. Temporary servers/copies and the downloaded
archive were removed after verification. T017 onward and all 11 publication
gates remain pending.

### T017 - Selected paper figures

**Completed 2026-10-22.** The [figure script](assets/charts.js) renders exactly
the seven approved catalog figure mappings using the pinned local Cartesian
bundle. The [entry page](index.html), [application](assets/app.js) and
[stylesheet](assets/styles.css) provide independent figure selection,
loading/error/retry states, zoom/reset, captions, exclusion details, and
expandable exact full-snapshot source tables. No backend, package installation,
build step, external asset, new estimator, or additional figure is introduced.
The [README](README.md) documents operation, encodings and remaining boundaries.

Scientific fidelity verified before completion:

- RQ1: all 36 means, original SDs and response Ns, checkpoint/family ordering,
  two cohort facets, 0-5 displayed axes, and original family-unit distinctions.
  All 36 rendered SD endpoint pairs match projected mean plus/minus SD within
  0.011 px; the caption explicitly distinguishes SD from confidence intervals
  and discloses clipped below-zero uncertainty.
- RQ2 pooled activity: 29 numerically ordered overlapping windows, original
  pooled Ns, day-zero T3 guide and original day-one/302 peak annotation.
- Planning/concentration: all 14 exact x/y pairs, stored marker diameters
  (also checked in rendered marker data), common original T3-score domain
  1.5-2.5, cohort symbols and frozen median guides. Composite hover identities
  and percent units are correct.
- M4/M5: distinct panels, axes, units and denominators. Global 2025.2 transcript
  density remains separate from pooled team-semester churn.
- Artifact presence: four stacked count observations, categorical cohort axis,
  original cohort Ns of 9/5, and no conversion to percentages or quality scores.
- Log rework: 11 original positive magnitudes plot; all three original zeros
  remain in the 14-row source table and are explicitly listed as excluded,
  never replaced with one. Eligibility is separate from magnitude.
- Complexity/rework: all 14 magnitudes and three zeros on a linear axis,
  separate planning/cohort encodings, fixed original guides, baseline eligibility
  and ratio status. Null ratio hover says Unavailable; the log-profile hover
  does not invent a ratio field absent from its source dataset.
- All seven rendered scientific arrays match the specifications checked against
  approved sources. All **1,378 source-table cells across 117 rows** match exact
  original scalar strings, including null-to-Unavailable presentation. No
  data/catalog/release/vendor bytes change.

Interaction and resilience checks verified explicit HTTP 404, malformed JSON,
invalid row shape/count, missing renderer and missing figure-script failures;
successful retries; observation-table independence; metadata-failure clearing
and recovery; and cancellation/stale-result protection after figure changes.
Zoom and legend toggles preserve source values/populations; Reset restores the
original ranges and trace visibility. Filtering the initial observation table
to 18 rows leaves the independent 14-case figure unchanged, with the full-snapshot
boundary visibly stated.

All seven specifications pass Plotly validation without warnings. Browser
validation originally exposed an unnecessary single-trace legend configuration
that triggered a validator exception, and rejected shared score-color-axis
references. The activity figure omits its unused legend; score traces now have
identical explicit full-population Viridis bounds and one visible colorbar.
An unused second colorbar container was removed as well. These changes preserve
scientific encodings without suppressing validation or modifying the vendor.
A doubled hover-percent suffix found by interaction testing was also corrected.

All seven figures retain their mark counts with local chart/table scrolling
at 1280/360/320 px (21 combinations), without whole-page horizontal overflow.
Enlarged source-table text remains contained. Requests stay local. The hidden
browser evidence is scalar/SVG geometry and programmatic interaction, not
pixel-perfect screenshots or real keyboard/pointer accessibility sign-off.

All **54 Python and 44 JavaScript tests pass** (98 total, zero failed/skipped),
including 12 new [figure tests](tools/test_charts.cjs) and a figure-shell
regression in the [page tests](tools/test_page.py). The independent copied site
passes syntax, 99-artifact release verification, and byte-identical root/nested
HTTP checks. Whitespace and local documentation links are verified.

**T018 remains pending:** figures intentionally use complete original snapshots,
not observation-filter subsets. Captions and standalone source alternatives
provided now do not complete permitted chart/table selection synchronization.
Exports, full accessibility/visual review and all 11 publication gates also
remain pending. No excerpt feature or payload was added.

### T018 - Grain-safe chart and table selection

**Completed 2026-10-22.** The [application](assets/app.js) now passes the same
permitted row selection and filter summary to the [figure viewer](assets/charts.js)
that it uses for the observation table. Selecting a mapped dataset opens its
figure; choosing a figure opens its primary source dataset and existing filters.
Figure source tables have explicit source-selection buttons. Unmapped datasets
show a clear no-mapped-figure message, not a stale unrelated chart.
The [entry page](index.html) and [README](README.md) explain these rules,
reset behavior, fixed summaries, and alternative tables.

Only exact source-dataset identities are linked. The two M4/M5 panels remain
independent: selecting a checkpoint in one filters only that source's existing
rows; the other source stays full-snapshot and is identified as such. Opening
the other source resets incompatible filters instead of transferring them across
repository/transcript grains. Repeated team labels remain cohort-plus-team keys.

Per-source captions and exact alternative tables show selected/original row
counts and filter scope, units, grain, denominator and missingness. Fixed pooled
summaries are labeled as existing published rows, never recalculated selected-case
populations or Ns. Original score-color bounds, sample sizes, thresholds and
median guides remain fixed. Sorting orders the matching source alternative
exactly like the observation table; scientific checkpoint/day order stays intact
in line plots.

Empty intersections show no marks, an explicit empty state and zero-row source
alternative. Log-axis zeros stay unchanged in source tables and exclusion lists;
an all-zero selection shows no-plottable-values rather than fabricated marks.
Null ratios remain Unavailable. A synthetic missing-SD probe found that the
renderer coerced null error magnitudes into zero-length bars. The viewer now
draws bars only for available SDs while retaining original means/lines; missing
SD hover/table values explicitly say Unavailable. With one SD removed, all
36 original means and exactly 35 SD bars render, with no validation warning.

Filtering exposed two other renderer-specific corner cases: unused second
facet axes after a one-cohort RQ1 selection, and an empty artifact-state trace
causing the single-visible-trace legend validator exception. The implementation
shows only the surviving labeled cohort facet (same original scale/colors/SDs)
and omits empty artifact-state series. No validation error is suppressed and no
vendor/scientific data is modified.

Verification before completion:

- All **54 Python and 50 JavaScript tests pass** (104 total, zero failed/skipped).
  Six new [figure regressions](tools/test_charts.cjs) verify exact subsets,
  independent fixed-summary panels, frozen guides/color limits, empty/log-zero
  selections, one-cohort facets, rejection of altered/duplicate rows, and
  all eight source mappings without mutation. Existing missing-SD and
  [page-shell tests](tools/test_page.py) were updated for the completed behavior.
- Browser checks cover all **118 full/single-choice selections across eight
  figure-source datasets**, including every offered filter value: rendered
  scientific arrays, 5,376 exact source-table cells, clean Plotly validation
  when marks exist, and three no-plottable zero selections.
- Additional checks verify repeated TEAM_01 across two cohorts (two exact cases),
  cohort/team intersection, empty intersection, reset-view retaining filters,
  reset-rows restoring all 14 cases, two baseline-unobserved cases with
  unavailable ratios, and a zero-only log selection retained in its table.
- M4/M5 selection gives 1/3 or 3/1 rows in the independent panels/alternatives.
  Sorting all three transcript rows by token count gives T2/T3/T1 in both tables
  while the plotted time series remains T1/T2/T3.
- An unavailable secondary dataset reports HTTP 404, clears figure content, and
  preserves the three valid primary observation rows; changing filters/retrying
  recovers the proper 1/3 scoped figure. Held old requests and old render
  completions cannot overwrite the newer source/filter selection.
- All seven figures retain original mark counts with local horizontal scrolling
  at 360/320 px (14 combinations), no whole-page overflow, and locally contained
  32 px source-table text. Browser requests stay local. Hidden-browser
  scalar/geometry/DOM checks are not real keyboard/pointer or pixel-perfect
  visual accessibility sign-off; the later audit remains required.
- An independent directory copy passes all 104 tests, JavaScript syntax,
  99-artifact data-manifest verification, and byte-identical root/nested HTTP
  checks. Frozen data/catalog/release and vendor/license bytes are unchanged.
  Whitespace, local documentation links and task/publication markers pass.

An initial broad browser loop used throttled timers in the hidden page and was
stopped in favor of event-driven observation; the final exhaustive 118-selection
run completed successfully. This was verification overhead, not a site failure.

T019 export controls and subsequent release tasks remain pending; all 11
publication gates stay unchecked. No excerpt feature, backend, new dependency,
statistical estimator or cross-dataset join was introduced.

### T019 - Full dataset and faithful filtered CSV downloads

**Completed 2026-10-22.** The [application](assets/app.js) supplies native links
to the selected dataset's original full CSV and typed JSON, plus a locally
generated CSV for exactly the displayed observation rows/current sort order.
Its matching JSON companion records snapshot/dataset/filename, selected and
original row counts, filter definitions/typed choices/combination semantics,
sort, approved column definitions/order/units, grain/key, denominator,
missingness, coverage and fixed-population limitations. Scope information stays
out of CSV data rows, so ordinary CSV readers receive a conventional table.
The [entry page](index.html) distinguishes these download scopes and gives
essential null/precision/safety guidance; the [README](README.md) documents
operation. T020's consolidated reuse guidance remains a separate pending task.

Full links ignore filtering, sort and legend visibility and point only to
catalog-validated local snapshot paths. Filtered exports reuse the table's
typed selection/sort helpers, never chart-only visibility, hidden fields or
another source panel. Native filenames contain only approved dataset IDs.
Both generated downloads are refreshed together when selection changes.
An empty intersection produces column headers only with zero selected rows
in the companion metadata, never a fabricated null row.

Generated CSV uses UTF-8 without BOM, LF records, comma separators, quoted
headers/text with doubled double quotes, lowercase booleans, original approved
column order, and finite numbers' round-trip JavaScript decimal spelling
without display rounding. Numeric values match loaded original values even
where authoring Python's decimal spelling differs. An empty unquoted cell is
null/Unavailable, not zero or false. Current data has no empty strings or
nullable text columns; any future ambiguous empty nullable text is rejected
explicitly rather than silently collapsed into null. Full typed JSON preserves
explicit nulls.

The existing preparation policy for spreadsheet-unsafe text is reused:
formula-leading strings (including whitespace-prefixed indicators) and
tab/CR/LF-leading text fail explicitly, without prefixes or value changes.
Negative numeric values remain numbers. Quoting alone is not claimed to make
spreadsheets preserve types/precision; import guidance and companion definitions
explain that boundary.

Loading/changing datasets clears stale filtered links. Missing/malformed data
cannot generate an export; the current full links remain independent native
snapshot links. Serialization/Blob URL errors log an alert, remove partial
downloads, retain valid observation tables, and offer retry. Replaced URLs are
revoked, page exit releases them, and back/forward cache restoration rebuilds
the current pair.

Verification before completion:

- All **55 Python and 58 JavaScript tests pass** (113 total, zero failed/skipped).
  Eight new [export tests](tools/test_exports.cjs) cover all 49 datasets and
  17,046 scalar cells, every permitted single-choice filter, composite
  selection/sort, metadata definitions/scope, empty output, CSV quoting/Unicode,
  null/zero/false distinctions, and explicit unsafe/invalid/ambiguous rejection.
  A new [page test](tools/test_page.py) checks scope, missingness and retry UI.
  All six initial export tests failed for absent helpers before implementation.
- Browser reads of actual generated Blob URLs verify all 49 filtered CSV
  payloads against the displayed tables (17,046 cells), original column order,
  metadata definitions/counts and MIME types. All 49 native JSON/CSV pairs
  were fetched and compared by typed scalar value; full targets/filenames
  resolve to their correct dataset.
- Repeated TEAM_01 across two cohorts exports exactly two sorted rows with
  composite filter choices and descending sort recorded. Conflicting filters
  produce one header record/zero data rows and explicit status. Reset restores
  all 14 rows and clears filters/sort. Legend visibility leaves export URLs
  and original selected row counts unchanged.
- Unsafe synthetic text remains literal in the valid observation table while
  filtered export fails explicitly without links. A simulated second-Blob
  creation failure revokes the first partial URL, leaves zero live URLs/links,
  preserves 14 observation rows and full links, and recovers through retry.
  Replaced pairs and page exit revoke URLs; simulated cached-page restoration
  recreates exactly two links.
- HTTP 404 clears filtered downloads and rows without exposing stale content;
  row retry recovers the 29-row dataset. A held old request cannot replace the
  newer dataset's filename, metadata or 14 selected rows.
- Four download links and scope guidance stay within 360/320 px layouts and
  enlarged text without whole-page overflow. Requests remain local.
- Independent-copy tests, JavaScript syntax, all 99 data-manifest hashes,
  whitespace/local-document links, and byte-identical root/nested HTTP
  delivery pass. The HTTP verifier now checks **both** formats for all 49
  dataset pairs. Data/catalog/release and vendor/license bytes are unchanged.

The integrated hidden browser did not emit Playwright file-save download events
for native download links using dispatched, DOM or forced clicks. Blob payloads,
MIME types, relative native URLs and download attributes/filenames were verified
directly instead; no actual save-dialog or downloaded-file-on-disk success is
claimed. Normal-browser download UX remains an explicit T021/T022/actual-host
check. This tool limitation is not hidden as a successful end-user gesture.
The initial page-shell test also caught an unnecessary extra section; downloads
now use a labeled region inside Explore, preserving the three-view structure.

T020 and subsequent acceptance/accessibility/release tasks remain pending.
All 11 publication gates are still unchecked; no publication approval, excerpt
payload, backend, dependency or statistical estimator was added.

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
- Use native select boxes or checkbox-based multiselects for cohort, checkpoint, role/category, and
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
- Use the locally bundled Plotly.js Cartesian 4.1.2 distribution selected by
  T016's fidelity/size check, because existing figures already use Plotly and
  require error bars, heatmaps, and scatterplots. Use only one library and retain
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
- [x] T009 [Plan:2.1] Write `microsite/data/release.json` with a neutral snapshot identifier, schema version, public artifact hashes, row counts, and coverage. Retain confidential source lineage only outside the directory. Verified all 99 public artifact hashes, 49 dataset counts/coverage, isolated byte-identical regeneration, 43 passing tests, and explicit failure paths; see Section 3.

**Exit:** Frozen public JSON/CSV that agrees with the paper and contains no private
fields. Preparation can depend on explicitly supplied research inputs; the
resulting directory cannot depend on them at runtime.

### Phase 3 - Implement navigation and the table explorer

**Plan 3.1:** Build the three-view shell.
**Requirements:** REQ-001, REQ-002, REQ-003, REQ-005.

- [x] T010 [US1] [Plan:3.1] Build semantic overview, explore, and methods sections in `microsite/index.html`, with RQ cards and a visible evidence-grain explanation. Verified semantic structure, RQ/metric scope, local links, keyboard skip-link focus, browser fragment navigation, isolated HTTP root/nested hosting, and all 48 tests; see Section 3.
- [x] T011 [US1] [Plan:3.1] Implement the responsive layout, system-font styling, accessible controls, focus states, and readable tables in `microsite/assets/styles.css`. Verified 52 tests, measured contrast, browser widths 320-1280 px, 200% text, keyboard focus and local table scrolling, and standalone HTTP CSS delivery; see Section 3.
- [x] T012 [US1] [Plan:3.1] Load the local catalog and implement RQ/metric navigation, definitions, snapshot details, and explicit loading/error states in `microsite/assets/app.js`. Verified all 49 descriptors, cross-RQ metrics, definition search, snapshot metadata, loading/errors/retry, 52 Python plus nine JavaScript tests, and isolated root/nested delivery; see Section 3.

**Plan 3.2:** Add compatible filtering, sorting, and comparisons.
**Requirements:** REQ-002, REQ-004, REQ-005.

- [x] T013 [US2] [Plan:3.2] Implement dataset-specific filters, reset, active-filter summaries, visible counts, numeric/text sorting, missing-value display, and empty states in `microsite/assets/app.js`. Verified all 49 tables/17,046 cells, every approved filter and column, explicit errors/retry/cancellation, 73 tests, and independent root/nested hosting; see Section 3.
- [x] T014 [US2] [Plan:3.2] Implement compatible multi-cohort/team-semester selections in `microsite/assets/app.js`, using cohort-plus-team keys and disabling unsupported team filters for surveys/transcripts. Verified all 49 datasets/51 checkbox groups, exact values, OR/AND/reset and evidence-grain limits, 78 tests, and independent root/nested delivery; see Section 3.
- [x] T015 [US2] [Plan:3.2] Render approved excerpts, if any, in `microsite/index.html` through `microsite/assets/app.js`, with checkpoint/source context and no fabricated team attribution. Completed the no-excerpt branch required by T004: no view/payload/placeholder/request; 82 tests, all 49 runtime datasets, fail-closed policy/retry and independent root/nested delivery verified; see Section 3.

**Exit:** A researcher can navigate from an RQ to exact values and understand what
is measured, what is missing, and which comparisons are valid.

### Phase 4 - Add paper figures and downloads

**Plan 4.1:** Recreate only the selected paper visualizations.
**Requirements:** REQ-002, REQ-004, REQ-005, REQ-006.

- [x] T016 [US3] [Plan:4.1] Check representative error-bar, heatmap, and scatterplot fidelity; if needed, bundle the pinned chart library and license under `microsite/assets/vendor/`. Do not add a chart framework or second library. Verified Plotly.js Cartesian 4.1.2, upstream integrity/MIT notices, 1.51 MB raw/0.50 MB gzip, representative rendered geometry/data, local-only requests, 85 tests and independent root/nested delivery; see Section 3.
- [x] T017 [US3] [Plan:4.1] Implement selected RQ1-RQ3 figures in `microsite/assets/charts.js` from approved figure-data mappings, preserving units, uncertainty semantics, axes, zero handling, eligibility, and sample sizes.
- [x] T018 [US3] [Plan:4.1] Connect permitted chart filtering to table selection in `microsite/assets/app.js`; label fixed pooled/association summaries and ensure unavailable values are not plotted as zero. Provide captions and table alternatives in `microsite/index.html`.

**Plan 4.2:** Make approved data easy to reuse.
**Requirements:** REQ-005, REQ-007, REQ-008, REQ-009.

- [x] T019 [US4] [Plan:4.2] Add full-dataset links and filtered CSV export in `microsite/assets/app.js`, preserving public column definitions, filter scope, exact numeric values, and unambiguous missingness.
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
