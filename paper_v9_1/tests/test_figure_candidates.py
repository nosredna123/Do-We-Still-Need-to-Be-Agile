from __future__ import annotations

from pathlib import Path

from paper_v9.scripts.results.generate_figure_candidates import generate


def test_figure_candidates_generate_official_data_and_formats() -> None:
    result = generate()
    assert result["status"] == "generated"
    figures = Path("paper_v9/figures")
    expected = [
        "candidate_rq1_perception_panel",
        "candidate_rq2_temporal_dynamics",
        "candidate_rq3_planning_rework_profile",
        "candidate_rq3_associations_leave_one_out",
    ]
    for stem in expected:
        assert (figures / f"{stem}_data.csv").is_file()
        assert all((figures / f"{stem}.{extension}").is_file() for extension in ("pdf", "svg", "png"))