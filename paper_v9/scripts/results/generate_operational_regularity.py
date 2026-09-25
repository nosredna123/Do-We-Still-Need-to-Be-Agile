"""Generate team-semester operational regularity metrics."""

from __future__ import annotations

import json
import math
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.artifact_policy import is_clean_path
from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256
from paper_v9.scripts.results.generate_score_trajectory_base import STEM as BASE_STEM

CONTRACT_VERSION = "rq2-operational-regularity-v1"
STEM = "rq2_operational_regularity"
TEAM_KEY = ["ID_Equipe", "Semestre"]
REQUIRED_BASE_COLUMNS = [
    *TEAM_KEY,
    "delta_score_t3_minus_t1",
    "score_trajectory_group",
    "planning_scope_tier",
    "final7_commit_share_pct",
    "final7_clean_churn_share_pct",
]
REQUIRED_COMMITS_COLUMNS = [*TEAM_KEY, "commit_hash", "timestamp", "ID_Autor_Local"]
REQUIRED_FILES_COLUMNS = [*TEAM_KEY, "commit_hash", "timestamp", "file_path", "lines_added", "lines_deleted"]
REQUIRED_PARTICIPATION_COLUMNS = [*TEAM_KEY, "presentation_anchor"]
REQUIRED_AUTHOR_COLUMNS = [*TEAM_KEY, "phase", "author_n", "max_author_share", "author_gini"]
REQUIRED_M7_COLUMNS = [*TEAM_KEY, "window_end_day_relative_to_t3", "repository_inactive_7d"]


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


def _normalized_entropy(values: pd.Series) -> float:
    total = float(values.sum())
    if total <= 0 or len(values) <= 1:
        return 0.0
    probabilities = values.loc[values.gt(0)].astype(float) / total
    entropy = float(-(probabilities * np.log(probabilities)).sum())
    return entropy / math.log(len(values))


def _coefficient_of_variation(values: pd.Series) -> float:
    mean = float(values.mean())
    if mean == 0:
        return 0.0
    return float(values.std(ddof=0) / mean)


def _inactive_run_lengths(active_mask: pd.Series) -> list[int]:
    runs: list[int] = []
    current = 0
    for active in active_mask.astype(bool).tolist():
        if active:
            if current:
                runs.append(current)
                current = 0
        else:
            current += 1
    if current:
        runs.append(current)
    return runs


def _weekly_counts(daily: pd.Series) -> pd.Series:
    weekly = daily.resample("W-MON", label="left", closed="left").sum()
    if weekly.empty:
        return pd.Series([float(daily.sum())])
    return weekly.astype(float)


def _regularity_for_team(
    *,
    key: tuple[str, str],
    commits: pd.DataFrame,
    clean_churn_daily: pd.Series,
    anchors: pd.DataFrame,
) -> dict[str, Any]:
    anchor_row = anchors.loc[
        anchors["ID_Equipe"].eq(key[0]) & anchors["Semestre"].eq(key[1])
    ]
    if len(anchor_row) != 1:
        raise ValueError(f"Expected one T3 anchor for {key}, got {len(anchor_row)}")
    anchor = pd.to_datetime(anchor_row["presentation_anchor"].iloc[0], utc=True)

    team_commits = commits.loc[commits["ID_Equipe"].eq(key[0]) & commits["Semestre"].eq(key[1])].copy()
    team_commits = team_commits.loc[team_commits["timestamp"].le(anchor)]
    if team_commits.empty:
        raise ValueError(f"No pre-T3 commits found for {key}")

    first_commit_day = team_commits["timestamp"].min().floor("D")
    anchor_day = anchor.floor("D")
    date_index = pd.date_range(first_commit_day, anchor_day, freq="D", tz="UTC")
    daily_commits = (
        team_commits.assign(day=team_commits["timestamp"].dt.floor("D"))
        .groupby("day")
        .size()
        .reindex(date_index, fill_value=0)
        .astype(float)
    )
    daily_clean_churn = clean_churn_daily.reindex(date_index, fill_value=0).astype(float)

    active_mask = daily_commits.gt(0)
    inactive_runs = _inactive_run_lengths(active_mask)
    weekly_commits = _weekly_counts(daily_commits)
    weekly_clean_churn = _weekly_counts(daily_clean_churn)

    active_day_count = int(active_mask.sum())
    project_span_days = int(len(date_index))
    return {
        "ID_Equipe": key[0],
        "Semestre": key[1],
        "active_day_count": active_day_count,
        "project_span_days": project_span_days,
        "active_day_share": active_day_count / project_span_days,
        "max_inactivity_gap_days": max(inactive_runs) if inactive_runs else 0,
        "median_inactivity_gap_days": float(np.median(inactive_runs)) if inactive_runs else 0.0,
        "commit_weekly_cv": _coefficient_of_variation(weekly_commits),
        "clean_churn_weekly_cv": _coefficient_of_variation(weekly_clean_churn),
        "temporal_entropy_commits": _normalized_entropy(daily_commits),
        "temporal_entropy_clean_churn": _normalized_entropy(daily_clean_churn),
    }


def _prepare_clean_churn_daily(files: pd.DataFrame, anchors: pd.DataFrame) -> dict[tuple[str, str], pd.Series]:
    files = files.copy()
    files["timestamp"] = pd.to_datetime(files["timestamp"], utc=True)
    files["lines_added"] = pd.to_numeric(files["lines_added"], errors="coerce").fillna(0)
    files["lines_deleted"] = pd.to_numeric(files["lines_deleted"], errors="coerce").fillna(0)
    files["clean_churn"] = files["lines_added"] + files["lines_deleted"]
    files = files.loc[files["file_path"].map(is_clean_path)].copy()
    files = files.merge(anchors[[*TEAM_KEY, "presentation_anchor"]], on=TEAM_KEY, validate="many_to_one")
    files["presentation_anchor"] = pd.to_datetime(files["presentation_anchor"], utc=True)
    files = files.loc[files["timestamp"].le(files["presentation_anchor"])]
    files["day"] = files["timestamp"].dt.floor("D")
    daily: dict[tuple[str, str], pd.Series] = {}
    for key, group in files.groupby(TEAM_KEY, sort=False):
        daily[(key[0], key[1])] = group.groupby("day")["clean_churn"].sum()
    return daily


def generate() -> dict[str, Any]:
    paper_v9 = resolve_paper_v9_dir()
    repo_root = paper_v9.parent
    figures_dir = resolve_figures_dir()
    metrics_dir = resolve_metrics_dir()

    paths = {
        "base": figures_dir / f"{BASE_STEM}_data.csv",
        "commits": repo_root / "data" / "lake" / "git_commits.parquet",
        "files": repo_root / "data" / "lake" / "git_files.parquet",
        "participation": metrics_dir / "m3_author_activity_participation.csv",
        "author_concentration": metrics_dir / "m3_author_concentration.csv",
        "m7": metrics_dir / "m7_inactivity_trajectory.csv",
    }

    base = pd.read_csv(paths["base"], dtype={"Semestre": str})
    commits = pd.read_parquet(paths["commits"])
    files = pd.read_parquet(paths["files"])
    participation = pd.read_csv(paths["participation"], dtype={"Semestre": str})
    author_concentration = pd.read_csv(paths["author_concentration"], dtype={"Semestre": str})
    m7 = pd.read_csv(paths["m7"], dtype={"Semestre": str})

    _require_columns(base, REQUIRED_BASE_COLUMNS, paths["base"])
    _require_columns(commits, REQUIRED_COMMITS_COLUMNS, paths["commits"])
    _require_columns(files, REQUIRED_FILES_COLUMNS, paths["files"])
    _require_columns(participation, REQUIRED_PARTICIPATION_COLUMNS, paths["participation"])
    _require_columns(author_concentration, REQUIRED_AUTHOR_COLUMNS, paths["author_concentration"])
    _require_columns(m7, REQUIRED_M7_COLUMNS, paths["m7"])

    commits = commits.copy()
    commits["Semestre"] = commits["Semestre"].astype(str)
    commits["timestamp"] = pd.to_datetime(commits["timestamp"], utc=True)
    anchors = participation[[*TEAM_KEY, "presentation_anchor"]].copy()
    anchors["presentation_anchor"] = pd.to_datetime(anchors["presentation_anchor"], utc=True)

    clean_churn_daily = _prepare_clean_churn_daily(files, anchors)
    rows: list[dict[str, Any]] = []
    for key_frame in base[TEAM_KEY].drop_duplicates().sort_values(TEAM_KEY).itertuples(index=False):
        key = (key_frame.ID_Equipe, key_frame.Semestre)
        rows.append(
            _regularity_for_team(
                key=key,
                commits=commits,
                clean_churn_daily=clean_churn_daily.get(key, pd.Series(dtype=float)),
                anchors=anchors,
            )
        )
    regularity = pd.DataFrame(rows)

    author_pre = author_concentration.loc[author_concentration["phase"].eq("pre")].copy()
    author_pre = author_pre[[*TEAM_KEY, "author_n", "max_author_share", "author_gini"]].rename(
        columns={"author_n": "author_count"}
    )
    m7_summary = (
        m7.groupby(TEAM_KEY, as_index=False)
        .agg(
            m7_window_count=("repository_inactive_7d", "size"),
            m7_inactive_window_share=("repository_inactive_7d", "mean"),
        )
    )

    output = (
        base[
            [
                *TEAM_KEY,
                "delta_score_t3_minus_t1",
                "score_trajectory_group",
                "planning_scope_tier",
                "final7_commit_share_pct",
                "final7_clean_churn_share_pct",
            ]
        ]
        .merge(regularity, on=TEAM_KEY, validate="one_to_one")
        .merge(author_pre, on=TEAM_KEY, validate="one_to_one")
        .merge(m7_summary, on=TEAM_KEY, validate="one_to_one")
        .sort_values(TEAM_KEY)
        .reset_index(drop=True)
    )
    if len(output) != 14:
        raise ValueError(f"Expected 14 team-semesters, got {len(output)}")

    data_path = figures_dir / f"{STEM}_data.csv"
    metadata_path = figures_dir / f"{STEM}.metadata.json"
    _atomic_csv(output, data_path)

    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_id": STEM,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "data_path": str(data_path.relative_to(repo_root)),
        "data_sha256": compute_sha256(data_path),
        "inputs": {name: str(path.relative_to(repo_root)) for name, path in paths.items()},
        "input_sha256": {name: compute_sha256(path) for name, path in paths.items()},
        "coverage": {
            "team_semesters": int(len(output)),
            "m7_windows_per_team_semester": sorted(output["m7_window_count"].unique().astype(int).tolist()),
        },
        "regularity_period": (
            "First observed commit day through the team-semester T3 presentation anchor; "
            "weekly and daily zero-activity bins are included only within this observed period."
        ),
        "formulas": {
            "active_day_count": "Count of days with at least one commit in the observed period.",
            "project_span_days": "Calendar days from first pre-T3 commit day through T3 anchor day, inclusive.",
            "active_day_share": "active_day_count / project_span_days.",
            "max_inactivity_gap_days": "Longest run of zero-commit days inside the observed daily series.",
            "median_inactivity_gap_days": "Median run length of zero-commit days inside the observed daily series.",
            "commit_weekly_cv": "Population coefficient of variation of weekly commit counts, including zero weeks in the observed period.",
            "clean_churn_weekly_cv": "Population coefficient of variation of weekly clean source/test churn, including zero weeks in the observed period.",
            "temporal_entropy_commits": "Shannon entropy of daily commit counts normalized by log(project_span_days).",
            "temporal_entropy_clean_churn": "Shannon entropy of daily clean churn normalized by log(project_span_days).",
            "author_count": "M3 pre-T3 author count.",
            "max_author_share": "M3 pre-T3 maximum local-author commit share.",
            "author_gini": "M3 pre-T3 local-author commit Gini coefficient.",
        },
        "separation_of_constructs": (
            "Regularity metrics describe temporal distribution of observed repository activity, "
            "not productivity, process compliance, or semantic quality."
        ),
        "inference": "descriptive_non_causal",
        "limitations": [
            "Repository regularity is an observable Git proxy, not a direct measurement of Scrum, Kanban, or coordination process.",
            "Weekly zero bins are included only after first observed commit and before the T3 anchor.",
            "Clean churn uses the repository code-path policy and is not semantic quality evidence.",
        ],
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
