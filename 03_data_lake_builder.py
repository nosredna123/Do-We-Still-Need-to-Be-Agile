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
            row = {
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
        git_agg = git_df.groupby(["ID_Equipe", "temporal_marker"]).agg({
            "lines_added": "sum",
            "lines_deleted": "sum",
            "files_changed": "sum",
            "ID_Autor_Local": "nunique",
            "commit_hash": "count",
        }).reset_index()
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
        merged = pd.merge(
            forms_df,
            git_agg,
            on=["ID_Equipe", "temporal_marker"],
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
        description="Build unified data lake from anonymized sources"
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
        required=True,
        help="Output Parquet file path",
    )

    args = parser.parse_args()

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
    logger.info(f"Data lake complete: {len(master_df)} records")

    # Print summary
    if "ID_Equipe" in master_df.columns:
        teams = master_df["ID_Equipe"].nunique()
        logger.info(f"Master dataset contains {teams} teams")


if __name__ == "__main__":
    main()
