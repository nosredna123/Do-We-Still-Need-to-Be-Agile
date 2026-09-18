## What it is
- **Artifact ID**: evidence_priority_matrix  
- **Unit of Analysis**: evidence_item  
- **Row Count (n_total)**: 77  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-priority-matrix-v1  

## How it was built
The evidence priority matrix was constructed using a script that processes data related to secondary exploratory evidence. It aggregates various metrics across 77 rows of evidence items, focusing on descriptive context and providing insights into their priority and relevance.

## Narrative binding
The narrative acts include 1, 2, 3, and 4. These acts are intended to support or qualify claims regarding the significance and applicability of the evidence presented in the matrix.

## What the current data actually shows
- **Coefficient**: Mean = -0.5365907760412248, Median = -0.5544826240669376, Min = -0.7854963073359155, Max = -0.0594088525786004, n_valid = 35  
- **p-value**: Mean = 0.20694046832180646, Median = 0.1212991257224558, Min = 0.0031279384351483, Max = 0.8857142857142857, n_valid = 59  
- **Jaccard**: Mean = 0.2164021164021164, Median = 0.1428571428571428, Min = 0.0, Max = 0.6, n_valid = 18  
- **Overlap_n**: Mean = 1.2222222222222223, Median = 1.0, Min = 0.0, Max = 3.0, n_valid = 18  
- **Missingness**: Not specified  
- **Cross-evidence labels**: Not specified  

## Contribution assessment
The verdict is not explicitly stated in the fact sheet. However, the data indicates a mean p-value of 0.20694046832180646, suggesting that the evidence may not be statistically significant. The mean coefficient of -0.5365907760412248 indicates a negative relationship, but the overall robustness of the findings is unclear due to the variability in p-values and the number of valid observations.

## Known limitations
- The evidence scope is limited to secondary exploratory evidence.
- The dataset has missing values, but specific details on missingness are not provided.
- The robustness class is not specified.
