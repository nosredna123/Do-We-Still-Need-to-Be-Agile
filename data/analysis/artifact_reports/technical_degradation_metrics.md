## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of 14 rows. It was produced using the script `05_metric_engine.py` and is in contract version `technical-degradation-metrics-v1`.

## How it was built
The dataset was constructed by processing technical degradation metrics through a defined script, which likely involved aggregating and calculating various technical complexity measures across different time points. The resulting data is stored in a parquet format, allowing for efficient querying and analysis.

## Narrative binding
The narrative acts associated with this artifact are 2 and 3. Act 2 supports the claim regarding the diagnosis of planning debt, while Act 3 provides evidence related to the human factor and the illusion of progress.

## What the current data actually shows
The dataset contains the following key statistics:
- For `delta_dt_t1_t2`: n_total = 14, n_valid = 14, mean = -0.014880952380952392, median = 0.0, min = -0.5, max = 0.75.
- For `delta_dt_t2_t3`: n_total = 14, n_valid = 14, mean = 0.22619047619047622, median = 0.1875, min = -0.125, max = 0.9999999999999999.
- For `technical_complexity_mean_t1`: n_total = 14, n_valid = 14, mean = 1.625, median = 1.7083333333333335, min = 1.0, max = 2.0.
- For `technical_complexity_mean_t2`: n_total = 14, n_valid = 14, mean = 1.6101190476190477, median = 1.6875, min = 0.8333333333333334, max = 2.0.
- For `technical_complexity_n_t1`: n_total = 14, n_valid = 14, mean = 3.642857142857143, median = 4.0, min = 3.0, max = 4.0.
- For `technical_complexity_n_t2`: n_total = 14, n_valid = 14, mean = 3.642857142857143, median = 4.0, min = 3.0, max = 4.0.
- For `technical_complexity_n_t3`: n_total = 14, n_valid = 14, mean = 3.2142857142857144, median = 3.0, min = 2.0, max = 4.0.
- For `technical_complexity_std_t3`: n_total = 14, n_valid = 14, mean = 0.17728934339777694, median = 0.25, min = 0.0, max = 0.5773502691896257.

## Contribution assessment
The deterministic verdict for this dataset is "descriptive_infrastructure." This is justified as there are no tests conducted, indicating that the data serves primarily to describe the infrastructure rather than to support or falsify specific claims.

## Known limitations
The limitations of this dataset include:
- No tests conducted.
- The dataset contains only 14 rows, which may limit the generalizability of the findings.
