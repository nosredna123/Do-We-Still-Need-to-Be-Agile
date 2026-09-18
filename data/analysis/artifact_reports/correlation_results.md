## What it is
The granularity/unit of analysis is "team_semester". The row count is 4. The producer script is "06_statistical_analyzer.py". The contract version is "spearman-correlation-results-v1".

## How it was built
The analytical artifact was constructed using a Spearman correlation analysis to explore relationships between various metrics related to team performance over semesters. The analysis involved processing data from multiple sources, applying statistical methods to determine the strength and direction of correlations, and generating results that could be visualized and interpreted.

## Narrative binding
The narrative acts are 2 and 3. They are meant to support or falsify the claims in "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)" and "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
- For the analysis "pi_vs_cc_primary": n = 14, p-value = 0.9816838660605892, coefficient = -0.0067666495245095, missingness = 0.
- For the analysis "pi_vs_delta_dt_primary": n = 14, p-value = 0.960194880594909, coefficient = -0.0147096475119091, missingness = 0.
- For the analysis "ai_vs_cc_primary": n = 7, p-value = 0.6445115810207203, coefficient = 0.2142857142857143, missingness = 7.
- For the analysis "context_ie_temporal_primary": n = 6, p-value = null, coefficient = null, missingness = 3.

## Contribution assessment
The deterministic verdict is "inconclusive". This is justified as all tests resulted in inconclusive outcomes, with p-values indicating no significant correlations: "pi_vs_cc_primary" (p = 0.9817), "pi_vs_delta_dt_primary" (p = 0.9602), and "ai_vs_cc_primary" (p = 0.6445). Additionally, the "context_ie_temporal_primary" analysis was unavailable due to zero variance.

## Known limitations
- The analysis "ai_vs_cc_primary" had a small sample size (n < 10).
- The analysis "context_ie_temporal_primary" was unavailable due to zero variance.
- Exclusions summary: None provided.
