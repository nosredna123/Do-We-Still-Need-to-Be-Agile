## What it is
The granularity/unit of analysis is "team_semester" and "cut_context". The row count is 3. The producer script is "06_statistical_analyzer.py". The contract version is "mann-whitney-hypothesis-results-v1".

## How it was built
The analytical artifact was constructed using a statistical analysis script that performed Mann-Whitney U tests on various group comparisons. The analysis aimed to explore relationships between different variables related to team performance and coordination, with a focus on understanding how these factors might influence outcomes in a semester context.

## Narrative binding
The narrative acts are 2 and 3. They are meant to support or falsify the claims related to "A Anatomia da Divida de Planejamento (Diagnosis)" and "O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
- For the analysis "pi_high_vs_low_cc_primary": n = 14, p-value = 0.7103729603729605, U statistic = 21.0, n_missing = 0.
- For the analysis "ai_high_vs_low_cc_primary": n = 14, p-value = 1.0, U statistic = 6.0, n_missing = 7.
- For the analysis "context_ie_high_vs_low_rework_primary": n = 6, p-value = null, U statistic = null, n_missing = 3.

## Contribution assessment
The deterministic verdict is "inconclusive". This is justified as all tests resulted in inconclusive outcomes: "pi_high_vs_low_cc_primary" verdict is inconclusive, "ai_high_vs_low_cc_primary" verdict is inconclusive, and "context_ie_high_vs_low_rework_primary" verdict is unavailable.

## Known limitations
- The analysis "context_ie_high_vs_low_rework_primary" was marked as unavailable due to insufficient group size.
- There were missing values in the "ai_high_vs_low_cc_primary" analysis, with 7 missing out of 14 total.
- The overall results were inconclusive, indicating a lack of significant findings across the analyses.
