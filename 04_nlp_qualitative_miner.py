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
    phase2_input_checksum,
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
    parser.add_argument("--backend", choices=("openai",), default="openai")
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
    }
    source_checksum = phase2_input_checksum(
        args.lake_dir,
        [Path(__file__).with_name("pipeline_config.py")],
        catalog_options,
    )
    if args.force:
        invalidate_stale_artifact(args.catalog_output, "force-regeneration")
        invalidate_stale_artifact(args.output, "force-regeneration")
        invalidate_stale_artifact(args.transcript_output, "force-regeneration")
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

    nlp_options = {
        "stage": "student_nlp",
        "backend": args.backend,
        "model": args.model,
        "prompt_version": STUDENT_NLP_PROMPT_VERSION,
        "response_schema_version": STUDENT_NLP_RESPONSE_SCHEMA_VERSION,
    }
    nlp_checksum = input_checksum(
        [args.catalog_output, Path(__file__).with_name("pipeline_prompts.py")],
        nlp_options,
    )
    checkpoint_path = args.output.with_name(f"{args.output.name}.partial")
    if not args.force and is_current_artifact(args.output, nlp_checksum):
        logger.info("Student NLP artifact is current: %s", args.output)
    else:
        load_project_environment()
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("openai package is not installed") from error
        client = OpenAI()
        results = mine_student_prompts(
            prompts,
            lambda prompt: openai_student_backend(prompt, client=client, model=args.model),
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
    }
    transcript_checksum = input_checksum(
        [
            args.lake_dir / "transcript_sessions.parquet",
            args.lake_dir / "transcript_sessions.parquet.metadata.json",
            Path(__file__).with_name("pipeline_prompts.py"),
            Path(__file__).with_name("pipeline_config.py"),
        ],
        transcript_options,
    )
    transcript_checkpoint = args.transcript_output.with_name(f"{args.transcript_output.name}.partial")
    if not args.force and is_current_artifact(args.transcript_output, transcript_checksum):
        logger.info("Transcript NLP artifact is current: %s", args.transcript_output)
        return
    client = locals().get("client")
    if client is None:
        load_project_environment()
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("openai package is not installed") from error
        client = OpenAI()
    transcript_results = mine_transcript_sessions(
        inputs["transcript_sessions"],
        lambda prompt: openai_transcript_backend(prompt, client=client, model=args.model),
        model=args.model,
        checkpoint_path=transcript_checkpoint,
        checkpoint_checksum=transcript_checksum,
    )
    write_transcript_nlp(
        transcript_results,
        args.transcript_output,
        source_checksum=transcript_checksum,
        options=transcript_options,
    )
    invalidate_stale_artifact(transcript_checkpoint, "completed-final-artifact")
    logger.info("Mined %s transcript NLP observations", len(transcript_results))


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
) -> pd.DataFrame:
    """Mine anonymized transcript sessions with resumable chunk processing.

    Args:
        sessions: Validated transcript-session contract DataFrame.
        backend: Callable receiving a prompt and returning strict JSON.
        model: Effective model identifier recorded per observation.
        checkpoint_path: Optional private partial checkpoint path.
        checkpoint_checksum: Checksum associated with the checkpoint inputs.

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

    completed = _load_transcript_checkpoint(checkpoint_path, checkpoint_checksum)
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