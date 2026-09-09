#!/usr/bin/env python3
"""Build repository structural snapshots for Phase 1.5."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from pipeline_config import (
    EVALUATOR_TEMPORAL_CUTS,
    EXCLUDED_PATH_PATTERNS_VERSION,
    REPOSITORY_SNAPSHOT_CONTRACT_VERSION,
    SOURCE_CODE_EXCLUDED_PATH_PATTERNS,
    SOURCE_CODE_EXTENSION_ALLOWLIST,
    SOURCE_LOC_DEFINITION_VERSION,
)
from pipeline_core import artifact_metadata_path, input_checksum, is_current_artifact, load_project_environment

logger = logging.getLogger(__name__)
KEY_COLUMNS = ["ID_Equipe", "Semestre", "temporal_marker", "repository"]
COMMIT_REQUIRED_COLUMNS = KEY_COLUMNS + ["commit_hash", "timestamp"]
REPOS_REQUIRED_COLUMNS = ["ID_Equipe", "URL_Repositorio_Fork", "Semestre"]
VALID_MARKERS = {"T1", "T2", "T3"}


def normalize_text(value: object) -> str:
    """Return a stripped scalar string or an empty string for null values."""
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def repository_cache_path(repo_url: str, cache_path: Path) -> Path:
    """Return the deterministic local cache path used by the Git parser."""
    repo_name = repo_url.split("/")[-1].replace(".git", "")
    repo_key = hashlib.sha256(repo_url.encode("utf-8")).hexdigest()[:12]
    return cache_path / f"{repo_name}-{repo_key}"


def repository_snapshot_id(repo_path: Path) -> str:
    """Return the current cached repository HEAD used for checksum invalidation."""
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


def require_columns(frame: pd.DataFrame, required: list[str], label: str) -> None:
    """Fail when a DataFrame lacks required columns or contains blank values."""
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {', '.join(missing)}")
    for column in required:
        values = frame[column]
        if values.isna().any() or values.astype(str).str.strip().eq("").any():
            raise ValueError(f"{label} contains missing or blank values in {column}")


def _run_git(repo_path: Path, args: list[str]) -> bytes:
    """Run a Git command and return stdout bytes."""
    return subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        check=True,
    ).stdout


def _tree_entries(repo_path: Path, commit_hash: str) -> list[dict[str, Any]]:
    """Return NUL-delimited Git tree entries for one commit."""
    output = _run_git(repo_path, ["ls-tree", "-r", "-l", "-z", commit_hash])
    rows: list[dict[str, Any]] = []
    for raw_entry in output.split(b"\0"):
        if not raw_entry:
            continue
        metadata, raw_path = raw_entry.split(b"\t", 1)
        parts = metadata.decode("utf-8", errors="strict").split()
        if len(parts) < 4:
            raise ValueError(f"Malformed Git tree entry for {commit_hash}")
        size = None if parts[3] == "-" else int(parts[3])
        rows.append(
            {
                "mode": parts[0],
                "object_type": parts[1],
                "object_hash": parts[2],
                "size": size,
                "path": raw_path.decode("utf-8", errors="strict"),
            }
        )
    return rows


def _excluded_by_pattern(path: str, patterns: Iterable[str]) -> bool:
    """Return whether a repository path matches a versioned exclusion pattern."""
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        if pattern.endswith("/") and normalized.startswith(pattern):
            return True
        if fnmatch.fnmatch(normalized, pattern):
            return True
    return False


def _is_source_path(path: str) -> bool:
    """Return whether a path is source code according to versioned definitions."""
    if _excluded_by_pattern(path, SOURCE_CODE_EXCLUDED_PATH_PATTERNS):
        return False
    return Path(path).suffix.lower() in SOURCE_CODE_EXTENSION_ALLOWLIST


def _blob_bytes(repo_path: Path, commit_hash: str, file_path: str) -> bytes:
    """Return one blob content from a commit without checking out the tree."""
    return _run_git(repo_path, ["show", f"{commit_hash}:{file_path}"])


def _looks_binary(content: bytes) -> bool:
    """Return whether bytes look binary using a conservative NUL-byte check."""
    return b"\0" in content[:8192]


def _line_count(content: bytes, repo_path: Path, commit_hash: str, file_path: str) -> int:
    """Count decoded source lines for a selected source file."""
    try:
        text = content.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        error.reason = f"{error.reason}: {repo_path}:{commit_hash}:{file_path}"
        raise
    if "\0" in text:
        raise ValueError(f"Source file contains NUL bytes: {repo_path}:{commit_hash}:{file_path}")
    return len(text.splitlines())


def measure_repository_tree(repo_path: Path, commit_hash: str) -> dict[str, int]:
    """Measure repository size and source LOC for one Git commit tree."""
    total_files = 0
    total_bytes = 0
    source_files = 0
    source_loc = 0
    binary_files = 0
    for entry in _tree_entries(repo_path, commit_hash):
        if entry["object_type"] != "blob":
            continue
        total_files += 1
        if entry["size"] is not None:
            total_bytes += int(entry["size"])
        content = _blob_bytes(repo_path, commit_hash, str(entry["path"]))
        if _looks_binary(content):
            binary_files += 1
        if _is_source_path(str(entry["path"])):
            source_files += 1
            source_loc += _line_count(content, repo_path, commit_hash, str(entry["path"]))
    return {
        "repo_total_files": total_files,
        "repo_total_bytes": total_bytes,
        "repo_source_files": source_files,
        "repo_source_loc": source_loc,
        "repo_binary_files": binary_files,
    }


def _load_repositories(repos_list_path: Path, cache_dir: Path) -> pd.DataFrame:
    """Load repository list and attach deterministic cache repository paths."""
    if not repos_list_path.is_file():
        raise FileNotFoundError(f"Repository list not found: {repos_list_path}")
    repos = pd.read_csv(repos_list_path)
    require_columns(repos, REPOS_REQUIRED_COLUMNS, "repository list")
    rows: list[dict[str, Any]] = []
    for index, row in repos.iterrows():
        team_id = normalize_text(row["ID_Equipe"])
        repo_url = normalize_text(row["URL_Repositorio_Fork"])
        semester = normalize_text(row["Semestre"])
        if semester not in EVALUATOR_TEMPORAL_CUTS:
            raise ValueError(f"Repository row {index} has unconfigured Semestre {semester!r}")
        repo_path = repository_cache_path(repo_url, cache_dir)
        if not repo_path.is_dir():
            raise FileNotFoundError(f"Cached repository not found: {repo_path}")
        rows.append(
            {
                "ID_Equipe": team_id,
                "Semestre": semester,
                "repository": repo_path.name,
                "repo_url": repo_url,
                "repo_path": repo_path,
            }
        )
    result = pd.DataFrame(rows)
    if result.duplicated(["ID_Equipe", "Semestre", "repository"]).any():
        raise ValueError("repository list contains duplicate team/semester repositories")
    return result


def _load_git_commits(git_commits_path: Path) -> pd.DataFrame:
    """Load and validate Git commits needed for snapshot selection."""
    if not git_commits_path.is_file():
        raise FileNotFoundError(f"Git commits contract not found: {git_commits_path}")
    commits = pd.read_parquet(git_commits_path)
    require_columns(commits, COMMIT_REQUIRED_COLUMNS, "git commits")
    commits = commits.copy()
    commits["timestamp"] = pd.to_datetime(commits["timestamp"], errors="raise", utc=True)
    commits["temporal_marker"] = commits["temporal_marker"].astype(str).str.strip().str.upper()
    invalid_markers = sorted(set(commits["temporal_marker"]) - VALID_MARKERS)
    if invalid_markers:
        raise ValueError(f"git commits contains invalid temporal markers: {invalid_markers}")
    return commits


def _build_checksum(repositories: pd.DataFrame, source_paths: list[Path]) -> str:
    """Build a checksum covering inputs, cached snapshots and versioned options."""
    snapshots = [
        f"{row.repository}:{repository_snapshot_id(row.repo_path)}"
        for row in repositories.itertuples(index=False)
    ]
    return input_checksum(
        source_paths,
        {
            "contract_version": REPOSITORY_SNAPSHOT_CONTRACT_VERSION,
            "source_loc_definition_version": SOURCE_LOC_DEFINITION_VERSION,
            "excluded_path_patterns_version": EXCLUDED_PATH_PATTERNS_VERSION,
            "source_extensions": json.dumps(sorted(SOURCE_CODE_EXTENSION_ALLOWLIST)),
            "excluded_paths": json.dumps(sorted(SOURCE_CODE_EXCLUDED_PATH_PATTERNS)),
            "cached_snapshots": json.dumps(sorted(snapshots)),
            "temporal_config": json.dumps(EVALUATOR_TEMPORAL_CUTS, sort_keys=True),
        },
    )


def _unavailable_row(team_id: str, semester: str, marker: str, repository: str) -> dict[str, Any]:
    """Build an explicit unavailable snapshot row without falling back to HEAD."""
    return {
        "ID_Equipe": team_id,
        "Semestre": semester,
        "temporal_marker": marker,
        "repository": repository,
        "snapshot_commit_hash": None,
        "snapshot_timestamp": pd.NaT,
        "snapshot_selection_rule": "last_observed_commit_in_cut",
        "snapshot_available": False,
        "snapshot_unavailable_reason": "no_observed_commit_for_cut",
        "repo_total_files": None,
        "repo_total_bytes": None,
        "repo_source_files": None,
        "repo_source_loc": None,
        "repo_binary_files": None,
        "source_loc_definition_version": SOURCE_LOC_DEFINITION_VERSION,
        "excluded_path_patterns_version": EXCLUDED_PATH_PATTERNS_VERSION,
        "source_type": "git_repository_snapshot",
    }


def _available_row(
    team_id: str,
    semester: str,
    marker: str,
    repository: str,
    repo_path: Path,
    commit_hash: str,
    timestamp: pd.Timestamp,
) -> dict[str, Any]:
    """Build an available snapshot row by measuring one commit tree."""
    metrics = measure_repository_tree(repo_path, commit_hash)
    return {
        "ID_Equipe": team_id,
        "Semestre": semester,
        "temporal_marker": marker,
        "repository": repository,
        "snapshot_commit_hash": commit_hash,
        "snapshot_timestamp": timestamp,
        "snapshot_selection_rule": "last_observed_commit_in_cut",
        "snapshot_available": True,
        "snapshot_unavailable_reason": None,
        **metrics,
        "source_loc_definition_version": SOURCE_LOC_DEFINITION_VERSION,
        "excluded_path_patterns_version": EXCLUDED_PATH_PATTERNS_VERSION,
        "source_type": "git_repository_snapshot",
    }


def build_snapshot_rows(repositories: pd.DataFrame, commits: pd.DataFrame) -> pd.DataFrame:
    """Build repository snapshot rows for every configured team semester cut."""
    rows: list[dict[str, Any]] = []
    for repo_row in repositories.itertuples(index=False):
        repo_commits = commits[
            (commits["ID_Equipe"].astype(str) == repo_row.ID_Equipe)
            & (commits["Semestre"].astype(str) == repo_row.Semestre)
            & (commits["repository"].astype(str) == repo_row.repository)
        ].copy()
        for marker in EVALUATOR_TEMPORAL_CUTS[repo_row.Semestre]:
            cut_commits = repo_commits[repo_commits["temporal_marker"] == marker]
            if cut_commits.empty:
                rows.append(
                    _unavailable_row(
                        repo_row.ID_Equipe,
                        repo_row.Semestre,
                        marker,
                        repo_row.repository,
                    )
                )
                continue
            latest = cut_commits.sort_values("timestamp").iloc[-1]
            rows.append(
                _available_row(
                    repo_row.ID_Equipe,
                    repo_row.Semestre,
                    marker,
                    repo_row.repository,
                    repo_row.repo_path,
                    str(latest["commit_hash"]),
                    latest["timestamp"],
                )
            )
    result = pd.DataFrame(rows)
    if result.duplicated(KEY_COLUMNS).any():
        raise ValueError("repository snapshots contain duplicate analytical keys")
    return result


def _write_metadata(artifact_path: Path, checksum: str) -> None:
    """Write metadata for a successful repository snapshot artifact."""
    artifact_metadata_path(artifact_path).write_text(
        json.dumps(
            {
                "input_checksum": checksum,
                "status": "success",
                "contract_version": REPOSITORY_SNAPSHOT_CONTRACT_VERSION,
                "source_loc_definition_version": SOURCE_LOC_DEFINITION_VERSION,
                "excluded_path_patterns_version": EXCLUDED_PATH_PATTERNS_VERSION,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def build_repository_snapshots(
    repos_list_path: Path,
    cache_dir: Path,
    git_commits_path: Path,
    git_files_path: Path,
    output_path: Path,
    force: bool = False,
) -> Path:
    """Build and write the Phase 1.5 repository snapshot contract.

    Args:
        repos_list_path: CSV with team, repository URL and semester.
        cache_dir: Directory containing cached Git repositories.
        git_commits_path: Phase 1 Git commit contract.
        git_files_path: Phase 1 Git file contract used for checksum coverage.
        output_path: Destination Parquet contract path.
        force: Rebuild even when metadata checksum is current.

    Returns:
        Path to the generated snapshot contract.
    """
    repositories = _load_repositories(repos_list_path, cache_dir)
    if not git_files_path.is_file():
        raise FileNotFoundError(f"Git files contract not found: {git_files_path}")
    checksum = _build_checksum(repositories, [repos_list_path, git_commits_path, git_files_path])
    if not force and is_current_artifact(output_path, checksum):
        logger.info("Skipping current repository snapshots")
        return output_path
    commits = _load_git_commits(git_commits_path)
    result = build_snapshot_rows(repositories, commits)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(f".{output_path.name}.tmp")
    try:
        result.to_parquet(temporary, index=False)
        temporary.replace(output_path)
        _write_metadata(output_path, checksum)
    except Exception:
        temporary.unlink(missing_ok=True)
        output_path.unlink(missing_ok=True)
        artifact_metadata_path(output_path).unlink(missing_ok=True)
        raise
    return output_path


def main() -> None:
    """Run the repository snapshot command-line entry point."""
    load_project_environment()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(
        description="Build Phase 1.5 repository structural snapshots",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--repos-list", type=Path, default=Path("data/raw/repos_list.csv"))
    parser.add_argument("--cache-dir", type=Path, default=Path("data/raw/repos_cache"))
    parser.add_argument("--git-commits", type=Path, default=Path("data/lake/git_commits.parquet"))
    parser.add_argument("--git-files", type=Path, default=Path("data/lake/git_files.parquet"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/lake/git_repository_snapshots.parquet"),
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    build_repository_snapshots(
        args.repos_list,
        args.cache_dir,
        args.git_commits,
        args.git_files,
        args.output,
        args.force,
    )
    logger.info("Repository snapshots written to %s", args.output)


if __name__ == "__main__":
    main()
