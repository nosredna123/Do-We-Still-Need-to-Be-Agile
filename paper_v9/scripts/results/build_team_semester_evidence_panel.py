"""Build an integrated team-semester evidence panel for Paper V9."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "team-semester-evidence-panel-v1"
STEM = "team_semester_evidence_panel"
TEAM_KEY = ["ID_Equipe", "Semestre"]
CHECKPOINTS = ("T1", "T2", "T3")
PHASES = ("pre_t1", "t1_to_t2", "t2_to_t3_excluding_final7", "final7_pre_t3")
M1_PANEL_COLUMNS = [
    "ai_benefit_mean",
    "autonomy_tool_dependency_mean",
    "ai_career_impact_5y_mean",
    "project_feeling_mean",
]
M2_ROLES = ["Backend", "Frontend", "Project Manager", "QA", "Scrum Master"]


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def _atomic_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _require_columns(frame: pd.DataFrame, columns: list[str], source: Path) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def _ensure_unique(frame: pd.DataFrame, keys: list[str], source: Path) -> None:
    duplicated = frame.duplicated(keys, keep=False)
    if duplicated.any():
        duplicates = frame.loc[duplicated, keys].to_dict("records")
        raise ValueError(f"Duplicate rows in {source} for {keys}: {duplicates}")


def _load_score_base(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    required = [
        *TEAM_KEY,
        "evaluator_score_t1",
        "evaluator_score_t2",
        "evaluator_score_t3",
        "delta_score_t3_minus_t1",
        "delta_score_t2_minus_t1",
        "delta_score_t3_minus_t2",
        "score_trajectory_group",
        "planning_present_t1",
        "planning_scope_log1p_t1",
        "planning_scope_tier",
        "final7_commit_share_pct",
        "final7_clean_churn_share_pct",
    ]
    _require_columns(frame, required, path)
    _ensure_unique(frame, TEAM_KEY, path)
    if len(frame) != 14:
        raise ValueError(f"Expected 14 team-semester rows in {path}, got {len(frame)}")
    return frame[required].copy()


def _load_regularity(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    columns = [
        *TEAM_KEY,
        "active_day_count",
        "project_span_days",
        "active_day_share",
        "max_inactivity_gap_days",
        "median_inactivity_gap_days",
        "commit_weekly_cv",
        "clean_churn_weekly_cv",
        "temporal_entropy_commits",
        "temporal_entropy_clean_churn",
        "author_count",
        "max_author_share",
        "author_gini",
        "m7_window_count",
        "m7_inactive_window_share",
        "regularity_index",
    ]
    _require_columns(frame, columns, path)
    _ensure_unique(frame, TEAM_KEY, path)
    return frame[columns].copy()


def _load_complexity(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    columns = [
        *TEAM_KEY,
        "technical_complexity_mean_t1",
        "technical_complexity_mean_t2",
        "technical_complexity_mean_t3",
        "delta_technical_complexity_t3_minus_t1",
        "clean_distinct_file_n",
        "clean_distinct_directory_n",
        "clean_max_path_depth",
        "clean_extension_n",
        "clean_touching_commit_n_inferred",
        "clean_total_churn_inferred",
        "mean_clean_files_per_commit",
        "frontend_clean_file_event_share",
        "backend_clean_file_event_share",
        "clean_churn_t3",
        "all_churn_t3",
        "clean_rework_churn_t3",
        "clean_rework_ratio_t3",
        "baseline_eligible_for_rework_t3",
        "measurement_status",
        "pi_file_count_t1",
        "pi_line_delta_t1",
    ]
    _require_columns(frame, columns, path)
    _ensure_unique(frame, TEAM_KEY, path)
    result = frame[columns].copy()
    return result.rename(columns={"measurement_status": "m8_rework_measurement_status"})


def _load_phase_totals(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    required = [
        *TEAM_KEY,
        "phase",
        "team_total_commit_n",
        "team_total_clean_churn",
        "commit_share_pct",
        "clean_churn_share_pct",
    ]
    _require_columns(frame, required, path)
    unexpected = sorted(set(frame["phase"]) - set(PHASES))
    if unexpected:
        raise ValueError(f"Unexpected phase labels in {path}: {unexpected}")
    totals = frame[[*TEAM_KEY, "team_total_commit_n", "team_total_clean_churn"]].drop_duplicates()
    _ensure_unique(totals, TEAM_KEY, path)
    phase_share = frame.pivot(index=TEAM_KEY, columns="phase", values=["commit_share_pct", "clean_churn_share_pct"])
    phase_share.columns = [f"{phase}_{metric}" for metric, phase in phase_share.columns]
    phase_share = phase_share.reset_index()
    _ensure_unique(phase_share, TEAM_KEY, path)
    return totals.merge(phase_share, on=TEAM_KEY, how="left", validate="one_to_one")


def _load_m5_summary(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = [
        "temporal_marker",
        "m5_friction_marker_density_per_1k_tokens",
        "m5_friction_marker_n",
        "m5_token_n",
    ]
    _require_columns(frame, required, path)
    _ensure_unique(frame, ["temporal_marker"], path)
    unexpected = sorted(set(frame["temporal_marker"]) - set(CHECKPOINTS))
    if unexpected:
        raise ValueError(f"Unexpected M5 markers in {path}: {unexpected}")
    flat: dict[str, float] = {}
    for row in frame.to_dict("records"):
        marker = str(row["temporal_marker"]).lower()
        flat[f"friction_marker_density_per_1k_tokens_{marker}"] = float(
            row["m5_friction_marker_density_per_1k_tokens"]
        )
        flat[f"friction_marker_n_{marker}"] = float(row["m5_friction_marker_n"])
        flat[f"token_n_{marker}"] = float(row["m5_token_n"])
    flat["m5_delta_density_t3_minus_t1"] = (
        flat["friction_marker_density_per_1k_tokens_t3"]
        - flat["friction_marker_density_per_1k_tokens_t1"]
    )
    return pd.DataFrame([flat])


def _load_m1_semester_checkpoint(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    required = ["Semestre", "temporal_marker", *M1_PANEL_COLUMNS]
    _require_columns(frame, required, path)
    rows: list[dict[str, Any]] = []
    for semester, group in frame.groupby("Semestre", sort=True):
        by_marker = group.set_index("temporal_marker")
        row: dict[str, Any] = {
            "Semestre": semester,
            "m1_aggregation_level": "semester_checkpoint_student_aggregate",
        }
        for column in M1_PANEL_COLUMNS:
            if {"T1", "T3"}.issubset(by_marker.index):
                row[f"m1_{column}_t1"] = float(by_marker.loc["T1", column])
                row[f"m1_{column}_t3"] = float(by_marker.loc["T3", column])
                row[f"m1_{column}_delta_t3_minus_t1"] = row[f"m1_{column}_t3"] - row[f"m1_{column}_t1"]
            else:
                row[f"m1_{column}_t1"] = pd.NA
                row[f"m1_{column}_t3"] = pd.NA
                row[f"m1_{column}_delta_t3_minus_t1"] = pd.NA
        rows.append(row)
    result = pd.DataFrame(rows)
    _ensure_unique(result, ["Semestre"], path)
    return result


def _load_m2_role_perception(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    required = ["Semestre", "temporal_marker", "role", "mean", "agreement_share", "n"]
    _require_columns(frame, required, path)
    t3 = frame.loc[frame["temporal_marker"].eq("T3") & frame["role"].isin(M2_ROLES)].copy()
    t3["role_slug"] = (
        t3["role"]
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )
    mean_pivot = t3.pivot(index="Semestre", columns="role_slug", values="mean").add_prefix("m2_t3_role_mean_")
    agreement_pivot = (
        t3.pivot(index="Semestre", columns="role_slug", values="agreement_share")
        .add_prefix("m2_t3_role_agreement_share_")
    )
    result = mean_pivot.join(agreement_pivot).reset_index()
    result["m2_aggregation_level"] = "semester_checkpoint_role_aggregate"
    _ensure_unique(result, ["Semestre"], path)
    return result


def _load_m6b(path: Path) -> pd.DataFrame:
    records = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for record in records:
        parsed = record.get("parsed_response", {})
        insufficient = record.get("insufficient_evidence") or parsed.get("insufficient_evidence") or []
        rows.append(
            {
                "ID_Equipe": record["ID_Equipe"],
                "Semestre": str(record["Semestre"]),
                "m6b_status": record.get("status", "missing_status"),
                "m6b_planning_evidence_present": parsed.get("planning_evidence_present", pd.NA),
                "m6b_input_subject_n": len(record.get("input_subjects", [])),
                "m6b_evidence_quote_n": len(parsed.get("evidence_quotes", [])),
                "m6b_insufficient_evidence_n": len(insufficient),
                "m6b_unavailable_reason": insufficient[0].get("reason") if insufficient else "",
            }
        )
    result = pd.DataFrame(rows)
    _ensure_unique(result, TEAM_KEY, path)
    return result


def _attach_m5(panel: pd.DataFrame, m5_summary: pd.DataFrame) -> pd.DataFrame:
    result = panel.copy()
    m5_values = m5_summary.iloc[0].to_dict()
    for column, value in m5_values.items():
        result[f"m5_global_{column}"] = pd.NA
        result.loc[result["Semestre"].eq("2025.2"), f"m5_global_{column}"] = value
    result["m5_coverage_status"] = "unavailable_not_measured"
    result.loc[result["Semestre"].eq("2025.2"), "m5_coverage_status"] = "available_transcript_corpus_2025_2"
    result["m5_analysis_level"] = "global_transcript_corpus_by_temporal_marker"
    result["m5_team_level_measure"] = False
    result["m5_zero_filled_unavailable_semesters"] = False
    return result


def _build_panel(paths: dict[str, Path]) -> pd.DataFrame:
    panel = _load_score_base(paths["score_base"])
    panel = panel.merge(_load_regularity(paths["regularity"]), on=TEAM_KEY, how="left", validate="one_to_one")
    panel = panel.merge(_load_complexity(paths["complexity"]), on=TEAM_KEY, how="left", validate="one_to_one")
    panel = panel.merge(_load_phase_totals(paths["phase_activity"]), on=TEAM_KEY, how="left", validate="one_to_one")
    panel = panel.merge(_load_m1_semester_checkpoint(paths["m1_perception"]), on="Semestre", how="left", validate="many_to_one")
    panel = panel.merge(_load_m2_role_perception(paths["m2_role"]), on="Semestre", how="left", validate="many_to_one")
    panel = panel.merge(_load_m6b(paths["m6b"]), on=TEAM_KEY, how="left", validate="one_to_one")
    panel = _attach_m5(panel, _load_m5_summary(paths["m5_summary"]))

    coverage_columns = [
        "m1_aggregation_level",
        "m2_aggregation_level",
        "m5_coverage_status",
        "m5_analysis_level",
        "m5_team_level_measure",
        "m5_zero_filled_unavailable_semesters",
        "m6b_status",
        "m8_rework_measurement_status",
    ]
    panel["panel_row_completeness_status"] = "complete_core_metrics"
    missing_core = panel[
        [
            "evaluator_score_t1",
            "evaluator_score_t2",
            "evaluator_score_t3",
            "planning_scope_log1p_t1",
            "regularity_index",
            "clean_rework_churn_t3",
            "technical_complexity_mean_t3",
        ]
    ].isna().any(axis=1)
    panel.loc[missing_core, "panel_row_completeness_status"] = "missing_core_metric"
    panel["coverage_fields_present"] = panel[coverage_columns].notna().all(axis=1)

    if len(panel) != 14:
        raise ValueError(f"Expected 14 panel rows, got {len(panel)}")
    if panel[TEAM_KEY].duplicated().any():
        raise ValueError("Panel has duplicate team-semester rows")
    return panel.sort_values(TEAM_KEY).reset_index(drop=True)


def generate() -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[3]
    metrics_dir = resolve_metrics_dir()
    figures_dir = resolve_figures_dir()
    paths = {
        "score_base": figures_dir / "rq2_score_trajectory_base_data.csv",
        "regularity": figures_dir / "rq2_operational_regularity_data.csv",
        "complexity": figures_dir / "rq3_complexity_profile_data.csv",
        "phase_activity": figures_dir / "rq2_phase_activity_share_data.csv",
        "m5_summary": figures_dir / "rq2_m5_2025_triangulation_summary.csv",
        "m1_perception": metrics_dir / "m1_rq1_perception_panel_wide.csv",
        "m2_role": metrics_dir / "m2_role_perception_by_team_semester.csv",
        "m6b": metrics_dir / "m6b_llm_planning_content.json",
    }
    output_paths = {
        "panel": figures_dir / f"{STEM}.csv",
        "metadata": figures_dir / f"{STEM}.metadata.json",
    }

    panel = _build_panel(paths)
    _atomic_csv(panel, output_paths["panel"])

    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_id": STEM,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {name: str(path.relative_to(repo_root)) for name, path in paths.items()},
        "input_sha256": {name: compute_sha256(path) for name, path in paths.items()},
        "outputs": {"panel": str(output_paths["panel"].relative_to(repo_root))},
        "output_sha256": {"panel": compute_sha256(output_paths["panel"])},
        "coverage": {
            "team_semesters": int(len(panel)),
            "semesters": sorted(panel["Semestre"].unique().tolist()),
            "m5_available_team_semesters": int(panel["m5_coverage_status"].eq("available_transcript_corpus_2025_2").sum()),
            "m5_unavailable_team_semesters": int(panel["m5_coverage_status"].eq("unavailable_not_measured").sum()),
            "m6b_success_team_semesters": int(panel["m6b_status"].eq("success").sum()),
            "m6b_unavailable_team_semesters": int(panel["m6b_status"].ne("success").sum()),
            "baseline_eligible_rework_team_semesters": int(panel["baseline_eligible_for_rework_t3"].astype(bool).sum()),
        },
        "grain_contract": {
            "row_unit": "team_semester",
            "team_semester_metrics": [
                "planning",
                "evaluator_scores",
                "git_activity",
                "regularity",
                "rework",
                "complexity",
                "phase_shares",
                "m6b_commit_subject_planning",
            ],
            "semester_checkpoint_aggregates_repeated_by_team_semester": [
                "m1_perception",
                "m2_role_perception",
            ],
            "global_transcript_corpus_context_repeated_for_2025_2_only": ["m5_marker_density"],
            "not_zero_filled": ["m5_2026_1_unavailable_not_measured"],
        },
        "inference": "descriptive_integrated_evidence_panel_not_causal",
        "limitations": [
            "The panel is an editorial/reproducibility index, not a statistical model.",
            "M1 and M2 are semester/checkpoint aggregates repeated on team-semester rows with explicit aggregation-level fields.",
            "M5 is global transcript-corpus evidence for 2025.2 only and is not a team-level metric.",
            "M6b depends on T1 commit-subject availability and is marked unavailable when no subjects exist.",
        ],
    }
    _atomic_json(metadata, output_paths["metadata"])
    return {
        "status": "generated",
        "panel": str(output_paths["panel"]),
        "metadata": str(output_paths["metadata"]),
        "coverage": metadata["coverage"],
    }


def main() -> None:
    print(json.dumps(generate(), indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
