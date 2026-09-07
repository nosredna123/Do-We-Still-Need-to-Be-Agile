#!/usr/bin/env python3
"""Git repository parser with intra-team author anonymization.

This script clones repositories from a list, extracts commit history,
and anonymizes authors based on relative volume of contributions within
each team (mapping to Dev_A, Dev_B, etc. based on commit count).

Usage:
    python 02_git_parser.py --repos-list repos_list.csv \
        --output-csv git_logs_anon.csv --cache-dir data/raw/repos_cache/
"""

from __future__ import annotations

import argparse
import logging
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from pipeline_core import extract_git_history

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def normalize_text(value: Any) -> str:
    """Normalize optional scalar values from CSV rows."""
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def clone_or_update_repo(repo_url: str, cache_path: Path) -> Optional[Path]:
    """Clone a repository or update if it already exists.

    Args:
        repo_url: Git repository URL
        cache_path: Path to cache directory

    Returns:
        Path to local repository, or None if failed
    """
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    local_path = cache_path / repo_name

    if local_path.exists():
        logger.info(f"Updating cached repository: {repo_name}")
        try:
            subprocess.run(
                ["git", "pull"],
                cwd=local_path,
                capture_output=True,
                check=True,
                timeout=30,
            )
            return local_path
        except Exception as e:
            logger.warning(f"Failed to update {repo_name}: {e}")
            return local_path
    else:
        logger.info(f"Cloning repository: {repo_url}")
        try:
            subprocess.run(
                ["git", "clone", repo_url, str(local_path)],
                capture_output=True,
                check=True,
                timeout=60,
            )
            return local_path
        except Exception as e:
            logger.error(f"Failed to clone {repo_url}: {e}")
            return None


def author_label(index: int) -> str:
    """Build spreadsheet-style author labels: A..Z, AA..AZ, etc."""
    label = ""
    index += 1
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        label = chr(65 + remainder) + label
    return f"Dev_{label}"


def map_authors_by_volume(
    commit_rows: list[dict[str, Any]],
) -> dict[str, str]:
    """Map authors to Dev_A, Dev_B, etc. based on commit volume.

    Args:
        commit_rows: List of commit records with author_alias

    Returns:
        Mapping of author alias -> Dev_X designation
    """
    alias_counts: dict[str, int] = defaultdict(int)

    for row in commit_rows:
        author_alias = row.get("author_alias", "unknown")
        alias_counts[author_alias] += 1

    # Sort by commit count (descending)
    sorted_aliases = sorted(alias_counts.items(), key=lambda x: x[1], reverse=True)

    author_mapping = {}
    for idx, (author_alias, count) in enumerate(sorted_aliases):
        # Map to Dev_A, Dev_B, Dev_C, etc.
        dev_name = author_label(idx)
        author_mapping[author_alias] = dev_name
        logger.info(f"  {author_alias} ({count} commits) -> {dev_name}")

    return author_mapping


def main() -> None:
    """Main entry point for Git parser."""
    parser = argparse.ArgumentParser(
        description="Extract anonymized Git history from repositories"
    )
    parser.add_argument(
        "--repos-list",
        type=Path,
        required=True,
        help="CSV file with columns: ID_Equipe, URL_Repositorio_Fork, Semestre",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        required=True,
        help="Output CSV file for anonymized Git logs",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("data/raw/repos_cache"),
        help="Directory to cache cloned repositories",
    )
    args = parser.parse_args()

    # Read repositories list
    logger.info(f"Reading repositories list from {args.repos_list}")
    repos_df = pd.read_csv(args.repos_list)

    args.cache_dir.mkdir(parents=True, exist_ok=True)

    all_commit_rows = []

    # Process each repository
    for idx, row in repos_df.iterrows():
        team_id = normalize_text(row.get("ID_Equipe")) or f"TEAM_{idx}"
        repo_url = normalize_text(row.get("URL_Repositorio_Fork"))
        semestre = normalize_text(row.get("Semestre"))

        if not repo_url:
            logger.warning(f"Skipping {team_id}: missing repository URL")
            continue

        logger.info(f"Processing: {team_id} - {repo_url}")

        # Clone or update repository
        repo_path = clone_or_update_repo(repo_url, args.cache_dir)
        if not repo_path:
            logger.warning(f"Skipping {team_id}: failed to clone/access repository")
            continue

        # Extract git history with team context
        commit_rows = extract_git_history(repo_path, {}, salt="")

        # Map authors within this team
        author_mapping = map_authors_by_volume(commit_rows)

        # Update rows with team-local author mapping
        for commit_row in commit_rows:
            author_alias = commit_row.get("author_alias", "unknown")
            commit_row["ID_Equipe"] = team_id
            commit_row["Semestre"] = semestre
            commit_row["ID_Autor_Local"] = author_mapping.get(author_alias, "unknown")
            commit_row.pop("author_alias", None)
            commit_row.pop("author_email", None)

            all_commit_rows.append(commit_row)

    logger.info(f"Extracted {len(all_commit_rows)} total commits")

    # Write to CSV
    if all_commit_rows:
        output_df = pd.DataFrame(all_commit_rows)

        # Ensure output directory exists
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)

        output_df.to_csv(args.output_csv, index=False)
        logger.info(f"Wrote Git logs to {args.output_csv}")
    else:
        logger.warning("No commits extracted from repositories")

    logger.info("Git parsing complete")


if __name__ == "__main__":
    main()
