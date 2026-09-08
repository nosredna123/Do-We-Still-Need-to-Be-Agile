"""Strict qualitative mining primitives for Phase 2."""

from __future__ import annotations

import json
import re
import argparse
import logging
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from pipeline_config import NLP_ENUMS, NLP_SCORE_SCALES, STUDENT_TEXT_QUESTION_REGISTRY
from phase2_contracts import load_phase2_inputs, validate_phase1_contracts
from pipeline_core import (
    invalidate_stale_artifact,
    is_current_artifact,
    phase2_input_checksum,
    write_artifact_metadata,
)

logger = logging.getLogger(__name__)


ALIAS_STRATEGIES = {
    "coalesce_without_conflict",
    "prefer_highest_suffix",
    "concatenate_with_separator",
}
REQUIRED_REGISTRY_FIELDS = {
    "question_id",
    "construct",
    "aliases",
    "required_scopes",
    "duplicate_strategy",
    "conflict_strategy",
    "registry_version",
}


def _strict_int(value: Any, field: str) -> int:
    scale = NLP_SCORE_SCALES[field]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field} must be an integer")
    if not scale["minimum"] <= value <= scale["maximum"]:
        raise ValueError(f"{field} is outside its configured scale")
    return value


def parse_student_llm_response(response: str) -> dict[str, Any]:
    """Parse and validate one strict student NLP JSON response."""
    try:
        value = json.loads(response)
    except json.JSONDecodeError as error:
        raise ValueError("LLM response must be JSON") from error
    if not isinstance(value, dict):
        raise ValueError("LLM response must be an object")
    required = ("sentiment_score", "cognitive_load_score", "ai_dependency_score", "methodological_orientation", "planning_debt_signal")
    if any(field not in value for field in required):
        raise ValueError("LLM response is missing a required field")
    result = {field: _strict_int(value[field], field) for field in required[:3]}
    for field in required[3:]:
        if value[field] not in NLP_ENUMS[field]:
            raise ValueError(f"{field} has an invalid enum value")
        result[field] = value[field]
    return result


def parse_transcript_llm_response(response: str) -> dict[str, Any]:
    """Parse the strict, non-textual fields returned for a transcript session."""
    try:
        value = json.loads(response)
    except json.JSONDecodeError as error:
        raise ValueError("LLM response must be JSON") from error
    required = ("coordination_friction_score", "rework_signal_score", "planning_clarity_score", "integration_risk_signal", "dominant_topics")
    if not isinstance(value, dict) or any(field not in value for field in required):
        raise ValueError("Transcript response is missing a required field")
    for field in required[:3]:
        if isinstance(value[field], bool) or not isinstance(value[field], int) or not 0 <= value[field] <= 4:
            raise ValueError(f"{field} must be an integer from 0 to 4")
    if not isinstance(value["integration_risk_signal"], str) or not value["integration_risk_signal"].strip():
        raise ValueError("integration_risk_signal must be non-empty")
    if not isinstance(value["dominant_topics"], list) or not all(isinstance(item, str) for item in value["dominant_topics"]):
        raise ValueError("dominant_topics must be a list of strings")
    return value


def _normalize_for_conflict(value: Any) -> str | None:
    """Normalize only whitespace for alias conflict comparison."""
    if pd.isna(value):
        return None
    normalized = re.sub(r"\s+", " ", str(value).strip())
    return normalized or None


def _validate_question_registry(registry: dict[str, dict[str, Any]]) -> None:
    """Validate the versioned registry shape before reading response values."""
    for question_id, definition in registry.items():
        missing = REQUIRED_REGISTRY_FIELDS - set(definition)
        if missing:
            raise ValueError(f"{question_id} registry missing fields: {sorted(missing)}")
        if definition["question_id"] != question_id:
            raise ValueError(f"{question_id} question_id does not match registry key")
        if not isinstance(definition["aliases"], list) or not definition["aliases"]:
            raise ValueError(f"{question_id} aliases must be non-empty")
        if definition["duplicate_strategy"] not in ALIAS_STRATEGIES:
            raise ValueError(f"{question_id} has invalid duplicate_strategy")
        if definition["conflict_strategy"] not in {"reject_on_conflict", "resolve_automatically"}:
            raise ValueError(f"{question_id} has invalid conflict_strategy")
        if not isinstance(definition["required_scopes"], list):
            raise ValueError(f"{question_id} required_scopes must be a list")


def _scope_requirement(definition: dict[str, Any], semester: Any, marker: Any) -> str:
    """Return the declared requirement for one semester and temporal cut."""
    for scope in definition["required_scopes"]:
        if scope.get("Semestre") == semester and scope.get("temporal_marker") == marker:
            requirement = scope.get("requirement")
            if requirement not in {"required", "optional", "unavailable"}:
                raise ValueError("required_scopes contains an invalid requirement")
            return requirement
    return "optional"


def _select_alias_value(
    values: list[tuple[str, Any]],
    definition: dict[str, Any],
    question_id: str,
) -> tuple[str, str, str, int]:
    """Resolve populated aliases according to the declared duplicate strategy."""
    normalized = [(column, _normalize_for_conflict(value), value) for column, value in values]
    distinct = {item[1] for item in normalized}
    strategy = definition["duplicate_strategy"]
    if len(distinct) > 1:
        if strategy == "coalesce_without_conflict":
            raise ValueError(f"conflicting aliases for {question_id}")
        if definition["conflict_strategy"] != "resolve_automatically":
            raise ValueError(f"conflicting aliases for {question_id}")
    if strategy == "prefer_highest_suffix":
        selected = max(normalized, key=lambda item: int(re.search(r"\.(\d+)$", item[0]).group(1)) if re.search(r"\.(\d+)$", item[0]) else 0)
        overwritten = max(0, len(values) - 1)
        resolution = "prefer_highest_suffix" if overwritten else "none"
    elif strategy == "concatenate_with_separator":
        selected = (values[0][0], " | ".join(str(item[2]).strip() for item in normalized), values[0][2])
        overwritten = 0
        resolution = "concatenate_with_separator" if len(values) > 1 else "none"
    else:
        selected = normalized[0]
        overwritten = 0
        resolution = "none"
    answer = str(selected[2]).strip()
    return selected[0], answer, resolution, overwritten


def catalog_student_prompts(frame: pd.DataFrame, registry: dict[str, dict[str, Any]]) -> pd.DataFrame:
    """Convert registered student text columns to a private long DataFrame.

    Args:
        frame: An anonymized ``student_responses`` contract DataFrame.
        registry: Versioned canonical question definitions.

    Returns:
        Long private prompt DataFrame with a ``catalog_audit`` attribute.

    Raises:
        ValueError: If required metadata, registry, aliases, scopes, or conflicts
            violate the declared contract.
    """
    required = {"Semestre", "temporal_marker", "source_file"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"student_responses missing columns: {sorted(missing)}")
    _validate_question_registry(registry)
    if frame["source_file"].isna().any() or frame["source_file"].astype(str).str.strip().eq("").any():
        raise ValueError("student_responses source_file must be non-empty")
    rows: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []
    for index, record in frame.reset_index(drop=True).iterrows():
        for question_id, definition in registry.items():
            aliases = [alias for alias in definition["aliases"] if alias in frame.columns]
            requirement = _scope_requirement(definition, record["Semestre"], record["temporal_marker"])
            if requirement == "unavailable":
                continue
            if not aliases and requirement == "required":
                raise ValueError(f"required question {question_id} has no alias column")
            values = [(alias, record[alias]) for alias in aliases if _normalize_for_conflict(record[alias]) is not None]
            if not values:
                if requirement == "required":
                    raise ValueError(f"required question {question_id} has no answer")
                continue
            source_column, answer, resolution, overwritten = _select_alias_value(values, definition, question_id)
            rows.append({"student_response_id": f"{record['source_file']}:{index}", "Semestre": record["Semestre"], "temporal_marker": record["temporal_marker"], "source_file": record["source_file"], "question_id": question_id, "construct": definition["construct"], "original_column": source_column, "answer_text": answer, "duplicate_strategy": definition["duplicate_strategy"], "conflict_resolution": resolution, "question_registry_version": definition["registry_version"]})
            audit.append({"Semestre": record["Semestre"], "temporal_marker": record["temporal_marker"], "source_file": record["source_file"], "question_id": question_id, "aliases_used": [item[0] for item in values], "answer_count": 1, "overwritten_count": overwritten, "conflicts_detected": int(len({_normalize_for_conflict(item[1]) for item in values}) > 1)})
    result = pd.DataFrame(rows)
    result.attrs["catalog_audit"] = audit
    return result


def write_student_prompt_catalog(
    prompts: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Write the private catalog intermediate with resumable metadata.

    Args:
        prompts: Private long DataFrame returned by cataloging.
        output_path: Private output below a ``.private`` directory.
        source_checksum: Checksum of contracts and registry inputs.
        options: Effective catalog options stored in the sidecar.

    Raises:
        ValueError: If the output is public or the catalog is empty.
    """
    if output_path.parent.name != ".private":
        raise ValueError("student prompt catalog must be written below a .private directory")
    if prompts.empty:
        raise ValueError("student prompt catalog is empty")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if is_current_artifact(output_path, source_checksum):
        return
    invalidate_stale_artifact(output_path, source_checksum)
    prompts.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="student-prompt-catalog-v1",
        options=options,
    )


def main() -> None:
    """Catalog anonymized student responses into the private NLP intermediate."""
    parser = argparse.ArgumentParser(description="Catalog Phase 2 student text prompts")
    parser.add_argument("--lake-dir", type=Path, default=Path("data/lake"))
    parser.add_argument(
        "--contract-report",
        type=Path,
        default=Path("data/analysis/phase2_contract_report.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/analysis/.private/student_prompt_catalog.parquet"),
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not args.contract_report.exists():
        raise FileNotFoundError(f"Contract report not found: {args.contract_report}")
    report = json.loads(args.contract_report.read_text(encoding="utf-8"))
    if report.get("status") != "success":
        raise ValueError("Phase 2 contract report is not successful")
    inputs = load_phase2_inputs(args.lake_dir)
    validate_phase1_contracts(inputs)
    options = {
        "stage": "student_catalog",
        "registry_version": "student-text-v1",
    }
    source_checksum = phase2_input_checksum(
        args.lake_dir,
        [Path(__file__).with_name("pipeline_config.py")],
        options,
    )
    if args.force:
        invalidate_stale_artifact(args.output, "force-regeneration")
    prompts = catalog_student_prompts(
        inputs["student_responses"], STUDENT_TEXT_QUESTION_REGISTRY
    )
    write_student_prompt_catalog(
        prompts,
        args.output,
        source_checksum=source_checksum,
        options=options,
    )
    logger.info("Cataloged %s private student prompts", len(prompts))


def mine_student_prompts(prompts: pd.DataFrame, backend: Callable[[str], str]) -> pd.DataFrame:
    """Mine private student prompts using an injected deterministic backend."""
    rows = []
    for record in prompts.to_dict("records"):
        result = parse_student_llm_response(backend(record["answer_text"]))
        rows.append({**{key: record[key] for key in ("student_response_id", "Semestre", "temporal_marker")}, "unit_of_analysis": "student_response", **result, "score_scale_version": "v1", "status": "success"})
    return pd.DataFrame(rows)


def aggregate_textual_cut_signals(students: pd.DataFrame, transcripts: pd.DataFrame) -> pd.DataFrame:
    """Aggregate student and transcript scores by semester and temporal cut."""
    keys = ["Semestre", "temporal_marker"]
    student = students.groupby(keys).agg(ie_student_cognitive_load_mean=("cognitive_load_score", "mean"), ie_student_sentiment_mean=("sentiment_score", "mean"), ie_student_ai_dependency_mean=("ai_dependency_score", "mean"), student_n=("student_response_id", "nunique")).reset_index()
    transcript = transcripts.groupby(keys).agg(ie_transcript_coordination_friction_mean=("coordination_friction_score", "mean"), ie_transcript_rework_signal_mean=("rework_signal_score", "mean"), transcript_session_n=("session_id", "nunique")).reset_index()
    result = student.merge(transcript, on=keys, how="outer", validate="one_to_one")
    result["unit_of_analysis"] = "cut_context"
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()