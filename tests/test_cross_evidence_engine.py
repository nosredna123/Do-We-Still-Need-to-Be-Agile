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


def evaluator_row(
    cut: str,
    *,
    team: str = "TEAM_1",
    semester: str = "2025.2",
    engagement: float = 1.0,
    progress: float = 2.0,
    scope: float = 1.5,
    complexity: float = 1.0,
) -> dict[str, object]:
    row: dict[str, object] = {
        "ID_Equipe": team,
        "Semestre": semester,
        "temporal_marker": cut,
    }
    for metric, value in (
        ("engagement_participation", engagement),
        ("project_progress", progress),
        ("scope_applicability", scope),
        ("technical_complexity", complexity),
    ):
        row[f"{metric}_mean"] = value
        row[f"{metric}_median"] = value
        row[f"{metric}_iqr"] = 0.5
        row[f"{metric}_std"] = 0.25
        row[f"{metric}_n"] = 4
    return row


def commit_row(
    index: int,
    *,
    team: str = "TEAM_1",
    semester: str = "2025.2",
    cut: str = "T1",
    author: str = "Dev_A",
    added: int = 10,
    deleted: int = 2,
    files_changed: int = 1,
) -> dict[str, object]:
    return {
        "repository": f"repo-{team}",
        "commit_hash": f"commit-{team}-{cut}-{index}",
        "timestamp": pd.Timestamp("2025-10-18T12:00:00Z"),
        "temporal_marker": cut,
        "files_changed": files_changed,
        "lines_added": added,
        "lines_deleted": deleted,
        "branch_or_ref": "main",
        "branch_or_ref_source": "observed",
        "ID_Equipe": team,
        "Semestre": semester,
        "ID_Autor_Local": author,
        "source_type": "git_commit",
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


def test_compute_evaluator_outcome_metrics_pivots_fields_deltas_and_gap() -> None:
    engine = load_engine()
    frame = pd.DataFrame(
        [
            evaluator_row("T1", progress=2.0, scope=1.0, complexity=1.0),
            evaluator_row("T2", progress=3.0, scope=1.5, complexity=1.25),
            evaluator_row("T3", progress=4.0, scope=2.0, complexity=2.0),
        ]
    )

    result = engine.compute_evaluator_outcome_metrics(frame)
    row = result.iloc[0]

    assert len(result) == 1
    assert row["project_progress_mean_t1"] == 2.0
    assert row["project_progress_median_t2"] == 3.0
    assert row["scope_applicability_iqr_t3"] == 0.5
    assert row["technical_complexity_mean_delta_t1_t3"] == 1.0
    assert row["project_progress_mean_delta_t1_t2"] == 1.0
    assert row["progress_scope_gap_t1"] == 1.0
    assert row["progress_scope_gap_t3"] == 2.0
    assert row["progress_scope_gap_delta_t1_t3"] == 1.0
    assert bool(row["evaluator_outcome_available"])
    assert row["evaluator_outcome_observation_unit"] == "team_semester"
    assert row["evaluator_outcome_contract_version"] == "cross-evidence-v1"


def test_compute_evaluator_outcome_metrics_marks_missing_cut_unavailable() -> None:
    engine = load_engine()
    frame = pd.DataFrame(
        [
            evaluator_row("T1", progress=2.0, scope=1.0),
            evaluator_row("T3", progress=4.0, scope=2.0),
        ]
    )

    row = engine.compute_evaluator_outcome_metrics(frame).iloc[0]

    assert not bool(row["evaluator_outcome_available"])
    assert row["evaluator_outcome_unavailable_reason"] == "missing_required_temporal_cut:T2"
    assert pd.isna(row["project_progress_mean_delta_t1_t3"])
    assert pd.isna(row["progress_scope_gap_delta_t1_t3"])


def test_compute_evaluator_outcome_metrics_rejects_invalid_input() -> None:
    engine = load_engine()
    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_evaluator_outcome_metrics(pd.DataFrame([{"ID_Equipe": "TEAM_1"}]))
    with pytest.raises(ValueError, match="duplicate team-cut"):
        engine.compute_evaluator_outcome_metrics(pd.DataFrame([evaluator_row("T1"), evaluator_row("T1")]))


def test_build_evaluator_outcome_metrics_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()
    evaluator = lake_dir / "evaluator_team_cuts.parquet"
    output = tmp_path / "analysis" / "cross_evidence" / "datasets" / "evaluator_outcome_metrics.parquet"
    pd.DataFrame(
        [
            evaluator_row("T1", progress=2.0, scope=1.0),
            evaluator_row("T2", progress=3.0, scope=1.5),
            evaluator_row("T3", progress=4.0, scope=2.0),
        ]
    ).to_parquet(evaluator, index=False)
    evaluator.with_name(f"{evaluator.name}.metadata.json").write_text(
        json.dumps({"status": "success", "input_checksum": "fixture"}),
        encoding="utf-8",
    )

    first = engine.build_evaluator_outcome_metrics(lake_dir=lake_dir, output_path=output)
    second = engine.build_evaluator_outcome_metrics(lake_dir=lake_dir, output_path=output)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-v1"
    assert first.equals(second)
    assert second.loc[0, "scope_applicability_mean_t3"] == 2.0


def test_compute_author_pressure_metrics_calculates_author_distribution_and_churn() -> None:
    engine = load_engine()
    frame = pd.DataFrame(
        [
            commit_row(1, author="Dev_A", added=10, deleted=0, files_changed=2),
            commit_row(2, author="Dev_A", added=5, deleted=1, files_changed=1),
            commit_row(3, author="Dev_B", added=4, deleted=0, files_changed=3),
        ]
    )

    row = engine.compute_author_pressure_metrics(frame).iloc[0]

    assert row["commit_n"] == 3
    assert row["author_n"] == 2
    assert row["commits_per_author"] == 1.5
    assert row["max_author_share"] == pytest.approx(2 / 3)
    assert row["commit_gini"] == pytest.approx(1 / 6)
    assert row["churn_lines"] == 20
    assert row["lines_added"] == 19
    assert row["lines_deleted"] == 1
    assert row["files_changed"] == 6
    assert row["churn_per_author"] == 10
    assert row["author_pressure_available"]
    assert row["author_pressure_observation_unit"] == "team_semester_cut"
    assert row["author_pressure_contract_version"] == "cross-evidence-v1"


def test_compute_author_pressure_metrics_assigns_global_quartile_statuses() -> None:
    engine = load_engine()
    rows = [commit_row(1, team="TEAM_1", cut="T1", author="Dev_A")]
    rows.extend(commit_row(index, team="TEAM_2", cut="T1", author="Dev_A") for index in range(1, 3))
    rows.extend(commit_row(index, team="TEAM_3", cut="T1", author="Dev_A") for index in range(1, 4))
    rows.extend(commit_row(index, team="TEAM_4", cut="T1", author="Dev_A") for index in range(1, 5))

    result = engine.compute_author_pressure_metrics(pd.DataFrame(rows)).sort_values("commits_per_author")

    assert result["active_author_pressure_status"].tolist() == ["low", "moderate", "high", "critical"]
    assert result["commit_gini"].iloc[-1] == 0


def test_compute_author_pressure_metrics_rejects_invalid_input() -> None:
    engine = load_engine()
    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_author_pressure_metrics(pd.DataFrame([{"ID_Equipe": "TEAM_1"}]))
    frame = pd.DataFrame([commit_row(1, cut="T4")])
    with pytest.raises(ValueError, match="invalid temporal markers"):
        engine.compute_author_pressure_metrics(frame)
    frame = pd.DataFrame([commit_row(1, added=-1)])
    with pytest.raises(ValueError, match="must not be negative"):
        engine.compute_author_pressure_metrics(frame)


def test_build_author_pressure_metrics_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir()
    commits = lake_dir / "git_commits.parquet"
    output = tmp_path / "analysis" / "cross_evidence" / "datasets" / "author_pressure_metrics.parquet"
    pd.DataFrame(
        [
            commit_row(1, author="Dev_A"),
            commit_row(2, author="Dev_A"),
            commit_row(3, author="Dev_B"),
        ]
    ).to_parquet(commits, index=False)
    commits.with_name(f"{commits.name}.metadata.json").write_text(
        json.dumps({"status": "success", "input_checksum": "fixture"}),
        encoding="utf-8",
    )

    first = engine.build_author_pressure_metrics(lake_dir=lake_dir, output_path=output)
    second = engine.build_author_pressure_metrics(lake_dir=lake_dir, output_path=output)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-v1"
    assert first.equals(second)
    assert second.loc[0, "commits_per_author"] == 1.5
