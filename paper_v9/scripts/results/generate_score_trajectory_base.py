"""Generate the evaluator score trajectory base dataset for Paper V9."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "rq2-score-trajectory-base-v2"
STEM = "rq2_score_trajectory_base"
GROUP_COUNTS_STEM = "rq2_score_trajectory_group_counts"
TEAM_KEY = ["ID_Equipe", "Semestre"]
CHECKPOINTS = ("T1", "T2", "T3")
INITIAL_TRAJECTORY_THRESHOLD = 0.25
MIN_TRAJECTORY_GROUP_SIZE = 2
FLOAT_TOLERANCE = 1e-9
EVALUATOR_SCORE_COLUMNS = [
    "project_progress_mean",
    "scope_applicability_mean",
    "technical_complexity_mean",
    "engagement_participation_mean",
]
REQUIRED_COLUMNS = [*TEAM_KEY, "temporal_marker", *EVALUATOR_SCORE_COLUMNS]
PLANNING_REQUIRED_COLUMNS = [
    *TEAM_KEY,
    "planning_artifact_present_t1",
    "planning_scope_log1p_t1",
]
DESCRIPTIVE_SCORE_NOTE = (
    "The composite evaluator score is the unweighted mean of four evaluator "
    "dimensions. It is a descriptive analysis construct, not an official global "
    "quality metric."
)


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


def _load_evaluator_scores(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    _require_columns(frame, REQUIRED_COLUMNS, path)

    duplicate_keys = frame.duplicated([*TEAM_KEY, "temporal_marker"], keep=False)
    if duplicate_keys.any():
        duplicates = frame.loc[duplicate_keys, [*TEAM_KEY, "temporal_marker"]].to_dict("records")
        raise ValueError(f"Duplicate evaluator checkpoint rows found: {duplicates}")

    unexpected_markers = sorted(set(frame["temporal_marker"].dropna()) - set(CHECKPOINTS))
    if unexpected_markers:
        raise ValueError(f"Unexpected temporal markers in evaluator cuts: {unexpected_markers}")

    frame = frame.copy()
    frame["Semestre"] = frame["Semestre"].astype(str)
    for column in EVALUATOR_SCORE_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    frame["evaluator_score_composite"] = frame[EVALUATOR_SCORE_COLUMNS].mean(axis=1)
    return frame


def _build_score_trajectory_base(evaluator: pd.DataFrame) -> pd.DataFrame:
    wide = (
        evaluator.pivot(
            index=TEAM_KEY,
            columns="temporal_marker",
            values="evaluator_score_composite",
        )
        .rename(columns={checkpoint: f"evaluator_score_{checkpoint.lower()}" for checkpoint in CHECKPOINTS})
        .reset_index()
    )
    expected_score_columns = [f"evaluator_score_{checkpoint.lower()}" for checkpoint in CHECKPOINTS]
    _require_columns(wide, [*TEAM_KEY, *expected_score_columns], Path("evaluator_score_wide"))

    missing = wide.loc[wide[expected_score_columns].isna().any(axis=1), TEAM_KEY + expected_score_columns]
    if not missing.empty:
        raise ValueError(f"Missing checkpoint evaluator scores: {missing.to_dict('records')}")

    if len(wide) != 14:
        raise ValueError(f"Expected 14 team-semesters, got {len(wide)}")

    wide["delta_score_t3_minus_t1"] = wide["evaluator_score_t3"] - wide["evaluator_score_t1"]
    wide["delta_score_t2_minus_t1"] = wide["evaluator_score_t2"] - wide["evaluator_score_t1"]
    wide["delta_score_t3_minus_t2"] = wide["evaluator_score_t3"] - wide["evaluator_score_t2"]

    base = wide[
        [
            *TEAM_KEY,
            "evaluator_score_t1",
            "evaluator_score_t2",
            "evaluator_score_t3",
            "delta_score_t3_minus_t1",
            "delta_score_t2_minus_t1",
            "delta_score_t3_minus_t2",
        ]
    ].sort_values(TEAM_KEY).reset_index(drop=True)
    grouped, _ = _assign_score_trajectory_groups(base)
    return grouped


def _load_planning(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype={"Semestre": str})
    _require_columns(frame, PLANNING_REQUIRED_COLUMNS, path)

    duplicate_keys = frame.duplicated(TEAM_KEY, keep=False)
    if duplicate_keys.any():
        duplicates = frame.loc[duplicate_keys, TEAM_KEY].to_dict("records")
        raise ValueError(f"Duplicate planning team-semester rows found: {duplicates}")

    frame = frame.copy()
    frame["planning_present_t1"] = frame["planning_artifact_present_t1"].astype(bool)
    frame["planning_scope_log1p_t1"] = pd.to_numeric(frame["planning_scope_log1p_t1"], errors="raise")
    return frame[[*TEAM_KEY, "planning_present_t1", "planning_scope_log1p_t1"]]


def _merge_repository_visible_planning(base: pd.DataFrame, planning: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    merged = base.merge(planning, on=TEAM_KEY, how="left", validate="one_to_one")
    missing = merged.loc[merged["planning_present_t1"].isna(), TEAM_KEY]
    if not missing.empty:
        raise ValueError(f"Missing planning rows for score base: {missing.to_dict('records')}")

    planning_scope_median = float(merged["planning_scope_log1p_t1"].median())
    merged["planning_scope_tier"] = "lower_repository_visible_planning"
    high_mask = merged["planning_present_t1"].astype(bool) & merged["planning_scope_log1p_t1"].ge(planning_scope_median)
    merged.loc[high_mask, "planning_scope_tier"] = "high_repository_visible_planning"
    return merged[_output_columns()], planning_scope_median


def _assign_four_group_labels(frame: pd.DataFrame, threshold: float) -> pd.Series:
    t3_median = float(frame["evaluator_score_t3"].median())

    def label(row: pd.Series) -> str:
        delta = row["delta_score_t3_minus_t1"]
        if delta > threshold:
            return "improved"
        if delta < -threshold:
            return "declined"
        if row["evaluator_score_t3"] >= t3_median:
            return "stable_high"
        return "stable_low"

    return frame.apply(label, axis=1)


def _assign_three_group_labels(frame: pd.DataFrame, threshold: float) -> pd.Series:
    def label(delta: float) -> str:
        if delta > threshold + FLOAT_TOLERANCE:
            return "improved"
        if delta <= -threshold + FLOAT_TOLERANCE:
            return "declined"
        return "stable"

    return frame["delta_score_t3_minus_t1"].map(label)


def _choose_fallback_threshold(frame: pd.DataFrame) -> float:
    negative_delta_abs = sorted(
        {
            abs(float(delta))
            for delta in frame["delta_score_t3_minus_t1"]
            if delta < 0 and abs(float(delta)) <= INITIAL_TRAJECTORY_THRESHOLD
        },
        reverse=True,
    )
    for threshold in negative_delta_abs:
        normalized_threshold = round(threshold, 6)
        counts = _assign_three_group_labels(frame, normalized_threshold).value_counts()
        if {"improved", "stable", "declined"}.issubset(counts.index) and int(counts.min()) >= MIN_TRAJECTORY_GROUP_SIZE:
            return float(normalized_threshold)
    return INITIAL_TRAJECTORY_THRESHOLD


def _assign_score_trajectory_groups(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    result = frame.copy()
    initial_labels = _assign_four_group_labels(result, INITIAL_TRAJECTORY_THRESHOLD)
    initial_counts = initial_labels.value_counts().reindex(
        ["improved", "stable_high", "stable_low", "declined"],
        fill_value=0,
    )

    if int(initial_counts.min()) >= MIN_TRAJECTORY_GROUP_SIZE:
        result["score_trajectory_group"] = initial_labels
        return result, {
            "strategy": "four_group_initial_threshold",
            "threshold": INITIAL_TRAJECTORY_THRESHOLD,
            "fallback_applied": False,
            "initial_four_group_counts": {key: int(value) for key, value in initial_counts.items()},
        }

    fallback_threshold = _choose_fallback_threshold(result)
    result["score_trajectory_group"] = _assign_three_group_labels(result, fallback_threshold)
    final_counts = result["score_trajectory_group"].value_counts().reindex(
        ["improved", "stable", "declined"],
        fill_value=0,
    )
    return result, {
        "strategy": "three_group_adaptive_signed_threshold",
        "initial_threshold": INITIAL_TRAJECTORY_THRESHOLD,
        "threshold": fallback_threshold,
        "minimum_group_size": MIN_TRAJECTORY_GROUP_SIZE,
        "fallback_applied": True,
        "initial_four_group_counts": {key: int(value) for key, value in initial_counts.items()},
        "final_group_counts": {key: int(value) for key, value in final_counts.items()},
        "interpretation": (
            "The initial four-group rule with a 0.25 threshold produced an undersized "
            "declined group. The registered fallback collapses stable_high/stable_low "
            "into stable and selects the largest signed threshold that preserves at "
            "least two team-semesters per observed trajectory group."
        ),
    }


def _score_group_counts(base: pd.DataFrame) -> pd.DataFrame:
    counts = (
        base.groupby("score_trajectory_group", as_index=False)
        .agg(team_semester_n=("ID_Equipe", "size"))
        .sort_values(["score_trajectory_group"])
        .reset_index(drop=True)
    )
    counts["team_semester_pct"] = 100 * counts["team_semester_n"] / len(base)
    return counts


def _output_columns() -> list[str]:
    return [
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
    ]


def generate() -> dict[str, Any]:
    paper_dir = resolve_paper_v9_dir()
    repo_root = paper_dir.parent
    figures_dir = resolve_figures_dir()
    source_path = repo_root / "data" / "lake" / "evaluator_team_cuts.parquet"
    planning_path = paper_dir / "data" / "metrics" / "m6a_structural_planning.csv"
    data_path = figures_dir / f"{STEM}_data.csv"
    group_counts_path = figures_dir / f"{GROUP_COUNTS_STEM}.csv"
    metadata_path = figures_dir / f"{STEM}.metadata.json"

    evaluator = _load_evaluator_scores(source_path)
    base = _build_score_trajectory_base(evaluator)
    planning = _load_planning(planning_path)
    base, planning_scope_median = _merge_repository_visible_planning(base, planning)
    _atomic_csv(base, data_path)
    group_counts = _score_group_counts(base)
    _atomic_csv(group_counts, group_counts_path)
    _, trajectory_grouping = _assign_score_trajectory_groups(base.drop(columns=["score_trajectory_group"]))

    coverage_by_checkpoint = {}
    for checkpoint, group in evaluator.groupby("temporal_marker"):
        coverage_by_checkpoint[checkpoint] = {
            "team_semesters": int(group[TEAM_KEY].drop_duplicates().shape[0]),
            "distinct_team_ids": int(group["ID_Equipe"].nunique()),
            "semesters": sorted(group["Semestre"].astype(str).unique().tolist()),
        }
    checkpoint_rows = evaluator.groupby("temporal_marker").size().to_dict()
    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_id": STEM,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "data_path": str(data_path.relative_to(repo_root)),
        "group_counts_path": str(group_counts_path.relative_to(repo_root)),
        "source_path": str(source_path.relative_to(repo_root)),
        "planning_path": str(planning_path.relative_to(repo_root)),
        "source_sha256": compute_sha256(source_path),
        "planning_sha256": compute_sha256(planning_path),
        "data_sha256": compute_sha256(data_path),
        "group_counts_sha256": compute_sha256(group_counts_path),
        "team_key": TEAM_KEY,
        "checkpoints": list(CHECKPOINTS),
        "coverage": {
            "team_semesters": int(len(base)),
            "checkpoint_rows": {key: int(value) for key, value in checkpoint_rows.items()},
            "coverage_by_checkpoint": coverage_by_checkpoint,
        },
        "composite_score": {
            "columns": EVALUATOR_SCORE_COLUMNS,
            "aggregation": "unweighted_mean",
            "interpretation": DESCRIPTIVE_SCORE_NOTE,
        },
        "score_trajectory_grouping": trajectory_grouping,
        "repository_visible_planning": {
            "presence_column": "planning_present_t1",
            "scope_column": "planning_scope_log1p_t1",
            "tier_column": "planning_scope_tier",
            "tier_values": [
                "high_repository_visible_planning",
                "lower_repository_visible_planning",
            ],
            "planning_scope_log1p_t1_median": planning_scope_median,
            "high_tier_rule": (
                "planning_present_t1 is true and planning_scope_log1p_t1 is greater than "
                "or equal to the sample median"
            ),
            "interpretation": (
                "Repository-visible planning is a structural T1 artifact presence/scope "
                "measure, not a semantic planning quality rating."
            ),
        },
        "output_columns": _output_columns(),
        "limitations": [
            "Descriptive evaluator construct; not an official project quality score.",
            "Scores summarize evaluator form dimensions and do not measure objective GenAI usage.",
            "Trajectory groups are descriptive bins over a 14 team-semester sample and should not be over-interpreted.",
            "Repository-visible planning measures structural presence and scope, not planning quality.",
        ],
        "inference": "descriptive_non_causal",
    }
    _atomic_json(metadata, metadata_path)

    return {
        "status": "generated",
        "data_path": str(data_path),
        "group_counts_path": str(group_counts_path),
        "metadata_path": str(metadata_path),
        "coverage": metadata["coverage"],
        "score_trajectory_group_counts": group_counts.to_dict("records"),
    }


def main() -> None:
    result = generate()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
