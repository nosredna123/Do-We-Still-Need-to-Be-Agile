from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_score_trajectory_base import (
    CHECKPOINTS,
    EVALUATOR_SCORE_COLUMNS,
    GROUP_COUNTS_STEM,
    STEM,
    generate,
)


def test_score_trajectory_base_generates_checkpoint_composite_artifacts() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"]["team_semesters"] == 14
    assert result["coverage"]["checkpoint_rows"] == {"T1": 14, "T2": 14, "T3": 14}
    assert result["coverage"]["final7_concentration"]["commit_team_semesters"] == 14
    assert result["coverage"]["final7_concentration"]["clean_churn_team_semesters"] == 14
    assert result["coverage"]["final7_concentration"]["zero_final7_clean_churn_team_semesters"] == [
        {"ID_Equipe": "TEAM_08", "Semestre": "2025.2"}
    ]
    assert result["score_trajectory_group_counts"] == [
        {"score_trajectory_group": "declined", "team_semester_n": 2, "team_semester_pct": 100 / 7},
        {"score_trajectory_group": "improved", "team_semester_n": 8, "team_semester_pct": 400 / 7},
        {"score_trajectory_group": "stable", "team_semester_n": 4, "team_semester_pct": 200 / 7},
    ]

    figures = Path("paper_v9/figures")
    data_path = figures / f"{STEM}_data.csv"
    group_counts_path = figures / f"{GROUP_COUNTS_STEM}.csv"
    metadata_path = figures / f"{STEM}.metadata.json"
    assert data_path.is_file()
    assert group_counts_path.is_file()
    assert metadata_path.is_file()

    data = pd.read_csv(data_path, dtype={"Semestre": str})
    group_counts = pd.read_csv(group_counts_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert data.shape == (14, 14)
    assert data[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
    assert list(data.columns) == [
        "ID_Equipe",
        "Semestre",
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
    assert data.filter(like="evaluator_score_").notna().all().all()
    assert data.filter(like="delta_score_").notna().all().all()
    assert sorted(data["score_trajectory_group"].unique().tolist()) == ["declined", "improved", "stable"]
    assert sorted(data["planning_scope_tier"].unique().tolist()) == [
        "high_repository_visible_planning",
        "lower_repository_visible_planning",
    ]
    assert data["planning_scope_tier"].value_counts().to_dict() == {
        "high_repository_visible_planning": 7,
        "lower_repository_visible_planning": 7,
    }
    assert data["final7_commit_share_pct"].between(0, 100).all()
    assert data["final7_clean_churn_share_pct"].between(0, 100).all()
    zero_clean = data.loc[data["final7_clean_churn_share_pct"].eq(0), ["ID_Equipe", "Semestre"]]
    assert zero_clean.to_dict("records") == [{"ID_Equipe": "TEAM_08", "Semestre": "2025.2"}]
    assert group_counts["team_semester_n"].sum() == 14

    assert metadata["contract_version"] == "rq2-score-trajectory-base-v3"
    assert metadata["checkpoints"] == list(CHECKPOINTS)
    assert metadata["composite_score"]["columns"] == EVALUATOR_SCORE_COLUMNS
    assert metadata["composite_score"]["aggregation"] == "unweighted_mean"
    assert "not an official global quality metric" in metadata["composite_score"]["interpretation"]
    assert metadata["score_trajectory_grouping"]["fallback_applied"] is True
    assert metadata["score_trajectory_grouping"]["threshold"] == 0.125
    assert metadata["score_trajectory_grouping"]["final_group_counts"] == {
        "declined": 2,
        "improved": 8,
        "stable": 4,
    }
    assert metadata["repository_visible_planning"]["planning_scope_log1p_t1_median"] == 1.791759469228055
    assert metadata["repository_visible_planning"]["tier_values"] == [
        "high_repository_visible_planning",
        "lower_repository_visible_planning",
    ]
    assert "not a semantic planning quality rating" in metadata["repository_visible_planning"]["interpretation"]
    assert metadata["final7_concentration"]["commit_column"] == "final7_commit_share_pct"
    assert metadata["final7_concentration"]["clean_churn_column"] == "final7_clean_churn_share_pct"
    assert metadata["final7_concentration"]["zero_final7_clean_churn_team_semesters"] == [
        {"ID_Equipe": "TEAM_08", "Semestre": "2025.2"}
    ]
    assert metadata["inference"] == "descriptive_non_causal"
