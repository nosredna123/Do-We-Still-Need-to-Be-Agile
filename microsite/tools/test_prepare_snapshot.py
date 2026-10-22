"""Synthetic fixtures only: run with python -B -m unittest discover -s tools."""

from __future__ import annotations

import csv
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import re
import tempfile
import unittest

from prepare_snapshot import (
    ContractError, agree, approvals, csv_bytes, csv_rows, json_bytes, json_projections,
    keyed, main, project, ratio_policy, read_json, resolved, scalar, write_snapshot,
)
from snapshot_contracts import CONTRACT_SHA256, INDEX_SHA256, TABLES, table


class ScalarTests(unittest.TestCase):
    def test_projections_match_the_reviewed_document(self) -> None:
        document = (Path(__file__).resolve().parent.parent / "dataset-contracts.md").read_text()
        documented = {}
        for line in document.splitlines():
            if re.match(r"\| `[^`]+\.(csv|json)` \|", line):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                source = re.findall(r"`([^`]+)`", cells[0])[0]
                documented[source] = cells
        macros = {"C": ["cohort"], "CP": ["cohort", "checkpoint"], "T": ["cohort", "team_id"],
                  "TP": ["cohort", "team_id", "checkpoint"], "P": ["checkpoint"], "W": ["window_end_day"]}
        overrides = {
            "m6a-presence-by-cohort": "cohort evidence_state team_semester_n team_semester_count",
            "planning-rework-profile": "cohort team_id pi_file_count_t1 pi_line_delta_t1 planning_artifact_present_t1 "
                                      "planning_scope_log1p_t1 measurement_status clean_rework_churn_t3 baseline_eligible_for_rework_t3",
            "complexity-rework-figure": "cohort team_id technical_complexity_mean_t3 clean_rework_churn_t3 "
                                       "clean_rework_ratio_t3 planning_scope_tier planning_scope_log1p_t1 "
                                       "score_trajectory_group final7_commit_share_pct final7_clean_churn_share_pct",
            "weekly-bin-definitions": "week_bin week_bin_order start_day_relative_to_t3 end_day_relative_to_t3 "
                                      "interval_notation assignment_policy rolling_window_used",
            "complexity-definitions": "metric construct_family definition heuristic_or_policy manual_genai_architecture_classification",
        }

        def inline_fields(block: str) -> set[str]:
            return {field.strip().split(" -> ")[-1]
                    for group in re.findall(r"`([^`]+)`", block) for field in group.split(",")}

        for spec in TABLES:
            if spec.dataset_id in overrides:
                expected = set(overrides[spec.dataset_id].split())
            else:
                cells = documented[spec.source]
                expression = re.findall(r"`([^`]+)`", cells[2])[0]
                expected = set()
                for key in expression.split(" + "):
                    expected.update(macros.get(key, [key]))
                fields = cells[3]
                if "Same fields as" in fields:
                    alias_id = re.findall(r"`([^`]+)`", fields)[0]
                    fields = next(c[3] for c in documented.values() if c[1] == f"`{alias_id}`")
                if spec.dataset_id == "complexity-profile":
                    fields = document.split("The `complexity-profile` projection is", 1)[1].split(".\n", 1)[0]
                expected |= inline_fields(fields)
                if spec.dataset_id == "operational-regularity":
                    expected |= inline_fields(document.split("The eight retained regularity components are", 1)[1].split(".\n", 1)[0])
            self.assertEqual({target for _, target in spec.fields}, expected, spec.dataset_id)

    def test_strict_types_and_precision(self) -> None:
        self.assertIs(scalar("False", "pi_available", "test"), False)
        self.assertIs(type(scalar("7", "planning_artifact_activity_t1", "test")), int)
        self.assertEqual(scalar("2025.2", "cohort", "test"), "2025.2")
        self.assertEqual(scalar("1.791759469228055", "planning_scope_log1p_t1", "test"), 1.791759469228055)
        self.assertEqual(scalar("5", "category", "m1-autonomy"), 5)
        self.assertEqual(scalar("5", "category", "m1-frequency"), "5")
        self.assertIsNone(scalar("", "spearman_rho", "test"))

    def test_invalid_scalars(self) -> None:
        for value, field in (
            ("true", "pi_available"), ("1", "pi_available"), ("", "count"),
            ("1.2", "count"), ("-1", "count"), ("NaN", "mean"), ("inf", "mean"),
            ("2", "spearman_rho"), ("-0.1", "share"), ("101", "final7_share_pct"),
            ("T4", "checkpoint"), ("6", "score"),
        ):
            with self.subTest(value=value, field=field), self.assertRaises(ContractError):
                scalar(value, field, "test")

    def test_ragged_schema_empty_and_duplicate_headers(self) -> None:
        for content, columns, count in (
            (b"a,a\n1,2\n", ["a", "a"], 1),
            (b"a,b\n1\n", ["a", "b"], 1),
            (b"a\n1,2\n", ["a"], 1),
            (b"a\n", ["a"], 0),
            (b"a\n1\n", ["different"], 1),
        ):
            with self.subTest(content=content), self.assertRaises(ContractError):
                csv_rows(content, columns, count)

    def test_projection_drops_private_fields_and_checks_keys(self) -> None:
        spec = table("synthetic.csv", "test", "T", "count")
        rows = [{"Semestre": "C", "ID_Equipe": "A", "count": "2", "secret": "not exported"}]
        projected = project(spec, rows, {"C": "C"}, {("C", "A"): ("C", "A")})
        self.assertEqual(projected, [{"cohort": "C", "team_id": "A", "count": 2}])
        for invalid in (rows * 2, [dict(rows[0], ID_Equipe="B")], [dict(rows[0], ID_Equipe="")]):
            with self.assertRaises(ContractError):
                project(spec, invalid, {"C": "C"}, {("C", "A"): ("C", "A")})
        with self.assertRaises(ContractError):
            project(spec, [{"Semestre": "C", "ID_Equipe": "A"}], {"C": "C"}, {("C", "A"): ("C", "A")})

    def test_definition_deduplication_rejects_conflicts(self) -> None:
        spec = table("synthetic.csv", "weekly-bin-definitions", "week_bin", "assignment_policy", definition=True)
        teams = {("C", label): ("C", label) for label in ("A", "B", "D")}
        rows = [{"Semestre": "C", "ID_Equipe": label, "week_bin": "one", "assignment_policy": "same"}
                for label in ("A", "B")]
        self.assertEqual(len(project(spec, rows, {"C": "C"}, teams)), 1)
        with self.assertRaises(ContractError):
            project(spec, rows + [dict(rows[0], ID_Equipe="D", assignment_policy="different")], {"C": "C"}, teams)

    def test_alias_coverage_and_values(self) -> None:
        rows = [{"key": "a", "value": "1.0000000000001"}]
        agree(rows, [{"key": "a", "value": "1"}], ("key",), {"value"})
        for invalid in ([{"key": "b", "value": "1"}], [{"key": "a", "value": "2"}]):
            with self.assertRaises(ContractError):
                agree(rows, invalid, ("key",), {"value"})
        with self.assertRaises(ContractError):
            keyed([{"key": ""}], ("key",))

    def test_ratio_precedence_and_eligible_values(self) -> None:
        for eligible, total, expected in (
            ("False", "10", "baseline_not_observed"), ("False", "0", "baseline_not_observed"),
            ("True", "0", "zero_clean_churn"), ("True", "10", "available"),
        ):
            row = {"clean_rework_ratio_t3": 0.123456789}
            ratio_policy(row, {"baseline_eligible_for_rework_t3": eligible, "clean_total_churn_t3": total})
            self.assertEqual(row["ratio_status"], expected)
            self.assertEqual(row["clean_rework_ratio_t3"], 0.123456789 if expected == "available" else None)

    def test_json_csv_same_values_quoting_and_null(self) -> None:
        rows = [{"label": 'a,"b"\nnext', "count": 4, "share": 0.123456789, "flag": False, "ratio": None}]
        self.assertEqual(json.loads(json_bytes(rows)), rows)
        csv_row = next(csv.DictReader(io.StringIO(csv_bytes(rows).decode())))
        self.assertEqual(csv_row, {"label": 'a,"b"\nnext', "count": "4", "share": "0.123456789",
                                   "flag": "false", "ratio": ""})
        for bad in ("=SUM(1)", " +formula", "-formula", "@formula", "\tformula", " \tformula"):
            with self.assertRaises(ContractError):
                csv_bytes([{"label": bad}])
        self.assertIn(b"-0.5", csv_bytes([{"delta": -0.5}]))

    def test_unapproved_field_has_no_cli_projection_override(self) -> None:
        self.assertFalse(any("raw_response" in dict(t.fields) for t in TABLES))
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main(["--fields", "raw_response"])


class FilesystemTests(unittest.TestCase):
    def test_duplicate_json_key_and_nonfinite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for content in ('{"a":1,"a":2}', '{"value":NaN}'):
                path.write_text(content)
                with self.assertRaises(ContractError):
                    read_json(path)

    def test_symlink_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "link").symlink_to(root, target_is_directory=True)
            with self.assertRaises(ContractError):
                resolved(root / "link" / "file")

    def test_deterministic_output_and_private_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = {"example": [{"count": 2, "flag": True}]}
            for name in ("a", "b"):
                write_snapshot(root / name, root / (name + ".json"), rows, {}, {"private": "lineage"})
            for path in (root / "a").rglob("*"):
                if path.is_file():
                    self.assertEqual(path.read_bytes(), (root / "b" / path.relative_to(root / "a")).read_bytes())
                    self.assertNotIn(b"private", path.read_bytes())
            self.assertEqual((root / "a.json").stat().st_mode & 0o777, 0o600)
            with self.assertRaises(ContractError):
                write_snapshot(root / "a", root / "new.json", rows, {}, {})

    def test_failure_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ContractError):
                write_snapshot(root / "data", root / "lineage.json",
                               {"example": [{"text": "=formula"}]}, {}, {})
            self.assertEqual(list(root.iterdir()), [])
            with self.assertRaises(ContractError):
                write_snapshot(root / "data", root / "data" / "private.json",
                               {"example": [{"count": 1}]}, {}, {})
            self.assertEqual(list(root.iterdir()), [])

    def test_missing_approval_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("approval", "registry", "excerpt"):
                (root / name).write_text("{}")
            with self.assertRaises(ContractError):
                approvals(root / "approval", root / "registry", root / "excerpt", root / "site")

    def test_pinned_approval_and_omission_are_required(self) -> None:
        approval = {
            "task": "T003", "status": "approved", "review_id": "synthetic",
            "contract": {"sha256": CONTRACT_SHA256}, "results_index": {"sha256": INDEX_SHA256},
            "proposed_allowlist": {"status": "approved_by_explicit_contract_reference",
                                  "publication_authority_confirmed": True, "human_review_attested": True},
            "open_decisions": [],
            "approval": {"additional_restrictions": [], "attestations": {
                "reviewed_every_proposed_field_and_actual_values_and_category_vocabularies": True,
                "authorized_and_applicable_permissions_confirmed": True,
                "exact_numeric_values_and_small_cells_approved_after_linkage_review": True,
                "original_cohort_labels_approved_after_linkage_review": True,
                "existing_TEAM_labels_scoped_by_cohort_approved_after_linkage_review": True,
            }},
        }
        excerpt = {
            "status": "completed_omit_excerpts", "contract_sha256": CONTRACT_SHA256,
            "results_index_sha256": INDEX_SHA256, "approved_excerpts": [], "candidates_selected": [],
            "public_dataset_allowed": False, "public_view_allowed": False, "public_descriptor_allowed": False,
            "empty_placeholder_allowed": False, "private_source_text_copied": False,
        }
        registry = {
            "status": "approved", "review_id": "synthetic",
            "cohorts": [{"source": c, "public": c} for c in ("C", "D")],
            "teams": [{"source_cohort": c, "source_team": str(i), "public_cohort": c, "public_team": str(i)}
                      for c in ("C", "D") for i in range(7)],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = [root / name for name in ("approval.json", "registry.json", "excerpt.json")]
            for path, value in zip(paths, (approval, registry, excerpt)):
                path.write_bytes(json_bytes(value))
            cohorts, teams = approvals(*paths, root / "site")
            self.assertEqual(len(cohorts), 2)
            self.assertEqual(len(teams), 14)
            for position, key, value in (
                (0, "status", "pending"), (0, "open_decisions", ["unresolved"]),
                (0, "contract", {"sha256": "changed"}),
                (1, "review_id", "other"), (1, "teams", []),
                (2, "approved_excerpts", ["unreviewed"]), (2, "public_dataset_allowed", True),
                (2, "contract_sha256", "changed"),
            ):
                original = (approval, registry, excerpt)[position]
                paths[position].write_bytes(json_bytes(dict(original, **{key: value})))
                with self.subTest(key=key), self.assertRaises(ContractError):
                    approvals(*paths, root / "site")
                paths[position].write_bytes(json_bytes(original))


class JsonProjectionTests(unittest.TestCase):
    def test_empty_success_lists_are_zero_but_unavailable_is_null(self) -> None:
        teams = {("C", str(i)): ("C", str(i)) for i in range(14)}
        fields = ("goals", "architecture_or_design", "task_decomposition", "risk_or_dependency", "evidence_quotes")
        planning = [
            {"Semestre": "C", "ID_Equipe": str(i),
             "status": "success" if i < 9 else "unavailable_not_measured",
             "input_subjects": ["PRIVATE"],
             "parsed_response": dict(planning_evidence_present=False, **{k: [] for k in fields}) if i < 9 else None}
            for i in range(14)
        ]
        data = {"m6b_llm_planning_content.json": planning,
                "m5_lexicon.json": {"version": "1", "language": "test", "counting_rule": "test",
                                    "patterns": {str(i): "pattern" for i in range(5)}}}
        result = json_projections(data, {"C": "C"}, teams)
        for row in result["m6b-planning-content"]:
            self.assertNotIn("input_subjects", row)
            self.assertEqual(row["goals_n"], 0 if row["measurement_status"] == "success" else None)
            self.assertIs(row["planning_evidence_present"],
                          False if row["measurement_status"] == "success" else None)
        planning[0]["status"] = "failed"
        with self.assertRaises(ContractError):
            json_projections(data, {"C": "C"}, teams)


if __name__ == "__main__":
    unittest.main()
