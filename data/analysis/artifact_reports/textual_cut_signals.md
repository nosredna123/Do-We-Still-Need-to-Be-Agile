## What it is
The analytical artifact is a dataset with a granularity/unit of analysis of 6 rows. It contains 349 columns and was produced using the script `04_nlp_qualitative_miner.py`. The contract version is `textual-cut-signals-v2`.

## How it was built
The dataset was constructed by applying a qualitative mining approach to textual data, focusing on extracting and analyzing various signals related to student career expectations and project challenges. The process involved processing the text data to derive quantitative scores that reflect students' dependency on AI and their sentiment towards project challenges.

## Narrative binding
The narrative act number is 3, which is meant to support the claim titled "Ato 3 - O Fator Humano e a Ilusao do Progresso (Evidence)."

## What the current data actually shows
The dataset contains the following statistics: 
- `student_career_expectation_ai_dependency_score_iqr`: n_total = 6, n_valid = 6, mean = 0.9166666666666666
- `student_career_expectation_ai_dependency_score_mode`: n_total = 6, n_valid = 6, mean = 0.0
- `student_career_expectation_ai_dependency_score_mode_n`: n_total = 6, n_valid = 6, mean = 22.166666666666668
- `student_career_expectation_ai_dependency_score_mode_share`: n_total = 6, n_valid = 6, mean = 0.6947191515722798
- `student_career_expectation_ai_dependency_score_q1`: n_total = 6, n_valid = 6, mean = 0.0
- `student_career_expectation_ai_dependency_score_q3`: n_total = 6, n_valid = 6, mean = 0.9166666666666666
- `student_n`: n_total = 6, n_valid = 6, mean = 31.166666666666668
- `student_project_challenges_sentiment_score_median`: n_total = 6, n_valid = 6, mean = 0.0

## Contribution assessment
The deterministic verdict is "descriptive_infrastructure." This is justified as there are no tests conducted, and the dataset primarily provides descriptive statistics without inferential analysis.

## Known limitations
- The dataset has a small sample size of only 6 rows.
- All key numeric columns have a limited range of valid data points, which may affect the reliability of the findings.
- There are no tests conducted to support any inferential claims.
