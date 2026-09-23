## What it is
The analytical artifact is a dataset with a granularity/unit of analysis at the file level, containing 14 rows. It was produced using the script `05_metric_engine.py` and is based on contract version `code-churn-metrics-v1`.

## How it was built
The dataset was constructed by executing a script that processes code churn metrics from a repository. It aggregates various metrics related to file events, commit churn, and total changes over specified time periods, resulting in a structured dataset suitable for analysis.

## Narrative binding
The narrative act number is 2, which is meant to support or falsify the claim titled "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)."

## What the current data actually shows
- Total rows (n): 14
- cc_binary_file_events_t2: mean = 5.714285714285714, n_valid = 14
- cc_commit_churn_n_missing_t3: mean = 0.0, n_valid = 14
- cc_commit_churn_n_total_t3: mean = 33.714285714285715, n_valid = 14
- cc_commit_churn_n_valid_t3: mean = 33.714285714285715, n_valid = 14
- cc_commit_n_t3: mean = 33.714285714285715, n_valid = 14
- cc_total_t1: mean = 3615.285714285714, n_valid = 14
- cc_total_t3: mean = 964437.9285714285, n_valid = 14

## Contribution assessment
The deterministic verdict is "descriptive_infrastructure." This is justified as the dataset provides descriptive statistics for various metrics, with all key numeric columns having valid counts of 14.

## Known limitations
- No significant tests were conducted, as indicated by the empty tests array.
- The dataset may not generalize beyond the specific repositories analyzed, limiting broader applicability.
