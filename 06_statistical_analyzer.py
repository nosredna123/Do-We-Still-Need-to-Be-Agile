"""Declared, non-causal statistical analyses and manifest preparation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
from scipy import stats as scipy_stats
from scipy.stats import spearmanr

from pipeline_config import HYPOTHESIS_TEST_REGISTRY, STATISTICAL_ANALYSIS_REGISTRY
from pipeline_core import (
    ANALYSIS_DIR,
    artifact_metadata_path,
    input_checksum,
    is_current_artifact,
    write_artifact_metadata,
)


MANIFEST_VERSION = "phase2-statistics-v2"
MANIFEST_CONTRACT_VERSION = "statistical-dataset-manifest-v1"
SUMMARY_VERSION = "distribution-summary-v1"
STATISTICAL_OPTIONS = {
    "statistical_summary_version": SUMMARY_VERSION,
    "std_ddof": 1,
    "quantile_method": "linear",
    "ordinal_scale_treatment": "ordinal_with_interval_summary",
}
DATASET_SPECS: dict[str, dict[str, Any]] = {
    "team_metrics": {
        "unit_of_analysis": "team_semester",
        "key": ["ID_Equipe", "Semestre"],
        "path_name": "team_metrics.parquet",
    },
    "cut_context_metrics": {
        "unit_of_analysis": "cut_context",
        "key": ["Semestre", "temporal_marker"],
        "path_name": "cut_context_metrics.parquet",
    },
    "student_nlp": {
        "unit_of_analysis": "student_response",
        "key": ["student_response_id", "question_id"],
        "path_name": "student_nlp.parquet",
    },
    "transcript_nlp": {
        "unit_of_analysis": "transcript_session",
        "key": ["transcript_file"],
        "path_name": "transcript_nlp.parquet",
    },
}
MIN_CORRELATION_N = 3
CORRELATION_CONTRACT_VERSION = "spearman-correlation-results-v1"
HYPOTHESIS_CONTRACT_VERSION = "mann-whitney-hypothesis-results-v1"
MIN_HYPOTHESIS_GROUP_N = 3


def run_declared_correlations(frame: pd.DataFrame, registry: list[dict[str, Any]]) -> pd.DataFrame:
    """Run only explicitly registered Spearman correlations."""
    rows: list[dict[str, Any]] = []
    for analysis in registry:
        x_name = analysis["x"]
        y_name = analysis["y"]
        missing = {name for name in (x_name, y_name) if name not in frame.columns}
        if missing:
            raise ValueError(f"Correlation {analysis['analysis_id']} has missing columns: {sorted(missing)}")
        values = frame[[x_name, y_name]].dropna()
        row = {"analysis_id": analysis["analysis_id"], "unit_of_analysis": analysis["unit_of_analysis"], "x": x_name, "y": y_name, "n": int(len(values))}
        if len(values) < 3:
            row.update({"status": "unavailable", "reason": "insufficient_n", "coefficient": None, "p_value": None})
        elif values[x_name].nunique() < 2 or values[y_name].nunique() < 2:
            row.update({"status": "unavailable", "reason": "zero_variance", "coefficient": None, "p_value": None})
        else:
            coefficient, p_value = spearmanr(values[x_name], values[y_name])
            row.update({"status": "success", "reason": None, "coefficient": float(coefficient), "p_value": float(p_value)})
        rows.append(row)
    return pd.DataFrame(rows)


def _run_one_correlation(frame: pd.DataFrame, analysis_id: str, analysis: dict[str, Any]) -> dict[str, Any]:
    """Calculate one declared Spearman pair and preserve availability counts."""
    x_name = analysis["x"]
    y_name = analysis["y"]
    pair = frame[[x_name, y_name]]
    valid = pair.notna().all(axis=1)
    values = pair.loc[valid]
    n_total = int(len(pair))
    n_valid = int(len(values))
    n_missing = n_total - n_valid
    missing_x = int(pair[x_name].isna().sum())
    missing_y = int(pair[y_name].isna().sum())
    row: dict[str, Any] = {
        "analysis_id": analysis_id,
        "unit_of_analysis": analysis["unit_of_analysis"],
        "x": x_name,
        "y": y_name,
        "test": analysis.get("test"),
        "priority": analysis.get("priority"),
        "figure": analysis.get("figure"),
        "n_total": n_total,
        "n_valid": n_valid,
        "n_missing": n_missing,
        "x_missing": missing_x,
        "y_missing": missing_y,
        "coefficient": None,
        "p_value": None,
        "confidence_interval": None,
        "confidence_interval_method": "not_calculated_v1",
        "status": "unavailable",
        "reason": None,
        "warning": None,
    }
    if n_valid < MIN_CORRELATION_N:
        row["reason"] = "insufficient_n"
        return row
    if values[x_name].nunique() < 2 or values[y_name].nunique() < 2:
        row["reason"] = "zero_variance"
        return row
    coefficient, p_value = spearmanr(values[x_name], values[y_name])
    row.update({
        "coefficient": float(coefficient),
        "p_value": float(p_value),
        "status": "success",
        "warning": "small_sample_n_lt_10" if n_valid < 10 else None,
    })
    return row


def run_persisted_correlations(
    analysis_dir: Path = ANALYSIS_DIR,
    *,
    output_path: Path | None = None,
    manifest_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Run declared Spearman analyses against persisted, unit-compatible data.

    Primary analyses fail fast when their exact columns or declared unit are
    unavailable. Missing values are handled pairwise and reported explicitly.
    """
    output_path = output_path or analysis_dir / "correlation_results.csv"
    manifest_path = manifest_path or analysis_dir / "statistical_dataset_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Statistical manifest not found: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid statistical manifest") from error
    if manifest.get("status") != "success":
        raise ValueError("Statistical manifest is not successful")
    if not manifest.get("input_checksum"):
        raise ValueError("Statistical manifest lacks input checksum")

    frames: dict[str, pd.DataFrame] = {}
    for name in ("team_metrics", "cut_context_metrics"):
        path = analysis_dir / DATASET_SPECS[name]["path_name"]
        frames[name], _ = _read_persisted_dataset(name, path)
    unit_frames = {
        "team_semester": frames["team_metrics"],
        "cut_context": frames["cut_context_metrics"],
    }
    result_inputs = [
        frames_path
        for name in ("team_metrics", "cut_context_metrics")
        for frames_path in (
            analysis_dir / DATASET_SPECS[name]["path_name"],
            artifact_metadata_path(analysis_dir / DATASET_SPECS[name]["path_name"]),
        )
    ]
    result_checksum = input_checksum(
        result_inputs,
        {
            "contract_version": CORRELATION_CONTRACT_VERSION,
            "registry": STATISTICAL_ANALYSIS_REGISTRY,
            "manifest_input_checksum": manifest["input_checksum"],
        },
    )
    if not force and is_current_artifact(output_path, result_checksum):
        return pd.read_csv(output_path)

    rows: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for analysis_id, analysis in STATISTICAL_ANALYSIS_REGISTRY.items():
        unit = analysis.get("unit_of_analysis")
        frame = unit_frames.get(unit)
        missing = [column for column in (analysis["x"], analysis["y"]) if frame is None or column not in frame.columns]
        if frame is None or missing:
            rejection = {
                "analysis_id": analysis_id,
                "unit_of_analysis": unit,
                "x": analysis["x"],
                "y": analysis["y"],
                "status": "rejected",
                "reason": "missing_unit_or_columns",
                "missing_columns": missing,
            }
            if analysis.get("priority") == "primary":
                raise ValueError(f"Primary correlation {analysis_id} has missing unit or columns: {missing}")
            rejected.append(rejection)
            continue
        rows.append(_run_one_correlation(frame, analysis_id, analysis))

    results = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    write_artifact_metadata(
        output_path,
        result_checksum,
        contract_version=CORRELATION_CONTRACT_VERSION,
        options={"registry": STATISTICAL_ANALYSIS_REGISTRY, "confidence_interval": "not_calculated_v1"},
    )
    manifest["correlations"] = {
        "status": "success",
        "contract_version": CORRELATION_CONTRACT_VERSION,
        "results_path": output_path.as_posix(),
        "results_input_checksum": result_checksum,
        "executed": results.to_dict("records"),
        "rejected": rejected,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return results


def _run_one_hypothesis(
    frame: pd.DataFrame,
    analysis_id: str,
    analysis: dict[str, Any],
) -> dict[str, Any]:
    """Run one median-split Mann-Whitney test with explicit diagnostics."""
    group_variable = analysis["group_variable"]
    outcome_variable = analysis["outcome_variable"]
    pair = frame[[group_variable, outcome_variable]].dropna()
    n_total = int(len(frame))
    n_valid = int(len(pair))
    n_missing = n_total - n_valid
    median = float(pair[group_variable].median()) if not pair.empty else None
    group_low = pair.loc[pair[group_variable] <= median, outcome_variable] if median is not None else pd.Series(dtype=float)
    group_high = pair.loc[pair[group_variable] > median, outcome_variable] if median is not None else pd.Series(dtype=float)
    result: dict[str, Any] = {
        "analysis_id": analysis_id,
        "unit_of_analysis": analysis["unit_of_analysis"],
        "test": analysis["test"],
        "priority": analysis.get("priority"),
        "group_variable": group_variable,
        "outcome_variable": outcome_variable,
        "split_rule": analysis["split_rule"],
        "split_median": median,
        "n_total": n_total,
        "n_valid": n_valid,
        "n_missing": n_missing,
        "n_group_low": int(len(group_low)),
        "n_group_high": int(len(group_high)),
        "u_statistic": None,
        "p_value": None,
        "multiple_testing_correction": "none_v1",
        "status": "unavailable",
        "reason": None,
        "interpretation": "exploratory_observational",
    }
    if len(group_low) < MIN_HYPOTHESIS_GROUP_N or len(group_high) < MIN_HYPOTHESIS_GROUP_N:
        result["reason"] = "insufficient_group_n"
        return result
    if group_low.nunique() < 2 or group_high.nunique() < 2:
        result["reason"] = "zero_variance"
        return result
    statistic, p_value = scipy_stats.mannwhitneyu(group_low, group_high, alternative="two-sided")
    result.update({
        "u_statistic": float(statistic),
        "p_value": float(p_value),
        "status": "success",
    })
    return result


def run_persisted_hypotheses(
    analysis_dir: Path = ANALYSIS_DIR,
    *,
    output_path: Path | None = None,
    manifest_path: Path | None = None,
    force: bool = False,
) -> pd.DataFrame:
    """Run declared Mann-Whitney tests on persisted, unit-compatible data."""
    output_path = output_path or analysis_dir / "hypothesis_results.csv"
    manifest_path = manifest_path or analysis_dir / "statistical_dataset_manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Statistical manifest not found: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid statistical manifest") from error
    if manifest.get("status") != "success":
        raise ValueError("Statistical manifest is not successful")
    if not manifest.get("input_checksum"):
        raise ValueError("Statistical manifest lacks input checksum")

    frames: dict[str, pd.DataFrame] = {}
    for name in ("team_metrics", "cut_context_metrics"):
        path = analysis_dir / DATASET_SPECS[name]["path_name"]
        frames[name], _ = _read_persisted_dataset(name, path)
    unit_frames = {
        "team_semester": frames["team_metrics"],
        "cut_context": frames["cut_context_metrics"],
    }
    result_inputs = [
        path
        for name in ("team_metrics", "cut_context_metrics")
        for path in (
            analysis_dir / DATASET_SPECS[name]["path_name"],
            artifact_metadata_path(analysis_dir / DATASET_SPECS[name]["path_name"]),
        )
    ]
    result_checksum = input_checksum(
        result_inputs,
        {
            "contract_version": HYPOTHESIS_CONTRACT_VERSION,
            "registry": HYPOTHESIS_TEST_REGISTRY,
            "manifest_input_checksum": manifest["input_checksum"],
            "minimum_group_n": MIN_HYPOTHESIS_GROUP_N,
        },
    )
    if not force and is_current_artifact(output_path, result_checksum):
        return pd.read_csv(output_path)

    rows: list[dict[str, Any]] = []
    for analysis_id, analysis in HYPOTHESIS_TEST_REGISTRY.items():
        frame = unit_frames.get(analysis.get("unit_of_analysis"))
        missing = [
            column
            for column in (analysis["group_variable"], analysis["outcome_variable"])
            if frame is None or column not in frame.columns
        ]
        if frame is None or missing:
            if analysis.get("priority") == "primary":
                raise ValueError(f"Primary hypothesis {analysis_id} has missing unit or columns: {missing}")
            rows.append({
                "analysis_id": analysis_id,
                "unit_of_analysis": analysis.get("unit_of_analysis"),
                "group_variable": analysis["group_variable"],
                "outcome_variable": analysis["outcome_variable"],
                "status": "unavailable",
                "reason": "missing_unit_or_columns",
            })
            continue
        rows.append(_run_one_hypothesis(frame, analysis_id, analysis))

    results = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    write_artifact_metadata(
        output_path,
        result_checksum,
        contract_version=HYPOTHESIS_CONTRACT_VERSION,
        options={
            "registry": HYPOTHESIS_TEST_REGISTRY,
            "minimum_group_n": MIN_HYPOTHESIS_GROUP_N,
            "multiple_testing_correction": "none_v1",
        },
    )
    manifest["hypotheses"] = {
        "status": "success",
        "contract_version": HYPOTHESIS_CONTRACT_VERSION,
        "results_path": output_path.as_posix(),
        "results_input_checksum": result_checksum,
        "executed": results.to_dict("records"),
        "registry": HYPOTHESIS_TEST_REGISTRY,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return results


def _key_hash(key: dict[str, Any]) -> str:
    """Return a privacy-safe stable hash for an observation key."""
    encoded = json.dumps(key, sort_keys=True, default=str, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_persisted_dataset(
    name: str,
    path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Read one persisted input and enforce its sidecar contract."""
    spec = DATASET_SPECS[name]
    metadata_path = artifact_metadata_path(path)
    if not path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError(f"Missing statistical input or sidecar: {path}")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Invalid statistical input sidecar: {metadata_path}") from error
    if metadata.get("status") != "success":
        raise ValueError(f"Statistical input sidecar is not successful: {path.name}")
    if not metadata.get("input_checksum"):
        raise ValueError(f"Statistical input sidecar lacks checksum: {path.name}")
    if not metadata.get("contract_version"):
        raise ValueError(f"Statistical input sidecar lacks contract version: {path.name}")

    frame = pd.read_parquet(path)
    missing = (set(spec["key"]) | {"unit_of_analysis"}) - set(frame.columns)
    if missing:
        raise ValueError(f"{path.name} missing manifest columns: {sorted(missing)}")
    expected_unit = spec["unit_of_analysis"]
    units = frame["unit_of_analysis"].dropna().unique().tolist()
    if units != [expected_unit]:
        raise ValueError(f"{path.name} has invalid unit_of_analysis: {units}")
    if frame[list(spec["key"])].isna().any().any():
        raise ValueError(f"{path.name} has null observation keys")
    if frame.duplicated(spec["key"]).any():
        raise ValueError(f"{path.name} has duplicate observation keys")
    if name == "team_metrics" and any(str(column).startswith("ie_") for column in frame.columns):
        raise ValueError("team_metrics must not contain replicated IE variables")
    return frame, metadata


def _variable_catalog(frame: pd.DataFrame, key: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build a non-text catalog and aggregate missingness exclusions."""
    variables: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    for column in sorted(str(value) for value in frame.columns):
        series = frame[column]
        n_total = int(len(series))
        n_missing = int(series.isna().sum())
        n_valid = n_total - n_missing
        entry: dict[str, Any] = {
            "name": column,
            "dtype": str(series.dtype),
            "n_total": n_total,
            "n_valid": n_valid,
            "n_missing": n_missing,
            "numeric": bool(pd.api.types.is_numeric_dtype(series)),
        }
        variables.append(entry)
        if n_missing:
            excluded = frame.loc[series.isna(), key]
            exclusions.append({
                "variable": column,
                "reason": "missing_value",
                "n_excluded": int(len(excluded)),
                "example_key_hashes": [_key_hash(dict(row)) for row in excluded.head(5).to_dict("records")],
            })
    return variables, exclusions


def _private_exclusion_catalog(
    dataset: str,
    frame: pd.DataFrame,
    key: list[str],
) -> list[dict[str, Any]]:
    """Return detailed exclusions with true keys for the private report only."""
    rows: list[dict[str, Any]] = []
    for column in sorted(str(value) for value in frame.columns):
        excluded = frame.loc[frame[column].isna(), key]
        if excluded.empty:
            continue
        rows.append({
            "dataset": dataset,
            "unit_of_analysis": DATASET_SPECS[dataset]["unit_of_analysis"],
            "variable": column,
            "reason": "missing_value",
            "n_excluded": int(len(excluded)),
            "observation_keys": excluded.to_dict("records"),
        })
    return rows


def _definition_versions(metadata_by_dataset: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Collect persisted metric definition versions without inferring them."""
    versions: dict[str, Any] = {}

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key.endswith("_definition_version") or key == "statistical_summary_version":
                    versions[key.removesuffix("_definition_version")] = child
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for metadata in metadata_by_dataset.values():
        visit(metadata.get("options", {}))
    required = {"pi", "cc", "dt", "ai", "ie"}
    missing = required - set(versions)
    if missing:
        raise ValueError(f"Missing persisted metric definition versions: {sorted(missing)}")
    return versions


def _declared_analysis_catalog(frames: dict[str, pd.DataFrame]) -> list[dict[str, Any]]:
    """Describe every registered test without executing statistical inference."""
    by_unit = {spec["unit_of_analysis"]: frame for name, frame in frames.items() for spec in [DATASET_SPECS[name]]}
    rows: list[dict[str, Any]] = []
    for analysis_id, analysis in STATISTICAL_ANALYSIS_REGISTRY.items():
        unit = analysis["unit_of_analysis"]
        frame = by_unit.get(unit)
        x_name = analysis["x"]
        y_name = analysis["y"]
        missing = [column for column in (x_name, y_name) if frame is None or column not in frame.columns]
        if frame is None or missing:
            rows.append({
                "analysis_id": analysis_id,
                "unit_of_analysis": unit,
                "x": x_name,
                "y": y_name,
                "status": "unavailable",
                "reason": "missing_unit_or_columns",
                "missing_columns": missing,
                "n_total": 0,
                "n_valid": 0,
                "n_missing": 0,
            })
            continue
        pair = frame[[x_name, y_name]]
        valid = pair.notna().all(axis=1)
        rows.append({
            "analysis_id": analysis_id,
            "unit_of_analysis": unit,
            "x": x_name,
            "y": y_name,
            "status": "available",
            "reason": None,
            "missing_columns": [],
            "n_total": int(len(pair)),
            "n_valid": int(valid.sum()),
            "n_missing": int((~valid).sum()),
        })
    return rows


def build_statistical_manifest(
    team_metrics: pd.DataFrame,
    context_metrics: pd.DataFrame,
    student_nlp: pd.DataFrame | None = None,
    transcript_nlp: pd.DataFrame | None = None,
    *,
    metadata_by_dataset: dict[str, dict[str, Any]] | None = None,
    input_artifacts: dict[str, dict[str, Any]] | None = None,
    source_checksum: str | None = None,
    exclusions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Describe persisted statistical inputs without including raw text.

    Args:
        team_metrics: Team-semester metrics loaded from disk.
        context_metrics: Cut-context metrics loaded from disk.
        student_nlp: Optional persisted student-response NLP output.
        transcript_nlp: Optional persisted transcript-session NLP output.
        metadata_by_dataset: Validated sidecars keyed by dataset name.
        input_artifacts: Checksums, paths, and contracts for lineage.
        source_checksum: Aggregate checksum of all manifest inputs.
        exclusions: Additional privacy-safe exclusion records.
    """
    frames = {
        "team_metrics": team_metrics,
        "cut_context_metrics": context_metrics,
    }
    if student_nlp is not None:
        frames["student_nlp"] = student_nlp
    if transcript_nlp is not None:
        frames["transcript_nlp"] = transcript_nlp

    datasets: dict[str, Any] = {}
    exclusion_rows = list(exclusions or [])
    for name, frame in frames.items():
        spec = DATASET_SPECS[name]
        variables, missing_rows = _variable_catalog(frame, spec["key"])
        exclusion_rows.extend({"dataset": name, "unit_of_analysis": spec["unit_of_analysis"], **row} for row in missing_rows)
        coverage: dict[str, list[str]] = {}
        for field in ("Semestre", "temporal_marker"):
            if field in frame.columns:
                coverage[field] = sorted(str(value) for value in frame[field].dropna().unique())
        datasets[name] = {
            "unit_of_analysis": spec["unit_of_analysis"],
            "observation_key": spec["key"],
            "n_rows": int(len(frame)),
            "n_unique_keys": int(frame[spec["key"]].drop_duplicates().shape[0]),
            "coverage": coverage,
            "variables": variables,
        }

    manifest: dict[str, Any] = {
        "status": "success",
        "manifest_version": MANIFEST_VERSION,
        "contract_version": MANIFEST_CONTRACT_VERSION,
        "input_checksum": source_checksum,
        "datasets": datasets,
        "declared_analyses": _declared_analysis_catalog(frames),
        "input_artifacts": input_artifacts or {},
        "metric_definition_versions": _definition_versions(metadata_by_dataset or {}) if metadata_by_dataset else {},
        "statistical_protocol": STATISTICAL_OPTIONS.copy(),
        "unit_compatibility": {
            "team_semester": {"direct_correlation_with": ["team_semester"], "broadcast_allowed": False},
            "cut_context": {"direct_correlation_with": ["cut_context"], "broadcast_allowed": False},
            "student_response": {"aggregation_target": "cut_context", "broadcast_allowed": False},
            "transcript_session": {"aggregation_target": "cut_context", "broadcast_allowed": False},
        },
        "pii_status": {
            "raw_text_in_manifest": False,
            "text_fields": "excluded",
            "source_artifacts_private": ["student_nlp", "transcript_nlp"],
        },
        "exclusions": exclusion_rows,
    }
    return manifest


def prepare_statistical_manifest(
    input_paths: dict[str, Path],
    contract_report_path: Path,
    output_path: Path,
    exclusions_path: Path,
    *,
    options: dict[str, Any] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Validate persisted inputs and write the resumable statistical manifest."""
    options = {**STATISTICAL_OPTIONS, **(options or {})}
    required_names = set(DATASET_SPECS)
    if set(input_paths) != required_names:
        raise ValueError(f"Manifest inputs must be exactly: {sorted(required_names)}")
    if not contract_report_path.is_file():
        raise FileNotFoundError(f"Contract report not found: {contract_report_path}")
    try:
        contract_report = json.loads(contract_report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Invalid Phase 2 contract report") from error
    if contract_report.get("status") != "success":
        raise ValueError("Phase 2 contract report is not successful")

    frames: dict[str, pd.DataFrame] = {}
    metadata: dict[str, dict[str, Any]] = {}
    for name, path in input_paths.items():
        frames[name], metadata[name] = _read_persisted_dataset(name, path)

    checksum_paths = [path for name in sorted(input_paths) for path in (input_paths[name], artifact_metadata_path(input_paths[name]))]
    checksum_paths.append(contract_report_path)
    source_checksum = input_checksum(checksum_paths, options)
    input_artifacts = {
        name: {
            "path": path.as_posix(),
            "checksum": metadata[name]["input_checksum"],
            "contract_version": metadata[name]["contract_version"],
            "unit_of_analysis": DATASET_SPECS[name]["unit_of_analysis"],
            "n_rows": int(len(frames[name])),
        }
        for name, path in input_paths.items()
    }
    if not force and output_path.is_file() and exclusions_path.is_file():
        try:
            current = json.loads(output_path.read_text(encoding="utf-8"))
            if current.get("status") == "success" and current.get("input_checksum") == source_checksum:
                return current
        except (OSError, UnicodeError, json.JSONDecodeError):
            pass
    manifest = build_statistical_manifest(
        frames["team_metrics"],
        frames["cut_context_metrics"],
        frames["student_nlp"],
        frames["transcript_nlp"],
        metadata_by_dataset=metadata,
        input_artifacts=input_artifacts,
        source_checksum=source_checksum,
    )
    private_key_exclusions = [
        exclusion
        for name, frame in frames.items()
        for exclusion in _private_exclusion_catalog(name, frame, DATASET_SPECS[name]["key"])
    ]
    private_exclusions = {
        "status": "success",
        "contract_version": "statistical-dataset-manifest-exclusions-v1",
        "input_checksum": source_checksum,
        "unit_policy": "true_observation_keys_are_private",
        "exclusions": private_key_exclusions,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    exclusions_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str), encoding="utf-8")
    exclusions_path.write_text(json.dumps(private_exclusions, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return manifest


def main() -> None:
    """Build the persisted statistical dataset manifest from Phase 2 outputs."""
    parser = argparse.ArgumentParser(description="Prepare the Phase 2 statistical dataset manifest")
    parser.add_argument("--analysis-dir", type=Path, default=ANALYSIS_DIR)
    parser.add_argument("--contract-report", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    analysis_dir = args.analysis_dir
    input_paths = {name: analysis_dir / spec["path_name"] for name, spec in DATASET_SPECS.items()}
    contract_report = args.contract_report or analysis_dir / "phase2_contract_report.json"
    manifest = prepare_statistical_manifest(
        input_paths,
        contract_report,
        analysis_dir / "statistical_dataset_manifest.json",
        analysis_dir / "statistical_dataset_manifest_exclusions.json",
        options={"statistical_analysis_registry": STATISTICAL_ANALYSIS_REGISTRY},
        force=args.force,
    )
    results = run_persisted_correlations(
        analysis_dir,
        output_path=analysis_dir / "correlation_results.csv",
        manifest_path=analysis_dir / "statistical_dataset_manifest.json",
        force=args.force,
    )
    hypotheses = run_persisted_hypotheses(
        analysis_dir,
        output_path=analysis_dir / "hypothesis_results.csv",
        manifest_path=analysis_dir / "statistical_dataset_manifest.json",
        force=args.force,
    )
    print(
        f"Statistical manifest: {manifest['status']} ({len(manifest['datasets'])} datasets); "
        f"correlations: {len(results)}; hypotheses: {len(hypotheses)}"
    )


if __name__ == "__main__":
    main()