from __future__ import annotations

import json
import importlib.util
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "data_lake_builder_refactoring", REPO_ROOT / "03_data_lake_builder.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_lake_writes_separate_contracts_and_validation_report(tmp_path: Path) -> None:
    builder = load_builder()
    forms_dir = tmp_path / "forms" / "2025.2"
    forms_dir.mkdir(parents=True)
    (forms_dir / "alunos_t1.csv").write_text("resposta\nboa\n", encoding="utf-8")
    (forms_dir / "avaliadores.csv").write_text(
        "Timestamp,To which group do these scores refer?,"
        "What is the score for \"Engagement/Participation\"?,"
        "What is the score for \"Project Progress\"?,"
        "What is the score for \"Scope/Applicability\"?,"
        "What is the score for \"Technical Complexity\"?\n"
        "10/17/2025 09:00:00,Group 4 (Team),5,4,3,2\n"
        "10/18/2025 09:00:00,Group 4 (Team),3,2,1,2\n",
        encoding="utf-8",
    )
    git_path = tmp_path / "git_logs_anon.csv"
    pd.DataFrame(
        [
            {
                "ID_Equipe": "TEAM_04",
                "Semestre": "2025.2",
                "temporal_marker": "T1",
                "lines_added": 3,
                "lines_deleted": 1,
                "files_changed": 2,
                "ID_Autor_Local": "Dev_A",
                "commit_hash": "abc",
            }
        ]
    ).to_csv(git_path, index=False)
    transcripts_dir = tmp_path / "transcripts"
    session_dir = transcripts_dir / "2025.2" / "session_1"
    session_dir.mkdir(parents=True)
    (session_dir / "feedback_2025-10-18.json").write_text(
        json.dumps({"status": "success", "text": "private transcript"}),
        encoding="utf-8",
    )

    output_dir = tmp_path / "lake"
    builder.build_lake(forms_dir, git_path, transcripts_dir, output_dir)

    expected_names = (
        "student_responses",
        "evaluator_team_cuts",
        "git_team_cuts",
        "transcript_sessions",
    )
    for name in expected_names:
        parquet_path = output_dir / f"{name}.parquet"
        assert parquet_path.exists()
        metadata = json.loads(
            (output_dir / f"{name}.parquet.metadata.json").read_text()
        )
        assert metadata["status"] == "success"

    assert not (output_dir / "master_dataset.parquet").exists()
    evaluator = pd.read_parquet(output_dir / "evaluator_team_cuts.parquet")
    assert evaluator.loc[0, "git_match_status"] == "matched"
    assert evaluator.loc[0, "engagement_participation_mean"] == 4
    assert evaluator.loc[0, "engagement_participation_median"] == 4
    assert evaluator.loc[0, "engagement_participation_n"] == 2
    assert evaluator.loc[0, "engagement_participation_std"] == 2**0.5
    assert evaluator.loc[0, "engagement_participation_iqr"] == 1
    assert evaluator.loc[0, "project_progress_mean"] == 3
    assert evaluator.loc[0, "scope_applicability_mean"] == 2
    assert evaluator.loc[0, "technical_complexity_mean"] == 2
    assert not any(column.startswith("What is the score") for column in evaluator.columns)
    report = json.loads((output_dir / "lake_validation_report.json").read_text())
    assert report["status"] == "success"
    assert report["pii_status"] == "passed"
    assert report["evaluator_score_names"] == [
        "engagement_participation",
        "project_progress",
        "scope_applicability",
        "technical_complexity",
    ]
    assert "private transcript" not in json.dumps(report)


def test_aggregate_evaluator_cuts_marks_missing_git_activity() -> None:
    builder = load_builder()
    evaluator = pd.DataFrame(
        [{
            "ID_Equipe": "TEAM_04",
            "Semestre": "2025.2",
            "temporal_marker": "T1",
            'What is the score for "Engagement/Participation"?': 5,
            "source_type": "evaluator_team_cut",
        }]
    )

    result = builder.aggregate_evaluator_cuts(evaluator, pd.DataFrame())

    assert result.loc[0, "git_match_status"] == "no_observed_activity"


def test_transcript_loader_derives_short_filename_date_from_semester(tmp_path: Path) -> None:
    builder = load_builder()
    transcript_dir = tmp_path / "2025.2" / "session_1"
    transcript_dir.mkdir(parents=True)
    (transcript_dir / "MyRec_1024_1131.part000.json").write_text(
        json.dumps({"status": "success", "text": "redacted"}), encoding="utf-8"
    )

    transcripts = builder.load_transcripts(tmp_path)

    assert transcripts.loc[0, "temporal_marker"] == "T1"
    assert transcripts.loc[0, "temporal_marker_source"] == "filename"