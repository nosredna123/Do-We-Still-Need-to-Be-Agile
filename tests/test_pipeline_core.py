from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
import importlib.util
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

    def test_parquet_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "data.parquet"
            rows = [{"participant": "anon_1", "code_churn": 5.0}]
            write_records(path, rows)
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
