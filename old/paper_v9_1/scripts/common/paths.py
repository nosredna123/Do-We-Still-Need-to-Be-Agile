"""Directory resolution for the Paper V9 conversion pipeline.

All paths are resolved relative to the repository root so that no script
depends on the current working directory or on absolute paths baked in at
authoring time. Every resolver fails fast (raises) when the expected
directory does not exist, instead of silently returning a dangling path.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PAPER_V9_ROOT = REPO_ROOT / "paper_v9"


def _require_dir(path: Path) -> Path:
    if not path.is_dir():
        raise FileNotFoundError(f"Required directory does not exist: {path}")
    return path


def resolve_paper_v9_dir() -> Path:
    """Return the root directory of the paper_v9 project."""
    return _require_dir(PAPER_V9_ROOT)


def resolve_data_dir() -> Path:
    """Return paper_v9/data/."""
    return _require_dir(PAPER_V9_ROOT / "data")


def resolve_manifests_dir() -> Path:
    """Return paper_v9/data/manifests/."""
    return _require_dir(PAPER_V9_ROOT / "data" / "manifests")


def resolve_metrics_dir() -> Path:
    """Return paper_v9/data/metrics/, creating it on first use."""
    metrics_dir = PAPER_V9_ROOT / "data" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    return metrics_dir


def resolve_results_dir() -> Path:
    """Return paper_v9/data/results/, creating it on first use."""
    results_dir = PAPER_V9_ROOT / "data" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir


def resolve_scripts_dir() -> Path:
    """Return paper_v9/scripts/."""
    return _require_dir(PAPER_V9_ROOT / "scripts")


def resolve_figures_dir() -> Path:
    """Return paper_v9/figures/, creating it on first use."""
    figures_dir = PAPER_V9_ROOT / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    return figures_dir


def resolve_verification_notebooks_dir() -> Path:
    """Return paper_v9/verification_notebooks/, creating it on first use."""
    notebooks_dir = PAPER_V9_ROOT / "verification_notebooks"
    notebooks_dir.mkdir(parents=True, exist_ok=True)
    return notebooks_dir
