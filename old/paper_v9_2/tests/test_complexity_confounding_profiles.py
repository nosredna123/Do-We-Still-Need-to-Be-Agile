from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_complexity_confounding_profiles import (
    CONFOUNDING_SUMMARY_STEM,
    FINAL_CONCENTRATION_STEM,
    PLANNING_REWORK_OVERLAY_STEM,
    STEM,
    TECH_REWORK_STEM,
    generate,
)


def test_complexity_confounding_profiles_generate_expected_artifacts() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"] == {"team_semesters": 14, "baseline_eligible_for_rework_t3": 12}

    figures = Path("paper_v9/figures")
    data = pd.read_csv(figures / f"{STEM}_data.csv", dtype={"Semestre": str})
    summary = pd.read_csv(figures / f"{CONFOUNDING_SUMMARY_STEM}.csv")
    metadata = json.loads((figures / f"{STEM}.metadata.json").read_text(encoding="utf-8"))

    assert data[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
    expected_columns = {
        "technical_complexity_mean_t1",
        "technical_complexity_mean_t2",
        "technical_complexity_mean_t3",
        "delta_technical_complexity_t3_minus_t1",
        "clean_distinct_file_n",
        "clean_distinct_directory_n",
        "clean_max_path_depth",
        "clean_extension_n",
        "frontend_clean_file_event_share",
        "backend_clean_file_event_share",
        "clean_rework_churn_t3",
        "clean_rework_ratio_t3",
        "final7_commit_share_pct",
        "final7_clean_churn_share_pct",
    }
    assert expected_columns.issubset(data.columns)
    assert data["technical_complexity_mean_t3"].notna().all()
    assert data["clean_max_path_depth"].ge(0).all()
    assert data[["frontend_clean_file_event_share", "backend_clean_file_event_share"]].apply(
        lambda column: column.between(0, 1).all()
    ).all()
    assert data["baseline_eligible_for_rework_t3"].sum() == 12

    assert set(summary["relationship"]) == {
        "planning_scope_to_clean_rework_churn",
        "planning_scope_to_clean_rework_ratio",
        "planning_scope_to_final7_commit_concentration",
        "planning_scope_to_final7_clean_churn_concentration",
        "final7_commit_concentration_to_clean_rework_churn",
        "final7_clean_churn_concentration_to_clean_rework_churn",
    }
    assert summary["minimum_n_for_rho"].eq(4).all()

    assert metadata["contract_version"] == "rq3-complexity-profile-v1"
    assert metadata["inference"] == "descriptive_confounding_profile_not_causal"
    assert metadata["coverage"] == {"team_semesters": 14, "baseline_eligible_for_rework_t3": 12}
    assert "not a causal adjustment model" in " ".join(metadata["limitations"])

    for stem in (TECH_REWORK_STEM, FINAL_CONCENTRATION_STEM, PLANNING_REWORK_OVERLAY_STEM):
        assert (figures / f"{stem}_data.csv").is_file()
        assert all((figures / f"{stem}.{extension}").is_file() for extension in ("pdf", "svg", "png"))
