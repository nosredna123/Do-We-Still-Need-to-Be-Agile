from __future__ import annotations

import json
from pathlib import Path

from paper_v9.scripts.results.build_results_summary import build_summary


def test_results_summary_resolves_all_metric_artifacts() -> None:
    summary = build_summary()
    assert summary["status"] == "success"
    assert set(summary["metrics"]) == {"M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"}
    assert all(record["bytes"] > 0 for metric in summary["metrics"].values() for record in metric["artifacts"])
    assert summary["key_summaries"]["M7"]["daily_windows"] == 994
    assert summary["key_summaries"]["M8"]["baseline_eligible_n"] == 12


def test_results_summary_includes_governed_robustness_artifacts() -> None:
    summary = build_summary()
    robustness = summary["robustness_artifacts"]
    assert robustness["source_of_truth"] == "paper_v9/ARTIFACT_USAGE_CATALOG.md"
    assert robustness["inventory"] == "paper_v9/FIGURES_CANDIDATES_WORKSHOP.md"
    assert set(robustness["families"]) == {
        "rq2_score_delta_vs_final7_concentration",
        "rq2_planning_concentration_quadrants",
        "rq2_nonoverlapping_phase_activity",
        "rq2_m5_2025_triangulation",
        "rq2_operational_regularity",
        "rq3_complexity_profile",
        "rq3_influence_map",
        "team_semester_evidence_panel",
        "rq2_student_syndrome_reviewer_response",
        "candidate_figure_inventory",
    }
    assert robustness["families"]["team_semester_evidence_panel"]["status"] == "appendix"
    assert robustness["families"]["rq2_student_syndrome_reviewer_response"]["status"] == "response_letter"
    assert all(
        record["bytes"] > 0
        for family in robustness["families"].values()
        for record in family["artifacts"]
    )


def test_results_summary_file_is_valid_json() -> None:
    path = Path("paper_v9/data/results/results_summary.json")
    assert path.is_file()
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == "success"