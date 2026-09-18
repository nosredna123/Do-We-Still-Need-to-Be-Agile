## What it is
- **Artifact ID**: late_instability_metrics  
- **Unit of Analysis**: team_semester  
- **Row Count (n_total)**: 14  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-v1  

## How it was built
The dataset was constructed to analyze late instability metrics across different teams and semesters. It includes 27 columns of data, capturing various metrics related to planning rework signals, source churn, and commit activities. The data was processed using the script named "08_cross_evidence_engine.py" and is formatted in a parquet file located at "data/analysis/cross_evidence/datasets/late_instability_metrics.parquet".

## Narrative binding
The narrative acts identified are 2, 3, and 4. These acts are intended to support or qualify claims regarding the relationship between planning rework signals, source churn, and overall team performance metrics.

## What the current data actually shows
- **Commits per Author (Rank Percent)**: Mean = 0.5357, n_valid = 14  
- **Delta DT (Rank Percent)**: Mean = 0.5357, n_valid = 14  
- **Late Instability Component Available**: Mean = 7.0, n_valid = 14  
- **Late Instability Component Missing**: Mean = 0.0, n_valid = 14  
- **Planning Rework Signal**: Mean = 163.64, n_valid = 14  
- **Planning Rework Signal (Rank Percent)**: Mean = 0.5357, n_valid = 14  
- **Source Churn (Rank Percent)**: Mean = 0.5357, n_valid = 14  
- **Source Events (Rank Percent)**: Mean = 0.5357, n_valid = 14  

## Contribution assessment
The dataset provides a comprehensive view of late instability metrics with valid data for all 14 rows. The mean values for various metrics suggest a consistent pattern across the teams analyzed, indicating potential areas for further exploration in relation to planning and performance.

## Known limitations
- No missing data was reported (0.0 for late_instability_component_missing_n).
- The dataset is limited to 14 rows, which may restrict the generalizability of the findings.
