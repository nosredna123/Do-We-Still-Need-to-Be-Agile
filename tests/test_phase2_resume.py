from __future__ import annotations

import json
from pathlib import Path

from pipeline_core import (
    ANALYSIS_DIR,
    ensure_analysis_dir,
    invalidate_artifacts,
    invalidate_stale_artifact,
    phase2_input_checksum,
    write_artifact_metadata,
    is_current_artifact,
)


def _write_phase2_inputs(tmp_path: Path) -> tuple[Path, Path]:
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()
    for name in (
        "student_responses",
        "evaluator_team_cuts",
        "git_team_cuts",
        "git_commits",
        "git_files",
        "git_repository_snapshots",
        "transcript_sessions",
    ):
        parquet = lake_dir / f"{name}.parquet"
        sidecar = lake_dir / f"{name}.parquet.metadata.json"
        parquet.write_bytes(name.encode("utf-8"))
        sidecar.write_text(json.dumps({"status": "success"}), encoding="utf-8")
    prompt = tmp_path / "pipeline_prompts.py"
    prompt.write_text("PROMPT_VERSION = 'v1'\n", encoding="utf-8")
    return lake_dir, prompt


def test_phase2_input_checksum_includes_contract_sidecars_prompts_and_options(tmp_path: Path) -> None:
    lake_dir, prompt = _write_phase2_inputs(tmp_path)
    first = phase2_input_checksum(lake_dir, [prompt], {"model": "test", "temperature": 0})

    prompt.write_text("PROMPT_VERSION = 'v2'\n", encoding="utf-8")
    second = phase2_input_checksum(lake_dir, [prompt], {"model": "test", "temperature": 0})
    assert first != second

    sidecar = lake_dir / "git_files.parquet.metadata.json"
    sidecar.write_text(json.dumps({"status": "success", "revision": 2}), encoding="utf-8")
    third = phase2_input_checksum(lake_dir, [prompt], {"model": "test", "temperature": 0})
    assert second != third

    fourth = phase2_input_checksum(lake_dir, [prompt], {"model": "test", "temperature": 1})
    assert third != fourth


def test_phase2_input_checksum_rejects_missing_contract_or_prompt(tmp_path: Path) -> None:
    lake_dir, prompt = _write_phase2_inputs(tmp_path)
    (lake_dir / "git_commits.parquet").unlink()
    missing_prompt = tmp_path / "missing_prompts.py"

    try:
        phase2_input_checksum(lake_dir, [prompt], {})
    except FileNotFoundError as error:
        assert "git_commits.parquet" in str(error)
    else:
        raise AssertionError("missing contract must fail")

    (lake_dir / "git_commits.parquet").write_bytes(b"restored")
    try:
        phase2_input_checksum(lake_dir, [missing_prompt], {})
    except FileNotFoundError as error:
        assert str(missing_prompt) in str(error)
    else:
        raise AssertionError("missing prompt must fail")


def test_write_metadata_supports_resume_contract_and_effective_options(tmp_path: Path) -> None:
    artifact = tmp_path / "analysis" / "result.parquet"
    artifact.parent.mkdir()
    artifact.write_bytes(b"result")
    write_artifact_metadata(
        artifact,
        "checksum",
        contract_version="phase2-v1",
        options={"model": "test", "temperature": 0},
    )

    metadata = json.loads(artifact.with_name(f"{artifact.name}.metadata.json").read_text())
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "phase2-v1"
    assert metadata["options"] == {"model": "test", "temperature": 0}
    assert is_current_artifact(artifact, "checksum")


def test_invalidate_artifacts_removes_artifact_and_sidecar(tmp_path: Path) -> None:
    artifact = tmp_path / "analysis" / "result.parquet"
    artifact.parent.mkdir()
    artifact.write_bytes(b"result")
    write_artifact_metadata(artifact, "checksum")

    invalidate_artifacts([artifact])

    assert not artifact.exists()
    assert not artifact.with_name(f"{artifact.name}.metadata.json").exists()


def test_invalidate_stale_artifact_removes_checksum_mismatch(tmp_path: Path) -> None:
    artifact = tmp_path / "analysis" / "result.parquet"
    artifact.parent.mkdir()
    artifact.write_bytes(b"result")
    write_artifact_metadata(artifact, "old-checksum")

    assert invalidate_stale_artifact(artifact, "new-checksum") is True
    assert not artifact.exists()
    assert not artifact.with_name(f"{artifact.name}.metadata.json").exists()


def test_ensure_analysis_dir_uses_requested_path(tmp_path: Path) -> None:
    analysis_dir = tmp_path / "data" / "analysis"
    result = ensure_analysis_dir(analysis_dir)

    assert result == analysis_dir
    assert result.is_dir()
    assert ANALYSIS_DIR.name == "analysis"