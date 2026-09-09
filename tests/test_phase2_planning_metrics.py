from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_engine():
    spec = importlib.util.spec_from_file_location(
        "phase2_planning_metrics", ROOT / "05_metric_engine.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def file_row(
    path: str,
    *,
    team: str = "TEAM_1",
    semester: str = "2025.2",
    cut: str = "T1",
    status: str = "added",
    binary: bool = False,
    added: int | None = 10,
    deleted: int | None = 2,
) -> dict[str, object]:
    return {
        "ID_Equipe": team,
        "Semestre": semester,
        "temporal_marker": cut,
        "file_path": path,
        "change_status": status,
        "is_binary": binary,
        "lines_added": added,
        "lines_deleted": deleted,
    }


def test_is_planning_artifact_uses_allowlist_and_config_path_rule() -> None:
    engine = load_engine()

    assert engine.is_planning_artifact("README.md")
    assert engine.is_planning_artifact("docs/architecture/model.drawio")
    assert engine.is_planning_artifact("requirements/schema.json")
    assert not engine.is_planning_artifact("src/config.json")
    assert not engine.is_planning_artifact("package.json")
    assert not engine.is_planning_artifact("src/main.py")


def test_compute_planning_metrics_counts_events_and_text_lines() -> None:
    engine = load_engine()
    frame = pd.DataFrame(
        [
            file_row("requirements.md", status="added", added=30, deleted=5),
            file_row("docs/design.md", status="modified", added=4, deleted=2),
            file_row("docs/diagram.pdf", status="added", binary=True, added=None, deleted=None),
            file_row("requirements.md", status="deleted", added=0, deleted=8),
            file_row("src/config.json", status="added", added=99, deleted=1),
            file_row("docs/design.md", cut="T2", status="modified", added=3, deleted=1),
            file_row("docs/design.md", cut="T3", status="renamed", added=0, deleted=0),
        ]
    )

    result = engine.compute_planning_metrics(frame)
    row = result.iloc[0]

    assert row["pi_file_count_t1"] == 3
    assert row["pi_line_delta_t1"] == 49
    assert row["pi_renamed_count_t1"] == 0
    assert row["pi_deleted_count_t1"] == 1
    assert row["pi_binary_event_count_t1"] == 1
    assert row["planning_artifact_activity_t2"] == 1
    assert row["planning_artifact_activity_t3"] == 1
    assert row["planning_rework_signal_t2_t3"] == 2
    assert bool(row["pi_available"])
    assert row["pi_observation_unit"] == "team_semester"
    assert row["pi_definition_version"] == "pi-v1"


def test_compute_planning_metrics_preserves_team_semester_keys_and_availability() -> None:
    engine = load_engine()
    frame = pd.DataFrame([file_row("src/main.py")])
    keys = pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2"},
            {"ID_Equipe": "TEAM_2", "Semestre": "2025.2"},
        ]
    )

    result = engine.compute_planning_metrics(frame, team_semester_keys=keys)
    unavailable = result.loc[result["ID_Equipe"] == "TEAM_2"].iloc[0]

    assert len(result) == 2
    assert not bool(unavailable["pi_available"])
    assert pd.isna(unavailable["pi_file_count_t1"])
    assert unavailable["pi_unavailable_reason"] == "no_observed_git_file_events"


def test_compute_planning_metrics_rejects_invalid_input() -> None:
    engine = load_engine()
    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_planning_metrics(pd.DataFrame([{"file_path": "docs/a.md"}]))


def test_write_planning_metrics_persists_contract_and_sidecar(tmp_path: Path) -> None:
    engine = load_engine()
    result = engine.compute_planning_metrics(
        pd.DataFrame([file_row("docs/requirements.md")])
    )
    output = tmp_path / "planning_metrics.parquet"

    engine.write_planning_metrics(
        result,
        output,
        source_checksum="planning-checksum-v1",
        options={"stage": "planning_metrics"},
    )

    assert output.exists()
    metadata = json.loads(
        output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "planning-metrics-v1"
    stored = pd.read_parquet(output)
    assert stored.loc[0, "pi_observation_unit"] == "team_semester"


def test_write_planning_metrics_refuses_stale_overwrite(tmp_path: Path) -> None:
    engine = load_engine()
    result = engine.compute_planning_metrics(
        pd.DataFrame([file_row("docs/requirements.md")])
    )
    output = tmp_path / "planning_metrics.parquet"
    engine.write_planning_metrics(
        result,
        output,
        source_checksum="planning-checksum-v1",
        options={},
    )

    with pytest.raises(ValueError, match="immutable"):
        engine.write_planning_metrics(
            result,
            output,
            source_checksum="planning-checksum-v2",
            options={},
        )