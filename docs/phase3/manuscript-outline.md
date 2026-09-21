# Manuscript outline: IMRaD plus Threats to Validity and Data Availability

**Target venue:** ICSE 2027 Software Engineering Education and Training (SEET), Research Paper category

**Working title:** When Planning Becomes Evidence: An Evidence-Constrained Study of Generative-AI-Supported Software Engineering Education

**Submission budget:** 10 pages including the main paper, plus up to 2 pages of references under the current call. Recheck the call before submission. The outline reserves space for a short Data Availability statement after the Conclusion and treats the four narrative acts as an argument map rather than as four empirical stages.

## Paper-wide evidence rule

The paper distinguishes three statement levels:

- **Observed:** directly reported by a persisted artifact and numerically verified.
- **Interpretive:** a bounded explanation consistent with the reports, structured sources, and literature.
- **Proposed:** a methodological implication or future hypothesis, especially SDD/BDUF; never a demonstrated intervention effect.

The central boundary appears early and repeatedly: team-semester `n = 14`, five tested primary analyses, no significant primary result, and a `conditional-go` verdict. Cross-evidence is secondary exploratory triangulation and cannot replace that verdict.

## Research questions

- **RQ1:** What planning, churn, technical-degradation, and temporal patterns are observable in the team-semester evidence?
- **RQ2:** What evidence is available, unavailable, or too sparse to characterize AI-related author concentration and coordination friction?
- **RQ3:** Which secondary cross-evidence patterns are worth carrying forward as bounded hypotheses, and how robust are they to multiplicity, exclusions, and sensitivity checks?
- **RQ4:** What implications for software engineering education and training can be proposed without claiming that SDD/BDUF has been experimentally validated?

## Page and evidence budget

| paper component | target space | controlling evidence |
| --- | --- | --- |
| Introduction | 0.75 page | CLAIM-01; `agile_manifesto_2001`, `williams_2024_ai_software_engineering_education` |
| Background and Related Work | 1.25 pages | `cunningham_1992_technical_debt`, `li_2015_technical_debt_mapping`, `brooks_1975_mythical_man_month`, `demarco_lister_1987_peopleware`, `chen_2021_evaluating_code_llms`, `perez_2022_planning_and_rework` |
| Method | 1.5 pages | CLAIM-02 through CLAIM-07; data book and source manifests |
| Results | 2.5 pages | CLAIM-02 through CLAIM-06; selected figures and primary statistical rows |
| Discussion | 1.5 pages | CLAIM-01, CLAIM-06, CLAIM-07; literature map; Acts 1-4 |
| Threats to Validity | 1.0 page | `threats_to_validity.md`; all claim threat notes |
| Conclusion and Data Availability | 0.5 page | all retained claims; privacy and artifact-lineage record |
| References | up to 2 pages | `references.bib` |

## 1. Introduction

### 1.1 Educational and generative-AI context

- **Purpose:** establish why software engineering education must examine planning, coordination, and evidence when AI-assisted programming changes the cost and speed of code production.
- **Claim level:** interpretive/contextual, not measured by this dataset.
- **Claims:** CLAIM-01.
- **Evidence:** [artifact report for Act 1](../../data/analysis/artifact_reports/act_1_evolutionary_ceiling.md); [statistical dataset manifest](../../data/analysis/statistical_dataset_manifest.json).
- **References:** `agile_manifesto_2001`; `williams_2024_ai_software_engineering_education`; `chen_2021_evaluating_code_llms`.
- **Allowed wording:** AI-supported course settings make planning and coordination an important educational design question.
- **Avoid:** claiming that AI necessarily causes planning debt or that the present cohort proves a general educational law.

### 1.2 Problem statement and motivation

- **Purpose:** motivate a study of whether observable planning signals align with later churn, degradation, rework, or coordination signals.
- **Claim level:** interpretive, with the empirical question deliberately narrower than the thesis.
- **Claims:** CLAIM-01, CLAIM-02, CLAIM-03.
- **Evidence:** [Phase 3 data book](../../data/analysis/paper_support/data_book.md); [argument matrix](argument-matrix.md).
- **References:** `cunningham_1992_technical_debt`; `li_2015_technical_debt_mapping`; `perez_2022_planning_and_rework`.
- **Required qualification:** planning intensity is a proxy for artifact volume, not planning quality.

### 1.3 Qualified hypothesis and research questions

- **Purpose:** state the qualified planning-debt hypothesis and RQ1-RQ4.
- **Claim level:** proposed hypothesis; not a confirmed result.
- **Claims:** CLAIM-01 through CLAIM-07 as the control set.
- **Evidence:** [claim-evidence matrix](argument-matrix.md).
- **References:** `cunningham_1992_technical_debt`; `li_2015_technical_debt_mapping`.
- **Boundary sentence:** the study tests whether the persisted evidence supports bounded descriptive and exploratory claims; it does not test SDD/BDUF superiority.

### 1.4 Contributions

Frame three contributions:

1. an empirical characterization of planning, churn, and human-factor signals in an AI-supported SE education cohort;
2. an auditable evidence organization linking reports, structured artifacts, figures, and caveats;
3. methodological implications for teaching specification and coordination under AI assistance.

- **Claim level:** observed contribution plus proposed implication.
- **Claims:** CLAIM-02 through CLAIM-07.
- **Evidence:** [phase3 evidence inventory](../../data/analysis/paper_support/phase3_evidence_inventory.md); [threats record](threats_to_validity.md).
- **References:** `williams_2024_ai_software_engineering_education`; `demarco_lister_1987_peopleware`.

## 2. Background and Related Work

### 2.1 Agile, planning, and specification

- **Purpose:** distinguish adaptive iteration from the question of how much explicit specification is needed before implementation in AI-supported education.
- **Claim level:** theoretical/contextual.
- **Claims:** CLAIM-01; no new empirical claim.
- **References:** `agile_manifesto_2001`; `brooks_1975_mythical_man_month`.
- **Evidence link:** [literature map](literature-map.md).
- **Caution:** SDD/BDUF is introduced as a proposed response, not as an empirically established alternative.

### 2.2 Planning debt, technical debt, and rework

- **Purpose:** define planning debt as a qualified interpretive construct and relate it to technical debt and rework without claiming equivalence.
- **Claim level:** theoretical.
- **Claims:** CLAIM-02, CLAIM-03, CLAIM-07.
- **References:** `cunningham_1992_technical_debt`; `li_2015_technical_debt_mapping`; `perez_2022_planning_and_rework`.
- **Evidence link:** [data book](../../data/analysis/paper_support/data_book.md), planning and technical-degradation entries.

### 2.3 AI-assisted software engineering education

- **Purpose:** position AI author concentration as a measurable but incomplete proxy and identify the educational need for process literacy.
- **Claim level:** contextual and interpretive.
- **Claims:** CLAIM-04.
- **References:** `chen_2021_evaluating_code_llms`; `williams_2024_ai_software_engineering_education`.
- **Evidence link:** [argument matrix](argument-matrix.md), CLAIM-04.

### 2.4 Coordination, teamwork, and software engineering skills

- **Purpose:** explain why coordination is theoretically important while acknowledging that the present transcript evidence is sparse and partly unavailable.
- **Claim level:** theoretical, qualified by unavailable evidence.
- **Claims:** CLAIM-05.
- **References:** `brooks_1975_mythical_man_month`; `demarco_lister_1987_peopleware`; `miller_2023_coordination_ai_teams`.
- **Evidence link:** [threats to validity](threats_to_validity.md), transcript and construct-validity sections.

### 2.5 SDD/BDUF as the proposed response

- **Purpose:** define specification-driven or front-loaded design as a methodological proposal for future evaluation.
- **Claim level:** proposed only.
- **Claims:** CLAIM-01 and CLAIM-06 provide motivation; no claim asserts superiority.
- **References:** `agile_manifesto_2001`; `cunningham_1992_technical_debt`; `brooks_1975_mythical_man_month`.
- **Evidence link:** [claim matrix](argument-matrix.md), especially the conditional-go and exploratory-support cautions.

## 3. Method

### 3.1 Educational context, participants, and permitted disclosure

- **Purpose:** describe the course/cohort and team-semester unit without exposing participant, repository, or institution-identifying information.
- **Claim level:** observed methodological description.
- **Claims:** CLAIM-01 context; CLAIM-02 through CLAIM-05 for unit and availability boundaries.
- **Evidence:** [statistical dataset manifest](../../data/analysis/statistical_dataset_manifest.json); [data book](../../data/analysis/paper_support/data_book.md).
- **Privacy rule:** exclude private analytical Parquets, raw prompts, raw transcripts, student identifiers, repository identities, and identifying URLs.

### 3.2 Data sources and evidence hierarchy

- **Purpose:** describe Phase 2.5 reports as interpretive authority, cross-evidence as secondary exploration, and Parquet/CSV/JSON/figure artifacts as verification layers.
- **Claim level:** observed process/method.
- **Evidence:** [phase3 evidence inventory](../../data/analysis/paper_support/phase3_evidence_inventory.md); [data book](../../data/analysis/paper_support/data_book.md).
- **Required statement:** no Phase 2 artifact was regenerated or overwritten for Phase 3.

### 3.3 Units of analysis and temporal cuts

- **Purpose:** make team-semester, team-semester-cut, file-category, student-response, and transcript-session units explicit.
- **Claim level:** observed methodological description.
- **Claims:** CLAIM-02 through CLAIM-07.
- **Evidence:** [data book](../../data/analysis/paper_support/data_book.md); [threats record](threats_to_validity.md).
- **Table candidate:** a compact unit-of-analysis and denominator table, sourced from the data book.

### 3.4 Metrics and operationalization

- **Purpose:** define PI, CC, AI, DeltaDT, and IE as proxies with their transformations, missingness, and exclusions.
- **Claim level:** observed method plus construct qualification.
- **Claims:** CLAIM-02 through CLAIM-05 and CLAIM-07.
- **Evidence:** [argument matrix](argument-matrix.md); [data book](../../data/analysis/paper_support/data_book.md).
- **References:** `li_2015_technical_debt_mapping`; `perez_2022_planning_and_rework`.
- **Required caveat:** PI is not planning quality; CC is not inherently waste; AI is not fully observed tool use; DeltaDT is not all technical debt; IE is not a complete measure of coordination.

### 3.5 Analysis procedure and missingness handling

- **Purpose:** describe primary correlations, the five-analysis boundary, complete-case handling, unavailable zero-variance analysis, and the exploratory cross-evidence layer.
- **Claim level:** observed method.
- **Claims:** CLAIM-02 through CLAIM-07.
- **Evidence:** [correlation results](../../data/analysis/correlation_results.csv); [statistical manifest](../../data/analysis/statistical_dataset_manifest.json); [threats record](threats_to_validity.md).
- **Required statement:** cross-evidence counts are inventory facts, not independent confirmatory tests.

### 3.6 Reproducibility, privacy, and artifact lineage

- **Purpose:** explain report-first reading, numeric verification, sidecars/manifests, anonymization, and the data-availability boundary.
- **Claim level:** observed process/method.
- **Evidence:** [phase3 evidence inventory](../../data/analysis/paper_support/phase3_evidence_inventory.md); [data book](../../data/analysis/paper_support/data_book.md).
- **Privacy check:** paper-facing outputs contain no raw PII or private evidence fields.

## 4. Results

### 4.1 Descriptive dataset profile

- **Purpose:** report the team-semester scope and artifact coverage before interpreting results.
- **Claim level:** observed.
- **Claims:** CLAIM-02 through CLAIM-05.
- **Evidence:** [data book](../../data/analysis/paper_support/data_book.md); [phase3 inventory](../../data/analysis/paper_support/phase3_evidence_inventory.md).
- **Table candidate:** `Table 1`, compact artifact/unit/row-count/availability profile.
- **Required wording:** identify missing and unavailable measures rather than silently excluding them.

### 4.2 Report-first evidence map

- **Purpose:** state what the Phase 2.5 artifact and consolidated reports say before presenting cross-evidence.
- **Claim level:** observed report interpretation, reconciled against structured sources.
- **Claims:** CLAIM-02, CLAIM-03, CLAIM-05, CLAIM-07.
- **Evidence:** [consolidated audit](../../data/analysis/artifact_reports/00_consolidated_audit.md); [argument matrix](argument-matrix.md).
- **Table candidate:** `Table 2`, claim/status/n/verification path/allowed wording.

### 4.3 Planning debt and code churn

- **Purpose:** answer the primary part of RQ1: whether initial planning intensity is statistically associated with later code churn or degradation.
- **Claim level:** observed null result.
- **Claims:** CLAIM-02 and CLAIM-03.
- **Evidence:** [correlation results](../../data/analysis/correlation_results.csv); [planning report](../../data/analysis/artifact_reports/planning_metrics.md); [technical-degradation report](../../data/analysis/artifact_reports/technical_degradation_metrics.md).
- **Figures:** `pi_vs_cc` as supplementary/null-descriptive; `temporal_escalation_panel` as the main descriptive candidate.
- **References:** `cunningham_1992_technical_debt`; `li_2015_technical_debt_mapping`.
- **Caption rule:** every caption states team-semester unit and `n`.

### 4.4 Integration and human-factor evidence

- **Purpose:** answer RQ2 without overstating sparse AI or transcript measures.
- **Claim level:** observed, qualified, or unavailable.
- **Claims:** CLAIM-04 and CLAIM-05.
- **Evidence:** [integration-friction report](../../data/analysis/artifact_reports/integration_friction_metrics.md); [cut-context report](../../data/analysis/artifact_reports/cut_context_metrics.md); [correlation results](../../data/analysis/correlation_results.csv).
- **Figure:** `author_pressure_vs_churn` as an exploratory candidate, with `n = 14` and the relevant complete-case limitation.
- **Required statement:** transcript coordination friction is unavailable for substantive inference where the primary measure has zero variance.

### 4.5 Secondary cross-evidence candidates

- **Purpose:** answer RQ3 with exploratory triangulation while preserving the Phase 2.5 verdict.
- **Claim level:** interpretive/secondary exploratory evidence.
- **Claim:** CLAIM-06.
- **Evidence:** [cross-evidence consolidated report](../../data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md); [semester-stratified results](../../data/analysis/cross_evidence/results/semester_stratified_results.csv); [plot book](../../data/analysis/paper_support/plot_book.md).
- **Figures:** `scope_vs_late_instability`; `author_pressure_vs_churn`.
- **Qualification visuals:** `leave_one_out_robustness`; `file_category_churn_by_cut`.
- **Required statement:** favorable cross-evidence rows are candidate associations, not confirmation; the aggregate `supports` label does not override the primary conditional-go result.

### 4.6 Null, unavailable, and mixed results

- **Purpose:** make non-significant and unavailable evidence visible rather than relegating it to limitations.
- **Claim level:** observed.
- **Claims:** CLAIM-02 through CLAIM-07.
- **Evidence:** [argument matrix](argument-matrix.md); [threats record](threats_to_validity.md).
- **Table candidate:** `Table 3`, primary and secondary result status with n, p-value/status, and interpretation.

## 5. Discussion

### 5.1 Act 1: evolutionary ceiling and educational context

- **Purpose:** interpret the educational motivation without presenting Act 1 as a cross-evidence finding.
- **Claim level:** contextual/interpretive.
- **Claims:** CLAIM-01.
- **Evidence:** [Act 1 report](../../data/analysis/artifact_reports/act_1_evolutionary_ceiling.md); [threats record](threats_to_validity.md).
- **References:** `williams_2024_ai_software_engineering_education`; `chen_2021_evaluating_code_llms`.

### 5.2 Act 2: planning debt as a qualified pattern

- **Purpose:** reconcile descriptive temporal and churn patterns with null primary correlations.
- **Claim level:** observed null plus bounded interpretation.
- **Claims:** CLAIM-02, CLAIM-03, CLAIM-07.
- **Evidence:** [planning report](../../data/analysis/artifact_reports/planning_metrics.md); [technical-degradation report](../../data/analysis/artifact_reports/technical_degradation_metrics.md); [plot book](../../data/analysis/paper_support/plot_book.md).
- **Figures:** `temporal_escalation_panel`; `file_category_churn_by_cut` only as an exclusion warning.
- **References:** `cunningham_1992_technical_debt`; `li_2015_technical_debt_mapping`; `perez_2022_planning_and_rework`.

### 5.3 Act 3: human factor and coordination boundary

- **Purpose:** discuss author concentration as measurable but sparse and coordination friction as unavailable for substantive inference.
- **Claim level:** descriptive/interpretive with explicit limitation.
- **Claims:** CLAIM-04 and CLAIM-05.
- **Evidence:** [integration-friction report](../../data/analysis/artifact_reports/integration_friction_metrics.md); [cut-context report](../../data/analysis/artifact_reports/cut_context_metrics.md); [threats record](threats_to_validity.md).
- **Figure:** `author_pressure_vs_churn` as candidate-level only.
- **References:** `miller_2023_coordination_ai_teams`; `demarco_lister_1987_peopleware`; `brooks_1975_mythical_man_month`.

### 5.4 Act 4: value inversion and methodological proposal

- **Purpose:** frame SDD/BDUF as a proposal motivated by the evidence boundary, not as a demonstrated solution.
- **Claim level:** proposed.
- **Claims:** CLAIM-01 and CLAIM-06 motivate the proposal; no claim establishes superiority.
- **Evidence:** [argument matrix](argument-matrix.md); [threats record](threats_to_validity.md).
- **References:** `agile_manifesto_2001`; `brooks_1975_mythical_man_month`; `cunningham_1992_technical_debt`.
- **Required wording:** future evaluation should test whether explicit specification and coordination practices improve outcomes under AI assistance.

### 5.5 Implications for SE education and training

- **Purpose:** derive actionable teaching implications that do not exceed the evidence.
- **Claim level:** proposed implication.
- **Evidence:** CLAIM-01, CLAIM-04, CLAIM-05, CLAIM-07; [threats record](threats_to_validity.md).
- **References:** `williams_2024_ai_software_engineering_education`; `demarco_lister_1987_peopleware`.
- **Permitted implications:** teach planning artifacts as inspectable reasoning, require explicit coordination checkpoints, and assess AI-supported engineering process rather than generated output alone.
- **Avoid:** claiming these practices have been validated as causal improvements by this study.

## 6. Threats to Validity

### 6.1 Statistical and internal validity

- **Content:** sample size, unevenness, null tests, zero variance, observational design, multiple comparisons, mixed units, non-paired transcripts, and visual/statistical discrepancies.
- **Evidence:** [threats-to-validity record](threats_to_validity.md); [correlation results](../../data/analysis/correlation_results.csv).
- **Claims:** CLAIM-02 through CLAIM-06.

### 6.2 Construct and external validity

- **Content:** PI, CC, AI, DeltaDT, and IE proxy limitations; educational-to-industry transfer; cohort/task dependence.
- **Evidence:** [threats record](threats_to_validity.md); [data book](../../data/analysis/paper_support/data_book.md).
- **Claims:** CLAIM-01, CLAIM-04, CLAIM-05.
- **References:** `li_2015_technical_debt_mapping`; `miller_2023_coordination_ai_teams`; `demarco_lister_1987_peopleware`.

### 6.3 Selection, privacy, and denominator validity

- **Content:** repository survivorship, privacy-driven release restrictions, file-category exclusions, report/source conflicts, and the four exclusion classes.
- **Evidence:** [exclusion manifest](../../data/analysis/statistical_dataset_manifest_exclusions.json); [team metrics exclusions](../../data/analysis/team_metrics_exclusions.json); [threats record](threats_to_validity.md).
- **Claims:** CLAIM-07.

## 7. Conclusion

### 7.1 Answer to the research questions

- **RQ1:** the artifacts show descriptive planning/churn and temporal patterns, but the primary team-semester relationships are not statistically supported.
- **RQ2:** AI author concentration is measurable in a sparse subset; transcript coordination friction is unavailable or too sparse for a substantive claim.
- **RQ3:** cross-evidence identifies exploratory candidate patterns, but multiplicity, exclusions, and fragility prevent confirmation.
- **RQ4:** the evidence supports SDD/BDUF as a proposal for educational and methodological evaluation, not as an established superior solution.

- **Claims:** CLAIM-02 through CLAIM-07.
- **Evidence:** [argument matrix](argument-matrix.md); [threats record](threats_to_validity.md).

### 7.2 Final contribution statement

Close with the paper’s actual contribution: an evidence-constrained characterization and an auditable way to organize mixed, null, and exploratory results for software engineering education research. Repeat the conditional-go boundary once, without introducing a new claim.

## 8. Data Availability

Place this section immediately after the Conclusion, as required by the current plan.

- Release the paper-facing aggregate Parquets, CSVs, JSON manifests, figure data, selected figures, data book, argument matrix, and report references that have passed privacy review.
- Do not release raw prompts, raw transcripts, student identifiers, repository identities, private analytical Parquets, or identifying URLs.
- Explain that reviewers can verify the analysis through persisted aggregate artifacts, sidecars, manifests, report chains, and the reproducibility inventory without receiving restricted raw evidence.
- Link the statement to [phase3 evidence inventory](../../data/analysis/paper_support/phase3_evidence_inventory.md), [data book](../../data/analysis/paper_support/data_book.md), and [threats record](threats_to_validity.md).
- **Privacy status before submission:** run a final double-anonymous and PII scan across all paper-support outputs, figures, metadata, repository history, and external artifact links.

## Traceability checklist before drafting prose

- Every empirical paragraph has one or more claim IDs from [argument-matrix.md](argument-matrix.md).
- Every number is verified in a persisted CSV, JSON, Parquet, manifest, or figure record through [data_book.md](../../data/analysis/paper_support/data_book.md).
- Every selected figure is listed in [selected_figures.json](../../data/analysis/paper_support/selected_figures.json) and explained in [plot_book.md](../../data/analysis/paper_support/plot_book.md).
- Every literature claim uses a key from [references.bib](references.bib) and is mapped in [literature-map.md](literature-map.md) and [reference_matrix.csv](../../data/analysis/paper_support/reference_matrix.csv).
- Every favorable cross-evidence statement carries a secondary-exploratory label and its fragility, multiplicity, and exclusion caveat.
- Acts 1 and 4 remain contextual/proposed; they are not presented as empirically proven by cross-evidence.
- The final draft preserves double anonymity and the Data Availability section after the Conclusion.
