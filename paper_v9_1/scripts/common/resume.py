"""Resume/cache logic for Paper V9 artifacts.

Wraps the canonical resume primitives in ``pipeline_core`` (DRY) instead of
reimplementing checksum comparison or metadata-sidecar handling.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from pipeline_core import (
    invalidate_artifacts,
    is_current_artifact,
    write_artifact_metadata,
)


def _combined_checksum(input_hash: str, config_hash: str) -> str:
    digest = hashlib.sha256()
    digest.update(input_hash.encode("utf-8"))
    digest.update(config_hash.encode("utf-8"))
    return digest.hexdigest()


class ArtifactCache:
    """Decide whether an artifact must be regenerated, and record completion."""

    def should_regenerate(
        self,
        artifact_path: Path,
        input_hash: str,
        config_hash: str,
        *,
        force: bool = False,
    ) -> bool:
        """Return True when ``artifact_path`` must be (re)computed."""
        if force:
            return True
        checksum = _combined_checksum(input_hash, config_hash)
        return not is_current_artifact(artifact_path, checksum)

    def mark_complete(
        self,
        artifact_path: Path,
        input_hash: str,
        config_hash: str,
        *,
        contract_version: str | None = None,
    ) -> None:
        """Record that ``artifact_path`` was generated successfully."""
        checksum = _combined_checksum(input_hash, config_hash)
        write_artifact_metadata(artifact_path, checksum, contract_version=contract_version)

    def clear_cache(self, artifact_path: Path) -> None:
        """Delete ``artifact_path`` and its sidecar so it will be regenerated."""
        invalidate_artifacts([artifact_path])
