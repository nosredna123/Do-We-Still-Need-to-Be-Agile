from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_student_syndrome_full_period_plots import (
    CHURN_STEM,
    COMMIT_STEM,
    CONCENTRATION_STEM,
    generate,
)


def test_student_syndrome_full_period_plots_generate_expected_artifacts() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"]["team_semesters"] == 14
    assert result["coverage"]["commit_windows"] > 100
    assert result["coverage"]["clean_churn_windows"] > 100

    figures = Path("paper_v9/figures")
    for stem in (COMMIT_STEM, CHURN_STEM):
        assert all((figures / f"{stem}.{extension}").is_file() for extension in ("pdf", "svg", "png"))
        assert (figures / f"{stem}_data.csv").is_file()
        assert (figures / f"{stem}_summary.csv").is_file()
        assert (figures / f"{stem}.metadata.json").is_file()

        data = pd.read_csv(figures / f"{stem}_data.csv", dtype={"Semestre": str})
        summary = pd.read_csv(figures / f"{stem}_summary.csv")
        metadata = json.loads((figures / f"{stem}.metadata.json").read_text(encoding="utf-8"))

        assert data[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
        assert data["window_end_day"].max() == 0
        assert summary["window_end_day"].nunique() == data["window_end_day"].nunique()
        assert metadata["config"]["rolling_normalization"].endswith("equals 100%.")
        assert {row["checkpoint"] for row in metadata["checkpoint_stats"]} == {"T1", "T2", "T3"}

    assert all((figures / f"{CONCENTRATION_STEM}.{extension}").is_file() for extension in ("pdf", "svg", "png"))
    concentration = pd.read_csv(figures / f"{CONCENTRATION_STEM}_data.csv", dtype={"Semestre": str})
    assert set(concentration["activity_metric"]) == {"commits", "clean_source_or_test_changed_lines"}
    assert concentration["final7_share_pct"].between(0, 100).all()
