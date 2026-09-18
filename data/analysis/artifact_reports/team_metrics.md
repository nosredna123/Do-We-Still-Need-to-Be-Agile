## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of "team_semester". It contains 14 rows and 183 columns. The producer script used to generate this dataset is "05_metric_engine.py", and it is based on contract version "team-metrics-v1".

## How it was built
The dataset was constructed using a script that processes various metrics related to team performance over different semesters. It aggregates data from multiple sources, ensuring that the information is structured in a way that allows for analysis of team dynamics and productivity across specified time periods.

## Narrative binding
The narrative acts associated with this dataset are 2 and 3. Act 2 supports the claim regarding the anatomy of planning debt, while Act 3 addresses the human factor and the illusion of progress.

## What the current data actually shows
The dataset contains 14 rows, with no missing values for key variables such as "ID_Equipe" and "Semestre". However, the analysis results are inconclusive, with all tests yielding non-significant outcomes: 
- pi_vs_cc_primary: inconclusive
- pi_vs_delta_dt_primary: inconclusive
- ai_vs_cc_primary: inconclusive
- pi_high_vs_low_cc_primary: inconclusive
- ai_high_vs_low_cc_primary: inconclusive

## Contribution assessment
The overall verdict of the analysis is "inconclusive". This is justified as all tests conducted, including correlation and hypothesis tests, did not provide significant results.

## Known limitations
The known limitations include:
- Affected rows due to integration friction (7 rows).
- Unavailable reasons for references in all time periods (14 rows).
- Missingness in various metrics, such as "ai_author_share_iqr_before_t3_window" (7 missing), "ai_author_share_median_before_t3_window" (7 missing), and others. 
The exclusions summary indicates that there are no affected counts for code churn, planning, and technical degradation.
