## What it is
The analytical artifact is focused on the granularity/unit of analysis of "cut_context" with a total row count of 18. The producer script used for this artifact is "06_statistical_analyzer.py" and the contract version is not specified.

## How it was built
The artifact was constructed by applying several transformations to the source data from "cut_context_metrics.parquet". The transformations included melting context signals, preserving gaps, and avoiding interpolation. This process aimed to prepare the data for analysis while maintaining the integrity of the original observations.

## Narrative binding
The narrative act number is 3, which is intended to support the claim related to "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
The current data shows a total of 18 observations, with 9 valid observations and 9 missing. The p-values and coefficients for the analyses are unavailable, indicating that no significant results were obtained.

## Contribution assessment
The deterministic verdict is "unavailable". This is justified as both analyses conducted (context_ie_temporal_primary and context_ie_high_vs_low_rework_primary) returned verdicts of "unavailable".

## Known limitations
- Three complete transcript-score observations for the primary pair.
- Exclusions summary is not provided.
