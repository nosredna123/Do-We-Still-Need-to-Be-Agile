## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of "team_semester". It contains 14 rows and 183 columns. The producer script used to generate this dataset is "05_metric_engine.py", and it is based on contract version "team-metrics-v1".

## How it was built
The dataset was constructed using a script that processes various metrics related to team performance over different semesters. It aggregates data from multiple sources, ensuring that the information is structured in a way that allows for analysis of team dynamics and productivity across specified time periods.

## Narrative binding
The narrative acts associated with this dataset are 2 and 3. These acts are intended to support or falsify the claims related to "A Anatomia da Divida de Planejamento (Diagnosis)" and "O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
The current data shows a total of 14 rows with no missing values for most variables. However, there are missing values for some variables: 7 missing for "ai_author_share_iqr_before_t3_window", 5 for "ai_author_share_iqr_t1", 4 for "ai_author_share_iqr_t2", 7 for "ai_author_share_median_before_t3_window", 5 for "ai_author_share_median_t1", 4 for "ai_author_share_median_t2", 7 for "ai_gini_before_t3_window", 5 for "ai_gini_t1", 4 for "ai_gini_t2", 7 for "ai_max_author_share_before_t3_window", 5 for "ai_max_author_share_t1", 4 for "ai_max_author_share_t2", 5 for "cc_commit_churn_mode_n_t1", 4 for "cc_commit_churn_mode_n_t2", 5 for "cc_commit_churn_mode_share_t1", 4 for "cc_commit_churn_mode_share_t2", 5 for "cc_mean_per_commit_t1", 4 for "cc_median_per_commit_t1", 7 for "repo_source_loc_t1", 4 for "repo_source_loc_t2", and 14 missing for "ai_ref_unavailable_reason_t1", "ai_ref_unavailable_reason_t2", "ai_ref_unavailable_reason_t3", "pi_unavailable_reason", "planning_rework_unavailable_reason", and "pi_unavailable_reason".

## Contribution assessment
The overall verdict of the analysis is "inconclusive". This is justified as all tests conducted, including correlations and hypotheses, returned inconclusive results.

## Known limitations
The known limitations include:
- Missing values for several variables.
- The overall analysis yielded inconclusive results across all tests.
- The dataset is limited to 14 rows, which may not provide a comprehensive view of the metrics being analyzed. 

The exclusions summary indicates that there were no affected rows for code churn and planning, but there were 7 affected rows for integration friction due to "one_or_more_cut_concentration_unavailable".
