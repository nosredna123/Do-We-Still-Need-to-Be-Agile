"""Cross-evidence extension computations.

This module starts with the pure file-category classifier required by CE-1.2.
Later CE tasks add persisted metric generation, statistics, figures, manifests,
and CLI orchestration.
"""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from pipeline_config import FILE_CATEGORY_RULES


NORMAL_CONFIDENCE = 1.0
WARNING_CONFIDENCE = 0.8
UNKNOWN_CONFIDENCE = 0.5


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
