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
import hashlib
import json
import logging
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any
import re

import pandas as pd

from pipeline_core import (
    input_checksum,
    is_current_artifact,
    load_project_environment,
    write_artifact_metadata,
)
from pipeline_core import extract_git_events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
EMAIL_PATTERN = re.compile(r"[\w.+'%-]+@[\w.-]+\.[A-Za-z]{2,}")
GIT_CONTRACT_VERSION = "git-event-level-v1"
GIT_EXTRACTION_OPTIONS = {
    "find_renames": True,
    "nul_delimited_paths": True,
    "snapshot_policy": "cached_head_no_pull",
}


def anonymize_path_pii(value: str | None) -> str | None:
    """Replace e-mail tokens embedded in repository paths with stable hashes."""
    if value is None:
        return None

    def replace(match: re.Match[str]) -> str:
        digest = hashlib.sha256(match.group(0).encode("utf-8")).hexdigest()[:12]
        return f"anon_{digest}"

    normalized_parts = []
    for part in value.split("/"):
        if "@" in part:
            normalized_parts.append(replace(re.match(r".*", part)))
        else:
            normalized_parts.append(EMAIL_PATTERN.sub(replace, part))
    return "/".join(normalized_parts)


def normalize_text(value: Any) -> str:
    """Normalize optional scalar values from CSV rows."""
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def clone_or_update_repo(repo_url: str, cache_path: Path) -> Path:
    """Clone a repository or update if it already exists.

    Args:
        repo_url: Git repository URL
        cache_path: Path to cache directory

    Returns:
        Path to local repository.
    """
    local_path = repository_cache_path(repo_url, cache_path)

    if local_path.exists():
        logger.info("Using cached repository snapshot: %s", local_path.name)
        return local_path
    logger.info("Cloning repository: %s", repo_url)
    subprocess.run(
        ["git", "clone", repo_url, str(local_path)],
        capture_output=True,
        check=True,
        timeout=60,
    )
    return local_path


def repository_cache_path(repo_url: str, cache_path: Path) -> Path:
    """Return the deterministic local cache path for a repository URL."""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_key = hashlib.sha256(repo_url.encode("utf-8")).hexdigest()[:12]
    return cache_path / f"{repo_name}-{repo_key}"


def repository_snapshot_id(repo_path: Path) -> str:
    """Return the immutable Git commit observed in a cached repository."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    snapshot = result.stdout.strip()
    if not snapshot:
        raise ValueError(f"Repository snapshot is missing for {repo_path}")
    return snapshot


def build_git_input_checksum(
    repos_list: Path,
    snapshots: list[str],
    extraction_options: dict[str, object] | None = None,
) -> str:
    """Build a checksum covering sources, snapshots, options and contract version."""
    options = {
        "contract_version": GIT_CONTRACT_VERSION,
        "snapshots": json.dumps(sorted(snapshots), sort_keys=True),
        "extraction_options": json.dumps(
            extraction_options or GIT_EXTRACTION_OPTIONS,
            sort_keys=True,
            default=str,
        ),
    }
    return input_checksum([repos_list], options)


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
        logger.info("  %s commits -> %s", count, dev_name)

    return author_mapping


def mirror_clean_repo(repo_path: Path, clean_repos_dir: Path) -> Path:
    """Mirror a repository working tree without git metadata."""
    target_path = clean_repos_dir / repo_path.name
    if target_path.exists():
        shutil.rmtree(target_path)

    shutil.copytree(
        repo_path,
        target_path,
        ignore=shutil.ignore_patterns(".git"),
        dirs_exist_ok=True,
    )
    return target_path


def main() -> None:
    """Main entry point for Git parser."""
    load_project_environment()

    parser = argparse.ArgumentParser(
        description="Extract anonymized Git history from repositories",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--repos-list",
        type=Path,
        default=Path("data/raw/repos_list.csv"),
        help="CSV file with columns: ID_Equipe, URL_Repositorio_Fork, Semestre",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("data/processed/git_logs_anon.csv"),
        help="Output CSV file for anonymized Git logs",
    )
    parser.add_argument(
        "--output-commits",
        type=Path,
        default=Path("data/processed/git_commits_anon.csv"),
        help="Event-level anonymized commit output",
    )
    parser.add_argument(
        "--output-files",
        type=Path,
        default=Path("data/processed/git_files_anon.csv"),
        help="Event-level anonymized file output",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path("data/raw/repos_cache"),
        help="Directory to cache cloned repositories",
    )
    parser.add_argument(
        "--clean-repos-dir",
        type=Path,
        default=Path("data/processed/clean_repos"),
        help="Directory for mirrored repositories without git metadata",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate Git artifacts even when the repository list is unchanged",
    )
    args = parser.parse_args()

    logger.info("Reading repositories list from %s", args.repos_list)
    repos_df = pd.read_csv(args.repos_list)
    snapshots: list[str] = []
    for idx, row in repos_df.iterrows():
        repo_url = normalize_text(row.get("URL_Repositorio_Fork"))
        if not repo_url:
            raise ValueError(f"Repository row {idx} is missing URL_Repositorio_Fork")
        cached_path = repository_cache_path(repo_url, args.cache_dir)
        snapshots.append(
            f"{repo_url}:" + (
                repository_snapshot_id(cached_path)
                if cached_path.is_dir()
                else "missing"
            )
        )
    checksum = build_git_input_checksum(args.repos_list, snapshots)
    clean_repos_ready = args.clean_repos_dir.is_dir() and any(args.clean_repos_dir.iterdir())
    outputs = [args.output_csv, args.output_commits, args.output_files]
    if not args.force and clean_repos_ready and all(
        is_current_artifact(output, checksum) for output in outputs
    ):
        logger.info("Skipping current Git outputs")
        return

    args.cache_dir.mkdir(parents=True, exist_ok=True)
    args.clean_repos_dir.mkdir(parents=True, exist_ok=True)

    all_commit_rows: list[dict[str, Any]] = []
    all_file_rows: list[dict[str, Any]] = []

    # Process each repository
    for idx, row in repos_df.iterrows():
        team_id = normalize_text(row.get("ID_Equipe"))
        repo_url = normalize_text(row.get("URL_Repositorio_Fork"))
        semestre = normalize_text(row.get("Semestre"))

        if not team_id:
            raise ValueError(f"Repository row {idx} is missing ID_Equipe")
        if not semestre:
            raise ValueError(f"Team {team_id} is missing Semestre")
        if not repo_url:
            raise ValueError(f"{team_id} has no repository URL")

        logger.info(f"Processing: {team_id} - {repo_url}")

        # Clone or update repository
        repo_path = clone_or_update_repo(repo_url, args.cache_dir)
        mirror_path = mirror_clean_repo(repo_path, args.clean_repos_dir)
        logger.info(f"Mirrored clean repository to {mirror_path}")

        # Extract git history with team context
        commit_rows, file_rows = extract_git_events(repo_path, semestre)

        # Map authors within this team
        author_mapping = map_authors_by_volume(commit_rows)

        # Update rows with team-local author mapping
        for commit_row in commit_rows:
            author_alias = commit_row.get("author_alias")
            if not author_alias:
                raise ValueError(f"Commit metadata for team {team_id} is missing author_alias")
            commit_row["ID_Equipe"] = team_id
            commit_row["Semestre"] = str(semestre)
            if author_alias not in author_mapping:
                raise ValueError(
                    f"Team {team_id} author alias {author_alias} was not assigned a local author label"
                )
            commit_row["ID_Autor_Local"] = author_mapping[author_alias]
            commit_row.pop("author_alias", None)
            all_commit_rows.append(commit_row)

        for file_row in file_rows:
            author_alias = file_row.pop("author_alias", None)
            if not author_alias or author_alias not in author_mapping:
                raise ValueError(f"File metadata for team {team_id} is missing a mapped author")
            file_row["ID_Equipe"] = team_id
            file_row["Semestre"] = str(semestre)
            file_row["ID_Autor_Local"] = author_mapping[author_alias]
            file_row["file_path"] = anonymize_path_pii(file_row["file_path"])
            file_row["file_path_old"] = anonymize_path_pii(file_row.get("file_path_old"))
            file_row["file_extension"] = Path(file_row["file_path"]).suffix.lower()
            all_file_rows.append(file_row)

    logger.info(f"Extracted {len(all_commit_rows)} total commits")

    if all_commit_rows:
        output_df = pd.DataFrame(all_commit_rows)
        files_df = pd.DataFrame(all_file_rows, columns=[
            "repository", "commit_hash", "timestamp", "temporal_marker",
            "ID_Equipe", "Semestre", "ID_Autor_Local", "file_path",
            "file_path_old", "file_extension", "change_status", "lines_added",
            "lines_deleted", "is_binary", "branch_or_ref", "branch_or_ref_source",
        ])

        # Ensure output directory exists
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)

        output_df.to_csv(args.output_csv, index=False)
        args.output_commits.parent.mkdir(parents=True, exist_ok=True)
        args.output_files.parent.mkdir(parents=True, exist_ok=True)
        output_df.to_csv(args.output_commits, index=False)
        files_df.to_csv(args.output_files, index=False)
        write_artifact_metadata(args.output_csv, checksum)
        write_artifact_metadata(args.output_commits, checksum)
        write_artifact_metadata(args.output_files, checksum)
        logger.info(f"Wrote Git logs to {args.output_csv}")
    else:
        raise RuntimeError("No commits extracted from repositories")

    logger.info("Git parsing complete")


if __name__ == "__main__":
    main()
