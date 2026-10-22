"""Catalog structure and scientific-grain regression checks (no private fixtures)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from build_catalog import build_catalog, validate_catalog
from prepare_snapshot import ContractError, json_bytes
from snapshot_contracts import RENAMES, TABLES


class CatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = build_catalog()
        self.datasets = {row["id"]: row for row in self.catalog["datasets"]}

    def test_saved_catalog_is_deterministic(self) -> None:
        saved = Path(__file__).resolve().parent.parent / "data/catalog.json"
        self.assertEqual(saved.read_bytes(), json_bytes(self.catalog))
        validate_catalog(self.catalog)

    def test_complete_explicit_projections(self) -> None:
        self.assertEqual(len(self.datasets), 49)
        for spec in TABLES:
            if spec.definition:
                continue
            expected = {target for _, target in spec.fields}
            if "clean_rework_ratio_t3" in expected:
                expected |= {"baseline_eligible_for_rework_t3", "ratio_status"}
            descriptor = self.datasets[spec.dataset_id]
            self.assertEqual({c["id"] for c in descriptor["columns"]}, expected, spec.dataset_id)
            self.assertEqual(descriptor["key"], [RENAMES.get(k, k) for k in spec.keys])
        for descriptor in self.datasets.values():
            self.assertTrue(descriptor["definition"])
            self.assertTrue(descriptor["denominator"])
            self.assertTrue(descriptor["limitations"])
            for column in descriptor["columns"]:
                self.assertTrue(column["label"])
                self.assertTrue(column["definition"])
                self.assertTrue(column["unit"])
                self.assertIn(column["type"], ("string", "integer", "number", "boolean"))

    def test_survey_and_transcript_have_no_team_filters(self) -> None:
        for descriptor in self.datasets.values():
            if descriptor["source"] in ("surveys", "transcript-aggregates"):
                self.assertNotIn("team_id", descriptor["key"])
                self.assertFalse(any("team_id" in f["fields"] for f in descriptor["filters"]))
        for dataset_id in ("m5-marker-density", "m5-marker-composition", "m5-corpus-coverage"):
            self.assertFalse(any("cohort" in f["fields"] for f in self.datasets[dataset_id]["filters"]))
            self.assertEqual(self.datasets[dataset_id]["coverage"]["cohorts"], ["2025.2"])

    def test_team_selection_uses_composite_identity(self) -> None:
        for descriptor in self.datasets.values():
            for selection in descriptor["filters"]:
                if "team_id" in selection["fields"]:
                    self.assertEqual(selection["fields"], ["cohort", "team_id"])
                if "omitted_team_id" in selection["fields"]:
                    self.assertEqual(selection["fields"], ["omitted_cohort", "omitted_team_id"])

    def test_missingness_and_fixed_populations(self) -> None:
        for dataset_id in ("m8-rework-magnitude", "complexity-profile", "complexity-rework-figure"):
            descriptor = self.datasets[dataset_id]
            ratio = next(c for c in descriptor["columns"] if c["id"] == "clean_rework_ratio_t3")
            self.assertTrue(ratio["nullable"])
            self.assertEqual(descriptor["missingness"]["ratio_status"],
                             ["available", "baseline_not_observed", "zero_clean_churn"])
        for dataset_id in ("m3-rolling-pooled", "m4-checkpoint-pooled", "influence-cases",
                           "complexity-stratified-associations", "m9-structural-outcomes"):
            self.assertEqual(self.datasets[dataset_id]["filter_effect"], "select_rows_only")
        self.assertIn("14 days", self.datasets["m3-participation"]["definition"])
        self.assertIn("before T3", self.datasets["planning-final7-commits"]["definition"])
        tri = self.datasets["transcript-context-2025"]
        for field in ("median_clean_rework_churn_t3", "median_clean_rework_ratio_t3_baseline_eligible"):
            self.assertEqual(next(c for c in tri["columns"] if c["id"] == field)["time_scope"], "fixed_T3")

    def test_figures_relationships_and_no_excerpts(self) -> None:
        self.assertEqual(len(self.catalog["figures"]), 7)
        panel = next(f for f in self.catalog["figures"] if f["id"] == "rq2-churn-and-lexical-density")
        self.assertEqual([p["dataset"] for p in panel["panels"]], ["m4-checkpoint-pooled", "m5-marker-density"])
        for figure in self.catalog["figures"]:
            for panel in figure["panels"]:
                columns = {c["id"] for c in self.datasets[panel["dataset"]]["columns"]}
                self.assertTrue(set(panel["fields"]) <= columns)
        self.assertEqual(self.catalog["excerpt_policy"], "omitted_by_human_decision")
        self.assertFalse(any("excerpt" in key for key in self.datasets))
        self.assertEqual(self.catalog["relationships"]["arbitrary_joins"], False)

    def test_catalog_contains_no_private_lineage_or_observations(self) -> None:
        content = json.dumps(self.catalog)
        for forbidden in ("/home/", "paper_v9", "sha256", "github.com", "parsed_response",
                          "raw_response", "input_subjects", "source_path", "reviewer"):
            self.assertNotIn(forbidden, content)
        for descriptor in self.datasets.values():
            self.assertNotIn("rows", descriptor)
            self.assertTrue(descriptor["paths"]["json"].startswith("data/datasets/"))

    def test_figure_series_and_axes_match_the_paper(self) -> None:
        figures = {f["id"]: f for f in self.catalog["figures"]}
        activity = figures["rq2-pooled-activity"]["panels"][0]
        self.assertEqual(activity["y"], "total_commit_n")
        perceptions = figures["rq1-perceptions"]["panels"][0]
        self.assertEqual(perceptions["facet"], "cohort")
        self.assertEqual(perceptions["color"], "perception_family")
        self.assertEqual(perceptions["y_range"], [0, 5])
        self.assertEqual(perceptions["score_range"], [0, 4])

    def test_embedded_definition_sets_and_frozen_thresholds(self) -> None:
        methods = self.catalog["methods"]
        sets = {s["id"]: s for s in methods["definition_sets"]}
        self.assertEqual(set(sets), {"weekly-bin-definitions", "complexity-definitions"})
        for definition in sets.values():
            self.assertEqual(len(definition["rows"]), 13)
            self.assertTrue(all("team_id" not in row and "source" not in row for row in definition["rows"]))
        bins = sets["weekly-bin-definitions"]["rows"]
        self.assertEqual(bins[0]["start_day_relative_to_t3"], -91)
        self.assertEqual(bins[-1]["end_day_relative_to_t3"], 0)
        self.assertEqual(bins[-1]["week_bin"], "final_7_days")
        self.assertTrue(all(not b["rolling_window_used"] for b in bins))
        self.assertEqual(methods["planning_high_tier"]["log_scope_minimum_inclusive"], 1.791759469228055)
        self.assertEqual(methods["score_trajectory"]["positive_delta_rule"], "> 0.125")
        self.assertEqual(methods["complexity_strata"]["median"], 1.875)

    def test_broken_catalog_rejected(self) -> None:
        for mutation in ("filter", "figure", "columns", "duplicate", "path", "unsupported_filter"):
            catalog = copy.deepcopy(self.catalog)
            if mutation == "filter":
                catalog["datasets"][0]["filters"][0]["fields"] = ["unknown"]
            elif mutation == "figure":
                catalog["figures"][0]["panels"][0]["fields"] = ["unknown"]
            elif mutation == "columns":
                catalog["datasets"][0]["columns"].pop()
            elif mutation == "duplicate":
                catalog["datasets"].append(catalog["datasets"][0])
            elif mutation == "path":
                catalog["datasets"][0]["paths"]["json"] = "../private.json"
            else:
                catalog["datasets"][0]["filters"].append(
                    {"id": "response_n", "label": "Responses", "fields": ["response_n"], "mode": "multi_select"})
            with self.subTest(mutation=mutation), self.assertRaises(ContractError):
                validate_catalog(catalog)


if __name__ == "__main__":
    unittest.main()
