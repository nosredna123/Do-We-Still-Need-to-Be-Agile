from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.metrics.m9_structured_associations import generate


def test_m9_real_outputs_are_stratified_and_descriptive() -> None:
    result = generate(force=True)
    assert result["status"] == "generated"
    metrics = Path("paper_v9/data/metrics")
    magnitude = pd.read_csv(metrics / "m9_planning_vs_rework_m6a_m8a.csv")
    ratio = pd.read_csv(metrics / "m9_planning_vs_rework_m6a_m8b_eligible_stratum.csv")
    outcomes = pd.read_csv(metrics / "m9_planning_vs_outcomes_m6a_t3.csv")
    m6b = pd.read_csv(metrics / "m9_planning_vs_outcomes_m6b_t3_if_approved.csv")
    loo = pd.read_csv(metrics / "m9_leave_one_out_intervals.csv")
    metadata = json.loads((metrics / "m9_structured_associations.metadata.json").read_text(encoding="utf-8"))

    assert len(magnitude) == 2
    assert len(ratio) == 2
    assert len(outcomes) == 8
    assert len(m6b) == 30
    assert m6b["analysis_id"].eq("m6b_structured_content").all()
    assert len(loo) == 52
    assert set(magnitude["analysis_id"]) == {"all_team_semesters"}
    assert set(ratio["analysis_id"]) == {"baseline_eligible_only"}
    assert loo["n_remaining"].ge(3).all()
    assert metadata["coverage"] == {"team_semesters": 14, "baseline_eligible": 12, "m6b_observed": 9, "leave_one_out_rows": 52}
    assert metadata["m6b_status"] == "approved_human_review"
    assert metadata["m7_used_as_predictor"] is False


def test_m9_resume_reuses_current_outputs() -> None:
    assert generate()["status"] == "resumed"