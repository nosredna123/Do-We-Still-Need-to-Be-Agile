"""Artifact-path classification for Paper V9 code-churn/rework metrics.

Adapts the single, central artifact policy in ``pipeline_config`` instead of
duplicating whitelist/blacklist rules (DRY). Fails fast on unknown policy
versions so a metric script can never silently apply the wrong contract.
"""

from __future__ import annotations

from pipeline_config import is_measurement_code_path

CURRENT_POLICY_VERSION = "code-churn-metrics-v2"
_SUPPORTED_POLICY_VERSIONS = frozenset({CURRENT_POLICY_VERSION})


def is_clean_path(file_path: str | None, policy_version: str = CURRENT_POLICY_VERSION) -> bool:
    """Return whether ``file_path`` is eligible for clean-churn measurement.

    Raises:
        ValueError: If ``policy_version`` is not a supported contract.
    """
    if policy_version not in _SUPPORTED_POLICY_VERSIONS:
        raise ValueError(
            f"Unsupported artifact policy version: {policy_version!r}. "
            f"Supported versions: {sorted(_SUPPORTED_POLICY_VERSIONS)}"
        )
    return is_measurement_code_path(file_path)
