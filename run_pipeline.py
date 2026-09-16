#!/usr/bin/env python3
"""Run the Phase 1 and Phase 1.5 pipeline stages in a controlled order.

Usage:
    python run_pipeline.py --csv data/raw/forms/students.csv
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
VENV_ROOT = VENV_PYTHON.parent.parent
if __name__ == "__main__" and VENV_PYTHON.is_file() and Path(sys.prefix).resolve() != VENV_ROOT.resolve():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(Path(__file__).resolve()), *sys.argv[1:]])

from pipeline_core import load_project_environment  # noqa: E402

logger = logging.getLogger(__name__)
PYTHON_EXECUTABLE = str(VENV_PYTHON) if VENV_PYTHON.is_file() else sys.executable
STAGES = (
    "cleanup", "prepare", "transcribe", "ner", "anonymize", "git", "lake",
    "repo-snapshots", "contracts", "nlp", "metrics", "stats",
)
STAGE_SCRIPTS = {
    "cleanup": "04_cleanup.py",
    "prepare": "00_audio_preparer.py",
    "transcribe": "00_audio_transcriber.py",
    "ner": "01_ner_extractor.py",
    "anonymize": "01_anonymizer.py",
    "git": "02_git_parser.py",
    "lake": "03_data_lake_builder.py",
    "repo-snapshots": "02b_git_repository_snapshots.py",
    "contracts": "phase2_contracts.py",
    "nlp": "04_nlp_qualitative_miner.py",
    "metrics": "05_metric_engine.py",
    "stats": "06_statistical_analyzer.py",
}


def resolve_stages(
    selected_stages: list[str] | None,
    from_stage: str | None,
    to_stage: str | None,
) -> list[str]:
    """Resolve selected stages into their required execution order."""
    if selected_stages:
        return [stage for stage in STAGES if stage in selected_stages]

    start_index = STAGES.index(from_stage) if from_stage else STAGES.index("prepare")
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
    nlp_backend: str = "openai",
) -> list[str]:
    """Build the subprocess command for a pipeline stage."""
    command = [PYTHON_EXECUTABLE, str(PROJECT_ROOT / STAGE_SCRIPTS[stage])]
    if stage == "anonymize":
        for csv_path in csv_paths:
            command.extend(["--csv", str(csv_path)])
        for transcript_path in transcript_paths:
            command.extend(["--transcript", str(transcript_path)])
        if salt:
            command.extend(["--salt", salt])
    if stage == "contracts":
        command.extend(
            [
                "--lake-dir",
                str(PROJECT_ROOT / "data" / "lake"),
                "--output",
                str(PROJECT_ROOT / "data" / "analysis" / "phase2_contract_report.json"),
            ]
        )
    if stage == "nlp":
        command.extend(
            [
                "--lake-dir",
                str(PROJECT_ROOT / "data" / "lake"),
                "--contract-report",
                str(PROJECT_ROOT / "data" / "analysis" / "phase2_contract_report.json"),
                "--catalog-output",
                str(PROJECT_ROOT / "data" / "analysis" / ".private" / "student_prompt_catalog.parquet"),
                "--output",
                str(PROJECT_ROOT / "data" / "analysis" / "student_nlp.parquet"),
                "--transcript-output",
                str(PROJECT_ROOT / "data" / "analysis" / "transcript_nlp.parquet"),
                "--textual-cut-signals-output",
                str(PROJECT_ROOT / "data" / "analysis" / "textual_cut_signals.parquet"),
                "--backend",
                nlp_backend,
            ]
        )
    if stage == "metrics":
        command.extend(
            [
                "--lake-dir",
                str(PROJECT_ROOT / "data" / "lake"),
                "--contract-report",
                str(PROJECT_ROOT / "data" / "analysis" / "phase2_contract_report.json"),
                "--output",
                str(PROJECT_ROOT / "data" / "analysis" / "planning_metrics.parquet"),
                "--code-churn-output",
                str(PROJECT_ROOT / "data" / "analysis" / "code_churn_metrics.parquet"),
                "--technical-degradation-output",
                str(PROJECT_ROOT / "data" / "analysis" / "technical_degradation_metrics.parquet"),
                "--integration-friction-output",
                str(PROJECT_ROOT / "data" / "analysis" / "integration_friction_metrics.parquet"),
                "--cut-context-output",
                str(PROJECT_ROOT / "data" / "analysis" / "cut_context_metrics.parquet"),
                "--team-metrics-output",
                str(PROJECT_ROOT / "data" / "analysis" / "team_metrics.parquet"),
            ]
        )
    if force:
        command.append("--force")
    if limite is not None and stage in {"prepare", "transcribe", "ner", "anonymize"}:
        command.extend(["--limite", str(limite)])
    return command


def validate_dry_run_requirements(stages: list[str], nlp_backend: str) -> None:
    """Validate non-destructive stage prerequisites before a dry run."""
    for stage in stages:
        script = PROJECT_ROOT / STAGE_SCRIPTS[stage]
        if not script.is_file():
            raise FileNotFoundError(f"Stage script not found: {script}")
    if any(stage in stages for stage in ("nlp", "metrics", "stats")):
        lake_dir = PROJECT_ROOT / "data" / "lake"
        if not lake_dir.is_dir():
            raise FileNotFoundError(f"Phase 2 lake directory not found: {lake_dir}")
        contract_report = PROJECT_ROOT / "data" / "analysis" / "phase2_contract_report.json"
        if not contract_report.is_file():
            raise FileNotFoundError(f"Phase 2 contract report not found: {contract_report}")
    if "nlp" in stages and nlp_backend not in {"openai", "mock"}:
        raise ValueError(f"Unsupported NLP backend: {nlp_backend}")


def write_run_manifest(path: Path, payload: dict[str, object]) -> None:
    """Persist a structured summary alongside the human-readable log."""
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")


def execution_log_path(log_dir: Path, now: datetime | None = None) -> Path:
    """Return a timestamped text path for one pipeline execution log."""
    timestamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%dT%H%M%SZ")
    return log_dir / f"pipeline_{timestamp}.txt"


def run_stage_process(command: list[str], log_path: Path) -> None:
    """Run one stage while streaming output to both terminal and log file."""
    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    with log_path.open("a", encoding="utf-8") as log_handle:
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            log_handle.write(line)
            log_handle.flush()
    return_code = process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)


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
        "--nlp-backend",
        choices=("openai", "mock"),
        default="openai",
        help="Backend used by the NLP stage; remote OpenAI or deterministic offline mock",
    )
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
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("logs"),
        help="Directory for timestamped execution logs",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Explicit execution log path; overrides --log-dir",
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
    if args.dry_run:
        try:
            validate_dry_run_requirements(stages, args.nlp_backend)
        except (FileNotFoundError, ValueError) as error:
            parser.error(str(error))
    log_path = args.log_file or execution_log_path(args.log_dir)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_path, encoding="utf-8")],
        force=True,
    )
    logger.info("Pipeline execution log: %s", log_path)
    run_manifest_path = log_path.with_suffix(".json")
    run_manifest: dict[str, object] = {
        "status": "dry_run" if args.dry_run else "running",
        "stages": stages,
        "nlp_backend": args.nlp_backend,
        "force": args.force,
        "dry_run": args.dry_run,
        "log_path": log_path.as_posix(),
        "stage_results": [],
    }
    write_run_manifest(run_manifest_path, run_manifest)
    for stage in stages:
        command = build_stage_command(
            stage,
            args.csv,
            args.transcript,
            args.salt,
            args.force,
            args.limite,
            args.nlp_backend,
        )
        logger.info("Running stage %s: %s", stage, " ".join(command))
        if args.dry_run:
            continue
        started_at = time.monotonic()
        try:
            run_stage_process(command, log_path)
            run_manifest["stage_results"].append({
                "stage": stage,
                "status": "success",
                "duration_seconds": round(time.monotonic() - started_at, 1),
                "command": command,
            })
            logger.info(
                "Finished stage %s status=success duration_seconds=%.1f",
                stage,
                time.monotonic() - started_at,
            )
        except subprocess.CalledProcessError as error:
            run_manifest["status"] = "failed"
            run_manifest["stage_results"].append({
                "stage": stage,
                "status": "failed",
                "exit_code": error.returncode,
                "duration_seconds": round(time.monotonic() - started_at, 1),
                "command": command,
            })
            write_run_manifest(run_manifest_path, run_manifest)
            logger.error(
                "Finished stage %s status=failed exit_code=%s duration_seconds=%.1f",
                stage,
                error.returncode,
                time.monotonic() - started_at,
            )
            raise SystemExit(error.returncode) from error
    if args.dry_run:
        run_manifest["status"] = "dry_run"
    else:
        run_manifest["status"] = "success"
    write_run_manifest(run_manifest_path, run_manifest)


if __name__ == "__main__":
    main()