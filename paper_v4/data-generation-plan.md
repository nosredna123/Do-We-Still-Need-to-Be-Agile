# Role and Context
You are a Senior Data Engineer assisting an empirical software engineering researcher. We are preparing a focused, team-level dataset for a paper submission to ICSE/SEET 2027.

Our unit of analysis is strictly the `team-semester` (N=14). We need a single, monolithic Python script named `12_paper_signals_extractor.py` to extract signals for planning-related evidence and merge them with evaluator scores, while preserving a separate descriptive cohort-friction artifact for temporal trend review.

# Architectural Constraints
1. **Root Execution:** The script must be executed from the project root.
2. **Centralized Artifacts:** All artifacts must be saved under `paper_v4/advanced_metrics/`. The script must dynamically create the following subdirectories if they do not exist:
   - `paper_v4/advanced_metrics/logs/` (for execution logs)
   - `paper_v4/advanced_metrics/llm_cache/` (for resumability and metadata)
   - `paper_v4/advanced_metrics/outputs/` (for the final datasets)
3. **Didactic Logging:** Use Python's `logging` module. Configure it to output to both the console and a timestamped text file (for example `logs/YYYYMMDD_HHMMSS_12_paper_signals_extractor.log`). Log messages must be comprehensive and explain exactly what each step is doing, including expected counts, exclusions, and any data-quality warnings.
4. **LLM Gateway:** You must NOT use raw OpenAI or Google SDKs. You must import and use the existing local utility module `from llm_gateway import ...`.
5. **Resumability & Call Logging:**
   - Before processing any team through the LLM, check a local JSON dictionary cache file, for example `paper_v4/advanced_metrics/llm_cache/llm_results_cache.json`.
   - If a key such as `"2025.2_Team1_Planning"` already exists, load the cached value and skip the API call.
   - If not, call the LLM gateway, parse the response, update the cache in memory, and immediately save the JSON cache file to disk.
   - Append every API call's metadata to a structured CSV ledger at `paper_v4/advanced_metrics/llm_cache/llm_call_history.csv` for human review. Suggested columns: `timestamp`, `task_type`, `ID_Equipe`, `Semestre`, `prompt_key`, `prompt_text`, `raw_response`, `parsed_score`, `status`, `notes`.
   - Keep the prompt definitions centralized in a dedicated Python module inside `paper_v4`, for example `paper_v4/advanced_metrics/llm_prompts.py`.
6. **Preserve Previous Runs:** The script must reuse prior cache and ledger entries by default. It should append new rows to the CSV ledger and only re-query the LLM when the cache key is missing. The user will manually delete the items they want to regenerate.
7. **Cross-check with Clean Repos:** Before using Git-derived file churn as final evidence, cross-check the file-level provenance against the cleaned repository snapshots in `data/processed/clean_repos/` to validate that the observed Git file paths and project metadata remain consistent. This is a validation layer, not the primary source of truth.
8. **Separate Cohort Artifact:** The cohort-level coordination-friction signal is descriptive only and must be exported as a separate artifact; it must not be merged into the final team-level dataframe.

# Required Pipeline Steps

## 1. True Rework vs. Deferred Work (From Git Files)
- Load `data/lake/git_files.parquet` and `data/lake/git_commits.parquet`.
- Join them on `commit_hash` so each file change is mapped to `ID_Equipe`, `Semestre`, and `temporal_marker` (T1, T2, T3).
- Validate required columns, row integrity, and temporal markers. Fail fast if any required source fields are missing.
- Filter out boilerplate paths (for example `node_modules`, `venv`, `package-lock`, `.json`, `.svg`, and obviously non-source file paths).
- For each file per team-semester, determine the earliest `temporal_marker` in which it appears.
- **Rework Churn:** Sum `lines_added` + `lines_deleted` in T3 for files whose earliest appearance is T1 or T2.
- **Deferred Churn:** Sum `lines_added` + `lines_deleted` in T3 for files whose earliest appearance is T3.
- Aggregate by `ID_Equipe` and `Semestre`.
- Cross-check file provenance against `data/processed/clean_repos/` and log any anomalies (missing repo, mismatched repo name, unmatched file path, or unexpected origin window) without silently dropping rows.

## 2. Planning Quality Signal (LLM over Commit Messages)
- Filter `git_commits.parquet` to T1 commits only.
- Group messages by `ID_Equipe` and `Semestre` into a single text block per team-semester.
- Use a centralized prompt from `paper_v4/advanced_metrics/llm_prompts.py`.
- Use the cache logic. If the key does not exist, call the `llm_gateway` and parse the result.
- The cache key must be unique per team-semester and task type, for example `"2025.2_Team1_Planning"`.
- Each team-semester pair triggers exactly one LLM call per task type. If the key exists, skip the call.
- Extract the score and save to cache/history.
- Output only JSON in the form `{"t1_planning_score": <int>}`.

## 3. Coordination Friction Signal (Descriptive Cohort-Level Only)
**Goal:** Because the team-level transcript signal is too sparse for the actual dataset, aggregate transcript text at the cohort/temporal level to show friction trends across T1, T2, and T3 without mixing it into the team-level DataFrame.
- Load `data/lake/transcript_sessions.parquet`.
- Group all transcript text strictly by `temporal_marker`, ignoring `ID_Equipe`, combining all conversations for T1 into one block, T2 into another, and T3 into a third.
- Use the centralized prompt from `paper_v4/advanced_metrics/llm_prompts.py`.
- Use the same cache logic; each temporal block gets one LLM call per task type.
- Prompt task type should be `"cohort_coordination_friction"` or a similar explicit label.
- Export this as a small, 3-row dataset with columns such as `Semestre`, `temporal_marker`, and `coordination_friction`, to `paper_v4/advanced_metrics/outputs/cohort_temporal_friction.csv`.
- Do not merge this dataset into the team-level DataFrame.

## 4. Integrating Existing Evaluator Ground Truth
- Load `data/lake/evaluator_team_cuts.parquet`.
- Compute the mean `scope_applicability_mean` and `technical_complexity_mean` across all cuts for each team-semester.
- Keep the evaluator metrics strictly at team-semester granularity and preserve missingness when a team has incomplete evaluation coverage.

## 5. Final Consolidation (Redesigned Team-Level DataFrame)
- Merge the Git-derived churn metrics and evaluator metrics into a single pandas DataFrame keyed strictly by `ID_Equipe` and `Semestre`.
- Add the planning-quality LLM signal as a team-level column.
- Preserve NaNs gracefully for missing semesters or incomplete coverage without introducing fabricated defaults.
- The final team-level table is structured as a proper `team_semester` dataset and is exported to `paper_v4/advanced_metrics/outputs/team_level_signals.csv`.
- The cohort friction artifact is stored separately and not included in this team-level DataFrame.

# Implementation Requirements
- The script must be a single monolithic file: `paper_v4/12_paper_signals_extractor.py` or, if the project convention expects it at project root, `12_paper_signals_extractor.py` from the repo root. The final artifact destination is still under `paper_v4/advanced_metrics/`.
- All prompts must be defined in a centralized module, preferably `paper_v4/advanced_metrics/llm_prompts.py`.
- Parse LLM JSON defensively; any malformed or missing JSON must be logged and handled explicitly rather than silently defaulted.
- Each result written to disk should be accompanied by structured metadata and a clear log entry.
- The script must be robust to repeated execution, preserving all existing cache and ledger entries unless the user explicitly deletes them.
- Use proper type hints, logging, and exception handling with a fail-fast pattern on missing required inputs.

# Expected Final Outputs
- `paper_v4/advanced_metrics/outputs/team_level_signals.csv`
- `paper_v4/advanced_metrics/outputs/cohort_temporal_friction.csv`
- `paper_v4/advanced_metrics/llm_cache/llm_results_cache.json`
- `paper_v4/advanced_metrics/llm_cache/llm_call_history.csv`
- `paper_v4/advanced_metrics/logs/YYYYMMDD_HHMMSS_12_paper_signals_extractor.log`

Generate the complete, robust Python script, including all necessary imports, type hints, and exception handling for JSON parsing of the LLM outputs.