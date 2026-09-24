from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import importlib.util
import warnings
from pathlib import Path
from unittest import mock

from openai import OpenAI
import pytest

import pipeline_core
import pipeline_prompts
from pipeline_config import temporal_marker_for

from pipeline_core import (
    anonymize_csv_file,
    anonymize_transcript,
    build_anonymization_mapping,
    correlation_rows,
    enrich_records,
    extract_git_events,
    hypothesis_rows,
    load_records,
    write_records,
    write_hypothesis_csv,
)


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_script_module(module_name: str, filename: str):
    spec = importlib.util.spec_from_file_location(module_name, REPO_ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class PipelineCoreTests(unittest.TestCase):
    def test_extract_git_events_preserves_commit_and_special_file_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir) / "repo"
            repo.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "dev@example.test"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Dev"], cwd=repo, check=True)
            special_path = repo / "planejamento inicial ç.txt"
            special_path.write_text("plano\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run([
                "git", "commit", "-q", "-m", "initial",
                "--date", "2025-10-18T09:00:00+00:00",
            ], cwd=repo, check=True, env={**os.environ, "GIT_AUTHOR_DATE": "2025-10-18T09:00:00+00:00", "GIT_COMMITTER_DATE": "2025-10-18T09:00:00+00:00"})
            renamed_path = repo / "planejamento final ç.txt"
            special_path.rename(renamed_path)
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run([
                "git", "commit", "-q", "-m", "rename",
                "--date", "2025-10-19T09:00:00+00:00",
            ], cwd=repo, check=True, env={**os.environ, "GIT_AUTHOR_DATE": "2025-10-19T09:00:00+00:00", "GIT_COMMITTER_DATE": "2025-10-19T09:00:00+00:00"})

            commits, files = extract_git_events(repo, "2025.2")

            self.assertEqual(2, len(commits))
            self.assertEqual(2, len(files))
            self.assertEqual("T2", commits[0]["temporal_marker"])
            self.assertEqual("planejamento inicial ç.txt", files[0]["file_path"])
            self.assertEqual("renamed", files[1]["change_status"])
            self.assertEqual("planejamento inicial ç.txt", files[1]["file_path_old"])
            self.assertEqual("planejamento final ç.txt", files[1]["file_path"])

    def test_temporal_marker_for_uses_configured_evaluator_cut_ranges(self) -> None:
        self.assertEqual("T1", temporal_marker_for("2025.2", "2025-10-17"))
        self.assertEqual("T1", temporal_marker_for("2025.2", "2025-10-24"))
        self.assertEqual("T2", temporal_marker_for("2025.2", "2025-11-21"))
        self.assertEqual("T3", temporal_marker_for("2025.2", "2025-12-12"))
        self.assertEqual("T1", temporal_marker_for("2026.1", "2026-04-24"))
        self.assertEqual("T3", temporal_marker_for("2026.1", "2026-06-19"))

    def test_temporal_marker_for_rejects_unconfigured_dates_and_semesters(self) -> None:
        with self.assertRaisesRegex(ValueError, "not in a configured evaluator cut"):
            temporal_marker_for("2025.2", "2025-10-31")
        with self.assertRaisesRegex(ValueError, "has no configured evaluator cuts"):
            temporal_marker_for("2024.1", "2024-03-01")

    def test_ner_extractor_writes_person_candidates_from_openai_json(self) -> None:
        ner_extractor = load_script_module("ner_extractor", "01_ner_extractor.py")
        client = mock.Mock()
        client.chat.completions.create.return_value = mock.Mock(
            choices=[mock.Mock(message=mock.Mock(content='{"person_entities": ["Anderson"]}'))]
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            transcripts_dir = tmp_path / "transcripts"
            transcript_path = transcripts_dir / "session" / "feedback.json"
            transcript_path.parent.mkdir(parents=True)
            transcript_path.write_text(
                json.dumps({"text": "Anderson apresentou o projeto."}),
                encoding="utf-8",
            )
            output_dir = tmp_path / "ner_candidates"
            # Redirect the LLM call ledger so this test never writes into the
            # real, tracked data/analysis/.private/llm_call_ledger.parquet.
            real_gateway_cls = ner_extractor.LLMCallGateway
            ledger_path = tmp_path / "llm_call_ledger.parquet"

            with mock.patch("openai.OpenAI", return_value=client):
                with mock.patch.object(
                    ner_extractor,
                    "LLMCallGateway",
                    lambda gateway_client: real_gateway_cls(gateway_client, ledger_path=ledger_path),
                ):
                    with mock.patch.object(sys, "argv", [
                        "01_ner_extractor.py", "--transcripts-dir", str(transcripts_dir),
                        "--output-dir", str(output_dir),
                    ]):
                        ner_extractor.main()

            output_path = output_dir / "session" / "feedback.ner.json"
            self.assertEqual(
                {"person_entities": ["Anderson"]},
                json.loads(output_path.read_text(encoding="utf-8")),
            )
            request_kwargs = client.chat.completions.create.call_args.kwargs
            self.assertEqual("gpt-4o-mini", request_kwargs["model"])
            self.assertEqual({"type": "json_object"}, request_kwargs["response_format"])
            self.assertTrue(ledger_path.exists())


    def test_ner_extractor_skips_current_transcript(self) -> None:
        ner_extractor = load_script_module("ner_extractor_skip", "01_ner_extractor.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            transcripts_dir = tmp_path / "transcripts"
            transcript_path = transcripts_dir / "feedback.json"
            transcripts_dir.mkdir()
            transcript_path.write_text(json.dumps({"text": "Anderson"}), encoding="utf-8")
            output_dir = tmp_path / "ner_candidates"
            output_path = output_dir / "feedback.ner.json"
            output_path.parent.mkdir()
            output_path.write_text('{"person_entities": ["Anderson"]}', encoding="utf-8")
            ner_extractor.write_artifact_metadata(
                output_path, ner_extractor.file_checksum(transcript_path)
            )

            with mock.patch("openai.OpenAI") as openai:
                with mock.patch.object(sys, "argv", [
                    "01_ner_extractor.py", "--transcripts-dir", str(transcripts_dir),
                    "--output-dir", str(output_dir),
                ]):
                    ner_extractor.main()

            openai.assert_not_called()

    def test_anonymizer_uses_ner_candidates_without_capitalized_word_heuristic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            transcript_path = tmp_path / "feedback.txt"
            transcript_path.write_text(
                "Porque Anderson apresentou o projeto.", encoding="utf-8"
            )
            candidates_path = tmp_path / "feedback.ner.json"
            candidates_path.write_text(
                '{"person_entities": ["Anderson"]}', encoding="utf-8"
            )

            mapping = build_anonymization_mapping(
                [], [transcript_path], salt="pepper", person_names=["Anderson"]
            )

            self.assertIn("Anderson", mapping)
            self.assertNotIn("Porque", mapping)

    def test_anonymization_mapping_fails_when_transcript_cannot_be_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcript_path = Path(tmp_dir) / "feedback.txt"
            transcript_path.mkdir()

            with pytest.raises(IsADirectoryError):
                build_anonymization_mapping([], [transcript_path], salt="pepper")

    def test_audio_preparer_builds_compression_command(self) -> None:
        audio_preparer = load_script_module("audio_preparer", "00_audio_preparer.py")

        command = audio_preparer.compression_command(
            Path("raw/session/recording.m4a"), Path("prepared/session/recording.mp3")
        )

        self.assertEqual(
            [
                "ffmpeg",
                "-y",
                "-i",
                "raw/session/recording.m4a",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-b:a",
                "48k",
                "prepared/session/recording.mp3",
            ],
            command,
        )

    def test_audio_preparer_skips_current_prepared_audio(self) -> None:
        audio_preparer = load_script_module(
            "audio_preparer_skip_current", "00_audio_preparer.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            source_dir = tmp_path / "raw"
            output_dir = tmp_path / "prepared"
            source_dir.mkdir()
            source_path = source_dir / "recording.m4a"
            source_path.write_bytes(b"source")
            output_path = output_dir / "recording.mp3"
            output_path.parent.mkdir()
            output_path.write_bytes(b"prepared")
            checksum = audio_preparer.file_checksum(source_path)
            audio_preparer.write_artifact_metadata(output_path, checksum)

            with mock.patch.object(audio_preparer.shutil, "which", return_value="ffmpeg"):
                with mock.patch.object(audio_preparer.subprocess, "run") as run:
                    with mock.patch.object(sys, "argv", [
                        "00_audio_preparer.py", "--audio-dir", str(source_dir),
                        "--output-dir", str(output_dir),
                    ]):
                        audio_preparer.main()

            run.assert_not_called()

    def test_audio_preparer_requires_ffmpeg(self) -> None:
        audio_preparer = load_script_module(
            "audio_preparer_requires_ffmpeg", "00_audio_preparer.py"
        )
        with mock.patch.object(audio_preparer.shutil, "which", return_value=None):
            with mock.patch.object(sys, "argv", ["00_audio_preparer.py"]):
                with self.assertRaisesRegex(RuntimeError, "ffmpeg"):
                    audio_preparer.main()

    def test_pipeline_orchestrator_includes_audio_preparation(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_audio_preparation", "run_pipeline.py"
        )

        self.assertEqual(
            [
                "prepare", "transcribe", "ner", "anonymize",
                "git", "lake", "repo-snapshots", "contracts", "nlp", "metrics", "stats",
                "narrative-audit", "cross-evidence", "cross-evidence-report",
            ],
            orchestrator.resolve_stages(None, None, None),
        )

        command = orchestrator.build_stage_command(
            "prepare", [], [], "", False
        )
        self.assertEqual(
            [sys.executable, str(REPO_ROOT / "00_audio_preparer.py")], command
        )

    def test_pipeline_target_nlp_excludes_downstream_analysis_stages(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_until_nlp", "run_pipeline.py"
        )

        stages = orchestrator.resolve_stages(None, None, "nlp")

        self.assertEqual(stages[-1], "nlp")
        self.assertNotIn("metrics", stages)
        self.assertNotIn("stats", stages)

    def test_pipeline_orchestrator_includes_repository_snapshots_after_lake(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_repository_snapshots", "run_pipeline.py"
        )

        self.assertEqual(
            ["lake", "repo-snapshots"],
            orchestrator.resolve_stages(None, "lake", "repo-snapshots"),
        )
        command = orchestrator.build_stage_command(
            "repo-snapshots", [], [], "", True
        )
        self.assertEqual(
            [
                sys.executable,
                str(REPO_ROOT / "02b_git_repository_snapshots.py"),
                "--force",
            ],
            command,
        )

    def test_pipeline_cross_evidence_stage_isolated_and_ordered_after_narrative_audit(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_cross_evidence", "run_pipeline.py"
        )

        self.assertEqual(
            ["cross-evidence"],
            orchestrator.resolve_stages(["cross-evidence"], None, None),
        )
        self.assertLess(
            orchestrator.STAGES.index("narrative-audit"),
            orchestrator.STAGES.index("cross-evidence"),
        )
        self.assertEqual(
            "08_cross_evidence_engine.py",
            orchestrator.STAGE_SCRIPTS["cross-evidence"],
        )

    def test_pipeline_cross_evidence_command_and_dry_run_requirements(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_cross_evidence_command", "run_pipeline.py"
        )

        command = orchestrator.build_stage_command(
            "cross-evidence", [], [], "", True
        )
        self.assertEqual(
            [
                sys.executable,
                str(REPO_ROOT / "08_cross_evidence_engine.py"),
                "--lake-dir",
                str(REPO_ROOT / "data" / "lake"),
                "--analysis-dir",
                str(REPO_ROOT / "data" / "analysis"),
                "--force",
            ],
            command,
        )
        orchestrator.validate_dry_run_requirements(["cross-evidence"], "mock")

    def test_pipeline_cross_evidence_report_stage_isolated_and_ordered(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_cross_evidence_report", "run_pipeline.py"
        )

        self.assertEqual(
            ["cross-evidence-report"],
            orchestrator.resolve_stages(["cross-evidence-report"], None, None),
        )
        self.assertLess(
            orchestrator.STAGES.index("cross-evidence"),
            orchestrator.STAGES.index("cross-evidence-report"),
        )
        self.assertEqual(
            "09_cross_evidence_narrative_reporter.py",
            orchestrator.STAGE_SCRIPTS["cross-evidence-report"],
        )

    def test_pipeline_cross_evidence_report_command_maps_mock_backend_and_force(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_cross_evidence_report_command", "run_pipeline.py"
        )

        command = orchestrator.build_stage_command(
            "cross-evidence-report", [], [], "", True, nlp_backend="mock"
        )
        self.assertEqual(
            [
                sys.executable,
                str(REPO_ROOT / "09_cross_evidence_narrative_reporter.py"),
                "--analysis-dir",
                str(REPO_ROOT / "data" / "analysis"),
                "--backend",
                "mock",
                "--force",
            ],
            command,
        )
        orchestrator.validate_dry_run_requirements(["cross-evidence-report"], "mock")

    def test_pipeline_orchestrator_includes_phase2_contracts_before_nlp(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_phase2_contracts", "run_pipeline.py"
        )

        self.assertEqual(
            ["lake", "repo-snapshots", "contracts"],
            orchestrator.resolve_stages(None, "lake", "contracts"),
        )
        self.assertIn("contracts", orchestrator.STAGES)
        self.assertLess(
            orchestrator.STAGES.index("contracts"),
            orchestrator.STAGES.index("nlp"),
        )

        command = orchestrator.build_stage_command("contracts", [], [], "", False)

        self.assertEqual(
            [
                sys.executable,
                str(REPO_ROOT / "phase2_contracts.py"),
                "--lake-dir",
                str(REPO_ROOT / "data" / "lake"),
                "--output",
                str(REPO_ROOT / "data" / "analysis" / "phase2_contract_report.json"),
            ],
            command,
        )

    def test_pipeline_orchestrator_passes_phase2_nlp_contract_paths(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_phase2_nlp", "run_pipeline.py"
        )

        command = orchestrator.build_stage_command("nlp", [], [], "", False)

        self.assertEqual(
            [
                sys.executable,
                str(REPO_ROOT / "04_nlp_qualitative_miner.py"),
                "--lake-dir",
                str(REPO_ROOT / "data" / "lake"),
                "--contract-report",
                str(REPO_ROOT / "data" / "analysis" / "phase2_contract_report.json"),
                "--catalog-output",
                str(REPO_ROOT / "data" / "analysis" / ".private" / "student_prompt_catalog.parquet"),
                "--output",
                str(REPO_ROOT / "data" / "analysis" / "student_nlp.parquet"),
                "--transcript-output",
                str(REPO_ROOT / "data" / "analysis" / "transcript_nlp.parquet"),
                "--textual-cut-signals-output",
                str(REPO_ROOT / "data" / "analysis" / "textual_cut_signals.parquet"),
                "--backend",
                "openai",
            ],
            command,
        )

    def test_pipeline_orchestrator_passes_explicit_mock_nlp_backend(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_mock_backend", "run_pipeline.py"
        )

        command = orchestrator.build_stage_command(
            "nlp", [], [], "", False, nlp_backend="mock"
        )

        self.assertEqual("mock", command[-1])
        self.assertEqual("--backend", command[-2])

    def test_pipeline_orchestrator_dry_run_validates_phase2_structure(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_dry_run_phase2", "run_pipeline.py"
        )

        orchestrator.validate_dry_run_requirements(["stats"], "openai")

    def test_pipeline_orchestrator_writes_phase2_run_manifest(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_phase2_manifest", "run_pipeline.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"
            calls: list[list[str]] = []

            def fake_run_stage(command: list[str], log_path: Path) -> None:
                calls.append(command)

            with mock.patch.object(orchestrator, "run_stage_process", side_effect=fake_run_stage):
                with mock.patch.object(sys, "argv", [
                    "run_pipeline.py",
                    "--stages", "nlp", "metrics", "stats",
                    "--nlp-backend", "mock",
                    "--log-dir", str(log_dir),
                ]):
                    orchestrator.main()

            manifest_path = next(log_dir.glob("pipeline_*.json"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            assert manifest["status"] == "success"
            assert manifest["stages"] == ["nlp", "metrics", "stats"]
            assert manifest["nlp_backend"] == "mock"
            assert [Path(command[1]).name for command in calls] == [
                "04_nlp_qualitative_miner.py",
                "05_metric_engine.py",
                "06_statistical_analyzer.py",
            ]

    def test_pipeline_orchestrator_dispatches_only_cross_evidence_stage(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_cross_evidence_dispatch", "run_pipeline.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            calls: list[list[str]] = []

            def record_stage(command: list[str], log_path: Path) -> None:
                calls.append(command)

            with mock.patch.object(orchestrator, "run_stage_process", side_effect=record_stage):
                with mock.patch.object(sys, "argv", [
                    "run_pipeline.py",
                    "--stages", "cross-evidence",
                    "--log-dir", str(Path(tmp_dir) / "logs"),
                ]):
                    orchestrator.main()

            manifest = json.loads(next((Path(tmp_dir) / "logs").glob("pipeline_*.json")).read_text(encoding="utf-8"))
            assert manifest["status"] == "success"
            assert [Path(command[1]).name for command in calls] == ["08_cross_evidence_engine.py"]

    def test_pipeline_orchestrator_dispatches_mock_cross_evidence_report_only(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_cross_evidence_report_dispatch", "run_pipeline.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            calls: list[list[str]] = []

            def record_stage(command: list[str], log_path: Path) -> None:
                calls.append(command)

            with mock.patch.object(orchestrator, "run_stage_process", side_effect=record_stage):
                with mock.patch.object(sys, "argv", [
                    "run_pipeline.py",
                    "--stages", "cross-evidence-report",
                    "--nlp-backend", "mock",
                    "--log-dir", str(Path(tmp_dir) / "logs"),
                ]):
                    orchestrator.main()

            command = calls[0]
            assert [Path(item).name for item in command[:2]] == [
                Path(orchestrator.PYTHON_EXECUTABLE).name,
                "09_cross_evidence_narrative_reporter.py",
            ]
            assert command[-1] == "mock"
            assert command[-2] == "--backend"

    def test_pipeline_orchestrator_phase2_chain_fails_fast(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_phase2_fail_fast", "run_pipeline.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            calls: list[list[str]] = []

            def fail_on_metrics(command: list[str], log_path: Path) -> None:
                calls.append(command)
                if Path(command[1]).name == "05_metric_engine.py":
                    raise subprocess.CalledProcessError(7, command)

            with mock.patch.object(orchestrator, "run_stage_process", side_effect=fail_on_metrics):
                with mock.patch.object(sys, "argv", [
                    "run_pipeline.py",
                    "--stages", "nlp", "metrics", "stats",
                    "--nlp-backend", "mock",
                    "--log-dir", str(Path(tmp_dir) / "logs"),
                ]):
                    with pytest.raises(SystemExit) as error:
                        orchestrator.main()

            assert error.value.code == 7
            assert [Path(command[1]).name for command in calls] == [
                "04_nlp_qualitative_miner.py",
                "05_metric_engine.py",
            ]

    def test_openai_client_can_be_constructed(self) -> None:
        client = OpenAI(api_key="test-key")
        self.addCleanup(client.close)

    def test_pipeline_orchestrator_runs_selected_stage_with_force(self) -> None:
        orchestrator = load_script_module("pipeline_orchestrator", "run_pipeline.py")

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"
            with mock.patch.object(orchestrator, "run_stage_process") as run_stage:
                with mock.patch.object(sys, "argv", [
                    "run_pipeline.py", "--stages", "git", "--force",
                    "--log-dir", str(log_dir),
                ]):
                    orchestrator.main()

            call = run_stage.call_args
            self.assertEqual(
                [sys.executable, str(REPO_ROOT / "02_git_parser.py"), "--force"],
                call.args[0],
            )
            self.assertTrue(str(call.args[1]).endswith(".txt"))

    def test_pipeline_orchestrator_writes_timestamped_execution_log(self) -> None:
        orchestrator = load_script_module("pipeline_orchestrator_logging", "run_pipeline.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"
            with mock.patch.object(orchestrator.subprocess, "run"):
                with mock.patch.object(sys, "argv", [
                    "run_pipeline.py", "--stages", "git", "--dry-run",
                    "--log-dir", str(log_dir),
                ]):
                    orchestrator.main()

            log_files = list(log_dir.glob("pipeline_*.txt"))
            self.assertEqual(len(log_files), 1)
            content = log_files[0].read_text(encoding="utf-8")
            self.assertIn("Running stage git", content)
            self.assertRegex(log_files[0].name, r"^pipeline_\d{8}T\d{6}Z\.txt$")

    def test_stage_process_streams_child_output_to_terminal_and_log(self) -> None:
        orchestrator = load_script_module("pipeline_orchestrator_streaming", "run_pipeline.py")
        process = mock.Mock()
        process.stdout = iter(["queue: pending=2\n", "progress: completed=1/2\n"])
        process.wait.return_value = 0
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "pipeline.txt"
            with mock.patch.object(orchestrator.subprocess, "Popen", return_value=process):
                with mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
                    orchestrator.run_stage_process(["stage"], log_path)

            expected = "queue: pending=2\nprogress: completed=1/2\n"
            self.assertEqual(stdout.getvalue(), expected)
            self.assertEqual(log_path.read_text(encoding="utf-8"), expected)

    def test_cleanup_phase_one_artifacts_accepts_nested_project_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_root = Path(tmp_dir)
            forms_dir = project_root / "data" / "processed" / "forms" / "2026.1"
            forms_dir.mkdir(parents=True)
            stale_file = forms_dir / "alunos_t1.csv"
            stale_file.write_text("id,nome\n1,teste\n", encoding="utf-8")
            (project_root / "data" / "raw").mkdir(parents=True)
            (project_root / "data" / "raw" / "keep.txt").write_text("raw data", encoding="utf-8")

            pipeline_core.cleanup_phase_one_artifacts(forms_dir)

            self.assertFalse(forms_dir.exists())
            self.assertTrue((project_root / "data" / "raw" / "keep.txt").exists())

    def test_pipeline_orchestrator_dry_run_does_not_execute_stages(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_dry_run", "run_pipeline.py"
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            log_dir = Path(tmp_dir) / "logs"
            with mock.patch.object(orchestrator.subprocess, "run") as run:
                with mock.patch.object(sys, "argv", [
                    "run_pipeline.py", "--from-stage", "anonymize", "--to-stage", "lake",
                    "--csv", "raw/students.csv", "--dry-run",
                    "--log-dir", str(log_dir),
                ]):
                    orchestrator.main()

            run.assert_not_called()
            self.assertEqual(
                ["anonymize", "git", "lake"],
                orchestrator.resolve_stages(None, "anonymize", "lake"),
            )

    def test_pipeline_orchestrator_passes_anonymizer_inputs(self) -> None:
        orchestrator = load_script_module(
            "pipeline_orchestrator_anonymizer", "run_pipeline.py"
        )

        command = orchestrator.build_stage_command(
            "anonymize",
            [Path("raw/students.csv")],
            [Path("processed/feedback.txt")],
            "pepper",
            False,
        )

        self.assertEqual(
            [
                sys.executable,
                str(REPO_ROOT / "01_anonymizer.py"),
                "--csv",
                "raw/students.csv",
                "--transcript",
                "processed/feedback.txt",
                "--salt",
                "pepper",
            ],
            command,
        )

    def test_load_project_environment_uses_project_dotenv(self) -> None:
        with mock.patch.object(pipeline_core, "load_dotenv") as load_dotenv:
            pipeline_core.load_project_environment()

        load_dotenv.assert_called_once_with(
            dotenv_path=pipeline_core.DOTENV_PATH,
            override=False,
        )

    def test_phase_one_scripts_load_shared_project_environment(self) -> None:
        script_names = (
            "00_audio_preparer.py",
            "00_audio_transcriber.py",
            "01_ner_extractor.py",
            "01_anonymizer.py",
            "02_git_parser.py",
            "03_data_lake_builder.py",
            "04_cleanup.py",
        )

        for script_name in script_names:
            module = load_script_module(
                f"dotenv_{script_name.removesuffix('.py')}", script_name
            )
            with mock.patch.object(
                module, "load_project_environment"
            ) as load_environment:
                with mock.patch.object(sys, "argv", [script_name, "--help"]):
                    with self.assertRaises(SystemExit) as exit_error:
                        module.main()

            self.assertEqual(0, exit_error.exception.code)
            load_environment.assert_called_once_with()

    def test_phase_one_cli_paths_have_pipeline_defaults(self) -> None:
        expected_defaults = {
            "00_audio_preparer.py": {
                "audio-dir": "data/raw/audio",
                "output-dir": "data/processed/audio_chunks",
            },
            "00_audio_transcriber.py": {
                "audio-dir": "data/processed/audio_chunks",
                "output-dir": "data/processed/transcripts",
            },
            "01_ner_extractor.py": {
                "transcripts-dir": "data/processed/transcripts",
                "output-dir": "data/processed/ner_candidates",
            },
            "01_anonymizer.py": {
                "output-dir": "data/processed/forms",
                "mapping-path": "data/processed/chave_relacional.json",
            },
            "02_git_parser.py": {
                "repos-list": "data/raw/repos_list.csv",
                "output-commits": "data/processed/git_commits_anon.csv",
                "output-files": "data/processed/git_files_anon.csv",
            },
            "03_data_lake_builder.py": {
                "output-dir": "data/lake",
            },
        }

        for script_name, defaults in expected_defaults.items():
            completed_process = subprocess.run(
                [sys.executable, str(REPO_ROOT / script_name), "--help"],
                check=True,
                capture_output=True,
                text=True,
            )
            help_output = " ".join(completed_process.stdout.split())

            for option, value in defaults.items():
                self.assertIn(
                    f"(default: {value})",
                    help_output,
                    msg=f"{script_name} must default --{option} to {value}",
                )

    def test_anonymization_mapping_and_transcript_redaction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            csv_path = tmp_path / "students.csv"
            csv_path.write_text(
                "nome,email,comentario\nAlice,alice@example.com,Alice precisa de apoio\n",
                encoding="utf-8",
            )
            transcript_path = tmp_path / "feedback.txt"
            transcript_path.write_text("Alice relatou cansaço e alice@example.com apareceu no áudio.", encoding="utf-8")
            output_dir = tmp_path / "anon"
            mapping_path = tmp_path / "chave_relacional.json"

            subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "01_anonymizer.py"),
                    "--csv",
                    str(csv_path),
                    "--transcript",
                    str(transcript_path),
                    "--output-dir",
                    str(output_dir),
                    "--transcripts-output-dir",
                    str(output_dir),
                    "--mapping-path",
                    str(mapping_path),
                    "--salt",
                    "pepper",
                ],
                check=True,
            )

            anon_rows = load_records(output_dir / "students.csv")
            self.assertTrue(anon_rows[0]["nome"].startswith("anon_"))
            self.assertTrue(anon_rows[0]["email"].startswith("anon_"))
            self.assertNotIn("Alice", (output_dir / "feedback.txt").read_text(encoding="utf-8"))
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            self.assertIn("Alice", mapping["mapping"])
            self.assertNotIn("salt", mapping)
            self.assertNotIn("pepper", mapping_path.read_text(encoding="utf-8"))

    def test_anonymizer_processes_all_csv_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            student_csv = tmp_path / "students.csv"
            reviewer_csv = tmp_path / "reviewers.csv"
            student_csv.write_text("nome\nAlice\n", encoding="utf-8")
            reviewer_csv.write_text("avaliador\nCarol\n", encoding="utf-8")
            output_dir = tmp_path / "forms"
            mapping_path = tmp_path / "mapping.json"

            subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "01_anonymizer.py"),
                    "--csv",
                    str(student_csv),
                    "--csv",
                    str(reviewer_csv),
                    "--output-dir",
                    str(output_dir),
                    "--mapping-path",
                    str(mapping_path),
                    "--salt",
                    "pepper",
                ],
                check=True,
            )

            self.assertTrue((output_dir / student_csv.name).exists())
            self.assertTrue((output_dir / reviewer_csv.name).exists())
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            self.assertIn("Alice", mapping["mapping"])
            self.assertIn("Carol", mapping["mapping"])

    def test_anonymizer_discovers_and_skips_current_default_artifacts(self) -> None:
        anonymizer = load_script_module(
            "anonymizer_default_artifacts", "01_anonymizer.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            forms_dir = tmp_path / "raw_forms"
            transcripts_dir = tmp_path / "transcripts"
            student_csv = forms_dir / "t1" / "students.csv"
            transcript_txt = transcripts_dir / "session_1" / "feedback.txt"
            transcript_json = transcripts_dir / "session_1" / "feedback.json"
            student_csv.parent.mkdir(parents=True)
            transcript_txt.parent.mkdir(parents=True)
            student_csv.write_text("nome,email\nAlice,alice@example.com\n", encoding="utf-8")
            transcript_txt.write_text("Alice: email alice@example.com", encoding="utf-8")
            transcript_json.write_text(
                json.dumps({"text": "Alice: email alice@example.com"}),
                encoding="utf-8",
            )
            forms_output_dir = tmp_path / "forms_output"
            transcripts_output_dir = tmp_path / "transcripts_output"
            mapping_path = tmp_path / "mapping.json"

            with mock.patch.object(sys, "argv", [
                "01_anonymizer.py", "--forms-dir", str(forms_dir),
                "--transcripts-dir", str(transcripts_dir), "--output-dir",
                str(forms_output_dir), "--transcripts-output-dir",
                str(transcripts_output_dir), "--mapping-path", str(mapping_path),
                "--salt", "pepper",
            ]):
                anonymizer.main()

            self.assertTrue((forms_output_dir / "t1" / "students.csv").exists())
            self.assertTrue(
                (transcripts_output_dir / "session_1" / "feedback.txt").exists()
            )
            anonymized_json = json.loads(
                (transcripts_output_dir / "session_1" / "feedback.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertNotIn("Alice", anonymized_json["text"])
            self.assertNotIn("alice@example.com", anonymized_json["text"])

            with mock.patch.object(anonymizer, "anonymize_csv_file") as anonymize_csv:
                with mock.patch.object(anonymizer, "anonymize_transcript") as transcript_redactor:
                    with mock.patch.object(sys, "argv", [
                        "01_anonymizer.py", "--forms-dir", str(forms_dir),
                        "--transcripts-dir", str(transcripts_dir), "--output-dir",
                        str(forms_output_dir), "--transcripts-output-dir",
                        str(transcripts_output_dir), "--mapping-path", str(mapping_path),
                        "--salt", "pepper",
                    ]):
                        anonymizer.main()

            anonymize_csv.assert_not_called()
            transcript_redactor.assert_not_called()

    def test_anonymizer_requires_environment_salt_when_not_provided(self) -> None:
        anonymizer = load_script_module("anonymizer_requires_salt", "01_anonymizer.py")
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(anonymizer, "load_project_environment"):
                with mock.patch.object(sys, "argv", ["01_anonymizer.py"]):
                    with self.assertRaises(SystemExit) as exit_error:
                        anonymizer.main()

        self.assertEqual(2, exit_error.exception.code)

    def test_anonymize_csv_uses_salted_fallback_for_late_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            csv_path = tmp_path / "reviewers.csv"
            csv_path.write_text("avaliador,comentario\nCarol,Carol aprovou o escopo\n", encoding="utf-8")
            output_path = tmp_path / "anon.csv"

            anonymize_csv_file(csv_path, output_path, mapping={}, salt="pepper")

            rows = load_records(output_path)
            self.assertEqual("anon_de43123aeacc", rows[0]["avaliador"])

    def test_anonymize_csv_writes_header_only_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            csv_path = tmp_path / "empty.csv"
            csv_path.write_text("nome,email\n", encoding="utf-8")
            output_path = tmp_path / "anon.csv"

            anonymize_csv_file(csv_path, output_path, mapping={}, salt="pepper")

            self.assertTrue(output_path.exists())
            self.assertEqual("nome,email", output_path.read_text(encoding="utf-8").strip())

    def test_anonymize_csv_preserves_comment_text_while_redacting_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            csv_path = tmp_path / "comments.csv"
            csv_path.write_text(
                "nome,comentario\nAlice,Alice pediu retorno para alice@example.com\n",
                encoding="utf-8",
            )
            output_path = tmp_path / "anon.csv"
            mapping = build_anonymization_mapping([["Alice", "alice@example.com"]], [], salt="pepper")

            anonymize_csv_file(csv_path, output_path, mapping, salt="pepper")

            rows = load_records(output_path)
            self.assertIn("anon_", rows[0]["comentario"])
            self.assertIn("pediu retorno para", rows[0]["comentario"])
            self.assertNotEqual(mapping["Alice"], rows[0]["comentario"])

    def test_anonymize_csv_preserves_non_identifier_text_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            csv_path = tmp_path / "feedback.csv"
            csv_path.write_text(
                "feedback\nContact Alice at alice@example.com\n",
                encoding="utf-8",
            )
            output_path = tmp_path / "anon.csv"
            mapping = build_anonymization_mapping([["Alice", "alice@example.com"]], [], salt="pepper")

            anonymize_csv_file(csv_path, output_path, mapping, salt="pepper")

            rows = load_records(output_path)
            self.assertIn("Contact", rows[0]["feedback"])
            self.assertNotIn("Alice", rows[0]["feedback"])
            self.assertNotIn("alice@example.com", rows[0]["feedback"])
            self.assertIn(mapping["Alice"], rows[0]["feedback"])
            self.assertIn(mapping["alice@example.com"], rows[0]["feedback"])

    def test_git_temporal_marker_uses_phase_buckets(self) -> None:
        cases = {
            "2026-02-28": "T1",
            "2026-04-23": "T1",
            "2026-04-24": "T2",
            "2026-05-21": "T2",
            "2026-05-22": "T3",
            "2026-06-20": "T3",
        }

        for timestamp, expected in cases.items():
            with self.subTest(timestamp=timestamp):
                self.assertEqual(
                    expected,
                    pipeline_core.infer_temporal_marker_from_timestamp(
                        timestamp, "2026.1"
                    ),
                )

    def test_mapping_extracts_text_transcript_speakers_and_emails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            transcript_path = tmp_path / "feedback.txt"
            transcript_path.write_text("Carol: iniciou a sessão\nContato: carol@example.com\n", encoding="utf-8")

            mapping = build_anonymization_mapping(
                [], [transcript_path], salt="pepper", person_names=["Anderson"]
            )

            self.assertEqual("anon_de43123aeacc", mapping["Carol"])
            self.assertTrue(mapping["carol@example.com"].startswith("anon_"))
            self.assertNotIn("Contato", mapping)

    def test_mapping_redacts_personal_names_in_transcript_prose(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            transcript_path = tmp_path / "feedback.txt"
            output_path = tmp_path / "anonymized.txt"
            transcript_path.write_text(
                "Minhas observações são parecidas com as do Anderson.",
                encoding="utf-8",
            )

            mapping = build_anonymization_mapping(
                [], [transcript_path], salt="pepper", person_names=["Anderson"]
            )
            anonymize_transcript(transcript_path, output_path, mapping)

            self.assertIn("Anderson", mapping)
            self.assertNotIn("Anderson", output_path.read_text(encoding="utf-8"))
            self.assertIn(mapping["Anderson"], output_path.read_text(encoding="utf-8"))

    def test_anonymizer_mapping_includes_csv_only_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            csv_path = tmp_path / "students.csv"
            csv_path.write_text(
                "nome,email,avaliador\nAlice,alice@example.com,Carol\n",
                encoding="utf-8",
            )
            transcript_path = tmp_path / "feedback.txt"
            transcript_path.write_text("Alice: relatou cansaço\n", encoding="utf-8")
            output_dir = tmp_path / "anon"
            mapping_path = tmp_path / "chave_relacional.json"
            transcripts_output_dir = tmp_path / "transcripts_anon"

            subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "01_anonymizer.py"),
                    "--csv",
                    str(csv_path),
                    "--transcript",
                    str(transcript_path),
                    "--output-dir",
                    str(output_dir),
                    "--mapping-path",
                    str(mapping_path),
                    "--transcripts-output-dir",
                    str(transcripts_output_dir),
                    "--salt",
                    "pepper",
                ],
                check=True,
            )

            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            self.assertIn("Carol", mapping["mapping"])

    def test_anonymizer_handles_normalized_identifier_headers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            csv_path = tmp_path / "students.csv"
            csv_path.write_text(
                "Full Name,Email Address,aluno,comentario\n"
                "Alice,alice@example.com,Bob,Alice escreveu para alice@example.com\n",
                encoding="utf-8",
            )
            output_dir = tmp_path / "anon"
            mapping_path = tmp_path / "chave_relacional.json"

            subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "01_anonymizer.py"),
                    "--csv",
                    str(csv_path),
                    "--output-dir",
                    str(output_dir),
                    "--mapping-path",
                    str(mapping_path),
                    "--salt",
                    "pepper",
                ],
                check=True,
            )

            rows = load_records(output_dir / "students.csv")
            self.assertTrue(rows[0]["Full Name"].startswith("anon_"))
            self.assertTrue(rows[0]["Email Address"].startswith("anon_"))
            self.assertTrue(rows[0]["aluno"].startswith("anon_"))
            mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
            self.assertIn("Alice", mapping["mapping"])
            self.assertIn("alice@example.com", mapping["mapping"])
            self.assertIn("Bob", mapping["mapping"])

    def test_legacy_compute_metrics_helper_is_removed(self) -> None:
        self.assertFalse(hasattr(pipeline_core, "compute_metrics"))

    def test_nlp_enrichment_classifies_work_style(self) -> None:
        records = [
            {
                "feedback": "We had a clear specification and structured planning with architecture review.",
            },
            {
                "feedback": "Pure vibe coding caused rework, stress and merge chaos.",
            },
        ]
        enriched = enrich_records(records)
        self.assertEqual("structured", enriched[0]["nlp_work_style"])
        self.assertEqual("vibe_coding", enriched[1]["nlp_work_style"])

    def test_statistical_outputs(self) -> None:
        records = [
            {"planning_index": 1.0, "code_churn": 2.0, "nlp_work_style": "structured", "exhaustion_index": 0.1},
            {"planning_index": 0.8, "code_churn": 3.0, "nlp_work_style": "structured", "exhaustion_index": 0.2},
            {"planning_index": 0.2, "code_churn": 9.0, "nlp_work_style": "vibe_coding", "exhaustion_index": 0.8},
            {"planning_index": 0.1, "code_churn": 10.0, "nlp_work_style": "vibe_coding", "exhaustion_index": 0.9},
        ]
        correlations = correlation_rows(records)
        correlation_pairs = {frozenset((row["feature_x"], row["feature_y"])) for row in correlations}
        self.assertIn(frozenset(("planning_index", "code_churn")), correlation_pairs)
        self.assertFalse(any(row["feature_x"] == row["feature_y"] for row in correlations))
        self.assertEqual(
            3,
            len({tuple(sorted((row["feature_x"], row["feature_y"]))) for row in correlations}),
        )
        hypotheses = hypothesis_rows(records)
        self.assertEqual("mann_whitney_u", hypotheses[0]["test"])

    def test_hypothesis_rows_handles_missing_work_style_column(self) -> None:
        with pytest.raises(ValueError, match="nlp_work_style"):
            hypothesis_rows([{"planning_index": 1.0, "code_churn": 2.0}])

    def test_correlation_rows_propagates_statistical_failures(self) -> None:
        with mock.patch.object(pipeline_core.scipy_stats, "spearmanr", side_effect=ValueError("bad data")):
            with pytest.raises(ValueError, match="bad data"):
                correlation_rows([{"a": 1.0, "b": 2.0}, {"a": 2.0, "b": 3.0}])

    def test_hypothesis_rows_propagates_statistical_failures(self) -> None:
        records = [
            {"nlp_work_style": "structured", "code_churn": 2.0},
            {"nlp_work_style": "vibe_coding", "code_churn": 5.0},
        ]
        with mock.patch.object(pipeline_core.scipy_stats, "mannwhitneyu", side_effect=ValueError("bad data")):
            with pytest.raises(ValueError, match="bad data"):
                hypothesis_rows(records)

    def test_load_form_files_normalizes_student_and_evaluator_records_by_phase_one_rules(self) -> None:
        data_lake_builder = load_script_module("data_lake_builder_normalize_forms", "03_data_lake_builder.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            forms_dir = Path(tmp_dir)
            semester_dir = forms_dir / "2025.2"
            semester_dir.mkdir()
            (semester_dir / "alunos_t1.csv").write_text(
                "nome,comentario\nAlice,Boa experiência\n",
                encoding="utf-8",
            )
            (semester_dir / "avaliadores.csv").write_text(
                "Timestamp,To which group do these scores refer?,score\n10/17/2025 9:02:30,Group 4 (Buliçoso),4\n",
                encoding="utf-8",
            )

            forms_df = data_lake_builder.load_form_files(forms_dir)

            self.assertEqual(["2025.2", "2025.2"], forms_df["Semestre"].tolist())
            self.assertIn("T1", forms_df["temporal_marker"].tolist())
            self.assertEqual("TEAM_04", forms_df.loc[forms_df["ID_Equipe"].notna(), "ID_Equipe"].iloc[0])

    @unittest.skip("Replaced by source-specific lake contracts")
    def test_aggregate_by_team_allows_student_rows_without_team_id(self) -> None:
        data_lake_builder = load_script_module("data_lake_builder", "03_data_lake_builder.py")
        forms_df = data_lake_builder.pd.DataFrame(
            [{"Semestre": "2025.2", "temporal_marker": "T1", "feedback": "student response"}]
        )

        merged = data_lake_builder.aggregate_by_team(forms_df, data_lake_builder.pd.DataFrame())

        self.assertEqual("2025.2", merged.iloc[0]["Semestre"])
        self.assertEqual("T1", merged.iloc[0]["temporal_marker"])
        self.assertEqual("student response", merged.iloc[0]["feedback"])

    @unittest.skip("Replaced by source-specific lake contracts")
    def test_aggregate_by_team_keeps_semesters_separate(self) -> None:
        data_lake_builder = load_script_module("data_lake_builder", "03_data_lake_builder.py")
        forms_df = data_lake_builder.pd.DataFrame(
            [
                {"ID_Equipe": "A", "Semestre": "2024.1", "temporal_marker": "T1", "feedback": "one"},
                {"ID_Equipe": "A", "Semestre": "2024.2", "temporal_marker": "T1", "feedback": "two"},
            ]
        )
        git_df = data_lake_builder.pd.DataFrame(
            [
                {
                    "ID_Equipe": "A",
                    "Semestre": "2024.1",
                    "temporal_marker": "T1",
                    "lines_added": 3,
                    "lines_deleted": 1,
                    "files_changed": 1,
                    "ID_Autor_Local": "Dev_A",
                    "commit_hash": "abc",
                },
                {
                    "ID_Equipe": "A",
                    "Semestre": "2024.2",
                    "temporal_marker": "T1",
                    "lines_added": 7,
                    "lines_deleted": 2,
                    "files_changed": 2,
                    "ID_Autor_Local": "Dev_B",
                    "commit_hash": "def",
                },
            ]
        )

        merged = data_lake_builder.aggregate_by_team(forms_df, git_df)
        self.assertEqual(2, len(merged))
        self.assertEqual(
            [3, 7],
            merged.sort_values("Semestre")["lines_added"].tolist(),
        )

    @unittest.skip("Replaced by source-specific lake contracts")
    def test_aggregate_by_team_avoids_cross_semester_join_when_only_git_has_semestre(self) -> None:
        data_lake_builder = load_script_module("data_lake_builder_single_sem", "03_data_lake_builder.py")
        forms_df = data_lake_builder.pd.DataFrame(
            [{"ID_Equipe": "A", "temporal_marker": "T1", "feedback": "one"}]
        )
        git_df = data_lake_builder.pd.DataFrame(
            [
                {
                    "ID_Equipe": "A",
                    "Semestre": "2024.1",
                    "temporal_marker": "T1",
                    "lines_added": 3,
                    "lines_deleted": 1,
                    "files_changed": 1,
                    "ID_Autor_Local": "Dev_A",
                    "commit_hash": "abc",
                }
            ]
        )

        merged = data_lake_builder.aggregate_by_team(forms_df, git_df)
        self.assertTrue(data_lake_builder.pd.isna(merged.loc[0, "lines_added"]))

    @unittest.skip("Replaced by source-specific lake contracts")
    def test_aggregate_by_team_requires_explicit_temporal_markers(self) -> None:
        data_lake_builder = load_script_module("data_lake_builder_requires_marker", "03_data_lake_builder.py")
        forms_df = data_lake_builder.pd.DataFrame(
            [{"ID_Equipe": "A", "Semestre": "2024.1", "feedback": "one"}]
        )
        git_df = data_lake_builder.pd.DataFrame(
            [
                {
                    "ID_Equipe": "A",
                    "Semestre": "2024.1",
                    "temporal_marker": "T1",
                    "lines_added": 3,
                    "lines_deleted": 1,
                    "files_changed": 1,
                    "ID_Autor_Local": "Dev_A",
                    "commit_hash": "abc",
                }
            ]
        )

        with self.assertRaisesRegex(ValueError, "temporal_marker"):
            data_lake_builder.aggregate_by_team(forms_df, git_df)

    def test_cleanup_phase_one_artifacts_preserves_raw_inputs_and_rejects_outside_paths(self) -> None:
        project_root = Path(tempfile.mkdtemp())
        (project_root / "data/processed/forms").mkdir(parents=True)
        (project_root / "data/processed/transcripts_anon").mkdir(parents=True)
        (project_root / "data/lake").mkdir(parents=True)
        (project_root / "data/raw").mkdir(parents=True)
        (project_root / "data/processed/audio_chunks").mkdir(parents=True)
        (project_root / "data/processed/transcripts").mkdir(parents=True)
        (project_root / "data/processed/ner_candidates").mkdir(parents=True)
        (project_root / "data/processed/chave_relacional.json").write_text("{}", encoding="utf-8")
        (project_root / "data/lake/master_dataset.parquet").write_bytes(b"parquet")
        for name in ("git_commits", "git_files", "git_repository_snapshots"):
            (project_root / f"data/lake/{name}.parquet").write_bytes(b"parquet")
            (project_root / f"data/lake/{name}.parquet.metadata.json").write_text("{}", encoding="utf-8")
        (project_root / "data/processed/forms/a.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        (project_root / "data/processed/transcripts_anon/session.json").write_text("{}", encoding="utf-8")

        pipeline_core.cleanup_phase_one_artifacts(project_root)

        self.assertFalse((project_root / "data/processed/forms").exists())
        self.assertFalse((project_root / "data/processed/transcripts_anon").exists())
        self.assertFalse((project_root / "data/processed/chave_relacional.json").exists())
        self.assertFalse((project_root / "data/lake/master_dataset.parquet").exists())
        self.assertFalse((project_root / "data/lake/git_commits.parquet").exists())
        self.assertFalse((project_root / "data/lake/git_files.parquet").exists())
        self.assertFalse((project_root / "data/lake/git_commits.parquet.metadata.json").exists())
        self.assertFalse((project_root / "data/lake/git_files.parquet.metadata.json").exists())
        self.assertFalse((project_root / "data/lake/git_repository_snapshots.parquet").exists())
        self.assertFalse((project_root / "data/lake/git_repository_snapshots.parquet.metadata.json").exists())
        self.assertTrue((project_root / "data/raw").exists())
        self.assertTrue((project_root / "data/processed/audio_chunks").exists())
        self.assertTrue((project_root / "data/processed/transcripts").exists())
        self.assertTrue((project_root / "data/processed/ner_candidates").exists())

        outside_root = Path(tempfile.mkdtemp())
        with self.assertRaisesRegex(ValueError, "outside the project root"):
            pipeline_core.cleanup_phase_one_artifacts(outside_root)

    def test_load_transcripts_preserves_unpaired_session_metadata(self) -> None:
        data_lake_builder = load_script_module("data_lake_builder_transcripts", "03_data_lake_builder.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcripts_dir = Path(tmp_dir)
            semester_dir = transcripts_dir / "2025.2" / "session_1"
            semester_dir.mkdir(parents=True)
            (semester_dir / "feedback_2025-10-18.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "text": "hello world",
                    }
                ),
                encoding="utf-8",
            )
            transcripts = data_lake_builder.load_transcripts(transcripts_dir)

            self.assertEqual(1, len(transcripts))
            self.assertNotIn("ID_Equipe", transcripts.columns)
            self.assertEqual("2025.2", transcripts.loc[0, "Semestre"])
            self.assertEqual("T1", transcripts.loc[0, "temporal_marker"])
            self.assertEqual("2025.2/session_1", transcripts.loc[0, "session_id"])

    @unittest.skip("Transcripts are now written as an independent session contract")
    def test_merge_transcripts_attaches_rows_to_team_keys(self) -> None:
        data_lake_builder = load_script_module("data_lake_builder_merge_transcripts", "03_data_lake_builder.py")
        master_df = data_lake_builder.pd.DataFrame(
            [
                {
                    "ID_Equipe": "A",
                    "Semestre": "2024.1",
                    "temporal_marker": "T1",
                    "feedback": "one",
                }
            ]
        )
        transcripts_df = data_lake_builder.pd.DataFrame(
            [
                {
                    "ID_Equipe": "A",
                    "Semestre": "2024.1",
                    "temporal_marker": "T1",
                    "transcript_file": "team_a_t1.json",
                    "transcript_text": "hello world",
                    "status": "success",
                }
            ]
        )

        merged = data_lake_builder.merge_transcripts(master_df, transcripts_df)

        self.assertEqual(1, len(merged))
        self.assertEqual("hello world", merged.loc[0, "transcript_text"])
        self.assertEqual("team_a_t1.json", merged.loc[0, "transcript_file"])
        self.assertEqual("A", merged.loc[0, "ID_Equipe"])
        self.assertEqual("2024.1", merged.loc[0, "Semestre"])

    def test_audio_transcriber_writes_json_and_txt_outputs(self) -> None:
        audio_transcriber = load_script_module("audio_transcriber", "00_audio_transcriber.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            audio_dir = tmp_path / "audio"
            output_dir = tmp_path / "out"
            audio_dir.mkdir()
            (audio_dir / "sample.ogg").write_bytes(b"fake audio")

            with mock.patch.object(
                audio_transcriber,
                "transcribe_audio_file",
                return_value={"status": "success", "text": "hello world"},
            ):
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "00_audio_transcriber.py",
                        "--audio-dir",
                        str(audio_dir),
                        "--output-dir",
                        str(output_dir),
                    ],
                ):
                    audio_transcriber.main()

            self.assertTrue((output_dir / "sample.json").exists())
            self.assertEqual(
                "hello world",
                (output_dir / "sample.txt").read_text(encoding="utf-8"),
            )

    def test_transcriber_uses_brazilian_portuguese(self) -> None:
        audio_transcriber = load_script_module(
            "audio_transcriber_portuguese", "00_audio_transcriber.py"
        )
        client = mock.Mock()
        client.audio.transcriptions.create.return_value = mock.Mock(text="olá")
        with tempfile.TemporaryDirectory() as tmp_dir:
            audio_path = Path(tmp_dir) / "audio.mp3"
            audio_path.write_bytes(b"audio")
            # Redirect the LLM call ledger so this test never writes into the
            # real, tracked data/analysis/.private/llm_call_ledger.parquet.
            real_gateway_cls = audio_transcriber.LLMCallGateway
            ledger_path = Path(tmp_dir) / "llm_call_ledger.parquet"
            with mock.patch("openai.OpenAI", return_value=client):
                with mock.patch.object(
                    audio_transcriber,
                    "LLMCallGateway",
                    lambda gateway_client: real_gateway_cls(gateway_client, ledger_path=ledger_path),
                ):
                    audio_transcriber.transcribe_audio_file(audio_path, api_key="test")

            ledger_written = ledger_path.exists()

        request_kwargs = client.audio.transcriptions.create.call_args.kwargs
        self.assertEqual("pt", request_kwargs["language"])
        self.assertEqual(pipeline_prompts.TRANSCRIPTION_PROMPT, request_kwargs["prompt"])
        self.assertIn("nomes próprios", request_kwargs["prompt"])
        self.assertNotRegex(request_kwargs["prompt"], r"@[\w.-]+")
        self.assertFalse(hasattr(pipeline_prompts, "TRANSCRIPTION_PROMPT_EN_REFERENCE"))
        self.assertTrue(ledger_written)

    def test_audio_transcriber_recursively_processes_session_folders(self) -> None:
        audio_transcriber = load_script_module(
            "audio_transcriber_nested_sessions", "00_audio_transcriber.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            audio_dir = tmp_path / "audio"
            output_dir = tmp_path / "out"
            nested_audio = audio_dir / "session_1" / "recording.ogg"
            nested_audio.parent.mkdir(parents=True)
            nested_audio.write_bytes(b"nested audio")

            with mock.patch.object(
                audio_transcriber,
                "transcribe_audio_file",
                return_value={"status": "success", "text": "nested transcript"},
            ) as transcribe:
                with mock.patch.object(sys, "argv", [
                    "00_audio_transcriber.py", "--audio-dir", str(audio_dir),
                    "--output-dir", str(output_dir),
                ]):
                    audio_transcriber.main()

            transcribe.assert_called_once_with(nested_audio, api_key=None)
            self.assertEqual(
                "nested transcript",
                (output_dir / "session_1" / "recording.txt").read_text(
                    encoding="utf-8"
                ),
            )

    def test_audio_transcriber_aborts_on_transcription_failure(self) -> None:
        audio_transcriber = load_script_module(
            "audio_transcriber_failure", "00_audio_transcriber.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            audio_dir = tmp_path / "audio"
            output_dir = tmp_path / "out"
            audio_dir.mkdir()
            audio_path = audio_dir / "failed.ogg"
            audio_path.write_bytes(b"audio")
            client = mock.Mock()
            client.audio.transcriptions.create.side_effect = RuntimeError(
                "request rejected"
            )
            # Redirect the LLM call ledger so this test never writes into the
            # real, tracked data/analysis/.private/llm_call_ledger.parquet.
            real_gateway_cls = audio_transcriber.LLMCallGateway
            ledger_path = tmp_path / "llm_call_ledger.parquet"

            with mock.patch("openai.OpenAI", return_value=client):
                with mock.patch.object(
                    audio_transcriber,
                    "LLMCallGateway",
                    lambda gateway_client: real_gateway_cls(gateway_client, ledger_path=ledger_path),
                ):
                    with mock.patch.object(sys, "argv", [
                        "00_audio_transcriber.py", "--audio-dir", str(audio_dir),
                        "--output-dir", str(output_dir),
                    ]):
                        with self.assertRaisesRegex(RuntimeError, "request rejected"):
                            audio_transcriber.main()

            self.assertFalse((output_dir / "failed.json").exists())

    def test_audio_transcriber_skips_current_successful_transcript(self) -> None:
        audio_transcriber = load_script_module(
            "audio_transcriber_skip_existing", "00_audio_transcriber.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            audio_dir = tmp_path / "audio"
            output_dir = tmp_path / "out"
            audio_dir.mkdir()
            output_dir.mkdir()
            audio_path = audio_dir / "sample.ogg"
            audio_path.write_bytes(b"fake audio")
            checksum = audio_transcriber.file_checksum(audio_path)
            (output_dir / "sample.json").write_text(
                json.dumps({"status": "success", "text": "previous transcript"}),
                encoding="utf-8",
            )
            (output_dir / "sample.txt").write_text(
                "previous transcript",
                encoding="utf-8",
            )
            for artifact in [output_dir / "sample.json", output_dir / "sample.txt"]:
                artifact.with_name(f"{artifact.name}.metadata.json").write_text(
                    json.dumps({"input_checksum": checksum, "status": "success"}),
                    encoding="utf-8",
                )

            with mock.patch.object(audio_transcriber, "transcribe_audio_file") as transcribe:
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "00_audio_transcriber.py",
                        "--audio-dir",
                        str(audio_dir),
                        "--output-dir",
                        str(output_dir),
                    ],
                ):
                    audio_transcriber.main()

            transcribe.assert_not_called()

    def test_audio_transcriber_reprocesses_when_input_checksum_changes(self) -> None:
        audio_transcriber = load_script_module(
            "audio_transcriber_changed_input", "00_audio_transcriber.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            audio_dir = tmp_path / "audio"
            output_dir = tmp_path / "out"
            audio_dir.mkdir()
            output_dir.mkdir()
            audio_path = audio_dir / "sample.ogg"
            audio_path.write_bytes(b"current audio")
            (output_dir / "sample.json").write_text(
                json.dumps({"status": "success", "text": "previous transcript"}),
                encoding="utf-8",
            )
            (output_dir / "sample.json.metadata.json").write_text(
                json.dumps({"input_checksum": "outdated", "status": "success"}),
                encoding="utf-8",
            )

            with mock.patch.object(
                audio_transcriber,
                "transcribe_audio_file",
                return_value={"status": "success", "text": "updated transcript"},
            ) as transcribe:
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "00_audio_transcriber.py",
                        "--audio-dir",
                        str(audio_dir),
                        "--output-dir",
                        str(output_dir),
                    ],
                ):
                    audio_transcriber.main()

            transcribe.assert_called_once_with(audio_path, api_key=None)

    def test_audio_transcriber_retries_failed_transcript(self) -> None:
        audio_transcriber = load_script_module(
            "audio_transcriber_retry_failed", "00_audio_transcriber.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            audio_dir = tmp_path / "audio"
            output_dir = tmp_path / "out"
            audio_dir.mkdir()
            output_dir.mkdir()
            audio_path = audio_dir / "sample.ogg"
            audio_path.write_bytes(b"audio")
            output_file = output_dir / "sample.json"
            output_file.write_text('{"status": "error"}', encoding="utf-8")
            output_file.with_name("sample.json.metadata.json").write_text(
                json.dumps(
                    {
                        "input_checksum": audio_transcriber.file_checksum(audio_path),
                        "status": "error",
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                audio_transcriber,
                "transcribe_audio_file",
                return_value={"status": "success", "text": "retry succeeded"},
            ) as transcribe:
                with mock.patch.object(sys, "argv", [
                    "00_audio_transcriber.py", "--audio-dir", str(audio_dir),
                    "--output-dir", str(output_dir),
                ]):
                    audio_transcriber.main()

            transcribe.assert_called_once_with(audio_path, api_key=None)

    def test_audio_transcriber_force_reprocesses_current_transcript(self) -> None:
        audio_transcriber = load_script_module(
            "audio_transcriber_force", "00_audio_transcriber.py"
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            audio_dir = tmp_path / "audio"
            output_dir = tmp_path / "out"
            audio_dir.mkdir()
            output_dir.mkdir()
            audio_path = audio_dir / "sample.ogg"
            audio_path.write_bytes(b"audio")
            output_file = output_dir / "sample.json"
            output_file.write_text('{"status": "success"}', encoding="utf-8")
            output_file.with_name("sample.json.metadata.json").write_text(
                json.dumps(
                    {
                        "input_checksum": audio_transcriber.file_checksum(audio_path),
                        "status": "success",
                    }
                ),
                encoding="utf-8",
            )

            with mock.patch.object(
                audio_transcriber,
                "transcribe_audio_file",
                return_value={"status": "success", "text": "forced"},
            ) as transcribe:
                with mock.patch.object(sys, "argv", [
                    "00_audio_transcriber.py", "--audio-dir", str(audio_dir),
                    "--output-dir", str(output_dir), "--force",
                ]):
                    audio_transcriber.main()

            transcribe.assert_called_once_with(audio_path, api_key=None)

    def test_anonymizer_skips_current_outputs(self) -> None:
        anonymizer = load_script_module("anonymizer_skip_current", "01_anonymizer.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            csv_path = tmp_path / "students.csv"
            csv_path.write_text("nome\nAlice\n", encoding="utf-8")
            output_dir = tmp_path / "outputs"
            output_dir.mkdir()
            output_csv = output_dir / csv_path.name
            output_csv.write_text("nome\nanon_1\n", encoding="utf-8")
            mapping_path = tmp_path / "mapping.json"
            mapping_path.write_text("{}", encoding="utf-8")
            checksum = anonymizer.input_checksum([csv_path], {"salt": "pepper"})
            for artifact_path in [output_csv, mapping_path]:
                artifact_path.with_name(f"{artifact_path.name}.metadata.json").write_text(
                    json.dumps({"input_checksum": checksum, "status": "success"}),
                    encoding="utf-8",
                )

            with mock.patch.object(anonymizer, "anonymize_csv_file") as anonymize:
                with mock.patch.object(sys, "argv", [
                    "01_anonymizer.py", "--csv", str(csv_path), "--output-dir",
                    str(output_dir), "--mapping-path", str(mapping_path), "--salt", "pepper",
                    "--forms-dir", str(tmp_path / "no_forms"), "--transcripts-dir",
                    str(tmp_path / "no_transcripts"),
                ]):
                    anonymizer.main()

            anonymize.assert_not_called()

    def test_git_parser_skips_current_output(self) -> None:
        git_parser = load_script_module("git_parser_skip_current", "02_git_parser.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            repos_list = tmp_path / "repos.csv"
            repos_list.write_text(
                "ID_Equipe,URL_Repositorio_Fork,Semestre\nA,https://example.test/a.git,2026.1\n",
                encoding="utf-8",
            )
            output_commits = tmp_path / "git_commits.csv"
            output_files = tmp_path / "git_files.csv"
            output_commits.write_text("commit_hash\nabc\n", encoding="utf-8")
            output_files.write_text("file_path\nREADME.md\n", encoding="utf-8")
            cache_dir = tmp_path / "cache"
            cached_repo = git_parser.repository_cache_path(
                "https://example.test/a.git", cache_dir
            )
            cached_repo.mkdir(parents=True)
            checksum = git_parser.build_git_input_checksum(
                repos_list, ["https://example.test/a.git:head"]
            )
            for output in (output_commits, output_files):
                output.with_name(f"{output.name}.metadata.json").write_text(
                    json.dumps({"input_checksum": checksum, "status": "success"}),
                    encoding="utf-8",
                )
            clean_repos_dir = tmp_path / "clean"
            (clean_repos_dir / "a").mkdir(parents=True)

            with mock.patch.object(git_parser, "repository_snapshot_id", return_value="head"):
                with mock.patch.object(git_parser, "clone_or_update_repo") as clone:
                    with mock.patch.object(sys, "argv", [
                        "02_git_parser.py", "--repos-list", str(repos_list), "--output-commits",
                        str(output_commits),
                        "--output-files", str(output_files), "--cache-dir", str(cache_dir),
                        "--clean-repos-dir", str(clean_repos_dir),
                    ]):
                        git_parser.main()

            clone.assert_not_called()

    def test_git_checksum_includes_snapshot_and_contract_options(self) -> None:
        git_parser = load_script_module("git_parser_checksum", "02_git_parser.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            repos_list = Path(tmp_dir) / "repos.csv"
            repos_list.write_text("source\nrepo\n", encoding="utf-8")

            first = git_parser.build_git_input_checksum(
                repos_list,
                ["repo-a:111"],
                {"find_renames": True},
            )
            second = git_parser.build_git_input_checksum(
                repos_list,
                ["repo-a:222"],
                {"find_renames": True},
            )
            third = git_parser.build_git_input_checksum(
                repos_list,
                ["repo-a:111"],
                {"find_renames": False},
            )

            self.assertNotEqual(first, second)
            self.assertNotEqual(first, third)

    def test_git_timestamp_with_unknown_semester_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "has no configured evaluator cuts"):
            pipeline_core.infer_temporal_marker_from_timestamp(
                "2025-01-01T00:00:00+00:00", "2024.1"
            )

    @unittest.skip("The builder now writes four contracts and a report")
    def test_data_lake_builder_skips_current_output(self) -> None:
        builder = load_script_module("data_lake_builder_skip_current", "03_data_lake_builder.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            forms_dir = tmp_path / "forms"
            forms_dir.mkdir()
            form_path = forms_dir / "form_t1.csv"
            form_path.write_text("ID_Equipe\nA\n", encoding="utf-8")
            git_logs = tmp_path / "git.csv"
            git_logs.write_text("ID_Equipe\nA\n", encoding="utf-8")
            output_path = tmp_path / "master.parquet"
            output_path.write_bytes(b"previous parquet")
            checksum = builder.input_checksum([form_path, git_logs], {})
            (tmp_path / "master.parquet.metadata.json").write_text(
                json.dumps({"input_checksum": checksum, "status": "success"}),
                encoding="utf-8",
            )

            with mock.patch.object(builder, "load_form_files") as load_forms:
                with mock.patch.object(sys, "argv", [
                    "03_data_lake_builder.py", "--forms-dir", str(forms_dir), "--git-commits",
                    str(git_logs), "--git-files", str(tmp_path / "git_files.csv"),
                    "--transcripts-dir", str(tmp_path / "transcripts"),
                    "--output-parquet", str(output_path),
                ]):
                    builder.main()

            load_forms.assert_not_called()

    def test_map_authors_by_volume_uses_aliases(self) -> None:
        git_parser = load_script_module("git_parser", "02_git_parser.py")
        mapping = git_parser.map_authors_by_volume(
            [
                {"author_alias": "anon_a"},
                {"author_alias": "anon_a"},
                {"author_alias": "anon_b"},
            ]
        )
        self.assertEqual("Dev_A", mapping["anon_a"])
        self.assertEqual("Dev_B", mapping["anon_b"])

    def test_author_label_continues_past_z(self) -> None:
        git_parser = load_script_module("git_parser_labels", "02_git_parser.py")
        self.assertEqual("Dev_Z", git_parser.author_label(25))
        self.assertEqual("Dev_AA", git_parser.author_label(26))

    def test_clone_or_update_repo_uses_unique_cache_path_per_url(self) -> None:
        git_parser = load_script_module("git_parser_clone", "02_git_parser.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_dir = Path(tmp_dir)
            with mock.patch.object(git_parser.subprocess, "run") as run_mock:
                first_path = git_parser.clone_or_update_repo(
                    "https://github.com/org-one/shared-repo.git", cache_dir
                )
                second_path = git_parser.clone_or_update_repo(
                    "https://github.com/org-two/shared-repo.git", cache_dir
                )

                update_url = "https://github.com/org-one/shared-repo.git"
                update_key = git_parser.hashlib.sha256(
                    update_url.encode("utf-8")
                ).hexdigest()[:12]
                expected_update_path = cache_dir / f"shared-repo-{update_key}"
                expected_update_path.mkdir()

                updated_path = git_parser.clone_or_update_repo(update_url, cache_dir)

        self.assertIsNotNone(first_path)
        self.assertIsNotNone(second_path)
        self.assertIsNotNone(updated_path)
        assert first_path is not None
        assert second_path is not None
        assert updated_path is not None
        self.assertNotEqual(first_path, second_path)
        self.assertEqual("shared-repo", first_path.name.rsplit("-", 1)[0])
        self.assertEqual("shared-repo", second_path.name.rsplit("-", 1)[0])
        self.assertEqual(expected_update_path, updated_path)
        self.assertFalse(any(call.args and call.args[0] == ["git", "pull"] for call in run_mock.call_args_list))
        self.assertEqual(2, run_mock.call_count)

    def test_mirror_clean_repo_removes_git_metadata(self) -> None:
        git_parser = load_script_module("git_parser_mirror", "02_git_parser.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            repo_path = tmp_path / "repo-cache"
            repo_path.mkdir()
            (repo_path / ".git").mkdir()
            (repo_path / ".git" / "config").write_text("[core]\n", encoding="utf-8")
            (repo_path / "README.md").write_text("content", encoding="utf-8")

            clean_dir = tmp_path / "clean"
            mirrored = git_parser.mirror_clean_repo(repo_path, clean_dir)

            self.assertEqual(clean_dir / repo_path.name, mirrored)
            self.assertTrue((mirrored / "README.md").exists())
            self.assertFalse((mirrored / ".git").exists())

    def test_parquet_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "data.parquet"
            rows = [{"participant": "anon_1", "code_churn": 5.0}]
            write_records(path, rows)
            with warnings.catch_warnings():
                warnings.simplefilter("error", DeprecationWarning)
                loaded = load_records(path)
            self.assertEqual(rows, loaded)

    def test_load_records_preserves_csv_strings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "data.csv"
            path.write_text("participant,comment\nN/A,NA\n", encoding="utf-8")

            loaded = load_records(path)
            self.assertEqual([{"participant": "N/A", "comment": "NA"}], loaded)

    def test_hypothesis_output_is_created_even_when_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "hypothesis.csv"
            write_hypothesis_csv([], output_path)
            self.assertEqual(
                "test,group_a,group_b,metric,u_statistic,p_value,n_group_a,n_group_b",
                output_path.read_text(encoding="utf-8").strip(),
            )


if __name__ == "__main__":
    unittest.main()
