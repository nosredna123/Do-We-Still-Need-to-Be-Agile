"""Shared path constants for paper_v8 Results-section scripts."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pipeline_core import PROJECT_ROOT  # noqa: E402

DATA_DIR = PROJECT_ROOT / "paper_v8" / "data"
RESULTS_OUTPUT_DIR = DATA_DIR / "results"
FIGURES_DIR = PROJECT_ROOT / "paper_v8" / "figures"


def ensure_results_output_dir() -> Path:
    """Create (if needed) and return `paper_v8/data/results/`."""
    RESULTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_OUTPUT_DIR


def ensure_figures_dir() -> Path:
    """Create (if needed) and return `paper_v8/figures/`."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR
