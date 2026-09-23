## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of 14 rows. It was produced using the script `05_metric_engine.py` and is in contract version `integration-friction-metrics-v1`. The dataset contains 61 columns.

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
The deterministic verdict is "descriptive_infrastructure." This is justified as all metrics are based on a valid sample size of 14, providing descriptive statistics without any tests indicating significant relationships or effects.

## Known limitations
- No tests were conducted to assess significance.
- All metrics are based on a small sample size of 14.
- There is no missing data, but the lack of variability in some metrics may limit insights.
