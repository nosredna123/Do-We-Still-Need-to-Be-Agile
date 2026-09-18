## What it is
The analytical artifact is a dataset with a granularity/unit of analysis at the technical degradation metrics level. It contains 14 rows and 24 columns. The producer script used to generate this dataset is `05_metric_engine.py`, and it is based on contract version `technical-degradation-metrics-v1`.

## How it was built
The dataset was constructed using a script that processes various technical metrics related to degradation over time. It aggregates data points from multiple sources, ensuring that the metrics reflect changes in technical complexity and performance across different time intervals.

## Narrative binding
The narrative acts associated with this dataset are 2 and 3. Act 2 supports the claim regarding the diagnosis of planning debt, while Act 3 provides evidence related to the human factor and the illusion of progress.

## What the current data actually shows
The dataset includes the following key statistics:
- For `delta_dt_t1_t2`: n_total = 14, n_valid = 14, mean = -0.014880952380952392, p-value = unavailable.
- For `delta_dt_t2_t3`: n_total = 14, n_valid = 14, mean = 0.22619047619047622, p-value = unavailable.
- For `technical_complexity_mean_t1`: n_total = 14, n_valid = 14, mean = 1.625, p-value = unavailable.
- For `technical_complexity_mean_t2`: n_total = 14, n_valid = 14, mean = 1.6101190476190477, p-value = unavailable.
- For `technical_complexity_n_t1`: n_total = 14, n_valid = 14, mean = 3.642857142857143, p-value = unavailable.
- For `technical_complexity_n_t2`: n_total = 14, n_valid = 14, mean = 3.642857142857143, p-value = unavailable.
- For `technical_complexity_n_t3`: n_total = 14, n_valid = 14, mean = 3.2142857142857144, p-value = unavailable.
- For `technical_complexity_std_t3`: n_total = 14, n_valid = 14, mean = 0.17728934339777694, p-value = unavailable.

## Contribution assessment
The deterministic verdict for this dataset is "descriptive_infrastructure." This is justified as there are no statistical tests conducted, and all metrics are descriptive in nature, with no significant results reported.

## Known limitations
- No statistical tests were performed.
- All p-values are unavailable.
- The dataset has a small sample size of 14 rows.
