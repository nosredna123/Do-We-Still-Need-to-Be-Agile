"""Privacy-safety audit for persisted Phase 2 analytical artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


RAW_TEXT_FIELDS = {"answer_text", "transcript_text", "evidence_summary_private"}
PRIVATE_DATASETS = {"student_nlp.parquet", "transcript_nlp.parquet"}
PRIVATE_PATH_PARTS = {".private"}


def _json_violations(value: Any, path: str = "") -> list[str]:
    violations: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            schema_metadata = any(part in path for part in ("/dtypes", "/null_counts", "/columns", "/schema"))
            if key in RAW_TEXT_FIELDS and child not in (None, "", [], {}) and not schema_metadata:
                violations.append(f"non-empty sensitive field: {path}/{key}")
            violations.extend(_json_violations(child, f"{path}/{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            violations.extend(_json_violations(child, f"{path}/{index}"))
    return violations


def audit_phase2_privacy(analysis_dir: Path) -> dict[str, Any]:
    """Audit reports, manifests, public metrics, and figure data for raw text."""
    violations: list[str] = []
    checked_json = 0
    checked_tables = 0

    for path in sorted(analysis_dir.glob("*.json")):
        if path.name == "privacy_audit_report.json":
            continue
        checked_json += 1
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            violations.append(f"invalid JSON: {path}: {error}")
            continue
        violations.extend(f"{path}: {item}" for item in _json_violations(payload))

    for path in sorted(analysis_dir.rglob("*.parquet")):
        checked_tables += 1
        frame = pd.read_parquet(path)
        is_private = path.name in PRIVATE_DATASETS or any(part in path.parts for part in PRIVATE_PATH_PARTS)
        if not is_private:
            leaked = RAW_TEXT_FIELDS.intersection(frame.columns)
            violations.extend(f"raw text column in public table: {path}:{column}" for column in sorted(leaked))
        if path.name == "team_metrics.parquet":
            violations.extend(
                f"IE column replicated in team metrics: {column}"
                for column in frame.columns
                if str(column).startswith("ie_")
            )

    for path in sorted((analysis_dir / "figure_data").rglob("*.csv")):
        checked_tables += 1
        frame = pd.read_csv(path)
        leaked = RAW_TEXT_FIELDS.intersection(frame.columns)
        violations.extend(f"raw text column in figure data: {path}:{column}" for column in sorted(leaked))

    report = {
        "status": "success" if not violations else "failed",
        "contract_version": "phase2-privacy-audit-v1",
        "analysis_dir": analysis_dir.as_posix(),
        "checked_json_reports": checked_json,
        "checked_tables": checked_tables,
        "raw_text_fields_checked": sorted(RAW_TEXT_FIELDS),
        "private_datasets": sorted(PRIVATE_DATASETS),
        "violations": violations,
        "publication_note": "This structural audit does not replace semantic PII review before publication.",
    }
    return report


def main() -> None:
    """Run and persist the Phase 2 privacy audit."""
    parser = argparse.ArgumentParser(description="Audit Phase 2 analytical artifacts for raw text")
    parser.add_argument("--analysis-dir", type=Path, default=Path("data/analysis"))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    output = args.output or args.analysis_dir / "privacy_audit_report.json"
    report = audit_phase2_privacy(args.analysis_dir)
    output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Privacy audit: {report['status']} ({len(report['violations'])} violations)")
    if report["status"] != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
