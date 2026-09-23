## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of "team_semester". It contains 14 rows and 183 columns. The producer script used to generate this dataset is "05_metric_engine.py", and it is based on contract version "team-metrics-v1".

## How it was built
The dataset was constructed using a script that processes various metrics related to team performance over different semesters. It aggregates data from multiple sources, ensuring that the information is structured in a way that allows for analysis of team dynamics and productivity across specified time periods.

## Narrative binding
The narrative acts associated with this dataset are 2 and 3. These acts are intended to support or falsify the claims related to "A Anatomia da Divida de Planejamento (Diagnosis)" and "O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
The current data shows a total of 14 rows with no missing values for key variables such as "ID_Equipe" and "Semestre". However, the results of the analyses are inconclusive, with all tests returning non-significant results: 
- Analysis ID: pi_vs_cc_primary, Verdict: inconclusive
- Analysis ID: pi_vs_delta_dt_primary, Verdict: inconclusive
- Analysis ID: ai_vs_cc_primary, Verdict: inconclusive
- Analysis ID: pi_high_vs_low_cc_primary, Verdict: inconclusive
- Analysis ID: ai_high_vs_low_cc_primary, Verdict: inconclusive

## Contribution assessment
The overall verdict of the dataset is "inconclusive". This is justified as all tests conducted returned inconclusive results, indicating that no significant relationships or effects were identified within the data.

## Known limitations
The known limitations include:
- Affected rows due to integration friction (7 rows affected).
- Missingness in several variables, including "ai_author_share_iqr_before_t3_window" (7 missing), "ai_author_share_median_before_t3_window" (7 missing), and others.
The exclusions summary indicates that there are no affected rows for code churn, planning, and technical degradation, but there are 14 rows affected by reasons related to unavailable data for integration friction.
