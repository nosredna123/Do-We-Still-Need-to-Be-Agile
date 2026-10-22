"""Build the traceable Paper V9 results catalog from approved metric artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import (
    resolve_figures_dir,
    resolve_metrics_dir,
    resolve_paper_v9_dir,
    resolve_results_dir,
)
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "results-summary-v1"

METRIC_FILES: dict[str, list[str]] = {
    "M1": ["m1_rq1_perception_panel_long.csv", "m1_rq1_perception_panel_wide.csv", "m1_rq1_usage_frequency.csv", "m1_rq1_usage_tasks.csv", "m1_rq1_usage_tools.csv", "m1_rq1_prior_ai_project_experience.csv", "m1_rq1_autonomy_tool_balance.csv", "m1_rq1_career_impact_topics_exploratory.csv", "m1_rq1_perception_distribution.csv", "m1_rq1_perception_panel.metadata.json"],
    "M2": ["m2_role_perception_distributions.csv", "m2_role_perception_by_team_semester.csv", "m2_role_perception_paired_t1_t3.csv", "m2_role_perception.metadata.json"],
    "M3": ["m3_author_activity_participation.csv", "m3_author_concentration.csv", "m3_activity_rolling_7day.csv", "m3_activity_rolling_7day_pooled.csv", "m3_author_activity_dynamics.metadata.json"],
    "M4": ["m4_churn_magnitude.csv", "m4_commit_intensity.csv", "m4_artifact_composition.csv", "m4_rolling_7day_trajectory.csv", "m4_churn_magnitude_pooled.csv", "m4_commit_intensity_pooled.csv", "m4_artifact_composition_pooled.csv", "m4_rolling_7day_trajectory_pooled.csv", "m4_clean_change_dynamics.metadata.json"],
    "M5": ["m5_marker_density.csv", "m5_marker_composition.csv", "m5_corpus_coverage.csv", "m5_evidence_audit_trail.csv", "m5_lexicon.json", "m5_coordination_evidence.metadata.json"],
    "M6": ["m6a_structural_planning.csv", "m6_structural_planning.metadata.json", "m6b_llm_planning_content.json", "m6_llm_planning_content.metadata.json", "m6b_llm_planning_sample_for_review.md"],
    "M7": ["m7_inactivity_trajectory.csv", "m7_inactivity_pattern.csv", "m7_checkpoint_inactivity.csv", "m7_repository_inactivity.metadata.json"],
    "M8": ["m8_rework_magnitude.csv", "m8_rework_participation.csv", "m8_rework_trajectory.csv", "m8_baseline_eligibility.csv", "m8_clean_rework.metadata.json"],
    "M9": ["m9_planning_vs_rework_m6a_m8a.csv", "m9_planning_vs_rework_m6a_m8b_eligible_stratum.csv", "m9_planning_vs_outcomes_m6a_t3.csv", "m9_planning_vs_outcomes_m6b_t3_if_approved.csv", "m9_leave_one_out_intervals.csv", "m9_structured_associations.metadata.json"],
}

ROBUSTNESS_ARTIFACT_FAMILIES: dict[str, dict[str, Any]] = {
    "rq2_score_delta_vs_final7_concentration": {
        "status": "main_text",
        "section_target": "Results/RQ2",
        "patterns": ["rq2_score_delta_vs_final7_*", "rq2_score_delta_final7_quadrants.csv"],
    },
    "rq2_planning_concentration_quadrants": {
        "status": "main_text",
        "section_target": "Results/RQ2",
        "patterns": ["rq2_planning_*"],
    },
    "rq2_nonoverlapping_phase_activity": {
        "status": "main_text",
        "section_target": "Results/RQ2 or Threats",
        "patterns": ["rq2_phase_*", "rq2_nonoverlapping_phase_activity.metadata.json", "rq2_nonoverlapping_weekly_activity_overview.*"],
    },
    "rq2_m5_2025_triangulation": {
        "status": "main_text",
        "section_target": "Results/RQ2 or Threats",
        "patterns": ["rq2_m5_2025_triangulation*"],
    },
    "rq2_operational_regularity": {
        "status": "main_text_or_appendix",
        "section_target": "Results/RQ2, Discussion, or Threats",
        "patterns": ["rq2_operational_regularity*", "rq2_regularity_*"],
    },
    "rq3_complexity_profile": {
        "status": "main_text",
        "section_target": "Discussion/Threats",
        "patterns": ["rq3_complexity*", "rq3_technical_complexity*", "rq3_planning_rework_complexity_overlay*", "rq3_directional_robustness_summary.csv"],
    },
    "rq3_influence_map": {
        "status": "main_text",
        "section_target": "Threats or Results/RQ3",
        "patterns": ["rq3_influence*"],
    },
    "team_semester_evidence_panel": {
        "status": "appendix",
        "section_target": "Appendix/Supplement",
        "patterns": ["team_semester_evidence_panel*"],
    },
    "rq2_student_syndrome_reviewer_response": {
        "status": "response_letter",
        "section_target": "Response letter",
        "patterns": ["rq2_student_syndrome*"],
    },
    "candidate_figure_inventory": {
        "status": "diagnostic_only",
        "section_target": "Internal diagnostic inventory",
        "patterns": ["candidate_*"],
    },
}


def _atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def _artifact_record(path: Path, root: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required results artifact is missing: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"Required results artifact is empty: {path}")
    record: dict[str, Any] = {
        "path": path.relative_to(root).as_posix(),
        "sha256": compute_sha256(path),
        "bytes": path.stat().st_size,
        "format": path.suffix.lstrip(".") or "text",
    }
    if path.suffix == ".csv":
        frame = pd.read_csv(path)
        record["rows"] = int(len(frame))
        record["columns"] = list(frame.columns)
    elif path.suffix == ".json":
        json.loads(path.read_text(encoding="utf-8"))
    return record


def _artifact_records_for_patterns(directory: Path, patterns: list[str], root: Path) -> list[dict[str, Any]]:
    paths: dict[Path, None] = {}
    for pattern in patterns:
        for path in sorted(directory.glob(pattern)):
            if path.is_file():
                paths[path] = None
    if not paths:
        raise FileNotFoundError(f"No robustness artifacts matched patterns {patterns} in {directory}")
    return [_artifact_record(path, root) for path in sorted(paths)]


def _metadata(metric: str, metrics_dir: Path) -> dict[str, Any]:
    candidates = sorted(metrics_dir.glob(f"{metric.lower()}*.metadata.json"))
    if metric == "M6":
        candidates = [metrics_dir / "m6_structural_planning.metadata.json", metrics_dir / "m6_llm_planning_content.metadata.json"]
    if not candidates:
        raise FileNotFoundError(f"No metadata found for {metric}")
    return {path.name: json.loads(path.read_text(encoding="utf-8")) for path in candidates if path.is_file()}


def _key_summaries(metrics_dir: Path) -> dict[str, Any]:
    m1 = pd.read_csv(metrics_dir / "m1_rq1_perception_panel_long.csv")
    m3 = pd.read_csv(metrics_dir / "m3_author_activity_participation.csv")
    m4 = pd.read_csv(metrics_dir / "m4_churn_magnitude_pooled.csv")
    m5 = pd.read_csv(metrics_dir / "m5_marker_density.csv")
    m6 = pd.read_csv(metrics_dir / "m6a_structural_planning.csv")
    m7 = pd.read_csv(metrics_dir / "m7_inactivity_trajectory.csv")
    m8 = pd.read_csv(metrics_dir / "m8_rework_magnitude.csv")
    m9 = pd.read_csv(metrics_dir / "m9_planning_vs_outcomes_m6a_t3.csv")
    return {
        "M1": {"rows": len(m1), "families": sorted(m1["perception_family"].unique().tolist()), "coverage_min": float(m1["coverage"].min())},
        "M3": {"team_semesters": int(len(m3)), "post_active_team_semesters": int(m3["post_commit_n"].gt(0).sum())},
        "M4": {"pooled_clean_churn_by_marker": m4.set_index("temporal_marker")["total_clean_churn"].to_dict()},
        "M5": {"density_per_1k_tokens": m5.set_index("temporal_marker")["friction_marker_density_per_1k_tokens"].round(6).to_dict()},
        "M6": {"team_semesters": int(len(m6)), "planning_artifact_present_n": int(m6["planning_artifact_present_t1"].sum())},
        "M7": {"daily_windows": int(len(m7)), "team_semesters": int(m7[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0])},
        "M8": {"team_semesters": int(len(m8)), "baseline_eligible_n": int(m8["baseline_eligible_for_rework_t3"].sum())},
        "M9": {"evaluator_association_rows": int(len(m9))},
    }


def _robustness_artifacts(root: Path) -> dict[str, Any]:
    figures_dir = resolve_figures_dir()
    families: dict[str, Any] = {}
    for family, config in ROBUSTNESS_ARTIFACT_FAMILIES.items():
        families[family] = {
            "status": config["status"],
            "section_target": config["section_target"],
            "artifacts": _artifact_records_for_patterns(figures_dir, config["patterns"], root),
        }
    return {
        "source_of_truth": "paper_v9/ARTIFACT_USAGE_CATALOG.md",
        "inventory": "paper_v9/FIGURES_CANDIDATES_WORKSHOP.md",
        "families": families,
    }


def build_summary() -> dict[str, Any]:
    root = resolve_paper_v9_dir()
    metrics_dir = resolve_metrics_dir()
    artifacts: dict[str, list[dict[str, Any]]] = {}
    metadata: dict[str, dict[str, Any]] = {}
    for metric, names in METRIC_FILES.items():
        artifacts[metric] = [_artifact_record(metrics_dir / name, root) for name in names]
        metadata[metric] = _metadata(metric, metrics_dir)
    return {
        "status": "success",
        "contract_version": CONTRACT_VERSION,
        "inference": "descriptive_or_exploratory_only",
        "source_of_truth": "paper_v9/data/metrics",
        "metrics": {metric: {"artifacts": artifacts[metric], "metadata": metadata[metric]} for metric in METRIC_FILES},
        "robustness_artifacts": _robustness_artifacts(root),
        "key_summaries": _key_summaries(metrics_dir),
        "limitations": ["Metric grains differ across RQ1-RQ3 and must not be pooled implicitly", "M6b structured fields are exploratory and non-composite", "M7 repository inactivity is not planning omission", "M8 path provenance is not semantic defect validation", "M9 associations are descriptive and non-causal", "Robustness artifacts are editorial/diagnostic views governed by ARTIFACT_USAGE_CATALOG.md, not additional causal estimators"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Paper V9 traceable results summary")
    parser.add_argument("--output", type=Path, default=None, help="Optional output path")
    args = parser.parse_args()
    output = args.output or (resolve_results_dir() / "results_summary.json")
    summary = build_summary()
    _atomic_write(output, json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()