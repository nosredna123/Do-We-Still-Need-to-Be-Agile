# Role and Context
You are a Senior Data Engineer assisting an empirical software engineering researcher. We are preparing a focused, team-level dataset for a paper submission to ICSE/SEET 2027. 

Our unit of analysis is strictly the `team-semester` (N=14). We need a single, monolithic Python script named `12_paper_signals_extractor.py` to extract signals regarding "Planning Debt," "Coordination Friction," and merge them with evaluator scores.

# Architectural Constraints
1. **Root Execution:** The script must be executed from the project root.
2. **Centralized Artifacts:** All artifacts must be saved under `paper_v4/advanced_metrics/`. The script must dynamically create the following subdirectories if they do not exist:
   - `paper_v4/advanced_metrics/logs/` (for execution logs)
   - `paper_v4/advanced_metrics/llm_cache/` (for resumability and metadata)
   - `paper_v4/advanced_metrics/outputs/` (for the final datasets)
3. **Didactic Logging:** Use Python's `logging` module. Configure it to output to both the console and a timestamped text file (e.g., `logs/YYYYMMDD_HHMMSS_12_paper_signals_extractor.log`). Log messages must be comprehensive, clear, and explain exactly what each step of the pipeline is doing (e.g., "Step 1: Merging Git files and commits...", "Found X files after boilerplate exclusion").
4. **LLM Gateway:** You must NOT use raw OpenAI or Google SDKs. You must import and use a pre-existing local utility module: `from llm_gateway import ...` (assume this module exposes a function to send a prompt and return a string response). 
5. **Resumability & Call Logging:** 
   - Implement a robust caching mechanism. Before processing any team's data through the LLM, check a local JSON dictionary (e.g., `llm_cache/llm_results_cache.json`).
   - If the key (e.g., `"2025.2_Team1_Planning"`) exists, load the result and skip the API call.
   - If not, call the `llm_gateway`, parse the response, update the cache, and immediately save the cache file to disk.
   - Additionally, append every API call's metadata (timestamp, ID_Equipe, Semestre, task_type, raw_prompt, raw_response) to a JSONL file (`llm_cache/llm_call_history.jsonl`) for future audit/inspection.

# Required Pipeline Steps

## 1. True Rework vs. Deferred Work (From Git Files)
- Load `data/lake/git_files.parquet` and `data/lake/git_commits.parquet`.
- Join them on `commit_hash` to map every file change to `ID_Equipe`, `Semestre`, and `temporal_marker` (T1, T2, T3).
- Filter out boilerplate paths (e.g., `node_modules`, `venv`, `package-lock`, `.json`, `.svg`).
- For each file per team, find the earliest `temporal_marker`.
- **Rework Churn:** Sum `lines_added` + `lines_deleted` in T3 for files that originated in T1 or T2.
- **Deferred Churn:** Sum `lines_added` + `lines_deleted` in T3 for files that originated in T3.
- Aggregate by `ID_Equipe` and `Semestre`.

## 2. Planning Quality Signal (LLM over Commit Messages)
- Filter `git_commits.parquet` for T1 commits. Group messages by `ID_Equipe` and `Semestre` into a single text block.
- Use the cache logic. If not cached, send to `llm_gateway` with the prompt: 
  *"You are a Software Engineering evaluator. Read these early-stage project commit messages. Score the team's 'Upfront Planning and Architectural Clarity' from 1 to 10. Output only a JSON object: `{"t1_planning_score": <int>}`"*
- Extract the score and save to cache/history.

## 3. Coordination Friction Signal (LLM over Transcripts)
- Load `data/lake/transcript_sessions.parquet`. Group text by `ID_Equipe`, `Semestre`, and `temporal_marker`.
- Use the cache logic. If not cached, send to `llm_gateway` with the prompt: 
  *"You are a qualitative coding assistant analyzing software engineering student meetings in Portuguese. Evaluate the text for signs of integration pain, misaligned architecture, and coordination friction. Score 'Coordination Friction' from 1 to 10. Output only a JSON object: `{"coordination_friction": <int>}`"*
- Calculate the average Coordination Friction for T2 and T3 per team.

## 4. Integrating Existing Evaluator Ground Truth
- Load `data/lake/evaluator_team_cuts.parquet`.
- Calculate the mean `scope_applicability_mean` and `technical_complexity_mean` across all cuts for each team-semester.

## 5. Final Consolidation
- Merge the File Churn metrics, LLM Planning Scores, LLM Friction Scores, and Evaluator metrics into a single pandas DataFrame grouped strictly by `ID_Equipe` and `Semestre`.
- Ensure NaNs are handled gracefully (e.g., missing transcripts for 2026.1).
- Export to `paper_v4/advanced_metrics/outputs/team_level_signals.csv`.

Generate the complete, robust Python script, including all necessary imports, type hints, and exception handling for JSON parsing of the LLM outputs.