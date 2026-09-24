## What it is
The analytical artifact is a figure that analyzes data at the granularity of team-semester. It contains a total of 42 rows, with 31 valid observations after accounting for missing data. The producer script used to generate this artifact is `06_statistical_analyzer.py`, and it is based on contract version 1.0.

## How it was built
The figure was constructed by processing data from the `team_metrics.parquet` source file. The data underwent transformations including melting the data across three time points (T1, T2, T3) and applying no interpolation. The resulting metrics were then normalized to present a linear view of churn across teams and semesters.

## Narrative binding
The narrative act number is 2, which corresponds to the claim "A Anatomia da Divida de Planejamento (Diagnosis)."

## What the current data actually shows
The current data shows a total of 42 observations, with 11 missing values, resulting in 31 valid entries. There are no statistical tests reported, and thus no p-values or coefficients are available.

## Contribution assessment
The deterministic verdict is "descriptive_infrastructure." This is justified as the artifact provides a descriptive overview of team-semester observations without any inferential statistical tests.

## Known limitations
- Panel values aggregate team-semester observations.
- Exclusions summary: None provided.
