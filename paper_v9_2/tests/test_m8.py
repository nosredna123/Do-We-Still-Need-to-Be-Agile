from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.metrics.m8_clean_rework import generate


def test_m8_real_outputs_have_baseline_conditioned_grain() -> None:
    result = generate(force=True)
    assert result["status"] == "generated"
    metrics = Path("paper_v9/data/metrics")
    magnitude = pd.read_csv(metrics / "m8_rework_magnitude.csv", dtype={"Semestre": str})
    participation = pd.read_csv(metrics / "m8_rework_participation.csv", dtype={"Semestre": str})
    trajectory = pd.read_csv(metrics / "m8_rework_trajectory.csv", dtype={"Semestre": str})
    eligibility = pd.read_csv(metrics / "m8_baseline_eligibility.csv", dtype={"Semestre": str})
    metadata = json.loads((metrics / "m8_clean_rework.metadata.json").read_text(encoding="utf-8"))

    assert len(magnitude) == 14
    assert len(participation) == 14
    assert len(eligibility) == 14
    assert len(trajectory) == 406
    assert trajectory.groupby(["ID_Equipe", "Semestre"]).size().eq(29).all()
    assert magnitude["clean_rework_churn_t3"].ge(0).all()
    assert magnitude["clean_deferred_churn_t3"].ge(0).all()
    assert magnitude.loc[~magnitude["baseline_eligible_for_rework_t3"], "clean_rework_churn_t3"].eq(0).all()
    assert magnitude["clean_rework_ratio_t3"].dropna().between(0, 1).all()
    assert trajectory["clean_rework_churn_7d"].ge(0).all()
    assert metadata["policy_version"] == "code-churn-metrics-v2"
    assert metadata["coverage"]["trajectory_rows"] == 406


def test_m8_resume_reuses_current_outputs() -> None:
    assert generate()["status"] == "resumed"