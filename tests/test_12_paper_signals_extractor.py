from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "12_paper_signals_extractor.py"


def load_module():
    spec = importlib.util.spec_from_file_location("paper_signals_extractor", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Module not found: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_rework_policy_uses_shared_code_measurement_rules() -> None:
    module = load_module()

    assert not module._is_boilerplate_path("src/app.py")
    assert module._is_boilerplate_path(".history/src/app_20251113000000.py")
    assert module._is_boilerplate_path("backend/testes/backups/llm_service.py")
    assert module._is_boilerplate_path("node_modules/react/index.js")


def test_team_level_signal_builder_and_cohort_output(tmp_path: Path, monkeypatch) -> None:
    module = load_module()

    git_files = pd.DataFrame(
        [
            {
                "ID_Equipe": "TEAM_01",
                "Semestre": "2025.2",
                "temporal_marker": "T1",
                "file_path": "src/app.py",
                "lines_added": 10,
                "lines_deleted": 2,
                "commit_hash": "c1",
            },
            {
                "ID_Equipe": "TEAM_01",
                "Semestre": "2025.2",
                "temporal_marker": "T3",
                "file_path": "src/app.py",
                "lines_added": 5,
                "lines_deleted": 3,
                "commit_hash": "c2",
            },
            {
                "ID_Equipe": "TEAM_01",
                "Semestre": "2025.2",
                "temporal_marker": "T3",
                "file_path": "docs/readme.md",
                "lines_added": 4,
                "lines_deleted": 1,
                "commit_hash": "c2",
            },
            {
                "ID_Equipe": "TEAM_02",
                "Semestre": "2025.2",
                "temporal_marker": "T3",
                "file_path": "src/legacy.py",
                "lines_added": 8,
                "lines_deleted": 2,
                "commit_hash": "c3",
            },
        ]
    )
    git_commits = pd.DataFrame(
        [
            {"commit_hash": "c1", "ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "message": "init project"},
            {"commit_hash": "c2", "ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T3", "message": "finalize app"},
            {"commit_hash": "c3", "ID_Equipe": "TEAM_02", "Semestre": "2025.2", "temporal_marker": "T3", "message": "legacy update"},
        ]
    )
    evaluator = pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "scope_applicability_mean": 2.0, "technical_complexity_mean": 3.0},
            {"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T2", "scope_applicability_mean": 4.0, "technical_complexity_mean": 5.0},
            {"ID_Equipe": "TEAM_02", "Semestre": "2025.2", "temporal_marker": "T1", "scope_applicability_mean": 1.0, "technical_complexity_mean": 2.0},
        ]
    )
    transcript = pd.DataFrame(
        [
            {"Semestre": "2025.2", "temporal_marker": "T1", "transcript_text": "team planning and alignment"},
            {"Semestre": "2025.2", "temporal_marker": "T2", "transcript_text": "coordination friction and merge conflicts"},
            {"Semestre": "2025.2", "temporal_marker": "T3", "transcript_text": "integration pain and deployment issues"},
        ]
    )

    monkeypatch.setattr(module, "call_llm_task", lambda *args, **kwargs: {"t1_planning_score": 7})
    monkeypatch.setattr(module, "call_cohort_llm_task", lambda *args, **kwargs: {"coordination_friction": 6})

    result = module.build_team_level_dataset(
        git_files=git_files,
        git_commits=git_commits,
        evaluator_team_cuts=evaluator,
        transcript_sessions=transcript,
        output_dir=tmp_path,
        llm_cache_path=tmp_path / "cache.json",
        llm_history_path=tmp_path / "history.csv",
        skip_llm=False,
    )

    assert list(result.columns) == [
        "ID_Equipe",
        "Semestre",
        "rework_churn_t3",
        "deferred_churn_t3",
        "t1_planning_score",
        "scope_applicability_mean",
        "technical_complexity_mean",
    ]
    assert result.loc[0, "t1_planning_score"] == 7
    assert result.loc[result["ID_Equipe"] == "TEAM_01", "rework_churn_t3"].iloc[0] == 8
    assert result.loc[result["ID_Equipe"] == "TEAM_01", "deferred_churn_t3"].iloc[0] == 0

    friction = module.build_cohort_friction_dataset(
        transcript_sessions=transcript,
        output_dir=tmp_path,
        llm_cache_path=tmp_path / "cache.json",
        llm_history_path=tmp_path / "history.csv",
        skip_llm=False,
    )
    assert len(friction) == 3
    assert set(friction["temporal_marker"]) == {"T1", "T2", "T3"}
    assert friction["coordination_friction"].tolist() == [6, 6, 6]
