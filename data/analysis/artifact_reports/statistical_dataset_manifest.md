## What it is
The analytical artifact is a statistical dataset manifest with a unit of analysis of "cut_context". It contains 6 rows and was produced using the script "06_statistical_analyzer.py". The contract version is "statistical-dataset-manifest-v1".

## How it was built
The dataset was constructed by aggregating various metrics related to cut context analysis over specified semesters and temporal markers. The data was processed to ensure completeness and accuracy, with attention given to the variables of interest, which include various scores and metrics related to student responses and team performance.

## Narrative binding
The narrative acts associated with this dataset are 2, 3, and 4. These acts are intended to support or falsify the claims regarding the anatomy of planning debt, the human factor in progress perception, and the inversion of values in the era of AI.

## What the current data actually shows
The dataset contains the following concrete numbers: 
- n: 6 (for cut_context_metrics)
- n: 1122 (for student_nlp)
- n: 14 (for team_metrics)
- n: 100 (for transcript_nlp)
- p-values: Not applicable
- coefficients: Not applicable
- missingness: 
  - For cut_context_metrics, 3 variables have missing values out of 6 total.
  - For student_nlp, there are no missing values.
  - For team_metrics, there are various missing values across multiple variables.
  - For transcript_nlp, there are no missing values.

## Contribution assessment
The deterministic verdict is "descriptive_infrastructure". This is justified as the dataset provides a foundational overview of the metrics collected, but does not include inferential statistics or tests that would allow for deeper conclusions.

## Known limitations
The limitations include:
- Missing values in several variables for the team_metrics dataset.
- Exclusions due to missing values in specific variables across multiple datasets, particularly in team_metrics and cut_context_metrics.
