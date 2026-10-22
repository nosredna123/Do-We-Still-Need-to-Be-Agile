"""Verify the shipped public rows without access to private research inputs."""

from __future__ import annotations

import csv
import io
import math
from pathlib import Path
import unittest

from build_catalog import validate_catalog
from snapshot_io import csv_bytes, json_bytes, read_json


class PublicSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.site = Path(__file__).resolve().parent.parent
        cls.catalog = read_json(cls.site / "data/catalog.json")
        cls.descriptors = {d["id"]: d for d in cls.catalog["datasets"]}
        cls.datasets = {
            dataset_id: read_json(cls.site / descriptor["paths"]["json"])
            for dataset_id, descriptor in cls.descriptors.items()
        }

    def test_exact_file_inventory(self) -> None:
        self.assertEqual(self.catalog["status"], "snapshot_prepared_release_pending")
        self.assertEqual(len(self.datasets), 49)
        for kind, suffix in (("json", ".json"), ("csv", ".csv")):
            folder = "datasets" if kind == "json" else "downloads"
            actual = {p.relative_to(self.site).as_posix() for p in (self.site / "data" / folder).rglob("*")}
            expected = {d["paths"][kind] for d in self.descriptors.values()}
            self.assertEqual(actual, expected)
            self.assertTrue(all(path.endswith(suffix) for path in actual))
        self.assertFalse((self.site / "data/definitions").exists())
        self.assertFalse(any("excerpt" in path.name for path in (self.site / "data").rglob("*")))
        self.assertFalse(any(path.is_symlink() for path in (self.site / "data").rglob("*")))

    def test_catalog_schema_keys_and_typed_values(self) -> None:
        validate_catalog(self.catalog)
        checks = {
            "string": lambda value: type(value) is str,
            "integer": lambda value: type(value) is int,
            "boolean": lambda value: type(value) is bool,
            "number": lambda value: type(value) in (int, float) and math.isfinite(value),
        }
        for dataset_id, rows in self.datasets.items():
            with self.subTest(dataset=dataset_id):
                self.assertTrue(rows)
                descriptor = self.descriptors[dataset_id]
                expected = [column["id"] for column in descriptor["columns"]]
                identities = []
                for row in rows:
                    self.assertEqual(list(row), expected)
                    identity = tuple(row[key] for key in descriptor["key"])
                    self.assertTrue(all(value is not None and value != "" for value in identity))
                    identities.append(identity)
                    for column in descriptor["columns"]:
                        value = row[column["id"]]
                        self.assertTrue(column["nullable"] if value is None else checks[column["type"]](value),
                                        (dataset_id, column["id"]))
                self.assertEqual(len(identities), len(set(identities)))

    def test_json_csv_exact_serialization_and_parity(self) -> None:
        for dataset_id, rows in self.datasets.items():
            with self.subTest(dataset=dataset_id):
                descriptor = self.descriptors[dataset_id]
                self.assertEqual((self.site / descriptor["paths"]["json"]).read_bytes(), json_bytes(rows))
                content = (self.site / descriptor["paths"]["csv"]).read_bytes()
                self.assertEqual(content, csv_bytes(rows))
                reader = csv.DictReader(io.StringIO(content.decode("utf-8"), newline=""))
                self.assertEqual(reader.fieldnames, list(rows[0]))
                records = list(reader)
                self.assertEqual(len(records), len(rows))
                for row, record in zip(rows, records):
                    for key, value in row.items():
                        expected = "" if value is None else "true" if value is True else "false" if value is False else str(value)
                        self.assertEqual(record[key], expected)

    def test_measured_and_unmeasured_planning(self) -> None:
        rows = self.datasets["m6b-planning-content"]
        fields = ("planning_evidence_present", "goals_n", "architecture_or_design_n",
                  "task_decomposition_n", "risk_or_dependency_n", "evidence_quotes_n")
        self.assertEqual(sum(row["measurement_status"] == "success" for row in rows), 9)
        self.assertEqual(sum(row["measurement_status"] == "unavailable_not_measured" for row in rows), 5)
        for row in rows:
            if row["measurement_status"] == "unavailable_not_measured":
                self.assertTrue(all(row[field] is None for field in fields))
            else:
                self.assertIs(type(row["planning_evidence_present"]), bool)
                self.assertTrue(all(type(row[field]) is int and row[field] >= 0 for field in fields[1:]))
        self.assertTrue(any(row["evidence_quotes_n"] == 0 for row in rows if row["measurement_status"] == "success"))
        self.assertTrue(all(type(row["planning_artifact_activity_t1"]) is int
                            for row in self.datasets["m6a-structural-planning"]))

    def test_rework_eligibility_ratios_and_profile_agreement(self) -> None:
        rework = {(r["cohort"], r["team_id"]): r for r in self.datasets["m8-rework-magnitude"]}
        self.assertEqual(sum(row["baseline_eligible_for_rework_t3"] for row in rework.values()), 12)
        self.assertEqual(sum(row["ratio_status"] == "baseline_not_observed" for row in rework.values()), 2)
        for row in rework.values():
            eligible = row["prior_clean_path_n"] > 0
            self.assertEqual(row["baseline_eligible_for_rework_t3"], eligible)
            status = "baseline_not_observed" if not eligible else "zero_clean_churn" if row["clean_total_churn_t3"] == 0 else "available"
            self.assertEqual(row["ratio_status"], status)
            if status == "available":
                self.assertAlmostEqual(row["clean_rework_ratio_t3"],
                                       row["clean_rework_churn_t3"] / row["clean_total_churn_t3"], places=12)
            else:
                self.assertIsNone(row["clean_rework_ratio_t3"])
        for dataset_id in ("complexity-profile", "complexity-rework-figure"):
            for row in self.datasets[dataset_id]:
                reference = rework[row["cohort"], row["team_id"]]
                for field in ("clean_rework_churn_t3", "clean_rework_ratio_t3",
                              "baseline_eligible_for_rework_t3", "ratio_status"):
                    if field == "clean_rework_ratio_t3" and reference[field] is not None:
                        # Distinct source tables retain their original serialization precision.
                        self.assertAlmostEqual(row[field], reference[field], delta=1e-12)
                    else:
                        self.assertEqual(row[field], reference[field])

    def test_coverage_and_grain_boundaries(self) -> None:
        canonical = {(r["cohort"], r["team_id"]) for r in self.datasets["m6a-structural-planning"]}
        self.assertEqual(len(canonical), 14)
        self.assertEqual(sum(cohort == "2025.2" for cohort, _ in canonical), 9)
        self.assertEqual(sum(cohort == "2026.1" for cohort, _ in canonical), 5)
        self.assertEqual(sum(len(rows) for rows in self.datasets.values()), 1674)
        self.assertEqual(sum(len(row) for rows in self.datasets.values() for row in rows), 17046)
        for dataset_id, rows in self.datasets.items():
            key = self.descriptors[dataset_id]["key"]
            if "team_id" in key:
                self.assertEqual({(r["cohort"], r["team_id"]) for r in rows}, canonical)
            if self.descriptors[dataset_id]["source"] in ("surveys", "transcript-aggregates"):
                self.assertTrue(all("team_id" not in row for row in rows))
        coverage = {r["checkpoint"]: r["transcript_chunk_n"] for r in self.datasets["m5-corpus-coverage"]}
        self.assertEqual(coverage, {"T1": 35, "T2": 37, "T3": 28})
        for field in ("median_clean_rework_churn_t3", "median_clean_rework_ratio_t3_baseline_eligible"):
            self.assertEqual(len({r[field] for r in self.datasets["transcript-context-2025"]}), 1)
        for row in self.datasets["m3-participation"]:
            self.assertEqual(row["final_window_commit_n"], row["pre_commit_n"] + row["post_commit_n"])

    def test_unavailable_concentration_and_no_private_fields(self) -> None:
        forbidden_fields = {
            "repository", "repository_url", "respondent_hash", "author_id", "input_subjects", "raw_response",
            "parsed_response", "evidence_quotes", "period_start", "period_end", "source_path",
            "checkpoint_anchor", "prompt_sha256", "commit_hash", "commit_subject",
        }
        for dataset_id, rows in self.datasets.items():
            for row in rows:
                self.assertFalse(forbidden_fields & row.keys(), dataset_id)
                self.assertTrue(all(not isinstance(v, (list, dict)) for v in row.values()))
                for value in row.values():
                    if isinstance(value, str):
                        self.assertFalse(value.startswith(("/", "http://", "https://", "file://")))
            if dataset_id in ("m3-author-concentration", "m3-rolling"):
                for row in rows:
                    if row["measurement_status"] == "no_observed_activity":
                        self.assertEqual(row["commit_n"], 0)
                        self.assertIsNone(row["max_author_share"])
                        self.assertIsNone(row["author_gini"])


if __name__ == "__main__":
    unittest.main()
