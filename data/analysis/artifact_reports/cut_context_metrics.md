## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of "cut_context". It contains 6 rows and 355 columns. The producer script used to generate this dataset is "05_metric_engine.py", and it adheres to the contract version "cut-context-metrics-v1".

## How it was built
The dataset was constructed using a script that processes various metrics related to cut contexts. It aggregates data across different semesters and temporal markers, ensuring that all relevant variables are captured. The data is stored in a parquet format, which allows for efficient querying and analysis.

## Narrative binding
The narrative act number is 3, which is meant to support the claim titled "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
The dataset contains 6 rows. There are no missing values for the variables "Semestre", "ie_definition_version", "ie_transcript_available", and others, but there are 3 missing values for the following variables: "ie_transcript_coordination_friction_score_iqr", "ie_transcript_coordination_friction_score_mean", "ie_transcript_coordination_friction_score_median", and several others. The overall verdict for the analyses conducted is "unavailable", with specific tests also yielding "unavailable" results.

## Contribution assessment
The deterministic verdict is "unavailable". This is justified as all analyses conducted, including "context_ie_temporal_primary" and "context_ie_high_vs_low_rework_primary", returned results that were classified as "unavailable".

## Known limitations
- All analyses returned results classified as "unavailable".
- The dataset has 3 missing values for several key variables, which may affect the reliability of the findings.
