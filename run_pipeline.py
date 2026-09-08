#!/usr/bin/env python3
"""Run the Phase 1 pipeline stages in a controlled order.

Usage:
    python run_pipeline.py --csv data/raw/forms/students.csv
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from pipeline_core import load_project_environment

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent
STAGES = ("prepare", "transcribe", "ner", "anonymize", "git", "lake")
STAGE_SCRIPTS = {
    "prepare": "00_audio_preparer.py",
    "transcribe": "00_audio_transcriber.py",
    "ner": "01_ner_extractor.py",
    "anonymize": "01_anonymizer.py",
    "git": "02_git_parser.py",
    "lake": "03_data_lake_builder.py",
}


def resolve_stages(
    selected_stages: list[str] | None,
    from_stage: str | None,
    to_stage: str | None,
) -> list[str]:
    """Resolve selected stages into their required execution order."""
    if selected_stages:
        return [stage for stage in STAGES if stage in selected_stages]

    start_index = STAGES.index(from_stage) if from_stage else 0
    end_index = STAGES.index(to_stage) if to_stage else len(STAGES) - 1
    if start_index > end_index:
        raise ValueError("--from-stage must not follow --to-stage")
    return list(STAGES[start_index : end_index + 1])


def build_stage_command(
    stage: str,
    csv_paths: list[Path],
    transcript_paths: list[Path],
    salt: str,
    force: bool,
    limite: int | None = None,
) -> list[str]:
    """Build the subprocess command for a pipeline stage."""
    command = [sys.executable, str(PROJECT_ROOT / STAGE_SCRIPTS[stage])]
    if stage == "anonymize":
        for csv_path in csv_paths:
            command.extend(["--csv", str(csv_path)])
        for transcript_path in transcript_paths:
            command.extend(["--transcript", str(transcript_path)])
        if salt:
            command.extend(["--salt", salt])
    if force:
        command.append("--force")
    if limite is not None and stage in {"prepare", "transcribe", "ner", "anonymize"}:
        command.extend(["--limite", str(limite)])
    return command


def main() -> None:
    """Parse CLI options and execute the requested pipeline stages."""
    load_project_environment()
    parser = argparse.ArgumentParser(description="Run the Phase 1 data pipeline")
    parser.add_argument(
        "--stages",
        choices=STAGES,
        nargs="+",
        help="Specific stages to run in pipeline order",
    )
    parser.add_argument(
        "--from-stage",
        choices=STAGES,
        help="First stage to run",
    )
    parser.add_argument(
        "--to-stage",
        choices=STAGES,
        help="Last stage to run",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        action="append",
        default=[],
        help="Raw CSV source passed to the anonymizer; may be repeated",
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        action="append",
        default=[],
        help="Transcript source passed to the anonymizer; may be repeated",
    )
    parser.add_argument("--salt", default="", help="Salt passed to the anonymizer")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force every selected stage to regenerate its outputs",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Maximum number of pending items per item-processing stage",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log selected commands without executing them",
    )
    args = parser.parse_args()
    if args.limite is not None and args.limite < 1:
        parser.error("--limite must be greater than zero")
    if args.stages and (args.from_stage or args.to_stage):
        parser.error("--stages cannot be combined with --from-stage or --to-stage")

    try:
        stages = resolve_stages(args.stages, args.from_stage, args.to_stage)
    except ValueError as error:
        parser.error(str(error))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    for stage in stages:
        command = build_stage_command(
            stage,
            args.csv,
            args.transcript,
            args.salt,
            args.force,
            args.limite,
        )
        logger.info("Running stage %s: %s", stage, " ".join(command))
        if args.dry_run:
            continue
        try:
            subprocess.run(command, check=True, cwd=PROJECT_ROOT)
        except subprocess.CalledProcessError as error:
            logger.error("Stage %s failed with exit code %s", stage, error.returncode)
            raise SystemExit(error.returncode) from error


if __name__ == "__main__":
    main()