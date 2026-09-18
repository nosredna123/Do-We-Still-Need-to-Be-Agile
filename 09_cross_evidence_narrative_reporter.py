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
from pipeline_config import CROSS_EVIDENCE_ARTIFACT_REGISTRY, MODEL_CONFIG, NARRATIVE_ACT_REGISTRY
from pipeline_core import ANALYSIS_DIR, PROJECT_ROOT, input_checksum, invalidate_stale_artifact, is_current_artifact, load_project_environment, write_artifact_metadata
from pipeline_prompts import (
    CROSS_EVIDENCE_ACT_REPORT_PROMPT,
    CROSS_EVIDENCE_ACT_REPORT_PROMPT_VERSION,
    CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT,
    CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT_VERSION,
    CROSS_EVIDENCE_ARTIFACT_REPORT_SYSTEM_PROMPT,
    CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT,
    CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT_VERSION,
    CROSS_EVIDENCE_CONSOLIDATED_REPORT_SYSTEM_PROMPT,
    CROSS_EVIDENCE_GROUP_REPORT_PROMPT,
    CROSS_EVIDENCE_GROUP_REPORT_PROMPT_VERSION,
)

logger = logging.getLogger(__name__)

DEFAULT_REPORTS_DIRNAME = "reports"
MAX_SUMMARY_COLUMNS = 8
GROUP_NAME_PATTERN_MAP = (
    ("temporal_escalation", ("temporal", "delta", "escalation", "semester", "t2_t3")),
    ("source_churn", ("source_churn", "source_events", "planning_rework", "file_category_churn")),
    ("evaluator_crossing", ("scope", "progress", "evaluator", "project_progress", "scope_applicability")),
    ("author_pressure", ("author", "commits_per_author", "commit_gini", "max_author")),
    ("robustness", ("robustness", "leave_one_out", "overlap", "sensitivity")),
)


def _as_int_list(value: Any) -> list[int]:
    if value is None:
        return []
    if isinstance(value, list):
        return [int(item) for item in value if item is not None]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            text = text.replace("[", "").replace("]", "").replace(" ", "")
            if not text:
                return []
            return [int(part) for part in text.split(",") if part]
        if isinstance(parsed, list):
            return [int(item) for item in parsed if item is not None]
        return [int(parsed)]
    return [int(value)]


def _group_name_for_analysis_id(analysis_id: str) -> str:
    lowered = str(analysis_id).lower()
    for group_name, patterns in GROUP_NAME_PATTERN_MAP:
        if any(pattern in lowered for pattern in patterns):
            return group_name
    return "methodological_warnings"


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


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


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
    _ = prompt
    config = MODEL_CONFIG["qualitative_mining"]
    gateway = LLMCallGateway(client)
    return gateway.chat_json(
        observation_id=f"cross_evidence_report:{hashlib.sha256(prompt.encode('utf-8')).hexdigest()}",
        model=model,
        system_prompt=system_prompt,
        user_prompt=prompt,
        request_options={"temperature": float(config["temperature"])},
    )


def _write_report(
    report_path: Path,
    content: str,
    *,
    source_checksum: str,
    options: dict[str, Any],
    contract_version: str,
) -> None:
    if not content.strip():
        raise ValueError(f"Empty narrative report content for {report_path}")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    invalidate_stale_artifact(report_path, source_checksum)
    report_path.write_text(content.strip() + "\n", encoding="utf-8")
    write_artifact_metadata(
        report_path,
        source_checksum,
        contract_version=contract_version,
        options=options,
    )


def build_group_payload(group_name: str, matrix_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate evidence-matrix rows into a bounded synthetic group summary."""
    group_rows = [
        row for row in matrix_rows if _group_name_for_analysis_id(str(row.get("analysis_id", ""))) == group_name
    ]
    if not group_rows:
        group_rows = [
            row for row in matrix_rows if str(row.get("source_artifact", "")).startswith(group_name)
        ]

    vote_counts: dict[str, int] = {}
    details: list[dict[str, Any]] = []
    for row in group_rows:
        verdict = str(row.get("verdict", "inconclusive")).lower()
        vote_counts[verdict] = vote_counts.get(verdict, 0) + 1
        details.append(
            {
                "analysis_id": row.get("analysis_id"),
                "source_artifact": row.get("source_artifact"),
                "priority": row.get("priority"),
                "verdict": verdict,
                "publication_readiness": row.get("publication_readiness"),
                "recommended_use": row.get("recommended_use"),
                "summary": row.get("summary"),
                "coefficient": row.get("coefficient"),
                "p_value": row.get("p_value"),
                "robustness_class": row.get("robustness_class"),
            }
        )

    if vote_counts.get("supports", 0) > 0:
        status = "supports"
    elif vote_counts.get("inconclusive", 0) > 0 and vote_counts.get("supports", 0) == 0:
        status = "contextualizes"
    else:
        status = "limits"

    return {
        "group_name": group_name,
        "artifact_count": len(details),
        "status": status,
        "verdict_counts": vote_counts,
        "member_artifacts": details,
    }


def build_act_payload(act_number: int, matrix_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate evidence across one narrative act using the priority matrix."""
    act_rows = [
        row for row in matrix_rows if act_number in _as_int_list(row.get("narrative_acts"))
    ]
    counts: dict[str, int] = {}
    for row in act_rows:
        verdict = str(row.get("verdict", "inconclusive")).lower()
        counts[verdict] = counts.get(verdict, 0) + 1

    act_title = NARRATIVE_ACT_REGISTRY.get(act_number, {}).get("title", f"Act {act_number}")
    act_description = {
        1: "Contextualizes the broader historical and methodological ceiling of the Agile claim.",
        2: "Diagnoses planning debt as late-stage rework and source churn under compressed design capacity.",
        3: "Tests whether coordination pressure, late instability, and author concentration explain the apparent productivity illusion.",
        4: "Reframes the thesis toward cognitive clarity, explicit specifications, and sustainable AI-supported delivery.",
    }.get(act_number, "Synthesizes the evidence for this narrative act.")

    if counts.get("supports", 0) > 0:
        status = "supports"
    elif counts.get("inconclusive", 0) > 0:
        status = "contextualizes"
    else:
        status = "limits"

    return {
        "act_number": act_number,
        "act_title": act_title,
        "act_description": act_description,
        "artifact_count": len(act_rows),
        "status": status,
        "verdict_counts": counts,
        "bound_artifacts": [
            {
                "analysis_id": row.get("analysis_id"),
                "source_artifact": row.get("source_artifact"),
                "verdict": str(row.get("verdict", "inconclusive")).lower(),
                "publication_readiness": row.get("publication_readiness"),
                "recommended_use": row.get("recommended_use"),
            }
            for row in act_rows
        ],
    }


def build_consolidated_payload(
    *,
    matrix_rows: list[dict[str, Any]],
    report_root: Path,
    artifact_reports_dir: Path,
    group_reports_dir: Path,
    act_reports_dir: Path,
) -> dict[str, Any]:
    """Assemble the final cross-evidence summary from the report hierarchy."""
    evidence_rows: list[dict[str, Any]] = []
    for row in matrix_rows:
        evidence_rows.append(
            {
                "artifact_id": row.get("source_artifact"),
                "group_name": _group_name_for_analysis_id(str(row.get("analysis_id", ""))),
                "unit_of_analysis": row.get("unit_of_analysis") or row.get("stratum") or "analysis_result",
                "n_valid": row.get("n_valid"),
                "principal_result": row.get("summary") or row.get("recommended_use") or row.get("verdict"),
                "status": str(row.get("verdict", "inconclusive")).lower(),
            }
        )

    status_counts = {"supports": 0, "contextualizes": 0, "limits": 0}
    for row in evidence_rows:
        status = row["status"]
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts["contextualizes"] += 1

    if status_counts["supports"] > 0:
        verdict = "supports"
        verdict_reason = "supporting_evidence_present"
    elif status_counts["contextualizes"] > 0:
        verdict = "contextualizes"
        verdict_reason = "evidence_is_mainly_contextual"
    else:
        verdict = "limits"
        verdict_reason = "evidence_is_limiting"

    methodological_warnings = [
        {
            "artifact_id": row.get("source_artifact"),
            "group_name": _group_name_for_analysis_id(str(row.get("analysis_id", ""))),
            "issue": row.get("summary") or row.get("recommended_use") or row.get("verdict"),
        }
        for row in matrix_rows
        if str(row.get("publication_readiness", "")).lower() in {"exploratory_only", "do_not_generalize", "methodological_warning"}
    ]

    report_index = [
        _display_path(report_root / "artifact_reports"),
        _display_path(report_root / "group_reports"),
        _display_path(report_root / "act_reports"),
        _display_path(report_root / "00_cross_evidence_consolidated_report.md"),
    ]

    return {
        "report_index": report_index,
        "evidence_matrix": evidence_rows,
        "aggregate_status": verdict,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "counts": status_counts,
        "methodological_warnings": methodological_warnings,
        "recommendations": [
            "Treat the strongest associations as candidate hypotheses rather than confirmed claims.",
            "Keep the warning-heavy evidence groups in a cautionary interpretation layer.",
        ],
        "artifact_reports_dir": _display_path(artifact_reports_dir),
        "group_reports_dir": _display_path(group_reports_dir),
        "act_reports_dir": _display_path(act_reports_dir),
    }


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
    default_reports_root = analysis_dir / "cross_evidence" / "reports"
    default_artifact_reports_root = default_reports_root / "artifact_reports"
    output_dir = args.output_dir or default_artifact_reports_root
    output_dir.mkdir(parents=True, exist_ok=True)
    report_root = output_dir.parent if output_dir.parent.name == "reports" else default_reports_root
    group_output_dir = report_root / "group_reports"
    act_output_dir = report_root / "act_reports"
    group_output_dir.mkdir(parents=True, exist_ok=True)
    act_output_dir.mkdir(parents=True, exist_ok=True)
    selected = set(args.only) if args.only else None

    client = None
    if args.backend == "openai":
        load_project_environment()
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("openai package is not installed") from error
        client = OpenAI()

    def call_backend(prompt: str, *, system_prompt: str | None = None) -> str:
        if client is not None:
            return openai_narrative_backend(
                prompt,
                client=client,
                model=args.model,
                system_prompt=system_prompt or CROSS_EVIDENCE_ARTIFACT_REPORT_SYSTEM_PROMPT,
            )
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
        _write_report(
            report_path,
            content,
            source_checksum=checksum,
            options=options,
            contract_version=CROSS_EVIDENCE_ARTIFACT_REPORT_PROMPT_VERSION,
        )
        generated += 1
        logger.info("Generated cross-evidence artifact report: %s", report_path)

    matrix_path = analysis_dir / "cross_evidence" / "results" / "evidence_priority_matrix.csv"
    if matrix_path.is_file():
        matrix_rows = pd.read_csv(matrix_path).to_dict("records")
        group_names = [
            "temporal_escalation",
            "source_churn",
            "evaluator_crossing",
            "author_pressure",
            "robustness",
            "methodological_warnings",
        ]
        for group_name in group_names:
            payload = build_group_payload(group_name, matrix_rows)
            report_id = group_name
            report_path = group_output_dir / f"{report_id}.md"
            if selected is not None and report_id not in selected:
                continue
            options = {
                "prompt_version": CROSS_EVIDENCE_GROUP_REPORT_PROMPT_VERSION,
                "backend": args.backend,
                "model": args.model,
                "group_name": group_name,
                "payload": payload,
            }
            source_paths = [matrix_path, _sidecar_path(matrix_path), Path(__file__).with_name("pipeline_prompts.py")]
            checksum = input_checksum(source_paths, options)
            if args.force:
                invalidate_stale_artifact(report_path, "force-regeneration")
            if is_current_artifact(report_path, checksum):
                logger.info("Cross-evidence group report current, skipping LLM call: %s", report_path)
                skipped += 1
                continue
            prompt = CROSS_EVIDENCE_GROUP_REPORT_PROMPT.format(
                group_name=group_name,
                payload_json=json.dumps(payload, sort_keys=True, default=str),
            )
            content = call_backend(prompt, system_prompt=CROSS_EVIDENCE_ARTIFACT_REPORT_SYSTEM_PROMPT)
            _write_report(
                report_path,
                content,
                source_checksum=checksum,
                options=options,
                contract_version=CROSS_EVIDENCE_GROUP_REPORT_PROMPT_VERSION,
            )
            generated += 1
            logger.info("Generated cross-evidence group report: %s", report_path)

        for act_number in sorted(NARRATIVE_ACT_REGISTRY):
            payload = build_act_payload(act_number, matrix_rows)
            report_id = f"act_{act_number}_{NARRATIVE_ACT_REGISTRY[act_number]['slug']}"
            report_path = act_output_dir / f"{report_id}.md"
            if selected is not None and report_id not in selected:
                continue
            options = {
                "prompt_version": CROSS_EVIDENCE_ACT_REPORT_PROMPT_VERSION,
                "backend": args.backend,
                "model": args.model,
                "act_number": act_number,
                "payload": payload,
            }
            source_paths = [matrix_path, _sidecar_path(matrix_path), Path(__file__).with_name("pipeline_prompts.py")]
            checksum = input_checksum(source_paths, options)
            if args.force:
                invalidate_stale_artifact(report_path, "force-regeneration")
            if is_current_artifact(report_path, checksum):
                logger.info("Cross-evidence act report current, skipping LLM call: %s", report_path)
                skipped += 1
                continue
            prompt = CROSS_EVIDENCE_ACT_REPORT_PROMPT.format(
                act_number=act_number,
                act_title=NARRATIVE_ACT_REGISTRY[act_number]["title"],
                payload_json=json.dumps(payload, sort_keys=True, default=str),
            )
            content = call_backend(prompt, system_prompt=CROSS_EVIDENCE_ARTIFACT_REPORT_SYSTEM_PROMPT)
            _write_report(
                report_path,
                content,
                source_checksum=checksum,
                options=options,
                contract_version=CROSS_EVIDENCE_ACT_REPORT_PROMPT_VERSION,
            )
            generated += 1
            logger.info("Generated cross-evidence act report: %s", report_path)

        consolidated_report_path = report_root / "00_cross_evidence_consolidated_report.md"
        report_id = "00_cross_evidence_consolidated_report"
        if selected is None or report_id in selected:
            consolidated_payload = build_consolidated_payload(
                matrix_rows=matrix_rows,
                report_root=report_root,
                artifact_reports_dir=output_dir,
                group_reports_dir=group_output_dir,
                act_reports_dir=act_output_dir,
            )
            options = {
                "prompt_version": CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT_VERSION,
                "backend": args.backend,
                "model": args.model,
                "payload": consolidated_payload,
            }
            source_paths = [
                matrix_path,
                _sidecar_path(matrix_path),
                Path(__file__).with_name("pipeline_prompts.py"),
                *[path for path in output_dir.glob("*.md")],
                *[path for path in group_output_dir.glob("*.md")],
                *[path for path in act_output_dir.glob("*.md")],
            ]
            checksum = input_checksum(source_paths, options)
            if args.force:
                invalidate_stale_artifact(consolidated_report_path, "force-regeneration")
            if is_current_artifact(consolidated_report_path, checksum):
                logger.info("Cross-evidence consolidated report current, skipping LLM call: %s", consolidated_report_path)
                skipped += 1
            else:
                prompt = CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT.format(
                    payload_json=json.dumps(consolidated_payload, sort_keys=True, default=str),
                )
                content = call_backend(prompt, system_prompt=CROSS_EVIDENCE_CONSOLIDATED_REPORT_SYSTEM_PROMPT)
                _write_report(
                    consolidated_report_path,
                    content,
                    source_checksum=checksum,
                    options=options,
                    contract_version=CROSS_EVIDENCE_CONSOLIDATED_REPORT_PROMPT_VERSION,
                )
                generated += 1
                logger.info("Generated cross-evidence consolidated report: %s", consolidated_report_path)

    print(f"Cross-evidence narrative reports: written={generated} skipped={skipped}")


if __name__ == "__main__":
    main()
