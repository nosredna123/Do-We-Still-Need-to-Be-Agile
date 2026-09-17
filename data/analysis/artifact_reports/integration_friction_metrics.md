## What it is
The analytical artifact is a dataset with a granularity/unit of analysis at the level of individual observations. It contains 14 rows and 61 columns. The producer script used to generate this dataset is `05_metric_engine.py`, and it is based on contract version `integration-friction-metrics-v1`.

## How it was built
The dataset was constructed using a script that processes various metrics related to integration friction. It aggregates data points from multiple sources, ensuring that the resulting dataset captures relevant metrics for analysis. The focus is on key performance indicators that reflect the behavior and performance of AI authors over specified time windows.

## Narrative binding
The narrative act number is 3, which is meant to support the claim titled "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)."

## What the current data actually shows
- n_total: 14
- ai_author_n_before_t3_window: mean = 1.8571428571428572, n_valid = 14
- ai_author_share_n_missing_t2: mean = 0.0, n_valid = 14
- ai_author_share_n_missing_t3: mean = 0.0, n_valid = 14
- ai_author_share_n_valid_before_t3_window: mean = 1.8571428571428572, n_valid = 14
- ai_churn_before_t3_window: mean = 5150.571428571428, n_valid = 14
- ai_commit_n_before_t3_window: mean = 10.214285714285714, n_valid = 14
- ai_commit_n_t1: mean = 7.928571428571429, n_valid = 14
- ai_gini_t3: mean = 0.2473397745718178, n_valid = 14

## Contribution assessment
The deterministic verdict is "descriptive_infrastructure." This is justified as the dataset provides descriptive statistics for various metrics, but no inferential tests were conducted, as indicated by the absence of tests in the verdict summary.

## Known limitations
- No inferential statistics were performed.
- The dataset is limited to 14 observations, which may not provide a comprehensive view of the phenomena being studied.
