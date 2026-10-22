from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_m5_2025_triangulation import PANEL_STEM, STEM, generate


def test_m5_2025_triangulation_generates_coverage_aware_panel() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"]["observed_semester"] == "2025.2"
    assert result["coverage"]["unavailable_semesters"] == {"2026.1": "unavailable_not_measured"}
    assert result["coverage"]["m5_team_level_measure"] is False
    assert result["coverage"]["m5_zero_filled_unavailable_semesters"] is False
    assert result["coverage"]["team_semesters"] == 9
    assert result["coverage"]["team_checkpoint_rows"] == 27

    figures = Path("paper_v9/figures")
    data_path = figures / f"{STEM}_data.csv"
    summary_path = figures / f"{STEM}_summary.csv"
    metadata_path = figures / f"{STEM}.metadata.json"
    assert data_path.is_file()
    assert summary_path.is_file()
    assert metadata_path.is_file()
    assert all((figures / f"{PANEL_STEM}.{extension}").is_file() for extension in ("pdf", "svg", "png"))

    data = pd.read_csv(data_path, dtype={"Semestre": str})
    summary = pd.read_csv(summary_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    assert data[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 9
    assert data.shape[0] == 27
    assert set(data["Semestre"]) == {"2025.2"}
    assert sorted(data["temporal_marker"].unique().tolist()) == ["T1", "T2", "T3"]
    assert data["m5_unavailable_semesters"].eq("2026.1=unavailable_not_measured").all()
    assert data["m5_analysis_scope_note"].str.contains("not a team-level measure").all()
    assert data["m5_analysis_level"].eq("global_transcript_corpus_by_temporal_marker").all()
    assert data["m5_measurement_status"].eq("available").all()
    assert data["m5_semester_coverage_status"].eq("available_transcript_corpus_2025_2").all()
    assert data["clean_churn"].ge(0).all()
    assert data["evaluator_score_composite"].between(1, 4).all()
    assert data["clean_rework_churn_t3"].ge(0).all()

    assert summary["temporal_marker"].tolist() == ["T1", "T2", "T3"]
    assert summary["m5_friction_marker_density_per_1k_tokens"].is_monotonic_increasing
    assert summary["median_clean_churn"].tolist() == [0.0, 2803.0, 5837.0]
    assert summary["baseline_eligible_rework_team_n"].eq(7).all()

    assert metadata["contract_version"] == "rq2-m5-2025-triangulation-v1"
    assert metadata["coverage"]["unavailable_semesters"] == {"2026.1": "unavailable_not_measured"}
    assert metadata["coverage"]["m5_zero_filled_unavailable_semesters"] is False
    assert metadata["inference"] == "descriptive_coverage_aware_triangulation_not_causal"
    assert PANEL_STEM in metadata["figure_outputs"]
