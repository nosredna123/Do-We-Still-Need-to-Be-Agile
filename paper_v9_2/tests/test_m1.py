from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.metrics.m1_rq1_perception_panel import QUESTION_ORDER, generate


def test_m1_real_outputs_are_separate_and_complete() -> None:
    result = generate()
    assert result["status"] in {"generated", "resumed"}
    metrics = Path("paper_v9/data/metrics")
    long = pd.read_csv(metrics / "m1_rq1_perception_panel_long.csv")
    assert len(long) == 36
    assert set(long["perception_family"]) == set(QUESTION_ORDER)
    assert long["coverage"].eq(1.0).all()
    assert long[["median", "q1", "q3", "iqr"]].notna().all().all()
    assert long["iqr"].ge(0).all()
    distribution = pd.read_csv(metrics / "m1_rq1_perception_distribution.csv")
    assert distribution["category"].between(0, 4).all()
    assert distribution["share"].between(0, 1).all()
    assert long["measurement_status"].eq("available").all()
    assert not long.duplicated(["Semestre", "temporal_marker", "perception_family"]).any()

    metadata = json.loads(
        (metrics / "m1_rq1_perception_panel.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "success"
    assert metadata["unavailable_not_measured"] == [
        "individual_T1_T3_panel",
        "team_semester",
    ]
    assert metadata["available_and_extracted"] == [
        "real_ai_use_frequency",
        "real_ai_use_tasks",
        "real_ai_use_tools",
        "prior_ai_project_experience",
        "autonomy_tool_balance",
    ]
    assert metadata["exploratory_unvalidated"] == ["career_impact_topics"]
    assert metadata["v8_comparison"]["max_absolute_difference"] < 1e-12