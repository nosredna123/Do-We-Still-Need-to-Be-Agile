## What it is
The analytical artifact is a figure that analyzes data at the granularity of "team_semester" with a total row count of 42. It was produced using the script "06_statistical_analyzer.py" and is based on contract version "team_metrics.parquet".

## How it was built
The figure was created by applying transformations to the data, specifically "melt_T1_T2_T3" and "no_interpolation". This process involved restructuring the dataset to facilitate analysis of the variable "technical_complexity" across different team semesters, allowing for a clearer visual representation of the data.

## Narrative binding
The narrative acts associated with this artifact are 2 and 3. Act 2 supports the claim regarding the diagnosis of planning debt anatomy, while Act 3 provides evidence related to the human factor and the illusion of progress.

## What the current data actually shows
The current data shows a total of 42 observations with no missing data (n_missing: 0). The analysis conducted was a correlation (analysis_id: "pi_vs_delta_dt_primary"), which yielded an inconclusive verdict (verdict: "inconclusive").

## Contribution assessment
The overall contribution of this artifact is deemed inconclusive. This is justified by the correlation analysis, which did not provide significant results, as indicated by the verdict summary.

## Known limitations
- Team-semester observations; no causal interpretation.
