## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of 14 rows. It contains 28 columns and was produced using the script `05_metric_engine.py`. The contract version is `planning-metrics-v1`.

## How it was built
The dataset was constructed by executing a script that processes various planning metrics, aggregating data related to events, file counts, and activity signals over specified timeframes. The resulting data is stored in a parquet format, allowing for efficient querying and analysis.

## Narrative binding
The narrative act number is 2, which is meant to support or falsify the claim titled "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)."

## What the current data actually shows
The dataset includes the following key numeric columns with their respective statistics: 
- `pi_binary_event_count_t3`: n_total = 14, mean = 4.0, median = 2.5
- `pi_deleted_count_t3`: n_total = 14, mean = 12.857142857142858, median = 0.0
- `pi_file_count_t1`: n_total = 14, mean = 2.5714285714285716, median = 2.0
- `pi_line_delta_t1`: n_total = 14, mean = 60.142857142857146, median = 6.5
- `pi_line_delta_t3`: n_total = 14, mean = 10164.57142857143, median = 705.5
- `pi_renamed_count_t3`: n_total = 14, mean = 1.5714285714285714, median = 0.5
- `planning_artifact_activity_t3`: n_total = 14, mean = 89.28571428571429, median = 10.0
- `planning_rework_signal_t2_t3`: n_total = 14, mean = 163.64285714285714, median = 25.0

## Contribution assessment
The deterministic verdict is "descriptive_infrastructure." This is justified as there are no tests conducted, indicating that the data serves primarily to describe the existing infrastructure without providing inferential insights.

## Known limitations
- No tests were conducted to assess the significance of the findings.
- The dataset has a small sample size of 14 rows, which may limit the generalizability of the results.
