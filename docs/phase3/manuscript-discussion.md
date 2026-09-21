# Manuscript Draft: Discussion, Threats to Validity, Conclusion, and Data Availability

## 5. Discussion

### 5.1 Act 1: Educational context, not empirical verdict

The first act frames a change in the educational environment rather than reporting a tested outcome. Generative-AI-supported programming makes it easier to begin implementation, but easier implementation does not by itself resolve questions of scope, architecture, interfaces, acceptance conditions, or team coordination. This is a relevant design problem for software engineering education because students need to learn how to inspect and justify AI-assisted engineering work, not only how to obtain code from a model [chen_2021_evaluating_code_llms; williams_2024_ai_software_engineering_education].

This framing should not be read as evidence that Agile is obsolete or that empiricism has reached a universal limit. The current Act 1 evidence is contextual and not yet tested. Its role is to motivate the research questions and connect them to software engineering education and training. The study therefore retains the historical value of iterative and collaborative development while asking whether explicit planning artifacts become more important when implementation can be initiated rapidly.

### 5.2 Act 2: Planning debt as a qualified interpretation

The second act provides a useful vocabulary for discussing the relationship between deferred design decisions, repository change, and technical rework. Technical debt literature supports treating deferred work as a tradeoff that can create later maintenance or rework burdens [cunningham_1992_technical_debt; li_2015_technical_debt_mapping]. In the present study, however, planning debt remains a qualified interpretive construct. Planning intensity is measured through observable artifact activity, not through a validated measure of planning quality.

The primary results constrain this interpretation. Initial planning intensity was not statistically associated with later code churn or the selected technical-degradation measure in the team-semester data. These null results do not establish that planning has no value. They indicate that the current proxy, cohort, sample, and observational design did not provide reliable support for the tested relationships. The descriptive temporal patterns and planning-artifact distributions can motivate a future study, but they cannot establish that insufficient planning caused rework or technical degradation.

This distinction also changes the methodological implication. The evidence does not justify replacing Agile with BDUF or asserting that more planning is always better. It does justify asking whether planning artifacts should be evaluated by their quality, consistency, and usefulness for coordination rather than by file count alone. A future study could compare explicit specification practices with alternative process conditions while measuring both the artifact itself and the outcomes it is intended to influence.

### 5.3 Act 3: Human-factor evidence and its boundary

The third act identifies human-factor questions that are important but only partly observable in the current data. Git-derived author concentration is measurable in the available subset, and the exploratory author-pressure visual can help formulate a candidate relationship between concentration and churn. Nevertheless, the primary AI-related analysis has only seven complete observations and is not statistically significant. Author concentration is also an incomplete proxy: it does not identify the quality of collaboration, the reasons for unequal contribution, the actual use of an AI tool, or the judgment applied to generated code.

The transcript/context evidence is even more limited for inference. It is organized by semester and temporal marker rather than by paired team observation, has sparse complete values, and produces an unavailable primary result because of zero variance. This is not evidence of an absence of coordination friction. It is a limit on what the current operationalization can test. The appropriate educational implication is therefore modest: coordination and AI-process literacy remain important teaching targets, but the present data do not establish a coordination mechanism linking author concentration, transcript language, and churn.

The distinction between available and unavailable evidence is itself consequential. A paper that silently converts sparse transcript evidence into a team-level claim would overstate the design. Preserving source-native granularity makes the result less rhetorically dramatic, but more useful for designing the next evaluation.

### 5.4 Act 4: SDD/BDUF as a proposal, not a demonstrated solution

The fourth act turns the evidence boundary into a methodological proposal. Explicit specifications, coordination checkpoints, and validation practices may be reasonable candidates for teaching AI-supported engineering. They should be evaluated as practices that could make reasoning inspectable and integration more tractable, not as a solution already validated by this study.

The current evidence does not show that SDD or BDUF is superior to Agile, that front-loaded design is universally appropriate, or that explicit planning improves outcomes. The defensible claim is narrower: the observed evidence and its limitations motivate comparative research on specification quality, coordination practices, and AI-assisted development processes. Such research should measure not only generated code, but also revision, integration, defects, planning quality, team distribution, and learning outcomes.

### 5.5 Implications for software engineering education and training

Three implications follow without exceeding the evidence. First, planning artifacts can be taught and assessed as inspectable reasoning rather than as document volume. Second, AI-assisted projects can include explicit coordination checkpoints that make interfaces, assumptions, and unresolved decisions visible before late integration. Third, assessment can include the engineering process surrounding AI assistance, including verification, attribution, revision, and integration, rather than evaluating generated output alone.

These are proposed educational implications, not tested effects. They should be presented as design hypotheses for future course studies. A stronger evaluation would compare cohorts or teams under clearly documented process conditions, preserve the relevant source-native units, measure specification quality directly, and define outcome and missingness contracts before analysis.

## 6. Threats to Validity

### 6.1 Statistical and internal validity

The primary team-semester sample contains 14 observations, and the AI-related complete-case subset contains seven. These sample sizes limit power and make estimates sensitive to individual observations. The five primary analyses were not statistically significant, while the transcript/context analysis was unavailable because of zero variance. Accordingly, non-significant must not be written as no effect, and unavailable must not be written as a negative finding.

The design is observational. Confounding, reverse causation, task difficulty, team composition, cohort effects, instructor scaffolding, and repository practices can explain observed patterns. The evidence does not identify a causal effect of planning intensity, AI concentration, or SDD/BDUF. The cross-evidence layer further contains multiple exploratory families: seven correlations, 21 semester-stratified rows, 24 best/worst contrasts, seven leave-one-out rows, and 18 extreme-case overlap rows. These rows are not independent confirmatory replications.

The evidence also combines different granularities: team-semester, team-semester-cut, cut-context, student-response, transcript-session, file-category, and metric-family-cut. The primary team-semester boundary is `n = 14`. A figure-data row count cannot be substituted for that denominator. The visual panels are therefore interpreted together with their source unit, valid n, missingness, and aggregation rule.

### 6.2 Construct validity

PI, CC, AI, DeltaDT, and IE are operational proxies. Planning-file volume may not represent planning quality; churn may reflect productive iteration as well as rework; author concentration is not a complete observation of AI use; technical-degradation measures do not represent all technical debt; and sparse textual/context indicators do not capture the full construct of coordination friction. These limitations mean that a null result can reflect insufficient operationalization as well as the absence of a relationship.

### 6.3 External validity and transfer

The evidence comes from an educational setting with particular teams, tasks, semesters, deadlines, technology, and assessment conditions. Student-team behavior should not be generalized directly to professional software organizations. The paper’s actionable implications are therefore directed to software engineering education and training. Transfer to professional practice remains a future hypothesis.

Repository evidence also has selection and survivorship limits. The analyzed history reflects artifacts that were created, retained, parsed, and available under the project’s collection rules. Abandoned work, uncommitted local changes, inaccessible repositories, or histories that did not survive into snapshots may be absent.

### 6.4 Data quality, privacy, and denominator validity

Transcript evidence is not fully paired with team-semester metrics, and privacy restrictions prevent unrestricted release of raw prompts, transcripts, student identifiers, and repository identities. Aggregate and anonymized release improves participant protection but limits external reanalysis at the raw-record level.

File-category churn has a substantial exclusion burden: unknown file category (`1,436 events / 30 rows`), missing line counts (`14,287 events / 67 rows`), category warnings (`10,564 events / 33 rows`), and low-confidence categories (`26,567 events / 35 rows`). These exclusions can change denominators and therefore make file-category churn a methodological warning rather than an unqualified outcome.

Finally, a visual pattern can disagree with its statistical status because it uses a different unit, a different aggregation, or a different complete-case subset. The paper treats figures as illustrations of questions and patterns, not as independent evidence. The aggregate cross-evidence label `supports` is retained as an inventory fact but does not override the inconclusive and fragile component results or the Phase 2.5 conditional-go verdict.

## 7. Conclusion

This study asked what planning, churn, technical-degradation, AI-concentration, and coordination patterns can be supported by a persisted software engineering education evidence package. The answer is bounded. At the team-semester level, the primary planning/code-churn and planning/technical-degradation relationships were not statistically supported in the current sample. AI-associated author concentration was measurable in a sparse subset but did not support a positive relationship claim. Transcript-based coordination evidence was too sparse and partly unavailable for a substantive inferential claim. Secondary cross-evidence identified candidate patterns and methodological warnings, but multiplicity, exclusions, and sensitivity behavior prevent confirmation.

The paper’s contribution is therefore an evidence-constrained characterization and an auditable organization of mixed, null, unavailable, and exploratory results. In relation to RQ1, the artifacts support descriptive patterns rather than a confirmed planning-debt relationship. Acts 1 and 4 remain contextual and proposed, respectively: SDD/BDUF is a proposed direction for future educational and methodological evaluation, not an experimentally established superior solution. A next study should enlarge the cohort, measure specification quality directly, preserve native source granularities, improve pairing where ethically and technically possible, and compare process conditions under a design capable of supporting causal interpretation.

## 8. Data Availability

The paper-facing release should include the aggregate or anonymized artifacts that pass final privacy review: selected Parquet/CSV/JSON outputs, statistical and figure manifests, figure data and selected figures, report references, the data book, argument matrix, and reproducibility documentation. Raw prompts, raw transcripts, student identifiers, repository identities, private analytical Parquets, and identifying URLs should not be released as unrestricted supplements.

Reviewers can verify the reported analysis through persisted aggregate artifacts, metadata sidecars, producer contracts, exclusion manifests, report chains, and the Phase 3 evidence inventory. This arrangement supports artifact lineage and denominator verification without implying that privacy-preserving release is equivalent to unrestricted raw-data access. The final package must undergo a separate double-anonymous and PII audit across files, figure metadata, repository history, and external links before submission.

## Discussion traceability controls

- Claims: CLAIM-01 through CLAIM-07 in the [argument matrix](../../data/analysis/paper_support/argument_matrix.csv).
- Validity record: [threats to validity](threats_to_validity.md).
- Act packages: [Act 1](../../data/analysis/paper_support/acts/act_1_context/index.md), [Act 2](../../data/analysis/paper_support/acts/act_2_planning_debt/index.md), [Act 3](../../data/analysis/paper_support/acts/act_3_human_factor/index.md), and [Act 4](../../data/analysis/paper_support/acts/act_4_value_inversion/index.md).
- Literature mapping: [literature map](literature-map.md) and [reference matrix](../../data/analysis/paper_support/reference_matrix.csv).
- Evidence inventory: [Phase 3 data book](../../data/analysis/paper_support/data_book.md) and [Phase 3 inventory](../../data/analysis/paper_support/phase3_evidence_inventory.md).
- Status: draft for Task 4.4; final integration, citation formatting, and venue-specific page review remain.
