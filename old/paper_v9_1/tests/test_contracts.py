"""Contract tests for paper_v9/scripts/common utilities.

Covers: import contracts, path resolution, checksum determinism, resume
behavior, artifact-policy versioning, and descriptive statistics.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from paper_v9.scripts.common import artifact_policy, paths, provenance, resume, statistics


def test_common_modules_import_cleanly() -> None:
    assert paths.resolve_paper_v9_dir().name == "paper_v9"
    assert artifact_policy.CURRENT_POLICY_VERSION == "code-churn-metrics-v2"


def test_paths_resolvers_return_existing_or_created_directories() -> None:
    assert paths.resolve_data_dir().is_dir()
    assert paths.resolve_manifests_dir().is_dir()
    assert paths.resolve_metrics_dir().is_dir()
    assert paths.resolve_results_dir().is_dir()


def test_paths_resolver_fails_fast_on_missing_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(paths, "PAPER_V9_ROOT", tmp_path / "does_not_exist")
    with pytest.raises(FileNotFoundError):
        paths.resolve_paper_v9_dir()


def test_provenance_checksum_is_deterministic_and_detects_changes(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("hello", encoding="utf-8")

    first = provenance.compute_sha256(sample)
    second = provenance.compute_sha256(sample)
    assert first == second
    assert provenance.verify_hash(sample, first)

    sample.write_text("hello world", encoding="utf-8")
    assert not provenance.verify_hash(sample, first)


def test_provenance_verify_hash_fails_fast_on_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        provenance.verify_hash(tmp_path / "missing.txt", "deadbeef")


def test_provenance_write_hash_sidecar_round_trips(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.csv"
    artifact.write_text("a,b\n1,2\n", encoding="utf-8")
    computed = provenance.compute_sha256(artifact)

    sidecar_path = provenance.write_hash_sidecar(artifact, computed, extra={"contract_version": "m1-v1"})

    assert sidecar_path.name == "artifact.csv.metadata.json"
    payload = sidecar_path.read_text(encoding="utf-8")
    assert computed in payload
    assert "m1-v1" in payload


def test_resume_should_regenerate_then_reuses_after_mark_complete(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.csv"
    artifact.write_text("a,b\n1,2\n", encoding="utf-8")
    cache = resume.ArtifactCache()

    assert cache.should_regenerate(artifact, "input-hash-1", "config-hash-1") is True

    cache.mark_complete(artifact, "input-hash-1", "config-hash-1")
    assert cache.should_regenerate(artifact, "input-hash-1", "config-hash-1") is False

    # A changed input checksum must force regeneration.
    assert cache.should_regenerate(artifact, "input-hash-2", "config-hash-1") is True

    # --force always forces regeneration regardless of checksum match.
    assert cache.should_regenerate(artifact, "input-hash-1", "config-hash-1", force=True) is True


def test_resume_clear_cache_removes_artifact_and_sidecar(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.csv"
    artifact.write_text("a,b\n1,2\n", encoding="utf-8")
    cache = resume.ArtifactCache()
    cache.mark_complete(artifact, "input-hash-1", "config-hash-1")

    cache.clear_cache(artifact)

    assert not artifact.exists()
    assert not artifact.with_name("artifact.csv.metadata.json").exists()


def test_artifact_policy_classifies_clean_and_excluded_paths() -> None:
    assert artifact_policy.is_clean_path("src/main.py") is True
    assert artifact_policy.is_clean_path("node_modules/lib/index.js") is False
    assert artifact_policy.is_clean_path(".git/HEAD") is False


def test_artifact_policy_rejects_unknown_policy_version() -> None:
    with pytest.raises(ValueError):
        artifact_policy.is_clean_path("src/main.py", policy_version="code-churn-metrics-v1")


def test_statistics_descriptive_summary_computes_expected_fields() -> None:
    summary = statistics.descriptive_summary([1, 2, 3, 4, 5, 6, 7, 8])

    assert summary["n"] == 8
    assert summary["mean"] == pytest.approx(4.5)
    assert summary["median"] == pytest.approx(4.5)
    assert summary["min"] == 1
    assert summary["max"] == 8
    assert "p25" in summary and "p75" in summary


def test_statistics_descriptive_summary_fails_fast_on_empty_input() -> None:
    with pytest.raises(ValueError):
        statistics.descriptive_summary([])


def test_statistics_descriptive_summary_fails_fast_on_non_numeric_input() -> None:
    with pytest.raises(ValueError):
        statistics.descriptive_summary([1, 2, "three"])  # type: ignore[list-item]
