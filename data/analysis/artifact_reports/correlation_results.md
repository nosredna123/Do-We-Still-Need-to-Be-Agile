## What it is
The granularity/unit of analysis is "team_semester" with a row count of 4. The producer script is "06_statistical_analyzer.py" and the contract version is "spearman-correlation-results-v1".

## How it was built
The analytical artifact was constructed using a Spearman correlation analysis to explore relationships between various metrics related to team performance and project outcomes. The analysis was executed through a script that processed the relevant data, generating correlation coefficients and p-values for each pair of variables under consideration.

## Narrative binding
The narrative acts are 2 and 3. They are meant to support or falsify the claims in "Ato 2 - A Anatomia da Divida de Planejamento (Diagnosis)" and "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
- Analysis ID: pi_vs_cc_primary: n = 14, p-value = 0.5952186358602511, coefficient = -0.1556329390637204, n_missing = 0
- Analysis ID: pi_vs_delta_dt_primary: n = 14, p-value = 0.960194880594909, coefficient = -0.0147096475119091, n_missing = 0
- Analysis ID: ai_vs_cc_primary: n = 7, p-value = 0.8191508555699912, coefficient = -0.1071428571428571, n_missing = 7
- Analysis ID: context_ie_temporal_primary: n = 3, p-value = 0.0, coefficient = 1.0, n_missing = 3

## Contribution assessment
The deterministic verdict is "supports_partially". This is justified as the analysis for "context_ie_temporal_primary" supports the claim, while the other analyses (pi_vs_cc_primary, pi_vs_delta_dt_primary, ai_vs_cc_primary) are inconclusive.

## Known limitations
- Small sample size for analyses involving "ai_vs_cc_primary" and "context_ie_temporal_primary" (n < 10).
- Missing data for "ai_vs_cc_primary" (7 missing).
- Inconclusive results for three out of four analyses.
