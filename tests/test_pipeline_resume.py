from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_pipeline_starts_without_destructive_cleanup() -> None:
    pipeline = load_module("resume_orchestrator", "run_pipeline.py")

    stages = pipeline.resolve_stages(None, None, None)

    assert stages[0] == "prepare"
    assert "cleanup" not in stages


def test_lake_builder_skips_current_contracts(tmp_path: Path) -> None:
    builder = load_module("resume_lake_builder", "03_data_lake_builder.py")
    output_dir = tmp_path / "lake"
    output_dir.mkdir()
    forms_dir = tmp_path / "forms"
    transcripts_dir = tmp_path / "transcripts"
    forms_dir.mkdir()
    transcripts_dir.mkdir()
    git_commits = tmp_path / "commits.csv"
    git_files = tmp_path / "files.csv"
    git_commits.write_text("commits", encoding="utf-8")
    git_files.write_text("files", encoding="utf-8")
    checksum = "same-checksum"
    names = builder.DATASET_NAMES
    for name in names:
        artifact = output_dir / f"{name}.parquet"
        artifact.write_bytes(b"existing")
        artifact.with_name(f"{artifact.name}.metadata.json").write_text(
            json.dumps({"status": "success", "input_checksum": checksum}),
            encoding="utf-8",
        )

    with mock.patch.object(builder, "source_paths", return_value=[git_commits, git_files]), mock.patch.object(
        builder, "input_checksum", return_value=checksum
    ), mock.patch.object(builder, "load_form_files") as load_forms, mock.patch.object(
        builder, "load_git_commits"
    ) as load_commits, mock.patch.object(builder, "load_git_files") as load_files, mock.patch.object(
        builder, "load_transcripts"
    ) as load_transcripts:
        builder.build_lake(forms_dir, git_commits, transcripts_dir, output_dir, git_files)

    load_forms.assert_not_called()
    load_commits.assert_not_called()
    load_files.assert_not_called()
    load_transcripts.assert_not_called()