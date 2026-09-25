from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_planning_concentration_quadrants import (
    CHURN_STEM,
    COMMIT_STEM,
    METADATA_STEM,
    SUMMARY_STEM,
    generate,
)


def test_planning_concentration_quadrants_generate_expected_artifacts() -> None:
    result = generate()

    assert result["status"] == "generated"
    figures = Path("paper_v9/figures")
    metadata_path = figures / f"{METADATA_STEM}.metadata.json"
    summary_path = figures / f"{SUMMARY_STEM}.csv"
    assert metadata_path.is_file()
    assert summary_path.is_file()

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    summary = pd.read_csv(summary_path)
    assert metadata["contract_version"] == "rq2-planning-concentration-quadrants-v1"
    assert metadata["inference"] == "descriptive_non_causal"
    assert metadata["summary_path"] == f"paper_v9/figures/{SUMMARY_STEM}.csv"
    assert set(summary["activity_metric"]) == {"commits", "clean_source_or_test_changed_lines"}
    assert summary.groupby("activity_metric")["team_semester_n"].sum().to_dict() == {
        "clean_source_or_test_changed_lines": 14,
        "commits": 14,
    }
    assert summary["team_semester_denominator"].eq(14).all()
    assert summary["small_n_flag"].isin([True, False]).all()
    assert "mean_clean_rework_churn_t3" in summary.columns

    for stem in (COMMIT_STEM, CHURN_STEM):
        assert all((figures / f"{stem}.{extension}").is_file() for extension in ("pdf", "svg", "png"))
        data_path = figures / f"{stem}_data.csv"
        assert data_path.is_file()

        data = pd.read_csv(data_path, dtype={"Semestre": str})
        assert data[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
        assert data["planning_scope_log1p_t1"].ge(0).all()
        assert data["final7_share_pct"].between(0, 100).all()
        assert data["evaluator_score_t3"].notna().all()
        assert data["planning_concentration_quadrant"].notna().all()
        assert metadata["outputs"][stem]["team_semesters"] == 14
