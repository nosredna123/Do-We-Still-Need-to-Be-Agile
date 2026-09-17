## What it is
The analytical artifact is a figure that analyzes data at the granularity of team-semester. It contains a total of 42 rows, with 31 valid observations after accounting for missing data. The producer script used to generate this artifact is `06_statistical_analyzer.py`, and it is based on contract version 1.0.

## How it was built
The figure was constructed by applying specific transformations to the source data, which is stored in a parquet file named `team_metrics.parquet`. The transformations included melting the data across three time points (T1, T2, T3) and avoiding any interpolation of values. The resulting data was then normalized to present a linear scale of churn.

## Narrative binding
The narrative act number is 2, which corresponds to the claim titled "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)." This act is intended to support or falsify the associated claim regarding the analysis of planning debt.

## What the current data actually shows
The current data shows a total of 42 observations, with 11 missing values, resulting in 31 valid entries. There are no specific p-values or coefficients reported, and no tests were conducted, indicating a lack of statistical significance in the findings.

## Contribution assessment
The deterministic verdict for this artifact is "descriptive_infrastructure." This is justified by the absence of tests and the overall descriptive nature of the data, as indicated by the lack of significant statistical results.

## Known limitations
- Panel values aggregate team-semester observations.
- Exclusions summary: None provided.
