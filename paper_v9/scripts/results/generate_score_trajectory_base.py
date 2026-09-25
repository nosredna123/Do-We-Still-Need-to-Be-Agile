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

CONTRACT_VERSION = "rq2-score-trajectory-base-v1"
STEM = "rq2_score_trajectory_base"
TEAM_KEY = ["ID_Equipe", "Semestre"]
CHECKPOINTS = ("T1", "T2", "T3")
EVALUATOR_SCORE_COLUMNS = [
    "project_progress_mean",
    "scope_applicability_mean",
    "technical_complexity_mean",
    "engagement_participation_mean",
]
REQUIRED_COLUMNS = [*TEAM_KEY, "temporal_marker", *EVALUATOR_SCORE_COLUMNS]
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

    columns = [
        *TEAM_KEY,
        "evaluator_score_t1",
        "evaluator_score_t2",
        "evaluator_score_t3",
        "delta_score_t3_minus_t1",
        "delta_score_t2_minus_t1",
        "delta_score_t3_minus_t2",
    ]
    return wide[columns].sort_values(TEAM_KEY).reset_index(drop=True)


def generate() -> dict[str, Any]:
    paper_dir = resolve_paper_v9_dir()
    repo_root = paper_dir.parent
    figures_dir = resolve_figures_dir()
    source_path = repo_root / "data" / "lake" / "evaluator_team_cuts.parquet"
    data_path = figures_dir / f"{STEM}_data.csv"
    metadata_path = figures_dir / f"{STEM}.metadata.json"

    evaluator = _load_evaluator_scores(source_path)
    base = _build_score_trajectory_base(evaluator)
    _atomic_csv(base, data_path)

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
        "source_path": str(source_path.relative_to(repo_root)),
        "source_sha256": compute_sha256(source_path),
        "data_sha256": compute_sha256(data_path),
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
        "output_columns": list(base.columns),
        "limitations": [
            "Descriptive evaluator construct; not an official project quality score.",
            "Scores summarize evaluator form dimensions and do not measure objective GenAI usage.",
        ],
        "inference": "descriptive_non_causal",
    }
    _atomic_json(metadata, metadata_path)

    return {
        "status": "generated",
        "data_path": str(data_path),
        "metadata_path": str(metadata_path),
        "coverage": metadata["coverage"],
    }


def main() -> None:
    result = generate()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
