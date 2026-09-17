## What it is
The analytical artifact is focused on the granularity/unit of analysis of "team_semester" with a total row count of 42. It was produced using the script "06_statistical_analyzer.py" and is based on contract version "team_metrics.parquet".

## How it was built
The artifact was created by applying specific transformations to the data, including "melt_T1_T2_T3" and "no_interpolation". This process allowed for the analysis of technical complexity across different team semesters, resulting in a structured output that can be visually interpreted.

## Narrative binding
The narrative acts associated with this artifact are 2 and 3. Act 2 supports the claim regarding the diagnosis of planning debt, while Act 3 provides evidence related to the human factor and the illusion of progress.

## What the current data actually shows
The current data shows a total of 42 valid observations (n = 42) with no missing data (n_missing = 0). The analysis conducted was a correlation (analysis_id: pi_vs_delta_dt_primary), which yielded an inconclusive verdict (verdict: inconclusive).

## Contribution assessment
The overall contribution assessment is "inconclusive". This is justified by the fact that the correlation analysis did not provide significant results, as indicated by the verdict of inconclusive.

## Known limitations
- Team-semester observations; no causal interpretation.
