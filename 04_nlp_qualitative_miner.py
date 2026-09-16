"""Strict qualitative mining primitives for Phase 2."""

from __future__ import annotations

import json
import hashlib
import re
import argparse
import logging
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from pipeline_config import (
    MODEL_CONFIG,
    NLP_ENUMS,
    NLP_SCORE_SCALES,
    STUDENT_TEXT_QUESTION_REGISTRY,
    TRANSCRIPT_CHUNK_OVERLAP_TOKENS,
    TRANSCRIPT_CHUNK_TOKENS,
    TRANSCRIPT_EVIDENCE_MAX_CHARS,
)
from phase2_contracts import load_phase2_inputs, validate_phase1_contracts
from pipeline_core import (
    invalidate_stale_artifact,
    input_checksum,
    is_current_artifact,
    load_project_environment,
    write_artifact_metadata,
)
from pipeline_prompts import (
    STUDENT_NLP_PROMPT,
    STUDENT_NLP_PROMPT_VERSION,
    STUDENT_NLP_RESPONSE_SCHEMA_VERSION,
    TRANSCRIPT_NLP_PROMPT,
    TRANSCRIPT_NLP_PROMPT_VERSION,
    TRANSCRIPT_NLP_RESPONSE_SCHEMA_VERSION,
    TRANSCRIPT_NLP_SYSTEM_PROMPT,
)
from llm_gateway import LLMCallGateway
from pipeline_statistics import flatten_distribution_summary, summarize_numeric_distribution

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
    if set(value) != set(required):
        raise ValueError("LLM response contains unexpected or missing fields")
    if any(field not in value for field in required):
        raise ValueError("LLM response is missing a required field")
    result = {field: _strict_int(value[field], field) for field in required[:3]}
    for field in required[3:]:
        if value[field] not in NLP_ENUMS[field]:
            raise ValueError(f"{field} has an invalid enum value")
        result[field] = value[field]
    return result


def parse_transcript_llm_response(response: str) -> dict[str, Any]:
    """Parse and validate one strict transcript-session JSON response."""
    try:
        value = json.loads(response)
    except json.JSONDecodeError as error:
        raise ValueError("LLM response must be JSON") from error
    required = (
        "coordination_friction_score",
        "rework_signal_score",
        "planning_clarity_score",
        "integration_risk_signal",
        "dominant_topics",
        "evidence_summary_private",
    )
    if not isinstance(value, dict) or set(value) != set(required):
        raise ValueError("Transcript response is missing a required field")
    for field in required[:3]:
        _strict_int(value[field], field)
    if value["integration_risk_signal"] not in NLP_ENUMS["integration_risk_signal"]:
        raise ValueError("integration_risk_signal has an invalid enum value")
    topics = value["dominant_topics"]
    if not isinstance(topics, list) or len(topics) > 5 or not all(
        isinstance(item, str) and item in NLP_ENUMS["dominant_topic"] for item in topics
    ):
        raise ValueError("dominant_topics contains invalid values")
    evidence = value["evidence_summary_private"]
    if not isinstance(evidence, str) or len(evidence) > TRANSCRIPT_EVIDENCE_MAX_CHARS:
        raise ValueError("evidence_summary_private must be a bounded string")
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
    """Catalog and mine anonymized student responses for Phase 2."""
    parser = argparse.ArgumentParser(description="Mine Phase 2 student responses")
    parser.add_argument("--lake-dir", type=Path, default=Path("data/lake"))
    parser.add_argument(
        "--contract-report",
        type=Path,
        default=Path("data/analysis/phase2_contract_report.json"),
    )
    parser.add_argument(
        "--catalog-output",
        type=Path,
        default=Path("data/analysis/.private/student_prompt_catalog.parquet"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/analysis/student_nlp.parquet"),
    )
    parser.add_argument(
        "--transcript-output",
        type=Path,
        default=Path("data/analysis/transcript_nlp.parquet"),
    )
    parser.add_argument(
        "--textual-cut-signals-output",
        type=Path,
        default=Path("data/analysis/textual_cut_signals.parquet"),
    )
    parser.add_argument("--backend", choices=("openai", "mock"), default="openai")
    parser.add_argument(
        "--model",
        default=str(MODEL_CONFIG["qualitative_mining"]["model"]),
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
    catalog_options = {
        "stage": "student_catalog",
        "registry_version": "student-text-v1",
        "question_registry": STUDENT_TEXT_QUESTION_REGISTRY,
    }
    source_checksum = input_checksum(
        [
            args.lake_dir / "student_responses.parquet",
            args.lake_dir / "student_responses.parquet.metadata.json",
        ],
        catalog_options,
    )
    if args.force:
        invalidate_stale_artifact(args.catalog_output, "force-regeneration")
        invalidate_stale_artifact(args.output, "force-regeneration")
        invalidate_stale_artifact(args.transcript_output, "force-regeneration")
        invalidate_stale_artifact(args.textual_cut_signals_output, "force-regeneration")
    if is_current_artifact(args.catalog_output, source_checksum):
        prompts = pd.read_parquet(args.catalog_output)
    else:
        prompts = catalog_student_prompts(
            inputs["student_responses"], STUDENT_TEXT_QUESTION_REGISTRY
        )
        write_student_prompt_catalog(
            prompts,
            args.catalog_output,
            source_checksum=source_checksum,
            options=catalog_options,
        )

    client = None

    nlp_options = {
        "stage": "student_nlp",
        "backend": args.backend,
        "model": args.model,
        "prompt_version": STUDENT_NLP_PROMPT_VERSION,
        "response_schema_version": STUDENT_NLP_RESPONSE_SCHEMA_VERSION,
        "score_scales": {
            name: NLP_SCORE_SCALES[name]
            for name in ("sentiment_score", "cognitive_load_score", "ai_dependency_score")
        },
        "enums": {
            name: sorted(NLP_ENUMS[name])
            for name in ("methodological_orientation", "planning_debt_signal")
        },
    }
    nlp_checksum = input_checksum(
        [args.catalog_output, Path(__file__).with_name("pipeline_prompts.py")],
        nlp_options,
    )
    checkpoint_path = args.output.with_name(f"{args.output.name}.partial")
    if not args.force and is_current_artifact(args.output, nlp_checksum):
        logger.info("Student NLP artifact is current: %s", args.output)
    else:
        client = None
        if args.backend == "openai":
            load_project_environment()
            try:
                from openai import OpenAI
            except ImportError as error:
                raise RuntimeError("openai package is not installed") from error
            client = OpenAI()
        student_backend = (
            (lambda prompt: openai_student_backend(prompt, client=client, model=args.model))
            if client is not None
            else mock_student_backend
        )
        results = mine_student_prompts(
            prompts,
            student_backend,
            model=args.model,
            checkpoint_path=checkpoint_path,
            checkpoint_checksum=nlp_checksum,
            prior_output_path=args.output,
        )
        write_student_nlp(
            results,
            args.output,
            source_checksum=nlp_checksum,
            options=nlp_options,
        )
        invalidate_stale_artifact(checkpoint_path, "completed-final-artifact")
        logger.info("Mined %s student NLP observations", len(results))

    transcript_options = {
        "stage": "transcript_nlp",
        "backend": args.backend,
        "model": args.model,
        "prompt_version": TRANSCRIPT_NLP_PROMPT_VERSION,
        "response_schema_version": TRANSCRIPT_NLP_RESPONSE_SCHEMA_VERSION,
        "chunk_tokens": TRANSCRIPT_CHUNK_TOKENS,
        "chunk_overlap_tokens": TRANSCRIPT_CHUNK_OVERLAP_TOKENS,
        "score_scales": {
            name: NLP_SCORE_SCALES[name]
            for name in (
                "coordination_friction_score",
                "rework_signal_score",
                "planning_clarity_score",
            )
        },
        "enums": {
            "integration_risk_signal": sorted(NLP_ENUMS["integration_risk_signal"]),
            "dominant_topic": sorted(NLP_ENUMS["dominant_topic"]),
        },
    }
    transcript_checksum = input_checksum(
        [
            args.lake_dir / "transcript_sessions.parquet",
            args.lake_dir / "transcript_sessions.parquet.metadata.json",
            Path(__file__).with_name("pipeline_prompts.py"),
        ],
        transcript_options,
    )
    transcript_checkpoint = args.transcript_output.with_name(f"{args.transcript_output.name}.partial")
    if not args.force and is_current_artifact(args.transcript_output, transcript_checksum):
        logger.info("Transcript NLP artifact is current: %s", args.transcript_output)
    else:
        if args.backend == "openai" and client is None:
            load_project_environment()
            try:
                from openai import OpenAI
            except ImportError as error:
                raise RuntimeError("openai package is not installed") from error
            client = OpenAI()
        transcript_backend = (
            (lambda prompt: openai_transcript_backend(prompt, client=client, model=args.model))
            if client is not None
            else mock_transcript_backend
        )
        transcript_results = mine_transcript_sessions(
            inputs["transcript_sessions"],
            transcript_backend,
            model=args.model,
            checkpoint_path=transcript_checkpoint,
            checkpoint_checksum=transcript_checksum,
            prior_output_path=args.transcript_output,
        )
        write_transcript_nlp(
            transcript_results,
            args.transcript_output,
            source_checksum=transcript_checksum,
            options=transcript_options,
        )
        invalidate_stale_artifact(transcript_checkpoint, "completed-final-artifact")
        logger.info("Mined %s transcript NLP observations", len(transcript_results))

    textual_options = {
        "stage": "textual_cut_signals",
        "merge_strategy": "outer",
        "contract_version": "textual-cut-signals-v2",
        "summary_version": "distribution-summary-v1",
        "statistical_decisions": {
            "std_ddof": 1,
            "quantile_method": "linear",
            "scale_treatment": "ordinal_with_interval_summary",
        },
        "score_scales": {
            name: NLP_SCORE_SCALES[name]
            for name in (
                "sentiment_score",
                "cognitive_load_score",
                "ai_dependency_score",
                "coordination_friction_score",
                "rework_signal_score",
                "planning_clarity_score",
            )
        },
        "enums": {
            "integration_risk_signal": sorted(NLP_ENUMS["integration_risk_signal"]),
            "dominant_topic": sorted(NLP_ENUMS["dominant_topic"]),
        },
    }
    textual_checksum = input_checksum(
        [
            args.output,
            args.output.with_name(f"{args.output.name}.metadata.json"),
            args.transcript_output,
            args.transcript_output.with_name(f"{args.transcript_output.name}.metadata.json"),
            Path(__file__),
            Path(__file__).with_name("pipeline_statistics.py"),
        ],
        textual_options,
    )
    if not args.force and is_current_artifact(args.textual_cut_signals_output, textual_checksum):
        logger.info("Textual cut signals artifact is current: %s", args.textual_cut_signals_output)
        return
    textual_results = aggregate_textual_cut_signals(
        pd.read_parquet(args.output),
        pd.read_parquet(args.transcript_output),
    )
    invalidate_stale_textual_cut_signals(
        args.textual_cut_signals_output,
        textual_checksum,
    )
    write_textual_cut_signals(
        textual_results,
        args.textual_cut_signals_output,
        source_checksum=textual_checksum,
        options=textual_options,
    )
    logger.info("Aggregated %s textual cut signal observations", len(textual_results))


def build_student_nlp_prompt(record: dict[str, Any]) -> str:
    """Build the versioned prompt for one cataloged student response."""
    return STUDENT_NLP_PROMPT.format(
        question_id=record["question_id"],
        construct=record["construct"],
        answer_text=record["answer_text"],
    )


def mine_student_prompts(
    prompts: pd.DataFrame,
    backend: Callable[[str], str],
    *,
    model: str,
    checkpoint_path: Path | None = None,
    checkpoint_checksum: str | None = None,
    prior_output_path: Path | None = None,
) -> pd.DataFrame:
    """Mine cataloged student prompts using an injected backend.

    Args:
        prompts: Private catalog produced by ``catalog_student_prompts``.
        backend: Callable receiving one versioned prompt and returning JSON.
        model: Effective model identifier recorded per observation.
        checkpoint_path: Optional private Parquet checkpoint written after each
            successful observation.
        checkpoint_checksum: Checksum associated with the checkpoint inputs.
        prior_output_path: Previous final artifact whose compatible observations
            can be reused when the current checksum changed.

    Returns:
        Individual-level NLP scores without the original response text.

    Raises:
        ValueError: If a response is malformed or required prompt columns are
            absent.
    """
    required_columns = {"student_response_id", "Semestre", "temporal_marker", "question_id", "construct", "answer_text"}
    missing = required_columns - set(prompts.columns)
    if missing:
        raise ValueError(f"student prompt catalog missing required columns: {sorted(missing)}")
    if checkpoint_path is not None and checkpoint_checksum is None:
        raise ValueError("checkpoint_checksum is required with checkpoint_path")
    completed_frames: list[pd.DataFrame] = []
    if prior_output_path is not None and prior_output_path.exists():
        metadata_path = prior_output_path.with_name(f"{prior_output_path.name}.metadata.json")
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            prior = pd.read_parquet(prior_output_path)
            required_prior = {
                "student_response_id", "question_id", "Semestre", "temporal_marker",
                "unit_of_analysis", "model", "prompt_version",
                "response_schema_version", "status",
            }
            if (
                metadata.get("status") == "success"
                and metadata.get("contract_version") == "student-nlp-v1"
                and required_prior.issubset(prior.columns)
                and prior["model"].eq(model).all()
                and prior["prompt_version"].eq(STUDENT_NLP_PROMPT_VERSION).all()
                and prior["response_schema_version"].eq(STUDENT_NLP_RESPONSE_SCHEMA_VERSION).all()
                and prior["status"].eq("success").all()
            ):
                completed_frames.append(prior)
                logger.info(
                    "Reusing %s completed student NLP observations from final artifact",
                    len(prior),
                )
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            logger.warning("Ignoring invalid prior student NLP artifact: %s", prior_output_path)
    if checkpoint_path is not None and checkpoint_path.exists():
        metadata_path = checkpoint_path.with_name(f"{checkpoint_path.name}.metadata.json")
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata.get("status") == "partial" and metadata.get("input_checksum") == checkpoint_checksum:
                completed_frames.append(pd.read_parquet(checkpoint_path))
            else:
                invalidate_stale_artifact(checkpoint_path, "checkpoint-is-stale")
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            invalidate_stale_artifact(checkpoint_path, "checkpoint-is-invalid")
    completed = pd.DataFrame()
    if completed_frames:
        completed = pd.concat(completed_frames, ignore_index=True).drop_duplicates(
            subset=["student_response_id", "question_id"], keep="last"
        )
    completed_keys = set()
    if not completed.empty:
        completed_keys = set(zip(completed["student_response_id"], completed["question_id"]))
        logger.info("Resuming %s completed student NLP observations", len(completed))
    total_observations = len(prompts)
    pending_observations = total_observations - len(completed_keys)
    logger.info(
        "Student NLP queue: total=%s completed=%s pending=%s",
        total_observations,
        len(completed_keys),
        pending_observations,
    )
    rows = completed.to_dict("records") if not completed.empty else []
    for record in prompts.to_dict("records"):
        observation_key = (record["student_response_id"], record["question_id"])
        if observation_key in completed_keys:
            logger.info(
                "Skipping completed student NLP observation %s/%s",
                *observation_key,
            )
            continue
        result = parse_student_llm_response(backend(build_student_nlp_prompt(record)))
        observation = {
            **{key: record[key] for key in ("student_response_id", "Semestre", "temporal_marker")},
            "question_id": record["question_id"],
            "unit_of_analysis": "student_response",
            **result,
            "score_scale_version": "v1",
            "model": model,
            "prompt_version": STUDENT_NLP_PROMPT_VERSION,
            "response_schema_version": STUDENT_NLP_RESPONSE_SCHEMA_VERSION,
            "status": "success",
        }
        rows.append(observation)
        completed_keys.add(observation_key)
        if checkpoint_path is not None:
            _write_partial_student_nlp_checkpoint(
                pd.DataFrame(rows), checkpoint_path, str(checkpoint_checksum)
            )
        completed_count = len(completed_keys)
        logger.info(
            "Student NLP progress: completed=%s/%s pending=%s observation=%s/%s",
            completed_count,
            total_observations,
            total_observations - completed_count,
            *observation_key,
        )
    return pd.DataFrame(rows)


def _write_partial_student_nlp_checkpoint(
    results: pd.DataFrame,
    checkpoint_path: Path,
    source_checksum: str,
) -> None:
    """Atomically persist completed individual NLP observations."""
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = checkpoint_path.with_name(f".{checkpoint_path.name}.tmp")
    results.to_parquet(temporary_path, index=False)
    temporary_path.replace(checkpoint_path)
    metadata_path = checkpoint_path.with_name(f"{checkpoint_path.name}.metadata.json")
    metadata_path.write_text(
        json.dumps(
            {
                "input_checksum": source_checksum,
                "status": "partial",
                "contract_version": "student-nlp-v1",
                "completed_observations": len(results),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def write_student_nlp(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Write validated individual NLP scores and their resumable sidecar."""
    required_columns = {
        "student_response_id", "Semestre", "temporal_marker", "question_id", "unit_of_analysis",
        "sentiment_score", "cognitive_load_score", "ai_dependency_score",
        "methodological_orientation", "planning_debt_signal", "score_scale_version",
        "model", "prompt_version", "response_schema_version", "status",
    }
    missing = required_columns - set(results.columns)
    if missing:
        raise ValueError(f"student_nlp output missing required columns: {sorted(missing)}")
    if "answer_text" in results.columns:
        raise ValueError("student_nlp output must not contain answer_text")
    if results.empty:
        raise ValueError("student_nlp output is empty")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if is_current_artifact(output_path, source_checksum):
        return
    invalidate_stale_artifact(output_path, source_checksum)
    results.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="student-nlp-v1",
        options=options,
    )


def mock_student_backend(prompt: str) -> str:
    """Return deterministic insufficient-evidence JSON for offline runs."""
    return json.dumps({
        "sentiment_score": 0,
        "cognitive_load_score": 0,
        "ai_dependency_score": 0,
        "methodological_orientation": "insufficient_evidence",
        "planning_debt_signal": "insufficient_evidence",
    })


def openai_student_backend(prompt: str, *, client: Any, model: str) -> str:
    """Request one strict JSON student analysis from an OpenAI client."""
    config = MODEL_CONFIG["qualitative_mining"]
    gateway = LLMCallGateway(client)
    return gateway.chat_json(
        observation_id=f"student_nlp:{hashlib.sha256(prompt.encode('utf-8')).hexdigest()}",
        model=model,
        system_prompt=STUDENT_NLP_PROMPT,
        user_prompt=prompt,
        request_options={
            "response_format": {"type": str(config["response_format"])},
            "temperature": float(config["temperature"]),
        },
    )


def build_transcript_nlp_prompt(transcript_text: str, *, chunk_number: int | None = None, chunk_total: int | None = None) -> str:
    """Build the versioned prompt for one transcript or transcript chunk."""
    prompt = TRANSCRIPT_NLP_PROMPT.format(transcript_text=transcript_text)
    if chunk_number is not None and chunk_total is not None:
        prompt = f"This is chunk {chunk_number} of {chunk_total}.\n\n{prompt}"
    return prompt


def _transcript_chunks(text: str) -> list[str]:
    """Split text into deterministic word chunks with configured overlap."""
    if TRANSCRIPT_CHUNK_TOKENS <= 0 or not 0 <= TRANSCRIPT_CHUNK_OVERLAP_TOKENS < TRANSCRIPT_CHUNK_TOKENS:
        raise ValueError("transcript chunk configuration is invalid")
    words = text.split()
    if len(words) <= TRANSCRIPT_CHUNK_TOKENS:
        return [text]
    step = TRANSCRIPT_CHUNK_TOKENS - TRANSCRIPT_CHUNK_OVERLAP_TOKENS
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + TRANSCRIPT_CHUNK_TOKENS, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += step
    return chunks


def _load_transcript_checkpoint(
    checkpoint_path: Path | None,
    checkpoint_checksum: str | None,
) -> pd.DataFrame:
    """Load a current partial transcript checkpoint or return an empty frame."""
    if checkpoint_path is None:
        return pd.DataFrame()
    if checkpoint_checksum is None:
        raise ValueError("checkpoint_checksum is required with checkpoint_path")
    if not checkpoint_path.exists():
        return pd.DataFrame()
    metadata_path = checkpoint_path.with_name(f"{checkpoint_path.name}.metadata.json")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("status") == "partial" and metadata.get("input_checksum") == checkpoint_checksum:
            return pd.read_parquet(checkpoint_path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        pass
    invalidate_stale_artifact(checkpoint_path, "checkpoint-is-invalid")
    return pd.DataFrame()


def _write_partial_transcript_checkpoint(
    results: pd.DataFrame,
    checkpoint_path: Path,
    source_checksum: str,
) -> None:
    """Atomically persist completed transcript-session observations."""
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = checkpoint_path.with_name(f".{checkpoint_path.name}.tmp")
    results.to_parquet(temporary_path, index=False)
    temporary_path.replace(checkpoint_path)
    metadata_path = checkpoint_path.with_name(f"{checkpoint_path.name}.metadata.json")
    metadata_path.write_text(
        json.dumps(
            {
                "input_checksum": source_checksum,
                "status": "partial",
                "contract_version": "transcript-nlp-v1",
                "completed_observations": len(results),
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def mine_transcript_sessions(
    sessions: pd.DataFrame,
    backend: Callable[[str], str],
    *,
    model: str,
    checkpoint_path: Path | None = None,
    checkpoint_checksum: str | None = None,
    prior_output_path: Path | None = None,
) -> pd.DataFrame:
    """Mine anonymized transcript sessions with resumable chunk processing.

    Args:
        sessions: Validated transcript-session contract DataFrame.
        backend: Callable receiving a prompt and returning strict JSON.
        model: Effective model identifier recorded per observation.
        checkpoint_path: Optional private partial checkpoint path.
        checkpoint_checksum: Checksum associated with the checkpoint inputs.
        prior_output_path: Previous final artifact whose compatible observations
            can be reused when the current checksum changed.

    Returns:
        One validated NLP observation per transcript session.

    Raises:
        ValueError: If input metadata, text, duplicate keys, or LLM output is invalid.
    """
    required_columns = {
        "session_id", "transcript_file", "Semestre", "temporal_marker",
        "temporal_marker_source", "transcript_text",
    }
    missing = required_columns - set(sessions.columns)
    if missing:
        raise ValueError(f"transcript sessions missing required columns: {sorted(missing)}")
    if sessions["session_id"].isna().any() or sessions["session_id"].astype(str).str.strip().eq("").any():
        raise ValueError("session_id must be non-empty")
    if sessions["transcript_text"].isna().any() or sessions["transcript_text"].astype(str).str.strip().eq("").any():
        raise ValueError("transcript_text must be non-empty")
    observation_columns = ["transcript_file"]
    if sessions.duplicated(observation_columns).any():
        raise ValueError("transcript session observations must be unique")

    completed_frames: list[pd.DataFrame] = []
    if prior_output_path is not None and prior_output_path.exists():
        metadata_path = prior_output_path.with_name(f"{prior_output_path.name}.metadata.json")
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            prior = pd.read_parquet(prior_output_path)
            required_prior = {
                "transcript_file", "session_id", "Semestre", "temporal_marker",
                "unit_of_analysis", "model", "prompt_version",
                "response_schema_version", "status",
            }
            if (
                metadata.get("status") == "success"
                and metadata.get("contract_version") == "transcript-nlp-v1"
                and required_prior.issubset(prior.columns)
                and prior["model"].eq(model).all()
                and prior["prompt_version"].eq(TRANSCRIPT_NLP_PROMPT_VERSION).all()
                and prior["response_schema_version"].eq(TRANSCRIPT_NLP_RESPONSE_SCHEMA_VERSION).all()
                and prior["status"].eq("success").all()
            ):
                completed_frames.append(prior)
                logger.info(
                    "Reusing %s completed transcript NLP observations from final artifact",
                    len(prior),
                )
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
            logger.warning("Ignoring invalid prior transcript NLP artifact: %s", prior_output_path)

    checkpoint = _load_transcript_checkpoint(checkpoint_path, checkpoint_checksum)
    if not checkpoint.empty:
        completed_frames.append(checkpoint)
    completed = pd.DataFrame()
    if completed_frames:
        completed = pd.concat(completed_frames, ignore_index=True).drop_duplicates(
            subset=["transcript_file"], keep="last"
        )
    completed_keys = set()
    if not completed.empty:
        completed_keys = set(completed["transcript_file"])
        logger.info("Resuming %s completed transcript NLP observations", len(completed_keys))
    rows = completed.to_dict("records") if not completed.empty else []
    total = len(sessions)
    logger.info("Transcript NLP queue: total=%s completed=%s pending=%s", total, len(completed_keys), total - len(completed_keys))
    for record in sessions.to_dict("records"):
        key = record["transcript_file"]
        if key in completed_keys:
            logger.info("Skipping completed transcript NLP observation %s", key)
            continue
        chunks = _transcript_chunks(str(record["transcript_text"]))
        chunk_results = []
        for index, chunk in enumerate(chunks, start=1):
            response = backend(build_transcript_nlp_prompt(chunk, chunk_number=index, chunk_total=len(chunks)))
            chunk_results.append(parse_transcript_llm_response(response))
        if len(chunk_results) == 1:
            result = chunk_results[0]
        else:
            consolidation_prompt = (
                "Consolidate these validated transcript chunk analyses into one session analysis. "
                "Return the exact transcript NLP JSON schema, resolving scores conservatively. "
                f"chunk_results={json.dumps(chunk_results, ensure_ascii=False, sort_keys=True)}"
            )
            result = parse_transcript_llm_response(backend(consolidation_prompt))
        observation = {
            **{key: record[key] for key in ("session_id", "transcript_file", "Semestre", "temporal_marker", "temporal_marker_source")},
            "unit_of_analysis": "transcript_session",
            **result,
            "model": model,
            "prompt_version": TRANSCRIPT_NLP_PROMPT_VERSION,
            "response_schema_version": TRANSCRIPT_NLP_RESPONSE_SCHEMA_VERSION,
            "status": "success",
        }
        rows.append(observation)
        completed_keys.add(key)
        if checkpoint_path is not None:
            _write_partial_transcript_checkpoint(pd.DataFrame(rows), checkpoint_path, str(checkpoint_checksum))
        logger.info("Transcript NLP progress: completed=%s/%s pending=%s session=%s", len(completed_keys), total, total - len(completed_keys), record["session_id"])
    return pd.DataFrame(rows)


def write_transcript_nlp(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Write validated transcript-session NLP results and metadata."""
    required_columns = {
        "session_id", "transcript_file", "Semestre", "temporal_marker",
        "temporal_marker_source", "unit_of_analysis", "coordination_friction_score",
        "rework_signal_score", "planning_clarity_score", "integration_risk_signal",
        "dominant_topics", "evidence_summary_private", "model", "prompt_version",
        "response_schema_version", "status",
    }
    missing = required_columns - set(results.columns)
    if missing:
        raise ValueError(f"transcript_nlp output missing required columns: {sorted(missing)}")
    if "transcript_text" in results.columns:
        raise ValueError("transcript_nlp output must not contain transcript_text")
    if results.empty:
        raise ValueError("transcript_nlp output is empty")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if is_current_artifact(output_path, source_checksum):
        return
    invalidate_stale_artifact(output_path, source_checksum)
    results.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="transcript-nlp-v1",
        options=options,
    )


def mock_transcript_backend(prompt: str) -> str:
    """Return deterministic bounded-evidence JSON for offline runs."""
    evidence = (
        "Análise offline: sem evidência específica extraída do texto, mas "
        "o registro foi processado conforme o contrato da sessão de transcrição."
    )
    return json.dumps({
        "coordination_friction_score": 0,
        "rework_signal_score": 0,
        "planning_clarity_score": 0,
        "integration_risk_signal": "absent",
        "dominant_topics": [],
        "evidence_summary_private": evidence[:TRANSCRIPT_EVIDENCE_MAX_CHARS],
    })


def openai_transcript_backend(prompt: str, *, client: Any, model: str) -> str:
    """Request one strict JSON transcript analysis through the central gateway."""
    config = MODEL_CONFIG["qualitative_mining"]
    gateway = LLMCallGateway(client)
    return gateway.chat_json(
        observation_id=f"transcript_nlp:{hashlib.sha256(prompt.encode('utf-8')).hexdigest()}",
        model=model,
        system_prompt=TRANSCRIPT_NLP_SYSTEM_PROMPT,
        user_prompt=prompt,
        request_options={
            "response_format": {"type": str(config["response_format"])},
            "temperature": float(config["temperature"]),
        },
    )


def aggregate_textual_cut_signals(students: pd.DataFrame, transcripts: pd.DataFrame) -> pd.DataFrame:
    """Aggregate NLP signals by semester and temporal cut without team keys.

    Args:
        students: Validated student NLP observations.
        transcripts: Validated transcript NLP observations.

    Returns:
        A ``cut_context`` DataFrame with an outer union of observed cuts.

    Raises:
        ValueError: If required columns, units, or keys are invalid.
    """
    keys = ["Semestre", "temporal_marker"]
    student_required = {
        *keys, "student_response_id", "question_id", "unit_of_analysis", "cognitive_load_score",
        "sentiment_score", "ai_dependency_score",
    }
    transcript_required = {
        *keys, "transcript_file", "unit_of_analysis", "coordination_friction_score",
        "rework_signal_score", "planning_clarity_score", "integration_risk_signal",
        "dominant_topics",
    }
    missing_students = student_required - set(students.columns)
    missing_transcripts = transcript_required - set(transcripts.columns)
    if missing_students:
        raise ValueError(f"student NLP input missing columns: {sorted(missing_students)}")
    if missing_transcripts:
        raise ValueError(f"transcript NLP input missing columns: {sorted(missing_transcripts)}")
    if not students["unit_of_analysis"].eq("student_response").all():
        raise ValueError("student NLP input has an invalid unit_of_analysis")
    if not transcripts["unit_of_analysis"].eq("transcript_session").all():
        raise ValueError("transcript NLP input has an invalid unit_of_analysis")
    if students.duplicated(["student_response_id", "question_id"]).any():
        raise ValueError("student NLP input has duplicate observations")
    if transcripts["transcript_file"].duplicated().any():
        raise ValueError("transcript NLP input has duplicate transcript_file observations")

    scale_versions = {name: definition["version"] for name, definition in NLP_SCORE_SCALES.items()}
    student_scores = ("sentiment_score", "cognitive_load_score", "ai_dependency_score")
    cut_keys = pd.concat(
        [students[keys], transcripts[keys]], ignore_index=True
    ).drop_duplicates().sort_values(keys).reset_index(drop=True)
    student_by_cut = students.groupby(keys, dropna=False)
    transcript_by_cut = transcripts.groupby(keys, dropna=False)
    risk_order = {"absent": 0, "low": 1, "moderate": 2, "high": 3, "critical": 4}

    def summarize_transcript_group(group: pd.DataFrame) -> pd.Series:
        risks = group["integration_risk_signal"].value_counts()
        risk_mode = max(risks.index, key=lambda value: (int(risks[value]), risk_order[value]))
        risk_mode_n = int(risks[risk_mode])
        topic_counts: dict[str, int] = {}
        for topic_values in group["dominant_topics"]:
            for topic in topic_values:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        topics = sorted(topic_counts)
        values: dict[str, Any] = {}
        for score in (
            "coordination_friction_score",
            "rework_signal_score",
            "planning_clarity_score",
        ):
            summary = summarize_numeric_distribution(
                group[score],
                scale_type="ordinal",
                scale_version=scale_versions[score],
            )
            values.update(flatten_distribution_summary(summary, f"ie_transcript_{score}"))
        values.update(
            {
                "ie_transcript_integration_risk_mode": risk_mode,
                "ie_transcript_integration_risk_mode_n": risk_mode_n,
                "ie_transcript_integration_risk_mode_share": float(risk_mode_n / len(group)),
                "ie_transcript_dominant_topics": topics,
                "ie_transcript_dominant_topic_counts": json.dumps(
                    topic_counts, ensure_ascii=False, sort_keys=True
                ),
                "ie_transcript_dominant_topic_shares": json.dumps(
                    {topic: count / len(group) for topic, count in topic_counts.items()},
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                "transcript_session_n": group["transcript_file"].nunique(),
            }
        )
        return pd.Series(values)

    rows: list[dict[str, Any]] = []
    for cut in cut_keys.to_dict("records"):
        key = (cut["Semestre"], cut["temporal_marker"])
        row: dict[str, Any] = dict(cut)
        student_group = student_by_cut.get_group(key) if key in student_by_cut.groups else students.iloc[0:0]
        transcript_group = transcript_by_cut.get_group(key) if key in transcript_by_cut.groups else transcripts.iloc[0:0]
        row["student_n"] = int(student_group["student_response_id"].nunique())
        row["student_response_n"] = int(len(student_group))
        for question_id, question_group in student_group.groupby("question_id", dropna=False):
            for score in student_scores:
                summary = summarize_numeric_distribution(
                    question_group[score],
                    scale_type="ordinal",
                    scale_version=scale_versions[score],
                )
                row.update(
                    flatten_distribution_summary(
                        summary, f"student_{question_id}_{score}"
                    )
                )
        if transcript_group.empty:
            row["transcript_session_n"] = None
            row["transcript_observation_n"] = 0
        else:
            row.update(summarize_transcript_group(transcript_group).to_dict())
            row["transcript_observation_n"] = int(len(transcript_group))
        row["unit_of_analysis"] = "cut_context"
        rows.append(row)
    return pd.DataFrame(rows)


def write_textual_cut_signals(
    results: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Write the immutable textual cut signal artifact and metadata."""
    required_columns = {
        "Semestre", "temporal_marker", "student_n", "student_response_n",
        "transcript_session_n", "transcript_observation_n", "unit_of_analysis",
    }
    missing = required_columns - set(results.columns)
    if missing:
        raise ValueError(f"textual_cut_signals output missing columns: {sorted(missing)}")
    if results.empty:
        raise ValueError("textual_cut_signals output is empty")
    if not results["unit_of_analysis"].eq("cut_context").all():
        raise ValueError("textual_cut_signals has an invalid unit_of_analysis")
    if results.duplicated(["Semestre", "temporal_marker"]).any():
        raise ValueError("textual_cut_signals has duplicate cut keys")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if is_current_artifact(output_path, source_checksum):
        return
    if output_path.exists() or output_path.with_name(f"{output_path.name}.metadata.json").exists():
        raise ValueError("textual_cut_signals artifact is immutable and stale")
    results.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version="textual-cut-signals-v2",
        options=options,
    )


def invalidate_stale_textual_cut_signals(
    output_path: Path,
    source_checksum: str,
) -> bool:
    """Invalidate a stale derived textual aggregate before regeneration.

    Upstream NLP artifacts are never touched by this operation. A current
    aggregate is preserved; a stale aggregate and its sidecar are removed so
    the sole producer can write a fresh version.
    """
    return invalidate_stale_artifact(output_path, source_checksum)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()