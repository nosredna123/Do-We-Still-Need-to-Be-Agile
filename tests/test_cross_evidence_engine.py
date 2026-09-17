from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_engine() -> Any:
    spec = importlib.util.spec_from_file_location(
        "cross_evidence_engine", ROOT / "08_cross_evidence_engine.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def classify(path: str | None, extension: str | None = None, old_path: str | None = None) -> dict[str, object]:
    engine = load_engine()
    return engine.classify_file_category(path, extension, file_path_old=old_path)


def git_file_row(
    path: str,
    *,
    extension: str | None = None,
    team: str = "TEAM_1",
    semester: str = "2025.2",
    cut: str = "T1",
    status: str = "added",
    old_path: str | None = None,
    added: int | None = 10,
    deleted: int | None = 2,
    binary: bool = False,
) -> dict[str, object]:
    return {
        "ID_Equipe": team,
        "Semestre": semester,
        "temporal_marker": cut,
        "file_path": path,
        "file_path_old": old_path,
        "file_extension": extension if extension is not None else Path(path).suffix.lower(),
        "change_status": status,
        "lines_added": added,
        "lines_deleted": deleted,
        "is_binary": binary,
    }


def test_classify_file_category_uses_source_extensions() -> None:
    result = classify("src/app.py", ".py")

    assert result["file_category"] == "source"
    assert result["category_rule"] == "extension:source:.py"
    assert result["category_confidence"] == 1.0
    assert result["category_warning"] is None


def test_classify_file_category_lets_generated_path_override_source_extension() -> None:
    result = classify("dist/app.js", ".js")

    assert result["file_category"] == "generated"
    assert result["category_rule"] == "path:generated:dist/"
    assert result["category_confidence"] == 0.8
    assert result["category_warning"] == "generated_path_takes_precedence"


def test_classify_file_category_uses_planning_context_for_contextual_config() -> None:
    result = classify("docs/architecture/schema.json", ".json")

    assert result["file_category"] == "planning"
    assert result["category_rule"] == "path:planning"
    assert result["category_confidence"] == 0.8
    assert result["category_warning"] == "planning_path_takes_precedence_over_config_extension"


def test_classify_file_category_keeps_non_contextual_json_as_config() -> None:
    result = classify("src/config.json", ".json")

    assert result["file_category"] == "config"
    assert result["category_rule"] == "extension:config:.json"
    assert result["category_confidence"] == 1.0


def test_classify_file_category_handles_typing_and_localization_outputs() -> None:
    assert classify("src/package/__init__.pyi", ".pyi")["file_category"] == "config"
    assert classify("src/types/index.d.ts", None)["file_category"] == "config"
    assert classify("locale/messages.po", ".po")["file_category"] == "localization"
    assert classify("locale/messages.mo", ".mo")["file_category"] == "generated"
    assert classify("__pycache__/app.cpython-311.pyc", ".pyc")["file_category"] == "generated"


def test_classify_file_category_handles_assets_tests_and_unknowns() -> None:
    assert classify("assets/logo.svg", ".svg")["file_category"] == "asset"
    assert classify("tests/test_app.py", ".py")["file_category"] == "test"
    assert classify("src/app.flow", ".flow")["file_category"] == "unknown"

    unknown = classify("Makefile", "")
    assert unknown["file_category"] == "unknown"
    assert unknown["category_rule"] == "extension:empty"
    assert unknown["category_confidence"] == 0.5
    assert unknown["category_warning"] == "classify_by_path_or_unknown"


def test_classify_file_category_infers_extension_and_falls_back_to_old_path() -> None:
    inferred = classify("src/app.ts", None)
    fallback = classify("", None, old_path="src/legacy.kt")

    assert inferred["file_category"] == "source"
    assert inferred["category_rule"] == "extension:source:.ts"
    assert fallback["file_category"] == "source"
    assert fallback["category_rule"] == "extension:source:.kt"


def test_compute_file_category_churn_metrics_aggregates_by_team_cut_and_category() -> None:
    engine = load_engine()
    frame = pd.DataFrame(
        [
            git_file_row("src/app.py", added=10, deleted=2),
            git_file_row("src/util.py", status="modified", added=4, deleted=1),
            git_file_row("docs/schema.json", added=3, deleted=1),
            git_file_row("dist/app.js", added=None, deleted=None, binary=True),
            git_file_row("locale/messages.po", cut="T2", added=7, deleted=3),
            git_file_row("src/unknown.flow", cut="T2", added=1, deleted=0),
        ]
    )

    result = engine.compute_file_category_churn_metrics(frame)
    t1_source = result.loc[
        (result["temporal_marker"] == "T1") & (result["file_category"] == "source")
    ].iloc[0]
    t1_generated = result.loc[
        (result["temporal_marker"] == "T1") & (result["file_category"] == "generated")
    ].iloc[0]
    t2_unknown = result.loc[
        (result["temporal_marker"] == "T2") & (result["file_category"] == "unknown")
    ].iloc[0]

    assert t1_source["event_n"] == 2
    assert t1_source["added_event_n"] == 1
    assert t1_source["modified_event_n"] == 1
    assert t1_source["lines_added"] == 14
    assert t1_source["lines_deleted"] == 3
    assert t1_source["churn_lines"] == 17
    assert t1_source["total_event_n"] == 4
    assert t1_source["category_event_share"] == 0.5
    assert t1_generated["binary_event_n"] == 1
    assert t1_generated["line_count_missing_event_n"] == 1
    assert t1_generated["churn_lines"] == 0
    assert t2_unknown["category_confidence_mean"] == 0.5
    assert result["file_category_definition_version"].eq("file-category-rules-v1").all()


def test_compute_file_category_churn_metrics_rejects_invalid_input() -> None:
    engine = load_engine()
    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_file_category_churn_metrics(pd.DataFrame([{"file_path": "src/app.py"}]))


def test_build_file_category_churn_metrics_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()
    git_files = lake_dir / "git_files.parquet"
    output = tmp_path / "analysis" / "cross_evidence" / "datasets" / "file_category_churn_metrics.parquet"
    pd.DataFrame([git_file_row("src/app.py", added=5, deleted=1)]).to_parquet(git_files, index=False)
    git_files.with_name(f"{git_files.name}.metadata.json").write_text(
        json.dumps({"status": "success", "input_checksum": "fixture"}),
        encoding="utf-8",
    )

    first = engine.build_file_category_churn_metrics(lake_dir=lake_dir, output_path=output)
    second = engine.build_file_category_churn_metrics(lake_dir=lake_dir, output_path=output)

    assert output.exists()
    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-v1"
    assert first.equals(second)
    assert second.loc[0, "file_category"] == "source"


def test_build_file_category_exclusions_payload_summarizes_unknown_missing_and_warnings() -> None:
    engine = load_engine()
    metrics = engine.compute_file_category_churn_metrics(
        pd.DataFrame(
            [
                git_file_row("docs/schema.json", added=3, deleted=1),
                git_file_row("dist/app.js", added=None, deleted=None, binary=True),
                git_file_row("src/unknown.flow", added=1, deleted=0),
            ]
        )
    )

    payload = engine.build_file_category_exclusions_payload(metrics, source_checksum="checksum-v1")
    exclusions = {item["reason"]: item for item in payload["exclusions"]}

    assert payload["status"] == "success"
    assert payload["contract_version"] == "cross-evidence-manifest-v1"
    assert payload["schema_version"] == "file-category-exclusions-v1"
    assert payload["input_checksum"] == "checksum-v1"
    assert payload["summary"]["rows"] == 3
    assert payload["sources"]["file_category_churn_metrics"]["unknown_event_n"] == 1
    assert payload["summary"]["exclusion_reasons"]["unknown_file_category"] == 1
    assert exclusions["unknown_file_category"]["n_affected_events"] == 1
    assert exclusions["missing_line_counts"]["n_affected_events"] == 1
    assert exclusions["category_warnings"]["n_affected_events"] == 2
    assert exclusions["low_confidence_categories"]["n_affected_rows"] == 3
    assert exclusions["unknown_file_category"]["affected_keys_sample"][0]["file_category"] == "unknown"


def test_build_file_category_exclusions_report_persists_and_skips(tmp_path: Path) -> None:
    engine = load_engine()
    metrics_path = tmp_path / "file_category_churn_metrics.parquet"
    output = tmp_path / "cross_evidence_manifest_exclusions.json"
    metrics = engine.compute_file_category_churn_metrics(
        pd.DataFrame(
            [
                git_file_row("docs/schema.json", added=3, deleted=1),
                git_file_row("src/app.py", added=4, deleted=0),
            ]
        )
    )
    metrics.to_parquet(metrics_path, index=False)
    metrics_path.with_name(f"{metrics_path.name}.metadata.json").write_text(
        json.dumps({"status": "success", "input_checksum": "metrics"}),
        encoding="utf-8",
    )

    first = engine.build_file_category_exclusions_report(metrics_path=metrics_path, output_path=output)
    second = engine.build_file_category_exclusions_report(metrics_path=metrics_path, output_path=output)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-manifest-v1"
    assert first == second
    assert second["schema_version"] == "file-category-exclusions-v1"
    assert second["sources"]["file_category_churn_metrics"]["rows"] == 2
