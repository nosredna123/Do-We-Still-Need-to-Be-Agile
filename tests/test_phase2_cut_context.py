from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_engine():
    spec = importlib.util.spec_from_file_location("phase2_cut_context", ROOT / "05_metric_engine.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def textual_frame() -> pd.DataFrame:
    frame = pd.DataFrame([
        {
            "Semestre": "2025.2",
            "temporal_marker": "T1",
            "student_n": 2,
            "student_response_n": 3,
            "transcript_session_n": 2,
            "unit_of_analysis": "cut_context",
            "ie_student_cognitive_load_score_mean": 2.0,
            "ie_student_cognitive_load_score_std": 1.0,
            "ie_student_cognitive_load_score_median": 2.0,
            "ie_student_cognitive_load_score_q1": 1.0,
            "ie_student_cognitive_load_score_q3": 3.0,
            "ie_student_cognitive_load_score_iqr": 2.0,
            "ie_student_cognitive_load_score_mode": 2,
            "ie_student_cognitive_load_score_mode_n": 2,
            "ie_student_cognitive_load_score_mode_share": 2 / 3,
            "ie_student_cognitive_load_score_n_total": 3,
            "ie_student_cognitive_load_score_n_valid": 3,
            "ie_student_cognitive_load_score_n_missing": 0,
            "ie_student_sentiment_score_mean": 0.5,
            "ie_student_sentiment_score_std": 0.5,
            "ie_student_sentiment_score_median": 0.5,
            "ie_student_sentiment_score_q1": 0.0,
            "ie_student_sentiment_score_q3": 1.0,
            "ie_student_sentiment_score_iqr": 1.0,
            "ie_student_sentiment_score_mode": 1,
            "ie_student_sentiment_score_mode_n": 2,
            "ie_student_sentiment_score_mode_share": 2 / 3,
            "ie_student_sentiment_score_n_total": 3,
            "ie_student_sentiment_score_n_valid": 3,
            "ie_student_sentiment_score_n_missing": 0,
            "ie_student_ai_dependency_score_mean": 1.0,
            "ie_student_ai_dependency_score_std": 0.0,
            "ie_student_ai_dependency_score_median": 1.0,
            "ie_student_ai_dependency_score_q1": 1.0,
            "ie_student_ai_dependency_score_q3": 1.0,
            "ie_student_ai_dependency_score_iqr": 0.0,
            "ie_student_ai_dependency_score_mode": 1,
            "ie_student_ai_dependency_score_mode_n": 3,
            "ie_student_ai_dependency_score_mode_share": 1.0,
            "ie_student_ai_dependency_score_n_total": 3,
            "ie_student_ai_dependency_score_n_valid": 3,
            "ie_student_ai_dependency_score_n_missing": 0,
            "ie_transcript_available": True,
            "ie_transcript_unavailable_reason": None,
        }
    ])
    for prefix in (
        "ie_transcript_coordination_friction_score",
        "ie_transcript_rework_signal_score",
        "ie_transcript_planning_clarity_score",
    ):
        for field, value in {
            "mean": 2.0, "std": 1.0, "median": 2.0, "q1": 1.0,
            "q3": 3.0, "iqr": 2.0, "mode": 2, "mode_n": 1,
            "mode_share": 0.5, "n_total": 2, "n_valid": 2,
            "n_missing": 0,
        }.items():
            frame[f"{prefix}_{field}"] = value
    return frame


def test_build_cut_context_metrics_transforms_canonical_textual_contract() -> None:
    engine = load_engine()
    result = engine.build_cut_context_metrics(textual_frame())
    row = result.iloc[0]

    assert row["unit_of_analysis"] == "cut_context"
    assert row["ie_definition_version"] == "ie-v1"
    assert row["statistical_summary_version"] == "distribution-summary-v1"
    assert row["ie_student_cognitive_load_score_iqr"] == 2.0
    assert row["ie_student_sentiment_score_mode"] == 1
    assert row["ie_transcript_available"]
    assert "ie_composite_score" not in result.columns


def test_build_cut_context_metrics_fails_on_missing_canonical_summary() -> None:
    engine = load_engine()
    frame = textual_frame().drop(columns=["ie_student_sentiment_score_iqr"])
    with pytest.raises(ValueError, match="missing student distribution summaries"):
        engine.build_cut_context_metrics(frame)


def test_write_cut_context_metrics_writes_sidecar_and_refuses_stale(tmp_path: Path) -> None:
    engine = load_engine()
    result = engine.build_cut_context_metrics(textual_frame())
    output = tmp_path / "cut_context_metrics.parquet"
    engine.write_cut_context_metrics(
        result, output, source_checksum="ie-v1-checksum", options={"stage": "cut_context_metrics"}
    )
    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cut-context-metrics-v1"
    with pytest.raises(ValueError, match="immutable"):
        engine.write_cut_context_metrics(result, output, source_checksum="ie-v2-checksum", options={})