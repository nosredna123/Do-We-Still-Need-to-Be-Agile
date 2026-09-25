"""Checksum and provenance sidecar helpers for the Paper V9 pipeline.

This module intentionally does not reimplement hashing or checksum logic:
it wraps the canonical implementations in ``pipeline_core`` so the whole
repository shares a single source of truth for file fingerprints (DRY).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from pipeline_core import file_checksum, input_checksum

# Re-exported under the names used by the Paper V9 task specification.
compute_sha256 = file_checksum
compute_input_checksum = input_checksum


def verify_hash(filepath: Path, expected_hash: str) -> bool:
    """Return whether ``filepath`` currently hashes to ``expected_hash``."""
    if not filepath.is_file():
        raise FileNotFoundError(f"Cannot verify hash, file not found: {filepath}")
    return compute_sha256(filepath) == expected_hash


def write_hash_sidecar(
    artifact_path: Path,
    computed_hash: str,
    *,
    extra: Mapping[str, Any] | None = None,
) -> Path:
    """Write a ``<artifact>.metadata.json`` sidecar recording ``computed_hash``.

    Returns the sidecar path. Fails fast if ``artifact_path`` does not exist.
    """
    if not artifact_path.is_file():
        raise FileNotFoundError(f"Cannot write sidecar, artifact not found: {artifact_path}")

    sidecar_path = artifact_path.with_name(f"{artifact_path.name}.metadata.json")
    payload: dict[str, Any] = {"sha256": computed_hash, "generated_by": "paper_v9"}
    if extra:
        payload.update(extra)
    sidecar_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    return sidecar_path
