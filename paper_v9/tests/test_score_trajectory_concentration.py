from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_score_trajectory_concentration import (
    CHURN_STEM,
    COMMIT_STEM,
    METADATA_STEM,
    generate,
)


def test_score_trajectory_concentration_generates_scatter_artifacts() -> None:
    result = generate()

    assert result["status"] == "generated"

    figures = Path("paper_v9/figures")
    metadata_path = figures / f"{METADATA_STEM}.metadata.json"
    assert metadata_path.is_file()

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert metadata["contract_version"] == "rq2-score-trajectory-concentration-v1"
    assert metadata["delta_threshold"] == 0.125
    assert metadata["inference"] == "descriptive_non_causal"

    for stem in (COMMIT_STEM, CHURN_STEM):
        assert all((figures / f"{stem}.{extension}").is_file() for extension in ("pdf", "svg", "png"))
        data_path = figures / f"{stem}_data.csv"
        assert data_path.is_file()

        data = pd.read_csv(data_path, dtype={"Semestre": str})
        assert data[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
        assert data["delta_score_t3_minus_t1"].notna().all()
        assert pd.api.types.is_numeric_dtype(data["delta_score_t3_minus_t1"])
        assert data["final7_share_pct"].between(0, 100).all()
        assert sorted(data["planning_scope_tier"].unique().tolist()) == [
            "high_repository_visible_planning",
            "lower_repository_visible_planning",
        ]
        assert data["quadrant"].notna().all()
        assert metadata["outputs"][stem]["team_semesters"] == 14
        assert metadata["outputs"][stem]["quadrant_counts_by_planning_tier"]
