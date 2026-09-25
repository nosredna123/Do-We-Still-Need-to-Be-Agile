"""Generate team-semester complexity profiles for confounding analysis."""

from __future__ import annotations

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.artifact_policy import CURRENT_POLICY_VERSION, is_clean_path
from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "rq3-complexity-profile-v1"
STEM = "rq3_complexity_profile"
METRICS_CONTRACT_STEM = "rq3_complexity_metrics_contract"
TEAM_KEY = ["ID_Equipe", "Semestre"]
TECHNICAL_COMPLEXITY_COLUMN = "technical_complexity_mean"
REQUIRED_EVALUATOR_COLUMNS = [
    *TEAM_KEY,
    "temporal_marker",
    TECHNICAL_COMPLEXITY_COLUMN,
]
REQUIRED_FILES_COLUMNS = [
    *TEAM_KEY,
    "commit_hash",
    "file_path",
    "file_extension",
    "lines_added",
    "lines_deleted",
    "is_binary",
]
REQUIRED_CHURN_COLUMNS = [
    *TEAM_KEY,
    "temporal_marker",
    "clean_churn",
    "all_churn",
    "clean_unique_file_n",
    "clean_touching_commit_n",
]
REQUIRED_REWORK_COLUMNS = [
    *TEAM_KEY,
    "clean_rework_churn_t3",
    "clean_rework_ratio_t3",
    "baseline_eligible_for_rework_t3",
    "measurement_status",
]
REQUIRED_PLANNING_COLUMNS = [
    *TEAM_KEY,
    "planning_artifact_present_t1",
    "planning_scope_log1p_t1",
    "pi_file_count_t1",
    "pi_line_delta_t1",
]
REQUIRED_BASE_COLUMNS = [
    *TEAM_KEY,
    "score_trajectory_group",
    "planning_scope_tier",
    "final7_commit_share_pct",
    "final7_clean_churn_share_pct",
]
FRONTEND_PATH_MARKERS = frozenset(
    {
        "frontend",
        "front-end",
        "client",
        "web",
        "ui",
        "pages",
        "components",
        "views",
    }
)
BACKEND_PATH_MARKERS = frozenset(
    {
        "backend",
        "back-end",
        "server",
        "api",
        "apis",
        "services",
        "controllers",
        "routes",
        "models",
        "repositories",
    }
)


EVALUATED_COMPLEXITY_COLUMNS = [
    "technical_complexity_mean_t1",
    "technical_complexity_mean_t2",
    "technical_complexity_mean_t3",
    "delta_technical_complexity_t3_minus_t1",
]
STRUCTURAL_COMPLEXITY_COLUMNS = [
    "clean_distinct_file_n",
    "clean_distinct_directory_n",
    "clean_max_path_depth",
    "clean_extension_n",
    "clean_touching_commit_n_inferred",
    "mean_clean_files_per_commit",
    "clean_total_churn_inferred",
    "frontend_clean_file_event_share",
    "backend_clean_file_event_share",
]


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


def _safe_path_parts(file_path: str | None) -> tuple[str, ...]:
    if file_path is None or pd.isna(file_path):
        return tuple()
    return tuple(part for part in PurePosixPath(str(file_path).replace("\\", "/")).parts if part not in {"", "."})


def _path_depth(file_path: str | None) -> int:
    return len(_safe_path_parts(file_path))


def _directory_key(file_path: str | None) -> str:
    parts = _safe_path_parts(file_path)
    if len(parts) <= 1:
        return "."
    return "/".join(parts[:-1])


def _architecture_layer(file_path: str | None) -> str:
    markers = {part.lower() for part in _safe_path_parts(file_path)}
    has_frontend = bool(markers & FRONTEND_PATH_MARKERS)
    has_backend = bool(markers & BACKEND_PATH_MARKERS)
    if has_frontend and has_backend:
        return "mixed"
    if has_frontend:
        return "frontend"
    if has_backend:
        return "backend"
    return "other_or_unclassified"


def _technical_complexity(evaluator: pd.DataFrame) -> pd.DataFrame:
    technical = evaluator[[*TEAM_KEY, "temporal_marker", TECHNICAL_COMPLEXITY_COLUMN]].copy()
    pivot = technical.pivot(index=TEAM_KEY, columns="temporal_marker", values=TECHNICAL_COMPLEXITY_COLUMN)
    pivot = pivot.rename(
        columns={
            "T1": "technical_complexity_mean_t1",
            "T2": "technical_complexity_mean_t2",
            "T3": "technical_complexity_mean_t3",
        }
    )
    pivot = pivot.reset_index()
    for column in [
        "technical_complexity_mean_t1",
        "technical_complexity_mean_t2",
        "technical_complexity_mean_t3",
    ]:
        if column not in pivot.columns:
            pivot[column] = pd.NA
    pivot["delta_technical_complexity_t3_minus_t1"] = (
        pivot["technical_complexity_mean_t3"] - pivot["technical_complexity_mean_t1"]
    )
    return pivot[[*TEAM_KEY, "technical_complexity_mean_t1", "technical_complexity_mean_t2", "technical_complexity_mean_t3", "delta_technical_complexity_t3_minus_t1"]]


def _structural_complexity(files: pd.DataFrame) -> pd.DataFrame:
    files = files.copy()
    files["Semestre"] = files["Semestre"].astype(str)
    files["lines_added"] = pd.to_numeric(files["lines_added"], errors="coerce").fillna(0)
    files["lines_deleted"] = pd.to_numeric(files["lines_deleted"], errors="coerce").fillna(0)
    files["clean_churn"] = files["lines_added"] + files["lines_deleted"]
    files["is_clean_path"] = files["file_path"].map(is_clean_path)
    files = files.loc[files["is_clean_path"] & ~files["is_binary"].fillna(False)].copy()
    files["directory"] = files["file_path"].map(_directory_key)
    files["path_depth"] = files["file_path"].map(_path_depth)
    files["architecture_layer"] = files["file_path"].map(_architecture_layer)
    files["file_extension_clean"] = files["file_extension"].fillna("").replace("", "(none)")

    per_commit = (
        files.groupby([*TEAM_KEY, "commit_hash"], as_index=False)
        .agg(clean_files_touched=("file_path", "nunique"))
    )
    per_team = (
        files.groupby(TEAM_KEY, as_index=False)
        .agg(
            clean_distinct_file_n=("file_path", "nunique"),
            clean_distinct_directory_n=("directory", "nunique"),
            clean_max_path_depth=("path_depth", "max"),
            clean_extension_n=("file_extension_clean", "nunique"),
            clean_touching_commit_n_inferred=("commit_hash", "nunique"),
            clean_total_churn_inferred=("clean_churn", "sum"),
            frontend_clean_file_event_n=("architecture_layer", lambda values: int((values == "frontend").sum())),
            backend_clean_file_event_n=("architecture_layer", lambda values: int((values == "backend").sum())),
            mixed_clean_file_event_n=("architecture_layer", lambda values: int((values == "mixed").sum())),
            unclassified_clean_file_event_n=(
                "architecture_layer",
                lambda values: int((values == "other_or_unclassified").sum()),
            ),
        )
    )
    commit_diversity = (
        per_commit.groupby(TEAM_KEY, as_index=False)
        .agg(mean_clean_files_per_commit=("clean_files_touched", "mean"))
    )
    per_team = per_team.merge(commit_diversity, on=TEAM_KEY, how="left", validate="one_to_one")
    total_events = (
        per_team["frontend_clean_file_event_n"]
        + per_team["backend_clean_file_event_n"]
        + per_team["mixed_clean_file_event_n"]
        + per_team["unclassified_clean_file_event_n"]
    )
    per_team["frontend_clean_file_event_share"] = per_team["frontend_clean_file_event_n"] / total_events
    per_team["backend_clean_file_event_share"] = per_team["backend_clean_file_event_n"] / total_events
    return per_team


def _churn_t3(churn: pd.DataFrame) -> pd.DataFrame:
    t3 = churn.loc[churn["temporal_marker"].eq("T3")].copy()
    return t3[
        [
            *TEAM_KEY,
            "clean_churn",
            "all_churn",
            "clean_unique_file_n",
            "clean_touching_commit_n",
        ]
    ].rename(
        columns={
            "clean_churn": "clean_churn_t3",
            "all_churn": "all_churn_t3",
            "clean_unique_file_n": "m4_clean_unique_file_n_t3",
            "clean_touching_commit_n": "m4_clean_touching_commit_n_t3",
        }
    )


def _metrics_contract() -> pd.DataFrame:
    rows = [
        {
            "metric": "technical_complexity_mean_t1",
            "construct_family": "evaluated_complexity",
            "plan_requirement": "technical_complexity_mean_t1",
            "source": "data/lake/evaluator_team_cuts.parquet",
            "definition": "Mean evaluator technical-complexity score at temporal marker T1.",
            "heuristic_or_policy": "Evaluator-derived; not repository structural inference.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "technical_complexity_mean_t2",
            "construct_family": "evaluated_complexity",
            "plan_requirement": "technical_complexity_mean_t2",
            "source": "data/lake/evaluator_team_cuts.parquet",
            "definition": "Mean evaluator technical-complexity score at temporal marker T2.",
            "heuristic_or_policy": "Evaluator-derived; not repository structural inference.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "technical_complexity_mean_t3",
            "construct_family": "evaluated_complexity",
            "plan_requirement": "technical_complexity_mean_t3",
            "source": "data/lake/evaluator_team_cuts.parquet",
            "definition": "Mean evaluator technical-complexity score at temporal marker T3.",
            "heuristic_or_policy": "Evaluator-derived; not repository structural inference.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "delta_technical_complexity_t3_minus_t1",
            "construct_family": "evaluated_complexity",
            "plan_requirement": "delta_technical_complexity_t3_minus_t1",
            "source": "data/lake/evaluator_team_cuts.parquet",
            "definition": "technical_complexity_mean_t3 minus technical_complexity_mean_t1.",
            "heuristic_or_policy": "Derived from evaluator technical-complexity means.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_distinct_file_n",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "número de arquivos limpos distintos",
            "source": "data/lake/git_files.parquet",
            "definition": "Number of distinct clean-path files touched in observed Git file events.",
            "heuristic_or_policy": CURRENT_POLICY_VERSION,
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_distinct_directory_n",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "número de diretórios distintos",
            "source": "data/lake/git_files.parquet",
            "definition": "Number of distinct parent directories among clean-path file events.",
            "heuristic_or_policy": "Directory is derived from normalized POSIX-style file paths after clean-path filtering.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_max_path_depth",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "profundidade máxima de caminho",
            "source": "data/lake/git_files.parquet",
            "definition": "Maximum normalized path depth among clean-path file events.",
            "heuristic_or_policy": "Depth counts normalized path segments after clean-path filtering.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_extension_n",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "número de extensões",
            "source": "data/lake/git_files.parquet",
            "definition": "Number of distinct file extensions among clean-path file events.",
            "heuristic_or_policy": "Missing/empty extensions are represented as (none).",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "frontend_clean_file_event_share",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "proporção backend/frontend, se inferível por path",
            "source": "data/lake/git_files.parquet",
            "definition": "Share of clean file events whose path segments match frontend markers.",
            "heuristic_or_policy": "Path segment markers only; no manual architecture or GenAI integration classification.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "backend_clean_file_event_share",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "proporção backend/frontend, se inferível por path",
            "source": "data/lake/git_files.parquet",
            "definition": "Share of clean file events whose path segments match backend markers.",
            "heuristic_or_policy": "Path segment markers only; no manual architecture or GenAI integration classification.",
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_touching_commit_n_inferred",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "número de commits tocando clean paths",
            "source": "data/lake/git_files.parquet",
            "definition": "Number of distinct commits touching at least one clean-path file.",
            "heuristic_or_policy": CURRENT_POLICY_VERSION,
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "mean_clean_files_per_commit",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "diversidade de arquivos por commit",
            "source": "data/lake/git_files.parquet",
            "definition": "Mean number of distinct clean-path files touched per clean-touching commit.",
            "heuristic_or_policy": CURRENT_POLICY_VERSION,
            "manual_genai_architecture_classification": False,
        },
        {
            "metric": "clean_total_churn_inferred",
            "construct_family": "repository_structural_complexity",
            "plan_requirement": "churn total limpo",
            "source": "data/lake/git_files.parquet",
            "definition": "Total clean-path changed lines, computed as lines_added plus lines_deleted.",
            "heuristic_or_policy": CURRENT_POLICY_VERSION,
            "manual_genai_architecture_classification": False,
        },
    ]
    return pd.DataFrame(rows)


def generate() -> dict[str, Any]:
    paper_v9 = resolve_paper_v9_dir()
    repo_root = paper_v9.parent
    figures_dir = resolve_figures_dir()
    metrics_dir = resolve_metrics_dir()
    paths = {
        "evaluator": repo_root / "data" / "lake" / "evaluator_team_cuts.parquet",
        "git_files": repo_root / "data" / "lake" / "git_files.parquet",
        "m4_churn": metrics_dir / "m4_churn_magnitude.csv",
        "m8_rework": metrics_dir / "m8_rework_magnitude.csv",
        "m6a_planning": metrics_dir / "m6a_structural_planning.csv",
        "score_base": figures_dir / "rq2_score_trajectory_base_data.csv",
    }

    evaluator = pd.read_parquet(paths["evaluator"])
    files = pd.read_parquet(paths["git_files"])
    churn = pd.read_csv(paths["m4_churn"], dtype={"Semestre": str})
    rework = pd.read_csv(paths["m8_rework"], dtype={"Semestre": str})
    planning = pd.read_csv(paths["m6a_planning"], dtype={"Semestre": str})
    score_base = pd.read_csv(paths["score_base"], dtype={"Semestre": str})

    _require_columns(evaluator, REQUIRED_EVALUATOR_COLUMNS, paths["evaluator"])
    _require_columns(files, REQUIRED_FILES_COLUMNS, paths["git_files"])
    _require_columns(churn, REQUIRED_CHURN_COLUMNS, paths["m4_churn"])
    _require_columns(rework, REQUIRED_REWORK_COLUMNS, paths["m8_rework"])
    _require_columns(planning, REQUIRED_PLANNING_COLUMNS, paths["m6a_planning"])
    _require_columns(score_base, REQUIRED_BASE_COLUMNS, paths["score_base"])

    technical = _technical_complexity(evaluator)
    structural = _structural_complexity(files)
    churn_t3 = _churn_t3(churn)

    profile = (
        technical.merge(structural, on=TEAM_KEY, how="left", validate="one_to_one")
        .merge(churn_t3, on=TEAM_KEY, how="left", validate="one_to_one")
        .merge(rework[REQUIRED_REWORK_COLUMNS], on=TEAM_KEY, how="left", validate="one_to_one")
        .merge(planning[REQUIRED_PLANNING_COLUMNS], on=TEAM_KEY, how="left", validate="one_to_one")
        .merge(score_base[REQUIRED_BASE_COLUMNS], on=TEAM_KEY, how="left", validate="one_to_one")
        .sort_values(TEAM_KEY)
        .reset_index(drop=True)
    )
    if len(profile) != 14:
        raise ValueError(f"Expected 14 team-semesters, got {len(profile)}")

    for column in STRUCTURAL_COMPLEXITY_COLUMNS:
        if profile[column].isna().any():
            profile[column] = profile[column].fillna(0)

    data_path = figures_dir / f"{STEM}_data.csv"
    metrics_contract_path = figures_dir / f"{METRICS_CONTRACT_STEM}.csv"
    metadata_path = figures_dir / f"{STEM}.metadata.json"
    _atomic_csv(profile, data_path)
    metrics_contract = _metrics_contract()
    _atomic_csv(metrics_contract, metrics_contract_path)

    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_id": STEM,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "data_path": str(data_path.relative_to(repo_root)),
        "data_sha256": compute_sha256(data_path),
        "metrics_contract_path": str(metrics_contract_path.relative_to(repo_root)),
        "metrics_contract_sha256": compute_sha256(metrics_contract_path),
        "inputs": {name: str(path.relative_to(repo_root)) for name, path in paths.items()},
        "input_sha256": {name: compute_sha256(path) for name, path in paths.items()},
        "coverage": {
            "team_semesters": int(len(profile)),
            "baseline_eligible_for_rework_t3": int(profile["baseline_eligible_for_rework_t3"].fillna(False).sum()),
        },
        "construct_separation": {
            "evaluated_complexity": EVALUATED_COMPLEXITY_COLUMNS,
            "repository_structural_complexity": STRUCTURAL_COMPLEXITY_COLUMNS,
        },
        "metric_contract_summary": {
            "evaluated_complexity_metrics": int(
                metrics_contract["construct_family"].eq("evaluated_complexity").sum()
            ),
            "repository_structural_complexity_metrics": int(
                metrics_contract["construct_family"].eq("repository_structural_complexity").sum()
            ),
            "manual_genai_architecture_classification_used": bool(
                metrics_contract["manual_genai_architecture_classification"].any()
            ),
        },
        "path_heuristics": {
            "clean_path_policy": CURRENT_POLICY_VERSION,
            "frontend_markers": sorted(FRONTEND_PATH_MARKERS),
            "backend_markers": sorted(BACKEND_PATH_MARKERS),
            "architecture_layer_rule": (
                "Path segment markers classify clean file events as frontend, backend, mixed, or other_or_unclassified; "
                "this is a coarse repository-structure heuristic, not manual GenAI architecture classification."
            ),
        },
        "inference": "descriptive_confounding_profile_not_causal",
        "limitations": [
            "Evaluator technical complexity is a human assessment dimension, not inferred repository structure.",
            "Structural complexity metrics are Git/path heuristics over clean paths and do not classify architecture semantics.",
            "Frontend/backend shares depend on path names and can under-detect unconventional project layouts.",
            "The profile supports confounding/sensitivity discussion and is not a causal adjustment model.",
        ],
    }
    _atomic_json(metadata, metadata_path)
    return {
        "status": "generated",
        "data_path": str(data_path),
        "metrics_contract_path": str(metrics_contract_path),
        "metadata_path": str(metadata_path),
        "coverage": metadata["coverage"],
    }


def main() -> None:
    result = generate()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
