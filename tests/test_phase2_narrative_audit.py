from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


MODULE_PATH = Path(__file__).parents[1] / "07_artifact_narrative_reporter.py"
SPEC = importlib.util.spec_from_file_location("artifact_narrative_reporter", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
REPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORTER)


def _write_parquet(analysis_dir: Path, name: str, frame: pd.DataFrame, *, contract_version: str) -> Path:
    path = analysis_dir / f"{name}.parquet"
    frame.to_parquet(path, index=False)
    metadata = {"status": "success", "contract_version": contract_version, "input_checksum": f"source-{name}"}
    path.with_name(f"{path.name}.metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return path


def _write_csv(analysis_dir: Path, name: str, frame: pd.DataFrame, *, contract_version: str) -> Path:
    path = analysis_dir / f"{name}.csv"
    frame.to_csv(path, index=False)
    metadata = {"status": "success", "contract_version": contract_version, "input_checksum": f"source-{name}"}
    path.with_name(f"{path.name}.metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    return path


def _dataset_manifest_entry(unit_of_analysis: str, key: list[str], n_rows: int) -> dict[str, object]:
    return {
        "unit_of_analysis": unit_of_analysis,
        "observation_key": key,
        "n_rows": n_rows,
        "n_unique_keys": n_rows,
        "coverage": {"Semestre": ["2025.2"]},
        "variables": [{"name": "pi_file_count_t1", "dtype": "float64", "n_total": n_rows, "n_missing": 0}],
    }


def _build_fixture(tmp_path: Path, *, correlation_p_values: list[float | None], statuses: list[str]) -> Path:
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()

    team_metrics = pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_A", "Semestre": "2025.2", "pi_file_count_t1": 2, "cc_per_source_loc_t3": 0.1},
            {"ID_Equipe": "TEAM_B", "Semestre": "2025.2", "pi_file_count_t1": 5, "cc_per_source_loc_t3": 0.2},
        ]
    )
    _write_parquet(analysis_dir, "team_metrics", team_metrics, contract_version="team-metrics-v1")
    _write_parquet(
        analysis_dir,
        "cut_context_metrics",
        pd.DataFrame([{"Semestre": "2025.2", "temporal_marker": "T1", "ie_transcript_rework_signal_score_mean": 1.0}]),
        contract_version="cut-context-metrics-v1",
    )
    _write_parquet(
        analysis_dir,
        "student_nlp",
        pd.DataFrame([{"student_response_id": "s1", "sentiment_score": 1}]),
        contract_version="student-nlp-v1",
    )
    _write_parquet(
        analysis_dir,
        "transcript_nlp",
        pd.DataFrame([{"transcript_file": "t1.json", "coordination_friction_score": 1}]),
        contract_version="transcript-nlp-v1",
    )
    _write_parquet(
        analysis_dir,
        "textual_cut_signals",
        pd.DataFrame([{"Semestre": "2025.2", "temporal_marker": "T1", "student_n": 3}]),
        contract_version="textual-cut-signals-v2",
    )
    _write_parquet(
        analysis_dir,
        "planning_metrics",
        pd.DataFrame([{"ID_Equipe": "TEAM_A", "Semestre": "2025.2", "pi_file_count_t1": 2}]),
        contract_version="planning-metrics-v1",
    )
    _write_parquet(
        analysis_dir,
        "code_churn_metrics",
        pd.DataFrame([{"ID_Equipe": "TEAM_A", "Semestre": "2025.2", "cc_total_t3": 8}]),
        contract_version="code-churn-metrics-v1",
    )
    _write_parquet(
        analysis_dir,
        "technical_degradation_metrics",
        pd.DataFrame([{"ID_Equipe": "TEAM_A", "Semestre": "2025.2", "delta_dt_t1_t3": 1.0}]),
        contract_version="technical-degradation-metrics-v1",
    )
    _write_parquet(
        analysis_dir,
        "integration_friction_metrics",
        pd.DataFrame([{"ID_Equipe": "TEAM_A", "Semestre": "2025.2", "ai_max_author_share_before_t3_window": 0.5}]),
        contract_version="integration-friction-metrics-v1",
    )

    (analysis_dir / "team_metrics_exclusions.json").write_text(
        json.dumps({"contract_version": "team-metrics-exclusions-v1", "sources": {}}), encoding="utf-8"
    )
    (analysis_dir / "statistical_dataset_manifest_exclusions.json").write_text(
        json.dumps({"contract_version": "statistical-dataset-manifest-exclusions-v1", "exclusions": []}),
        encoding="utf-8",
    )

    analysis_ids = ["pi_vs_cc_primary", "pi_vs_delta_dt_primary", "ai_vs_cc_primary", "context_ie_temporal_primary"]
    correlation_rows = []
    for analysis_id, p_value, status in zip(analysis_ids, correlation_p_values, statuses):
        correlation_rows.append(
            {
                "analysis_id": analysis_id,
                "unit_of_analysis": "team_semester",
                "priority": "primary",
                "n_valid": 14,
                "coefficient": 0.1,
                "p_value": p_value,
                "status": status,
            }
        )
    _write_csv(analysis_dir, "correlation_results", pd.DataFrame(correlation_rows), contract_version="spearman-correlation-results-v1")

    hypothesis_rows = [
        {
            "analysis_id": "pi_high_vs_low_cc_primary",
            "unit_of_analysis": "team_semester",
            "priority": "primary",
            "n_valid": 14,
            "u_statistic": 21.0,
            "p_value": 0.71,
            "status": "success",
        },
        {
            "analysis_id": "ai_high_vs_low_cc_primary",
            "unit_of_analysis": "team_semester",
            "priority": "primary",
            "n_valid": 7,
            "u_statistic": 6.0,
            "p_value": 1.0,
            "status": "success",
        },
        {
            "analysis_id": "context_ie_high_vs_low_rework_primary",
            "unit_of_analysis": "cut_context",
            "priority": "primary",
            "n_valid": 3,
            "u_statistic": None,
            "p_value": None,
            "status": "unavailable",
        },
    ]
    _write_csv(analysis_dir, "hypothesis_results", pd.DataFrame(hypothesis_rows), contract_version="mann-whitney-hypothesis-results-v1")

    statistical_manifest = {
        "contract_version": "statistical-dataset-manifest-v1",
        "status": "success",
        "datasets": {
            "team_metrics": _dataset_manifest_entry("team_semester", ["ID_Equipe", "Semestre"], 2),
            "cut_context_metrics": _dataset_manifest_entry("cut_context", ["Semestre", "temporal_marker"], 1),
            "student_nlp": _dataset_manifest_entry("student_response", ["student_response_id"], 1),
            "transcript_nlp": _dataset_manifest_entry("transcript_session", ["transcript_file"], 1),
        },
        "correlations": {"status": "success"},
        "hypotheses": {"status": "success"},
    }
    (analysis_dir / "statistical_dataset_manifest.json").write_text(json.dumps(statistical_manifest), encoding="utf-8")

    contract_report = {
        "contract_version": "phase2-inputs-v1",
        "status": "success",
        "contracts": {
            "student_responses": {"counts_by_semester_and_cut": [{"Semestre": "2025.2", "rows": 9}]},
        },
    }
    (analysis_dir / "phase2_contract_report.json").write_text(json.dumps(contract_report), encoding="utf-8")

    def _figure(figure_id: str, source: str) -> dict[str, object]:
        return {
            "figure_id": figure_id,
            "status": "success",
            "category": "prioritarias",
            "source": source,
            "unit_of_analysis": "team_semester",
            "variables": ["pi_file_count_t1"],
            "n_total": 14,
            "n_valid": 14,
            "n_missing": 0,
            "limitations": ["observational association; n=14"],
            "transformations": [],
            "scale_notes": [],
            "interactive_path": f"assets/figures/prioritarias/{figure_id}.html",
        }

    figure_manifest = {
        "status": "success",
        "figures": [
            _figure("pi_vs_cc", "team_metrics.parquet"),
            _figure("cc_by_temporal_cut", "team_metrics.parquet"),
            _figure("delta_dt_by_team_semester", "team_metrics.parquet"),
            _figure("ai_before_t3", "team_metrics.parquet"),
            _figure("ie_by_cut_or_corpus", "cut_context_metrics.parquet"),
        ]
    }
    (analysis_dir / "figure_manifest.json").write_text(json.dumps(figure_manifest), encoding="utf-8")

    return analysis_dir


def test_missing_artifact_fails_fast(tmp_path: Path) -> None:
    analysis_dir = _build_fixture(
        tmp_path,
        correlation_p_values=[0.98, 0.96, 0.64, None],
        statuses=["success", "success", "success", "unavailable"],
    )
    (analysis_dir / "team_metrics.parquet").unlink()
    with pytest.raises(FileNotFoundError):
        REPORTER._require_success_sidecar(analysis_dir / "team_metrics.parquet")


def test_stale_sidecar_triggers_regeneration(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    analysis_dir = _build_fixture(
        tmp_path,
        correlation_p_values=[0.98, 0.96, 0.64, None],
        statuses=["success", "success", "success", "unavailable"],
    )
    output_dir = analysis_dir / "artifact_reports"
    calls = {"count": 0}

    def fake_mock_backend(prompt: str) -> str:
        calls["count"] += 1
        return f"Mock report body #{calls['count']}"

    monkeypatch.setattr(REPORTER, "mock_narrative_backend", fake_mock_backend)
    monkeypatch.setattr(
        "sys.argv",
        ["07_artifact_narrative_reporter.py", "--analysis-dir", str(analysis_dir), "--output-dir", str(output_dir), "--backend", "mock"],
    )
    REPORTER.main()
    first_call_count = calls["count"]
    assert first_call_count > 0
    report_path = output_dir / "team_metrics.md"
    assert report_path.exists()

    # Second run with unchanged inputs must not call the backend again.
    REPORTER.main()
    assert calls["count"] == first_call_count

    # Editing the underlying artifact invalidates only its own report.
    team_metrics_path = analysis_dir / "team_metrics.parquet"
    frame = pd.read_parquet(team_metrics_path)
    frame.loc[0, "pi_file_count_t1"] = 99
    frame.to_parquet(team_metrics_path, index=False)
    REPORTER.main()
    assert calls["count"] > first_call_count


def test_verdict_reflects_injected_significance_and_n() -> None:
    correlation_rows = {
        "pi_vs_cc_primary": {"priority": "primary", "status": "success", "p_value": 0.98},
        "pi_vs_delta_dt_primary": {"priority": "primary", "status": "success", "p_value": 0.96},
        "ai_vs_cc_primary": {"priority": "primary", "status": "success", "p_value": 0.64},
        "context_ie_temporal_primary": {"priority": "primary", "status": "unavailable", "p_value": None},
    }
    hypothesis_rows = {
        "pi_high_vs_low_cc_primary": {"priority": "primary", "status": "success", "p_value": 0.71},
        "ai_high_vs_low_cc_primary": {"priority": "primary", "status": "success", "p_value": 1.0},
        "context_ie_high_vs_low_rework_primary": {"priority": "primary", "status": "unavailable", "p_value": None},
    }
    verdict = REPORTER.compute_consolidated_verdict(correlation_rows, hypothesis_rows, team_semester_n=14)
    assert verdict["verdict"] == "conditional-go"
    assert verdict["verdict_reason"] == "no_significant_result_and_small_sample_reframe_as_exploratory"
    assert verdict["count_supports"] == 0
    assert verdict["count_tested"] == 5

    significant_rows = dict(correlation_rows)
    significant_rows["pi_vs_cc_primary"] = {"priority": "primary", "status": "success", "p_value": 0.01}
    verdict_significant_small_n = REPORTER.compute_consolidated_verdict(significant_rows, hypothesis_rows, team_semester_n=14)
    assert verdict_significant_small_n["verdict"] == "conditional-go"
    assert verdict_significant_small_n["verdict_reason"] == "significant_result_but_small_sample"

    verdict_significant_large_n = REPORTER.compute_consolidated_verdict(significant_rows, hypothesis_rows, team_semester_n=40)
    assert verdict_significant_large_n["verdict"] == "go"


def test_no_private_fields_reach_fact_sheet(tmp_path: Path) -> None:
    analysis_dir = _build_fixture(
        tmp_path,
        correlation_p_values=[0.98, 0.96, 0.64, None],
        statuses=["success", "success", "success", "unavailable"],
    )
    statistical_manifest = json.loads((analysis_dir / "statistical_dataset_manifest.json").read_text(encoding="utf-8"))
    figure_manifest = json.loads((analysis_dir / "figure_manifest.json").read_text(encoding="utf-8"))
    correlation_rows = REPORTER._load_analysis_rows(analysis_dir / "correlation_results.csv")
    hypothesis_rows = REPORTER._load_analysis_rows(analysis_dir / "hypothesis_results.csv")

    forbidden_fields = {"answer_text", "evidence_summary_private", "transcript_text"}
    from pipeline_config import ARTIFACT_NARRATIVE_REGISTRY

    for artifact_id, entry in ARTIFACT_NARRATIVE_REGISTRY.items():
        fact_sheet = REPORTER.build_fact_sheet(
            artifact_id,
            entry,
            analysis_dir=analysis_dir,
            statistical_manifest=statistical_manifest,
            figure_manifest=figure_manifest,
            correlation_rows=correlation_rows,
            hypothesis_rows=hypothesis_rows,
        )
        serialized = json.dumps(fact_sheet, default=str)
        for field in forbidden_fields:
            assert field not in serialized


def test_cross_evidence_prompts_are_versioned_and_private_safe() -> None:
    from pipeline_prompts import (
        CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT,
        CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT_VERSION,
        CROSS_EVIDENCE_ARTIFACT_REPORT_SYSTEM_PROMPT,
        CROSS_EVIDENCE_ACT_REPORT_PROMPT,
        CROSS_EVIDENCE_ACT_REPORT_PROMPT_VERSION,
        CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT,
        CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT_VERSION,
        CROSS_EVIDENCE_GROUP_REPORT_PROMPT,
        CROSS_EVIDENCE_GROUP_REPORT_PROMPT_VERSION,
    )

    required_versions = {
        CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT_VERSION: "cross-evidence-artifact-report-v1",
        CROSS_EVIDENCE_GROUP_REPORT_PROMPT_VERSION: "cross-evidence-group-report-v1",
        CROSS_EVIDENCE_ACT_REPORT_PROMPT_VERSION: "cross-evidence-act-report-v1",
        CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT_VERSION: "cross-evidence-consolidated-report-v1",
    }
    assert required_versions

    forbidden_fields = {"answer_text", "evidence_summary_private", "transcript_text", "raw_text"}
    for prompt_text in (
        CROSS_EVIDENCE_ARTIFACT_REPORT_SYSTEM_PROMPT,
        CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT,
        CROSS_EVIDENCE_GROUP_REPORT_PROMPT,
        CROSS_EVIDENCE_ACT_REPORT_PROMPT,
        CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT,
    ):
        assert isinstance(prompt_text, str)
        for field in forbidden_fields:
            assert field not in prompt_text
