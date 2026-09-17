"""Generate didactic English narrative audit reports for Phase 2 artifacts.

This is the Phase 2.5 (docs/02a.artifact-narrative-audit.md) producer. It
never re-derives Phase 2 statistics: it reads already-validated artifacts and
sidecars, builds a small bounded "fact sheet" of numbers per artifact, and
asks an LLM only to write the didactic prose that cites those exact numbers.
No raw survey/transcript text or private evidence field is ever read or sent
to the model.
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

from pipeline_config import (
    ARTIFACT_NARRATIVE_REGISTRY,
    MODEL_CONFIG,
    NARRATIVE_ACT_REGISTRY,
    NARRATIVE_AUDIT_MIN_SUFFICIENT_TEAM_N,
    NARRATIVE_REPORT_CONTRACT_VERSION,
)
from pipeline_core import (
    ANALYSIS_DIR,
    PROJECT_ROOT,
    input_checksum,
    invalidate_stale_artifact,
    is_current_artifact,
    load_project_environment,
    write_artifact_metadata,
)
from pipeline_prompts import (
    ACT_SYNTHESIS_PROMPT,
    ACT_SYNTHESIS_PROMPT_VERSION,
    ACT_SYNTHESIS_SYSTEM_PROMPT,
    ARTIFACT_REPORT_PROMPT,
    ARTIFACT_REPORT_PROMPT_VERSION,
    ARTIFACT_REPORT_SYSTEM_PROMPT,
    AUDIT_VERDICT_PROMPT,
    AUDIT_VERDICT_PROMPT_VERSION,
    AUDIT_VERDICT_SYSTEM_PROMPT,
)
from llm_gateway import LLMCallGateway

logger = logging.getLogger(__name__)

REPORTS_DIRNAME = "artifact_reports"
FIGURE_MANIFEST_NAME = "figure_manifest.json"
STATISTICAL_MANIFEST_NAME = "statistical_dataset_manifest.json"
MAX_KEY_NUMERIC_COLUMNS = 8
MANIFEST_DATASET_IDS = {"team_metrics", "cut_context_metrics", "student_nlp", "transcript_nlp"}
REMEDIATION_OPTIONS = [
    "Collect additional semesters/teams to raise team_semester n toward the "
    "configured sufficiency threshold.",
    "Reframe Phase 3/4 claims as exploratory/descriptive case-study findings "
    "rather than confirmatory results.",
    "Expand qualitative triangulation (transcripts, open-ended responses) to "
    "compensate for low quantitative power.",
    "Add repository-level covariates (team size, prior experience) to explain "
    "variance beyond the current primary pairs.",
]
ACT_DESCRIPTIONS = {
    1: (
        "Argues that the Agile Manifesto solved waterfall paralysis in 2001, "
        "but that Generative-AI-era complexity and coding speed have pushed "
        "pure empiricism past its scalability ceiling."
    ),
    2: (
        "Argues that skipping BDUF does not remove planning work; it defers "
        "and multiplies it as Planning Debt, visible as structural drift and "
        "as human/computational waste such as Code Churn."
    ),
    3: (
        "Argues that skipping upfront design collapses a team's asynchronous "
        "coordination capacity, producing cognitive overload and a "
        "late-stage integration bottleneck (the 'hero developer' pattern)."
    ),
    4: (
        "Argues that the current data should invert the Agile Manifesto's "
        "values toward cognitive clarity, actionable specifications (SDD), "
        "continuous automated validation, and sustainable predictive design."
    ),
}


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


def _require_success_json(path: Path) -> dict[str, Any]:
    payload = _load_json(path)
    if payload.get("status") != "success":
        raise ValueError(f"Artifact status is not successful: {path}")
    return payload


def _clean_number(value: Any) -> Any:
    """Convert NaN float values into JSON-safe null; pass through everything else."""
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def _top_numeric_columns(frame: pd.DataFrame, max_columns: int = MAX_KEY_NUMERIC_COLUMNS) -> dict[str, Any]:
    """Summarize the most populated numeric columns of a tabular artifact."""
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


def _trim_manifest_dataset(entry: dict[str, Any]) -> dict[str, Any]:
    """Keep only the compact scalar fields of one manifest dataset entry."""
    trimmed = {
        key: entry[key]
        for key in ("unit_of_analysis", "observation_key", "n_rows", "n_unique_keys", "coverage")
        if key in entry
    }
    variables = entry.get("variables")
    if isinstance(variables, list):
        trimmed["variables_missingness"] = [
            {
                "name": variable.get("name"),
                "dtype": variable.get("dtype"),
                "n_total": variable.get("n_total"),
                "n_missing": variable.get("n_missing"),
            }
            for variable in variables
            if isinstance(variable, dict)
        ]
    return trimmed


def _trim_exclusions(payload: dict[str, Any]) -> dict[str, Any]:
    """Keep only bounded counts and reasons from a private exclusions report."""
    trimmed: dict[str, Any] = {"contract_version": payload.get("contract_version")}
    sources = payload.get("sources")
    if isinstance(sources, dict):
        trimmed["sources"] = {
            name: {
                "rows": entry.get("rows"),
                "affected_count": len(entry.get("affected_keys") or []),
                "affected_reasons": sorted(
                    {
                        item.get("reason")
                        for item in (entry.get("affected_keys") or [])
                        if isinstance(item, dict) and item.get("reason")
                    }
                ),
            }
            for name, entry in sources.items()
            if isinstance(entry, dict)
        }
    exclusions = payload.get("exclusions")
    if isinstance(exclusions, list):
        trimmed["exclusions_summary"] = [
            {
                "dataset": item.get("dataset"),
                "variable": item.get("variable"),
                "reason": item.get("reason"),
                "n_excluded": item.get("n_excluded"),
            }
            for item in exclusions
            if isinstance(item, dict)
        ][:50]
    return trimmed


def _load_analysis_rows(path: Path) -> dict[str, dict[str, Any]]:
    """Load one results CSV keyed by analysis_id with JSON-safe values."""
    _require_success_sidecar(path)
    frame = pd.read_csv(path)
    if "analysis_id" not in frame.columns:
        raise ValueError(f"{path} is missing analysis_id")
    return {
        str(row["analysis_id"]): {key: _clean_number(value) for key, value in row.items()}
        for row in frame.to_dict("records")
    }


def _single_test_verdict(row: dict[str, Any] | None) -> str:
    """Classify one primary correlation/hypothesis row deterministically."""
    if row is None:
        return "not_tested"
    if row.get("status") == "unavailable":
        return "unavailable"
    p_value = row.get("p_value")
    if p_value is None:
        return "inconclusive"
    return "supports" if float(p_value) < 0.05 else "inconclusive"


def compute_verdict(
    entry: dict[str, Any],
    correlation_rows: dict[str, dict[str, Any]],
    hypothesis_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Compute the deterministic contribution verdict for one artifact."""
    if entry.get("verdict_mode") != "aggregate_from_tests":
        return {"overall": "descriptive_infrastructure", "tests": []}
    tests: list[dict[str, Any]] = []
    for analysis_id in entry.get("related_correlations", []):
        tests.append(
            {
                "analysis_id": analysis_id,
                "kind": "correlation",
                "verdict": _single_test_verdict(correlation_rows.get(analysis_id)),
            }
        )
    for analysis_id in entry.get("related_hypotheses", []):
        tests.append(
            {
                "analysis_id": analysis_id,
                "kind": "hypothesis",
                "verdict": _single_test_verdict(hypothesis_rows.get(analysis_id)),
            }
        )
    if not tests:
        overall = "descriptive_infrastructure"
    elif any(test["verdict"] == "supports" for test in tests):
        overall = "supports_partially"
    elif all(test["verdict"] == "unavailable" for test in tests):
        overall = "unavailable"
    else:
        overall = "inconclusive"
    return {"overall": overall, "tests": tests}


def build_fact_sheet(
    artifact_id: str,
    entry: dict[str, Any],
    *,
    analysis_dir: Path,
    statistical_manifest: dict[str, Any],
    figure_manifest: dict[str, Any],
    correlation_rows: dict[str, dict[str, Any]],
    hypothesis_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build the bounded, no-PII fact sheet consumed by the artifact-report prompt."""
    kind = entry["kind"]
    fact: dict[str, Any] = {
        "artifact_id": artifact_id,
        "kind": kind,
        "producer_script": entry.get("producer_script"),
        "narrative_acts": entry.get("acts", []),
        "narrative_act_titles": [
            NARRATIVE_ACT_REGISTRY[act]["title"] for act in entry.get("acts", []) if act in NARRATIVE_ACT_REGISTRY
        ],
        "verdict_summary": compute_verdict(entry, correlation_rows, hypothesis_rows),
    }

    if kind == "parquet":
        path = analysis_dir / str(entry["path"])
        metadata = _require_success_sidecar(path)
        frame = pd.read_parquet(path)
        fact.update(
            {
                "relative_path": f"data/analysis/{entry['path']}",
                "row_count": int(len(frame)),
                "column_count": int(len(frame.columns)),
                "contract_version": metadata.get("contract_version"),
            }
        )
        if artifact_id in MANIFEST_DATASET_IDS:
            dataset_entry = statistical_manifest.get("datasets", {}).get(artifact_id)
            if isinstance(dataset_entry, dict):
                fact["manifest_summary"] = _trim_manifest_dataset(dataset_entry)
        else:
            fact["key_numeric_columns"] = _top_numeric_columns(frame)
    elif kind == "csv":
        path = analysis_dir / str(entry["path"])
        metadata = _require_success_sidecar(path)
        frame = pd.read_csv(path)
        fact.update(
            {
                "relative_path": f"data/analysis/{entry['path']}",
                "row_count": int(len(frame)),
                "contract_version": metadata.get("contract_version"),
                "rows": [{key: _clean_number(value) for key, value in row.items()} for row in frame.to_dict("records")],
            }
        )
    elif kind == "json":
        path = analysis_dir / str(entry["path"])
        payload = _require_success_json(path)
        fact["relative_path"] = f"data/analysis/{entry['path']}"
        fact["contract_version"] = payload.get("contract_version")
        fact["status"] = payload.get("status")
        if artifact_id == "phase2_contract_report":
            contracts = payload.get("contracts", {})
            fact["contracts_summary"] = {
                name: {
                    "total_rows": sum(
                        int(item.get("rows", 0)) for item in (contract.get("counts_by_semester_and_cut") or [])
                    ),
                    "counts_by_semester_and_cut": contract.get("counts_by_semester_and_cut"),
                }
                for name, contract in contracts.items()
                if isinstance(contract, dict)
            }
        elif artifact_id == "statistical_dataset_manifest":
            datasets = payload.get("datasets", {})
            fact["datasets_summary"] = {
                name: _trim_manifest_dataset(dataset_entry)
                for name, dataset_entry in datasets.items()
                if isinstance(dataset_entry, dict)
            }
            fact["correlations_status"] = (payload.get("correlations") or {}).get("status")
            fact["hypotheses_status"] = (payload.get("hypotheses") or {}).get("status")
    elif kind == "figure":
        figures_by_id = {
            figure.get("figure_id"): figure
            for figure in figure_manifest.get("figures", [])
            if isinstance(figure, dict)
        }
        figure_entry = figures_by_id.get(entry["figure_id"])
        if figure_entry is None:
            raise ValueError(f"Figure not found in figure_manifest.json: {entry['figure_id']}")
        if figure_entry.get("status") != "success":
            raise ValueError(f"Figure status is not successful: {entry['figure_id']}")
        fact.update(
            {
                "relative_path": figure_entry.get("interactive_path"),
                "category": figure_entry.get("category"),
                "source": figure_entry.get("source"),
                "unit_of_analysis": figure_entry.get("unit_of_analysis"),
                "variables": figure_entry.get("variables"),
                "n_total": figure_entry.get("n_total"),
                "n_valid": figure_entry.get("n_valid"),
                "n_missing": figure_entry.get("n_missing"),
                "limitations": figure_entry.get("limitations"),
                "transformations": figure_entry.get("transformations"),
                "scale_notes": figure_entry.get("scale_notes"),
            }
        )
    else:
        raise ValueError(f"Unsupported artifact kind: {kind}")

    exclusions_path = entry.get("exclusions_path")
    if exclusions_path:
        fact["exclusions_summary"] = _trim_exclusions(_load_json(analysis_dir / str(exclusions_path)))
    return fact


def _artifact_source_paths(
    entry: dict[str, Any],
    *,
    analysis_dir: Path,
    figure_manifest_path: Path,
    statistical_manifest_path: Path,
) -> list[Path]:
    """Return the physical files that must be current for one Layer-1 report."""
    paths = [Path(__file__).with_name("pipeline_prompts.py")]
    kind = entry["kind"]
    if kind in ("parquet", "csv"):
        path = analysis_dir / str(entry["path"])
        paths.extend([path, _sidecar_path(path)])
        if kind == "parquet" and entry.get("path", "").removesuffix(".parquet") in MANIFEST_DATASET_IDS:
            paths.append(statistical_manifest_path)
    elif kind == "json":
        paths.append(analysis_dir / str(entry["path"]))
    elif kind == "figure":
        paths.append(figure_manifest_path)
    if entry.get("exclusions_path"):
        paths.append(analysis_dir / str(entry["exclusions_path"]))
    if entry.get("verdict_mode") == "aggregate_from_tests":
        paths.append(analysis_dir / "correlation_results.csv")
        paths.append(_sidecar_path(analysis_dir / "correlation_results.csv"))
        paths.append(analysis_dir / "hypothesis_results.csv")
        paths.append(_sidecar_path(analysis_dir / "hypothesis_results.csv"))
    return paths


def build_act_payload(act_number: int, artifact_facts: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Aggregate Layer-1 verdicts bound to one narrative act."""
    act_info = NARRATIVE_ACT_REGISTRY[act_number]
    bound = [
        {"artifact_id": artifact_id, "verdict": fact["verdict_summary"]["overall"]}
        for artifact_id, fact in artifact_facts.items()
        if act_number in fact.get("narrative_acts", [])
    ]
    counts: dict[str, int] = {}
    for item in bound:
        counts[item["verdict"]] = counts.get(item["verdict"], 0) + 1
    tested = [item for item in bound if item["verdict"] != "descriptive_infrastructure"]
    if not tested:
        act_status = "not_yet_tested"
    elif any(item["verdict"] == "supports_partially" for item in tested):
        act_status = "partially_supported"
    else:
        act_status = "unsupported_by_current_tests"
    return {
        "act_number": act_number,
        "act_title": act_info["title"],
        "act_description": ACT_DESCRIPTIONS[act_number],
        "artifact_verdicts": bound,
        "verdict_counts": counts,
        "act_status": act_status,
    }


def compute_consolidated_verdict(
    correlation_rows: dict[str, dict[str, Any]],
    hypothesis_rows: dict[str, dict[str, Any]],
    team_semester_n: int,
) -> dict[str, Any]:
    """Compute the deterministic go/conditional-go/no-go verdict."""
    primary_rows = [
        row
        for row in list(correlation_rows.values()) + list(hypothesis_rows.values())
        if row.get("priority") == "primary"
    ]
    tested = [row for row in primary_rows if row.get("status") == "success"]
    supports = [row for row in tested if row.get("p_value") is not None and float(row["p_value"]) < 0.05]
    count_tested = len(tested)
    count_supports = len(supports)
    if count_tested == 0:
        verdict, reason = "no-go", "no_primary_test_executed"
    elif count_supports >= 1 and team_semester_n >= NARRATIVE_AUDIT_MIN_SUFFICIENT_TEAM_N:
        verdict, reason = "go", "significant_result_with_sufficient_sample"
    elif count_supports >= 1:
        verdict, reason = "conditional-go", "significant_result_but_small_sample"
    elif team_semester_n < NARRATIVE_AUDIT_MIN_SUFFICIENT_TEAM_N:
        verdict, reason = "conditional-go", "no_significant_result_and_small_sample_reframe_as_exploratory"
    else:
        verdict, reason = "no-go", "no_significant_result_with_sufficient_sample"
    return {
        "verdict": verdict,
        "verdict_reason": reason,
        "count_supports": count_supports,
        "count_tested": count_tested,
        "team_semester_n": team_semester_n,
    }


def mock_narrative_backend(prompt: str) -> str:
    """Return a deterministic offline placeholder report for tests/dry runs."""
    return (
        "_Offline mock backend: this report was generated without a remote "
        "LLM call. The injected fact sheet below is the only data this report "
        "would have been grounded on._\n"
    )


def openai_narrative_backend(prompt: str, *, client: Any, model: str, system_prompt: str) -> str:
    """Request one free-text narrative report through the central gateway."""
    config = MODEL_CONFIG["qualitative_mining"]
    gateway = LLMCallGateway(client)
    return gateway.chat_json(
        observation_id=f"narrative_audit:{hashlib.sha256(prompt.encode('utf-8')).hexdigest()}",
        model=model,
        system_prompt=system_prompt,
        user_prompt=prompt,
        request_options={"temperature": float(config["temperature"])},
    )


def _relative_path_label(path: Path) -> str:
    """Return a project-relative path label, falling back to the raw path."""
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _write_report(report_path: Path, content: str, *, source_checksum: str, options: dict[str, Any]) -> None:
    """Persist one narrative report and its resume sidecar."""
    if not content.strip():
        raise ValueError(f"Empty narrative report content for {report_path}")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    invalidate_stale_artifact(report_path, source_checksum)
    report_path.write_text(content.strip() + "\n", encoding="utf-8")
    write_artifact_metadata(
        report_path,
        source_checksum,
        contract_version=NARRATIVE_REPORT_CONTRACT_VERSION,
        options=options,
    )


def main() -> None:
    """Generate every Phase 2.5 narrative-audit report that is missing or stale."""
    parser = argparse.ArgumentParser(description="Generate the Phase 2.5 artifact narrative audit reports")
    parser.add_argument("--analysis-dir", type=Path, default=ANALYSIS_DIR)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--backend", choices=("openai", "mock"), default="openai")
    parser.add_argument("--model", default=str(MODEL_CONFIG["qualitative_mining"]["model"]))
    parser.add_argument("--force", action="store_true", help="Regenerate selected reports even if current")
    parser.add_argument(
        "--only",
        nargs="+",
        default=None,
        help="Limit generation to these report ids (artifact_id, act_<n>_<slug>, or 00_consolidated_audit)",
    )
    args = parser.parse_args()

    analysis_dir = args.analysis_dir
    output_dir = args.output_dir or (analysis_dir / REPORTS_DIRNAME)
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = set(args.only) if args.only else None

    figure_manifest_path = analysis_dir / FIGURE_MANIFEST_NAME
    needs_figures = any(entry["kind"] == "figure" for entry in ARTIFACT_NARRATIVE_REGISTRY.values())
    figure_manifest = _require_success_json(figure_manifest_path) if needs_figures else {}
    statistical_manifest_path = analysis_dir / STATISTICAL_MANIFEST_NAME
    statistical_manifest = _require_success_json(statistical_manifest_path)
    correlation_rows = _load_analysis_rows(analysis_dir / "correlation_results.csv")
    hypothesis_rows = _load_analysis_rows(analysis_dir / "hypothesis_results.csv")
    team_metrics_path = analysis_dir / "team_metrics.parquet"
    _require_success_sidecar(team_metrics_path)
    team_semester_n = int(len(pd.read_parquet(team_metrics_path)))

    client = None
    if args.backend == "openai":
        load_project_environment()
        try:
            from openai import OpenAI
        except ImportError as error:
            raise RuntimeError("openai package is not installed") from error
        client = OpenAI()

    def call_backend(prompt: str, system_prompt: str) -> str:
        if client is not None:
            return openai_narrative_backend(prompt, client=client, model=args.model, system_prompt=system_prompt)
        return mock_narrative_backend(prompt)

    artifact_facts: dict[str, dict[str, Any]] = {}
    generated_reports: list[str] = []
    reports_written = 0
    reports_skipped = 0

    for artifact_id, entry in ARTIFACT_NARRATIVE_REGISTRY.items():
        fact_sheet = build_fact_sheet(
            artifact_id,
            entry,
            analysis_dir=analysis_dir,
            statistical_manifest=statistical_manifest,
            figure_manifest=figure_manifest,
            correlation_rows=correlation_rows,
            hypothesis_rows=hypothesis_rows,
        )
        artifact_facts[artifact_id] = fact_sheet
        report_path = output_dir / f"{artifact_id}.md"
        generated_reports.append(_relative_path_label(report_path))
        if selected is not None and artifact_id not in selected:
            continue
        sources = _artifact_source_paths(
            entry,
            analysis_dir=analysis_dir,
            figure_manifest_path=figure_manifest_path,
            statistical_manifest_path=statistical_manifest_path,
        )
        options = {
            "prompt_version": ARTIFACT_REPORT_PROMPT_VERSION,
            "backend": args.backend,
            "model": args.model,
            "fact_sheet": fact_sheet,
        }
        checksum = input_checksum(sources, options)
        if args.force:
            invalidate_stale_artifact(report_path, "force-regeneration")
        if is_current_artifact(report_path, checksum):
            logger.info("Artifact report is current, skipping LLM call: %s", report_path)
            reports_skipped += 1
            continue
        prompt = ARTIFACT_REPORT_PROMPT.format(fact_sheet_json=json.dumps(fact_sheet, sort_keys=True, default=str))
        content = call_backend(prompt, ARTIFACT_REPORT_SYSTEM_PROMPT)
        _write_report(report_path, content, source_checksum=checksum, options=options)
        reports_written += 1
        logger.info("Generated artifact report: %s", report_path)

    for act_number in sorted(NARRATIVE_ACT_REGISTRY):
        slug = NARRATIVE_ACT_REGISTRY[act_number]["slug"]
        report_id = f"act_{act_number}_{slug}"
        payload = build_act_payload(act_number, artifact_facts)
        report_path = output_dir / f"{report_id}.md"
        generated_reports.append(_relative_path_label(report_path))
        if selected is not None and report_id not in selected:
            continue
        options = {
            "prompt_version": ACT_SYNTHESIS_PROMPT_VERSION,
            "backend": args.backend,
            "model": args.model,
            "payload": payload,
        }
        sources = [
            Path(__file__).with_name("pipeline_prompts.py"),
            analysis_dir / "correlation_results.csv",
            _sidecar_path(analysis_dir / "correlation_results.csv"),
            analysis_dir / "hypothesis_results.csv",
            _sidecar_path(analysis_dir / "hypothesis_results.csv"),
        ]
        checksum = input_checksum(sources, options)
        if args.force:
            invalidate_stale_artifact(report_path, "force-regeneration")
        if is_current_artifact(report_path, checksum):
            logger.info("Act report is current, skipping LLM call: %s", report_path)
            reports_skipped += 1
            continue
        prompt = ACT_SYNTHESIS_PROMPT.format(
            act_number=act_number,
            act_title=payload["act_title"],
            payload_json=json.dumps(payload, sort_keys=True, default=str),
        )
        content = call_backend(prompt, ACT_SYNTHESIS_SYSTEM_PROMPT)
        _write_report(report_path, content, source_checksum=checksum, options=options)
        reports_written += 1
        logger.info("Generated act report: %s", report_path)

    verdict_info = compute_consolidated_verdict(correlation_rows, hypothesis_rows, team_semester_n)
    evidence_rows: list[dict[str, Any]] = []
    for analysis_id, row in correlation_rows.items():
        evidence_rows.append(
            {
                "analysis_id": analysis_id,
                "unit_of_analysis": row.get("unit_of_analysis"),
                "n_valid": row.get("n_valid"),
                "coefficient_or_statistic": row.get("coefficient"),
                "p_value": row.get("p_value"),
                "status": row.get("status"),
            }
        )
    for analysis_id, row in hypothesis_rows.items():
        evidence_rows.append(
            {
                "analysis_id": analysis_id,
                "unit_of_analysis": row.get("unit_of_analysis"),
                "n_valid": row.get("n_valid"),
                "coefficient_or_statistic": row.get("u_statistic"),
                "p_value": row.get("p_value"),
                "status": row.get("status"),
            }
        )
    consolidated_payload = {
        "report_index": sorted(generated_reports),
        "evidence_rows": evidence_rows,
        **verdict_info,
        "remediation_options": [] if verdict_info["verdict"] == "go" else list(REMEDIATION_OPTIONS),
    }
    report_id = "00_consolidated_audit"
    report_path = output_dir / f"{report_id}.md"
    if selected is None or report_id in selected:
        options = {
            "prompt_version": AUDIT_VERDICT_PROMPT_VERSION,
            "backend": args.backend,
            "model": args.model,
            "payload": consolidated_payload,
        }
        sources = [
            Path(__file__).with_name("pipeline_prompts.py"),
            analysis_dir / "correlation_results.csv",
            _sidecar_path(analysis_dir / "correlation_results.csv"),
            analysis_dir / "hypothesis_results.csv",
            _sidecar_path(analysis_dir / "hypothesis_results.csv"),
            team_metrics_path,
            _sidecar_path(team_metrics_path),
        ]
        checksum = input_checksum(sources, options)
        if args.force:
            invalidate_stale_artifact(report_path, "force-regeneration")
        if is_current_artifact(report_path, checksum):
            logger.info("Consolidated audit report is current, skipping LLM call: %s", report_path)
            reports_skipped += 1
        else:
            prompt = AUDIT_VERDICT_PROMPT.format(payload_json=json.dumps(consolidated_payload, sort_keys=True, default=str))
            content = call_backend(prompt, AUDIT_VERDICT_SYSTEM_PROMPT)
            _write_report(report_path, content, source_checksum=checksum, options=options)
            reports_written += 1
            logger.info("Generated consolidated audit report: %s", report_path)

    print(
        f"Narrative audit: written={reports_written} skipped={reports_skipped} "
        f"verdict={verdict_info['verdict']} reason={verdict_info['verdict_reason']}"
    )


if __name__ == "__main__":
    main()
