from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parse_student_llm_response_is_strict() -> None:
    miner = load_script("phase2_nlp", "04_nlp_qualitative_miner.py")
    parsed = miner.parse_student_llm_response(
        '{"sentiment_score": 1, "cognitive_load_score": 2, "ai_dependency_score": 3, '
        '"methodological_orientation": "structured", "planning_debt_signal": "present"}'
    )
    assert parsed["sentiment_score"] == 1
    with pytest.raises(ValueError):
        miner.parse_student_llm_response('{"sentiment_score": 8}')


def test_build_cut_context_metrics_keeps_student_and_transcript_counts() -> None:
    engine = load_script("phase2_metrics", "05_metric_engine.py")
    students = pd.DataFrame(
        [{"Semestre": "2025.2", "temporal_marker": "T1", "cognitive_load_score": 2, "sentiment_score": 1, "ai_dependency_score": 3}]
    )
    transcripts = pd.DataFrame(
        [{"Semestre": "2025.2", "temporal_marker": "T1", "coordination_friction_score": 4, "rework_signal_score": 2}]
    )
    result = engine.build_cut_context_metrics(students, transcripts)
    assert result.loc[0, "unit_of_analysis"] == "cut_context"
    assert result.loc[0, "ie_student_n"] == 1
    assert result.loc[0, "ie_transcript_session_n"] == 1


def test_compute_code_churn_uses_observed_source_loc_without_zero_fallback() -> None:
    engine = load_script("phase2_metrics_churn", "05_metric_engine.py")
    commits = pd.DataFrame(
        [{"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c1", "timestamp": pd.Timestamp("2025-10-18", tz="UTC"), "lines_added": 3, "lines_deleted": 1, "files_changed": 2}]
    )
    files = pd.DataFrame(
        [{"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "c1", "timestamp": pd.Timestamp("2025-10-18", tz="UTC"), "file_path": "src/a.py", "file_extension": ".py", "lines_added": 3, "lines_deleted": 1, "is_binary": False}]
    )
    snapshots = pd.DataFrame(
        [{"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "repo_source_loc": 10}]
    )
    result = engine.compute_code_churn(commits, files, snapshots)
    assert result.loc[0, "cc_total_t1"] == 4
    assert result.loc[0, "cc_per_source_loc_t1"] == 0.4


def test_run_declared_correlations_rejects_missing_columns() -> None:
    analyzer = load_script("phase2_stats", "06_statistical_analyzer.py")
    with pytest.raises(ValueError, match="missing"):
        analyzer.run_declared_correlations(pd.DataFrame({"x": [1, 2]}), [{"analysis_id": "a", "x": "missing", "y": "x", "unit_of_analysis": "team_semester"}])