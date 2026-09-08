from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from phase2_contracts import (
    load_phase2_inputs,
    validate_phase1_contracts,
    write_contract_report,
)


CONTRACT_FILES = (
    "student_responses.parquet",
    "evaluator_team_cuts.parquet",
    "git_team_cuts.parquet",
    "git_commits.parquet",
    "git_files.parquet",
    "git_repository_snapshots.parquet",
    "transcript_sessions.parquet",
)


def _write_contracts(tmp_path: Path) -> Path:
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()
    frames = {
        "student_responses.parquet": pd.DataFrame(
            [{"Semestre": "2025.2", "temporal_marker": "T1", "source_file": "a.csv", "source_type": "student_response"}]
        ),
        "evaluator_team_cuts.parquet": pd.DataFrame(
            [{"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "technical_complexity_mean": 1.0}]
        ),
        "git_team_cuts.parquet": pd.DataFrame(
            [{"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "lines_added": 3, "lines_deleted": 1, "files_changed": 2, "num_authors": 1, "num_commits": 1}]
        ),
        "git_commits.parquet": pd.DataFrame(
            [{"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "abc", "timestamp": pd.Timestamp("2025-10-18", tz="UTC"), "lines_added": 3, "lines_deleted": 1, "files_changed": 2, "ID_Autor_Local": "Dev_1", "branch_or_ref": "refs/heads/main", "branch_or_ref_source": "observed"}]
        ),
        "git_files.parquet": pd.DataFrame(
            [{"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "commit_hash": "abc", "timestamp": pd.Timestamp("2025-10-18", tz="UTC"), "file_path": "src/a.py", "change_status": "added", "is_binary": False}]
        ),
        "git_repository_snapshots.parquet": pd.DataFrame(
            [{"ID_Equipe": "TEAM_01", "Semestre": "2025.2", "temporal_marker": "T1", "repository": "repo", "snapshot_commit_hash": "abc", "snapshot_timestamp": pd.Timestamp("2025-10-18", tz="UTC"), "snapshot_available": True, "repo_source_loc": 10}]
        ),
        "transcript_sessions.parquet": pd.DataFrame(
            [{"session_id": "s1", "transcript_file": "s1.txt", "Semestre": "2025.2", "temporal_marker": "T1", "temporal_marker_source": "filename", "transcript_text": "texto"}]
        ),
    }
    for filename, frame in frames.items():
        path = lake_dir / filename
        frame.to_parquet(path, index=False)
        (lake_dir / f"{filename}.metadata.json").write_text(
            json.dumps({"status": "success"}), encoding="utf-8"
        )
    return lake_dir


@pytest.mark.parametrize("filename", CONTRACT_FILES)
def test_load_phase2_inputs_requires_every_contract(tmp_path: Path, filename: str) -> None:
    lake_dir = _write_contracts(tmp_path)
    (lake_dir / filename).unlink()

    with pytest.raises(FileNotFoundError, match=filename):
        load_phase2_inputs(lake_dir)


def test_load_phase2_inputs_rejects_invalid_sidecar(tmp_path: Path) -> None:
    lake_dir = _write_contracts(tmp_path)
    sidecar = lake_dir / "git_commits.parquet.metadata.json"
    sidecar.write_text(json.dumps({"status": "failed"}), encoding="utf-8")

    with pytest.raises(ValueError, match="status"):
        load_phase2_inputs(lake_dir)


def test_validation_rejects_missing_source_file_and_duplicate_key(tmp_path: Path) -> None:
    lake_dir = _write_contracts(tmp_path)
    student_path = lake_dir / "student_responses.parquet"
    student = pd.read_parquet(student_path)
    student.loc[0, "source_file"] = ""
    student.to_parquet(student_path, index=False)
    evaluator_path = lake_dir / "evaluator_team_cuts.parquet"
    evaluator = pd.read_parquet(evaluator_path)
    evaluator = pd.concat([evaluator, evaluator], ignore_index=True)
    evaluator.to_parquet(evaluator_path, index=False)

    inputs = load_phase2_inputs(lake_dir)
    with pytest.raises(ValueError, match="source_file|duplicate"):
        validate_phase1_contracts(inputs)


def test_validation_rejects_non_utc_git_timestamp_and_snapshot_invariants(tmp_path: Path) -> None:
    lake_dir = _write_contracts(tmp_path)
    commits_path = lake_dir / "git_commits.parquet"
    commits = pd.read_parquet(commits_path)
    commits["timestamp"] = commits["timestamp"].dt.tz_localize(None)
    commits.to_parquet(commits_path, index=False)

    inputs = load_phase2_inputs(lake_dir)
    with pytest.raises(ValueError, match="UTC"):
        validate_phase1_contracts(inputs)


def test_validation_reconciles_git_team_cuts_before_success(tmp_path: Path) -> None:
    lake_dir = _write_contracts(tmp_path)
    team_path = lake_dir / "git_team_cuts.parquet"
    team = pd.read_parquet(team_path)
    team.loc[0, "lines_added"] = 99
    team.to_parquet(team_path, index=False)

    inputs = load_phase2_inputs(lake_dir)
    with pytest.raises(ValueError, match="reconcil"):
        validate_phase1_contracts(inputs)


def test_validation_rejects_loose_transcript_source_without_reading_it(tmp_path: Path) -> None:
    lake_dir = _write_contracts(tmp_path)
    loose = tmp_path / "data" / "processed" / "transcripts_anon"
    loose.mkdir(parents=True)
    (loose / "unexpected.txt").write_text("PII", encoding="utf-8")

    inputs = load_phase2_inputs(lake_dir)
    report = validate_phase1_contracts(inputs)
    assert report["status"] == "success"


def test_contract_report_contains_privacy_safe_schema_and_counts(tmp_path: Path) -> None:
    lake_dir = _write_contracts(tmp_path)
    report = validate_phase1_contracts(load_phase2_inputs(lake_dir))
    write_path = tmp_path / "analysis" / "phase2_contract_report.json"
    write_contract_report(report, write_path)
    written = json.loads(write_path.read_text(encoding="utf-8"))

    student_report = written["contracts"]["student_responses"]
    assert "null_counts" in student_report
    assert student_report["null_counts"]["source_file"] == 0
    assert student_report["counts_by_semester_and_cut"] == [
        {"Semestre": "2025.2", "temporal_marker": "T1", "rows": 1}
    ]
    assert student_report["keys"]["columns"] == []
    assert written["violations"] == []
    assert "texto" not in write_path.read_text(encoding="utf-8")


def test_validation_rejects_observable_snapshot_without_hash(tmp_path: Path) -> None:
    lake_dir = _write_contracts(tmp_path)
    path = lake_dir / "git_repository_snapshots.parquet"
    snapshots = pd.read_parquet(path)
    snapshots.loc[0, "snapshot_commit_hash"] = None
    snapshots.to_parquet(path, index=False)

    with pytest.raises(ValueError, match="snapshot_commit_hash"):
        validate_phase1_contracts(load_phase2_inputs(lake_dir))


def test_validation_rejects_negative_observable_source_loc(tmp_path: Path) -> None:
    lake_dir = _write_contracts(tmp_path)
    path = lake_dir / "git_repository_snapshots.parquet"
    snapshots = pd.read_parquet(path)
    snapshots.loc[0, "repo_source_loc"] = -1
    snapshots.to_parquet(path, index=False)

    with pytest.raises(ValueError, match="repo_source_loc"):
        validate_phase1_contracts(load_phase2_inputs(lake_dir))