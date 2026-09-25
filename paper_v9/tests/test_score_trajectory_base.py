from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_score_trajectory_base import (
    CHECKPOINTS,
    EVALUATOR_SCORE_COLUMNS,
    STEM,
    generate,
)


def test_score_trajectory_base_generates_checkpoint_composite_artifacts() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"]["team_semesters"] == 14
    assert result["coverage"]["checkpoint_rows"] == {"T1": 14, "T2": 14, "T3": 14}

    figures = Path("paper_v9/figures")
    data_path = figures / f"{STEM}_data.csv"
    metadata_path = figures / f"{STEM}.metadata.json"
    assert data_path.is_file()
    assert metadata_path.is_file()

    data = pd.read_csv(data_path, dtype={"Semestre": str})
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert data.shape == (14, 8)
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
    ]
    assert data.filter(like="evaluator_score_").notna().all().all()
    assert data.filter(like="delta_score_").notna().all().all()

    assert metadata["contract_version"] == "rq2-score-trajectory-base-v1"
    assert metadata["checkpoints"] == list(CHECKPOINTS)
    assert metadata["composite_score"]["columns"] == EVALUATOR_SCORE_COLUMNS
    assert metadata["composite_score"]["aggregation"] == "unweighted_mean"
    assert "not an official global quality metric" in metadata["composite_score"]["interpretation"]
    assert metadata["inference"] == "descriptive_non_causal"
