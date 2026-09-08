"""Versioned research-protocol configuration for the data pipeline.

This module contains non-secret, version-controlled decisions that determine
how raw research inputs are interpreted. It must not contain PII, credentials,
or raw data values.
"""

from __future__ import annotations

from datetime import date


# Models and request parameters are version-controlled protocol decisions.
# Secrets and local overrides belong in the environment, not here.
MODEL_CONFIG: dict[str, dict[str, object]] = {
    "transcription": {
        "provider": "openai",
        "model": "whisper-1",
        "language": "pt",
    },
    "ner": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0,
        "response_format": "json_object",
    },
    "qualitative_mining": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0,
        "response_format": "json_object",
        "service_tier": "standard",
    },
}

REPOSITORY_SNAPSHOT_CONTRACT_VERSION = "git-repository-snapshots-v1"
SOURCE_LOC_DEFINITION_VERSION = "source-loc-v1"
EXCLUDED_PATH_PATTERNS_VERSION = "source-exclusions-v1"
SOURCE_CODE_EXTENSION_ALLOWLIST = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".css",
    ".dart",
    ".go",
    ".h",
    ".hpp",
    ".html",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".php",
    ".py",
    ".rb",
    ".rs",
    ".scss",
    ".sh",
    ".sql",
    ".swift",
    ".ts",
    ".tsx",
    ".vue",
}
SOURCE_CODE_EXCLUDED_PATH_PATTERNS = {
    ".git/",
    ".next/",
    ".venv/",
    "build/",
    "coverage/",
    "dist/",
    "node_modules/",
    "target/",
    "vendor/",
}

# Each range identifies one evaluation moment. The two-day ranges in 2025.2 are
# deliberate: teams were distributed between presentation days because all teams
# could not be evaluated in one session. Each range is therefore one observation
# window, not two independent longitudinal observations.
EVALUATOR_TEMPORAL_CUTS: dict[str, dict[str, tuple[str, str]]] = {
    "2025.2": {
        "T1": ("2025-10-17", "2025-10-24"),
        "T2": ("2025-11-14", "2025-11-21"),
        "T3": ("2025-12-05", "2025-12-12"),
    },
    "2026.1": {
        "T1": ("2026-04-24", "2026-04-24"),
        "T2": ("2026-05-22", "2026-05-22"),
        "T3": ("2026-06-19", "2026-06-19"),
    },
}


def temporal_marker_for(semester: str, evaluation_date: str) -> str:
    """Return the configured temporal marker for an evaluator response date.

    Args:
        semester: Semester identifier, such as ``2025.2``.
        evaluation_date: Evaluation date in ISO-8601 ``YYYY-MM-DD`` format.

    Returns:
        The configured ``T1``, ``T2``, or ``T3`` marker.

    Raises:
        ValueError: If the semester or date is not covered by the protocol.
    """
    cuts = EVALUATOR_TEMPORAL_CUTS.get(semester)
    if cuts is None:
        raise ValueError(f"Semester {semester} has no configured evaluator cuts")

    parsed_date = date.fromisoformat(evaluation_date)
    for marker, (start_date, end_date) in cuts.items():
        if date.fromisoformat(start_date) <= parsed_date <= date.fromisoformat(end_date):
            return marker

    raise ValueError(
        f"Date {evaluation_date} is not in a configured evaluator cut for {semester}"
    )


def git_temporal_marker_for(semester: str, event_date: str) -> str:
    """Assign a Git event to a semester phase using ordered cut boundaries.

    Git history is continuous, unlike evaluator submissions. Events before the
    T1 boundary belong to T1, events before T2 belong to T2, and events from
    T2 onward belong to T3.
    """
    cuts = EVALUATOR_TEMPORAL_CUTS.get(semester)
    if cuts is None:
        raise ValueError(f"Semester {semester} has no configured evaluator cuts")

    parsed_date = date.fromisoformat(event_date)
    t1_start = date.fromisoformat(cuts["T1"][0])
    t2_start = date.fromisoformat(cuts["T2"][0])
    if parsed_date < t1_start:
        return "T1"
    if parsed_date < t2_start:
        return "T2"
    return "T3"
