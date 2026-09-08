from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd
import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent


def load_snapshots_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "git_repository_snapshots", REPO_ROOT / "02b_git_repository_snapshots.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git(repo_path: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def commit_file(repo_path: Path, relative_path: str, content: bytes, iso_date: str) -> str:
    path = repo_path / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    run_git(repo_path, "add", relative_path)
    env = {
        "GIT_AUTHOR_NAME": "Test Author",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test Author",
        "GIT_COMMITTER_EMAIL": "test@example.com",
        "GIT_AUTHOR_DATE": iso_date,
        "GIT_COMMITTER_DATE": iso_date,
    }
    run_git(repo_path, "commit", "-m", f"commit {relative_path}", env=env)
    return run_git(repo_path, "rev-parse", "HEAD")


def make_repo(repo_path: Path) -> None:
    repo_path.mkdir(parents=True)
    run_git(repo_path, "init")
    run_git(repo_path, "config", "user.name", "Test Author")
    run_git(repo_path, "config", "user.email", "test@example.com")


def write_git_inputs(tmp_path: Path, repository: str, commits: list[dict[str, object]]) -> tuple[Path, Path]:
    git_commits = tmp_path / "git_commits.parquet"
    git_files = tmp_path / "git_files.parquet"
    pd.DataFrame(commits).to_parquet(git_commits, index=False)
    pd.DataFrame(
        [
            {
                "repository": repository,
                "commit_hash": row["commit_hash"],
                "timestamp": row["timestamp"],
                "temporal_marker": row["temporal_marker"],
                "ID_Equipe": row["ID_Equipe"],
                "Semestre": row["Semestre"],
                "ID_Autor_Local": "Dev_A",
                "source_type": "git_file",
                "file_path": "src/app.py",
                "file_path_old": None,
                "file_extension": ".py",
                "change_status": "modified",
                "lines_added": 1,
                "lines_deleted": 0,
                "is_binary": False,
                "branch_or_ref": "main",
                "branch_or_ref_source": "git_branch_contains",
            }
            for row in commits
        ]
    ).to_parquet(git_files, index=False)
    return git_commits, git_files


def test_build_repository_snapshots_selects_last_commit_per_cut_without_head_fallback(tmp_path: Path) -> None:
    snapshots = load_snapshots_module()
    repos_list = tmp_path / "repos_list.csv"
    cache_dir = tmp_path / "repos_cache"
    output_path = tmp_path / "git_repository_snapshots.parquet"
    repo_url = "https://example.com/team-alpha.git"
    repos_list.write_text(
        "ID_Equipe,URL_Repositorio_Fork,Semestre\nTEAM_01,https://example.com/team-alpha.git,2025.2\n",
        encoding="utf-8",
    )
    repo_path = snapshots.repository_cache_path(repo_url, cache_dir)
    make_repo(repo_path)
    commit_t1_old = commit_file(
        repo_path,
        "src/app.py",
        b"print('old')\n",
        "2025-10-18T09:00:00+00:00",
    )
    commit_t1_new = commit_file(
        repo_path,
        "src/app.py",
        b"print('new')\nprint('more')\n",
        "2025-10-19T09:00:00+00:00",
    )
    commit_t2 = commit_file(
        repo_path,
        "assets/logo.bin",
        b"\x00\x01\x02",
        "2025-11-15T09:00:00+00:00",
    )
    git_commits, git_files = write_git_inputs(
        tmp_path,
        repo_path.name,
        [
            {
                "repository": repo_path.name,
                "commit_hash": commit_t1_old,
                "timestamp": pd.Timestamp("2025-10-18T09:00:00Z"),
                "temporal_marker": "T1",
                "ID_Equipe": "TEAM_01",
                "Semestre": "2025.2",
                "ID_Autor_Local": "Dev_A",
                "source_type": "git_commit",
            },
            {
                "repository": repo_path.name,
                "commit_hash": commit_t1_new,
                "timestamp": pd.Timestamp("2025-10-19T09:00:00Z"),
                "temporal_marker": "T1",
                "ID_Equipe": "TEAM_01",
                "Semestre": "2025.2",
                "ID_Autor_Local": "Dev_A",
                "source_type": "git_commit",
            },
            {
                "repository": repo_path.name,
                "commit_hash": commit_t2,
                "timestamp": pd.Timestamp("2025-11-15T09:00:00Z"),
                "temporal_marker": "T2",
                "ID_Equipe": "TEAM_01",
                "Semestre": "2025.2",
                "ID_Autor_Local": "Dev_A",
                "source_type": "git_commit",
            },
        ],
    )

    snapshots.build_repository_snapshots(
        repos_list,
        cache_dir,
        git_commits,
        git_files,
        output_path,
    )

    result = pd.read_parquet(output_path).sort_values("temporal_marker").reset_index(drop=True)
    metadata = json.loads(output_path.with_name(f"{output_path.name}.metadata.json").read_text())
    assert metadata["status"] == "success"
    assert result["temporal_marker"].tolist() == ["T1", "T2", "T3"]
    assert result.loc[0, "snapshot_commit_hash"] == commit_t1_new
    assert result.loc[0, "repo_source_files"] == 1
    assert result.loc[0, "repo_source_loc"] == 2
    assert result.loc[1, "snapshot_commit_hash"] == commit_t2
    assert not result.loc[2, "snapshot_available"]
    assert result.loc[2, "snapshot_commit_hash"] is None
    assert result.loc[2, "snapshot_unavailable_reason"] == "no_observed_commit_for_cut"
    assert str(result.loc[0:1, "snapshot_timestamp"].dt.tz) == "UTC"


def test_build_repository_snapshots_fails_when_cached_repository_is_missing(tmp_path: Path) -> None:
    snapshots = load_snapshots_module()
    repos_list = tmp_path / "repos_list.csv"
    repos_list.write_text(
        "ID_Equipe,URL_Repositorio_Fork,Semestre\nTEAM_01,https://example.com/missing.git,2025.2\n",
        encoding="utf-8",
    )
    git_commits, git_files = write_git_inputs(tmp_path, "missing", [])

    with pytest.raises(FileNotFoundError, match="Cached repository not found"):
        snapshots.build_repository_snapshots(
            repos_list,
            tmp_path / "repos_cache",
            git_commits,
            git_files,
            tmp_path / "snapshots.parquet",
        )


def test_build_repository_snapshots_fails_for_undecodable_source_file(tmp_path: Path) -> None:
    snapshots = load_snapshots_module()
    repos_list = tmp_path / "repos_list.csv"
    cache_dir = tmp_path / "repos_cache"
    repo_url = "https://example.com/binary-source.git"
    repos_list.write_text(
        "ID_Equipe,URL_Repositorio_Fork,Semestre\nTEAM_02,https://example.com/binary-source.git,2025.2\n",
        encoding="utf-8",
    )
    repo_path = snapshots.repository_cache_path(repo_url, cache_dir)
    make_repo(repo_path)
    commit_hash = commit_file(
        repo_path,
        "src/broken.py",
        b"\xff\xfe\x00",
        "2025-10-18T09:00:00+00:00",
    )
    git_commits, git_files = write_git_inputs(
        tmp_path,
        repo_path.name,
        [
            {
                "repository": repo_path.name,
                "commit_hash": commit_hash,
                "timestamp": pd.Timestamp("2025-10-18T09:00:00Z"),
                "temporal_marker": "T1",
                "ID_Equipe": "TEAM_02",
                "Semestre": "2025.2",
                "ID_Autor_Local": "Dev_A",
                "source_type": "git_commit",
            }
        ],
    )

    with pytest.raises(UnicodeDecodeError):
        snapshots.build_repository_snapshots(
            repos_list,
            cache_dir,
            git_commits,
            git_files,
            tmp_path / "snapshots.parquet",
        )
