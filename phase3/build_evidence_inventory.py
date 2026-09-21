"""Build a compact, reproducible inventory for Phase 3 paper support.

This script reads persisted Phase 2 and cross-evidence artifacts only. It does
not rerun or mutate any Phase 2 stage and writes one report under
``data/analysis/paper_support``.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "analysis" / "paper_support" / "phase3_evidence_inventory.md"
KEYWORDS = (
    "verdict",
    "support",
    "inconclusive",
    "unavailable",
    "limitation",
    "status",
    "p-value",
    "p_value",
    "n=",
    "n =",
)
FIGURE_SUFFIXES = {".html", ".json", ".pdf", ".png", ".svg", ".jpg", ".jpeg"}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def all_files(path: Path, suffixes: set[str] | None = None) -> list[Path]:
    if not path.exists():
        return []
    files = sorted(item for item in path.rglob("*") if item.is_file())
    return [item for item in files if suffixes is None or item.suffix.lower() in suffixes]


def extension_counts(paths: list[Path]) -> str:
    counts = Counter(path.suffix.lower() or "[no extension]" for path in paths)
    return ", ".join(f"{suffix}: {count}" for suffix, count in sorted(counts.items()))


def markdown_summary(path: Path) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    headings = [line.strip() for line in lines if line.startswith("#")]
    hits = [
        line.strip()
        for line in lines
        if any(keyword.lower() in line.lower() for keyword in KEYWORDS)
    ]
    return {"path": rel(path), "lines": len(lines), "headings": headings, "hits": hits[:8]}


def read_csv_summary(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    distributions: dict[str, dict[str, int]] = {}
    for key in ("status", "verdict", "priority", "reason"):
        if rows and key in rows[0]:
            distributions[key] = dict(Counter(row.get(key) or "<empty>" for row in rows))
    p_values = []
    for row in rows:
        if row.get("p_value"):
            p_values.append(
                f"{row.get('analysis_id') or row.get('contrast_id') or '<row>'}: {row['p_value']}"
            )
    return {
        "path": rel(path),
        "rows": len(rows),
        "columns": list(rows[0]) if rows else [],
        "distributions": distributions,
        "p_values": p_values,
    }


def read_json_summary(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary: dict[str, Any] = {"path": rel(path), "keys": sorted(payload) if isinstance(payload, dict) else []}
    if isinstance(payload, dict) and "artifacts" in payload:
        summary["artifact_count"] = len(payload["artifacts"])
    if isinstance(payload, dict) and "exclusions" in payload:
        summary["exclusions"] = [
            {
                "dataset": item.get("dataset"),
                "reason": item.get("reason"),
                "n_affected_events": item.get("n_affected_events"),
                "n_affected_rows": item.get("n_affected_rows"),
            }
            for item in payload["exclusions"]
            if isinstance(item, dict)
        ]
    return summary


def parquet_summary(path: Path) -> dict[str, Any]:
    try:
        import pandas as pd

        frame = pd.read_parquet(path)
        columns = list(frame.columns)
        key_columns = [
            column
            for column in columns
            if column in {"ID_Equipe", "Semestre", "temporal_marker", "unit_of_analysis"}
            or column.endswith("_id")
        ]
        return {"path": rel(path), "rows": len(frame), "columns": columns, "key_columns": key_columns}
    except Exception as error:  # pragma: no cover - preserves inventory on optional reader failure
        return {"path": rel(path), "error": f"{type(error).__name__}: {error}"}


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- `{item}`" for item in items) or "- None"


def render_report() -> str:
    artifact_reports = all_files(ROOT / "data" / "analysis" / "artifact_reports", {".md"})
    cross_reports = all_files(ROOT / "data" / "analysis" / "cross_evidence" / "reports", {".md"})
    analysis_files = all_files(ROOT / "data" / "analysis")
    cross_files = all_files(ROOT / "data" / "analysis" / "cross_evidence")
    figure_files = all_files(ROOT / "assets" / "figures", FIGURE_SUFFIXES)
    phase25_summaries = [markdown_summary(path) for path in artifact_reports]
    cross_summaries = [markdown_summary(path) for path in cross_reports]
    result_summaries = [
        read_csv_summary(path)
        for path in all_files(ROOT / "data" / "analysis" / "cross_evidence" / "results", {".csv"})
    ]
    manifest_summaries = [
        read_json_summary(path)
        for path in all_files(ROOT / "data" / "analysis" / "cross_evidence", {".json"})
        if "manifest" in path.name
    ]
    parquet_summaries = [
        parquet_summary(path)
        for path in all_files(ROOT / "data" / "analysis", {".parquet"})
    ]

    lines = [
        "# Phase 3 Evidence Inventory",
        "",
        f"Generated at `{datetime.now(timezone.utc).isoformat()}` by `phase3/build_evidence_inventory.py`.",
        "",
        "## Interpretation Policy",
        "",
        "The Phase 2.5 Markdown reports are the primary interpretive layer for Phase 3. "
        "Their artifact, act, and consolidated reports define the current narrative reading. "
        "Parquets, CSVs, JSON manifests, sidecars, and figures are used to verify, quantify, "
        "and visually support those interpretations. Cross-evidence remains secondary and "
        "exploratory; supporting, inconclusive, fragile, and methodological-warning results "
        "must remain distinguishable.",
        "",
        "## Persisted Inventory",
        "",
        f"- Analysis tree: {len(analysis_files)} files ({extension_counts(analysis_files)}).",
        f"- Cross-evidence tree: {len(cross_files)} files ({extension_counts(cross_files)}).",
        f"- Figure assets: {len(figure_files)} files ({extension_counts(figure_files)}).",
        f"- Phase 2.5 artifact reports: {len(artifact_reports)} Markdown files.",
        f"- Cross-evidence reports: {len(cross_reports)} Markdown files.",
        "",
        "## Phase 2.5 Report Layer",
        "",
        "These reports are the starting point for claim extraction. Each claim must be "
        "traced from a report to its source artifact before entering the paper.",
        "",
    ]
    for summary in phase25_summaries:
        lines.extend([f"### `{summary['path']}`", f"- Lines: {summary['lines']}"])
        if summary["headings"]:
            lines.append(f"- Headings: {' | '.join(summary['headings'][:6])}")
        for hit in summary["hits"][:5]:
            lines.append(f"- Evidence text: {hit}")
        lines.append("")

    lines.extend([
        "## Cross-Evidence Report Layer",
        "",
        "Cross-evidence is a secondary exploratory layer for Acts 2 and 3, with "
        "contextual or methodological relevance to Acts 1 and 4. It cannot override "
        "the Phase 2.5 consolidated audit. Its positive results require checks for "
        "sample size, multiple comparisons, exclusions, and leave-one-out stability.",
        "",
    ])
    for summary in cross_summaries:
        lines.extend([f"### `{summary['path']}`", f"- Lines: {summary['lines']}"])
        if summary["headings"]:
            lines.append(f"- Headings: {' | '.join(summary['headings'][:6])}")
        for hit in summary["hits"][:5]:
            lines.append(f"- Evidence text: {hit}")
        lines.append("")

    lines.extend(["## Cross-Evidence Structured Checks", ""])
    for summary in manifest_summaries:
        lines.append(f"### `{summary['path']}`")
        if "artifact_count" in summary:
            lines.append(f"- Manifest artifacts: {summary['artifact_count']}")
        if summary.get("exclusions"):
            for exclusion in summary["exclusions"]:
                lines.append(f"- Exclusion: `{exclusion}`")
        lines.append(f"- Keys: {', '.join(summary['keys'])}")
        lines.append("")
    for summary in result_summaries:
        lines.extend([f"### `{summary['path']}`", f"- Rows: {summary['rows']}"])
        for key, distribution in summary["distributions"].items():
            lines.append(f"- {key}: `{distribution}`")
        if summary["p_values"]:
            lines.append(f"- p-values: {', '.join(summary['p_values'])}")
        lines.append("")

    lines.extend(["## Parquet Verification Index", ""])
    for summary in parquet_summaries:
        if "error" in summary:
            lines.append(f"- `{summary['path']}`: reader error `{summary['error']}`")
        else:
            lines.append(
                f"- `{summary['path']}`: rows={summary['rows']}; "
                f"key columns={', '.join(summary['key_columns']) or 'not detected'}; "
                f"columns={len(summary['columns'])}."
            )
    lines.extend([
        "",
        "## Required Reconciliations for Paper Writing",
        "",
        "1. Treat the Phase 2.5 artifact, act, and consolidated reports as the authoritative "
        "interpretive index, while checking every quoted number against its persisted source.",
        "2. Keep the current Phase 2.5 boundary visible: team-semester n=14, five tested "
        "primary analyses, no significant primary result, and conditional-go.",
        "3. Treat cross-evidence supporting results as exploratory candidates, not confirmation. "
        "Record inconclusive results, fragile leave-one-out behavior, and methodological warnings "
        "next to every favorable claim.",
        "4. Do not merge team-semester, team-semester-cut, category, student-response, and "
        "transcript-session units into one denominator.",
        "5. Do not infer causality or SDD superiority from plots, correlations, contrasts, or "
        "extreme-case overlap.",
        "6. Preserve unknown-file-category exclusions and any privacy/anonymization constraints "
        "in the data book and threats-to-validity record.",
        "7. Any new derived analysis must be isolated in a separate script, documented, and "
        "explicitly authorized before execution; Phase 2 artifacts remain unchanged.",
        "",
        "## Intended Phase 3 Use",
        "",
        "This inventory feeds the data book, argument matrix, plot book, four act packages, "
        "literature map, threats-to-validity record, and IMRaD manuscript outline. It is an "
        "inventory and reconciliation aid, not a replacement for the canonical artifacts or "
        "the Phase 2.5 narrative reports.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_report(), encoding="utf-8")
    print(f"wrote {rel(OUTPUT)}")


if __name__ == "__main__":
    main()
