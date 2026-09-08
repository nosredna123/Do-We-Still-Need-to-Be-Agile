#!/usr/bin/env python3
"""Build the six independent Phase 1 data lake contracts."""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any

import pandas as pd

from pipeline_config import EVALUATOR_TEMPORAL_CUTS, temporal_marker_for
from pipeline_core import input_checksum, load_project_environment, write_artifact_metadata

logger = logging.getLogger(__name__)
VALID_MARKERS = {"T1", "T2", "T3"}
DATASET_NAMES = ("student_responses", "evaluator_team_cuts", "git_team_cuts", "git_commits", "git_files", "transcript_sessions")
KEY_COLUMNS = ["ID_Equipe", "Semestre", "temporal_marker"]
COMMIT_KEY_COLUMNS = KEY_COLUMNS + ["repository", "commit_hash"]
FILE_KEY_COLUMNS = COMMIT_KEY_COLUMNS + ["file_path"]
EVALUATOR_SCORE_NAMES = {
    'What is the score for "Engagement/Participation"?': "engagement_participation",
    'What is the score for "Project Progress"?': "project_progress",
    'What is the score for "Scope/Applicability"?': "scope_applicability",
    'What is the score for "Technical Complexity"?': "technical_complexity",
}
COMMIT_REQUIRED = COMMIT_KEY_COLUMNS + ["timestamp", "ID_Autor_Local", "lines_added", "lines_deleted", "files_changed", "branch_or_ref_source"]
FILE_REQUIRED = FILE_KEY_COLUMNS + ["timestamp", "ID_Autor_Local", "change_status", "lines_added", "lines_deleted", "is_binary", "branch_or_ref_source"]


def normalize_temporal_marker(value: object) -> str:
    """Validate and return an explicit temporal marker."""
    marker = str(value).strip().upper()
    if marker not in VALID_MARKERS:
        raise ValueError(f"Invalid temporal_marker {value!r}; expected T1, T2 or T3")
    return marker


def require_columns(df: pd.DataFrame, required: list[str], label: str) -> None:
    """Require columns and non-blank values for a source contract."""
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")
    for column in required:
        values = df[column]
        if values.isna().any() or values.astype(str).str.strip().eq("").any():
            raise ValueError(f"{label} contains missing or blank values in {column}")


def _ensure_unique_keys(frame: pd.DataFrame, keys: list[str], label: str) -> None:
    """Reject duplicate analytical keys."""
    if frame.duplicated(keys).any():
        raise ValueError(f"{label} contains duplicate analytical keys")


def parse_evaluator_team_id(raw_value: object) -> str:
    """Convert an evaluator group label to its anonymized team identifier."""
    match = re.search(r"Group\s+(\d+)", str(raw_value or ""), flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Evaluator group label is invalid: {raw_value!r}")
    return f"TEAM_{int(match.group(1)):02d}"


def student_temporal_marker_for_filename(csv_file: Path) -> str:
    """Read a student temporal marker from its filename."""
    match = re.search(r"(?:^|[_-])t([123])(?:[_-]|$)", csv_file.stem.lower())
    if not match:
        raise ValueError(f"Student form file {csv_file} lacks an explicit temporal marker")
    return f"T{match.group(1)}"


def transcript_temporal_marker_for_filename(transcript_file: Path, semester: str) -> str:
    """Derive a transcript cut from an observable filename date."""
    match = re.search(r"(20\d{2}-\d{2}-\d{2})", transcript_file.stem)
    if match:
        return temporal_marker_for(semester, match.group(1))
    short_date = re.search(r"(?:MyRec_)?(\d{2})(\d{2})", transcript_file.stem)
    if not short_date:
        raise ValueError(f"Transcript {transcript_file} lacks an observable date")
    return temporal_marker_for(semester, f"{semester.split('.')[0]}-{short_date.group(1)}-{short_date.group(2)}")


def load_form_files(forms_dir: Path) -> pd.DataFrame:
    """Load student and evaluator forms with source-specific provenance."""
    if not forms_dir.is_dir():
        raise FileNotFoundError(f"Forms directory not found: {forms_dir}")
    frames: list[pd.DataFrame] = []
    for csv_file in sorted(forms_dir.rglob("*.csv")):
        frame = pd.read_csv(csv_file)
        semester = str(csv_file.parent.name)
        frame["Semestre"] = semester
        if "alunos" in csv_file.stem.lower():
            frame["temporal_marker"] = student_temporal_marker_for_filename(csv_file)
            frame["source_type"] = "student_response"
        elif {"Timestamp", "To which group do these scores refer?"}.issubset(frame.columns):
            frame["ID_Equipe"] = frame["To which group do these scores refer?"].map(parse_evaluator_team_id)
            frame["temporal_marker"] = frame["Timestamp"].map(lambda value, semester=semester: temporal_marker_for(semester, pd.to_datetime(value).strftime("%Y-%m-%d")))
            frame["source_type"] = "evaluator_team_cut"
        else:
            raise ValueError(f"Form file {csv_file} does not match a known form schema")
        frame["source_file"] = str(csv_file.relative_to(forms_dir))
        frames.append(frame)
    if not frames:
        raise ValueError(f"Forms directory contains no CSV sources: {forms_dir}")
    result = pd.concat(frames, ignore_index=True)
    result["Semestre"] = result["Semestre"].astype("string")
    result["temporal_marker"] = result["temporal_marker"].map(normalize_temporal_marker)
    return result


def _validate_git_values(frame: pd.DataFrame, required: list[str], label: str, keys: list[str], nullable_line_counts: bool = False) -> pd.DataFrame:
    """Validate common event-level Git fields."""
    required_for_presence = [column for column in required if not (nullable_line_counts and column in {"lines_added", "lines_deleted"})]
    require_columns(frame, required_for_presence, label)
    for column in {"lines_added", "lines_deleted"} if nullable_line_counts else set():
        if column not in frame.columns:
            raise ValueError(f"{label} is missing required columns: {column}")
    frame = frame.copy()
    frame["Semestre"] = frame["Semestre"].astype("string")
    frame["temporal_marker"] = frame["temporal_marker"].map(normalize_temporal_marker)
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise", utc=True).astype("string")
    for column in ["lines_added", "lines_deleted"] + (["files_changed"] if "files_changed" in frame else []):
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        invalid_nulls = frame[column].isna() & ~frame.get("is_binary", pd.Series(False, index=frame.index)).astype(bool) if nullable_line_counts else frame[column].isna()
        if invalid_nulls.any() or (frame[column].dropna() < 0).any():
            raise ValueError(f"{label} has invalid numeric values in {column}")
    _ensure_unique_keys(frame, keys, label)
    return frame


def load_git_commits(git_csv_path: Path) -> pd.DataFrame:
    """Load and validate one row per observed Git commit."""
    if not git_csv_path.is_file():
        raise FileNotFoundError(f"Git commits file not found: {git_csv_path}")
    return _validate_git_values(pd.read_csv(git_csv_path), COMMIT_REQUIRED, "git commits", COMMIT_KEY_COLUMNS)


def load_git_files(git_csv_path: Path) -> pd.DataFrame:
    """Load and validate one row per file changed in a Git commit."""
    if not git_csv_path.is_file():
        raise FileNotFoundError(f"Git files file not found: {git_csv_path}")
    frame = _validate_git_values(pd.read_csv(git_csv_path), FILE_REQUIRED, "git files", FILE_KEY_COLUMNS, nullable_line_counts=True)
    if "file_extension" not in frame.columns:
        raise ValueError("git files is missing required column file_extension")
    frame["file_extension"] = frame["file_extension"].fillna("").astype("string").str.lower()
    if not frame["change_status"].isin({"added", "modified", "deleted", "renamed", "copied"}).all():
        raise ValueError("git files contains an invalid change_status")
    if frame["file_path"].astype(str).str.startswith(".git/").any():
        raise ValueError("git files must not contain .git/ paths")
    return frame


def load_git_logs(git_csv_path: Path) -> pd.DataFrame:
    """Load the legacy aggregate CSV for backward-compatible fixtures."""
    if not git_csv_path.is_file():
        raise FileNotFoundError(f"Git logs file not found: {git_csv_path}")
    frame = pd.read_csv(git_csv_path)
    require_columns(frame, KEY_COLUMNS + ["lines_added", "lines_deleted", "files_changed", "ID_Autor_Local", "commit_hash"], "git logs")
    frame["Semestre"] = frame["Semestre"].astype("string")
    frame["temporal_marker"] = frame["temporal_marker"].map(normalize_temporal_marker)
    for column in ["lines_added", "lines_deleted", "files_changed"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame


def load_transcripts(transcripts_dir: Path) -> pd.DataFrame:
    """Load transcript sessions without inferring team membership."""
    if not transcripts_dir.is_dir():
        raise FileNotFoundError(f"Transcripts directory not found: {transcripts_dir}")
    rows: list[dict[str, Any]] = []
    for json_file in sorted(transcripts_dir.rglob("*.json")):
        if json_file.name.endswith(".metadata.json"):
            continue
        data = json.loads(json_file.read_text(encoding="utf-8"))
        semester = str(data.get("Semestre") or json_file.parent.parent.name)
        if semester not in EVALUATOR_TEMPORAL_CUTS:
            raise ValueError(f"Transcript {json_file} lacks a configured Semestre")
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Transcript {json_file} lacks non-empty text")
        marker = data.get("temporal_marker")
        marker_source = "metadata" if marker is not None else "filename"
        if marker is None:
            marker = transcript_temporal_marker_for_filename(json_file, semester)
        rows.append({"session_id": str(json_file.parent.relative_to(transcripts_dir)), "transcript_file": str(json_file.relative_to(transcripts_dir)), "Semestre": semester, "temporal_marker": normalize_temporal_marker(marker), "temporal_marker_source": marker_source, "transcript_text": text, "status": data.get("status") or "success", "source_type": "transcript_session"})
    if not rows:
        raise ValueError(f"Transcripts directory contains no JSON sources: {transcripts_dir}")
    result = pd.DataFrame(rows)
    require_columns(result, ["session_id", "transcript_file", "Semestre", "temporal_marker", "status"], "transcripts")
    _ensure_unique_keys(result, ["session_id", "transcript_file"], "transcripts")
    return result


def aggregate_git_cuts(git_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate Git activity by team, semester and temporal cut."""
    require_columns(git_df, KEY_COLUMNS + ["lines_added", "lines_deleted", "files_changed", "ID_Autor_Local", "commit_hash"], "git commits")
    result = git_df.groupby(KEY_COLUMNS, as_index=False).agg(lines_added=("lines_added", "sum"), lines_deleted=("lines_deleted", "sum"), files_changed=("files_changed", "sum"), num_authors=("ID_Autor_Local", "nunique"), num_commits=("commit_hash", "count"))
    result["source_type"] = "git_team_cut"
    _ensure_unique_keys(result, KEY_COLUMNS, "git cuts")
    return result


def _interquartile_range(values: pd.Series) -> float:
    """Return the interquartile range of one evaluator score group."""
    return float(values.quantile(0.75) - values.quantile(0.25))


def aggregate_evaluator_cuts(forms_df: pd.DataFrame, git_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate evaluator responses and attach only Git match status."""
    require_columns(forms_df, ["Semestre", "temporal_marker", "source_type"], "forms")
    evaluator = forms_df[forms_df["source_type"] == "evaluator_team_cut"].copy()
    if evaluator.empty:
        raise ValueError("No evaluator responses were found")
    require_columns(evaluator, KEY_COLUMNS, "evaluator forms")
    score_columns = [column for column in evaluator.columns if "score" in column.lower() and "group" not in column.lower()]
    if not score_columns:
        raise ValueError("Evaluator forms contain no score columns")
    unknown = [column for column in score_columns if column not in EVALUATOR_SCORE_NAMES]
    if unknown:
        raise ValueError("Evaluator forms contain unmapped score columns: " + ", ".join(unknown))
    aggregations: dict[str, tuple[str, object]] = {}
    for column in score_columns:
        evaluator[column] = pd.to_numeric(evaluator[column], errors="raise")
        name = EVALUATOR_SCORE_NAMES[column]
        aggregations.update({f"{name}_mean": (column, "mean"), f"{name}_std": (column, "std"), f"{name}_median": (column, "median"), f"{name}_iqr": (column, _interquartile_range), f"{name}_n": (column, "count")})
    result = evaluator.groupby(KEY_COLUMNS, as_index=False).agg(**aggregations)
    git_keys = aggregate_git_cuts(git_df)[KEY_COLUMNS] if not git_df.empty else pd.DataFrame(columns=KEY_COLUMNS)
    observed = set(map(tuple, git_keys.itertuples(index=False, name=None)))
    result["git_match_status"] = ["matched" if tuple(row) in observed else "no_observed_activity" for row in result[KEY_COLUMNS].itertuples(index=False, name=None)]
    result["source_type"] = "evaluator_team_cut"
    _ensure_unique_keys(result, KEY_COLUMNS, "evaluator cuts")
    return result


def source_paths(forms_dir: Path, git_paths: list[Path], transcripts_dir: Path) -> list[Path]:
    """Return all effective source files for checksum calculation."""
    paths = [*git_paths, *sorted(forms_dir.rglob("*.csv"))]
    paths.extend(path for path in sorted(transcripts_dir.rglob("*.json")) if not path.name.endswith(".metadata.json"))
    return paths


def validation_report(outputs: dict[str, pd.DataFrame], artifacts: dict[str, Path]) -> dict[str, Any]:
    """Create a PII-free validation summary for generated contracts."""
    pii_status = "passed_structural_scan"
    email_pattern = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")
    datasets: dict[str, Any] = {}
    for name, frame in outputs.items():
        for column in frame.select_dtypes(include=["object", "string"]).columns:
            values = frame[column].dropna().astype(str)
            if values.str.contains(email_pattern, regex=True).any():
                pii_status = "failed"
            if any(token in column.lower() for token in ("email", "nome", "name")) and values[~values.str.startswith("anon_")].size:
                pii_status = "failed"
        key = FILE_KEY_COLUMNS if name == "git_files" else COMMIT_KEY_COLUMNS if name == "git_commits" else KEY_COLUMNS
        datasets[name] = {"rows": len(frame), "schema": {column: str(dtype) for column, dtype in frame.dtypes.items()}, "duplicate_key_count": int(frame.duplicated(key).sum()) if set(key).issubset(frame.columns) else 0, "artifact": str(artifacts[name])}
    evaluator = outputs["evaluator_team_cuts"]
    return {"status": "success", "datasets": datasets, "evaluator_score_names": list(EVALUATOR_SCORE_NAMES.values()), "git_match_status": evaluator["git_match_status"].value_counts().to_dict(), "evaluator_keys_without_git": evaluator.loc[evaluator["git_match_status"] == "no_observed_activity", KEY_COLUMNS].astype(str).to_dict("records"), "pii_status": pii_status, "sidecars_status": "success", "event_level": {"commits": len(outputs["git_commits"]), "files": len(outputs["git_files"])}}


def build_lake(forms_dir: Path, git_logs_path: Path, transcripts_dir: Path, output_dir: Path, git_files_path: Path | None = None) -> dict[str, Path]:
    """Load, validate and atomically write the six Phase 1 lake contracts."""
    forms = load_form_files(forms_dir)
    event_level = git_files_path is not None
    git = load_git_commits(git_logs_path) if event_level else load_git_logs(git_logs_path)
    files = load_git_files(git_files_path) if git_files_path else pd.DataFrame(columns=FILE_REQUIRED)
    transcripts = load_transcripts(transcripts_dir)
    outputs = {"student_responses": forms[forms["source_type"] == "student_response"].drop(columns=["ID_Equipe"], errors="ignore"), "evaluator_team_cuts": aggregate_evaluator_cuts(forms, git), "git_team_cuts": aggregate_git_cuts(git), "git_commits": git, "git_files": files, "transcript_sessions": transcripts}
    checksum = input_checksum(source_paths(forms_dir, [git_logs_path, *([git_files_path] if git_files_path else [])], transcripts_dir), {"contracts": ",".join(DATASET_NAMES), "event_level": str(event_level)})
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {name: output_dir / f"{name}.parquet" for name in outputs}
    temporary = {name: output_dir / f".{name}.parquet.tmp" for name in outputs}
    try:
        for name, frame in outputs.items():
            frame.to_parquet(temporary[name], index=False)
        for name, path in artifacts.items():
            temporary[name].replace(path)
            write_artifact_metadata(path, checksum)
        (output_dir / "lake_validation_report.json").write_text(json.dumps(validation_report(outputs, artifacts), indent=2), encoding="utf-8")
        return artifacts
    except Exception:
        for path in [*temporary.values(), *artifacts.values()]:
            path.unlink(missing_ok=True)
            path.with_name(f"{path.name}.metadata.json").unlink(missing_ok=True)
        raise


def main() -> None:
    """Run the lake builder command-line entry point."""
    load_project_environment()
    parser = argparse.ArgumentParser(description="Build the Phase 1 data lake contracts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--forms-dir", type=Path, default=Path("data/processed/forms"))
    parser.add_argument("--git-logs", type=Path, default=Path("data/processed/git_logs_anon.csv"))
    parser.add_argument("--git-commits", type=Path, default=Path("data/processed/git_commits_anon.csv"))
    parser.add_argument("--git-files", type=Path, default=Path("data/processed/git_files_anon.csv"))
    parser.add_argument("--transcripts-dir", type=Path, default=Path("data/processed/transcripts_anon"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/lake"), help="Directory for lake artifacts")
    args = parser.parse_args()
    build_lake(args.forms_dir, args.git_commits, args.transcripts_dir, args.output_dir, args.git_files)
    logger.info("Data lake contracts written to %s", args.output_dir)


if __name__ == "__main__":
    main()