from __future__ import annotations

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

from pipeline_core import (
    anonymize_csv_file,
    build_anonymization_mapping,
    compute_metrics,
    correlation_rows,
    enrich_records,
    extract_git_history,
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
    def test_phase_one_cli_paths_have_pipeline_defaults(self) -> None:
        expected_defaults = {
            "00_audio_transcriber.py": {
                "audio-dir": "data/raw/audio",
                "output-dir": "data/processed/transcripts",
            },
            "01_anonymizer.py": {
                "output-dir": "data/processed/forms",
                "mapping-path": "data/processed/chave_relacional.json",
            },
            "02_git_parser.py": {
                "repos-list": "data/raw/repos_list.csv",
                "output-csv": "data/processed/git_logs_anon.csv",
            },
            "03_data_lake_builder.py": {
                "output-parquet": "data/lake/master_dataset.parquet",
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

    def test_git_history_is_anonymized_and_mirrored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            repo_path = tmp_path / "sample-repo"
            repo_path.mkdir()
            subprocess.run(["git", "init"], cwd=repo_path, check=True, stdout=subprocess.DEVNULL)
            (repo_path / "README.md").write_text("hello\n", encoding="utf-8")
            env = os.environ | {
                "GIT_AUTHOR_NAME": "Alice",
                "GIT_AUTHOR_EMAIL": "alice@example.com",
                "GIT_COMMITTER_NAME": "Alice",
                "GIT_COMMITTER_EMAIL": "alice@example.com",
            }
            subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True, env=env)
            subprocess.run(["git", "commit", "-m", "initial commit"], cwd=repo_path, check=True, env=env, stdout=subprocess.DEVNULL)

            mapping = build_anonymization_mapping([], [], salt="pepper")
            rows = extract_git_history(repo_path, mapping, salt="pepper")
            self.assertEqual(1, len(rows))
            self.assertTrue(rows[0]["author_alias"].startswith("anon_"))
            self.assertEqual("sample-repo", rows[0]["repository"])
            self.assertEqual(1, rows[0]["files_changed"])
            self.assertNotIn("author_email", rows[0])

    def test_mapping_extracts_text_transcript_speakers_and_emails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            transcript_path = tmp_path / "feedback.txt"
            transcript_path.write_text("Carol: iniciou a sessão\nContato: carol@example.com\n", encoding="utf-8")

            mapping = build_anonymization_mapping([], [transcript_path], salt="pepper")

            self.assertEqual("anon_de43123aeacc", mapping["Carol"])
            self.assertTrue(mapping["carol@example.com"].startswith("anon_"))
            self.assertNotIn("Contato", mapping)

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

    def test_nlp_and_metrics_pipeline(self) -> None:
        records = [
            {
                "feedback": "We had a clear specification and structured planning with architecture review.",
                "lines_added": 10,
                "lines_deleted": 2,
                "files_changed": 2,
                "technical_complexity_t1": 2,
                "technical_complexity_t3": 3,
            },
            {
                "feedback": "Pure vibe coding caused rework, stress and merge chaos.",
                "lines_added": 8,
                "lines_deleted": 12,
                "files_changed": 4,
                "technical_complexity_t1": 1,
                "technical_complexity_t3": 5,
            },
        ]
        enriched = enrich_records(records)
        self.assertEqual("structured", enriched[0]["nlp_work_style"])
        self.assertEqual("vibe_coding", enriched[1]["nlp_work_style"])

        metric_rows = compute_metrics(enriched)
        self.assertAlmostEqual(12.0, metric_rows[0]["code_churn"])
        self.assertGreater(metric_rows[1]["exhaustion_index"], 0)
        self.assertGreater(metric_rows[1]["delta_technical_degradation"], metric_rows[0]["delta_technical_degradation"])

    def test_metrics_coerce_string_numbers(self) -> None:
        metric_rows = compute_metrics(
            [
                {
                    "nlp_work_style": "structured",
                    "lines_added": "10",
                    "lines_deleted": "2",
                    "technical_complexity_t1": "2",
                    "technical_complexity_t3": "5",
                }
            ]
        )
        self.assertEqual(12.0, metric_rows[0]["code_churn"])
        self.assertEqual(3.0, metric_rows[0]["delta_technical_degradation"])
        self.assertEqual(0.3, metric_rows[0]["exhaustion_index"])

    def test_metrics_coerce_comma_decimal_strings(self) -> None:
        metric_rows = compute_metrics(
            [
                {
                    "nlp_work_style": "structured",
                    "lines_added": "2,5",
                    "lines_deleted": "1,5",
                    "technical_complexity_t1": "1,0",
                    "technical_complexity_t3": "3,5",
                }
            ]
        )
        self.assertEqual(4.0, metric_rows[0]["code_churn"])
        self.assertEqual(2.5, metric_rows[0]["delta_technical_degradation"])
        self.assertEqual(0.25, metric_rows[0]["exhaustion_index"])

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
        self.assertEqual([], hypothesis_rows([{"planning_index": 1.0, "code_churn": 2.0}]))

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

    def test_load_transcripts_requires_team_and_semester_metadata(self) -> None:
        data_lake_builder = load_script_module("data_lake_builder_transcripts", "03_data_lake_builder.py")
        with tempfile.TemporaryDirectory() as tmp_dir:
            transcripts_dir = Path(tmp_dir)
            (transcripts_dir / "team_a_t1.json").write_text(
                json.dumps(
                    {
                        "ID_Equipe": "A",
                        "Semestre": "2024.1",
                        "status": "success",
                        "text": "hello world",
                    }
                ),
                encoding="utf-8",
            )
            (transcripts_dir / "missing_meta_t1.json").write_text(
                json.dumps({"status": "success", "text": "ignored"}),
                encoding="utf-8",
            )

            transcripts_df = data_lake_builder.load_transcripts(transcripts_dir)

        self.assertEqual(1, len(transcripts_df))
        self.assertEqual("A", transcripts_df.loc[0, "ID_Equipe"])
        self.assertEqual("2024.1", transcripts_df.loc[0, "Semestre"])
        self.assertEqual("T1", transcripts_df.loc[0, "temporal_marker"])

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
            output_csv = tmp_path / "git_logs.csv"
            output_csv.write_text("commit_hash\nabc\n", encoding="utf-8")
            checksum = git_parser.file_checksum(repos_list)
            (tmp_path / "git_logs.csv.metadata.json").write_text(
                json.dumps({"input_checksum": checksum, "status": "success"}),
                encoding="utf-8",
            )
            clean_repos_dir = tmp_path / "clean"
            (clean_repos_dir / "a").mkdir(parents=True)

            with mock.patch.object(git_parser, "clone_or_update_repo") as clone:
                with mock.patch.object(sys, "argv", [
                    "02_git_parser.py", "--repos-list", str(repos_list), "--output-csv",
                    str(output_csv), "--cache-dir", str(tmp_path / "cache"),
                    "--clean-repos-dir", str(clean_repos_dir),
                ]):
                    git_parser.main()

            clone.assert_not_called()

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
                    "03_data_lake_builder.py", "--forms-dir", str(forms_dir), "--git-logs",
                    str(git_logs), "--transcripts-dir", str(tmp_path / "transcripts"),
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
        run_mock.assert_any_call(
            ["git", "pull"],
            cwd=expected_update_path,
            capture_output=True,
            check=True,
            timeout=30,
        )
        self.assertEqual(3, run_mock.call_count)

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
