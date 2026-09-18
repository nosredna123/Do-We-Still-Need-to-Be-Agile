## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of "cut_context". It contains 6 rows and 355 columns. The producer script used to generate this dataset is "05_metric_engine.py", and it adheres to the contract version "cut-context-metrics-v1".

## How it was built
The dataset was constructed using a script that processes various metrics related to cut contexts. It aggregates data across different semesters and temporal markers, ensuring that all relevant variables are captured. The data is stored in a parquet format, which allows for efficient querying and analysis.

## Narrative binding
The narrative act number is 3, which is meant to support or falsify the claim associated with "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
The dataset contains 6 rows, with the following missingness: 3 missing values for the columns "ie_transcript_coordination_friction_score_iqr", "ie_transcript_coordination_friction_score_mean", "ie_transcript_coordination_friction_score_median", and others. The overall verdict from the analysis is "unavailable", with specific tests also yielding "unavailable" results.

## Contribution assessment
The deterministic verdict is "unavailable". This is justified as all analyses conducted on the dataset returned results that were classified as "unavailable".

## Known limitations
- All analyses returned "unavailable" results.
- The dataset has missing values in several columns, specifically 3 missing values in multiple metrics.
