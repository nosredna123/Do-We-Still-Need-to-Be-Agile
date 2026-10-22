"""Command-line orchestrator for the Paper V9 conversion pipeline.

Stages are registered explicitly; there is no dynamic plugin discovery
(KISS). Each stage function is added to the pipeline as its task is
implemented in a later phase of the conversion plan.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Callable

StageFn = Callable[[bool], dict[str, object]]

# Populated incrementally as metrics/results/figures/latex-check scripts land.
STAGE_REGISTRY: dict[str, StageFn] = {}


def _run_stage(stage: str, force: bool) -> dict[str, object]:
    if stage not in STAGE_REGISTRY:
        raise ValueError(
            f"Stage {stage!r} is not implemented yet. "
            f"Available stages: {sorted(STAGE_REGISTRY) or '(none registered)'}"
        )
    return STAGE_REGISTRY[stage](force)


def run(stage: str, *, force: bool = False, verbose: bool = False) -> dict[str, object]:
    """Execute one stage (or 'all' registered stages) and return a status report."""
    if stage == "all":
        if not STAGE_REGISTRY:
            raise ValueError("No stages are registered yet; nothing to run for 'all'.")
        return {name: _run_stage(name, force) for name in STAGE_REGISTRY}

    report = _run_stage(stage, force)
    if verbose:
        print(f"[orchestrate_v9] stage={stage} force={force} report={report}", file=sys.stderr)
    return report


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Paper V9 pipeline orchestrator")
    parser.add_argument(
        "stage",
        choices=["metrics", "results", "figures", "latex-check", "all"],
        help="Pipeline stage to execute",
    )
    parser.add_argument("--force", action="store_true", help="Disable resume; regenerate all artifacts")
    parser.add_argument("--verbose", action="store_true", help="Print stage execution details to stderr")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        report = run(args.stage, force=args.force, verbose=args.verbose)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
