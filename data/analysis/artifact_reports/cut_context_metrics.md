## What it is
The analytical artifact is a dataset with a unit of analysis of "cut_context" and contains 6 rows. It was produced using the script "05_metric_engine.py" and is in contract version "cut-context-metrics-v1".

## How it was built
The dataset was constructed by processing data related to various metrics of cut contexts over specified semesters and temporal markers. The data was organized into a parquet format, ensuring efficient storage and retrieval. Each row represents a unique combination of semester and temporal marker, with multiple metrics calculated for each context.

## Narrative binding
The narrative act number is 3, which is meant to support or falsify the claim associated with "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
The dataset contains 6 rows, with 0 missing values for the "Semestre" and "ie_definition_version" columns. However, there are 3 missing values for several float64 columns, including "ie_transcript_coordination_friction_score_iqr", "ie_transcript_coordination_friction_score_mean", and "ie_transcript_coordination_friction_score_median". The overall verdict for the analyses conducted is "unavailable", with no significant results reported.

## Contribution assessment
The deterministic verdict is "unavailable". This is justified as all tests conducted, including "context_ie_temporal_primary" and "context_ie_high_vs_low_rework_primary", returned an unavailable verdict.

## Known limitations
- The overall analysis results are unavailable.
- Specific tests conducted yielded no significant results.
