#!/usr/bin/env python3
"""Remove stale Phase 1 generated artifacts before rerunning the pipeline.

Usage:
    python 04_cleanup.py
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from pipeline_core import cleanup_phase_one_artifacts, load_project_environment

logger = logging.getLogger(__name__)


def main() -> None:
    """Remove only the Phase 1 derived artifacts while preserving raw inputs."""
    load_project_environment()
    parser = argparse.ArgumentParser(
        description="Remove stale Phase 1 derived artifacts while preserving raw inputs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Project root whose derived Phase 1 outputs should be cleaned",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    project_root = args.project_root.resolve()
    logger.info("Cleaning derived Phase 1 artifacts under %s", project_root)
    cleanup_phase_one_artifacts(project_root)
    logger.info("Cleanup complete")


if __name__ == "__main__":
    main()
