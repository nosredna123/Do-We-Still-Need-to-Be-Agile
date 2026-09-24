from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest

from pipeline_core import write_artifact_metadata

ROOT = Path(__file__).resolve().parent.parent


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "phase2_team_metrics", ROOT / "05_metric_engine.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contract_frame(unit_column: str) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID_Equipe": "TEAM_1",
                "Semestre": "2025.2",
                unit_column: "team_semester",
                f"{unit_column.split('_')[0]}_available": True,
                f"{unit_column.split('_')[0]}_value": 1.0,
            }
        ]
    )


def write_contract(path: Path, frame: pd.DataFrame, version: str) -> None:
    frame.to_parquet(path, index=False)
    write_artifact_metadata(
        path,
        f"{version}-input",
        contract_version=version,
        options={"stage": version},
    )


def test_consolidate_team_metrics_persists_contract_and_excludes_ie(tmp_path: Path) -> None:
    engine = load_engine()
    specs = {
        "planning": ("pi_observation_unit", "planning-metrics-v1"),
        "code_churn": ("cc_observation_unit", "code-churn-metrics-v2"),
        "technical_degradation": ("dt_observation_unit", "technical-degradation-metrics-v1"),
        "integration_friction": ("ai_observation_unit", "integration-friction-metrics-v1"),
    }
    paths = {}
    for name, (unit_column, version) in specs.items():
        path = tmp_path / f"{name}.parquet"
        write_contract(path, contract_frame(unit_column), version)
        paths[name] = path
    report = tmp_path / "phase2_contract_report.json"
    report.write_text(json.dumps({"status": "success", "contracts": {}}), encoding="utf-8")

    output = tmp_path / "team_metrics.parquet"
    result = engine.consolidate_team_metrics(
        paths,
        output_path=output,
        contract_report_path=report,
        options={"stage": "team_metrics"},
    )

    assert len(result) == 1
    assert result.loc[0, "unit_of_analysis"] == "team_semester"
    assert not any(column.startswith("ie_") for column in result.columns)
    assert output.exists()
    assert (tmp_path / "team_metrics_exclusions.json").exists()
    metadata = json.loads(
        output.with_name("team_metrics.parquet.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["contract_version"] == "team-metrics-v1"


def test_write_team_metrics_rejects_replicated_ie(tmp_path: Path) -> None:
    engine = load_engine()
    frame = pd.DataFrame(
        [{"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "unit_of_analysis": "team_semester", "ie_mean": 1.0}]
    )
    with pytest.raises(ValueError, match="replicated IE"):
        engine.write_team_metrics(
            frame,
            tmp_path / "team_metrics.parquet",
            source_checksum="team-v1",
            options={},
            exclusions={},
        )
