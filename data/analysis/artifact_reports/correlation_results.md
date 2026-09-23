## What it is
The granularity/unit of analysis is "team_semester". The row count is 4. The producer script is "06_statistical_analyzer.py". The contract version is "spearman-correlation-results-v1".

## How it was built
The analytical artifact was constructed using a Spearman correlation analysis to explore relationships between various metrics related to team performance and project outcomes. The analysis was executed on a dataset containing multiple variables, and the results were compiled into a CSV format for further examination.

## Narrative binding
The narrative acts are 2 and 3. They are meant to support or falsify the claims in "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)" and "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
- For the analysis "pi_vs_cc_primary": n = 14, p-value = 0.9816838660605892, coefficient = -0.0067666495245095, missingness = 0.
- For the analysis "pi_vs_delta_dt_primary": n = 14, p-value = 0.960194880594909, coefficient = -0.0147096475119091, missingness = 0.
- For the analysis "ai_vs_cc_primary": n = 7, p-value = 0.6445115810207203, coefficient = 0.2142857142857143, missingness = 7.
- For the analysis "context_ie_temporal_primary": n = 3, p-value = 0.0, coefficient = 1.0, missingness = 3.

## Contribution assessment
The deterministic verdict is "supports_partially". This is justified as follows: the analysis "context_ie_temporal_primary" supports the claim, while the other analyses ("pi_vs_cc_primary", "pi_vs_delta_dt_primary", and "ai_vs_cc_primary") are inconclusive.

## Known limitations
- Small sample size for "ai_vs_cc_primary" and "context_ie_temporal_primary" (n < 10).
- Missing data for "ai_vs_cc_primary" (7 missing) and "context_ie_temporal_primary" (3 missing).
