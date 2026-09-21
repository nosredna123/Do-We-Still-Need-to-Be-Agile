# Literature map for the Phase 3 manuscript

This literature map is intentionally evidence-constrained. It helps explain the observed patterns and the manuscript framing, but it does not treat any cited paper as proof of the current dataset’s results.

## 1) Contextual references

These sources situate the study in software engineering education and AI-supported programming.

- `agile_manifesto_2001` — frames the commitment to iterative, people-centered, and adaptive delivery; useful for positioning the project’s planning and specification emphasis in a software-engineering education context.
- `chen_2021_evaluating_code_llms` — establishes the technical and educational relevance of large language models as programming support tools, while also emphasizing that model support is not equivalent to a validated engineering process.
- `williams_2024_ai_software_engineering_education` — contextualizes AI in software engineering education and motivates the design of explicit planning and coordination signals.

## 2) Theoretical references

These references ground the core constructs that the manuscript is allowed to discuss: planning debt, rework, coordination, and technical debt.

- `cunningham_1992_technical_debt` — the origin of the technical debt concept and the key source for interpreting deferral and rework as a software engineering tradeoff.
- `li_2015_technical_debt_mapping` — systematic review framing that helps connect debt, rework, and code-quality consequences to a broader software engineering literature.
- `brooks_1975_mythical_man_month` — classic theoretical anchor for coordination cost, communication overhead, and the risk of productivity illusions in team work.
- `demarco_lister_1987_peopleware` — supports the educational and team-level framing that human coordination and project environment matter at least as much as raw tool capability.

## 3) Methodological references

These references support the measurement and narrow interpretation strategy used in the manuscript.

- `perez_2022_planning_and_rework` — useful for the method narrative on planning quality, rework, and project-based learning, especially when the paper distinguishes descriptive patterns from formal causal inference.
- `li_2015_technical_debt_mapping` — also serves the methodology discussion by highlighting the need to interpret software-engineering signals with recognition of scope, missingness, and operationalization tradeoffs.

## 4) Empirical external references

These are useful as external comparison points for framing the study without claiming they prove the current dataset’s result.

- `miller_2023_coordination_ai_teams` — helps situate coordination and team dynamics in AI-assisted collaborative settings.
- `perez_2022_planning_and_rework` — provides a comparable educational or team-level lens on planning and rework, which helps explain the current evidence without equating it with equivalent outcomes.

## 5) Pedagogical references

These references connect the paper to software engineering education and training audiences.

- `demarco_lister_1987_peopleware` — classic pedagogical text for team productivity and engineering practice.
- `williams_2024_ai_software_engineering_education` — explicitly speaks to the SEET audience and the need to teach coordination, process discipline, and AI-aware engineering practice.

## 6) Counterpoint references

These are used to bound or qualify the forecasting story.

- `brooks_1975_mythical_man_month` — a counterpoint to scaling claims and heroic productivity assumptions; it keeps the manuscript honest about coordination limits and complexity.
- `chen_2021_evaluating_code_llms` — useful as a counterpoint to over-optimistic claims about AI-generated value, since it shows capability gains without implying a guaranteed process improvement in a small course cohort.

## 7) Claim-to-reference mapping at a glance

| claim_id | dominant references | role |
| --- | --- | --- |
| CLAIM-01 | `agile_manifesto_2001`, `williams_2024_ai_software_engineering_education` | contextual |
| CLAIM-02 | `cunningham_1992_technical_debt`, `li_2015_technical_debt_mapping` | theoretical / methodological |
| CLAIM-03 | `cunningham_1992_technical_debt`, `li_2015_technical_debt_mapping` | theoretical / methodological |
| CLAIM-04 | `chen_2021_evaluating_code_llms`, `miller_2023_coordination_ai_teams` | contextual / qualifies |
| CLAIM-05 | `brooks_1975_mythical_man_month`, `demarco_lister_1987_peopleware` | theoretical / counterpoint |
| CLAIM-06 | `agile_manifesto_2001`, `li_2015_technical_debt_mapping` | contextual / qualifies |
| CLAIM-07 | `cunningham_1992_technical_debt`, `li_2015_technical_debt_mapping` | methodological / qualification |

## Interpretation rule

The manuscript may use these sources to explain the project, motivate the question, or qualify the evidence. It must not present any cited work as direct empirical proof of the current team-semester findings.
