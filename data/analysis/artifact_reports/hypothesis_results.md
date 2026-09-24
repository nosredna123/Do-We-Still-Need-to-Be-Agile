## What it is
The granularity/unit of analysis is "team_semester" and "cut_context". The row count is 3. The producer script is "06_statistical_analyzer.py". The contract version is "mann-whitney-hypothesis-results-v1".

## How it was built
The analytical artifact was constructed using a statistical analysis script that performed Mann-Whitney U tests on various group comparisons. The analysis aimed to explore differences in outcome variables based on specified group variables, with no multiple testing corrections applied.

## Narrative binding
The narrative acts are 2 and 3. They are meant to support or falsify the claims related to "A Anatomia da Divida de Planejamento (Diagnosis)" and "O Fator Humano e a Ilusao do Progresso (Evidence)".

## What the current data actually shows
- For the analysis "pi_high_vs_low_cc_primary": n = 14, p-value = 0.6200466200466201, U statistic = 29.0, n_missing = 0.
- For the analysis "ai_high_vs_low_cc_primary": n = 14, p-value = 0.8571428571428571, U statistic = 7.0, n_missing = 7.
- For the analysis "context_ie_high_vs_low_rework_primary": n = 6, p-value = null, U statistic = null, n_missing = 3.

## Contribution assessment
The deterministic verdict is "inconclusive". This is justified as all tests resulted in inconclusive outcomes: "pi_high_vs_low_cc_primary" and "ai_high_vs_low_cc_primary" both had inconclusive verdicts, while "context_ie_high_vs_low_rework_primary" was unavailable due to insufficient group size.

## Known limitations
- The analysis "context_ie_high_vs_low_rework_primary" was unavailable due to insufficient group size.
- There were missing values in the "ai_high_vs_low_cc_primary" analysis, with 7 missing out of 14 total.
- The results for the other analyses were inconclusive.
