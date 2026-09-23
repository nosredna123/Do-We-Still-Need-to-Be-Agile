"""Aggregate metric-bound LLM calls into one auditable CSV.

Definition
----------
Every LLM call in this repository is persisted to a single ledger
(`data/analysis/.private/llm_call_ledger.parquet`), regardless of which
pipeline stage issued it. This script filters that ledger down to the three
tasks whose output directly feeds one of M1--M9, and reshapes them into one
flat, human-readable table with a uniform schema:

    - Survey Coding            (observation_id prefix "student_nlp:")   -> M1
    - Coordination-Friction Scoring (observation_id prefix
      "<Semestre>_cohort_<cut>_CoordinationFriction")                   -> M5
    - Planning-Quality Scoring (observation_id prefix
      "<Semestre>_<ID_Equipe>_Planning")                                -> M6

Only successful calls are included, and the handful of `mock-model` test
fixture rows (from unit tests, not real analysis runs) are excluded. Prompt/
response text is copied verbatim; it was already anonymized upstream (NER +
redaction, see the Data Anonymization and Privacy paragraph in the
Methodology), so no further redaction is applied here.

Source artifact (read-only)
---------------------------
    data/analysis/.private/llm_call_ledger.parquet
    (append-only call ledger written by llm_gateway.py; every LLM call in the
    repository, from every stage, is recorded here with request/response
    text, token usage, cost, and timing)

Output
------
    paper_v8/data/llm_usage/llm_calls_metric_bound.csv
    columns: task, metric_fed, identifier, model, temperature, prompt_text,
             response_text, parsed_value, status, source_artifact
"""

from __future__ import annotations

import json
import re

import pandas as pd
from _paths import ensure_llm_usage_output_dir, PROJECT_ROOT

LEDGER_PATH = PROJECT_ROOT / "data" / "analysis" / ".private" / "llm_call_ledger.parquet"
OUTPUT_PATH = ensure_llm_usage_output_dir() / "llm_calls_metric_bound.csv"

SURVEY_CODING_PATTERN = re.compile(r"^student_nlp:")
FRICTION_PATTERN = re.compile(r"^(?P<semestre>[\w.]+)_cohort_(?P<cut>T\d)_CoordinationFriction$")
PLANNING_PATTERN = re.compile(r"^(?P<semestre>[\w.]+)_(?P<team>TEAM_\d+)_Planning$")


def _temperature(request_options_json: str) -> float | None:
    """Extract the decoding temperature from a ledger row's request options."""
    try:
        return json.loads(request_options_json).get("temperature")
    except (TypeError, json.JSONDecodeError):
        return None


def _parsed_value(task: str, response_text: str) -> object:
    """Extract the single numeric score this task's response is expected to carry."""
    try:
        payload = json.loads(response_text)
    except (TypeError, json.JSONDecodeError):
        return None
    if task == "Survey Coding":
        return payload.get("ai_dependency_score")
    if task == "Coordination-Friction Scoring":
        return payload.get("coordination_friction")
    if task == "Planning-Quality Scoring":
        return payload.get("t1_planning_score")
    return None


def classify_row(observation_id: str) -> tuple[str, str, str] | None:
    """Classify one ledger row into (task, metric_fed, identifier), or None if out of scope."""
    if SURVEY_CODING_PATTERN.match(observation_id):
        return "Survey Coding", "M1", observation_id
    match = FRICTION_PATTERN.match(observation_id)
    if match:
        identifier = f"{match['semestre']}|{match['cut']}"
        return "Coordination-Friction Scoring", "M5", identifier
    match = PLANNING_PATTERN.match(observation_id)
    if match:
        identifier = f"{match['team']}|{match['semestre']}"
        return "Planning-Quality Scoring", "M6", identifier
    return None


def build_aggregate(ledger: pd.DataFrame) -> pd.DataFrame:
    """Filter the ledger to metric-bound, successful, non-test calls and unify their schema."""
    successful = ledger[(ledger["status"] == "success") & (ledger["model"] != "mock-model")]
    rows: list[dict[str, object]] = []
    for _, row in successful.iterrows():
        classification = classify_row(str(row["observation_id"]))
        if classification is None:
            continue
        task, metric_fed, identifier = classification
        rows.append(
            {
                "task": task,
                "metric_fed": metric_fed,
                "identifier": identifier,
                "model": row["model"],
                "temperature": _temperature(row["request_options_json"]),
                "prompt_text": row["prompt_text"],
                "response_text": row["response_text"],
                "parsed_value": _parsed_value(task, row["response_text"]),
                "status": row["status"],
                "source_artifact": "data/analysis/.private/llm_call_ledger.parquet",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    ledger = pd.read_parquet(LEDGER_PATH)
    aggregate = build_aggregate(ledger)
    aggregate.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(aggregate)} rows to {OUTPUT_PATH}")
    print(aggregate["task"].value_counts().to_string())


if __name__ == "__main__":
    main()
