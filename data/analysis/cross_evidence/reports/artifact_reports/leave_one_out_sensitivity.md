## What it is
- **Artifact ID**: leave_one_out_sensitivity  
- **Unit of Analysis**: analysis_result  
- **Row Count (n_total)**: 7  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-leave-one-out-v1  

## How it was built
The artifact was constructed using a script that processes cross-evidence data, specifically focusing on leave-one-out sensitivity analysis. It aggregates results from multiple analyses, capturing various metrics such as coefficients and p-values across a total of 7 rows of data.

## Narrative binding
The narrative acts identified are 2 and 3. These acts are meant to support or qualify claims regarding the robustness and reliability of the analysis results.

## What the current data actually shows
- **Original Coefficient**: Mean = -0.5207027851032128, Median = -0.5207396621025063, Min = -0.7284815485795703, Max = -0.2647382010005621  
- **Original P-Value**: Mean = 0.10340406311635783, Median = 0.056231526062027, Min = 0.0031279384351483, Max = 0.3603606340812801  
- **Leave-One-Out Total N (loo_total_n)**: 14  
- **Leave-One-Out Tested N (loo_tested_n)**: 14  
- **Leave-One-Out Unavailable N (loo_unavailable_n)**: 0  
- **Leave-One-Out Supports N (loo_supports_n)**: Mean = 6.714285714285714, Median = 2.0, Min = 1.0, Max = 14.0  
- **Leave-One-Out Support Share (loo_support_share)**: Mean = 0.4795918367346938, Median = 0.1428571428571428, Min = 0.0714285714285714, Max = 1.0  

## Contribution assessment
The verdict is that the evidence is exploratory and primarily serves as a candidate for further investigation. This is justified by the presence of a mean original p-value of 0.10340406311635783, indicating that the results are not statistically significant at conventional levels.

## Known limitations
- The analysis is based on secondary exploratory evidence.
- The maximum number of unavailable data points is 0, indicating no missing data.
- The results may not generalize beyond the specific analyses conducted, as they are exploratory in nature.
