"""Generate deterministic M6a structural planning evidence for T1."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "m6a-structural-planning-v1"
SOURCE_DEFINITION_VERSION = "pi-v1"
TEAM_KEY = ["ID_Equipe", "Semestre"]
REQUIRED_COLUMNS = {
    "ID_Equipe", "Semestre", "pi_available", "pi_unavailable_reason",
    "pi_file_count_t1", "pi_line_delta_t1", "pi_renamed_count_t1",
    "pi_deleted_count_t1", "pi_binary_event_count_t1", "planning_artifact_activity_t1",
    "pi_observation_unit", "pi_definition_version",
}
NONNEGATIVE_COLUMNS = [
    "pi_file_count_t1", "pi_line_delta_t1", "pi_renamed_count_t1",
    "pi_deleted_count_t1", "pi_binary_event_count_t1", "planning_artifact_activity_t1",
]


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def _atomic_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    os.replace(temporary, path)


def _load_planning(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"M6 planning contract not found: {path}")
    frame = pd.read_parquet(path)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"M6 planning contract is missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("M6 planning contract is empty")
    if frame.duplicated(TEAM_KEY).any():
        raise ValueError("M6 planning contract contains duplicate team-semester keys")
    if frame[TEAM_KEY].isna().any().any():
        raise ValueError("M6 planning contract contains null team-semester keys")
    if frame["pi_definition_version"].ne(SOURCE_DEFINITION_VERSION).any():
        raise ValueError(f"M6 planning contract must use definition {SOURCE_DEFINITION_VERSION}")
    if frame["pi_observation_unit"].ne("team_semester").any():
        raise ValueError("M6 planning contract has an unexpected observation unit")
    for column in NONNEGATIVE_COLUMNS:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any() or values.lt(0).any():
            raise ValueError(f"M6 planning contract has invalid nonnegative field: {column}")
    if frame["pi_available"].isna().any():
        raise ValueError("M6 planning contract has null availability values")
    return frame.copy()


def _build_output(planning: pd.DataFrame) -> pd.DataFrame:
    output = planning[[
        "ID_Equipe", "Semestre", "pi_available", "pi_unavailable_reason",
        "pi_file_count_t1", "pi_line_delta_t1", "pi_renamed_count_t1",
        "pi_deleted_count_t1", "pi_binary_event_count_t1", "planning_artifact_activity_t1",
        "pi_observation_unit", "pi_definition_version",
    ]].copy()
    output["planning_artifact_present_t1"] = output["pi_file_count_t1"].gt(0)
    output["planning_scope_log1p_t1"] = output["pi_line_delta_t1"].map(lambda value: float(__import__("math").log1p(value)))
    output["measurement_status"] = output["pi_available"].map({True: "available", False: "unavailable_not_measured"})
    output["analysis_level"] = "team_semester"
    return output.sort_values(TEAM_KEY).reset_index(drop=True)


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir()
    metrics_dir = resolve_metrics_dir()
    planning_path = root.parent / "data" / "analysis" / "planning_metrics.parquet"
    input_hash = compute_sha256(planning_path)
    config = {"contract_version": CONTRACT_VERSION, "source_definition_version": SOURCE_DEFINITION_VERSION, "t1_checkpoint": "T1"}
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    names = ["m6a_structural_planning.csv", "m6_structural_planning.metadata.json"]
    paths = [metrics_dir / name for name in names]
    if not force and all(path.is_file() for path in paths):
        metadata = json.loads(paths[-1].read_text(encoding="utf-8"))
        if metadata.get("input_sha256") == input_hash and metadata.get("config_sha256") == config_hash:
            return {"status": "resumed", "artifacts": [str(path) for path in paths]}

    planning = _load_planning(planning_path)
    output = _build_output(planning)
    metadata = {
        "status": "success", "gate_status": "pending", "contract_version": CONTRACT_VERSION,
        "metric_definition_version": CONTRACT_VERSION, "source_definition_version": SOURCE_DEFINITION_VERSION,
        "input_sha256": input_hash, "config_sha256": config_hash, "rq": "RQ3",
        "unit_of_analysis": "team_semester", "source_contract": "data/analysis/planning_metrics.parquet",
        "checkpoint": "T1", "llm_calls_required": False, "inference": "exploratory_descriptive",
        "absence_policy": "report_separately_not_as_score_floor",
        "coverage": {"team_semester_n": int(len(output)), "available_n": int(output["pi_available"].sum()), "unavailable_not_measured_n": int((~output["pi_available"]).sum())},
        "limitations": ["file presence and line scope are observable structural signals, not semantic planning quality", "absence of a repository artifact does not prove absence of planning outside the repository", "M6b textual content extraction is a separate gated task"],
        "artifacts": names,
    }
    _atomic_csv(output, paths[0])
    _atomic_json(metadata, paths[1])
    if verbose:
        print(json.dumps(metadata, indent=2, sort_keys=True))
    return {"status": "generated", "artifacts": [str(path) for path in paths]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the v9 M6a structural planning metric")
    parser.add_argument("--force", action="store_true", help="Regenerate existing artifacts")
    parser.add_argument("--verbose", action="store_true", help="Print generated metadata")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2))


if __name__ == "__main__":
    main()