"""Generate M3 repository author-activity dynamics for RQ2."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "m3-author-activity-dynamics-v1"
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


def _gini(counts: pd.Series) -> float:
    values = sorted(float(value) for value in counts.tolist())
    if len(values) <= 1 or sum(values) == 0:
        return 0.0 if values else float("nan")
    weighted = sum((index + 1) * value for index, value in enumerate(values))
    return 2 * weighted / (len(values) * sum(values)) - (len(values) + 1) / len(values)


def _repo_dir(root: Path, repository: str) -> Path:
    path = root / "data" / "raw" / "repos_parent_cache" / f"{repository}.git"
    if not path.is_dir():
        raise FileNotFoundError(f"Parent mirror not found: {path}")
    return path


def _last_t3_anchors(root: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for semester in ("2025.2", "2026.1"):
        path = root / "data" / "processed" / "forms" / semester / "avaliadores.csv"
        if not path.is_file():
            raise FileNotFoundError(f"Evaluator form not found: {path}")
        frame = pd.read_csv(path)
        group_column = "To which group do these scores refer?"
        timestamp_column = "Timestamp"
        if group_column not in frame or timestamp_column not in frame:
            raise ValueError(f"Evaluator form lacks anchor columns: {path}")
        frame["ID_Equipe"] = (
            frame[group_column].astype(str).str.extract(r"Group\s+(\d+)", expand=False)
            .map(lambda value: f"TEAM_{int(value):02d}" if pd.notna(value) else None)
        )
        frame["vote_at"] = pd.to_datetime(frame[timestamp_column], format="mixed")
        frame = frame.dropna(subset=["ID_Equipe", "vote_at"])
        # The final T3 vote is the latest evaluator observation in the semester's final cut.
        t3 = frame[frame["vote_at"].dt.month.isin([6, 12])]
        if semester == "2025.2":
            t3 = t3[t3["vote_at"].dt.day >= 5]
        else:
            t3 = t3[t3["vote_at"].dt.day >= 19]
        anchors = t3.groupby("ID_Equipe", as_index=False)["vote_at"].max()
        anchors["Semestre"] = semester
        rows.extend(anchors.to_dict("records"))
    result = pd.DataFrame(rows)
    if len(result) != 14 or result.duplicated(TEAM_KEY).any():
        raise ValueError(f"Expected 14 unique T3 anchors, got {len(result)}")
    return result


def _mirror_commits(mirror: Path, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    branch = subprocess.check_output(
        ["git", f"--git-dir={mirror}", "symbolic-ref", "--short", "HEAD"],
        text=True,
    ).strip()
    output = subprocess.check_output(
        ["git", f"--git-dir={mirror}", "log", branch, "--format=%H%x09%cI%x09%aE"],
        text=True,
    )
    rows: list[dict[str, Any]] = []
    for line in output.splitlines():
        commit_hash, timestamp_text, author_email = line.split("\t", 2)
        timestamp = pd.Timestamp(timestamp_text).tz_convert("UTC")
        if start.tz_convert("UTC") <= timestamp < end.tz_convert("UTC"):
            author_key = hashlib.sha256(author_email.strip().lower().encode()).hexdigest()[:12]
            rows.append({"commit_hash": commit_hash, "timestamp": timestamp, "author_key": author_key})
    return pd.DataFrame(rows, columns=["commit_hash", "timestamp", "author_key"])


def _summarize_phase(commits: pd.DataFrame, phase: str) -> dict[str, Any]:
    if commits.empty:
        return {
            "phase": phase, "commit_n": 0, "active_days": 0, "author_n": 0,
            "max_author_share": None, "author_gini": None,
            "measurement_status": "no_observed_activity",
        }
    counts = commits["author_key"].value_counts()
    return {
        "phase": phase,
        "commit_n": int(len(commits)),
        "active_days": int(commits["timestamp"].dt.date.nunique()),
        "author_n": int(len(counts)),
        "max_author_share": float((counts / len(commits)).max()),
        "author_gini": float(_gini(counts)),
        "measurement_status": "available",
    }


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir()
    metrics_dir = resolve_metrics_dir()
    commits_path = root.parent / "data" / "lake" / "git_commits.parquet"
    evaluator_paths = [root.parent / "data" / "processed" / "forms" / semester / "avaliadores.csv" for semester in ("2025.2", "2026.1")]
    input_hash = hashlib.sha256("".join(compute_sha256(path) for path in [commits_path, *evaluator_paths]).encode()).hexdigest()
    config = {"contract_version": CONTRACT_VERSION, "phase_days": 7, "rolling_offsets": list(ROLLING_OFFSETS), "anchor": "last_t3_evaluator_vote"}
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    output_names = [
        "m3_author_activity_participation.csv",
        "m3_author_concentration.csv",
        "m3_activity_rolling_7day.csv",
            "m3_activity_rolling_7day_pooled.csv",
        "m3_author_activity_dynamics.metadata.json",
    ]
    paths = [metrics_dir / name for name in output_names]
    manifest_path = paths[-1]
    if not force and manifest_path.is_file() and all(path.is_file() for path in paths[:-1]):
        metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
        if metadata.get("input_sha256") == input_hash and metadata.get("config_sha256") == config_hash:
            return {"status": "resumed", "artifacts": [str(path) for path in paths]}

    anchors = _last_t3_anchors(root.parent)
    participation_rows: list[dict[str, Any]] = []
    phase_rows: list[dict[str, Any]] = []
    rolling_rows: list[dict[str, Any]] = []
    for anchor in anchors.to_dict("records"):
        presentation = pd.Timestamp(anchor["vote_at"]).tz_localize("America/Fortaleza")
        analysis_start = presentation - pd.Timedelta(days=7)
        analysis_end = presentation + pd.Timedelta(days=7)
        mirror = _repo_dir(root.parent, _repository_for_team(root.parent, anchor["Semestre"], anchor["ID_Equipe"]))
        commits = _mirror_commits(mirror, pd.Timestamp("1970-01-01", tz="UTC"), analysis_end)
        pre = commits[(commits["timestamp"] >= analysis_start.tz_convert("UTC")) & (commits["timestamp"] < presentation.tz_convert("UTC"))]
        post = commits[(commits["timestamp"] >= presentation.tz_convert("UTC")) & (commits["timestamp"] < analysis_end.tz_convert("UTC"))]
        whole = commits[commits["timestamp"] < analysis_end.tz_convert("UTC")]
        phase_metrics = {phase: _summarize_phase(data, phase) for phase, data in (("pre", pre), ("post", post))}
        total_n = len(whole)
        participation_rows.append({
            **{key: anchor[key] for key in TEAM_KEY},
            "repository": mirror.name.removesuffix(".git"),
            "presentation_anchor": presentation,
            "total_commit_n": int(total_n),
            "pre_commit_n": int(len(pre)), "post_commit_n": int(len(post)),
            "final_window_commit_n": int(len(pre) + len(post)),
            "pre_share": len(pre) / total_n if total_n else None,
            "post_share": len(post) / total_n if total_n else None,
            "final_window_share": (len(pre) + len(post)) / total_n if total_n else None,
            "small_denominator_lt_10": total_n < 10,
            "measurement_status": "available" if total_n else "no_observed_activity",
        })
        for phase, metrics in phase_metrics.items():
            phase_rows.append({**{key: anchor[key] for key in TEAM_KEY}, "presentation_anchor": presentation, **metrics})
        for offset in ROLLING_OFFSETS:
            window_end = presentation + pd.Timedelta(days=offset)
            window_start = window_end - pd.Timedelta(days=7)
            current = commits[(commits["timestamp"] >= window_start.tz_convert("UTC")) & (commits["timestamp"] < window_end.tz_convert("UTC"))]
            metrics = _summarize_phase(current, "rolling")
            rolling_rows.append({**{key: anchor[key] for key in TEAM_KEY}, "window_end_day": offset, "window_start": window_start, "window_end": window_end, **metrics})

    participation = pd.DataFrame(participation_rows)
    phases = pd.DataFrame(phase_rows)
    rolling = pd.DataFrame(rolling_rows)
    pooled_rolling = (
        rolling.groupby("window_end_day", as_index=False)
        .agg(
            team_semester_n=("ID_Equipe", "size"),
            active_team_semester_n=("commit_n", lambda values: int(values.gt(0).sum())),
            total_commit_n=("commit_n", "sum"),
            mean_commit_n=("commit_n", "mean"),
            median_commit_n=("commit_n", "median"),
            max_commit_n=("commit_n", "max"),
            median_active_days=("active_days", "median"),
            median_max_author_share=("max_author_share", "median"),
            median_author_gini=("author_gini", "median"),
        )
    )
    pooled_rolling["active_team_semester_share"] = (
        pooled_rolling["active_team_semester_n"] / pooled_rolling["team_semester_n"]
    )
    pooled_rolling["aggregation_grain"] = "temporal_marker_relative_to_t3_anchor"
    _atomic_csv(participation, paths[0])
    _atomic_csv(phases, paths[1])
    _atomic_csv(rolling, paths[2])
    _atomic_csv(pooled_rolling, paths[3])
    metadata = {
        "status": "success", "gate_status": "approved", "gate_approved_on": "2026-09-24",
        "gate_scope": "descriptive M3a-M3c RQ2 outputs approved, including semester-independent pooled M3c view",
        "contract_version": CONTRACT_VERSION,
        "metric_definition_version": CONTRACT_VERSION, "input_sha256": input_hash, "config_sha256": config_hash,
        "unit_of_analysis": "team-semester and phase/rolling window", "keys": [*TEAM_KEY, "phase"],
        "rq": "RQ2", "anchor": "last T3 evaluator vote", "window_days": {"before": 7, "after": 7},
        "roles": ["temporal activity", "author concentration", "rolling activity"],
        "limitations": ["repository activity is not coordination friction", "no activity means concentration is unobserved", "self-contained Git mirror history does not identify push actors"],
        "coverage": {"team_semesters": int(len(anchors)), "post_active_team_semesters": int(participation["post_commit_n"].gt(0).sum())},
        "artifacts": output_names,
        "pooled_rolling": {
            "artifact": "m3_activity_rolling_7day_pooled.csv",
            "grain": "window_end_day across all semesters",
            "semester_dimension": "excluded from pooled output",
        },
    }
    _atomic_json(metadata, manifest_path)
    if verbose:
        print(json.dumps(metadata, indent=2, sort_keys=True, default=str))
    return {"status": "generated", "artifacts": [str(path) for path in paths]}


def _repository_for_team(project_root: Path, semester: str, team: str) -> str:
    prefix = f"extensao3-{semester.replace('.', '_')}-"
    numeric = int(team.removeprefix("TEAM_"))
    tokens = [f"team_{numeric:02d}", f"team{numeric}"]
    mirror_dir = project_root / "data" / "raw" / "repos_parent_cache"
    candidates = sorted(
        {
            path.name.removesuffix(".git")
            for token in tokens
            for path in mirror_dir.glob(f"{prefix}{token}-*.git")
        }
    )
    if len(candidates) != 1:
        raise ValueError(f"Expected one parent mirror for {semester}/{team}, got {candidates}")
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the v9 M3 author activity dynamics metric")
    parser.add_argument("--force", action="store_true", help="Regenerate existing artifacts")
    parser.add_argument("--verbose", action="store_true", help="Print the generated manifest")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2, default=str))


if __name__ == "__main__":
    main()
