## What it is
- **Artifact ID**: cross_evidence_panel  
- **Unit of Analysis**: team_semester  
- **Row Count (n_total)**: 14  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-v1  

## How it was built
The cross-evidence panel dataset was constructed using a script that processes data related to team performance across different semesters. It includes various metrics such as project progress, scope applicability, technical complexity, and engagement participation, all measured at three different time points.

## Narrative binding
The narrative acts identified are 2, 3, and 4. These acts are intended to support or qualify claims regarding the performance metrics and their implications for team dynamics and project outcomes.

## What the current data actually shows
- **cc_per_source_loc_t3**: Mean = 1.263, n_valid = 14  
- **cc_total_t3**: Mean = 9737.5, n_valid = 14  
- **commits_per_author_t3**: Mean = 7.572, n_valid = 14  
- **pi_line_delta_t3**: Mean = 10164.57, n_valid = 14  
- **project_progress_mean_t1**: Mean = 3.039, n_valid = 14  
- **project_progress_mean_t2**: Mean = 3.030, n_valid = 14  
- **source_churn_t3**: Mean = 9630.93, n_valid = 14  
- **source_events_t3**: Mean = 135.14, n_valid = 14  

## Contribution assessment
The contribution of this dataset is significant as it provides a comprehensive overview of team performance metrics across semesters, with all metrics having valid data for the full sample size of 14.

## Known limitations
- No missingness data is provided.  
- The dataset is limited to 14 rows, which may restrict the generalizability of the findings.  
- The evidence scope is classified as secondary exploratory evidence, which may imply limitations in the robustness of the conclusions drawn from it.
