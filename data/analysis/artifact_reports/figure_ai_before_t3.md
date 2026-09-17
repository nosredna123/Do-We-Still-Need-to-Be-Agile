## What it is
The granularity/unit of analysis is "team_semester" with a total row count of 7. The producer script used is "06_statistical_analyzer.py" and the contract version is not specified.

## How it was built
The analytical artifact was constructed using data from the "team_metrics.parquet" source. It involved transformations such as "complete_case_pair" and "size_by_commit_count" to prepare the data for analysis. The resulting figure visualizes the relationship between AI metrics and team performance over a specified observation window.

## Narrative binding
The narrative act number is 3, which is meant to support the claim related to "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)."

## What the current data actually shows
The current data shows a total of 7 observations with no missing data (n_missing: 0). The analyses conducted yielded inconclusive results, with p-values and coefficients not specified.

## Contribution assessment
The deterministic verdict is "inconclusive." This is justified as both analyses (ai_vs_cc_primary and ai_high_vs_low_cc_primary) returned inconclusive results.

## Known limitations
The limitations include "available AI window observations only." There are no exclusions specified.
