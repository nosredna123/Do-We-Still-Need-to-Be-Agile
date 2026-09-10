from __future__ import annotations

import json
import importlib.util
from pathlib import Path

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
