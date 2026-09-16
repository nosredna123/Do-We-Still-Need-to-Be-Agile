from __future__ import annotations

import json
import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


MODULE_PATH = Path(__file__).parents[1] / "06_statistical_analyzer.py"
SPEC = importlib.util.spec_from_file_location("statistical_analyzer", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
STATISTICAL_ANALYZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STATISTICAL_ANALYZER)


def _write_input(
	analysis_dir: Path,
	name: str,
	frame: pd.DataFrame,
	*,
	contract_version: str,
	options: dict[str, object],
) -> None:
	path = analysis_dir / f"{name}.parquet"
	frame.to_parquet(path, index=False)
	metadata = {
		"status": "success",
		"contract_version": contract_version,
		"input_checksum": f"source-{name}",
		"options": options,
	}
	path.with_name(f"{path.name}.metadata.json").write_text(
		json.dumps(metadata), encoding="utf-8"
	)


def _write_fixture_inputs(tmp_path: Path) -> tuple[dict[str, Path], Path]:
	analysis_dir = tmp_path / "analysis"
	analysis_dir.mkdir()
	_write_input(
		analysis_dir,
		"team_metrics",
		pd.DataFrame(
			[
				{"ID_Equipe": "TEAM_A", "Semestre": "2025.2", "unit_of_analysis": "team_semester", "pi_file_count_t1": 2, "cc_total_t3": 8},
				{"ID_Equipe": "TEAM_B", "Semestre": "2025.2", "unit_of_analysis": "team_semester", "pi_file_count_t1": None, "cc_total_t3": 4},
			]
		),
		contract_version="team-metrics-v1",
		options={
			"pi_definition_version": "pi-v1",
			"cc_definition_version": "cc-v1",
			"dt_definition_version": "dt-v1",
			"ai_definition_version": "ai-v1",
		},
	)
	_write_input(
		analysis_dir,
		"cut_context_metrics",
		pd.DataFrame(
			[{"Semestre": "2025.2", "temporal_marker": "T1", "unit_of_analysis": "cut_context", "ie_student_cognitive_load_mean": 2.0}]
		),
		contract_version="cut-context-metrics-v1",
		options={"ie_definition_version": "ie-v1", "statistical_summary_version": "distribution-summary-v1"},
	)
	_write_input(
		analysis_dir,
		"student_nlp",
		pd.DataFrame(
			[{"student_response_id": "student-1", "question_id": "q1", "Semestre": "2025.2", "temporal_marker": "T1", "unit_of_analysis": "student_response", "sentiment_score": 1}]
		),
		contract_version="student-nlp-v1",
		options={},
	)
	_write_input(
		analysis_dir,
		"transcript_nlp",
		pd.DataFrame(
			[{"transcript_file": "session-1", "Semestre": "2025.2", "temporal_marker": "T1", "unit_of_analysis": "transcript_session", "rework_signal_score": 2}]
		),
		contract_version="transcript-nlp-v1",
		options={},
	)
	contract_report = analysis_dir / "phase2_contract_report.json"
	contract_report.write_text(json.dumps({"status": "success"}), encoding="utf-8")
	return (
		{name: analysis_dir / f"{name}.parquet" for name in ("team_metrics", "cut_context_metrics", "student_nlp", "transcript_nlp")},
		contract_report,
	)


def test_prepare_manifest_separates_units_and_keeps_true_keys_private(tmp_path: Path) -> None:
	input_paths, contract_report = _write_fixture_inputs(tmp_path)
	output_path = tmp_path / "manifest.json"
	exclusions_path = tmp_path / "manifest_exclusions.json"

	manifest = STATISTICAL_ANALYZER.prepare_statistical_manifest(
		input_paths, contract_report, output_path, exclusions_path
	)

	assert set(manifest["datasets"]) == {"team_metrics", "cut_context_metrics", "student_nlp", "transcript_nlp"}
	assert manifest["datasets"]["team_metrics"]["unit_of_analysis"] == "team_semester"
	assert manifest["datasets"]["cut_context_metrics"]["unit_of_analysis"] == "cut_context"
	assert manifest["datasets"]["team_metrics"]["n_unique_keys"] == 2
	assert manifest["unit_compatibility"]["cut_context"]["broadcast_allowed"] is False
	private = json.loads(exclusions_path.read_text(encoding="utf-8"))
	assert private["exclusions"]
	assert any("observation_keys" in row for row in private["exclusions"])
	assert any(
		{"ID_Equipe": "TEAM_B", "Semestre": "2025.2"} in row["observation_keys"]
		for row in private["exclusions"]
	)
	assert "TEAM_B" not in output_path.read_text(encoding="utf-8")


def test_prepare_manifest_fails_before_writing_for_invalid_sidecar(tmp_path: Path) -> None:
	input_paths, contract_report = _write_fixture_inputs(tmp_path)
	sidecar = input_paths["team_metrics"].with_name("team_metrics.parquet.metadata.json")
	sidecar.write_text(json.dumps({"status": "failed"}), encoding="utf-8")
	output_path = tmp_path / "manifest.json"
	exclusions_path = tmp_path / "manifest_exclusions.json"

	with pytest.raises(ValueError, match="not successful"):
		STATISTICAL_ANALYZER.prepare_statistical_manifest(
			input_paths, contract_report, output_path, exclusions_path
		)
	assert not output_path.exists()
	assert not exclusions_path.exists()


def test_prepare_manifest_integrates_real_persisted_artifacts(tmp_path: Path) -> None:
	project_root = Path(__file__).parents[1]
	analysis_dir = project_root / "data" / "analysis"
	input_paths = {
		name: analysis_dir / f"{name}.parquet"
		for name in ("team_metrics", "cut_context_metrics", "student_nlp", "transcript_nlp")
	}
	manifest = STATISTICAL_ANALYZER.prepare_statistical_manifest(
		input_paths,
		analysis_dir / "phase2_contract_report.json",
		tmp_path / "statistical_dataset_manifest.json",
		tmp_path / "statistical_dataset_manifest_exclusions.json",
	)

	assert manifest["status"] == "success"
	assert manifest["input_checksum"]
	assert manifest["datasets"]["team_metrics"]["n_rows"] == 14
	assert manifest["datasets"]["team_metrics"]["n_unique_keys"] == 14
	assert not any(
		variable["name"].startswith("ie_")
		for variable in manifest["datasets"]["team_metrics"]["variables"]
	)


def test_run_persisted_correlations_keeps_units_and_missingness_explicit(tmp_path: Path) -> None:
	project_root = Path(__file__).parents[1]
	analysis_dir = project_root / "data" / "analysis"
	source_manifest = analysis_dir / "statistical_dataset_manifest.json"
	manifest_path = tmp_path / "statistical_dataset_manifest.json"
	manifest_path.write_text(source_manifest.read_text(encoding="utf-8"), encoding="utf-8")
	output_path = tmp_path / "correlation_results.csv"

	results = STATISTICAL_ANALYZER.run_persisted_correlations(
		analysis_dir,
		output_path=output_path,
		manifest_path=manifest_path,
	)

	assert set(results["analysis_id"]) == {
		"pi_vs_cc_primary",
		"pi_vs_delta_dt_primary",
		"ai_vs_cc_primary",
		"context_ie_temporal_primary",
	}
	ai_row = results.loc[results["analysis_id"] == "ai_vs_cc_primary"].iloc[0]
	assert ai_row["n_total"] == 14
	assert ai_row["n_valid"] == 7
	assert ai_row["n_missing"] == 7
	assert ai_row["x_missing"] == 7
	assert ai_row["warning"] == "small_sample_n_lt_10"
	context_row = results.loc[results["analysis_id"] == "context_ie_temporal_primary"].iloc[0]
	assert context_row["unit_of_analysis"] == "cut_context"
	assert context_row["n_total"] == 6
	assert context_row["n_valid"] == 3
	assert context_row["n_missing"] == 3
	assert context_row["confidence_interval_method"] == "not_calculated_v1"
	updated = json.loads(manifest_path.read_text(encoding="utf-8"))
	assert updated["correlations"]["status"] == "success"
	assert output_path.with_name("correlation_results.csv.metadata.json").exists()


def test_run_persisted_correlations_resumes_with_stable_checksum(tmp_path: Path) -> None:
	project_root = Path(__file__).parents[1]
	analysis_dir = project_root / "data" / "analysis"
	manifest_path = tmp_path / "statistical_dataset_manifest.json"
	manifest_path.write_text(
		(analysis_dir / "statistical_dataset_manifest.json").read_text(encoding="utf-8"),
		encoding="utf-8",
	)
	output_path = tmp_path / "correlation_results.csv"
	first = STATISTICAL_ANALYZER.run_persisted_correlations(
		analysis_dir, output_path=output_path, manifest_path=manifest_path
	)
	second = STATISTICAL_ANALYZER.run_persisted_correlations(
		analysis_dir, output_path=output_path, manifest_path=manifest_path
	)

	assert list(first.columns) == list(second.columns)
	for column in first.columns:
		if pd.api.types.is_numeric_dtype(first[column]):
			assert np.allclose(
				first[column].fillna(-999).to_numpy(),
				second[column].fillna(-999).to_numpy(),
			)
		else:
			assert first[column].fillna("").astype(str).tolist() == second[column].fillna("").astype(str).tolist()


def test_run_persisted_hypotheses_uses_median_groups_and_explicit_unavailability(tmp_path: Path) -> None:
	project_root = Path(__file__).parents[1]
	analysis_dir = project_root / "data" / "analysis"
	manifest_path = tmp_path / "statistical_dataset_manifest.json"
	manifest_path.write_text(
		(analysis_dir / "statistical_dataset_manifest.json").read_text(encoding="utf-8"),
		encoding="utf-8",
	)
	output_path = tmp_path / "hypothesis_results.csv"

	results = STATISTICAL_ANALYZER.run_persisted_hypotheses(
		analysis_dir,
		output_path=output_path,
		manifest_path=manifest_path,
	)

	assert set(results["analysis_id"]) == {
		"pi_high_vs_low_cc_primary",
		"ai_high_vs_low_cc_primary",
		"context_ie_high_vs_low_rework_primary",
	}
	pi_row = results.loc[results["analysis_id"] == "pi_high_vs_low_cc_primary"].iloc[0]
	assert pi_row["split_rule"] == "median_low_le_high_gt"
	assert pi_row["n_group_low"] == 7
	assert pi_row["n_group_high"] == 7
	assert pi_row["status"] == "success"
	ai_row = results.loc[results["analysis_id"] == "ai_high_vs_low_cc_primary"].iloc[0]
	assert ai_row["status"] == "success"
	assert ai_row["n_group_low"] == 4
	assert ai_row["n_group_high"] == 3
	context_row = results.loc[results["analysis_id"] == "context_ie_high_vs_low_rework_primary"].iloc[0]
	assert context_row["unit_of_analysis"] == "cut_context"
	assert context_row["status"] == "unavailable"
	assert context_row["reason"] == "insufficient_group_n"
	updated = json.loads(manifest_path.read_text(encoding="utf-8"))
	assert updated["hypotheses"]["status"] == "success"
	assert output_path.with_name("hypothesis_results.csv.metadata.json").exists()


def test_run_persisted_hypotheses_rejects_zero_variance_groups(tmp_path: Path) -> None:
	analysis_dir = tmp_path / "analysis"
	analysis_dir.mkdir()
	team = pd.DataFrame(
		[
			{"ID_Equipe": "A", "Semestre": "S", "unit_of_analysis": "team_semester", "group": 0, "outcome": 1},
			{"ID_Equipe": "B", "Semestre": "S", "unit_of_analysis": "team_semester", "group": 0, "outcome": 1},
			{"ID_Equipe": "C", "Semestre": "S", "unit_of_analysis": "team_semester", "group": 1, "outcome": 1},
			{"ID_Equipe": "D", "Semestre": "S", "unit_of_analysis": "team_semester", "group": 1, "outcome": 1},
			{"ID_Equipe": "E", "Semestre": "S", "unit_of_analysis": "team_semester", "group": 2, "outcome": 1},
			{"ID_Equipe": "F", "Semestre": "S", "unit_of_analysis": "team_semester", "group": 2, "outcome": 2},
			{"ID_Equipe": "G", "Semestre": "S", "unit_of_analysis": "team_semester", "group": 3, "outcome": 3},
			{"ID_Equipe": "H", "Semestre": "S", "unit_of_analysis": "team_semester", "group": 3, "outcome": 4},
		]
	)
	_write_input(analysis_dir, "team_metrics", team, contract_version="team-metrics-v1", options={})
	context = pd.DataFrame(
		[{"Semestre": "S", "temporal_marker": "T1", "unit_of_analysis": "cut_context", "context_group": 1, "context_outcome": 1}]
	)
	_write_input(analysis_dir, "cut_context_metrics", context, contract_version="cut-context-metrics-v1", options={})
	contract_report = analysis_dir / "phase2_contract_report.json"
	contract_report.write_text(json.dumps({"status": "success"}), encoding="utf-8")
	manifest_path = analysis_dir / "statistical_dataset_manifest.json"
	manifest_path.write_text(json.dumps({"status": "success", "input_checksum": "fixture"}), encoding="utf-8")

	original_registry = STATISTICAL_ANALYZER.HYPOTHESIS_TEST_REGISTRY.copy()
	STATISTICAL_ANALYZER.HYPOTHESIS_TEST_REGISTRY.clear()
	STATISTICAL_ANALYZER.HYPOTHESIS_TEST_REGISTRY["fixture_zero_variance"] = {
		"unit_of_analysis": "team_semester",
		"group_variable": "group",
		"outcome_variable": "outcome",
		"test": "mann_whitney_u",
		"priority": "primary",
		"split_rule": "median_low_le_high_gt",
	}
	try:
		results = STATISTICAL_ANALYZER.run_persisted_hypotheses(
			analysis_dir,
			output_path=tmp_path / "hypothesis_results.csv",
			manifest_path=manifest_path,
		)
	finally:
		STATISTICAL_ANALYZER.HYPOTHESIS_TEST_REGISTRY.clear()
		STATISTICAL_ANALYZER.HYPOTHESIS_TEST_REGISTRY.update(original_registry)
	assert results.loc[0, "status"] == "unavailable"
	assert results.loc[0, "reason"] == "zero_variance"
