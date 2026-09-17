## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of "team_semester" and a row count of 14. It was produced using the script "05_metric_engine.py" and is based on contract version "team-metrics-v1".

## How it was built
The dataset was constructed by aggregating various metrics related to team performance over different semesters. It includes multiple variables that capture aspects such as activity status, author contributions, and technical complexity, ensuring a comprehensive view of team dynamics across the specified time periods.

## Narrative binding
The narrative acts associated with this artifact are 2 and 3. Act 2 supports the claim regarding the anatomy of planning debt, while Act 3 addresses the human factor and the illusion of progress.

## What the current data actually shows
The dataset contains 14 rows, with no missing values for most variables. However, there are some variables with missingness: 7 missing for "ai_author_share_iqr_before_t3_window", 5 for "ai_author_share_iqr_t1", 4 for "ai_author_share_iqr_t2", and others. The overall analysis verdict is inconclusive, with no significant correlations or hypotheses being supported.

## Contribution assessment
The deterministic verdict for this artifact is "inconclusive". This is justified as all tests conducted, including correlations and hypotheses, returned inconclusive results.

## Known limitations
- The dataset has a small row count of 14, which may limit the generalizability of the findings.
- Several variables exhibit missingness, which could affect the robustness of the analysis.
- The overall analysis results are inconclusive, indicating a lack of significant findings.
