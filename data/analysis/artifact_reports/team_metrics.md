## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of "team_semester". It contains 14 rows and 183 columns. The producer script used to generate this dataset is "05_metric_engine.py", and it adheres to contract version "team-metrics-v1".

## How it was built
The dataset was constructed using a script that processes various metrics related to team performance over different semesters. It aggregates data from multiple sources, ensuring that the information is structured in a way that allows for analysis of team dynamics and productivity across specified time periods.

## Narrative binding
The narrative acts associated with this dataset are 2 and 3. These acts are intended to support or falsify the claims related to "A Anatomia da Divida de Planejamento (Diagnosis)" and "O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
The current data shows a total of 14 rows with no missing values for key variables such as "ID_Equipe" and "Semestre". However, the results of the analyses are as follows: 
- For the analysis "pi_vs_cc_primary", the verdict is "inconclusive".
- For the analysis "pi_vs_delta_dt_primary", the verdict is "inconclusive".
- For the analysis "ai_vs_cc_primary", the verdict is "inconclusive".
- For the analysis "pi_high_vs_low_cc_primary", the verdict is "inconclusive".
- For the analysis "ai_high_vs_low_cc_primary", the verdict is "inconclusive".

## Contribution assessment
The overall contribution assessment is "inconclusive". This is justified as all tests conducted, including correlation and hypothesis tests, returned inconclusive results.

## Known limitations
The known limitations include:
- Affected rows in the "integration_friction" source due to "one_or_more_cut_concentration_unavailable".
- Exclusions summary indicates that there are 0 affected rows for "code_churn", "planning", and "technical_degradation", but 7 affected rows for "integration_friction".
