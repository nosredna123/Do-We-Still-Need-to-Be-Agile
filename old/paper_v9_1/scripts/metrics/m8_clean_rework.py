"""Generate M8 clean rework measures under the current M4 path policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.artifact_policy import is_clean_path
from paper_v9.scripts.common.paths import resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256
from paper_v9.scripts.common.validate_keys import assert_current_code_churn_contract

CONTRACT_VERSION = "m8-clean-rework-v1"
TEAM_KEY = ["Semestre", "ID_Equipe"]
ROLLING_OFFSETS = tuple(range(-21, 8))


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def _atomic_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    os.replace(temporary, path)


def _anchors(root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for semester in ("2025.2", "2026.1"):
        frame = pd.read_csv(root / "data" / "processed" / "forms" / semester / "avaliadores.csv")
        frame["ID_Equipe"] = frame["To which group do these scores refer?"].astype(str).str.extract(r"Group\s+(\d+)", expand=False).map(lambda value: f"TEAM_{int(value):02d}" if pd.notna(value) else None)
        frame["vote_at"] = pd.to_datetime(frame["Timestamp"], format="mixed").dt.tz_localize("America/Fortaleza")
        ranges = ("2025-12-05", "2025-12-12") if semester == "2025.2" else ("2026-06-19", "2026-06-19")
        selected = frame.loc[frame["vote_at"].dt.date.between(pd.Timestamp(ranges[0]).date(), pd.Timestamp(ranges[1]).date())]
        rows.extend(selected.groupby("ID_Equipe", as_index=False)["vote_at"].max().assign(Semestre=semester).to_dict("records"))
    result = pd.DataFrame(rows)
    if len(result) != 14 or result.duplicated(TEAM_KEY).any():
        raise ValueError(f"Expected 14 M8 T3 anchors, got {len(result)}")
    return result


def _prepare_files(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"Semestre", "ID_Equipe", "temporal_marker", "timestamp", "file_path", "file_extension", "lines_added", "lines_deleted"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"M8 file input is missing columns: {sorted(missing)}")
    result = frame.copy()
    result["timestamp"] = pd.to_datetime(result["timestamp"], utc=True)
    added = pd.to_numeric(result["lines_added"], errors="coerce")
    deleted = pd.to_numeric(result["lines_deleted"], errors="coerce")
    binary = result["is_binary"] if "is_binary" in result else pd.Series(False, index=result.index)
    invalid_nulls = added.isna().ne(deleted.isna()) | (added.isna() & ~binary.astype(bool))
    if invalid_nulls.any():
        raise ValueError("M8 file input contains unexplained null churn values")
    result["churn_lines"] = added.fillna(0) + deleted.fillna(0)
    if result["churn_lines"].lt(0).any():
        raise ValueError("M8 file input contains negative churn values")
    result["clean_included"] = result["file_path"].map(is_clean_path)
    result["marker_rank"] = result["temporal_marker"].map({"T1": 1, "T2": 2, "T3": 3})
    if result["marker_rank"].isna().any():
        raise ValueError("M8 file input contains invalid temporal markers")
    return result


def _with_origins(files: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = files.loc[files["clean_included"]]
    origins = clean.groupby(TEAM_KEY + ["file_path"], as_index=False)["marker_rank"].min().rename(columns={"marker_rank": "first_clean_marker_rank"})
    result = files.merge(origins, on=TEAM_KEY + ["file_path"], how="left", validate="many_to_one")
    result["clean_origin_type"] = result["first_clean_marker_rank"].map(lambda rank: "rework" if rank in (1, 2) else "deferred" if rank == 3 else "not_included")
    return result, origins


def _team_output(files: pd.DataFrame, universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    t3 = files.loc[files["temporal_marker"].eq("T3") & files["clean_included"]]
    summary = t3.groupby(TEAM_KEY + ["clean_origin_type"], as_index=False)["churn_lines"].sum().pivot_table(index=TEAM_KEY, columns="clean_origin_type", values="churn_lines", fill_value=0).reset_index()
    for column in ("rework", "deferred"):
        if column not in summary:
            summary[column] = 0.0
    prior = files.loc[files["first_clean_marker_rank"].isin([1, 2])].groupby(TEAM_KEY + ["file_path"]).size().groupby(level=TEAM_KEY).size().rename("prior_clean_path_n").reset_index()
    output = universe.merge(summary[TEAM_KEY + ["rework", "deferred"]], on=TEAM_KEY, how="left").merge(prior, on=TEAM_KEY, how="left")
    output[["rework", "deferred"]] = output[["rework", "deferred"]].fillna(0.0)
    output["prior_clean_path_n"] = output["prior_clean_path_n"].fillna(0).astype(int)
    output = output.rename(columns={"rework": "clean_rework_churn_t3", "deferred": "clean_deferred_churn_t3"})
    output["clean_total_churn_t3"] = output["clean_rework_churn_t3"] + output["clean_deferred_churn_t3"]
    output["baseline_eligible_for_rework_t3"] = output["prior_clean_path_n"].gt(0)
    output["clean_rework_ratio_t3"] = output["clean_rework_churn_t3"] / output["clean_total_churn_t3"].where(output["clean_total_churn_t3"].ne(0))
    output["measurement_status"] = output["baseline_eligible_for_rework_t3"].map({True: "baseline_eligible", False: "baseline_not_observed"})
    return output.sort_values(TEAM_KEY).reset_index(drop=True), prior


def _trajectory(files: pd.DataFrame, anchors: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for anchor in anchors.to_dict("records"):
        team = files.loc[(files["Semestre"] == anchor["Semestre"]) & (files["ID_Equipe"] == anchor["ID_Equipe"]) & files["clean_included"] & files["clean_origin_type"].eq("rework")]
        t3 = pd.Timestamp(anchor["vote_at"]).tz_convert("UTC")
        for offset in ROLLING_OFFSETS:
            end = t3 + pd.Timedelta(days=offset)
            current = team.loc[team["timestamp"].ge(end - pd.Timedelta(days=7)) & team["timestamp"].lt(end)]
            rows.append({"Semestre": anchor["Semestre"], "ID_Equipe": anchor["ID_Equipe"], "window_end_day_relative_to_t3": offset, "clean_rework_churn_7d": float(current["churn_lines"].sum()), "reworked_clean_path_n_7d": int(current["file_path"].nunique()), "measurement_status": "available"})
    return pd.DataFrame(rows)


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir().parent
    metrics = resolve_metrics_dir()
    files_path = root / "data" / "lake" / "git_files.parquet"
    policy_path = root / "data" / "analysis" / "code_churn_metrics.parquet.metadata.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    assert_current_code_churn_contract(policy)
    input_hash = hashlib.sha256((compute_sha256(files_path) + compute_sha256(policy_path)).encode()).hexdigest()
    config = {"contract_version": CONTRACT_VERSION, "policy": "code-churn-metrics-v2", "rolling_offsets": list(ROLLING_OFFSETS)}
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    names = ["m8_rework_magnitude.csv", "m8_rework_participation.csv", "m8_rework_trajectory.csv", "m8_baseline_eligibility.csv", "m8_clean_rework.metadata.json"]
    paths = [metrics / name for name in names]
    if not force and all(path.is_file() for path in paths):
        metadata = json.loads(paths[-1].read_text(encoding="utf-8"))
        if metadata.get("input_sha256") == input_hash and metadata.get("config_sha256") == config_hash:
            return {"status": "resumed", "artifacts": [str(path) for path in paths]}
    files, origins = _with_origins(_prepare_files(pd.read_parquet(files_path)))
    universe = pd.read_parquet(root / "data" / "analysis" / "code_churn_metrics.parquet")[TEAM_KEY].drop_duplicates()
    anchors = _anchors(root)
    team, prior = _team_output(files, universe)
    trajectory = _trajectory(files, anchors)
    participation = team[TEAM_KEY + ["clean_rework_churn_t3", "clean_deferred_churn_t3", "clean_total_churn_t3", "clean_rework_ratio_t3", "baseline_eligible_for_rework_t3", "measurement_status"]]
    eligibility = team[TEAM_KEY + ["prior_clean_path_n", "baseline_eligible_for_rework_t3", "measurement_status"]]
    metadata = {"status": "success", "gate_status": "pending", "contract_version": CONTRACT_VERSION, "metric_definition_version": CONTRACT_VERSION, "input_sha256": input_hash, "config_sha256": config_hash, "rq": "RQ3", "unit_of_analysis": "team_semester_then_rolling_window", "policy_version": "code-churn-metrics-v2", "clean_definition": "pipeline_config.is_measurement_code_path", "anchor": "last T3 evaluator vote", "rolling_offsets": list(ROLLING_OFFSETS), "inference": "exploratory_descriptive", "coverage": {"team_semesters": int(len(team)), "eligible_team_semesters": int(team["baseline_eligible_for_rework_t3"].sum()), "trajectory_rows": int(len(trajectory))}, "limitations": ["path provenance is a proxy and not semantic destructive-rework validation", "rolling windows overlap", "ratio is not interpreted for baseline-ineligible teams or zero clean T3 churn", "M8 does not measure defects or causality"], "artifacts": names}
    _atomic_csv(team, paths[0]); _atomic_csv(participation, paths[1]); _atomic_csv(trajectory, paths[2]); _atomic_csv(eligibility, paths[3]); _atomic_json(metadata, paths[4])
    if verbose: print(json.dumps(metadata, indent=2, sort_keys=True))
    return {"status": "generated", "artifacts": [str(path) for path in paths]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate v9 M8 clean rework measures")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2))


if __name__ == "__main__":
    main()