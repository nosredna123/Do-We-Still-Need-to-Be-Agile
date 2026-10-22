from __future__ import annotations

import json
from pathlib import Path

from paper_v9.scripts.results.build_results_summary import build_summary


def test_results_summary_resolves_all_metric_artifacts() -> None:
    summary = build_summary()
    assert summary["status"] == "success"
    assert set(summary["metrics"]) == {"M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"}
    assert all(record["bytes"] > 0 for metric in summary["metrics"].values() for record in metric["artifacts"])
    assert summary["key_summaries"]["M7"]["daily_windows"] == 994
    assert summary["key_summaries"]["M8"]["baseline_eligible_n"] == 12


def test_results_summary_file_is_valid_json() -> None:
    path = Path("paper_v9/data/results/results_summary.json")
    assert path.is_file()
    assert json.loads(path.read_text(encoding="utf-8"))["status"] == "success"