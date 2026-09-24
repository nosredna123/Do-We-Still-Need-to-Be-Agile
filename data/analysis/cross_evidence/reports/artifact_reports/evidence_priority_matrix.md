## What it is
- **Artifact ID**: evidence_priority_matrix  
- **Unit of Analysis**: evidence_item  
- **Row Count (n_total)**: 77  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-priority-matrix-v1  

## How it was built
The evidence priority matrix was constructed using a script that processes data related to secondary exploratory evidence. It aggregates various metrics across 77 rows of evidence items, focusing on descriptive context and providing a structured overview of evidence tiers and scopes.

## Narrative binding
The narrative acts identified are 1, 2, 3, and 4. These acts are intended to support or qualify claims regarding the robustness and relevance of the evidence presented in the matrix.

## What the current data actually shows
- **Coefficient**: Mean = -0.5804202179159421, Median = -0.5831555764121896, Min = -0.7854963073359155, Max = -0.2376354103144018, n_valid = 35  
- **p-value**: Mean = 0.12857866996541645, Median = 0.0667530151696345, Min = 0.0031279384351483, Max = 0.8857142857142857, n_valid = 59  
- **Jaccard**: Mean = 0.21375661375661373, Median = 0.1428571428571428, Min = 0.0, Max = 0.6, n_valid = 18  
- **Overlap_n**: Mean = 1.2222222222222223, Median = 1.0, Min = 0.0, Max = 3.0, n_valid = 18  

## Contribution assessment
The verdict is not explicitly stated in the fact sheet. However, the data indicates a range of effect sizes and p-values, suggesting variability in the evidence's significance and robustness.

## Known limitations
- The evidence scope is limited to secondary exploratory evidence.
- There is a notable amount of missing data, with n_valid counts varying across metrics.
- The robustness class is not specified, which may affect the interpretation of the evidence's reliability.
