## What it is
- **Artifact ID**: late_instability_metrics  
- **Unit of Analysis**: team_semester  
- **Row Count (n_total)**: 14  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-v1  

## How it was built
The dataset was constructed using a script that processes data related to team performance over semesters, focusing on various metrics such as planning rework signals, source churn, and commit activity. It includes 27 columns capturing different aspects of team dynamics and software development activities.

## Narrative binding
The narrative acts identified are 2, 3, and 4. These acts are intended to support or qualify claims regarding the relationship between planning rework signals and team performance metrics, as well as to caution against overinterpreting the data without considering context.

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
The dataset provides valuable insights into team dynamics and performance metrics, with all 14 rows being valid. The consistent means across various metrics suggest a stable dataset for exploratory analysis.

## Known limitations
- No missing data was reported, as all components were available.
- The dataset is limited to 14 rows, which may restrict the generalizability of findings.
