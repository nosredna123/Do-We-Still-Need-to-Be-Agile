## What it is
- **Artifact ID**: evaluator_outcome_metrics  
- **Unit of Analysis**: team_semester  
- **Row Count (n_total)**: 14  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-v1  

## How it was built
The dataset was constructed using a script that processes data related to team performance across different semesters. It includes various metrics such as engagement participation, project progress, scope applicability, and technical complexity, measured at three different time points.

## Narrative binding
The narrative act present is 3, which is meant to support or qualify claims regarding the evaluation of team performance metrics over time.

## What the current data actually shows
- **Engagement Participation Mean (t1)**: Mean = 1.6875, n_valid = 14  
- **Scope Applicability Mean Delta (t1 to t2)**: Mean = 0.0565, n_valid = 14  
- **Scope Applicability Mean Delta (t1 to t3)**: Mean = 0.1607, n_valid = 14  
- **Scope Applicability Mean Delta (t2 to t3)**: Mean = 0.1042, n_valid = 14  
- **Technical Complexity Mean (t1)**: Mean = 1.625, n_valid = 14  
- **Technical Complexity Mean (t2)**: Mean = 1.6101, n_valid = 14  
- **Technical Complexity Mean (t3)**: Mean = 1.8363, n_valid = 14  

## Contribution assessment
The contribution assessment is inconclusive due to the lack of significant effect sizes or p-values provided in the data. The dataset contains descriptive statistics but does not indicate the strength or significance of the relationships between the measured variables.

## Known limitations
- The dataset is limited to 14 rows, which may not provide a comprehensive view of the evaluated metrics.
- There is no information on missingness or the reasons for any unavailable outcomes.
