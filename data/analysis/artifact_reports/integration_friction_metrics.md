## What it is
The granularity/unit of analysis for this artifact is at the level of individual metrics. The dataset contains 14 rows. The producer script used to generate this artifact is `05_metric_engine.py`, and the contract version is `integration-friction-metrics-v1`.

## How it was built
This analytical artifact was constructed using a script that processes various metrics related to integration friction. The script aggregates data from multiple sources, calculating key performance indicators such as author contributions and churn rates over specified time windows. The resulting dataset is stored in a parquet format, allowing for efficient querying and analysis.

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
The deterministic verdict is "descriptive_infrastructure." This is justified as all key metrics have valid counts (n_valid = 14) and provide descriptive statistics without any significant tests or results to indicate a different conclusion.

## Known limitations
- No significant tests were conducted.
- All metrics are based on a small sample size (n = 14).
- There is no indication of variability or significance in the results.
