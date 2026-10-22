"""Shared path constants for paper_v8 LLM-usage scripts.

Reuses `pipeline_core.PROJECT_ROOT` as the single source of truth for the
repo-root location, consistent with `paper_v8/scripts/metrics/_paths.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline_core import PROJECT_ROOT  # noqa: E402

LLM_USAGE_OUTPUT_DIR = PROJECT_ROOT / "paper_v8" / "data" / "llm_usage"


def ensure_llm_usage_output_dir() -> Path:
    """Create (if needed) and return `paper_v8/data/llm_usage/`."""
    LLM_USAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return LLM_USAGE_OUTPUT_DIR
