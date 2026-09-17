"""Cross-evidence extension computations."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

import pandas as pd

from pipeline_config import (
    CROSS_EVIDENCE_ARTIFACT_REGISTRY,
    CROSS_EVIDENCE_CONTRACT_VERSION,
    CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY,
    FILE_CATEGORY_DEFINITION_VERSION,
    FILE_CATEGORY_RULES,
)
from pipeline_core import input_checksum, invalidate_stale_artifact, is_current_artifact, write_artifact_metadata


logger = logging.getLogger(__name__)


NORMAL_CONFIDENCE = 1.0
WARNING_CONFIDENCE = 0.8
UNKNOWN_CONFIDENCE = 0.5
FILE_CATEGORY_CHURN_CONTRACT_VERSION = CROSS_EVIDENCE_CONTRACT_VERSION
FILE_CATEGORY_CHURN_REQUIRED_COLUMNS = {
    "ID_Equipe",
    "Semestre",
    "temporal_marker",
    "file_path",
    "file_path_old",
    "file_extension",
    "change_status",
    "lines_added",
    "lines_deleted",
    "is_binary",
}
FILE_CATEGORY_CHURN_GROUP_COLUMNS = ["ID_Equipe", "Semestre", "temporal_marker", "file_category"]


def _normalize_path(value: str | None) -> str:
    """Normalize repository paths for deterministic category matching."""
    return str(value or "").replace("\\", "/").strip().lower().lstrip("./")


def _normalize_extension(file_path: str, file_extension: str | None) -> str:
    """Return an explicit extension or infer one from the normalized path."""
    extension = str(file_extension or "").strip().lower()
    if extension and not extension.startswith("."):
        extension = f".{extension}"
    if extension:
        return extension
    return PurePosixPath(file_path).suffix.lower()


def _matches_path_pattern(file_path: str, pattern: str) -> bool:
    """Return whether a normalized path matches a configured path pattern."""
    normalized_pattern = pattern.replace("\\", "/").strip().lower().lstrip("./")
    if not normalized_pattern:
        return False
    if normalized_pattern.endswith("/"):
        return file_path.startswith(normalized_pattern) or f"/{normalized_pattern}" in file_path
    return file_path == normalized_pattern or normalized_pattern in file_path


def _result(category: str, rule: str, confidence: float, warning: str | None = None) -> dict[str, object]:
    """Build the classifier result payload used by dataframe expansion."""
    return {
        "file_category": category,
        "category_rule": rule,
        "category_confidence": confidence,
        "category_warning": warning,
    }


def classify_file_category(
    file_path: str | None,
    file_extension: str | None = None,
    change_status: str | None = None,
    file_path_old: str | None = None,
    *,
    rules: dict[str, Any] | None = None,
) -> dict[str, object]:
    """Classify one Git file event into the versioned cross-evidence taxonomy.

    Args:
        file_path: Current or primary file path from the Git event.
        file_extension: Optional extension column from the lake. If empty, the
            extension is inferred from ``file_path``.
        change_status: Git change status. Accepted for API symmetry with the
            persisted lake schema; CE-1.2 does not branch on status yet.
        file_path_old: Previous path, used only as a fallback when ``file_path``
            is empty.
        rules: Optional taxonomy override for tests.

    Returns:
        Dict with ``file_category``, ``category_rule``,
        ``category_confidence`` and ``category_warning``.
    """
    del change_status
    taxonomy = rules or FILE_CATEGORY_RULES
    selected_path = _normalize_path(file_path) or _normalize_path(file_path_old)
    extension = _normalize_extension(selected_path, file_extension)
    path_patterns = taxonomy["path_patterns"]
    filename_suffixes = taxonomy["filename_suffixes"]
    extensions = taxonomy["extensions"]
    contextual = taxonomy["contextual_extensions"]
    warnings = taxonomy["warnings"]

    for pattern in path_patterns.get("generated", set()):
        if _matches_path_pattern(selected_path, pattern):
            warning = None
            confidence = NORMAL_CONFIDENCE
            if extension in extensions.get("source", set()) or extension in extensions.get("planning", set()):
                warning = str(warnings["generated_source_like_path"])
                confidence = WARNING_CONFIDENCE
            return _result("generated", f"path:generated:{pattern}", confidence, warning)

    planning_context = any(
        _matches_path_pattern(selected_path, pattern)
        for pattern in path_patterns.get("planning", set())
    )
    planning_contextual_extensions = contextual.get("planning_when_path_matches_planning", set())
    if planning_context and extension in extensions.get("planning", set()):
        warning = None
        confidence = NORMAL_CONFIDENCE
        if extension in planning_contextual_extensions:
            warning = str(warnings["planning_config_extension"])
            confidence = WARNING_CONFIDENCE
        return _result("planning", "path:planning", confidence, warning)

    for pattern in path_patterns.get("test", set()):
        if _matches_path_pattern(selected_path, pattern):
            return _result("test", f"path:test:{pattern}", NORMAL_CONFIDENCE)

    for category in taxonomy["category_order"]:
        for suffix in filename_suffixes.get(category, set()):
            if selected_path.endswith(suffix):
                return _result(category, f"filename_suffix:{category}:{suffix}", NORMAL_CONFIDENCE)

    if not extension:
        return _result(
            str(taxonomy["default_category"]),
            "extension:empty",
            UNKNOWN_CONFIDENCE,
            str(warnings["empty_extension"]),
        )

    for category in taxonomy["category_order"]:
        if category == "unknown":
            continue
        if category == "planning" and extension in planning_contextual_extensions:
            continue
        if extension in extensions.get(category, set()):
            return _result(category, f"extension:{category}:{extension}", NORMAL_CONFIDENCE)

    return _result(
        str(taxonomy["default_category"]),
        f"extension:unknown:{extension}",
        UNKNOWN_CONFIDENCE,
    )


def _require_success_sidecar(path: Path) -> dict[str, Any]:
    """Load and validate the required sidecar for an input artifact."""
    metadata_path = path.with_name(f"{path.name}.metadata.json")
    if not path.is_file():
        raise FileNotFoundError(f"Required artifact not found: {path}")
    if not metadata_path.is_file():
        raise FileNotFoundError(f"Required sidecar not found: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("status") != "success":
        raise ValueError(f"Artifact sidecar is not successful: {metadata_path}")
    return metadata


def compute_file_category_churn_metrics(files: pd.DataFrame) -> pd.DataFrame:
    """Aggregate Git file events by team, semester, cut, and file category."""
    missing = FILE_CATEGORY_CHURN_REQUIRED_COLUMNS - set(files.columns)
    if missing:
        raise ValueError(f"git_files missing columns: {sorted(missing)}")
    if files[["ID_Equipe", "Semestre", "temporal_marker"]].isna().any().any():
        raise ValueError("git_files team-semester-cut keys must be non-null")

    working = files.copy()
    classifications = [
        classify_file_category(
            row.file_path,
            row.file_extension,
            row.change_status,
            row.file_path_old,
        )
        for row in working[["file_path", "file_extension", "change_status", "file_path_old"]].itertuples(index=False)
    ]
    classified = pd.concat([working.reset_index(drop=True), pd.DataFrame(classifications)], axis=1)
    classified["lines_added_missing"] = classified["lines_added"].isna()
    classified["lines_deleted_missing"] = classified["lines_deleted"].isna()
    classified["lines_added_observed"] = pd.to_numeric(classified["lines_added"], errors="coerce").fillna(0)
    classified["lines_deleted_observed"] = pd.to_numeric(classified["lines_deleted"], errors="coerce").fillna(0)
    if (classified["lines_added_observed"] < 0).any() or (classified["lines_deleted_observed"] < 0).any():
        raise ValueError("git_files line counts must not be negative")
    classified["churn_lines"] = classified["lines_added_observed"] + classified["lines_deleted_observed"]
    classified["category_warning_present"] = classified["category_warning"].notna()
    classified["is_binary_bool"] = classified["is_binary"].fillna(False).astype(bool)

    grouped = classified.groupby(FILE_CATEGORY_CHURN_GROUP_COLUMNS, dropna=False)
    result = grouped.agg(
        event_n=("file_path", "size"),
        added_event_n=("change_status", lambda values: int((values == "added").sum())),
        deleted_event_n=("change_status", lambda values: int((values == "deleted").sum())),
        modified_event_n=("change_status", lambda values: int((values == "modified").sum())),
        renamed_event_n=("change_status", lambda values: int((values == "renamed").sum())),
        copied_event_n=("change_status", lambda values: int((values == "copied").sum())),
        binary_event_n=("is_binary_bool", "sum"),
        lines_added=("lines_added_observed", "sum"),
        lines_deleted=("lines_deleted_observed", "sum"),
        churn_lines=("churn_lines", "sum"),
        line_count_missing_event_n=("lines_added_missing", "sum"),
        category_warning_event_n=("category_warning_present", "sum"),
        category_confidence_mean=("category_confidence", "mean"),
    ).reset_index()

    denominators = result.groupby(["ID_Equipe", "Semestre", "temporal_marker"], dropna=False).agg(
        total_event_n=("event_n", "sum"),
        total_churn_lines=("churn_lines", "sum"),
    ).reset_index()
    result = result.merge(denominators, on=["ID_Equipe", "Semestre", "temporal_marker"], validate="many_to_one")
    result["category_event_share"] = result["event_n"] / result["total_event_n"]
    result["category_churn_share"] = result["churn_lines"] / result["total_churn_lines"].where(result["total_churn_lines"] != 0)
    result["category_churn_share"] = result["category_churn_share"].fillna(0)
    result["file_category_definition_version"] = FILE_CATEGORY_DEFINITION_VERSION
    result["contract_version"] = FILE_CATEGORY_CHURN_CONTRACT_VERSION
    return result.sort_values(FILE_CATEGORY_CHURN_GROUP_COLUMNS).reset_index(drop=True)


def write_file_category_churn_metrics(
    metrics: pd.DataFrame,
    output_path: Path,
    *,
    source_checksum: str,
    options: dict[str, Any],
) -> None:
    """Persist file-category churn metrics and their sidecar."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_parquet(output_path, index=False)
    write_artifact_metadata(
        output_path,
        source_checksum,
        contract_version=FILE_CATEGORY_CHURN_CONTRACT_VERSION,
        options=options,
    )


def build_file_category_churn_metrics(
    *,
    lake_dir: Path = Path("data/lake"),
    output_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Build or load the persisted file-category churn metrics artifact."""
    output_path = output_path or Path(str(CROSS_EVIDENCE_ARTIFACT_REGISTRY["file_category_churn_metrics"]["path"]))
    git_files_input = CROSS_EVIDENCE_LEGACY_INPUT_REGISTRY["lake.git_files"]
    git_files_path = lake_dir / Path(str(git_files_input["path"])).name
    git_files_sidecar = lake_dir / Path(str(git_files_input["metadata_path"])).name
    _require_success_sidecar(git_files_path)
    options = {
        "stage": "file_category_churn_metrics",
        "contract_version": FILE_CATEGORY_CHURN_CONTRACT_VERSION,
        "file_category_definition_version": FILE_CATEGORY_DEFINITION_VERSION,
        "line_count_missing_policy": "fill_zero_and_count_missing_events",
        "share_denominator": "team_semester_cut",
        "materialize_unobserved_categories": False,
    }
    checksum = input_checksum([git_files_path, git_files_sidecar], options)
    if force:
        invalidate_stale_artifact(output_path, "force-regeneration")
    if not force and is_current_artifact(output_path, checksum):
        logger.info("File-category churn metrics artifact is current: %s", output_path)
        return pd.read_parquet(output_path)

    files = pd.read_parquet(git_files_path)
    metrics = compute_file_category_churn_metrics(files)
    invalidate_stale_artifact(output_path, checksum)
    write_file_category_churn_metrics(metrics, output_path, source_checksum=checksum, options=options)
    logger.info("Wrote %s file-category churn observations", len(metrics))
    return metrics


def main() -> None:
    """Run the currently implemented cross-evidence artifact builders."""
    parser = argparse.ArgumentParser(description="Build cross-evidence extension artifacts")
    parser.add_argument("--lake-dir", type=Path, default=Path("data/lake"))
    parser.add_argument("--file-category-churn-output", type=Path, default=None)
    parser.add_argument("--only", choices=["file_category_churn_metrics"], nargs="+")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    selected = set(args.only or ["file_category_churn_metrics"])
    if "file_category_churn_metrics" in selected:
        build_file_category_churn_metrics(
            lake_dir=args.lake_dir,
            output_path=args.file_category_churn_output,
            force=args.force,
        )


if __name__ == "__main__":
    main()
