## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of "team_semester". It contains 14 rows and 183 columns. The producer script used to generate this dataset is "05_metric_engine.py", and it is based on contract version "team-metrics-v1".

## How it was built
The dataset was constructed using a script that processes various metrics related to team performance over different semesters. It aggregates data from multiple sources, ensuring that the information is structured in a way that allows for analysis of team dynamics and productivity across specified time periods.

## Narrative binding
The narrative acts associated with this dataset are 2 and 3. These acts are intended to support or falsify the claims related to "A Anatomia da Divida de Planejamento (Diagnosis)" and "O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
The current data shows a total of 14 observations. All variables have some degree of missingness, with the following specifics: 
- 7 missing values for "ai_author_share_iqr_before_t3_window"
- 5 missing values for "ai_author_share_iqr_t1"
- 4 missing values for "ai_author_share_iqr_t2"
- 7 missing values for "ai_author_share_median_before_t3_window"
- 5 missing values for "ai_author_share_median_t1"
- 4 missing values for "ai_author_share_median_t2"
- 14 missing values for "ai_ref_unavailable_reason_t1", "ai_ref_unavailable_reason_t2", "ai_ref_unavailable_reason_t3", and "pi_unavailable_reason".

All other variables have complete data. The results of the analyses conducted are inconclusive, with no significant correlations or hypotheses being supported.

## Contribution assessment
The overall verdict of the analyses is "inconclusive". This is justified as all tests, including correlations and hypotheses, returned inconclusive results, indicating that no definitive conclusions can be drawn from the current dataset.

## Known limitations
The known limitations include:
- Missing values in several key metrics.
- Inconclusive results across all analyses conducted.
The exclusions summary indicates that there were no affected rows for code churn and planning, but there were 7 affected rows for integration friction due to "one_or_more_cut_concentration_unavailable".
