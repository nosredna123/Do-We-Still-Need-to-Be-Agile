"""Generate independent narrative reports for the cross-evidence layer.

This module is intentionally separate from the Phase 2 artifact-narrative reporter:
it reads already-computed cross-evidence datasets/results/figure-data artifacts and
sends only compact, aggregated fact sheets to a prompt backend. No raw text or
private evidence is ever passed to the model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
from pathlib import Path
from typing import Any

import pandas as pd

from llm_gateway import LLMCallGateway
from pipeline_config import CROSS_EVIDENCE_ARTIFACT_REGISTRY, MODEL_CONFIG
from pipeline_core import ANALYSIS_DIR, PROJECT_ROOT, input_checksum, invalidate_stale_artifact, is_current_artifact, load_project_environment, write_artifact_metadata
from pipeline_prompts import (
    CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT,
    CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT_VERSION,
    CROSS_EVIDENCE_ARTIFACT_REPORT_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)

DEFAULT_REPORTS_DIRNAME = "reports"
MAX_SUMMARY_COLUMNS = 8


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required artifact not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sidecar_path(path: Path) -> Path:
    return path.with_name(f"{path.name}.metadata.json")


def _require_success_sidecar(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required artifact not found: {path}")
    sidecar = _sidecar_path(path)
    if not sidecar.is_file():
        raise FileNotFoundError(f"Required sidecar not found: {sidecar}")
    metadata = json.loads(sidecar.read_text(encoding="utf-8"))
    if metadata.get("status") != "success":
        raise ValueError(f"Artifact sidecar is not successful: {sidecar}")
    return metadata


def _clean_number(value: Any) -> Any:
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _summarize_numeric_columns(frame: pd.DataFrame, max_columns: int = MAX_SUMMARY_COLUMNS) -> dict[str, Any]:
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        return {}
    ranked = numeric.notna().sum().sort_values(ascending=False)
    summary: dict[str, Any] = {}
    for column in ranked.index[:max_columns]:
        series = numeric[column].dropna()
        summary[str(column)] = {
            "n_valid": int(series.shape[0]),
            "n_total": int(len(frame)),
            "mean": _clean_number(float(series.mean())) if not series.empty else None,
            "median": _clean_number(float(series.median())) if not series.empty else None,
            "min": _clean_number(float(series.min())) if not series.empty else None,
            "max": _clean_number(float(series.max())) if not series.empty else None,
        }
    return summary


def _resolve_artifact_path(entry_path: str, analysis_dir: Path) -> Path:
    normalized = entry_path.replace("\\", "/")

    if normalized.startswith("data/analysis/"):
        suffix = normalized[len("data/analysis/") :]
        return analysis_dir / suffix

    if normalized.startswith("assets/"):
        return PROJECT_ROOT / normalized

    if normalized.startswith("./"):
        return (analysis_dir.parent / normalized[2:]).resolve()

    project_relative = Path(normalized)
    if project_relative.is_absolute():
        return project_relative
    return analysis_dir / project_relative.name


def build_fact_sheet(artifact_id: str, entry: dict[str, Any], *, analysis_dir: Path) -> dict[str, Any]:
    """Build a compact fact-sheet for one cross-evidence artifact."""
    artifact_path = _resolve_artifact_path(str(entry["path"]), analysis_dir)
    if not artifact_path.is_file():
        raise FileNotFoundError(f"Cross-evidence artifact not found: {artifact_path}")

    metadata: dict[str, Any] = {}
    try:
        metadata = _require_success_sidecar(artifact_path)
    except FileNotFoundError:
        if entry.get("kind") in {"figure", "report", "report_collection", "manifest"}:
            metadata = {"status": "success", "contract_version": entry.get("contract_version")}
        else:
            raise

    fact: dict[str, Any] = {
        "artifact_id": artifact_id,
        "kind": entry.get("kind"),
        "producer_script": entry.get("producer_script"),
        "unit_of_analysis": entry.get("unit_of_analysis"),
        "contract_version": metadata.get("contract_version") or entry.get("contract_version"),
        "evidence_scope": entry.get("evidence_scope"),
        "evidence_type": entry.get("evidence_type"),
        "narrative_acts": entry.get("acts", []),
        "path": str(artifact_path.relative_to(PROJECT_ROOT)) if artifact_path.is_relative_to(PROJECT_ROOT) else str(artifact_path),
    }

    suffix = artifact_path.suffix.lower()
    if suffix == ".parquet":
        frame = pd.read_parquet(artifact_path)
        fact.update(
            {
                "n_rows": int(len(frame)),
                "n_columns": int(len(frame.columns)),
                "columns": list(frame.columns),
                "numeric_summary": _summarize_numeric_columns(frame),
            }
        )
    elif suffix == ".csv":
        frame = pd.read_csv(artifact_path)
        fact.update(
            {
                "n_rows": int(len(frame)),
                "n_columns": int(len(frame.columns)),
                "columns": list(frame.columns),
                "numeric_summary": _summarize_numeric_columns(frame),
            }
        )
    elif suffix == ".json":
        payload = _load_json(artifact_path)
        fact.update(
            {
                "status": payload.get("status"),
                "contract_version": payload.get("contract_version", metadata.get("contract_version")),
                "summary_keys": list(payload.keys())[:12],
            }
        )
    else:
        fact["summary_note"] = "Artifact exists but no bounded fact-sheet payload was generated for this file type."
    return fact


def mock_narrative_backend(prompt: str) -> str:
    return (
        "_Offline mock backend: this cross-evidence report was generated without a "
        "remote LLM call. The prompt was grounded only in compact fact-sheet values._\n"
    )


def openai_narrative_backend(prompt: str, *, client: Any, model: str, system_prompt: str) -> str:
    config = MODEL_CONFIG["qualitative_mining"]
    gateway = LLMCallGateway(client)
    return gateway.chat_json(
        observation_id=f"cross_evidence_report:{hashlib.sha256(prompt.encode('utf-8')).hexdigest()}",
        model=model,
        system_prompt=system_prompt,
        user_prompt=prompt,
        request_options={"temperature": float(config["temperature"])},
    )


def _write_report(report_path: Path, content: str, *, source_checksum: str, options: dict[str, Any]) -> None:
    if not content.strip():
        raise ValueError(f"Empty narrative report content for {report_path}")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    invalidate_stale_artifact(report_path, source_checksum)
    report_path.write_text(content.strip() + "\n", encoding="utf-8")
    write_artifact_metadata(
        report_path,
        source_checksum,
        contract_version=CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT_VERSION,
        options=options,
    )


def main() -> None:
    """Generate every available cross-evidence artifact report that is missing or stale."""
    parser = argparse.ArgumentParser(description="Generate independent narrative reports for cross-evidence artifacts")
    parser.add_argument("--analysis-dir", type=Path, default=ANALYSIS_DIR)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--backend", choices=("openai", "mock"), default="openai")
    parser.add_argument("--model", default=str(MODEL_CONFIG["qualitative_mining"]["model"]))
    parser.add_argument("--force", action="store_true", help="Regenerate selected reports even if current")
    parser.add_argument(
        "--only",
        nargs="+",
        default=None,
        help="Limit generation to specific cross-evidence artifact ids",
    )
    args = parser.parse_args()

    analysis_dir = args.analysis_dir
    default_reports_root = analysis_dir / "cross_evidence" / "reports" / "artifact_reports"
    output_dir = args.output_dir or default_reports_root
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = set(args.only) if args.only else None

    client = None
    if args.backend == "openai":
        load_project_environment()
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("openai package is not installed") from error
        client = OpenAI()

    def call_backend(prompt: str) -> str:
        if client is not None:
            return openai_narrative_backend(prompt, client=client, model=args.model, system_prompt=CROSS_EVIDENCE_ARTIFACT_REPORT_SYSTEM_PROMPT)
        return mock_narrative_backend(prompt)

    generated = 0
    skipped = 0
    for artifact_id, entry in CROSS_EVIDENCE_ARTIFACT_REGISTRY.items():
        if entry.get("kind") not in {"dataset", "result", "figure_data", "manifest"}:
            continue
        if selected is not None and artifact_id not in selected:
            continue
        artifact_path = _resolve_artifact_path(str(entry["path"]), analysis_dir)
        if not artifact_path.is_file():
            logger.info("Skipping cross-evidence artifact without a current file: %s", artifact_id)
            continue
        fact_sheet = build_fact_sheet(artifact_id, entry, analysis_dir=analysis_dir)
        report_path = output_dir / f"{artifact_id}.md"
        options = {
            "prompt_version": CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT_VERSION,
            "backend": args.backend,
            "model": args.model,
            "artifact_id": artifact_id,
            "fact_sheet": fact_sheet,
        }
        source_paths = [artifact_path, _sidecar_path(artifact_path), Path(__file__).with_name("pipeline_prompts.py")]
        checksum = input_checksum(source_paths, options)
        if args.force:
            invalidate_stale_artifact(report_path, "force-regeneration")
        if is_current_artifact(report_path, checksum):
            logger.info("Cross-evidence artifact report is current, skipping LLM call: %s", report_path)
            skipped += 1
            continue
        prompt = CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT.format(
            fact_sheet_json=json.dumps(fact_sheet, sort_keys=True, default=str)
        )
        content = call_backend(prompt)
        _write_report(report_path, content, source_checksum=checksum, options=options)
        generated += 1
        logger.info("Generated cross-evidence artifact report: %s", report_path)

    print(f"Cross-evidence narrative reports: written={generated} skipped={skipped}")


if __name__ == "__main__":
    main()
