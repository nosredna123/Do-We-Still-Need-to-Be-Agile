## What it is
- **Artifact ID**: temporal_escalation_panel_data  
- **Unit of Analysis**: metric_family_cut  
- **Row Count (n_total)**: 54  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-figure-data-v1  

## How it was built
The artifact was constructed using a script that processes data related to various metrics over time, specifically focusing on a family of metrics. The data is aggregated and includes raw values, baseline comparisons, and semester indicators, resulting in a structured dataset with 54 rows and 13 columns.

## Narrative binding
The narrative acts identified are 2 and 3. These acts are intended to support or qualify claims regarding the temporal escalation of metrics and their relative values over time.

## What the current data actually shows
- **Baseline T1**:  
  - Max: 6360.0  
  - Mean: 684.30  
  - Median: 3.62  
  - Min: 1.58  
  - n_valid: 54  
- **n_valid**:  
  - Max: 14.0  
  - Mean: 9.33  
  - Median: 9.0  
  - Min: 5.0  
  - n_total: 54  
- **Semester**:  
  - Max: 2026.1  
  - Mean: 2025.65  
  - Median: 2025.65  
  - Min: 2025.2  
  - n_valid: 36  
- **Value Raw**:  
  - Max: 1485854.33  
  - Mean: 47606.23  
  - Median: 16.88  
  - Min: 1.53  
  - n_valid: 54  
- **Value Relative T1**:  
  - Max: 710.78  
  - Mean: 35.21  
  - Median: 1.13  
  - Min: 0.85  
  - n_valid: 54  

## Contribution assessment
The verdict on the contribution of this artifact is that it provides a structured dataset for analyzing temporal metrics. The data includes comprehensive statistics on baseline values, raw values, and semester indicators, which can be useful for exploratory analysis.

## Known limitations
- The evidence scope is classified as secondary exploratory evidence.
- The dataset has a missingness issue, as only 36 out of 54 rows are valid for the semester column.
