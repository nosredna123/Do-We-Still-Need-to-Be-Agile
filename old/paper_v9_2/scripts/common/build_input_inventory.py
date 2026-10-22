"""Generate paper_v9/data/manifests/input_inventory.json from real repository data.

Regenerate whenever the lake, git parent mirrors, or artifact policy change:

    python -m paper_v9.scripts.common.build_input_inventory

Fails fast if a declared data source is missing so the inventory can never
silently describe stale or absent inputs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pipeline_config import (
    EXCLUDED_PATH_PATTERNS_VERSION,
    SOURCE_CODE_EXCLUDED_PATH_PATTERNS,
    SOURCE_CODE_EXTENSION_ALLOWLIST,
)

from paper_v9.scripts.common.artifact_policy import CURRENT_POLICY_VERSION
from paper_v9.scripts.common.paths import REPO_ROOT, resolve_manifests_dir
from paper_v9.scripts.common.provenance import compute_sha256
from paper_v9.scripts.common.validate_keys import (
    EXPECTED_CC_DEFINITION_VERSION,
    checkpoint_coverage_report,
    validate_team_semester_keys,
)

LAKE_CONTRACT_NAMES: tuple[str, ...] = (
    "student_responses",
    "evaluator_team_cuts",
    "git_team_cuts",
    "git_commits",
    "git_files",
    "git_repository_snapshots",
    "transcript_sessions",
)


def _describe_lake_contracts(lake_dir: Path) -> dict[str, Any]:
    contracts: dict[str, Any] = {}
    for name in LAKE_CONTRACT_NAMES:
        parquet_path = lake_dir / f"{name}.parquet"
        sidecar_path = lake_dir / f"{name}.parquet.metadata.json"
        if not parquet_path.is_file() or not sidecar_path.is_file():
            raise FileNotFoundError(f"Lake contract incomplete for {name!r}: {parquet_path}")
        frame = pd.read_parquet(parquet_path)
        contracts[name] = {
            "parquet_path": parquet_path.relative_to(REPO_ROOT).as_posix(),
            "parquet_sha256": compute_sha256(parquet_path),
            "sidecar_path": sidecar_path.relative_to(REPO_ROOT).as_posix(),
            "sidecar_sha256": compute_sha256(sidecar_path),
            "rows": len(frame),
            "semesters": sorted(frame["Semestre"].astype(str).unique()) if "Semestre" in frame.columns else [],
            "temporal_markers": (
                sorted(frame["temporal_marker"].astype(str).unique())
                if "temporal_marker" in frame.columns
                else []
            ),
            "has_team_semester_key": {"ID_Equipe", "Semestre"}.issubset(frame.columns),
        }
    return contracts



def _describe_git_parent_mirrors(raw_dir: Path) -> dict[str, Any]:
    mirrors_dir = raw_dir / "repos_parent_cache"
    if not mirrors_dir.is_dir():
        raise FileNotFoundError(f"Git parent mirrors directory not found: {mirrors_dir}")
    repo_dirs = sorted(entry.name for entry in mirrors_dir.iterdir() if entry.is_dir())
    return {
        "path": mirrors_dir.relative_to(REPO_ROOT).as_posix(),
        "policy": "read_only",
        "repo_count": len(repo_dirs),
        "repo_directories": repo_dirs,
        "note": (
            "Bare/mirror clones are not content-hashed here (large, binary git objects). "
            "Team-semester activity is consumed through the git_repository_snapshots, "
            "git_commits, and git_files lake contracts, which are individually hashed above."
        ),
    }


def _describe_processed_transcripts(processed_dir: Path, lake_semesters: list[str]) -> dict[str, Any]:
    transcripts_dir = processed_dir / "transcripts_anon"
    if not transcripts_dir.is_dir():
        raise FileNotFoundError(f"Processed transcripts directory not found: {transcripts_dir}")
    covered_semesters = sorted(entry.name for entry in transcripts_dir.iterdir() if entry.is_dir())
    missing_semesters = sorted(set(lake_semesters) - set(covered_semesters))
    return {
        "path": transcripts_dir.relative_to(REPO_ROOT).as_posix(),
        "canonical_lake_contract": "transcript_sessions",
        "covered_semesters": covered_semesters,
        "missing_semesters": missing_semesters,
        "note": (
            "Known coverage gap, not a blocker: semesters listed in "
            "missing_semesters have zero transcript sessions and must be "
            "declared as unavailable_not_measured by M5, never imputed."
        ),
    }


def _describe_artifact_policy() -> dict[str, Any]:
    return {
        "policy_function": "pipeline_config.is_measurement_code_path",
        "current_policy_version": CURRENT_POLICY_VERSION,
        "cc_definition_version": EXPECTED_CC_DEFINITION_VERSION,
        "excluded_path_patterns_version": EXCLUDED_PATH_PATTERNS_VERSION,
        "excluded_path_patterns": sorted(SOURCE_CODE_EXCLUDED_PATH_PATTERNS),
        "source_code_extension_allowlist": sorted(SOURCE_CODE_EXTENSION_ALLOWLIST),
    }


def build_input_inventory(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Assemble the full input inventory from real, on-disk repository data."""
    lake_dir = repo_root / "data" / "lake"
    raw_dir = repo_root / "data" / "raw"
    processed_dir = repo_root / "data" / "processed"

    lake_contracts = _describe_lake_contracts(lake_dir)
    key_validation = validate_team_semester_keys(lake_dir)
    checkpoint_coverage = checkpoint_coverage_report(lake_dir)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "paper_v9.scripts.common.build_input_inventory",
        "lake_contracts": lake_contracts,
        "git_parent_mirrors": _describe_git_parent_mirrors(raw_dir),
        "processed_transcripts": _describe_processed_transcripts(
            processed_dir, lake_contracts["transcript_sessions"]["semesters"] or ["2025.2", "2026.1"]
        ),
        "evaluations": {
            "canonical_lake_contract": "evaluator_team_cuts",
            "note": (
                "There is no separate raw 'evaluations' directory; evaluator "
                "scores are embedded in student_responses.parquet and "
                "aggregated per team-semester in evaluator_team_cuts.parquet."
            ),
        },
        "artifact_policy": _describe_artifact_policy(),
        "team_semester_key_validation": key_validation,
        "checkpoint_coverage": checkpoint_coverage,
    }


def main() -> int:
    inventory = build_input_inventory()
    output_path = resolve_manifests_dir() / "input_inventory.json"
    output_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    print(f"Wrote {output_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
