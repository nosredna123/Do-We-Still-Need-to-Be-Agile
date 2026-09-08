#!/usr/bin/env python3
"""Data Lake Builder: Unify anonymized sources into master dataset.

This script consolidates multiple data sources (anonymized forms, Git logs,
transcripts) into a single normalized Parquet data lake, aligned by team
and temporal markers (T1, T2, T3).

Usage:
    python 03_data_lake_builder.py \
        --forms-dir data/processed/forms/ \
        --git-logs data/processed/git_logs_anon.csv \
        --output-parquet data/lake/master_dataset.parquet
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from pipeline_config import EVALUATOR_TEMPORAL_CUTS, temporal_marker_for
from pipeline_core import (
    input_checksum,
    is_current_artifact,
    load_project_environment,
    write_artifact_metadata,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def normalize_temporal_marker(text: str) -> Optional[str]:
    """Extract temporal marker (T1, T2, T3) from text.

    Args:
        text: Text that may contain temporal marker

    Returns:
        'T1', 'T2', 'T3', or None
    """
    text_upper = str(text).upper()
    for marker in ["T1", "T2", "T3"]:
        if marker in text_upper:
            return marker
    return None


def require_columns(df: pd.DataFrame, required: list[str], label: str) -> None:
    """Validate that a DataFrame contains all required analytical columns."""
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")

    for column in required:
        values = df[column].dropna()
        if values.empty:
            raise ValueError(f"{label} has no non-null values for required column {column}")
        if values.astype(str).str.strip().eq("").any():
            raise ValueError(f"{label} contains blank values in required column {column}")


def parse_evaluator_team_id(raw_value: object) -> str:
    """Convert evaluator group labels like 'Group 4 (Team Name)' to TEAM_04."""
    text = str(raw_value or "").strip()
    match = re.search(r"Group\s+(\d+)", text, flags=re.IGNORECASE)
    if not match:
        raise ValueError(f"Evaluator group label is not in the expected format: {raw_value!r}")
    return f"TEAM_{int(match.group(1)):02d}"


def student_temporal_marker_for_filename(csv_file: Path) -> str:
    """Derive the temporal marker from a student CSV filename such as alunos_t1.csv."""
    lower_name = csv_file.stem.lower()
    match = re.search(r"t([123])", lower_name)
    if not match:
        raise ValueError(f"Student form file {csv_file} must include a temporal marker like alunos_t1.csv")
    return f"T{match.group(1)}"


def transcript_temporal_marker_for_filename(transcript_file: Path, semester: str) -> str:
    """Derive a transcript cut from an observable date in its filename."""
    full_date = re.search(r"(20\d{2}-\d{2}-\d{2})", transcript_file.stem)
    if full_date:
        evaluation_date = full_date.group(1)
    else:
        short_date = re.search(r"(?:MyRec_)?(\d{2})(\d{2})", transcript_file.stem)
        if not short_date:
            raise ValueError(
                f"Transcript {transcript_file} has no observable ISO or MMDD date"
            )
        year = semester.split(".")[0]
        evaluation_date = f"{year}-{short_date.group(1)}-{short_date.group(2)}"

    for marker, (start_date, end_date) in EVALUATOR_TEMPORAL_CUTS[semester].items():
        if start_date <= evaluation_date <= end_date:
            return marker
    raise ValueError(
        f"Transcript date {evaluation_date} is not in a configured cut for {semester}"
    )


def load_form_files(forms_dir: Path) -> pd.DataFrame:
    """Load and normalize student/evaluator form CSVs under the Phase 1 schema."""
    dfs = []

    for csv_file in sorted(forms_dir.rglob("*.csv")):
        logger.info(f"Loading form: {csv_file}")
        df = pd.read_csv(csv_file)
        semester = csv_file.parent.name
        if "alunos" in csv_file.stem.lower():
            df = df.copy()
            df["Semestre"] = str(semester)
            df["temporal_marker"] = student_temporal_marker_for_filename(csv_file)
            df["source_type"] = "student_response"
            require_columns(df, ["Semestre", "temporal_marker"], f"student form {csv_file}")
            dfs.append(df)
            continue

        if {"Timestamp", "To which group do these scores refer?"}.issubset(df.columns):
            df = df.copy()
            df["Semestre"] = str(semester)
            df["ID_Equipe"] = df["To which group do these scores refer?"].map(parse_evaluator_team_id)
            df["temporal_marker"] = df["Timestamp"].map(
                lambda value: temporal_marker_for(
                    semester,
                    pd.to_datetime(value, dayfirst=False).strftime("%Y-%m-%d"),
                )
            )
            df["source_type"] = "evaluator_team_cut"
            require_columns(df, ["ID_Equipe", "Semestre", "temporal_marker"], f"evaluator form {csv_file}")
            dfs.append(df)
            continue

        raise ValueError(
            f"Form file {csv_file} does not match the Phase 1 schema for students or evaluators"
        )

    if not dfs:
        return pd.DataFrame()

    forms_df = pd.concat(dfs, ignore_index=True)
    return forms_df


def load_git_logs(git_csv_path: Path) -> pd.DataFrame:
    """Load anonymized Git logs.

    Args:
        git_csv_path: Path to git_logs_anon.csv

    Returns:
        DataFrame with Git history
    """
    if not git_csv_path.exists():
        raise FileNotFoundError(f"Git logs file not found: {git_csv_path}")

    logger.info(f"Loading Git logs from {git_csv_path}")
    df = pd.read_csv(git_csv_path)
    require_columns(df, ["ID_Equipe", "Semestre", "temporal_marker"], "git logs")
    df["Semestre"] = df["Semestre"].astype("string").str.strip()
    if df["Semestre"].isna().any() or df["Semestre"].eq("").any():
        raise ValueError("git logs contains blank values in required column Semestre")
    return df


def load_transcripts(transcripts_dir: Path) -> pd.DataFrame:
    """Load and index transcript JSON files.

    Args:
        transcripts_dir: Directory containing transcription JSON files

    Returns:
        DataFrame with transcript metadata and text
    """
    rows = []

    for json_file in transcripts_dir.rglob("*.json"):
        if json_file.name.endswith(".metadata.json"):
            continue
        data = json.loads(json_file.read_text(encoding="utf-8"))
        semester = data.get("Semestre") or json_file.parent.parent.name
        if not semester or semester not in EVALUATOR_TEMPORAL_CUTS:
            raise ValueError(f"Transcript {json_file} lacks a valid Semestre")
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Transcript {json_file} lacks non-empty text")
        row = {
            "ID_Equipe": data.get("ID_Equipe"),
            "Semestre": semester,
            "source_type": "transcript_session",
            "session_id": str(json_file.parent.relative_to(transcripts_dir)),
            "transcript_file": str(json_file.relative_to(transcripts_dir)),
            "transcript_text": text,
            "status": data.get("status"),
            "temporal_marker": normalize_temporal_marker(json_file.stem)
            or transcript_temporal_marker_for_filename(json_file, semester),
        }
        if not row["status"]:
            raise ValueError(f"Transcript {json_file} lacks status")
        rows.append(row)

    if rows:
        df = pd.DataFrame(rows)
        require_columns(df, ["Semestre", "temporal_marker", "session_id"], "transcripts")
        return df
    return pd.DataFrame()


def source_paths(
    forms_dir: Path,
    git_logs_path: Path,
    transcripts_dir: Path,
) -> list[Path]:
    """Collect existing files that contribute to the master dataset."""
    paths = [git_logs_path] if git_logs_path.exists() else []
    if forms_dir.exists():
        paths.extend(forms_dir.rglob("*.csv"))
    if transcripts_dir.exists():
        paths.extend(
            path
            for path in transcripts_dir.rglob("*.json")
            if not path.name.endswith(".metadata.json")
        )
    return paths


def merge_transcripts(
    master_df: pd.DataFrame,
    transcripts_df: pd.DataFrame,
) -> pd.DataFrame:
    """Attach transcript data to keyed team rows."""
    if transcripts_df.empty:
        return master_df.copy()

    group_keys = ["ID_Equipe", "Semestre"]
    if "temporal_marker" in transcripts_df.columns:
        group_keys.append("temporal_marker")

    transcript_agg = (
        transcripts_df.groupby(group_keys, dropna=False)
        .agg(
            {
                "transcript_file": lambda values: " | ".join(
                    str(value)
                    for value in values
                    if pd.notna(value) and str(value)
                ),
                "transcript_text": lambda values: "\n\n".join(
                    str(value)
                    for value in values
                    if pd.notna(value) and str(value)
                ),
                "status": lambda values: ",".join(
                    sorted(
                        {
                            str(value)
                            for value in values
                            if pd.notna(value) and str(value)
                        }
                    )
                ),
            }
        )
        .reset_index()
    )

    if master_df.empty:
        return transcript_agg

    merge_keys = ["ID_Equipe", "Semestre"]
    if "temporal_marker" in master_df.columns or "temporal_marker" in transcript_agg.columns:
        if "temporal_marker" not in master_df.columns:
            master_df = master_df.copy()
            master_df["temporal_marker"] = None
        if "temporal_marker" not in transcript_agg.columns:
            transcript_agg = transcript_agg.copy()
            transcript_agg["temporal_marker"] = None
        merge_keys.append("temporal_marker")

    return pd.merge(
        master_df,
        transcript_agg,
        on=merge_keys,
        how="outer",
    )


def aggregate_by_team(
    forms_df: pd.DataFrame,
    git_df: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate data by team and temporal markers.

    This performs a merge on ID_Equipe and temporal markers to align
    form responses with Git activity.

    Args:
        forms_df: Form data
        git_df: Git log data

    Returns:
        Merged DataFrame
    """
    if forms_df.empty and git_df.empty:
        logger.warning("No data to aggregate")
        return pd.DataFrame()

    for df, label in [(forms_df, "forms"), (git_df, "git")]:
        if df.empty:
            continue

        if label == "git":
            required = ["ID_Equipe", "Semestre", "temporal_marker"]
        else:
            required = ["temporal_marker"]
            if "Semestre" in df.columns:
                required.append("Semestre")
            if "ID_Equipe" in df.columns:
                required.append("ID_Equipe")

        missing = [column for column in required if column not in df.columns]
        if missing:
            raise ValueError(f"{label.title()} data is missing required columns: {', '.join(missing)}")

        for column in required:
            values = df[column].dropna()
            if values.empty:
                raise ValueError(f"{label.title()} data has no non-null values for required column {column}")
            if values.astype(str).str.strip().eq("").any():
                raise ValueError(f"{label.title()} data contains blank values in required column {column}")

    if not git_df.empty:
        group_keys = ["ID_Equipe", "temporal_marker"]
        if "Semestre" in git_df.columns:
            group_keys.append("Semestre")
        git_agg = (
            git_df.groupby(group_keys)
            .agg(
                {
                    "lines_added": "sum",
                    "lines_deleted": "sum",
                    "files_changed": "sum",
                    "ID_Autor_Local": "nunique",
                    "commit_hash": "count",
                }
            )
            .reset_index()
        )
        git_agg.rename(
            columns={
                "ID_Autor_Local": "num_authors",
                "commit_hash": "num_commits",
            },
            inplace=True,
        )
    else:
        git_agg = pd.DataFrame()

    if forms_df.empty:
        git_agg["source_type"] = "git_team_cut"
        return git_agg

    if "Semestre" not in forms_df.columns and "Semestre" in git_agg.columns:
        merged = forms_df.copy()
        for column in git_agg.columns:
            if column not in merged.columns:
                merged[column] = pd.NA
        for column in [
            "lines_added",
            "lines_deleted",
            "files_changed",
            "num_authors",
            "num_commits",
        ]:
            if column in merged.columns:
                merged[column] = pd.NA
        return merged

    if "ID_Equipe" in forms_df.columns:
        student_rows = forms_df[forms_df["ID_Equipe"].isna()].copy()
        evaluator_rows = forms_df[forms_df["ID_Equipe"].notna()].copy()
    else:
        student_rows = forms_df.copy()
        evaluator_rows = pd.DataFrame()

    if not evaluator_rows.empty and not git_agg.empty:
        merge_keys = ["ID_Equipe", "temporal_marker"]
        if "Semestre" in evaluator_rows.columns and "Semestre" in git_agg.columns:
            merge_keys.append("Semestre")
        merged_evaluator = pd.merge(
            evaluator_rows,
            git_agg,
            on=merge_keys,
            how="left",
        )
    elif not evaluator_rows.empty:
        merged_evaluator = evaluator_rows.copy()
    else:
        merged_evaluator = pd.DataFrame()

    if not student_rows.empty:
        if merged_evaluator.empty:
            return student_rows
        return pd.concat([student_rows, merged_evaluator], ignore_index=True)

    return merged_evaluator


def main() -> None:
    """Main entry point for data lake builder."""
    load_project_environment()

    parser = argparse.ArgumentParser(
        description="Build unified data lake from anonymized sources",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--forms-dir",
        type=Path,
        default=Path("data/processed/forms"),
        help="Directory with anonymized form CSVs",
    )
    parser.add_argument(
        "--git-logs",
        type=Path,
        default=Path("data/processed/git_logs_anon.csv"),
        help="Path to anonymized Git logs CSV",
    )
    parser.add_argument(
        "--transcripts-dir",
        type=Path,
        default=Path("data/processed/transcripts_anon"),
        help="Directory with transcript JSON files",
    )
    parser.add_argument(
        "--output-parquet",
        type=Path,
        default=Path("data/lake/master_dataset.parquet"),
        help="Output Parquet file path",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild the data lake even when all source inputs are unchanged",
    )

    args = parser.parse_args()

    checksum = input_checksum(
        source_paths(args.forms_dir, args.git_logs, args.transcripts_dir), {}
    )
    if not args.force and is_current_artifact(args.output_parquet, checksum):
        logger.info("Skipping current data lake output: %s", args.output_parquet)
        return

    logger.info("Building data lake...")

    # Load all data sources
    forms_df = (
        load_form_files(args.forms_dir)
        if args.forms_dir.exists()
        else pd.DataFrame()
    )
    git_df = load_git_logs(args.git_logs)
    transcripts_df = (
        load_transcripts(args.transcripts_dir)
        if args.transcripts_dir.exists()
        else pd.DataFrame()
    )

    logger.info(f"Loaded {len(forms_df)} form records")
    logger.info(f"Loaded {len(git_df)} git records")
    logger.info(f"Loaded {len(transcripts_df)} transcript records")

    # Aggregate by team
    master_df = aggregate_by_team(forms_df, git_df)

    if not transcripts_df.empty:
        keyed_transcripts = transcripts_df[transcripts_df["ID_Equipe"].notna()].copy()
        session_transcripts = transcripts_df[transcripts_df["ID_Equipe"].isna()].copy()
        if not keyed_transcripts.empty:
            master_df = merge_transcripts(master_df, keyed_transcripts)
        if not session_transcripts.empty:
            master_df = pd.concat([master_df, session_transcripts], ignore_index=True, sort=False)

    # Normalize temporal markers
    if "temporal_marker" in master_df.columns:
        master_df["temporal_marker"] = master_df[
            "temporal_marker"
        ].apply(normalize_temporal_marker)

    # Ensure output directory exists
    args.output_parquet.parent.mkdir(parents=True, exist_ok=True)

    # Write master dataset
    logger.info(f"Writing master dataset to {args.output_parquet}")
    master_df.to_parquet(args.output_parquet, index=False)
    write_artifact_metadata(args.output_parquet, checksum)
    logger.info(f"Data lake complete: {len(master_df)} records")

    # Print summary
    if "ID_Equipe" in master_df.columns:
        teams = master_df["ID_Equipe"].nunique()
        logger.info(f"Master dataset contains {teams} teams")


if __name__ == "__main__":
    main()
