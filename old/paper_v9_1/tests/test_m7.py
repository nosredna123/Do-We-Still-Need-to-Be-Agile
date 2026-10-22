from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.metrics.m7_repository_inactivity import generate


def test_m7_real_outputs_have_expected_grain_and_coverage() -> None:
    result = generate(force=True)
    assert result["status"] == "generated"
    metrics = Path("paper_v9/data/metrics")
    trajectory = pd.read_csv(metrics / "m7_inactivity_trajectory.csv", dtype={"Semestre": str})
    pattern = pd.read_csv(metrics / "m7_inactivity_pattern.csv", dtype={"Semestre": str})
    checkpoint = pd.read_csv(metrics / "m7_checkpoint_inactivity.csv", dtype={"Semestre": str})
    metadata = json.loads((metrics / "m7_repository_inactivity.metadata.json").read_text(encoding="utf-8"))

    assert len(trajectory) == 994
    assert len(checkpoint) == 42
    assert len(pattern) == 14
    assert trajectory.groupby(["ID_Equipe", "Semestre"]).size().eq(71).all()
    assert set(checkpoint["temporal_marker"]) == {"T1", "T2", "T3"}
    assert trajectory["commit_n_7d"].ge(0).all()
    assert trajectory["repository_inactive_7d"].isin([True, False]).all()
    assert set(pattern["inactivity_pattern"]) <= {"never_inactive", "t1_only", "intermittent", "persistent_all_checkpoints"}
    assert metadata["status"] == "success"
    assert metadata["planning_claim"] == "not_identifiable_from_repository_inactivity"
    assert metadata["coverage"]["daily_rows"] == 994


def test_m7_resume_reuses_current_outputs() -> None:
    assert generate()["status"] == "resumed"