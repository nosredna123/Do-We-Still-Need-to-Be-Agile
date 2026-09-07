"""Versioned research-protocol configuration for the data pipeline.

This module contains non-secret, version-controlled decisions that determine
how raw research inputs are interpreted. It must not contain PII, credentials,
or raw data values.
"""

from __future__ import annotations

from datetime import date

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
