## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of 14 rows. It contains 28 columns and was produced using the script `05_metric_engine.py`. The contract version is `planning-metrics-v1`.

## How it was built
The dataset was constructed by executing a script that processes various planning metrics, aggregating data related to events, file counts, and other relevant metrics over specified timeframes. The resulting data is stored in a parquet format, which allows for efficient querying and analysis.

## Narrative binding
The narrative act number is 2, which is meant to support or falsify the claim titled "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)."

## What the current data actually shows
The dataset includes the following key numeric columns with their respective statistics: 
- `pi_binary_event_count_t3`: n = 14, mean = 4.0, p-value = unavailable
- `pi_deleted_count_t3`: n = 14, mean = 12.857142857142858, p-value = unavailable
- `pi_file_count_t1`: n = 14, mean = 2.5714285714285716, p-value = unavailable
- `pi_line_delta_t1`: n = 14, mean = 60.142857142857146, p-value = unavailable
- `pi_line_delta_t3`: n = 14, mean = 10164.57142857143, p-value = unavailable
- `pi_renamed_count_t3`: n = 14, mean = 1.5714285714285714, p-value = unavailable
- `planning_artifact_activity_t3`: n = 14, mean = 89.28571428571429, p-value = unavailable
- `planning_rework_signal_t2_t3`: n = 14, mean = 163.64285714285714, p-value = unavailable

All columns have a total of 14 valid entries, with no missingness reported.

## Contribution assessment
The deterministic verdict is "descriptive_infrastructure." This is justified as there are no statistical tests conducted, and the dataset primarily provides descriptive statistics without inferential claims.

## Known limitations
- No statistical tests were performed.
- The p-values for all key metrics are unavailable.
