from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_miner():
    spec = importlib.util.spec_from_file_location(
        "phase2_student_nlp", ROOT / "04_nlp_qualitative_miner.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prompt_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "student_response_id": "students.csv:0",
                "Semestre": "2025.2",
                "temporal_marker": "T1",
                "source_file": "students.csv",
                "question_id": "project_feeling",
                "construct": "cognitive_load",
                "answer_text": "Resposta privada",
            }
        ]
    )


def prompt_frame_with_three_observations() -> pd.DataFrame:
    frame = prompt_frame()
    return pd.concat(
        [
            frame,
            frame.assign(student_response_id="students.csv:1"),
            frame.assign(student_response_id="students.csv:2"),
        ],
        ignore_index=True,
    )


def valid_response() -> str:
    return json.dumps(
        {
            "sentiment_score": 1,
            "cognitive_load_score": 2,
            "ai_dependency_score": 3,
            "methodological_orientation": "structured",
            "planning_debt_signal": "present",
        }
    )


def test_mine_student_prompts_sends_versioned_prompt_and_metadata() -> None:
    miner = load_miner()
    calls: list[str] = []

    def backend(prompt: str) -> str:
        calls.append(prompt)
        return valid_response()

    result = miner.mine_student_prompts(
        prompt_frame(),
        backend,
        model="mock-model",
    )

    assert len(calls) == 1
    assert "project_feeling" in calls[0]
    assert "Resposta privada" in calls[0]
    assert result.loc[0, "unit_of_analysis"] == "student_response"
    assert result.loc[0, "model"] == "mock-model"
    assert result.loc[0, "prompt_version"] == "student-nlp-v1"
    assert result.loc[0, "response_schema_version"] == "student-nlp-response-v1"
    assert result.loc[0, "status"] == "success"
    assert "answer_text" not in result.columns


def test_mine_student_prompts_fails_before_writing_on_invalid_response() -> None:
    miner = load_miner()
    with pytest.raises(ValueError, match="outside|missing|JSON"):
        miner.mine_student_prompts(
            prompt_frame(),
            lambda _prompt: '{"sentiment_score": 9}',
            model="mock-model",
        )


def test_write_student_nlp_rejects_private_source_text_and_writes_sidecar(tmp_path: Path) -> None:
    miner = load_miner()
    output = tmp_path / "analysis" / "student_nlp.parquet"
    result = miner.mine_student_prompts(
        prompt_frame(), lambda _prompt: valid_response(), model="mock-model"
    )

    miner.write_student_nlp(
        result,
        output,
        source_checksum="checksum",
        options={"model": "mock-model"},
    )

    assert output.exists()
    assert "answer_text" not in pd.read_parquet(output).columns
    metadata = json.loads(
        output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["contract_version"] == "student-nlp-v1"
    assert metadata["status"] == "success"


def test_write_student_nlp_rejects_missing_required_output_columns(tmp_path: Path) -> None:
    miner = load_miner()
    with pytest.raises(ValueError, match="required"):
        miner.write_student_nlp(
            pd.DataFrame([{ "student_response_id": "only-id" }]),
            tmp_path / "analysis" / "student_nlp.parquet",
            source_checksum="checksum",
            options={},
        )


def test_openai_student_backend_uses_versioned_json_request() -> None:
    miner = load_miner()
    client = type("Client", (), {})()
    client.chat = type("Chat", (), {})()
    client.chat.completions = type("Completions", (), {})()
    calls: list[dict[str, object]] = []

    def create(**kwargs: object):
        calls.append(kwargs)
        message = type("Message", (), {"content": valid_response()})()
        choice = type("Choice", (), {"message": message})()
        return type("Response", (), {"choices": [choice]})()

    client.chat.completions.create = create
    response = miner.openai_student_backend("prompt", client=client, model="mock-model")

    assert json.loads(response)["sentiment_score"] == 1
    assert calls[0]["model"] == "mock-model"
    assert calls[0]["response_format"] == {"type": "json_object"}
    assert calls[0]["temperature"] == 0


def test_mine_student_prompts_resumes_completed_observations(tmp_path: Path) -> None:
    miner = load_miner()
    prompts = prompt_frame_with_three_observations()
    checkpoint = tmp_path / ".private" / "student_nlp.partial.parquet"
    first_run_calls: list[str] = []

    def interrupted_backend(prompt: str) -> str:
        first_run_calls.append(prompt)
        if len(first_run_calls) == 3:
            raise RuntimeError("simulated interruption")
        return valid_response()

    with pytest.raises(RuntimeError, match="simulated interruption"):
        miner.mine_student_prompts(
            prompts,
            interrupted_backend,
            model="mock-model",
            checkpoint_path=checkpoint,
            checkpoint_checksum="checkpoint-v1",
        )

    assert checkpoint.exists()
    resumed_calls: list[str] = []
    result = miner.mine_student_prompts(
        prompts,
        lambda prompt: (resumed_calls.append(prompt) or valid_response()),
        model="mock-model",
        checkpoint_path=checkpoint,
        checkpoint_checksum="checkpoint-v1",
    )

    assert len(first_run_calls) == 3
    assert len(resumed_calls) == 1
    assert len(result) == 3
    assert not result.duplicated(["student_response_id", "question_id"]).any()