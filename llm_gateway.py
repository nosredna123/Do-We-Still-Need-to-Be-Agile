"""Centralized OpenAI gateway and private call ledger for the pipeline."""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pandas as pd

from pipeline_config import LLM_MAX_RETRIES, LLM_PRICING_REGISTRY, LLM_PRICING_VERSION

logger = logging.getLogger(__name__)
LEDGER_CONTRACT_VERSION = "llm-call-ledger-v1"
DEFAULT_LEDGER_PATH = Path("data/analysis/.private/llm_call_ledger.parquet")


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _usage_value(usage: Any, name: str) -> int | None:
    if usage is None:
        return None
    if isinstance(usage, dict):
        value = usage.get(name)
    else:
        value = getattr(usage, name, None)
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _cached_tokens(usage: Any) -> int:
    details = getattr(usage, "prompt_tokens_details", None)
    if details is None and isinstance(usage, dict):
        details = usage.get("prompt_tokens_details")
    if isinstance(details, dict):
        value = details.get("cached_tokens")
        return int(value) if isinstance(value, (int, float)) else 0
    value = getattr(details, "cached_tokens", 0)
    return int(value) if isinstance(value, (int, float)) else 0


def _cost(model: str, usage: Any) -> tuple[float | None, str, str]:
    pricing = LLM_PRICING_REGISTRY.get(model)
    if pricing is None:
        logger.warning("No pricing registered for OpenAI model %s", model)
        return None, "unavailable_model_pricing", "unknown"
    if pricing.get("pricing_mode") != "token":
        return None, "unavailable_non_token_usage", str(pricing["pricing_mode"])
    prompt_tokens = _usage_value(usage, "prompt_tokens")
    completion_tokens = _usage_value(usage, "completion_tokens")
    if prompt_tokens is None or completion_tokens is None:
        return None, "unavailable_usage", "token"
    cached = min(_cached_tokens(usage), prompt_tokens)
    uncached = prompt_tokens - cached
    value = (
        uncached * float(pricing["input_usd_per_1m_tokens"])
        + cached * float(pricing["cached_input_usd_per_1m_tokens"])
        + completion_tokens * float(pricing["output_usd_per_1m_tokens"])
    ) / 1_000_000
    return value, "estimated_from_provider_usage", "token"


class LLMCallGateway:
    """Execute OpenAI calls and append one structured ledger row per attempt."""

    def __init__(
        self,
        client: Any,
        ledger_path: Path = DEFAULT_LEDGER_PATH,
        max_retries: int = LLM_MAX_RETRIES,
    ) -> None:
        self.client = client
        self.ledger_path = ledger_path
        self.max_retries = max_retries

    def _append(self, record: dict[str, Any]) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        frame = pd.DataFrame([record])
        if self.ledger_path.exists():
            existing = pd.read_parquet(self.ledger_path)
            records = existing.to_dict("records")
            records.extend(frame.to_dict("records"))
            frame = pd.DataFrame.from_records(records)
        temporary = self.ledger_path.with_name(f".{self.ledger_path.name}.tmp")
        frame.to_parquet(temporary, index=False)
        temporary.replace(self.ledger_path)
        metadata_path = self.ledger_path.with_name(f"{self.ledger_path.name}.metadata.json")
        metadata_path.write_text(
            json.dumps(
                {
                    "status": "success",
                    "contract_version": LEDGER_CONTRACT_VERSION,
                    "pricing_version": LLM_PRICING_VERSION,
                    "rows": len(frame),
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    def _execute(
        self,
        *,
        operation: str,
        observation_id: str,
        model: str,
        prompt_text: str,
        request_options: dict[str, Any],
        call: Callable[[], Any],
        response_text: Callable[[Any], str],
    ) -> Any:
        prompt_hash = _sha256(prompt_text)
        for attempt in range(1, self.max_retries + 2):
            started = datetime.now(timezone.utc)
            monotonic_started = time.monotonic()
            call_id = str(uuid.uuid4())
            try:
                response = call()
                usage = getattr(response, "usage", None)
                result_text = response_text(response)
                cost, cost_status, pricing_unit = _cost(model, usage)
                status = "success"
                error_type = None
                error_message = None
                retryable = False
                return_value = response
            except KeyboardInterrupt:
                usage = None
                result_text = ""
                cost, cost_status, pricing_unit = _cost(model, usage)
                status = "interrupted"
                error_type = "KeyboardInterrupt"
                error_message = "Call interrupted by user"
                retryable = False
                self._record(
                    call_id, observation_id, operation, model, attempt, started,
                    monotonic_started, prompt_text, prompt_hash, request_options,
                    result_text, usage, cost, cost_status, pricing_unit, status,
                    error_type, error_message, retryable,
                )
                raise
            except Exception as error:
                usage = None
                result_text = ""
                cost, cost_status, pricing_unit = _cost(model, usage)
                status = "error"
                error_type = type(error).__name__
                error_message = str(error)
                retryable = attempt <= self.max_retries
                return_value = None
                self._record(
                    call_id, observation_id, operation, model, attempt, started,
                    monotonic_started, prompt_text, prompt_hash, request_options,
                    result_text, usage, cost, cost_status, pricing_unit, status,
                    error_type, error_message, retryable,
                )
                if not retryable:
                    raise
                continue
            self._record(
                call_id, observation_id, operation, model, attempt, started,
                monotonic_started, prompt_text, prompt_hash, request_options,
                result_text, usage, cost, cost_status, pricing_unit, status,
                error_type, error_message, retryable,
            )
            return return_value
        raise RuntimeError("LLM gateway exhausted retries")

    def _record(self, call_id: str, observation_id: str, operation: str, model: str, attempt: int, started: datetime, monotonic_started: float, prompt_text: str, prompt_hash: str, request_options: dict[str, Any], result_text: str, usage: Any, cost: float | None, cost_status: str, pricing_unit: str, status: str, error_type: str | None, error_message: str | None, retryable: bool) -> None:
        finished = datetime.now(timezone.utc)
        self._append({
            "call_id": call_id,
            "observation_id": observation_id,
            "operation": operation,
            "provider": "openai",
            "model": model,
            "attempt": attempt,
            "status": status,
            "started_at": started,
            "finished_at": finished,
            "duration_ms": round((time.monotonic() - monotonic_started) * 1000, 3),
            "request_options_json": json.dumps(request_options, sort_keys=True, default=str),
            "prompt_text": prompt_text,
            "response_text": result_text,
            "prompt_sha256": prompt_hash,
            "response_sha256": _sha256(result_text),
            "prompt_tokens": _usage_value(usage, "prompt_tokens"),
            "completion_tokens": _usage_value(usage, "completion_tokens"),
            "total_tokens": _usage_value(usage, "total_tokens"),
            "estimated_cost_usd": cost,
            "cost_status": cost_status,
            "pricing_unit": pricing_unit,
            "pricing_version": LLM_PRICING_VERSION,
            "error_type": error_type,
            "error_message": error_message,
            "retryable": retryable,
        })

    def chat_json(self, *, observation_id: str, model: str, system_prompt: str, user_prompt: str, request_options: dict[str, Any]) -> str:
        """Execute one JSON chat call and return its raw response content."""
        response = self._execute(
            operation="chat.completions.create",
            observation_id=observation_id,
            model=model,
            prompt_text=f"[system]\n{system_prompt}\n[user]\n{user_prompt}",
            request_options=request_options,
            call=lambda: self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                **request_options,
            ),
            response_text=lambda response: str(response.choices[0].message.content or ""),
        )
        return str(response.choices[0].message.content or "")

    def transcribe(self, *, observation_id: str, model: str, file: Any, prompt: str, request_options: dict[str, Any]) -> Any:
        """Execute one transcription call and record its text privately."""
        return self._execute(
            operation="audio.transcriptions.create",
            observation_id=observation_id,
            model=model,
            prompt_text=prompt,
            request_options=request_options,
            call=lambda: self.client.audio.transcriptions.create(model=model, file=file, prompt=prompt, **request_options),
            response_text=lambda response: str(getattr(response, "text", "")),
        )