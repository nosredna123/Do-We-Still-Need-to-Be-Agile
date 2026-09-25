from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_operational_regularity import STEM, generate


def test_operational_regularity_generates_expected_data_contract() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"]["team_semesters"] == 14

    figures = Path("paper_v9/figures")
    data_path = figures / f"{STEM}_data.csv"
    metadata_path = figures / f"{STEM}.metadata.json"
    assert data_path.is_file()
    assert metadata_path.is_file()

    data = pd.read_csv(data_path, dtype={"Semestre": str})
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert data[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
    expected_columns = {
        "active_day_count",
        "project_span_days",
        "active_day_share",
        "max_inactivity_gap_days",
        "median_inactivity_gap_days",
        "commit_weekly_cv",
        "clean_churn_weekly_cv",
        "temporal_entropy_commits",
        "temporal_entropy_clean_churn",
        "final7_commit_share_pct",
        "final7_clean_churn_share_pct",
        "author_count",
        "max_author_share",
        "author_gini",
    }
    assert expected_columns.issubset(data.columns)
    assert data["project_span_days"].ge(data["active_day_count"]).all()
    assert data["active_day_share"].between(0, 1).all()
    assert data["temporal_entropy_commits"].between(0, 1).all()
    assert data["temporal_entropy_clean_churn"].between(0, 1).all()
    assert data[["commit_weekly_cv", "clean_churn_weekly_cv"]].ge(0).all().all()
    assert data[["final7_commit_share_pct", "final7_clean_churn_share_pct"]].apply(
        lambda column: column.between(0, 100).all()
    ).all()
    assert data["author_count"].ge(1).all()
    assert data["max_author_share"].between(0, 1).all()
    assert data["author_gini"].between(0, 1).all()

    assert metadata["contract_version"] == "rq2-operational-regularity-v1"
    assert metadata["coverage"]["team_semesters"] == 14
    assert metadata["separation_of_constructs"].startswith("Regularity metrics describe")
    assert "commit_weekly_cv" in metadata["formulas"]
    assert metadata["inference"] == "descriptive_non_causal"
