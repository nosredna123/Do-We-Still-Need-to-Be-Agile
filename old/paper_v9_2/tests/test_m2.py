from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.metrics.m2_role_perception import generate, ROLE_ORDER


def test_m2_real_outputs_are_role_specific_and_complete() -> None:
    result = generate()
    assert result["status"] in {"generated", "resumed"}
    metrics = Path("paper_v9/data/metrics")
    distributions = pd.read_csv(metrics / "m2_role_perception_distributions.csv")
    summary = pd.read_csv(metrics / "m2_role_perception_by_team_semester.csv")
    paired = pd.read_csv(metrics / "m2_role_perception_paired_t1_t3.csv")
    assert set(distributions["role"]) == set(ROLE_ORDER)
    assert set(summary["role"]) == set(ROLE_ORDER)
    assert distributions["score"].between(1, 5).all()
    assert distributions["share"].between(0, 1).all()
    assert summary[["mean", "median", "q1", "q3", "iqr"]].notna().all().all()
    assert summary["iqr"].ge(0).all()
    assert paired["pairs"].gt(0).all()

    metadata = json.loads(
        (metrics / "m2_role_perception.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "success"
    assert metadata["gate_status"] == "approved"
    assert metadata["gate_approved_on"] == "2026-09-24"
    assert metadata["interpretation"] == "perceived role disruption agreement, not objective extinction risk"
