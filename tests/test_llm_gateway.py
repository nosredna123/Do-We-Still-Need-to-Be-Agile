from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest import mock

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent


def load_gateway():
    spec = importlib.util.spec_from_file_location("llm_gateway_test", ROOT / "llm_gateway.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def response(content: str, usage: object | None = None):
    return mock.Mock(
        choices=[mock.Mock(message=mock.Mock(content=content))],
        usage=usage,
    )


def test_chat_gateway_persists_prompt_response_usage_and_attached_price(tmp_path: Path) -> None:
    gateway_module = load_gateway()
    usage = mock.Mock(prompt_tokens=1_000_000, completion_tokens=1_000_000, total_tokens=2_000_000)
    usage.prompt_tokens_details = mock.Mock(cached_tokens=0)
    client = mock.Mock()
    client.chat.completions.create.return_value = response('{"ok": true}', usage)
    ledger = tmp_path / ".private" / "llm_call_ledger.parquet"

    result = gateway_module.LLMCallGateway(client, ledger_path=ledger).chat_json(
        observation_id="student:1",
        model="gpt-4o-mini",
        system_prompt="system",
        user_prompt="user",
        request_options={"temperature": 0},
    )

    assert result == '{"ok": true}'
    row = pd.read_parquet(ledger).iloc[0]
    assert row["status"] == "success"
    assert row["observation_id"] == "student:1"
    assert row["estimated_cost_usd"] == 0.75
    assert row["pricing_version"] == "openai-pricing-2026-09-attached-v1"
    assert row["prompt_text"] == "[system]\nsystem\n[user]\nuser"


def test_gateway_records_error_attempt_and_unknown_model_warning(tmp_path: Path, caplog) -> None:
    gateway_module = load_gateway()
    client = mock.Mock()
    client.chat.completions.create.side_effect = RuntimeError("provider failed")
    ledger = tmp_path / "ledger.parquet"

    with caplog.at_level("WARNING"):
        try:
            gateway_module.LLMCallGateway(client, ledger_path=ledger).chat_json(
                observation_id="unknown:1",
                model="future-model",
                system_prompt="system",
                user_prompt="user",
                request_options={},
            )
        except RuntimeError:
            pass

    row = pd.read_parquet(ledger).iloc[0]
    assert row["status"] == "error"
    assert row["cost_status"] == "unavailable_model_pricing"
    assert "No pricing registered" in caplog.text