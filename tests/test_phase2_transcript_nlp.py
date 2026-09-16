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


def test_mock_transcript_backend_returns_valid_bounded_evidence_string() -> None:
    miner = load_miner()

    payload = json.loads(miner.mock_transcript_backend("prompt"))

    assert isinstance(payload["evidence_summary_private"], str)
    assert len(payload["evidence_summary_private"]) <= miner.TRANSCRIPT_EVIDENCE_MAX_CHARS
    miner.parse_transcript_llm_response(json.dumps(payload))


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


def test_mine_transcript_sessions_reuses_prior_final_artifact(tmp_path: Path) -> None:
    miner = load_miner()
    prior_output = tmp_path / "transcript_nlp.parquet"
    prior_result = miner.mine_transcript_sessions(
        transcript_frame(), lambda _prompt: valid_response(), model="mock-model"
    )
    prior_result.to_parquet(prior_output, index=False)
    prior_output.with_name(f"{prior_output.name}.metadata.json").write_text(
        json.dumps(
            {
                "status": "success",
                "input_checksum": "legacy-checksum",
                "contract_version": "transcript-nlp-v1",
            }
        ),
        encoding="utf-8",
    )

    def unexpected_call(_prompt: str) -> str:
        raise AssertionError("completed transcript should have been reused")

    result = miner.mine_transcript_sessions(
        transcript_frame(),
        unexpected_call,
        model="mock-model",
        prior_output_path=prior_output,
    )

    assert len(result) == 1
    assert result.loc[0, "transcript_file"] == "session-1.txt"


def test_aggregate_textual_cut_signals_preserves_outer_cuts_and_uses_observed_keys() -> None:
    miner = load_miner()
    students = pd.DataFrame(
        [
            {"student_response_id": "student-1", "question_id": "project_feeling", "unit_of_analysis": "student_response", "Semestre": "2025.2", "temporal_marker": "T1", "cognitive_load_score": 2, "sentiment_score": 1, "ai_dependency_score": 3},
            {"student_response_id": "student-2", "question_id": "project_feeling", "unit_of_analysis": "student_response", "Semestre": "2025.2", "temporal_marker": "T1", "cognitive_load_score": 4, "sentiment_score": -1, "ai_dependency_score": 1},
        ]
    )
    transcripts = pd.DataFrame(
        [
            {"session_id": "group-1", "transcript_file": "t1-a.txt", "unit_of_analysis": "transcript_session", "Semestre": "2025.2", "temporal_marker": "T1", "coordination_friction_score": 2, "rework_signal_score": 1, "planning_clarity_score": 3, "integration_risk_signal": "high", "dominant_topics": ["coordination"]},
            {"session_id": "group-1", "transcript_file": "t1-b.txt", "unit_of_analysis": "transcript_session", "Semestre": "2025.2", "temporal_marker": "T1", "coordination_friction_score": 4, "rework_signal_score": 3, "planning_clarity_score": 1, "integration_risk_signal": "critical", "dominant_topics": ["rework", "coordination"]},
        ]
    )

    result = miner.aggregate_textual_cut_signals(students, transcripts)

    assert len(result) == 1
    row = result.iloc[0]
    assert row["student_n"] == 2
    assert row["transcript_session_n"] == 2
    assert row["student_project_feeling_cognitive_load_score_mean"] == 3
    assert row["student_project_feeling_cognitive_load_score_n_valid"] == 2
    assert row["ie_transcript_planning_clarity_score_mean"] == 2
    assert row["ie_transcript_planning_clarity_score_iqr"] == 1.0
    assert row["ie_transcript_integration_risk_mode"] == "critical"
    assert row["ie_transcript_integration_risk_mode_n"] == 1
    assert row["ie_transcript_dominant_topics"] == ["coordination", "rework"]
    assert row["unit_of_analysis"] == "cut_context"


def test_aggregate_textual_cut_signals_outer_join_retains_source_only_cut() -> None:
    miner = load_miner()
    students = pd.DataFrame(
        [{"student_response_id": "student-1", "question_id": "project_feeling", "unit_of_analysis": "student_response", "Semestre": "2025.2", "temporal_marker": "T2", "cognitive_load_score": 2, "sentiment_score": 0, "ai_dependency_score": 1}]
    )
    transcripts = pd.DataFrame(
        [{"session_id": "group-1", "transcript_file": "t1.txt", "unit_of_analysis": "transcript_session", "Semestre": "2025.2", "temporal_marker": "T1", "coordination_friction_score": 1, "rework_signal_score": 2, "planning_clarity_score": 3, "integration_risk_signal": "low", "dominant_topics": ["planning_debt"]}]
    )

    result = miner.aggregate_textual_cut_signals(students, transcripts)

    assert set(result["temporal_marker"]) == {"T1", "T2"}
    t2 = result.loc[result["temporal_marker"] == "T2"].iloc[0]
    assert pd.isna(t2["transcript_session_n"])
    assert t2["student_n"] == 1


def test_aggregate_textual_cut_signals_serializes_empty_topic_maps() -> None:
    miner = load_miner()
    result = miner.aggregate_textual_cut_signals(
        pd.DataFrame([
            {"student_response_id": "student-1", "question_id": "project_feeling", "unit_of_analysis": "student_response", "Semestre": "2025.2", "temporal_marker": "T1", "cognitive_load_score": 2, "sentiment_score": 0, "ai_dependency_score": 1},
        ]),
        pd.DataFrame([
            {"session_id": "group-1", "transcript_file": "t1.txt", "unit_of_analysis": "transcript_session", "Semestre": "2025.2", "temporal_marker": "T1", "coordination_friction_score": 1, "rework_signal_score": 2, "planning_clarity_score": 3, "integration_risk_signal": "low", "dominant_topics": []},
        ]),
    )

    row = result.iloc[0]
    assert row["ie_transcript_dominant_topics"] == []
    assert json.loads(row["ie_transcript_dominant_topic_counts"]) == {}
    assert json.loads(row["ie_transcript_dominant_topic_shares"]) == {}
    miner.write_textual_cut_signals(result, Path("/tmp/test_textual_cut_signals.parquet"), source_checksum="checksum-empty-topics", options={"stage": "textual_cut_signals"})


def test_write_textual_cut_signals_writes_sidecar_and_refuses_stale_overwrite(tmp_path: Path) -> None:
    miner = load_miner()
    result = miner.aggregate_textual_cut_signals(
        pd.DataFrame([{
            "student_response_id": "student-1", "question_id": "project_feeling",
            "unit_of_analysis": "student_response", "Semestre": "2025.2",
            "temporal_marker": "T1", "cognitive_load_score": 2,
            "sentiment_score": 0, "ai_dependency_score": 1,
        }]),
        pd.DataFrame([{
            "session_id": "group-1", "transcript_file": "t1.txt",
            "unit_of_analysis": "transcript_session", "Semestre": "2025.2",
            "temporal_marker": "T1", "coordination_friction_score": 1,
            "rework_signal_score": 2, "planning_clarity_score": 3,
            "integration_risk_signal": "low", "dominant_topics": ["planning_debt"],
        }]),
    )
    output = tmp_path / "textual_cut_signals.parquet"
    miner.write_textual_cut_signals(result, output, source_checksum="checksum-v1", options={"stage": "textual_cut_signals"})

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert metadata["contract_version"] == "textual-cut-signals-v2"
    assert metadata["status"] == "success"
    with pytest.raises(ValueError, match="immutable"):
        miner.write_textual_cut_signals(result, output, source_checksum="checksum-v2", options={"stage": "textual_cut_signals"})


def test_invalidate_stale_textual_cut_signals_removes_only_derived_artifact(tmp_path: Path) -> None:
    miner = load_miner()
    result = miner.aggregate_textual_cut_signals(
        pd.DataFrame([{
            "student_response_id": "student-1", "question_id": "project_feeling",
            "unit_of_analysis": "student_response", "Semestre": "2025.2",
            "temporal_marker": "T1", "cognitive_load_score": 2,
            "sentiment_score": 0, "ai_dependency_score": 1,
        }]),
        pd.DataFrame([{
            "session_id": "group-1", "transcript_file": "t1.txt",
            "unit_of_analysis": "transcript_session", "Semestre": "2025.2",
            "temporal_marker": "T1", "coordination_friction_score": 1,
            "rework_signal_score": 2, "planning_clarity_score": 3,
            "integration_risk_signal": "low", "dominant_topics": ["planning_debt"],
        }]),
    )
    output = tmp_path / "textual_cut_signals.parquet"
    miner.write_textual_cut_signals(
        result, output, source_checksum="old-checksum", options={"stage": "textual_cut_signals"}
    )

    assert miner.invalidate_stale_textual_cut_signals(output, "new-checksum")
    assert not output.exists()
    assert not output.with_name(f"{output.name}.metadata.json").exists()