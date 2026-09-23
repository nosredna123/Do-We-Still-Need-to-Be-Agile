## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of 6 rows. It contains 349 columns and was produced using the script `04_nlp_qualitative_miner.py`. The contract version is `textual-cut-signals-v2`.

## How it was built
The dataset was constructed by processing qualitative data through a natural language processing script designed to extract and analyze textual signals. This involved collecting various metrics related to student career expectations and project challenges, which were then organized into a structured format for further analysis.

## Narrative binding
The narrative act number is 3, which is meant to support the claim titled "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)."

## What the current data actually shows
The dataset contains the following concrete numbers: 
- `n_total`: 6 
- `n_valid`: 6 
- `student_career_expectation_ai_dependency_score_iqr`: mean 0.9166666666666666, median 1.0 
- `student_career_expectation_ai_dependency_score_mode`: mean 0.0, median 0.0 
- `student_career_expectation_ai_dependency_score_mode_n`: mean 22.166666666666668, median 20.0 
- `student_career_expectation_ai_dependency_score_mode_share`: mean 0.6947191515722798, median 0.6875 
- `student_career_expectation_ai_dependency_score_q1`: mean 0.0, median 0.0 
- `student_career_expectation_ai_dependency_score_q3`: mean 0.9166666666666666, median 1.0 
- `student_n`: mean 31.166666666666668, median 31.0 
- `student_project_challenges_sentiment_score_median`: mean 0.0, median 0.0 

## Contribution assessment
The deterministic verdict is "descriptive_infrastructure." This is justified as all tests returned no significant results, indicating that the dataset primarily serves as a descriptive tool rather than a source of inferential insights.

## Known limitations
- The dataset has a very small sample size (n=6), which limits the generalizability of the findings.
- All key metrics show a lack of variability, with several means and medians being zero.
- There are no significant tests conducted, which further limits the interpretability of the data.
- Exclusions summary is not provided.
