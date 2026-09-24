## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of "cut_context". It contains 6 rows and 355 columns. The producer script used to generate this dataset is "05_metric_engine.py", and it adheres to the contract version "cut-context-metrics-v1".

## How it was built
The dataset was constructed using a script that processes various metrics related to cut contexts. It aggregates data across different semesters and temporal markers, ensuring that the resulting dataset captures relevant metrics for analysis. The data is stored in a parquet format, which allows for efficient querying and storage.

## Narrative binding
The narrative act number is 3, which is meant to support the claim titled "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
The dataset contains 6 rows. There are 3 missing values in the following columns: "ie_transcript_coordination_friction_score_iqr", "ie_transcript_coordination_friction_score_mean", and "ie_transcript_coordination_friction_score_median". The analysis verdicts are as follows: the correlation analysis (context_ie_temporal_primary) supports the claim, while the hypothesis analysis (context_ie_high_vs_low_rework_primary) is unavailable.

## Contribution assessment
The deterministic verdict is "supports_partially". This is justified by the correlation analysis supporting the claim while the hypothesis analysis is unavailable, indicating that not all aspects of the claim are substantiated by the data.

## Known limitations
- The hypothesis analysis (context_ie_high_vs_low_rework_primary) is unavailable.
- There are missing values in key metrics, specifically in the coordination friction score columns.
