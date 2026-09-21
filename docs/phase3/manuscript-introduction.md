# Manuscript Draft: Introduction

## 1. Introduction

Generative AI is changing how software can be produced in educational settings. Students can obtain implementation suggestions, revise code, and explore design alternatives at a speed that changes the relationship between planning and construction. This development creates an important software engineering education question: when implementation becomes easier to initiate, how should teams make their intended system, dependencies, and coordination obligations explicit? The question is educational as well as technical. Students must learn not only to produce code with AI assistance, but also to inspect, integrate, and justify the engineering process that produced it [chen_2021_evaluating_code_llms; williams_2024_ai_software_engineering_education].

The Agile Manifesto established a productive reaction against heavyweight processes that could delay feedback and obscure working software [agile_manifesto_2001]. Its emphasis on iteration, collaboration, and adaptation remains a useful point of departure for software engineering education. However, AI-assisted programming may alter the cost profile of early implementation without removing the complexity of system-level decisions. A team can generate or modify code quickly while still lacking a shared account of scope, architecture, interfaces, or acceptance conditions. In that setting, planning is not simply the opposite of agility. It becomes an empirical question whether the planning artifacts available to a team are sufficient to guide distributed work and later integration.

This paper studies that question in a software engineering education setting using persisted repository, planning, technical-degradation, integration, and textual artifacts. We use the term *planning debt* as a qualified interpretive construct for the burden that may arise when important design and coordination decisions remain implicit or are deferred into implementation. The construct is related to, but not identical with, technical debt and rework [cunningham_1992_technical_debt; li_2015_technical_debt_mapping]. In this study, planning intensity is operationalized through observable artifact activity and should not be read as planning quality. Similarly, code churn is an observable change signal, not a direct measure of waste, and AI-associated author concentration is a proxy rather than a complete measure of tool use or assistance quality.

The evidence does not support a confirmatory version of the central thesis. The primary unit is the team-semester, with 14 observations. Five primary analyses were tested, and none produced a statistically significant result. The resulting Phase 2.5 audit is `conditional-go`: the data support a bounded paper about descriptive patterns, evidence organization, and exploratory hypotheses, but they do not establish that insufficient planning causes churn, coordination friction, or technical degradation. Some secondary cross-evidence results identify candidate patterns; these analyses remain exploratory and cannot replace the primary verdict. The distinction matters because a visually suggestive pattern, a positive coefficient, or an aggregate `supports` label is not equivalent to confirmatory evidence.

The paper therefore treats its four narrative acts as an organizing structure rather than as four empirically demonstrated stages. Act 1 frames the educational and generative-AI context. Act 2 examines planning, churn, and technical-degradation signals. Act 3 considers AI-associated author concentration and the limits of transcript-based coordination evidence. Act 4 treats specification-driven development (SDD) and Big Design Up Front (BDUF) as methodological proposals for future evaluation, not as experimentally validated solutions. This framing preserves the motivating concern while allowing null, unavailable, and mixed findings to remain visible.

### 1.1 Research questions

The study addresses four questions:

- **RQ1:** What planning, churn, technical-degradation, and temporal patterns are observable in the team-semester evidence?
- **RQ2:** What evidence is available, unavailable, or too sparse to characterize AI-related author concentration and coordination friction?
- **RQ3:** Which secondary cross-evidence patterns are worth carrying forward as bounded hypotheses, and how robust are they to multiplicity, exclusions, and sensitivity checks?
- **RQ4:** What implications for software engineering education and training can be proposed without claiming that SDD/BDUF has been experimentally validated?

These questions deliberately separate observation from interpretation and proposal. RQ1 and RQ2 concern what the persisted artifacts can show at their supported granularities. RQ3 concerns candidate relationships that require future testing rather than confirmation in this cohort. RQ4 concerns educational implications that remain defensible after the statistical and construct-validity limits are taken into account.

### 1.2 Contributions

This paper makes three bounded contributions. First, it provides an empirical characterization of planning, code-change, technical-degradation, and human-factor signals in an AI-supported software engineering education cohort. Second, it provides an auditable evidence organization that connects Phase 2.5 reports, structured sources, figures, denominators, exclusions, and validity qualifications. Third, it derives methodological implications for teaching explicit planning, coordination, and AI-supported engineering practice without claiming that any particular process has been shown to cause better outcomes.

The paper's central contribution is consequently not proof of SDD/BDUF superiority. It is a disciplined account of what this evidence can support now, what remains exploratory, and what a stronger future evaluation would need to measure.

## Drafting controls

- Evidence authority: [Act 1 package](../../data/analysis/paper_support/acts/act_1_context/index.md), [CLAIM-01](../../data/analysis/paper_support/argument_matrix.csv), and [Act 1 report](../../data/analysis/artifact_reports/act_1_evolutionary_ceiling.md).
- Boundary verification: [consolidated audit](../../data/analysis/artifact_reports/00_consolidated_audit.md) and [threats to validity](threats_to_validity.md).
- Literature mapping: [literature map](literature-map.md) and [reference matrix](../../data/analysis/paper_support/reference_matrix.csv).
- Planned space: approximately 0.75 page for the Introduction, with the research questions and contributions kept compact; Background and Related Work remains a separate drafting task.
- Status: draft for Task 4.1; citations and venue formatting require later bibliography verification.
