## What it is
The analytical artifact is a figure that analyzes data at the granularity of team-semester. It contains a total of 42 rows, with 31 valid observations after accounting for missing data. The producer script used to generate this artifact is `06_statistical_analyzer.py`, and it is based on contract version 1.0.

## How it was built
The figure was constructed by applying specific transformations to the source data, which is stored in `team_metrics.parquet`. The transformations included melting the data across three time points (T1, T2, T3) and avoiding interpolation to maintain the integrity of the original observations. The resulting data was then analyzed to produce a visual representation of the metrics.

## Narrative binding
The narrative act number is 2, which supports the claim titled "A Anatomia da Divida de Planejamento (Diagnosis)."

## What the current data actually shows
The current data shows a total of 42 observations, with 11 missing values, resulting in 31 valid observations. There are no statistical tests reported, and thus no p-values or coefficients are available.

## Contribution assessment
The deterministic verdict for this artifact is "descriptive_infrastructure." This is justified as there are no statistical tests conducted, indicating that the artifact primarily serves to describe the data rather than provide inferential insights.

## Known limitations
- Panel values aggregate team-semester observations.
