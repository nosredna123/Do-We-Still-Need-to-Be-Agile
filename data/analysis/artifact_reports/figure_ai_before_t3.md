## What it is
The analytical artifact is a figure with a granularity/unit of analysis at the team_semester level. It contains a total of 7 rows, produced by the script `06_statistical_analyzer.py`, and is based on contract version 1.0.

## How it was built
The figure was constructed using data from the `team_metrics.parquet` source file. It involved transformations such as complete case pair analysis and size calculations based on commit counts. The resulting visual representation aims to illustrate the relationship between AI metrics and team performance over specific semesters.

## Narrative binding
The narrative act number is 3, which supports the claim related to "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)."

## What the current data actually shows
The current data shows a total of 7 valid observations with no missing data (n_missing: 0). The analyses conducted were inconclusive, with p-values and coefficients not specified, leading to an overall verdict of inconclusive.

## Contribution assessment
The deterministic verdict is "inconclusive." This is justified as both analyses (ai_vs_cc_primary and ai_high_vs_low_cc_primary) returned inconclusive results, indicating that no definitive conclusions can be drawn from the data.

## Known limitations
- Available AI window observations only.
