# Threats to validity and treatment of null findings

This record defines the limits that must travel with the Phase 3 manuscript. It is not an argument against the project; it is the boundary that makes the evidence interpretable. The canonical position is conditional-go: the evidence package is sufficient for a bounded manuscript, but it does not establish that specification-driven development, planning intensity, or any related intervention causes better outcomes.

## 1. Evidence boundary and null findings

The primary inferential unit is the team-semester. The current dataset contains `n = 14` team-semester observations. Five primary analyses were tested, and none produced a statistically significant result. This is the central validity boundary and must remain visible in the abstract, Results, Discussion, and conclusion.

The null findings are part of the evidence record. They do not prove that planning, specification, AI use, or coordination has no effect, and they do not support the thesis by themselves. They mean that the current cohort, measures, sample size, missingness pattern, and design did not provide statistically reliable support for the tested relationships.

The principal examples are:

- `pi_vs_cc_primary`: coefficient `-0.006766649524509584`, `p = 0.9816838660605893`, `n = 14`;
- `pi_vs_delta_dt_primary`: coefficient `-0.014709647511909141`, `p = 0.960194880594909`, `n = 14`;
- `ai_vs_cc_primary`: coefficient `0.21428571428571433`, `p = 0.6445115810207203`, `n_valid = 7`, with seven missing observations;
- `context_ie_temporal_primary`: unavailable because of zero variance, with `n_total = 6`, `n_valid = 3`, and three missing observations.

Source chain: `data/analysis/correlation_results.csv`, `data/analysis/artifact_reports/00_consolidated_audit.md`, and the claim-evidence matrix.

## 2. Statistical conclusion validity

### Small and uneven samples

The team-semester sample is small (`n = 14`) and is not necessarily balanced across semesters or teams. The AI-related primary analysis has only seven complete observations. Small samples reduce power, make estimates sensitive to individual observations, and make visual separation look more decisive than it is. Any subgroup or semester-specific pattern must be labeled exploratory.

The paper must report the denominator and missingness beside every result. It must not imply that a non-significant result demonstrates equivalence, and it must not turn a positive coefficient with a large p-value into evidence of an effect.

### Non-significant primary tests

The five-primary-analysis boundary prevents selective emphasis on favorable signs or visually persuasive plots. Primary analyses remain primary even when their results are null. The manuscript should distinguish `not statistically supported` from `no effect`, and `inconclusive` from `negative`.

### Unavailable and zero-variance analyses

The transcript/context analysis is not a weak positive or negative result; it is unavailable for inference because the relevant measure has zero variance and sparse complete observations. A missing p-value cannot be silently converted into a null result. The associated visual may document data availability, but it cannot support a substantive coordination claim.

### Multiple comparisons and secondary multiplicity

The cross-evidence layer contains seven correlations, 21 semester-stratified rows, 24 best/worst contrasts, seven leave-one-out rows, and 18 extreme-case overlap rows. These are not independent confirmatory tests. Their counts must never be presented as a large number of replications. The paper should use them for triangulation, sensitivity, and hypothesis generation, not for post hoc confirmation.

The aggregate cross-evidence verdict may be `supports`, while many component rows are inconclusive and robustness can be fragile. The aggregate label therefore does not override the component-level evidence or the Phase 2.5 conditional-go verdict.

## 3. Internal validity

### Observational and non-causal design

The analyses are observational correlations and descriptive comparisons. They do not establish that planning intensity causes churn, that AI author concentration causes integration friction, or that specification-driven development would improve outcomes. Confounding, reverse causation, cohort composition, task difficulty, team composition, and repository practices remain plausible explanations.

Use terms such as `associated with`, `co-occurs with`, `descriptive pattern`, or `candidate relationship`. Avoid `causes`, `leads to`, `improves`, `reduces`, or `demonstrates superiority` unless a future design provides the relevant identification strategy.

### Multiple granularities

The evidence combines artifacts with different units of analysis: team-semester, team-semester-cut, file-category rows, student responses, transcript sessions, and aggregate temporal panels. These units cannot share one denominator. A result computed over file-category events must not be narrated as if it were computed over the 14 team-semester observations.

### Non-paired transcript evidence

Transcript and textual evidence is sparse, differently structured, and not fully paired with the team-semester metric rows. This prevents a clean individual- or team-level test linking coordination language to churn or planning outcomes. Transcript-derived signals should remain contextual, descriptive, or unavailable where the report records zero variance or incomplete pairing.

### Selection and survivorship effects in repositories

The repository evidence represents the artifacts that were created, retained, parsed, and available under the project’s collection rules. It may omit abandoned work, uncommitted local changes, inaccessible repositories, or teams whose histories do not survive into the analyzed snapshots. Observed churn and planning patterns can therefore reflect repository selection and survivorship rather than the full development process.

## 4. Construct validity

The project’s constructs are operational proxies, not direct observations of the theoretical concepts.

- **PI (planning intensity):** file counts, planning artifacts, or related activity measures may capture volume or visibility rather than planning quality, completeness, or actual cognitive investment.
- **CC (code churn):** changed lines or churn counts capture repository change, not necessarily waste, defect correction, productive iteration, or rework in isolation.
- **AI:** author or commit concentration before T3 is a proxy for AI-associated contribution, not a complete measure of tool use, generated code, assistance quality, or human judgment.
- **DeltaDT:** technical-degradation signals depend on the selected metrics and temporal aggregation; they are not a direct measurement of all technical debt.
- **IE (integration friction):** sparse textual or context-derived indicators cannot establish the full construct of coordination friction, integration difficulty, or teamwork quality.

These construct limitations mean that null findings may reflect weak or incomplete operationalization as well as the absence of a relationship. They also mean that favorable descriptive patterns should not be treated as validation of the constructs themselves.

## 5. External validity and transfer

### Educational setting versus software engineering practice

The observations come from an educational setting. Student teams, course deadlines, instructor scaffolding, assignment constraints, and assessment incentives differ from professional software organizations. The manuscript may discuss implications for software engineering education and training, but it must not generalize the observed patterns directly to industrial teams.

Any connection to professional practice should be presented as a design implication or hypothesis for future study, not as an established transfer result.

### Cohort and task dependence

The cohort, semesters, assignment structure, technology stack, and team composition constrain generalizability. A later cohort or different project type may produce different relationships between planning artifacts, AI assistance, churn, and coordination.

## 6. Data quality, privacy, and reproducibility

### Privacy-driven restrictions

Raw prompts, transcripts, student identifiers, repository identities, and other sensitive material cannot be distributed as unrestricted paper supplements. Anonymization and aggregate reporting protect participants but limit independent reanalysis and can prevent external reviewers from checking every transformation at the raw-record level.

The reproducibility package therefore relies on persisted aggregate artifacts, manifests, report chains, and exclusion records. It must not imply that privacy-preserving release is equivalent to open raw-data access.

### Category-classification exclusions and denominator effects

File-category churn is especially sensitive to classification quality and exclusion rules. The recorded exclusion burden includes:

- unknown file category: `1,436 events / 30 rows`;
- missing line counts: `14,287 events / 67 rows`;
- category warnings: `10,564 events / 33 rows`;
- low-confidence categories: `26,567 events / 35 rows`.

These exclusions can change both the numerator and denominator of category-level summaries. Category churn must therefore be presented as a methodological warning or conditional descriptive result, never as a robust outcome without the exclusion accounting beside it.

### Visual/statistical discrepancies

A plot can show a slope, cluster, temporal escalation, or apparent separation even when the corresponding test is null, unavailable, fragile, or based on a different unit of analysis. Figures are not independent evidence. Every figure must be read with its source report, n, denominator, missingness, statistical status, and caveat.

The selected exploratory figures, especially `scope_vs_late_instability` and `author_pressure_vs_churn`, may illustrate candidate patterns. They cannot upgrade a non-significant primary result or a fragile cross-evidence association into confirmation. The leave-one-out visual is a qualification check, and `file_category_churn_by_cut` is an exclusion-sensitive methodological warning.

## 7. Report and source reconciliation

Phase 2.5 reports are the interpretive entry point, while Parquet, CSV, JSON, and figure manifests provide numeric verification. A report may omit a p-value, summarize an exploratory artifact as `support`, or present a favorable pattern without carrying every caveat that appears in the source manifest. The paper must reconcile such differences rather than choosing the most favorable wording.

The reconciliation rule is:

1. preserve the report’s interpretive role;
2. verify quoted numbers against the persisted source artifact;
3. carry forward missingness, exclusion, and robustness caveats;
4. downgrade a claim when the source cannot support its stronger wording;
5. never use a report-level exploratory label to override the consolidated audit.

This is particularly important for cross-evidence, where an aggregate `supports` label coexists with inconclusive rows and fragile leave-one-out behavior.

## 8. Acts 1 and 4

The cross-evidence act reports do not provide empirical support for Acts 1 and 4. Those acts remain contextual and interpretive: they organize the manuscript’s narrative about the educational setting, the proposed response, and the implications of the evidence. They must not be written as data-proven stages or as outcomes established by the cross-evidence analysis.

## 9. Manuscript handling rules

- Report the conditional-go boundary before discussing exploratory support.
- Put null and unavailable findings in Results, not only in limitations.
- Keep primary, secondary, descriptive, methodological, and contextual evidence visibly separate.
- Put the full caveat beside each favorable cross-evidence claim, not several pages later.
- Treat robustness and exclusion analyses as qualification evidence.
- Do not claim SDD/BDUF superiority; describe it as a proposed response or future research direction.
- Treat the current paper as an empirical characterization and evidence-organization contribution, not a causal intervention study.

## Source record

Primary sources for this document are:

- `data/analysis/correlation_results.csv`
- `data/analysis/statistical_dataset_manifest.json`
- `data/analysis/statistical_dataset_manifest_exclusions.json`
- `data/analysis/team_metrics_exclusions.json`
- `data/analysis/artifact_reports/00_consolidated_audit.md`
- `data/analysis/cross_evidence/reports/00_cross_evidence_consolidated_report.md`
- `data/analysis/cross_evidence/results/semester_stratified_results.csv`
- `data/analysis/cross_evidence/results/leave_one_out_sensitivity.csv`
- `data/analysis/paper_support/argument_matrix.csv`
- `data/analysis/paper_support/plot_book.md`
