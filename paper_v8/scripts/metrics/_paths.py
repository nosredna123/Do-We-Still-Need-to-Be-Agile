"""Shared path constants for paper_v8 metric extraction scripts.

Reuses `pipeline_core.PROJECT_ROOT` / `pipeline_core.ANALYSIS_DIR` as the single
source of truth for repo-root and Phase 2 analysis-dir locations, so every
metric script under `paper_v8/scripts/metrics/` resolves paths the same way as
the rest of the pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PAPER_V8_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline_core import ANALYSIS_DIR, PROJECT_ROOT  # noqa: E402

LAKE_DIR = PROJECT_ROOT / "data" / "lake"
CROSS_EVIDENCE_DATASETS_DIR = ANALYSIS_DIR / "cross_evidence" / "datasets"
PAPER_V4_OUTPUTS_DIR = PROJECT_ROOT / "paper_v4" / "advanced_metrics" / "outputs"
PAPER_V8_DATA_DIR = PROJECT_ROOT / "paper_v8" / "data"


def ensure_output_dir() -> Path:
    """Create (if needed) and return `paper_v8/data/`, the metric-output directory."""
    PAPER_V8_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return PAPER_V8_DATA_DIR
