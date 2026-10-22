# Plan — "LLM Usage in Data Extraction, Processing, and Metrics" subsection (paper_v8)

Status: IMPLEMENTED (2026-09-23). LaTeX subsection drafted in
`paper_v8/latex_code/main.tex` (`\subsection{LLM Usage in Data Extraction,
Processing, and Metrics}`, `\label{sec:llm-usage}`), placed after
`sec:advanced-metrics` and before `\section{Results}`. New script
`paper_v8/scripts/llm_usage/aggregate_llm_calls.py` (+ its `_paths.py`
helper) writes `paper_v8/data/llm_usage/llm_calls_metric_bound.csv` (1,134
rows: 1,122 Survey Coding + 9 Planning-Quality Scoring + 3
Coordination-Friction Scoring; mock-model test rows excluded). All three
tasks turned out to be sourced from the single private ledger
(`data/analysis/.private/llm_call_ledger.parquet`), simplifying the
two-source design originally sketched in §4 below.

## 0. Placement and scope

New `\subsection` in `sec:method`, placed **after** "Advanced Metrics
Operationalization" (`sec:advanced-metrics`) and before `\section{Results}`.
Purpose: methodological transparency and reproducibility disclosure for every
LLM-assisted step used anywhere in data extraction, processing, and metric
computation (M1–M9 and their upstream inputs). Written in the same
jargon-light, process-first style as `sec:advanced-metrics` (visible text
describes what was done in plain terms; `% PROVENANCE` comments carry
repo-specific paths/scripts for audit purposes).

## 1. Verified facts (research complete, 2026-09-23; ledger gap resolved 2026-09-23)

- **Survey Coding ledger gap, now resolved.** An earlier pass found only 3
  `mock-model` rows under the `student_nlp:` prefix in
  `data/analysis/.private/llm_call_ledger.parquet`, with `student_nlp.parquet`
  and `transcript_nlp.parquet` themselves containing all-zero/`insufficient_evidence`
  placeholder data despite being labeled `model=gpt-4o-mini`. Root cause: a
  stub/placeholder result had been persisted as the "final" artifact for both
  files, never replaced by a real run. This was fixed by re-running
  `04_nlp_qualitative_miner.py` (and the downstream `metrics`/`stats`/
  `narrative-audit`/`cross-evidence`/`cross-evidence-report` stages) with the
  real `openai` backend. The ledger now contains 1,122 real `student_nlp`
  calls and 100 real `transcript_nlp` calls (all `gpt-4o-mini`, `status=success`),
  and `student_nlp.parquet`/`transcript_nlp.parquet`/`textual_cut_signals.parquet`
  now show real score variance. **The Survey Coding task in §4's aggregation
  script now has genuine per-call data to draw from**, closing the gap noted
  below when this plan was first drafted.
- **Single centralized gateway.** All LLM calls in the repository route
  through one gateway module that talks to the OpenAI API directly (Chat
  Completions API for text tasks, Audio Transcriptions API for Whisper). No
  call bypasses this gateway.
- **Two models only**: `gpt-4o-mini` (all text scoring/coding/report-writing
  tasks, temperature fixed at 0 for determinism) and `whisper-1` (audio
  transcription, no temperature parameter).
- **Every call is persisted** to a structured ledger before/after execution,
  recording: a caller-supplied observation/correlation id, the operation and
  model, request/response text (and their hashes), token usage, wall-clock
  duration, estimated cost, and success/error status. This is what lets us
  describe the process as "centralized and fully logged," per your request.
- **Seven distinct LLM tasks exist in the repository**, but per your decision
  this subsection reports **only the three tasks whose output directly feeds
  one of M1--M9** (all others — audio transcription, PII-NER, transcript-
  chunk coding, and the two narrative-report-writing tasks — are upstream
  data-collection/anonymization infrastructure or background reporting, and
  are out of scope here):
  1. **Survey Coding** — per-response LLM scoring of student free-text
     answers (ordinal 0–4 scores incl. `ai_dependency_score`) — feeds M1
     (AI-Dependency Trajectory).
  2. **Coordination-Friction Scoring** — per-cut, cohort-pooled transcript
     scoring (1–10 scale) — feeds M5 (Coordination-Friction Trajectory).
  3. **Planning-Quality Scoring** — per-team-semester scoring of $T_1$
     commit-message text (1–10 scale) — feeds M6 ($T_1$ Planning-Quality
     Score), which in turn is the basis of M7 and M9.
- **Volume/cost**: confirmed exact counts and total cost internally, but per
  your decision we will describe volume **qualitatively** in the paper (e.g.,
  "several hundred calls across all tasks, at a total cost of a few tenths of
  a US dollar") rather than publishing exact figures.
- **Human review**: per your confirmation, every LLM output used in this
  study was subsequently reviewed by the research team (an independent peer
  panel), which read the outputs and manually adjusted a small number of
  minor errors where needed; the number of corrections was not material. This
  review was conducted outside this code repository. The paper will state
  this in general terms, without granular methodology detail (no reviewer
  count, no per-task breakdown, no agreement statistics), per your
  instruction to keep this paragraph general rather than procedural.

## 2. Proposed subsection content

1. **Opening paragraph**: single centralized gateway, two models, full
   request/response persistence, deterministic decoding (temperature 0) for
   every scoring/coding task.
2. **Prompt catalog table** (one row per task, restricted to the three tasks
   that directly feed a metric), columns: Task (short display name), Model,
   Granularity, Feeds Metric, Prompt (short verbatim excerpt).
3. **Example call/response pair(s)**: the two already-anonymized examples
   already surfaced in this conversation (a low-scoring $T_1$ planning-quality
   call, and a $T_1$ coordination-friction cohort call), quoted as compact
   blocks.
4. **Persistence/reproducibility paragraph**: explain the ledger (what's
   captured per call) without exposing raw counts, framed as "this supports
   full auditability of every LLM-derived value in this paper."
5. **Human-review paragraph**: general statement (per your wording) that all
   LLM outputs used in this study were reviewed by the research team, with a
   small number of minor errors manually corrected; no material corrections
   were required. No procedural or quantitative detail beyond that.

## 3. Resolved decisions

1. **Short display names** will be used in the table (Survey Coding,
   Coordination-Friction Scoring, Planning-Quality Scoring) rather than
   internal task labels/observation-id prefixes.
2. **Example call/response pairs**: reuse the actual already-anonymized
   examples already found (T1 planning score for a low-scoring team, and the
   T1 coordination-friction cohort call), as originally suggested.
3. **Scope restricted to metric-bound tasks only.** Audio transcription,
   PII-NER, transcript-chunk coding, and both narrative-report-writing tasks
   are excluded from this subsection entirely — only the three tasks that
   directly produce a value consumed by M1--M9 are reported.
4. **Human-review paragraph kept general**, per your wording: the research
   team reviewed all LLM outputs and manually adjusted a small number of
   minor errors; the number of fixes was not material. No reviewer count,
   procedure detail, or agreement statistics will be stated in the paper.

## 4. New: LLM-calls aggregation script

All artifacts for this subsection live under a dedicated subtree of
`paper_v8/`, kept separate from the M1--M9 metric scripts/outputs for clarity:

- `paper_v8/scripts/llm_usage/aggregate_llm_calls.py` (new script)
- `paper_v8/data/llm_usage/llm_calls_metric_bound.csv` (new output)

The script writes one row per successful LLM call for the three
metric-bound tasks only, unifying two heterogeneous sources into one schema:

- **Survey Coding** rows: read from
  `data/analysis/.private/llm_call_ledger.parquet`, filtered to
  `operation == "chat.completions.create"` and `observation_id` prefixed
  `student_nlp:`, `status == "success"`.
- **Coordination-Friction Scoring** and **Planning-Quality Scoring** rows:
  read from `paper_v4/advanced_metrics/llm_cache/llm_call_history.csv`,
  filtered to `task_type in {"cohort_coordination_friction", "planning"}`,
  `status == "success"`.

Unified output columns: `task` (short display name), `metric_fed`
(M1/M5/M6), `identifier` (student-response id, or `ID_Equipe|Semestre`, or
`Semestre|temporal_marker`, depending on the task's grain), `model`,
`temperature`, `prompt_text`, `response_text`, `parsed_value`, `status`,
`source_artifact` (which underlying file the row came from).

Per your decisions: only the 3 metric-bound tasks, only successful calls,
one combined CSV, and full prompt/response text included (no separate
privacy-audit pass requested). Note: the Survey Coding source lives under
`data/analysis/.private/`, a directory otherwise treated as restricted; since
its text was already anonymized upstream (NER + redaction, per the Data
Anonymization and Privacy paragraph in Section~\ref{sec:method}), and you've
confirmed no additional audit is needed, this script will read from it
read-only and copy only the already-anonymized text into the new
`paper_v8/data/llm_usage/` output.

### Updated `paper_v8/` layout for this subsection

```
paper_v8/
  LLM_USAGE_PLAN.md
  scripts/
    metrics/                      (existing, M1--M9 scripts, unchanged)
    llm_usage/
      aggregate_llm_calls.py      (new)
  data/
    m1_ai_dependency_trajectory.csv ...  (existing, M1--M9 outputs, unchanged)
    llm_usage/
      llm_calls_metric_bound.csv  (new)
```

Next step: draft the LaTeX subsection (with `% PROVENANCE` comments analogous
to `sec:advanced-metrics`), restricted to the three metric-bound LLM tasks
above, plus the persistence and human-review paragraphs.
