"""Generate M4 clean-change dynamics under the current artifact policy."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.artifact_policy import is_clean_path
from paper_v9.scripts.common.paths import resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256
from paper_v9.scripts.common.validate_keys import assert_current_code_churn_contract

CONTRACT_VERSION = "m4-clean-change-dynamics-v1"
TEAM_KEY = ["Semestre", "ID_Equipe"]
ROLLING_OFFSETS = tuple(range(-63, 8))


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
        frame["vote_at"] = pd.to_datetime(frame["Timestamp"], format="mixed")
        frame = frame.dropna(subset=["ID_Equipe", "vote_at"])
        if semester == "2025.2":
            frame = frame[frame["vote_at"].dt.day >= 5]
        else:
            frame = frame[frame["vote_at"].dt.day >= 19]
        latest = frame.groupby("ID_Equipe", as_index=False)["vote_at"].max().assign(Semestre=semester)
        rows.extend(latest.to_dict("records"))
    result = pd.DataFrame(rows)
    if len(result) != 14 or result.duplicated(TEAM_KEY).any():
        raise ValueError(f"Expected 14 unique M4 anchors, got {len(result)}")
    return result


def _prepare_files(frame: pd.DataFrame) -> pd.DataFrame:
    required = {"Semestre", "ID_Equipe", "temporal_marker", "timestamp", "file_path", "file_extension", "lines_added", "lines_deleted", "commit_hash"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"M4 file input is missing columns: {sorted(missing)}")
    frame = frame.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    frame["lines_added"] = pd.to_numeric(frame["lines_added"], errors="coerce").fillna(0)
    frame["lines_deleted"] = pd.to_numeric(frame["lines_deleted"], errors="coerce").fillna(0)
    frame["churn_lines"] = frame["lines_added"] + frame["lines_deleted"]
    frame["clean_included"] = frame["file_path"].map(is_clean_path)
    frame["file_category"] = frame["clean_included"].map({True: "clean_source_or_test", False: "excluded_or_non_measurement"})
    return frame


def _summary(frame: pd.DataFrame, team_keys: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for key, group in frame.groupby(TEAM_KEY + ["temporal_marker"], observed=True):
        clean = group[group["clean_included"]]
        touched = clean.groupby("commit_hash")["churn_lines"].sum() if not clean.empty else pd.Series(dtype=float)
        rows.append({
            "Semestre": key[0], "ID_Equipe": key[1], "temporal_marker": key[2],
            "clean_churn": float(clean["churn_lines"].sum()),
            "all_churn": float(group["churn_lines"].sum()),
            "clean_unique_file_n": int(clean["file_path"].nunique()),
            "clean_touching_commit_n": int(clean["commit_hash"].nunique()),
            "median_clean_churn_per_touching_commit": float(touched.median()) if len(touched) else None,
            "max_clean_churn_per_touching_commit": float(touched.max()) if len(touched) else None,
            "clean_share_of_all_churn": float(clean["churn_lines"].sum() / group["churn_lines"].sum()) if group["churn_lines"].sum() else None,
            "measurement_status": "available" if not clean.empty else "no_clean_change_observed",
        })
    result = pd.DataFrame(rows)
    markers = pd.DataFrame({"temporal_marker": ["T1", "T2", "T3"]})
    grid = team_keys.assign(_join=1).merge(markers.assign(_join=1), on="_join").drop(columns="_join")
    return grid.merge(result, on=TEAM_KEY + ["temporal_marker"], how="left").assign(
        clean_churn=lambda frame: frame["clean_churn"].fillna(0),
        all_churn=lambda frame: frame["all_churn"].fillna(0),
        clean_unique_file_n=lambda frame: frame["clean_unique_file_n"].fillna(0).astype(int),
        clean_touching_commit_n=lambda frame: frame["clean_touching_commit_n"].fillna(0).astype(int),
        measurement_status=lambda frame: frame["measurement_status"].fillna("no_clean_change_observed"),
    ).sort_values(TEAM_KEY + ["temporal_marker"]).reset_index(drop=True)


def _composition(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.groupby(TEAM_KEY + ["temporal_marker", "file_category"], observed=True).agg(
        file_event_n=("file_path", "size"), unique_file_n=("file_path", "nunique"), churn_lines=("churn_lines", "sum")
    ).reset_index()
    result["churn_share"] = result["churn_lines"] / result.groupby(TEAM_KEY + ["temporal_marker"])["churn_lines"].transform("sum").replace(0, pd.NA)
    result["included_in_m4"] = result["file_category"].eq("clean_source_or_test")
    return result


def _rolling(files: pd.DataFrame, anchors: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    keys = files[TEAM_KEY].drop_duplicates().merge(anchors, on=TEAM_KEY, validate="one_to_one")
    for anchor in keys.to_dict("records"):
        team = files[(files["Semestre"] == anchor["Semestre"]) & (files["ID_Equipe"] == anchor["ID_Equipe"]) & files["clean_included"]]
        t3 = pd.Timestamp(anchor["vote_at"]).tz_localize("America/Fortaleza").tz_convert("UTC")
        for offset in ROLLING_OFFSETS:
            end = t3 + pd.Timedelta(days=offset)
            start = end - pd.Timedelta(days=7)
            current = team[(team["timestamp"] >= start) & (team["timestamp"] < end)]
            rows.append({
                "Semestre": anchor["Semestre"], "ID_Equipe": anchor["ID_Equipe"], "window_end_day": offset,
                "clean_churn_7d": float(current["churn_lines"].sum()),
                "unique_clean_file_n_7d": int(current["file_path"].nunique()),
                "clean_file_event_n_7d": int(len(current)),
                "measurement_status": "available" if not current.empty else "no_clean_change_observed",
            })
    return pd.DataFrame(rows)


def _build_pooled_outputs(
    magnitude: pd.DataFrame,
    intensity: pd.DataFrame,
    composition: pd.DataFrame,
    rolling: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    pooled_magnitude = magnitude.groupby("temporal_marker", as_index=False).agg(
        team_semester_n=("ID_Equipe", "size"),
        observed_clean_team_semester_n=("clean_churn", lambda values: int(values.gt(0).sum())),
        total_clean_churn=("clean_churn", "sum"),
        median_clean_churn=("clean_churn", "median"),
        total_all_churn=("all_churn", "sum"),
        median_clean_unique_file_n=("clean_unique_file_n", "median"),
    )
    pooled_magnitude["clean_share_of_all_churn"] = pooled_magnitude["total_clean_churn"] / pooled_magnitude["total_all_churn"].replace(0, pd.NA)
    pooled_magnitude["aggregation_grain"] = "temporal_marker_across_semesters"

    pooled_intensity = intensity.groupby("temporal_marker", as_index=False).agg(
        team_semester_n=("ID_Equipe", "size"),
        touching_commit_n=("clean_touching_commit_n", "sum"),
        median_clean_churn_per_touching_commit=("median_clean_churn_per_touching_commit", "median"),
        max_clean_churn_per_touching_commit=("max_clean_churn_per_touching_commit", "max"),
        total_clean_unique_file_n=("clean_unique_file_n", "sum"),
    )
    pooled_intensity["aggregation_grain"] = "temporal_marker_across_semesters"

    pooled_composition = composition.groupby(["temporal_marker", "file_category", "included_in_m4"], as_index=False).agg(
        team_semester_n=("ID_Equipe", "nunique"),
        file_event_n=("file_event_n", "sum"),
        unique_file_n=("unique_file_n", "sum"),
        churn_lines=("churn_lines", "sum"),
    )
    pooled_composition["churn_share"] = pooled_composition["churn_lines"] / pooled_composition.groupby("temporal_marker")["churn_lines"].transform("sum").replace(0, pd.NA)
    pooled_composition["aggregation_grain"] = "temporal_marker_across_semesters"

    pooled_rolling = rolling.groupby("window_end_day", as_index=False).agg(
        team_semester_n=("ID_Equipe", "size"),
        active_team_semester_n=("clean_churn_7d", lambda values: int(values.gt(0).sum())),
        total_clean_churn_7d=("clean_churn_7d", "sum"),
        median_clean_churn_7d=("clean_churn_7d", "median"),
        max_clean_churn_7d=("clean_churn_7d", "max"),
        median_unique_clean_file_n_7d=("unique_clean_file_n_7d", "median"),
    )
    pooled_rolling["active_team_semester_share"] = pooled_rolling["active_team_semester_n"] / pooled_rolling["team_semester_n"]
    pooled_rolling["aggregation_grain"] = "relative_t3_window_across_semesters"
    return pooled_magnitude, pooled_intensity, pooled_composition, pooled_rolling


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir()
    metrics_dir = resolve_metrics_dir()
    files_path = root.parent / "data" / "lake" / "git_files.parquet"
    policy_meta_path = root.parent / "data" / "analysis" / "code_churn_metrics.parquet.metadata.json"
    policy_metadata = json.loads(policy_meta_path.read_text(encoding="utf-8"))
    assert_current_code_churn_contract(policy_metadata)
    anchors = _anchors(root.parent)
    input_hash = hashlib.sha256("".join(compute_sha256(path) for path in [files_path, policy_meta_path]).encode()).hexdigest()
    config = {"contract_version": CONTRACT_VERSION, "policy": "code-churn-metrics-v2", "rolling_offsets": list(ROLLING_OFFSETS)}
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    names = [
        "m4_churn_magnitude.csv", "m4_commit_intensity.csv", "m4_artifact_composition.csv", "m4_rolling_7day_trajectory.csv",
        "m4_churn_magnitude_pooled.csv", "m4_commit_intensity_pooled.csv", "m4_artifact_composition_pooled.csv", "m4_rolling_7day_trajectory_pooled.csv",
        "m4_clean_change_dynamics.metadata.json",
    ]
    paths = [metrics_dir / name for name in names]
    if not force and paths[-1].is_file() and all(path.is_file() for path in paths[:-1]):
        metadata = json.loads(paths[-1].read_text())
        if metadata.get("input_sha256") == input_hash and metadata.get("config_sha256") == config_hash:
            return {"status": "resumed", "artifacts": [str(path) for path in paths]}
    files = _prepare_files(pd.read_parquet(files_path))
    code_churn = pd.read_parquet(root.parent / "data" / "analysis" / "code_churn_metrics.parquet")
    team_keys = code_churn[TEAM_KEY].drop_duplicates()
    if len(team_keys) != 14:
        raise ValueError(f"Expected 14 M4 team-semesters, got {len(team_keys)}")
    magnitude = _summary(files, team_keys)
    intensity = magnitude[TEAM_KEY + ["temporal_marker", "clean_touching_commit_n", "median_clean_churn_per_touching_commit", "max_clean_churn_per_touching_commit", "clean_unique_file_n", "measurement_status"]]
    composition = _composition(files)
    rolling = _rolling(files, anchors)
    pooled_magnitude, pooled_intensity, pooled_composition, pooled_rolling = _build_pooled_outputs(magnitude, intensity, composition, rolling)
    _atomic_csv(magnitude, paths[0]); _atomic_csv(intensity, paths[1]); _atomic_csv(composition, paths[2]); _atomic_csv(rolling, paths[3])
    _atomic_csv(pooled_magnitude, paths[4]); _atomic_csv(pooled_intensity, paths[5]); _atomic_csv(pooled_composition, paths[6]); _atomic_csv(pooled_rolling, paths[7])
    metadata = {"status": "success", "gate_status": "pending", "contract_version": CONTRACT_VERSION, "metric_definition_version": CONTRACT_VERSION, "input_sha256": input_hash, "config_sha256": config_hash, "rq": "RQ2", "unit_of_analysis": "team-semester, checkpoint, and rolling window", "anchor": "last T3 evaluator vote", "policy_version": "code-churn-metrics-v2", "clean_definition": "pipeline_config.is_measurement_code_path", "coverage": {"team_semesters": int(len(anchors)), "rolling_rows": int(len(rolling))}, "limitations": ["clean path provenance is not semantic defect validation", "rolling windows overlap", "M4 does not measure coordination friction"], "artifacts": names}
    _atomic_json(metadata, paths[-1])
    if verbose: print(json.dumps(metadata, indent=2, sort_keys=True, default=str))
    return {"status": "generated", "artifacts": [str(path) for path in paths]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the v9 M4 clean change dynamics metric")
    parser.add_argument("--force", action="store_true", help="Regenerate existing artifacts")
    parser.add_argument("--verbose", action="store_true", help="Print the generated manifest")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2, default=str))


if __name__ == "__main__":
    main()
