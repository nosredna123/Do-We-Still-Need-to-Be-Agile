from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
)


REPO_ROOT = Path(__file__).resolve().parent.parent


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
            self.assertEqual("anon_8c20d385a603", rows[0]["avaliador"])

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

    def test_statistical_outputs(self) -> None:
        records = [
            {"planning_index": 1.0, "code_churn": 2.0, "nlp_work_style": "structured", "exhaustion_index": 0.1},
            {"planning_index": 0.8, "code_churn": 3.0, "nlp_work_style": "structured", "exhaustion_index": 0.2},
            {"planning_index": 0.2, "code_churn": 9.0, "nlp_work_style": "vibe_coding", "exhaustion_index": 0.8},
            {"planning_index": 0.1, "code_churn": 10.0, "nlp_work_style": "vibe_coding", "exhaustion_index": 0.9},
        ]
        correlations = correlation_rows(records)
        self.assertTrue(any(row["feature_x"] == "planning_index" and row["feature_y"] == "code_churn" for row in correlations))
        hypotheses = hypothesis_rows(records)
        self.assertEqual("mann_whitney_u", hypotheses[0]["test"])

    def test_parquet_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "data.parquet"
            rows = [{"participant": "anon_1", "code_churn": 5.0}]
            write_records(path, rows)
            loaded = load_records(path)
            self.assertEqual(rows, loaded)


if __name__ == "__main__":
    unittest.main()
