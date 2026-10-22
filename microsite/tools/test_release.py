"""Public-only release metadata and failure-path regression tests."""

from __future__ import annotations

import csv
import hashlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest

from build_release import build_release, main
from snapshot_io import ContractError, json_bytes, read_json


class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.site = Path(__file__).resolve().parent.parent

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.copy = Path(self.temporary.name) / "site"
        shutil.copytree(self.site / "data", self.copy / "data")

    def test_saved_release_and_independent_reproduction(self) -> None:
        release = build_release(self.copy)
        self.assertEqual((self.site / "data/release.json").read_bytes(), json_bytes(release))
        self.assertEqual(release["schema_version"], "1.0")
        self.assertEqual(release["snapshot_id"], "research-data-001")
        self.assertEqual(release["status"], "snapshot_prepared_release_pending")
        self.assertEqual(release["summary"], {
            "dataset_count": 49, "artifact_count": 99,
            "observation_row_count": 1674, "scalar_cell_count": 17046,
        })

    def test_exact_public_artifact_hashes(self) -> None:
        release = build_release(self.copy)
        paths = []
        for artifact in release["artifacts"]:
            path = self.copy / artifact["path"]
            paths.append(artifact["path"])
            self.assertEqual(artifact["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(artifact["bytes"], path.stat().st_size)
            if path.suffix == ".csv":
                rows = list(csv.DictReader(io.StringIO(path.read_text(), newline="")))
                self.assertEqual(artifact["row_count"], len(rows))
            elif path.parent.name == "datasets":
                self.assertEqual(artifact["row_count"], len(read_json(path)))
        actual = {p.relative_to(self.copy).as_posix()
                  for p in (self.copy / "data").rglob("*") if p.is_file()}
        self.assertEqual(set(paths), actual - {"data/release.json"})
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn("data/release.json", paths)

    def test_rows_and_scientific_coverage(self) -> None:
        release = build_release(self.copy)
        datasets = {dataset["id"]: dataset for dataset in release["datasets"]}
        self.assertEqual(sum(d["row_count"] for d in datasets.values()), 1674)
        for dataset_id, descriptor in datasets.items():
            rows = read_json(self.copy / "data/datasets" / (dataset_id + ".json"))
            self.assertEqual(descriptor["row_count"], len(rows))
            self.assertEqual(descriptor["column_count"], len(rows[0]))
        planning = datasets["m6b-planning-content"]["coverage"]
        self.assertEqual(planning["measurement_status_counts"], {
            "success": 9, "unavailable_not_measured": 5,
        })
        self.assertEqual(planning["team_semesters_by_cohort"], {"2025.2": 9, "2026.1": 5})
        rework = datasets["m8-rework-magnitude"]["coverage"]
        self.assertEqual(rework["baseline_eligible"], 12)
        self.assertEqual(rework["baseline_ineligible"], 2)
        corpus = datasets["m5-corpus-coverage"]["coverage"]
        self.assertEqual(corpus["declared"]["cohorts"], ["2025.2"])
        self.assertEqual(corpus["chunks_by_checkpoint"], {"T1": 35, "T2": 37, "T3": 28})
        self.assertNotIn("team_semesters_by_cohort", corpus)
        self.assertNotIn("team_semesters_by_cohort", datasets["m2-role-summaries"]["coverage"])

    def test_public_only_metadata(self) -> None:
        release = build_release(self.copy)
        content = json_bytes(release).decode()
        for marker in (str(self.site), str(self.copy), "source_sha256", "contract_sha256",
                       "index_sha256", "reviewer", "lineage", "http://", "https://"):
            self.assertNotIn(marker, content)
        self.assertEqual(set(release), {
            "schema_version", "snapshot_id", "status", "path_base", "hash_algorithm",
            "artifact_scope", "coverage_note", "summary", "artifacts", "datasets",
        })

    def test_missing_or_extra_artifact_rejected(self) -> None:
        path = self.copy / "data/downloads/m1-perceptions.csv"
        content = path.read_bytes()
        path.unlink()
        with self.assertRaises((ContractError, OSError)):
            build_release(self.copy)
        path.write_bytes(content)
        (self.copy / "data/private.json").write_text("{}")
        with self.assertRaisesRegex(ContractError, "inventory"):
            build_release(self.copy)

    def test_csv_disagreement_and_malformed_rows_rejected(self) -> None:
        csv_path = self.copy / "data/downloads/m1-perceptions.csv"
        content = csv_path.read_bytes()
        csv_path.write_bytes(content + b"\n")
        with self.assertRaisesRegex(ContractError, "CSV"):
            build_release(self.copy)
        csv_path.write_bytes(content)
        path = self.copy / "data/datasets/m1-perceptions.json"
        rows = read_json(path)
        rows[0]["unapproved_field"] = 1
        path.write_bytes(json_bytes(rows))
        with self.assertRaisesRegex(ContractError, "columns"):
            build_release(self.copy)

    def test_wrong_types_and_duplicate_keys_rejected(self) -> None:
        path = self.copy / "data/datasets/m6a-structural-planning.json"
        original = path.read_bytes()
        rows = read_json(path)
        rows[0]["planning_artifact_activity_t1"] = True
        path.write_bytes(json_bytes(rows))
        with self.assertRaisesRegex(ContractError, "type"):
            build_release(self.copy)
        path.write_bytes(original)
        rows = read_json(path)
        rows.append(rows[0])
        path.write_bytes(json_bytes(rows))
        with self.assertRaisesRegex(ContractError, "key"):
            build_release(self.copy)

    def test_symlinks_rejected(self) -> None:
        path = self.copy / "data/downloads/m1-perceptions.csv"
        target = Path(self.temporary.name) / "outside.csv"
        path.rename(target)
        path.symlink_to(target)
        with self.assertRaisesRegex(ContractError, "Symlink"):
            build_release(self.copy)

    def test_cli_no_overwrite_stale_check_and_invalid_input(self) -> None:
        output = Path(self.temporary.name) / "candidate.json"
        arguments = ["--site-root", str(self.copy), "--output", str(output)]
        self.assertEqual(main(arguments), 0)
        self.assertEqual(main(arguments + ["--check"]), 0)
        with self.assertLogs(level="ERROR"):
            self.assertEqual(main(arguments), 1)
        altered = read_json(output)
        altered["artifacts"][0]["sha256"] = "0" * 64
        output.write_bytes(json_bytes(altered))
        with self.assertLogs(level="ERROR"):
            self.assertEqual(main(arguments + ["--check"]), 1)
        (self.copy / "data/downloads/m1-perceptions.csv").unlink()
        new_output = output.with_name("invalid.json")
        with self.assertLogs(level="ERROR"):
            self.assertEqual(main(["--site-root", str(self.copy), "--output", str(new_output)]), 1)
        self.assertFalse(new_output.exists())


if __name__ == "__main__":
    unittest.main()
