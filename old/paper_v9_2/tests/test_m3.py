from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.metrics.m3_author_activity_dynamics import generate


def test_m3_real_outputs_have_expected_grains_and_boundaries() -> None:
    result = generate()
    assert result["status"] in {"generated", "resumed"}
    metrics = Path("paper_v9/data/metrics")
    participation = pd.read_csv(metrics / "m3_author_activity_participation.csv")
    concentration = pd.read_csv(metrics / "m3_author_concentration.csv")
    rolling = pd.read_csv(metrics / "m3_activity_rolling_7day.csv")
    pooled = pd.read_csv(metrics / "m3_activity_rolling_7day_pooled.csv")

    assert len(participation) == 14
    assert len(concentration) == 28
    assert len(rolling) == 14 * 29
    assert len(pooled) == 29
    assert "Semestre" not in pooled.columns
    assert set(pooled["window_end_day"]) == set(range(-21, 8))
    assert pooled["team_semester_n"].eq(14).all()
    assert participation[["pre_share", "post_share", "final_window_share"]].apply(
        lambda column: column.dropna().between(0, 1).all()
    ).all()
    assert concentration["phase"].isin(["pre", "post"]).all()
    assert concentration.loc[
        concentration["measurement_status"].eq("no_observed_activity"),
        ["max_author_share", "author_gini"],
    ].isna().all().all()
    assert set(rolling["window_end_day"]) == set(range(-21, 8))
    assert not set(concentration.columns).intersection({"author_email", "author_name"})

    metadata = json.loads(
        (metrics / "m3_author_activity_dynamics.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "success"
    assert metadata["gate_status"] == "approved"
    assert metadata["gate_approved_on"] == "2026-09-24"
    assert metadata["rq"] == "RQ2"
    assert metadata["coverage"]["team_semesters"] == 14
    assert metadata["anchor"] == "last T3 evaluator vote"
