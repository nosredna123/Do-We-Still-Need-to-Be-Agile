from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


MODULE_PATH = Path(__file__).parents[1] / "09_cross_evidence_narrative_reporter.py"
SPEC = importlib.util.spec_from_file_location("cross_evidence_narrative_reporter", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
REPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REPORTER)


def _write_metadata(path: Path, *, contract_version: str) -> None:
    path.with_name(f"{path.name}.metadata.json").write_text(
        json.dumps({"status": "success", "contract_version": contract_version, "input_checksum": f"checksum-{path.name}"}),
        encoding="utf-8",
    )


def test_cross_evidence_artifact_reports_generate_and_skip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    analysis_dir = tmp_path / "analysis"
    cross_evidence_dir = analysis_dir / "cross_evidence"
    cross_evidence_dir.mkdir(parents=True)
    result_dir = cross_evidence_dir / "results"
    result_dir.mkdir(parents=True)
    figure_dir = cross_evidence_dir / "figure_data"
    figure_dir.mkdir(parents=True)

    result_path = result_dir / "cross_evidence_correlations.csv"
    pd.DataFrame(
        [
            {
                "analysis_id": "scope_vs_source_churn_t3",
                "unit_of_analysis": "team_semester",
                "priority": "primary_candidate",
                "n_valid": 12,
                "coefficient": -0.61,
                "p_value": 0.02,
                "status": "success",
            }
        ]
    ).to_csv(result_path, index=False)
    _write_metadata(result_path, contract_version="cross-evidence-correlations-v1")

    figure_path = figure_dir / "scope_vs_late_instability.csv"
    pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_A", "Semestre": "2025.2", "scope_index": 0.8, "late_instability_index": 1.2},
            {"ID_Equipe": "TEAM_B", "Semestre": "2025.2", "scope_index": 1.4, "late_instability_index": 2.1},
        ]
    ).to_csv(figure_path, index=False)
    _write_metadata(figure_path, contract_version="cross-evidence-v1")

    output_dir = cross_evidence_dir / "reports" / "artifact_reports"
    calls: list[str] = []

    def fake_mock_backend(prompt: str) -> str:
        calls.append(prompt)
        return "Mock cross-evidence report body"

    monkeypatch.setattr(REPORTER, "mock_narrative_backend", fake_mock_backend)
    monkeypatch.setattr(
        "sys.argv",
        [
            "09_cross_evidence_narrative_reporter.py",
            "--analysis-dir",
            str(analysis_dir),
            "--output-dir",
            str(output_dir),
            "--backend",
            "mock",
        ],
    )

    REPORTER.main()
    assert (output_dir / "cross_evidence_correlations.md").exists()
    assert (output_dir / "scope_vs_late_instability_data.md").exists()
    assert len(calls) >= 2

    REPORTER.main()
    assert len(calls) == 2


def test_cross_evidence_report_defaults_to_cross_evidence_reports_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    analysis_dir = tmp_path / "analysis"
    cross_evidence_dir = analysis_dir / "cross_evidence"
    cross_evidence_dir.mkdir(parents=True)
    result_dir = cross_evidence_dir / "results"
    result_dir.mkdir(parents=True)

    result_path = result_dir / "cross_evidence_correlations.csv"
    pd.DataFrame([
        {
            "analysis_id": "scope_vs_source_churn_t3",
            "unit_of_analysis": "team_semester",
            "priority": "primary_candidate",
            "n_valid": 12,
            "coefficient": -0.61,
            "p_value": 0.02,
            "status": "success",
        }
    ]).to_csv(result_path, index=False)
    _write_metadata(result_path, contract_version="cross-evidence-correlations-v1")

    monkeypatch.setattr(REPORTER, "mock_narrative_backend", lambda prompt: "Mock cross-evidence report body")
    monkeypatch.setattr(
        "sys.argv",
        [
            "09_cross_evidence_narrative_reporter.py",
            "--analysis-dir",
            str(analysis_dir),
            "--backend",
            "mock",
        ],
    )

    REPORTER.main()

    expected_output = cross_evidence_dir / "reports" / "artifact_reports" / "cross_evidence_correlations.md"
    assert expected_output.exists()


def test_cross_evidence_group_and_act_reports_generate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    analysis_dir = tmp_path / "analysis"
    cross_evidence_dir = analysis_dir / "cross_evidence"
    (cross_evidence_dir / "results").mkdir(parents=True)
    (cross_evidence_dir / "datasets").mkdir(parents=True)
    (cross_evidence_dir / "figure_data").mkdir(parents=True)

    result_path = cross_evidence_dir / "results" / "cross_evidence_correlations.csv"
    pd.DataFrame([
        {
            "analysis_id": "scope_vs_source_churn_t3",
            "unit_of_analysis": "team_semester",
            "priority": "primary_candidate",
            "n_valid": 12,
            "coefficient": -0.61,
            "p_value": 0.02,
            "status": "success",
        }
    ]).to_csv(result_path, index=False)
    _write_metadata(result_path, contract_version="cross-evidence-correlations-v1")

    matrix_path = cross_evidence_dir / "results" / "evidence_priority_matrix.csv"
    pd.DataFrame([
        {
            "source_artifact": "cross_evidence_correlations",
            "analysis_id": "scope_vs_source_churn_t3",
            "priority": "primary_candidate",
            "verdict": "supports",
            "narrative_acts": "[2, 3]",
            "recommended_use": "anchor_narrative_claim",
            "publication_readiness": "candidate_primary",
            "summary": "Strong support.",
            "evidence_scope": "global_cross_evidence",
            "evidence_tier": "A",
            "stratum": "global",
            "semester": "",
            "x": "source_churn_t3",
            "y": "scope_applicability_mean_t3",
            "coefficient": -0.61,
            "p_value": 0.02,
            "robustness_class": "robust_all",
        }
    ]).to_csv(matrix_path, index=False)
    _write_metadata(matrix_path, contract_version="cross-evidence-priority-matrix-v1")

    dataset_path = cross_evidence_dir / "datasets" / "temporal_escalation_metrics.parquet"
    pd.DataFrame([
        {"team_id": "T1", "metric_id": "source_churn_t3", "value": 15.0},
        {"team_id": "T2", "metric_id": "planning_rework_signal_t2_t3", "value": 9.0},
    ]).to_parquet(dataset_path, index=False)
    _write_metadata(dataset_path, contract_version="cross-evidence-v1")

    monkeypatch.setattr(REPORTER, "mock_narrative_backend", lambda prompt: "Mock cross-evidence synthesis")
    monkeypatch.setattr(
        "sys.argv",
        [
            "09_cross_evidence_narrative_reporter.py",
            "--analysis-dir",
            str(analysis_dir),
            "--backend",
            "mock",
        ],
    )

    REPORTER.main()

    assert (cross_evidence_dir / "reports" / "group_reports" / "temporal_escalation.md").exists()
    assert (cross_evidence_dir / "reports" / "act_reports" / "act_2_planning_debt.md").exists()


def test_cross_evidence_consolidated_report_generates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    analysis_dir = tmp_path / "analysis"
    cross_evidence_dir = analysis_dir / "cross_evidence"
    (cross_evidence_dir / "results").mkdir(parents=True)
    (cross_evidence_dir / "datasets").mkdir(parents=True)
    (cross_evidence_dir / "figure_data").mkdir(parents=True)

    pd.DataFrame([
        {
            "analysis_id": "scope_vs_source_churn_t3",
            "unit_of_analysis": "team_semester",
            "priority": "primary_candidate",
            "n_valid": 12,
            "coefficient": -0.61,
            "p_value": 0.02,
            "status": "success",
        }
    ]).to_csv(cross_evidence_dir / "results" / "cross_evidence_correlations.csv", index=False)
    _write_metadata(cross_evidence_dir / "results" / "cross_evidence_correlations.csv", contract_version="cross-evidence-correlations-v1")

    pd.DataFrame([
        {
            "source_artifact": "cross_evidence_correlations",
            "analysis_id": "scope_vs_source_churn_t3",
            "priority": "primary_candidate",
            "verdict": "supports",
            "narrative_acts": "[2, 3]",
            "recommended_use": "anchor_narrative_claim",
            "publication_readiness": "candidate_primary",
            "summary": "Strong support.",
            "evidence_scope": "global_cross_evidence",
            "evidence_tier": "A",
            "stratum": "global",
            "semester": "",
            "x": "source_churn_t3",
            "y": "scope_applicability_mean_t3",
            "coefficient": -0.61,
            "p_value": 0.02,
            "robustness_class": "robust_all",
        }
    ]).to_csv(cross_evidence_dir / "results" / "evidence_priority_matrix.csv", index=False)
    _write_metadata(cross_evidence_dir / "results" / "evidence_priority_matrix.csv", contract_version="cross-evidence-priority-matrix-v1")

    monkeypatch.setattr(REPORTER, "mock_narrative_backend", lambda prompt: "Mock consolidated cross-evidence report")
    monkeypatch.setattr(
        "sys.argv",
        [
            "09_cross_evidence_narrative_reporter.py",
            "--analysis-dir",
            str(analysis_dir),
            "--backend",
            "mock",
        ],
    )

    REPORTER.main()

    assert (cross_evidence_dir / "reports" / "00_cross_evidence_consolidated_report.md").exists()
