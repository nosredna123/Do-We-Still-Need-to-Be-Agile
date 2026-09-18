## What it is
The granularity/unit of analysis for this artifact is at the level of individual metrics. The dataset contains 14 rows and 61 columns. The producer script used to generate this artifact is `05_metric_engine.py`, and the contract version is `integration-friction-metrics-v1`.

## How it was built
This analytical artifact was constructed using a script that processes various metrics related to integration friction. The script aggregates data from multiple sources, ensuring that the resulting dataset captures key performance indicators relevant to the analysis of integration processes.

## Narrative binding
The narrative act number is 3, which is meant to support the claim titled "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)."

## What the current data actually shows
The current data shows the following key statistics: 
- ai_author_n_before_t3_window: n = 14, mean = 1.8571428571428572, median = 1.0, min = 0.0, max = 5.0
- ai_author_share_n_missing_t2: n = 14, mean = 0.0, median = 0.0, min = 0.0, max = 0.0
- ai_author_share_n_missing_t3: n = 14, mean = 0.0, median = 0.0, min = 0.0, max = 0.0
- ai_author_share_n_valid_before_t3_window: n = 14, mean = 1.8571428571428572, median = 1.0, min = 0.0, max = 5.0
- ai_churn_before_t3_window: n = 14, mean = 5150.571428571428, median = 187.5, min = 0.0, max = 31713.0
- ai_commit_n_before_t3_window: n = 14, mean = 10.214285714285714, median = 3.0, min = 0.0, max = 51.0
- ai_commit_n_t1: n = 14, mean = 7.928571428571429, median = 4.0, min = 0.0, max = 40.0
- ai_gini_t3: n = 14, mean = 0.2473397745718178, median = 0.2055322128851541, min = 0.0, max = 0.5302325581395348

## Contribution assessment
The deterministic verdict for this artifact is "descriptive_infrastructure." This is justified as there are no tests conducted, indicating that the data serves primarily to describe the existing infrastructure rather than to provide inferential insights.

## Known limitations
- No tests were conducted to validate the findings.
- The dataset is limited to 14 rows, which may not provide a comprehensive view of the integration friction metrics.
- All key numeric columns have a total of 14 valid entries, indicating no missing data, but the small sample size may limit generalizability.
