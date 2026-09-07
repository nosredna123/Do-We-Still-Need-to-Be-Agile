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
from pathlib import Path
from typing import Optional

import pandas as pd

from pipeline_core import input_checksum, is_current_artifact, write_artifact_metadata

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


def load_form_files(forms_dir: Path) -> pd.DataFrame:
    """Load and concatenate all anonymized form CSVs.

    Args:
        forms_dir: Directory containing form CSV files

    Returns:
        Combined DataFrame from all forms
    """
    dfs = []

    for csv_file in forms_dir.glob("*.csv"):
        logger.info(f"Loading form: {csv_file.name}")
        try:
            df = pd.read_csv(csv_file)
            # Infer temporal marker from filename
            temporal = normalize_temporal_marker(csv_file.stem)
            if temporal:
                df["temporal_marker"] = temporal

            dfs.append(df)
        except Exception as e:
            logger.warning(f"Failed to load {csv_file}: {e}")

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()


def load_git_logs(git_csv_path: Path) -> pd.DataFrame:
    """Load anonymized Git logs.

    Args:
        git_csv_path: Path to git_logs_anon.csv

    Returns:
        DataFrame with Git history
    """
    if git_csv_path.exists():
        logger.info(f"Loading Git logs from {git_csv_path}")
        df = pd.read_csv(git_csv_path)
        return df
    else:
        logger.warning(f"Git logs file not found: {git_csv_path}")
        return pd.DataFrame()


def load_transcripts(transcripts_dir: Path) -> pd.DataFrame:
    """Load and index transcript JSON files.

    Args:
        transcripts_dir: Directory containing transcription JSON files

    Returns:
        DataFrame with transcript metadata and text
    """
    rows = []

    for json_file in transcripts_dir.glob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            team_id = data.get("ID_Equipe")
            semester = data.get("Semestre")
            if not team_id or not semester:
                logger.warning(
                    "Skipping transcript %s without required ID_Equipe/Semestre metadata",
                    json_file,
                )
                continue
            row = {
                "ID_Equipe": team_id,
                "Semestre": semester,
                "transcript_file": json_file.name,
                "transcript_text": data.get("text", ""),
                "status": data.get("status", "unknown"),
            }
            temporal = normalize_temporal_marker(json_file.stem)
            if temporal:
                row["temporal_marker"] = temporal

            rows.append(row)
        except Exception as e:
            logger.warning(f"Failed to load transcript {json_file}: {e}")

    if rows:
        return pd.DataFrame(rows)
    else:
        return pd.DataFrame()


def source_paths(
    forms_dir: Path,
    git_logs_path: Path,
    transcripts_dir: Path,
) -> list[Path]:
    """Collect existing files that contribute to the master dataset."""
    paths = [git_logs_path] if git_logs_path.exists() else []
    if forms_dir.exists():
        paths.extend(forms_dir.glob("*.csv"))
    if transcripts_dir.exists():
        paths.extend(
            path
            for path in transcripts_dir.glob("*.json")
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

    # Ensure both have temporal markers
    if "temporal_marker" not in forms_df.columns:
        forms_df["temporal_marker"] = "T1"
    if "temporal_marker" not in git_df.columns:
        git_df["temporal_marker"] = "T1"

    # Aggregate Git data by team
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

    # Merge forms with Git data
    if not forms_df.empty and not git_agg.empty:
        merge_keys = ["ID_Equipe", "temporal_marker"]
        if "Semestre" in forms_df.columns or "Semestre" in git_agg.columns:
            if "Semestre" not in forms_df.columns:
                forms_df = forms_df.copy()
                forms_df["Semestre"] = ""
            if "Semestre" not in git_agg.columns:
                git_agg = git_agg.copy()
                git_agg["Semestre"] = ""
            merge_keys.append("Semestre")
        merged = pd.merge(
            forms_df,
            git_agg,
            on=merge_keys,
            how="left",
        )
    elif not forms_df.empty:
        merged = forms_df.copy()
    else:
        merged = git_agg

    return merged


def main() -> None:
    """Main entry point for data lake builder."""
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
        default=Path("data/processed/transcripts"),
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
        master_df = merge_transcripts(master_df, transcripts_df)

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
