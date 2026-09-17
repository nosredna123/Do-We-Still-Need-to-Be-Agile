## What it is
The analytical artifact is a statistical dataset manifest with a unit of analysis of "cut_context." It contains 6 rows and was produced using the script "06_statistical_analyzer.py." The contract version is "statistical-dataset-manifest-v1."

## How it was built
The dataset was constructed by aggregating various metrics related to cut context, focusing on different semesters and temporal markers. The data was processed to ensure completeness and accuracy, with specific attention given to the variables of interest, which include various scores and metrics related to student responses and team activities.

## Narrative binding
The narrative acts associated with this dataset are 2, 3, and 4. These acts are intended to support or falsify the claims regarding the anatomy of planning debt, the human factor in progress perception, and the inversion of values in the era of AI.

## What the current data actually shows
The dataset contains the following concrete numbers: 
- For cut_context_metrics: n = 6, with missingness in several variables (e.g., 3 missing for "ie_transcript_coordination_friction_score_iqr," "ie_transcript_coordination_friction_score_mean," etc.).
- For student_nlp: n = 1122, with no missing values across all variables.
- For team_metrics: n = 14, with missingness in several variables (e.g., 7 missing for "ai_author_share_iqr_before_t3_window," 5 missing for "ai_author_share_iqr_t1," etc.).
- For transcript_nlp: n = 100, with no missing values across all variables.

## Contribution assessment
The deterministic verdict for this dataset is "descriptive_infrastructure." This is justified as the dataset provides a foundational overview of the metrics without conducting any inferential tests, as indicated by the absence of tests in the verdict summary.

## Known limitations
The known limitations include:
- Missing values in several variables across the datasets, particularly in team_metrics and cut_context_metrics.
- Exclusions due to missing values in specific variables, such as "ai_author_share_iqr_before_t3_window" and "ie_transcript_coordination_friction_score_iqr."
