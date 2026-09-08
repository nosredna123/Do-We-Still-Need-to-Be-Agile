#!/usr/bin/env python3
"""Build the Phase 1 data lake as four independent Parquet contracts."""

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

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
VALID_MARKERS = {"T1", "T2", "T3"}
DATASET_NAMES = ("student_responses", "evaluator_team_cuts", "git_team_cuts", "transcript_sessions")
KEY_COLUMNS = ["ID_Equipe", "Semestre", "temporal_marker"]


def normalize_temporal_marker(value: object) -> str:
    """Validate and return an explicit temporal marker."""
    marker = str(value).strip().upper()
    if marker not in VALID_MARKERS:
        raise ValueError(f"Invalid temporal_marker {value!r}; expected T1, T2 or T3")
    return marker


def require_columns(df: pd.DataFrame, required: list[str], label: str) -> None:
    """Require non-empty values for every column in a source contract."""
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")
    for column in required:
        values = df[column]
        if values.isna().any() or values.astype(str).str.strip().eq("").any():
            raise ValueError(f"{label} contains missing or blank values in {column}")


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
    if match is not None:
        return temporal_marker_for(semester, match.group(1))
    short_date = re.search(r"(?:MyRec_)?(\d{2})(\d{2})", transcript_file.stem)
    if short_date is None:
        raise ValueError(f"Transcript {transcript_file} lacks an observable date")
    evaluation_date = f"{semester.split('.')[0]}-{short_date.group(1)}-{short_date.group(2)}"
    return temporal_marker_for(semester, evaluation_date)


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
            frame["temporal_marker"] = frame["Timestamp"].map(
                lambda value, current_semester=semester: temporal_marker_for(current_semester, pd.to_datetime(value).strftime("%Y-%m-%d"))
            )
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


def load_git_logs(git_csv_path: Path) -> pd.DataFrame:
    """Load and validate anonymized Git activity rows."""
    if not git_csv_path.is_file():
        raise FileNotFoundError(f"Git logs file not found: {git_csv_path}")
    frame = pd.read_csv(git_csv_path)
    required = KEY_COLUMNS + ["lines_added", "lines_deleted", "files_changed", "ID_Autor_Local", "commit_hash"]
    require_columns(frame, required, "git logs")
    frame["Semestre"] = frame["Semestre"].astype("string")
    frame["temporal_marker"] = frame["temporal_marker"].map(normalize_temporal_marker)
    for column in ["lines_added", "lines_deleted", "files_changed"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if frame[column].isna().any() or (frame[column] < 0).any():
            raise ValueError(f"git logs has invalid numeric values in {column}")
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
        rows.append({"session_id": str(json_file.parent.relative_to(transcripts_dir)),
                     "transcript_file": str(json_file.relative_to(transcripts_dir)),
                     "Semestre": semester, "temporal_marker": normalize_temporal_marker(marker),
                     "temporal_marker_source": marker_source, "transcript_text": text,
                     "status": data.get("status") or "success", "source_type": "transcript_session"})
    if not rows:
        raise ValueError(f"Transcripts directory contains no JSON sources: {transcripts_dir}")
    result = pd.DataFrame(rows)
    require_columns(result, ["session_id", "transcript_file", "Semestre", "temporal_marker", "status"], "transcripts")
    if result.duplicated(["session_id", "transcript_file"]).any():
        raise ValueError("transcripts contain duplicate session_id and transcript_file keys")
    return result


def _ensure_unique_keys(frame: pd.DataFrame, keys: list[str], label: str) -> None:
    """Reject duplicate analytical keys."""
    if frame.duplicated(keys).any():
        raise ValueError(f"{label} contains duplicate analytical keys")


def aggregate_git_cuts(git_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate Git activity by team, semester and temporal cut."""
    require_columns(git_df, KEY_COLUMNS, "git logs")
    result = git_df.groupby(KEY_COLUMNS, as_index=False).agg(
        lines_added=("lines_added", "sum"), lines_deleted=("lines_deleted", "sum"),
        files_changed=("files_changed", "sum"), num_authors=("ID_Autor_Local", "nunique"),
        num_commits=("commit_hash", "count"))
    result["source_type"] = "git_team_cut"
    _ensure_unique_keys(result, KEY_COLUMNS, "git cuts")
    return result


def aggregate_evaluator_cuts(forms_df: pd.DataFrame, git_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate evaluator responses and attach only Git match status."""
    require_columns(forms_df, ["Semestre", "temporal_marker", "source_type"], "forms")
    evaluator = forms_df[forms_df["source_type"] == "evaluator_team_cut"].copy()
    if evaluator.empty:
        raise ValueError("No evaluator responses were found")
    require_columns(evaluator, KEY_COLUMNS, "evaluator forms")
    numeric = [column for column in evaluator.columns if column.lower().startswith("score")]
    aggregations: dict[str, str] = {column: "mean" for column in numeric}
    if "source_file" in evaluator.columns:
        aggregations["source_file"] = "first"
    result = evaluator.groupby(KEY_COLUMNS, as_index=False).agg(aggregations)
    git_keys = aggregate_git_cuts(git_df)[KEY_COLUMNS] if not git_df.empty else pd.DataFrame(columns=KEY_COLUMNS)
    observed = set(map(tuple, git_keys[KEY_COLUMNS].itertuples(index=False, name=None)))
    result["git_match_status"] = ["matched" if tuple(row) in observed else "no_observed_activity" for row in result[KEY_COLUMNS].itertuples(index=False, name=None)]
    result["source_type"] = "evaluator_team_cut"
    _ensure_unique_keys(result, KEY_COLUMNS, "evaluator cuts")
    return result


def source_paths(forms_dir: Path, git_logs_path: Path, transcripts_dir: Path) -> list[Path]:
    """Return all effective source files for checksum calculation."""
    paths = [git_logs_path, *sorted(forms_dir.rglob("*.csv"))]
    paths.extend(path for path in sorted(transcripts_dir.rglob("*.json")) if not path.name.endswith(".metadata.json"))
    return paths


def validation_report(outputs: dict[str, pd.DataFrame], artifacts: dict[str, Path]) -> dict[str, Any]:
    """Create a PII-free validation summary for generated contracts."""
    evaluator = outputs["evaluator_team_cuts"]
    pii_status = "passed"
    email_pattern = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")
    identifier_tokens = ("email", "nome", "name")
    for frame in outputs.values():
        for column in frame.select_dtypes(include=["object", "string"]).columns:
            values = frame[column].dropna().astype(str)
            if values.str.contains(email_pattern, regex=True).any():
                pii_status = "failed"
            if any(token in column.lower() for token in identifier_tokens):
                if values[~values.str.startswith("anon_")].size:
                    pii_status = "failed"
    datasets: dict[str, Any] = {}
    for name, frame in outputs.items():
        datasets[name] = {"rows": len(frame), "schema": {c: str(t) for c, t in frame.dtypes.items()},
                          "semesters": sorted(frame["Semestre"].astype(str).unique().tolist()),
                          "temporal_markers": sorted(frame["temporal_marker"].astype(str).unique().tolist()),
                          "duplicate_key_count": int(frame.duplicated(KEY_COLUMNS).sum()) if set(KEY_COLUMNS).issubset(frame.columns) else 0,
                          "artifact": str(artifacts[name])}
    return {"status": "success", "datasets": datasets,
            "git_match_status": evaluator["git_match_status"].value_counts().to_dict(),
            "evaluator_keys_without_git": evaluator.loc[evaluator["git_match_status"] == "no_observed_activity", KEY_COLUMNS].astype(str).to_dict("records"),
            "pii_status": pii_status, "sidecars_status": "success"}


def build_lake(forms_dir: Path, git_logs_path: Path, transcripts_dir: Path, output_dir: Path) -> dict[str, Path]:
    """Load, validate and atomically write the four Phase 1 lake contracts."""
    forms, git, transcripts = load_form_files(forms_dir), load_git_logs(git_logs_path), load_transcripts(transcripts_dir)
    outputs = {"student_responses": forms[forms["source_type"] == "student_response"].drop(columns=["ID_Equipe"], errors="ignore"),
               "evaluator_team_cuts": aggregate_evaluator_cuts(forms, git), "git_team_cuts": aggregate_git_cuts(git),
               "transcript_sessions": transcripts}
    checksum = input_checksum(source_paths(forms_dir, git_logs_path, transcripts_dir), {"contracts": DATASET_NAMES})
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
            Path(f"{path}.metadata.json").unlink(missing_ok=True)
        raise


def main() -> None:
    """Run the lake builder command-line entry point."""
    load_project_environment()
    parser = argparse.ArgumentParser(description="Build the Phase 1 data lake contracts", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--forms-dir", type=Path, default=Path("data/processed/forms"), help="Directory with anonymized forms")
    parser.add_argument("--git-logs", type=Path, default=Path("data/processed/git_logs_anon.csv"), help="Anonymized Git log CSV")
    parser.add_argument("--transcripts-dir", type=Path, default=Path("data/processed/transcripts_anon"), help="Directory with anonymized transcripts")
    parser.add_argument("--output-dir", type=Path, default=Path("data/lake"), help="Directory for the four lake contracts")
    parser.add_argument("--force", action="store_true", help="Regenerate all lake contracts")
    args = parser.parse_args()
    build_lake(args.forms_dir, args.git_logs, args.transcripts_dir, args.output_dir)
    logger.info("Data lake contracts written to %s", args.output_dir)


if __name__ == "__main__":
    main()