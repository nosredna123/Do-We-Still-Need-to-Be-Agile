from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_miner():
    spec = importlib.util.spec_from_file_location(
        "phase2_transcript_nlp", ROOT / "04_nlp_qualitative_miner.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def transcript_frame(text: str = "A sessão discutiu o planejamento.") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "session_id": "session-1",
                "transcript_file": "session-1.txt",
                "Semestre": "2025.2",
                "temporal_marker": "T1",
                "temporal_marker_source": "filename",
                "transcript_text": text,
            }
        ]
    )


def valid_response() -> str:
    return json.dumps(
        {
            "coordination_friction_score": 2,
            "rework_signal_score": 1,
            "planning_clarity_score": 3,
            "integration_risk_signal": "moderate",
            "dominant_topics": ["planning_debt", "coordination"],
            "evidence_summary_private": "A sessão menciona revisão do planejamento.",
        }
    )


def test_mine_transcript_sessions_preserves_session_metadata_and_private_evidence() -> None:
    miner = load_miner()
    calls: list[str] = []

    result = miner.mine_transcript_sessions(
        transcript_frame(),
        lambda prompt: (calls.append(prompt) or valid_response()),
        model="mock-model",
    )

    assert len(calls) == 1
    assert "A sessão discutiu" in calls[0]
    assert result.loc[0, "session_id"] == "session-1"
    assert result.loc[0, "unit_of_analysis"] == "transcript_session"
    assert result.loc[0, "evidence_summary_private"]
    assert result.loc[0, "prompt_version"] == "transcript-nlp-v1"
    assert result.loc[0, "response_schema_version"] == "transcript-nlp-response-v1"


def test_parse_transcript_response_rejects_unknown_topic_and_long_evidence() -> None:
    miner = load_miner()
    invalid = json.loads(valid_response())
    invalid["dominant_topics"] = ["free_text_topic"]
    with pytest.raises(ValueError, match="dominant_topics"):
        miner.parse_transcript_llm_response(json.dumps(invalid))

    invalid["dominant_topics"] = ["planning_debt"]
    invalid["evidence_summary_private"] = "x" * 1001
    with pytest.raises(ValueError, match="evidence_summary_private"):
        miner.parse_transcript_llm_response(json.dumps(invalid))


def test_mine_transcript_sessions_fails_on_empty_text() -> None:
    miner = load_miner()
    frame = transcript_frame("")
    with pytest.raises(ValueError, match="transcript_text"):
        miner.mine_transcript_sessions(frame, lambda _prompt: valid_response(), model="mock-model")


def test_mine_transcript_sessions_allows_repeated_session_id_when_files_are_unique() -> None:
    miner = load_miner()
    frame = pd.concat(
        [transcript_frame(), transcript_frame().assign(transcript_file="session-2.txt")],
        ignore_index=True,
    )

    result = miner.mine_transcript_sessions(
        frame, lambda _prompt: valid_response(), model="mock-model"
    )

    assert len(result) == 2
    assert result["transcript_file"].is_unique


def test_mine_transcript_sessions_chunks_with_overlay_and_consolidates(monkeypatch) -> None:
    miner = load_miner()
    monkeypatch.setattr(miner, "TRANSCRIPT_CHUNK_TOKENS", 4)
    monkeypatch.setattr(miner, "TRANSCRIPT_CHUNK_OVERLAP_TOKENS", 1)
    calls: list[str] = []

    def backend(prompt: str) -> str:
        calls.append(prompt)
        return valid_response()

    result = miner.mine_transcript_sessions(
        transcript_frame("one two three four five six seven"),
        backend,
        model="mock-model",
    )

    assert len(calls) == 3
    assert "chunk" in calls[-1].lower()
    assert len(result) == 1
    assert result.loc[0, "session_id"] == "session-1"


def test_write_transcript_nlp_writes_sidecar(tmp_path: Path) -> None:
    miner = load_miner()
    result = miner.mine_transcript_sessions(
        transcript_frame(), lambda _prompt: valid_response(), model="mock-model"
    )
    output = tmp_path / "analysis" / "transcript_nlp.parquet"

    miner.write_transcript_nlp(
        result,
        output,
        source_checksum="checksum",
        options={"model": "mock-model"},
    )

    assert output.exists()
    stored = pd.read_parquet(output)
    assert stored.loc[0, "unit_of_analysis"] == "transcript_session"
    metadata = json.loads(
        output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["contract_version"] == "transcript-nlp-v1"
    assert metadata["status"] == "success"