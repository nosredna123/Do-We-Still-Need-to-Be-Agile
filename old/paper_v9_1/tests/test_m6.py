from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.metrics.m6_structural_planning import generate


def test_m6a_real_outputs_preserve_structural_planning_and_absence() -> None:
    result = generate(force=True)
    assert result["status"] == "generated"
    metrics = Path("paper_v9/data/metrics")
    output = pd.read_csv(metrics / "m6a_structural_planning.csv", dtype={"Semestre": str})
    metadata = json.loads((metrics / "m6_structural_planning.metadata.json").read_text(encoding="utf-8"))

    assert len(output) == 14
    assert output.duplicated(["ID_Equipe", "Semestre"]).sum() == 0
    assert output["pi_available"].eq(True).all()
    assert output["measurement_status"].eq("available").all()
    assert output["planning_artifact_present_t1"].equals(output["pi_file_count_t1"].gt(0))
    assert output["planning_scope_log1p_t1"].ge(0).all()
    assert "t1_planning_score" not in output.columns
    assert metadata["status"] == "success"
    assert metadata["rq"] == "RQ3"
    assert metadata["llm_calls_required"] is False
    assert metadata["absence_policy"] == "report_separately_not_as_score_floor"


def test_m6a_resume_reuses_current_outputs() -> None:
    result = generate()
    assert result["status"] == "resumed"