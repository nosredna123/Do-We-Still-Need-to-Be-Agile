# Role and Context
You are a Senior Data Engineer assisting an empirical software engineering researcher. We are preparing a focused, team-level dataset for a paper submission to ICSE/SEET 2027. 

Our unit of analysis is strictly the `team-semester` (N=14). We need a single, monolithic Python script to extract clear, simplified signals regarding "Planning Debt" and "Coordination Friction." 

# Directory Structure Constraints
- **Inputs:** Read from `data/lake/` using pandas (`git_commits.parquet`, `git_files.parquet`, `transcript_sessions.parquet`).
- **Outputs:** Save a single consolidated dataset to `data/analysis/advanced_metrics/team_level_signals.csv`.
- Execute from the project root.

# Objective
Generate a single Python script named `12_paper_signals_extractor.py`. The script must use `pandas` for transformations and an LLM client (e.g., `google-generativeai` or `openai`) to classify textual data. 

# Required Pipeline Steps

## 1. True Rework vs. Deferred Work (From Git Files)
**Goal:** Separate late-stage churn into productive new work vs. destructive rework.
- Join `git_files.parquet` and `git_commits.parquet` on `commit_hash` to map every file change to an `ID_Equipe`, `Semestre`, and `temporal_marker` (T1, T2, T3).
- **Filter:** Drop boilerplate (e.g., paths containing `node_modules`, `venv`, `package-lock`, `.json`, `.svg`).
- **Determine File Origin:** For each file in each team, find the earliest `temporal_marker` it was introduced.
- **Calculate T3 Rework Churn:** Sum `lines_added` + `lines_deleted` in T3 for files that originated in T1 or T2.
- **Calculate T3 Deferred Churn:** Sum `lines_added` + `lines_deleted` in T3 for files that originated in T3.
- Aggregate these two metrics by `ID_Equipe` and `Semestre`.

## 2. Planning Quality Signal (LLM over Commit Messages)
**Goal:** Overcome the limitation of just counting `.md` file volumes by having an LLM assess the *quality* of planning commits.
- Filter `git_commits.parquet` for commits made in T1.
- Group the commit messages by `ID_Equipe` and `Semestre` into a single T1 text block per team.
- **LLM Call:** Pass this text block to the LLM with a system prompt: 
  *"You are a Software Engineering evaluator. Read these early-stage project commit messages. Score the team's 'Upfront Planning and Architectural Clarity' from 1 to 10. Output only a JSON object: `{"t1_planning_score": <int>}`"*
- Extract and append this score to the team.

## 3. Coordination Friction Signal (LLM over Transcripts)
**Goal:** Extract variance from the 2025.2 cohort transcripts where traditional NLP failed.
- Read `transcript_sessions.parquet`. Group transcripts by `ID_Equipe`, `Semestre`, and `temporal_marker`.
- **LLM Call:** Pass the combined transcript text to the LLM with a system prompt: 
  *"You are a qualitative coding assistant analyzing software engineering student meetings in Portuguese. Evaluate the text for signs of integration pain, misaligned architecture, and coordination friction. Score 'Coordination Friction' from 1 to 10. Output only a JSON object: `{"coordination_friction": <int>}`"*
- Calculate the average Coordination Friction for T2 and T3, appending it to the team.

## 4. Final Consolidation
- Merge all generated metrics into a single pandas DataFrame grouped strictly by `ID_Equipe` and `Semestre`.
- Ensure missing values (e.g., T3 friction for the 2026.1 cohort missing transcripts) are handled gracefully (leave as NaN).
- Export to `data/analysis/advanced_metrics/team_level_signals.csv`.

Please output the complete, executable, and robust Python code with clear logging and batch processing for the LLM calls to respect API rate limits.

## 5. Integrating Existing Evaluator Ground Truth
**Goal:** Merge the new signals with the existing evaluator ratings so we can test the new hypotheses against the paper's strongest exploratory findings.
- Read `data/lake/evaluator_team_cuts.parquet` (which contains `scope_applicability_mean`, `technical_complexity_mean`, etc., grouped by `ID_Equipe`, `Semestre`, and `temporal_marker`).
- Filter or aggregate the evaluator metrics so they represent the overall team-semester (e.g., take the mean evaluator scores across all cuts for a team).
- Join these evaluator metrics into the final consolidation DataFrame based on `ID_Equipe` and `Semestre`.
- The final output in `data/analysis/advanced_metrics/team_level_signals.csv` must contain the new Rework Churn, Deferred Churn, LLM Planning Score, LLM Friction Score, AND the existing Evaluator Scope Applicability side-by-side.
