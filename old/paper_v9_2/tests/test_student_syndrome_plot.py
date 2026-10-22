from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_student_syndrome_plot import CHURN_STEM, STEM, generate


def test_student_syndrome_plot_generates_tiered_final_window_artifacts() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"] == {
        "high_evaluator_good_planning_n": 4,
        "lower_or_weaker_planning_n": 10,
        "team_semesters": 14,
        "window_count": 7,
    }

    figures = Path("paper_v9/figures")
    assert all((figures / f"{STEM}.{extension}").is_file() for extension in ("pdf", "svg", "png"))
    assert (figures / f"{STEM}_data.csv").is_file()
    assert (figures / f"{STEM}_summary.csv").is_file()
    assert (figures / f"{STEM}.metadata.json").is_file()

    data = pd.read_csv(figures / f"{STEM}_data.csv", dtype={"Semestre": str})
    summary = pd.read_csv(figures / f"{STEM}_summary.csv")
    metadata = json.loads((figures / f"{STEM}.metadata.json").read_text(encoding="utf-8"))

    assert data[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
    assert sorted(data["window_end_day"].unique().tolist()) == [-6, -5, -4, -3, -2, -1, 0]
    assert summary.shape[0] == 14
    assert metadata["inference"] == "descriptive_non_causal"
    assert metadata["activity_normalization"].startswith("Each team-semester sums to 100%")

    assert all((figures / f"{CHURN_STEM}.{extension}").is_file() for extension in ("pdf", "svg", "png"))
    assert (figures / f"{CHURN_STEM}_data.csv").is_file()
    assert (figures / f"{CHURN_STEM}_summary.csv").is_file()
    assert (figures / f"{CHURN_STEM}.metadata.json").is_file()

    churn_data = pd.read_csv(figures / f"{CHURN_STEM}_data.csv", dtype={"Semestre": str})
    churn_summary = pd.read_csv(figures / f"{CHURN_STEM}_summary.csv")
    churn_metadata = json.loads((figures / f"{CHURN_STEM}.metadata.json").read_text(encoding="utf-8"))

    assert churn_data[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 13
    assert sorted(churn_data["window_end_day"].unique().tolist()) == [-6, -5, -4, -3, -2, -1, 0]
    assert churn_summary.shape[0] == 14
    assert churn_metadata["activity_metric"] == "clean_source_or_test_changed_lines"
    assert churn_metadata["coverage"]["excluded_zero_clean_churn_team_semesters"] == [
        {"ID_Equipe": "TEAM_08", "Semestre": "2025.2"}
    ]
