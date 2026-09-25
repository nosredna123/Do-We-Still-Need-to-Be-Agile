"""Generate descriptive repository-inactivity trajectories for M7."""

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
from pipeline_config import EVALUATOR_TEMPORAL_CUTS

CONTRACT_VERSION = "m7-repository-inactivity-v1"
ROLLING_OFFSETS = tuple(range(-63, 8))
WINDOW_DAYS = 7
TEAM_KEY = ["ID_Equipe", "Semestre"]


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
    for semester, ranges in EVALUATOR_TEMPORAL_CUTS.items():
        votes = pd.read_csv(root / "data" / "processed" / "forms" / semester / "avaliadores.csv")
        required = {"To which group do these scores refer?", "Timestamp"}
        if not required.issubset(votes.columns):
            raise ValueError(f"M7 evaluator input is missing columns: {sorted(required - set(votes.columns))}")
        votes["ID_Equipe"] = votes["To which group do these scores refer?"].astype(str).str.extract(r"Group\s+(\d+)", expand=False).map(lambda value: f"TEAM_{int(value):02d}" if pd.notna(value) else None)
        votes["vote_at"] = pd.to_datetime(votes["Timestamp"], format="mixed").dt.tz_localize("America/Fortaleza")
        for marker, (start, end) in ranges.items():
            selected = votes.loc[votes["vote_at"].dt.date.between(pd.Timestamp(start).date(), pd.Timestamp(end).date())]
            latest = selected.groupby("ID_Equipe", as_index=False)["vote_at"].max()
            latest["Semestre"] = semester
            latest["temporal_marker"] = marker
            rows.extend(latest.to_dict("records"))
    result = pd.DataFrame(rows)
    if result.empty or result.duplicated(TEAM_KEY + ["temporal_marker"]).any():
        raise ValueError("M7 evaluator anchors are empty or duplicated")
    if len(result) != 42:
        raise ValueError(f"Expected 42 M7 checkpoint anchors, got {len(result)}")
    return result


def _load_commits(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    required = {"ID_Equipe", "Semestre", "timestamp", "temporal_marker"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"M7 commit contract is missing columns: {sorted(missing)}")
    frame = frame.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True)
    if frame[TEAM_KEY].isna().any().any() or frame["timestamp"].isna().any():
        raise ValueError("M7 commits contain null team keys or timestamps")
    return frame


def _checkpoint_output(commits: pd.DataFrame, anchors: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for anchor in anchors.to_dict("records"):
        end = pd.Timestamp(anchor["vote_at"]).tz_convert("UTC")
        start = end - pd.Timedelta(days=WINDOW_DAYS)
        team = commits.loc[(commits["Semestre"].astype(str) == str(anchor["Semestre"])) & commits["ID_Equipe"].eq(anchor["ID_Equipe"])]
        recent = team.loc[team["timestamp"].ge(start) & team["timestamp"].lt(end)]
        rows.append({**{key: anchor[key] for key in TEAM_KEY}, "temporal_marker": anchor["temporal_marker"], "checkpoint_anchor": end, "window_start": start, "window_end": end, "commit_n_7d": int(len(recent)), "repository_inactive_7d": not bool(len(recent)), "measurement_status": "available"})
    return pd.DataFrame(rows).sort_values(TEAM_KEY + ["temporal_marker"]).reset_index(drop=True)


def _daily_output(commits: pd.DataFrame, anchors: pd.DataFrame) -> pd.DataFrame:
    t3 = anchors.loc[anchors["temporal_marker"].eq("T3")]
    rows: list[dict[str, Any]] = []
    for anchor in t3.to_dict("records"):
        end_anchor = pd.Timestamp(anchor["vote_at"]).tz_convert("UTC")
        team = commits.loc[(commits["Semestre"].astype(str) == str(anchor["Semestre"])) & commits["ID_Equipe"].eq(anchor["ID_Equipe"])]
        for offset in ROLLING_OFFSETS:
            end = end_anchor + pd.Timedelta(days=offset)
            start = end - pd.Timedelta(days=WINDOW_DAYS)
            recent = team.loc[team["timestamp"].ge(start) & team["timestamp"].lt(end)]
            rows.append({**{key: anchor[key] for key in TEAM_KEY}, "window_end_day_relative_to_t3": offset, "checkpoint_anchor": end_anchor, "window_start": start, "window_end": end, "commit_n_7d": int(len(recent)), "repository_inactive_7d": not bool(len(recent)), "measurement_status": "available"})
    result = pd.DataFrame(rows).sort_values(TEAM_KEY + ["window_end_day_relative_to_t3"]).reset_index(drop=True)
    if len(result) != 14 * len(ROLLING_OFFSETS):
        raise ValueError(f"Expected {14 * len(ROLLING_OFFSETS)} M7 daily windows, got {len(result)}")
    return result


def _pattern(checkpoints: pd.DataFrame) -> pd.DataFrame:
    result = checkpoints.pivot_table(index=TEAM_KEY, columns="temporal_marker", values="repository_inactive_7d", aggfunc="first").reindex(columns=["T1", "T2", "T3"]).reset_index()
    if result[["T1", "T2", "T3"]].isna().any().any():
        raise ValueError("M7 persistence pattern has missing checkpoint observations")
    result["inactive_checkpoint_n"] = result[["T1", "T2", "T3"]].sum(axis=1).astype(int)
    result["inactivity_pattern"] = result.apply(lambda row: "never_inactive" if row["inactive_checkpoint_n"] == 0 else "t1_only" if bool(row["T1"]) and not bool(row["T2"]) and not bool(row["T3"]) else "persistent_all_checkpoints" if row["inactive_checkpoint_n"] == 3 else "intermittent", axis=1)
    result["analysis_level"] = "team_semester_checkpoint_windows"
    return result.sort_values(TEAM_KEY).reset_index(drop=True)


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir().parent
    metrics = resolve_metrics_dir()
    commits_path = root / "data" / "lake" / "git_commits.parquet"
    evaluator_path = root / "data" / "lake" / "evaluator_team_cuts.parquet"
    forms_paths = [root / "data" / "processed" / "forms" / semester / "avaliadores.csv" for semester in EVALUATOR_TEMPORAL_CUTS]
    input_hash = hashlib.sha256("".join(compute_sha256(path) for path in [commits_path, evaluator_path, *forms_paths]).encode()).hexdigest()
    config = {"contract_version": CONTRACT_VERSION, "window_days": WINDOW_DAYS, "rolling_offsets": list(ROLLING_OFFSETS), "anchor": "last_evaluator_vote_per_team_checkpoint"}
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    names = ["m7_inactivity_trajectory.csv", "m7_inactivity_pattern.csv", "m7_checkpoint_inactivity.csv", "m7_repository_inactivity.metadata.json"]
    paths = [metrics / name for name in names]
    if not force and all(path.is_file() for path in paths):
        metadata = json.loads(paths[-1].read_text(encoding="utf-8"))
        if metadata.get("input_sha256") == input_hash and metadata.get("config_sha256") == config_hash:
            return {"status": "resumed", "artifacts": [str(path) for path in paths]}
    commits = _load_commits(commits_path)
    anchors = _anchors(root)
    checkpoint = _checkpoint_output(commits, anchors)
    trajectory = _daily_output(commits, anchors)
    pattern = _pattern(checkpoint)
    metadata = {"status": "success", "gate_status": "pending", "contract_version": CONTRACT_VERSION, "metric_definition_version": CONTRACT_VERSION, "input_sha256": input_hash, "config_sha256": config_hash, "rq": "RQ3", "unit_of_analysis": "team_semester_rolling_window_then_checkpoint_pattern", "source_contracts": ["data/lake/git_commits.parquet", "data/lake/evaluator_team_cuts.parquet", "data/processed/forms/{semester}/avaliadores.csv"], "window_days": WINDOW_DAYS, "rolling_offsets": list(ROLLING_OFFSETS), "anchor": "last evaluator vote per team and checkpoint", "inference": "descriptive_only", "planning_claim": "not_identifiable_from_repository_inactivity", "coverage": {"team_semesters": 14, "checkpoint_rows": int(len(checkpoint)), "daily_rows": int(len(trajectory)), "pattern_rows": int(len(pattern))}, "limitations": ["repository inactivity does not identify planning omission", "seven-day windows overlap", "Git does not observe off-repository work", "M7 is not an independent planning predictor for M9"], "artifacts": names}
    _atomic_csv(trajectory, paths[0]); _atomic_csv(pattern, paths[1]); _atomic_csv(checkpoint, paths[2]); _atomic_json(metadata, paths[3])
    if verbose: print(json.dumps(metadata, indent=2, sort_keys=True))
    return {"status": "generated", "artifacts": [str(path) for path in paths]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate v9 M7 repository inactivity outputs")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2))


if __name__ == "__main__":
    main()