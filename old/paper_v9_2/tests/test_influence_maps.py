from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_influence_maps import (
    DIRECTIONAL_SUMMARY_STEM,
    HEATMAP_MATRIX_STEM,
    RELATIONSHIPS,
    STEM,
    generate,
)


def test_influence_map_generates_leave_one_out_contract() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"] == {
        "relationships": len(RELATIONSHIPS),
        "removed_team_semesters": 14,
        "task_4_2_requirements": 8,
        "rows": len(RELATIONSHIPS) * 14,
    }

    figures = Path("paper_v9/figures")
    data = pd.read_csv(figures / f"{STEM}_data.csv", dtype={"removed_Semestre": str})
    heatmap = pd.read_csv(figures / f"{HEATMAP_MATRIX_STEM}.csv")
    summary = pd.read_csv(figures / f"{DIRECTIONAL_SUMMARY_STEM}.csv")
    metadata = json.loads((figures / f"{STEM}.metadata.json").read_text(encoding="utf-8"))

    assert len(data) == len(RELATIONSHIPS) * 14
    assert data["relationship_id"].nunique() == len(RELATIONSHIPS)
    assert data[["removed_ID_Equipe", "removed_Semestre"]].drop_duplicates().shape[0] == 14
    assert {"available", "unavailable"}.issuperset(set(data["availability_status"]))
    available = data["availability_status"].eq("available")
    assert data.loc[available, "abs_rho_delta_from_full"].ge(0).all()

    assert len(heatmap) == 14
    assert set(summary["relationship_id"]) == {relationship["relationship_id"] for relationship in RELATIONSHIPS}
    assert summary["sign_preservation_share"].between(0, 1).all()
    assert summary["available_leave_one_out_rows"].le(summary["total_leave_one_out_rows"]).all()

    assert metadata["contract_version"] == "rq3-influence-map-v1"
    assert metadata["inference"] == "descriptive_directional_robustness_not_confirmatory"
    assert metadata["coverage"]["relationships"] == len(RELATIONSHIPS)
    assert metadata["coverage"]["removed_team_semesters"] == 14
    assert "not confirmatory statistical tests" in " ".join(metadata["limitations"])
    assert all((figures / f"{STEM}.{extension}").is_file() for extension in ("pdf", "svg", "png"))
