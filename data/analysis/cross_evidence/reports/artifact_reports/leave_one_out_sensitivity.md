## What it is
- **Artifact ID**: leave_one_out_sensitivity  
- **Unit of Analysis**: analysis_result  
- **Row Count (n_total)**: 7  
- **Producer Script**: 08_cross_evidence_engine.py  
- **Contract Version**: cross-evidence-leave-one-out-v1  

## How it was built
The artifact was constructed using a script that processes cross-evidence data, specifically focusing on leave-one-out sensitivity analysis. It aggregates results from multiple analyses to evaluate the robustness of findings by systematically excluding one observation at a time.

## Narrative binding
- **Narrative Acts**: 2, 3  
- **Claims/Cautions Supported/Qualified**: These narrative acts are intended to support or qualify the robustness of the findings derived from the leave-one-out sensitivity analysis.

## What the current data actually shows
- **Original Coefficient**: Mean = -0.5692, Median = -0.5832, Min = -0.7285, Max = -0.3806  
- **Original p-value**: Mean = 0.0542, Median = 0.0286, Min = 0.0031, Max = 0.1795  
- **n_valid**: 7  
- **loo_total_n**: 14  
- **loo_tested_n**: 14  
- **loo_unavailable_n**: 0  
- **loo_supports_n**: Mean = 8.2857, Median = 13.0, Min = 1.0, Max = 14.0  
- **loo_support_share**: Mean = 0.5918, Median = 0.9286, Min = 0.0714, Max = 1.0  

## Contribution assessment
The verdict is that the findings provide preliminary evidence regarding the robustness of the analysis results, as indicated by the mean original p-value of 0.0542 and the support share mean of 0.5918. However, the maximum original p-value of 0.1795 suggests that some results may not be statistically significant.

## Known limitations
- No limitations were explicitly stated in the fact sheet.
- There are no exclusions summary provided.
