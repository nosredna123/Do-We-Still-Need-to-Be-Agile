## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of 14 rows. It contains 61 columns and was produced using the script `05_metric_engine.py`. The contract version is `integration-friction-metrics-v1`.

## How it was built
The dataset was constructed by executing a script that processes various metrics related to integration friction. It aggregates data points from multiple sources to provide insights into the performance and behavior of AI authors over specified time windows.

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
The deterministic verdict is "descriptive_infrastructure." This is justified as all metrics are based on a total of 14 valid observations, indicating that the dataset provides descriptive statistics without any inferential tests.

## Known limitations
- No inferential statistics were conducted.
- The dataset is limited to 14 rows, which may not provide a comprehensive view of the subject matter.
- All key numeric columns have a maximum of 14 valid entries, indicating potential issues with generalizability.
