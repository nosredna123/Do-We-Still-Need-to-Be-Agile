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


def temporal_source_frames() -> dict[str, pd.DataFrame]:
    keys = [
        {"ID_Equipe": "TEAM_1", "Semestre": "2025.2"},
        {"ID_Equipe": "TEAM_2", "Semestre": "2025.2"},
        {"ID_Equipe": "TEAM_3", "Semestre": "2026.1"},
    ]
    planning = pd.DataFrame(
        [
            keys[0] | {"planning_artifact_activity_t1": 1, "planning_artifact_activity_t2": 2, "planning_artifact_activity_t3": 4, "pi_line_delta_t1": 0, "pi_line_delta_t2": 2, "pi_line_delta_t3": 8},
            keys[1] | {"planning_artifact_activity_t1": 2, "planning_artifact_activity_t2": 2, "planning_artifact_activity_t3": 3, "pi_line_delta_t1": 2, "pi_line_delta_t2": 3, "pi_line_delta_t3": 6},
            keys[2] | {"planning_artifact_activity_t1": 3, "planning_artifact_activity_t2": 4, "planning_artifact_activity_t3": 2, "pi_line_delta_t1": 3, "pi_line_delta_t2": 4, "pi_line_delta_t3": 9},
        ]
    )
    churn = pd.DataFrame(
        [
            keys[0] | {"cc_total_t1": 1, "cc_total_t2": 3, "cc_total_t3": 9, "cc_commit_n_t1": 1, "cc_commit_n_t2": 2, "cc_commit_n_t3": 3},
            keys[1] | {"cc_total_t1": 2, "cc_total_t2": 2, "cc_total_t3": 8, "cc_commit_n_t1": 2, "cc_commit_n_t2": 2, "cc_commit_n_t3": 4},
            keys[2] | {"cc_total_t1": 4, "cc_total_t2": 5, "cc_total_t3": 4, "cc_commit_n_t1": 3, "cc_commit_n_t2": 4, "cc_commit_n_t3": 2},
        ]
    )
    degradation = pd.DataFrame(
        [
            keys[0] | {"technical_complexity_mean_t1": 1.0, "technical_complexity_mean_t2": 1.5, "technical_complexity_mean_t3": 2.0},
            keys[1] | {"technical_complexity_mean_t1": 1.0, "technical_complexity_mean_t2": 1.0, "technical_complexity_mean_t3": 1.5},
            keys[2] | {"technical_complexity_mean_t1": 2.0, "technical_complexity_mean_t2": 1.5, "technical_complexity_mean_t3": 1.0},
        ]
    )
    return {
        "planning_metrics": planning,
        "code_churn_metrics": churn,
        "technical_degradation_metrics": degradation,
    }


def late_instability_source_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    team = pd.DataFrame(
        [
            {
                "ID_Equipe": "TEAM_1",
                "Semestre": "2025.2",
                "planning_rework_signal_t2_t3": 10,
                "planning_artifact_activity_t3": 5,
                "pi_line_delta_t3": 100,
                "cc_total_t3": 1000,
                "cc_per_source_loc_t3": 2.0,
                "delta_dt_t2_t3": 0.1,
            },
            {
                "ID_Equipe": "TEAM_2",
                "Semestre": "2025.2",
                "planning_rework_signal_t2_t3": 20,
                "planning_artifact_activity_t3": 10,
                "pi_line_delta_t3": 200,
                "cc_total_t3": 2000,
                "cc_per_source_loc_t3": 4.0,
                "delta_dt_t2_t3": 0.2,
            },
        ]
    )
    file_category = pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T3", "file_category": "source", "event_n": 3, "churn_lines": 30},
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T3", "file_category": "config", "event_n": 2, "churn_lines": 10},
            {"ID_Equipe": "TEAM_2", "Semestre": "2025.2", "temporal_marker": "T3", "file_category": "source", "event_n": 6, "churn_lines": 60},
        ]
    )
    author = pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "temporal_marker": "T3", "commits_per_author": 2.0, "commit_gini": 0.1, "active_author_pressure_status": "low", "churn_lines": 100},
            {"ID_Equipe": "TEAM_2", "Semestre": "2025.2", "temporal_marker": "T3", "commits_per_author": 4.0, "commit_gini": 0.2, "active_author_pressure_status": "critical", "churn_lines": 200},
        ]
    )
    return team, file_category, author


def cross_evidence_panel_source_frames() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    engine = load_engine()
    evaluator = engine.compute_evaluator_outcome_metrics(
        pd.DataFrame(
            [
                evaluator_row("T1", team="TEAM_1", progress=2.0, scope=1.0),
                evaluator_row("T2", team="TEAM_1", progress=3.0, scope=1.5),
                evaluator_row("T3", team="TEAM_1", progress=4.0, scope=2.0),
                evaluator_row("T1", team="TEAM_2", progress=1.0, scope=1.0),
                evaluator_row("T2", team="TEAM_2", progress=2.0, scope=1.0),
                evaluator_row("T3", team="TEAM_2", progress=3.0, scope=1.5),
            ]
        )
    )
    team, _, _ = late_instability_source_frames()
    file_category = engine.compute_file_category_churn_metrics(
        pd.DataFrame(
            [
                git_file_row("src/app.py", team="TEAM_1", cut="T3", status="added", added=30, deleted=0),
                git_file_row("src/app.py", team="TEAM_2", cut="T3", status="added", added=60, deleted=0),
            ]
        )
    )
    author = engine.compute_author_pressure_metrics(
        pd.DataFrame(
            [
                commit_row(1, team="TEAM_1", cut="T3", author="Dev_A", added=30, deleted=0),
                commit_row(1, team="TEAM_2", cut="T3", author="Dev_A", added=60, deleted=0),
            ]
        )
    )
    late = engine.compute_late_instability_metrics(team, file_category, author)
    return evaluator, late, author, file_category


def test_compute_temporal_escalation_metrics_summarizes_deltas_ratios_and_wilcoxon() -> None:
    engine = load_engine()

    result = engine.compute_temporal_escalation_metrics(temporal_source_frames())
    planning = result.loc[result["metric_id"] == "planning_artifact_activity"].iloc[0]
    pi_delta = result.loc[result["metric_id"] == "pi_line_delta"].iloc[0]

    assert len(result) == 5
    assert planning["source_artifact"] == "planning_metrics"
    assert planning["n_total"] == 3
    assert planning["n_valid_t1"] == 3
    assert planning["median_t3"] == 3
    assert planning["t1_t3_paired_n"] == 3
    assert planning["t1_t3_increase_n"] == 2
    assert planning["t1_t3_same_n"] == 0
    assert planning["t1_t3_decrease_n"] == 1
    assert planning["t1_t3_median_delta"] == 1
    assert planning["t1_t3_wilcoxon_status"] == "success"
    assert planning["t3_t1_ratio_valid_n"] == 3
    assert planning["t3_t1_ratio_zero_denominator_n"] == 0
    assert pi_delta["t3_t1_ratio_valid_n"] == 2
    assert pi_delta["t3_t1_ratio_zero_denominator_n"] == 1
    assert pi_delta["temporal_escalation_contract_version"] == "cross-evidence-v1"


def test_compute_temporal_escalation_metrics_rejects_invalid_input() -> None:
    engine = load_engine()
    frames = temporal_source_frames()
    frames["planning_metrics"] = frames["planning_metrics"].drop(columns=["pi_line_delta_t3"])

    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_temporal_escalation_metrics(frames)


def test_build_temporal_escalation_metrics_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    analysis_dir = tmp_path / "analysis"
    analysis_dir.mkdir()
    output = tmp_path / "analysis" / "cross_evidence" / "datasets" / "temporal_escalation_metrics.parquet"
    for name, frame in temporal_source_frames().items():
        path = analysis_dir / f"{name}.parquet"
        frame.to_parquet(path, index=False)
        path.with_name(f"{path.name}.metadata.json").write_text(
            json.dumps({"status": "success", "input_checksum": name}),
            encoding="utf-8",
        )

    first = engine.build_temporal_escalation_metrics(analysis_dir=analysis_dir, output_path=output)
    second = engine.build_temporal_escalation_metrics(analysis_dir=analysis_dir, output_path=output)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-v1"
    assert first.equals(second)
    assert set(second["metric_id"]) == {"planning_artifact_activity", "pi_line_delta", "cc_total", "cc_commit_n", "technical_complexity_mean"}


def test_compute_late_instability_metrics_consolidates_components_and_index() -> None:
    engine = load_engine()
    team, file_category, author = late_instability_source_frames()

    result = engine.compute_late_instability_metrics(team, file_category, author)
    row = result.loc[result["ID_Equipe"] == "TEAM_2"].iloc[0]

    assert len(result) == 2
    assert row["source_churn_t3"] == 60
    assert row["source_events_t3"] == 6
    assert row["commits_per_author_t3"] == 4.0
    assert row["commit_gini_t3"] == 0.2
    assert row["active_author_pressure_status_t3"] == "critical"
    assert row["late_instability_component_available_n"] == 7
    assert row["late_instability_component_missing_n"] == 0
    assert row["late_instability_index"] == 1.0
    assert row["late_instability_observation_unit"] == "team_semester"
    assert row["late_instability_contract_version"] == "cross-evidence-v1"


def test_compute_late_instability_metrics_uses_available_rank_mean_when_component_missing() -> None:
    engine = load_engine()
    team, file_category, author = late_instability_source_frames()
    file_category = file_category.loc[file_category["ID_Equipe"] != "TEAM_1"]

    row = engine.compute_late_instability_metrics(team, file_category, author).loc[lambda frame: frame["ID_Equipe"] == "TEAM_1"].iloc[0]

    assert pd.isna(row["source_churn_t3"])
    assert row["late_instability_component_available_n"] == 5
    assert row["late_instability_component_missing_n"] == 2
    assert not pd.isna(row["late_instability_index"])


def test_compute_late_instability_metrics_rejects_invalid_input() -> None:
    engine = load_engine()
    team, file_category, author = late_instability_source_frames()
    with pytest.raises(ValueError, match="team_metrics missing columns"):
        engine.compute_late_instability_metrics(team.drop(columns=["cc_total_t3"]), file_category, author)
    duplicated_author = pd.concat([author, author.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate T3 team-semester"):
        engine.compute_late_instability_metrics(team, file_category, duplicated_author)


def test_build_late_instability_metrics_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    analysis_dir = tmp_path / "analysis"
    cross_dir = tmp_path / "cross" / "datasets"
    analysis_dir.mkdir()
    cross_dir.mkdir(parents=True)
    output = tmp_path / "analysis" / "cross_evidence" / "datasets" / "late_instability_metrics.parquet"
    team, file_category, author = late_instability_source_frames()
    team_path = analysis_dir / "team_metrics.parquet"
    team.to_parquet(team_path, index=False)
    team_path.with_name(f"{team_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")
    file_path = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets" / "file_category_churn_metrics.parquet"
    author_path = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets" / "author_pressure_metrics.parquet"
    file_path.parent.mkdir(parents=True)
    file_category.to_parquet(file_path, index=False)
    author.to_parquet(author_path, index=False)
    file_path.with_name(f"{file_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")
    author_path.with_name(f"{author_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")

    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_late_instability_metrics(analysis_dir=analysis_dir, output_path=output)
        second = engine.build_late_instability_metrics(analysis_dir=analysis_dir, output_path=output)
    finally:
        os.chdir(old_cwd)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-v1"
    assert first.equals(second)
    assert second.loc[1, "late_instability_index"] == 1.0


def test_compute_cross_evidence_panel_builds_curated_complete_panel() -> None:
    engine = load_engine()
    evaluator, late, author, file_category = cross_evidence_panel_source_frames()

    panel = engine.compute_cross_evidence_panel(evaluator, late, author, file_category)
    row = panel.loc[panel["ID_Equipe"] == "TEAM_2"].iloc[0]

    assert len(panel) == 2
    assert row["scope_applicability_mean_t3"] == 1.5
    assert row["project_progress_mean_t3"] == 3.0
    assert row["progress_scope_gap_t3"] == 1.5
    assert row["late_instability_index"] == pytest.approx(0.9285714285714286)
    assert row["source_event_share_t3"] == 1.0
    assert row["source_churn_share_t3"] == 1.0
    assert row["commit_n_t3"] == 1
    assert row["author_n_t3"] == 1
    assert row["cross_evidence_panel_available"]
    assert row["cross_evidence_panel_observation_unit"] == "team_semester"
    assert row["cross_evidence_panel_contract_version"] == "cross-evidence-v1"


def test_compute_cross_evidence_panel_fails_when_join_loses_coverage() -> None:
    engine = load_engine()
    evaluator, late, author, file_category = cross_evidence_panel_source_frames()
    late = late.loc[late["ID_Equipe"] != "TEAM_2"]

    with pytest.raises(ValueError, match="late_instability join lost"):
        engine.compute_cross_evidence_panel(evaluator, late, author, file_category)


def test_build_cross_evidence_panel_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    evaluator, late, author, file_category = cross_evidence_panel_source_frames()
    datasets = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets"
    datasets.mkdir(parents=True)
    output = datasets / "cross_evidence_panel.parquet"
    for name, frame in (
        ("evaluator_outcome_metrics", evaluator),
        ("late_instability_metrics", late),
        ("author_pressure_metrics", author),
        ("file_category_churn_metrics", file_category),
    ):
        path = datasets / f"{name}.parquet"
        frame.to_parquet(path, index=False)
        path.with_name(f"{path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")

    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_cross_evidence_panel(output_path=output)
        second = engine.build_cross_evidence_panel(output_path=output)
    finally:
        os.chdir(old_cwd)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-v1"
    assert first.equals(second)
    assert second.loc[0, "cross_evidence_panel_available"]


def correlation_panel() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ID_Equipe": f"TEAM_{index}",
                "Semestre": "2025.2",
                "scope_applicability_mean_t3": 10 - index,
                "source_churn_t3": index,
                "source_events_t3": index * 2,
                "pi_line_delta_t3": index * 3,
                "planning_artifact_activity_t3": index * 4,
                "planning_rework_signal_t2_t3": index * 5,
                "commits_per_author_t3": index * 6,
                "late_instability_index": index / 10,
            }
            for index in range(1, 6)
        ]
    )


def test_compute_cross_evidence_correlations_runs_declared_spearman_pairs() -> None:
    engine = load_engine()

    result = engine.compute_cross_evidence_correlations(correlation_panel())
    row = result.loc[result["analysis_id"] == "scope_vs_source_churn_t3"].iloc[0]

    assert len(result) == 7
    assert row["x"] == "source_churn_t3"
    assert row["y"] == "scope_applicability_mean_t3"
    assert row["n_valid"] == 5
    assert row["coefficient"] == pytest.approx(-1.0)
    assert row["p_value"] < 0.05
    assert row["status"] == "success"
    assert row["verdict"] == "supports"
    assert row["contract_version"] == "cross-evidence-correlations-v1"


def test_compute_cross_evidence_correlations_preserves_unavailable_zero_variance() -> None:
    engine = load_engine()
    panel = correlation_panel()
    panel["source_churn_t3"] = 1

    row = engine.compute_cross_evidence_correlations(panel).loc[lambda frame: frame["analysis_id"] == "scope_vs_source_churn_t3"].iloc[0]

    assert row["status"] == "unavailable"
    assert row["reason"] == "zero_variance"
    assert row["verdict"] == "unavailable"


def test_compute_cross_evidence_correlations_rejects_missing_columns() -> None:
    engine = load_engine()
    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_cross_evidence_correlations(correlation_panel().drop(columns=["source_churn_t3"]))


def test_build_cross_evidence_correlations_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    datasets = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets"
    results = tmp_path / "data" / "analysis" / "cross_evidence" / "results"
    datasets.mkdir(parents=True)
    panel_path = datasets / "cross_evidence_panel.parquet"
    output = results / "cross_evidence_correlations.csv"
    correlation_panel().to_parquet(panel_path, index=False)
    panel_path.with_name(f"{panel_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")

    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_cross_evidence_correlations(output_path=output)
        second = engine.build_cross_evidence_correlations(output_path=output)
    finally:
        os.chdir(old_cwd)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-correlations-v1"
    assert first["analysis_id"].tolist() == second["analysis_id"].tolist()
    assert first["verdict"].tolist() == second["verdict"].tolist()
    assert first["coefficient"].astype(float).tolist() == pytest.approx(second["coefficient"].astype(float).tolist())
    assert second.loc[0, "test"] == "spearman"


def contrast_panel() -> pd.DataFrame:
    rows = []
    for index in range(1, 9):
        rows.append(
            {
                "ID_Equipe": f"TEAM_{index}",
                "Semestre": "2025.2",
                "scope_applicability_mean_t3": index,
                "project_progress_mean_t3": index,
                "late_instability_index": index / 10,
                "planning_rework_signal_t2_t3": index * 10,
                "planning_artifact_activity_t3": index * 2,
                "pi_line_delta_t3": index * 3,
                "source_churn_t3": index * 4,
                "source_events_t3": index * 5,
                "commits_per_author_t3": index * 6,
            }
        )
    return pd.DataFrame(rows)


def test_compute_best_worst_project_contrasts_uses_top_bottom_four_and_effect_size() -> None:
    engine = load_engine()

    result = engine.compute_best_worst_project_contrasts(contrast_panel())
    row = result.loc[
        result["contrast_id"] == "scope_applicability_mean_t3__planning_rework_signal_t2_t3__top_bottom_4"
    ].iloc[0]

    assert len(result) == 24
    assert row["low_group_n"] == 4
    assert row["high_group_n"] == 4
    assert row["low_score_min"] == 1
    assert row["low_score_max"] == 4
    assert row["high_score_min"] == 5
    assert row["high_score_max"] == 8
    assert row["low_median"] == 25
    assert row["high_median"] == 65
    assert row["median_difference_high_minus_low"] == 40
    assert row["cliffs_delta_high_vs_low"] == 1.0
    assert row["status"] == "success"
    assert row["contract_version"] == "cross-evidence-best-worst-contrasts-v1"


def test_compute_best_worst_project_contrasts_preserves_zero_variance_unavailable() -> None:
    engine = load_engine()
    panel = contrast_panel()
    panel["source_churn_t3"] = 1

    row = engine.compute_best_worst_project_contrasts(panel).loc[
        lambda frame: frame["contrast_id"] == "scope_applicability_mean_t3__source_churn_t3__top_bottom_4"
    ].iloc[0]

    assert row["status"] == "unavailable"
    assert row["reason"] == "zero_variance"


def test_compute_best_worst_project_contrasts_rejects_missing_columns() -> None:
    engine = load_engine()
    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_best_worst_project_contrasts(contrast_panel().drop(columns=["source_churn_t3"]))


def test_build_best_worst_project_contrasts_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    datasets = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets"
    results = tmp_path / "data" / "analysis" / "cross_evidence" / "results"
    datasets.mkdir(parents=True)
    panel_path = datasets / "cross_evidence_panel.parquet"
    output = results / "best_worst_project_contrasts.csv"
    contrast_panel().to_parquet(panel_path, index=False)
    panel_path.with_name(f"{panel_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")

    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_best_worst_project_contrasts(output_path=output)
        second = engine.build_best_worst_project_contrasts(output_path=output)
    finally:
        os.chdir(old_cwd)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-best-worst-contrasts-v1"
    assert first["contrast_id"].tolist() == second["contrast_id"].tolist()
    assert second.loc[0, "test"] == "mann_whitney_u"


def test_compute_leave_one_out_sensitivity_summarizes_all_declared_correlations() -> None:
    engine = load_engine()
    panel = correlation_panel()
    correlations = engine.compute_cross_evidence_correlations(panel)

    result = engine.compute_leave_one_out_sensitivity(panel, correlations)
    row = result.loc[result["analysis_id"] == "scope_vs_source_churn_t3"].iloc[0]

    assert len(result) == 7
    assert row["test"] == "spearman_leave_one_out"
    assert row["original_coefficient"] == pytest.approx(-1.0)
    assert row["original_verdict"] == "supports"
    assert row["loo_total_n"] == 5
    assert row["loo_tested_n"] == 5
    assert row["loo_supports_n"] == 5
    assert row["loo_support_share"] == 1.0
    assert row["robustness_class"] == "robust_all"
    assert row["contract_version"] == "cross-evidence-leave-one-out-v1"


def test_compute_leave_one_out_sensitivity_classifies_no_support() -> None:
    engine = load_engine()
    panel = correlation_panel()
    panel["scope_applicability_mean_t3"] = range(1, 6)
    correlations = engine.compute_cross_evidence_correlations(panel)

    row = engine.compute_leave_one_out_sensitivity(panel, correlations).loc[
        lambda frame: frame["analysis_id"] == "scope_vs_source_churn_t3"
    ].iloc[0]

    assert row["original_verdict"] == "contradicts"
    assert row["loo_supports_n"] == 0
    assert row["robustness_class"] == "no_support"


def test_compute_leave_one_out_sensitivity_rejects_missing_inputs() -> None:
    engine = load_engine()
    panel = correlation_panel()
    correlations = engine.compute_cross_evidence_correlations(panel)

    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_leave_one_out_sensitivity(panel.drop(columns=["source_churn_t3"]), correlations)
    with pytest.raises(ValueError, match="missing analysis row"):
        engine.compute_leave_one_out_sensitivity(panel, correlations.iloc[1:])


def test_build_leave_one_out_sensitivity_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    datasets = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets"
    results = tmp_path / "data" / "analysis" / "cross_evidence" / "results"
    datasets.mkdir(parents=True)
    results.mkdir(parents=True)
    panel_path = datasets / "cross_evidence_panel.parquet"
    correlations_path = results / "cross_evidence_correlations.csv"
    output = results / "leave_one_out_sensitivity.csv"
    panel = correlation_panel()
    panel.to_parquet(panel_path, index=False)
    panel_path.with_name(f"{panel_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")
    engine.compute_cross_evidence_correlations(panel).to_csv(correlations_path, index=False)
    correlations_path.with_name(f"{correlations_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")

    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_leave_one_out_sensitivity(output_path=output)
        second = engine.build_leave_one_out_sensitivity(output_path=output)
    finally:
        os.chdir(old_cwd)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-leave-one-out-v1"
    assert first["analysis_id"].tolist() == second["analysis_id"].tolist()
    assert second.loc[0, "robustness_class"] == "robust_all"


def overlap_panel() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"ID_Equipe": f"TEAM_{index:02d}", "Semestre": "2025.2", "planning_rework_signal_t2_t3": index, "source_churn_t3": index, "commits_per_author_t3": 9 - index, "scope_applicability_mean_t3": 10 - index}
            for index in range(1, 9)
        ]
    )


def test_compute_extreme_case_overlap_uses_fixed_four_and_persists_anonymized_keys() -> None:
    engine = load_engine()

    result = engine.compute_extreme_case_overlap(overlap_panel())
    row = result.loc[
        result["overlap_id"] == "planning_rework_signal_t2_t3__top__source_churn_t3__top"
    ].iloc[0]
    inverse = result.loc[
        result["overlap_id"] == "planning_rework_signal_t2_t3__top__commits_per_author_t3__bottom"
    ].iloc[0]

    assert len(result) == 18
    assert row["group_rule"] == "top_bottom_fixed_n"
    assert row["group_size_requested"] == 4
    assert row["left_group_n"] == 4
    assert row["right_group_n"] == 4
    assert row["overlap_n"] == 4
    assert row["overlap_rate_left"] == 1.0
    assert row["jaccard"] == 1.0
    assert json.loads(row["overlap_keys"])[0] == {"ID_Equipe": "TEAM_05", "Semestre": "2025.2"}
    assert inverse["overlap_n"] == 4
    assert inverse["contract_version"] == "cross-evidence-extreme-overlap-v1"


def test_compute_extreme_case_overlap_rejects_missing_columns() -> None:
    engine = load_engine()
    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_extreme_case_overlap(overlap_panel().drop(columns=["source_churn_t3"]))


def test_build_extreme_case_overlap_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    datasets = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets"
    results = tmp_path / "data" / "analysis" / "cross_evidence" / "results"
    datasets.mkdir(parents=True)
    results.mkdir(parents=True)
    panel_path = datasets / "cross_evidence_panel.parquet"
    output = results / "extreme_case_overlap.csv"
    overlap_panel().to_parquet(panel_path, index=False)
    panel_path.with_name(f"{panel_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")

    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_extreme_case_overlap(output_path=output)
        second = engine.build_extreme_case_overlap(output_path=output)
    finally:
        os.chdir(old_cwd)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-extreme-overlap-v1"
    assert first["overlap_id"].tolist() == second["overlap_id"].tolist()
    assert second["overlap_n"].astype(int).tolist() == first["overlap_n"].astype(int).tolist()


def semester_panel() -> pd.DataFrame:
    rows = []
    for index in range(1, 10):
        rows.append(
            {
                "ID_Equipe": f"TEAM_{index:02d}",
                "Semestre": "2025.2",
                "scope_applicability_mean_t3": 10 - index,
                "source_churn_t3": index,
                "source_events_t3": index * 2,
                "pi_line_delta_t3": index * 3,
                "planning_artifact_activity_t3": index * 4,
                "planning_rework_signal_t2_t3": index * 5,
                "commits_per_author_t3": index * 6,
                "late_instability_index": index / 10,
            }
        )
    for index in range(1, 6):
        rows.append(
            {
                "ID_Equipe": f"TEAM_B{index}",
                "Semestre": "2026.1",
                "scope_applicability_mean_t3": 10 - index,
                "source_churn_t3": index,
                "source_events_t3": index * 2,
                "pi_line_delta_t3": index * 3,
                "planning_artifact_activity_t3": index * 4,
                "planning_rework_signal_t2_t3": index * 5,
                "commits_per_author_t3": index * 6,
                "late_instability_index": index / 10,
            }
        )
    return pd.DataFrame(rows)


def test_compute_semester_stratified_results_returns_global_and_semester_rows() -> None:
    engine = load_engine()

    result = engine.compute_semester_stratified_results(semester_panel())
    global_row = result.loc[
        (result["analysis_id"] == "scope_vs_source_churn_t3") & (result["stratum"] == "global")
    ].iloc[0]
    small_row = result.loc[
        (result["analysis_id"] == "scope_vs_source_churn_t3") & (result["semester"] == "2026.1")
    ].iloc[0]

    assert len(result) == 21
    assert set(result["stratum"]) == {"global", "semester"}
    assert global_row["n_valid"] == 14
    assert global_row["warning"] is None or pd.isna(global_row["warning"])
    assert small_row["n_valid"] == 5
    assert small_row["warning"] == "very_small_sample_n_lt_6"
    assert small_row["status"] == "success"
    assert global_row["stratification_class"] == "global_supported_semester_supported"
    assert global_row["contract_version"] == "cross-evidence-semester-stratified-v1"


def test_compute_semester_stratified_results_rejects_missing_columns() -> None:
    engine = load_engine()
    with pytest.raises(ValueError, match="missing columns"):
        engine.compute_semester_stratified_results(semester_panel().drop(columns=["source_churn_t3"]))


def test_build_semester_stratified_results_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    datasets = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets"
    results_dir = tmp_path / "data" / "analysis" / "cross_evidence" / "results"
    datasets.mkdir(parents=True)
    results_dir.mkdir(parents=True)
    panel_path = datasets / "cross_evidence_panel.parquet"
    output = results_dir / "semester_stratified_results.csv"
    semester_panel().to_parquet(panel_path, index=False)
    panel_path.with_name(f"{panel_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")

    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_semester_stratified_results(output_path=output)
        second = engine.build_semester_stratified_results(output_path=output)
    finally:
        os.chdir(old_cwd)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-semester-stratified-v1"
    first_keys = first[["analysis_id", "stratum", "semester"]].fillna("<NA>").astype(str)
    second_keys = second[["analysis_id", "stratum", "semester"]].fillna("<NA>").astype(str)
    assert first_keys.values.tolist() == second_keys.values.tolist()


def priority_matrix_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    engine = load_engine()
    panel = correlation_panel()
    correlations = engine.compute_cross_evidence_correlations(panel)
    contrasts = engine.compute_best_worst_project_contrasts(contrast_panel())
    leave_one_out = engine.compute_leave_one_out_sensitivity(panel, correlations)
    overlap = engine.compute_extreme_case_overlap(overlap_panel())
    semester = engine.compute_semester_stratified_results(semester_panel())
    return correlations, contrasts, leave_one_out, overlap, semester


def test_compute_evidence_priority_matrix_preserves_atomic_rows_and_tiers() -> None:
    engine = load_engine()
    matrix = engine.compute_evidence_priority_matrix(*priority_matrix_inputs())

    assert len(matrix) == 77
    assert set(matrix["source_artifact"]) == {
        "cross_evidence_correlations",
        "best_worst_project_contrasts",
        "leave_one_out_sensitivity",
        "extreme_case_overlap",
        "semester_stratified_results",
    }
    assert set(matrix["evidence_tier"]) == {"A", "B", "C"}
    assert matrix["evidence_id"].is_unique
    correlation = matrix.loc[matrix["evidence_id"] == "correlation__scope_vs_source_churn_t3"].iloc[0]
    assert correlation["evidence_tier"] == "A"
    assert correlation["recommended_use"] == "anchor_narrative_claim"
    robust = matrix.loc[matrix["evidence_id"] == "leave_one_out__scope_vs_source_churn_t3"].iloc[0]
    assert robust["evidence_tier"] == "A"
    assert matrix["contract_version"].eq("cross-evidence-priority-matrix-v1").all()


def test_compute_evidence_priority_matrix_rejects_missing_source_columns() -> None:
    engine = load_engine()
    inputs = list(priority_matrix_inputs())
    inputs[0] = inputs[0].drop(columns=["verdict"])
    with pytest.raises(ValueError, match="cross_evidence_correlations missing columns"):
        engine.compute_evidence_priority_matrix(*inputs)


def test_build_evidence_priority_matrix_persists_and_skips_current_artifact(tmp_path: Path) -> None:
    engine = load_engine()
    results_dir = tmp_path / "data" / "analysis" / "cross_evidence" / "results"
    results_dir.mkdir(parents=True)
    inputs = priority_matrix_inputs()
    artifact_names = [
        "cross_evidence_correlations",
        "best_worst_project_contrasts",
        "leave_one_out_sensitivity",
        "extreme_case_overlap",
        "semester_stratified_results",
    ]
    for artifact, frame in zip(artifact_names, inputs):
        path = results_dir / f"{artifact}.csv"
        frame.to_csv(path, index=False)
        path.with_name(f"{path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")
    output = results_dir / "evidence_priority_matrix.csv"

    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_evidence_priority_matrix(output_path=output)
        second = engine.build_evidence_priority_matrix(output_path=output)
    finally:
        os.chdir(old_cwd)

    metadata = json.loads(output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8"))
    assert output.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-priority-matrix-v1"
    assert len(first) == len(second) == 77
    assert first["evidence_id"].tolist() == second["evidence_id"].tolist()


def test_compute_scope_vs_late_instability_figure_data_builds_four_anonymized_panels() -> None:
    engine = load_engine()
    panel = correlation_panel().assign(
        planning_artifact_activity_t3=lambda frame: frame["planning_artifact_activity_t3"],
    )

    result = engine.compute_scope_vs_late_instability_figure_data(panel)

    assert len(result) == 20
    assert set(result["plot_id"]) == {
        "scope_vs_late_instability_index",
        "scope_vs_source_churn_t3",
        "scope_vs_planning_artifact_activity_t3",
        "scope_vs_commits_per_author_t3",
    }
    assert result["anonymized_team_id"].isin({f"TEAM_{index:02d}" for index in range(1, 6)}).all()
    assert result.loc[result["plot_id"] == "scope_vs_source_churn_t3", "y_scale"].eq("log").all()
    assert result.loc[result["plot_id"] == "scope_vs_late_instability_index", "y_scale"].eq("linear").all()


def test_build_scope_vs_late_instability_figure_exports_and_skips(tmp_path: Path) -> None:
    engine = load_engine()
    panel_path = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets" / "cross_evidence_panel.parquet"
    panel_path.parent.mkdir(parents=True)
    panel = correlation_panel().assign(
        planning_artifact_activity_t3=lambda frame: frame["planning_artifact_activity_t3"],
    )
    panel.to_parquet(panel_path, index=False)
    panel_path.with_name(f"{panel_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")
    data_path = tmp_path / "data" / "analysis" / "cross_evidence" / "figure_data" / "scope_vs_late_instability.csv"
    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_scope_vs_late_instability_figure(
            output_data_path=data_path,
            figure_root=tmp_path / "assets" / "figures" / "cross_evidence",
            figure_data_root=data_path.parent,
        )
        second = engine.build_scope_vs_late_instability_figure(
            output_data_path=data_path,
            figure_root=tmp_path / "assets" / "figures" / "cross_evidence",
            figure_data_root=data_path.parent,
        )
    finally:
        os.chdir(old_cwd)

    manifest_path = data_path.with_name(f"{data_path.stem}.manifest.json")
    metadata = json.loads(data_path.with_name(f"{data_path.name}.metadata.json").read_text(encoding="utf-8"))
    assert data_path.exists()
    assert manifest_path.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-figure-data-v1"
    assert len(first) == len(second) == 20
    assert (tmp_path / "assets" / "figures" / "cross_evidence" / "prioritarias" / "scope_vs_late_instability.png").exists()
    entry = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert entry["visual_spec_version"] == "cross-evidence-visual-spec-v1"
    assert entry["export_formats"] == ["html", "png", "svg", "pdf"]


def test_compute_source_churn_vs_planning_rework_figure_data_uses_source_churn_and_log_scales() -> None:
    engine = load_engine()
    late = pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "planning_rework_signal_t2_t3": 10, "source_churn_t3": 100},
            {"ID_Equipe": "TEAM_2", "Semestre": "2026.1", "planning_rework_signal_t2_t3": 100, "source_churn_t3": 10000},
        ]
    )

    result = engine.compute_source_churn_vs_planning_rework_figure_data(late)

    assert len(result) == 2
    assert result["x"].eq("planning_rework_signal_t2_t3").all()
    assert result["y"].eq("source_churn_t3").all()
    assert result["x_scale"].eq("log").all()
    assert result["y_scale"].eq("log").all()
    assert result["transformation"].eq("complete_case_pair|source_category_only").all()


def test_compute_source_churn_vs_planning_rework_rejects_nonpositive_values() -> None:
    engine = load_engine()
    late = pd.DataFrame(
        [{"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "planning_rework_signal_t2_t3": 0, "source_churn_t3": 100}]
    )

    with pytest.raises(ValueError, match="must be positive"):
        engine.compute_source_churn_vs_planning_rework_figure_data(late)


def test_build_source_churn_vs_planning_rework_figure_exports_and_skips(tmp_path: Path) -> None:
    engine = load_engine()
    source_path = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets" / "late_instability_metrics.parquet"
    source_path.parent.mkdir(parents=True)
    late = pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "planning_rework_signal_t2_t3": 10, "source_churn_t3": 100},
            {"ID_Equipe": "TEAM_2", "Semestre": "2026.1", "planning_rework_signal_t2_t3": 100, "source_churn_t3": 10000},
        ]
    )
    late.to_parquet(source_path, index=False)
    source_path.with_name(f"{source_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")
    data_path = tmp_path / "data" / "analysis" / "cross_evidence" / "figure_data" / "source_churn_vs_planning_rework.csv"
    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_source_churn_vs_planning_rework_figure(
            output_data_path=data_path,
            figure_root=tmp_path / "assets" / "figures" / "cross_evidence",
            figure_data_root=data_path.parent,
        )
        second = engine.build_source_churn_vs_planning_rework_figure(
            output_data_path=data_path,
            figure_root=tmp_path / "assets" / "figures" / "cross_evidence",
            figure_data_root=data_path.parent,
        )
    finally:
        os.chdir(old_cwd)

    manifest_path = data_path.with_name(f"{data_path.stem}.manifest.json")
    metadata = json.loads(data_path.with_name(f"{data_path.name}.metadata.json").read_text(encoding="utf-8"))
    assert data_path.exists()
    assert manifest_path.exists()
    assert metadata["status"] == "success"
    assert metadata["contract_version"] == "cross-evidence-figure-data-v1"
    assert len(first) == len(second) == 2
    assert (tmp_path / "assets" / "figures" / "cross_evidence" / "prioritarias" / "source_churn_vs_planning_rework.pdf").exists()
    entry = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert entry["visual_spec_version"] == "cross-evidence-visual-spec-v1"
    assert entry["transformations"][-1] == "log_y"


def temporal_escalation_fixture() -> tuple[pd.DataFrame, pd.DataFrame]:
    temporal = pd.DataFrame(
        [
            {"metric_id": "planning_artifact_activity", "mean_t1": 10.0, "mean_t2": 20.0, "mean_t3": 40.0, "n_valid_t1": 4, "n_valid_t2": 4, "n_valid_t3": 4},
            {"metric_id": "pi_line_delta", "mean_t1": 2.0, "mean_t2": 10.0, "mean_t3": 20.0, "n_valid_t1": 4, "n_valid_t2": 4, "n_valid_t3": 4},
            {"metric_id": "cc_total", "mean_t1": 100.0, "mean_t2": 200.0, "mean_t3": 400.0, "n_valid_t1": 4, "n_valid_t2": 4, "n_valid_t3": 4},
            {"metric_id": "cc_commit_n", "mean_t1": 2.0, "mean_t2": 3.0, "mean_t3": 4.0, "n_valid_t1": 4, "n_valid_t2": 4, "n_valid_t3": 4},
            {"metric_id": "technical_complexity_mean", "mean_t1": 1.0, "mean_t2": 1.2, "mean_t3": 1.5, "n_valid_t1": 4, "n_valid_t2": 4, "n_valid_t3": 4},
        ]
    )
    evaluator = pd.DataFrame(
        [
            {"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "project_progress_mean_t1": 2.0, "project_progress_mean_t2": 3.0, "project_progress_mean_t3": 4.0},
            {"ID_Equipe": "TEAM_2", "Semestre": "2026.1", "project_progress_mean_t1": 1.0, "project_progress_mean_t2": 2.0, "project_progress_mean_t3": 2.0},
        ]
    )
    return temporal, evaluator


def test_compute_temporal_escalation_figure_data_normalizes_six_metrics() -> None:
    engine = load_engine()
    temporal, evaluator = temporal_escalation_fixture()

    result = engine.compute_temporal_escalation_figure_data(temporal, evaluator)

    assert len(result) == 24
    assert set(result["metric_id"]) == {
        "planning_artifact_activity", "pi_line_delta", "cc_total", "cc_commit_n", "technical_complexity_mean", "project_progress"
    }
    assert result["temporal_marker"].isin({"T1", "T2", "T3"}).all()
    assert result.loc[(result["metric_id"] == "cc_total") & (result["series"] == "global") & (result["temporal_marker"] == "T1"), "value_relative_t1"].iloc[0] == 1.0
    assert result.loc[(result["metric_id"] == "cc_total") & (result["series"] == "global") & (result["temporal_marker"] == "T3"), "value_relative_t1"].iloc[0] == 4.0
    assert set(result.loc[result["metric_id"] == "project_progress", "series"]) == {"global", "semester"}
    assert result["transformation"].eq("relative_to_t1_baseline").all()


def test_compute_temporal_escalation_figure_data_rejects_missing_metric() -> None:
    engine = load_engine()
    temporal, evaluator = temporal_escalation_fixture()
    with pytest.raises(ValueError, match="exactly one row"):
        engine.compute_temporal_escalation_figure_data(temporal.loc[temporal["metric_id"] != "cc_total"], evaluator)


def test_build_temporal_escalation_figure_exports_and_skips(tmp_path: Path) -> None:
    engine = load_engine()
    temporal, evaluator = temporal_escalation_fixture()
    datasets = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets"
    datasets.mkdir(parents=True)
    temporal_path = datasets / "temporal_escalation_metrics.parquet"
    evaluator_path = datasets / "evaluator_outcome_metrics.parquet"
    temporal.to_parquet(temporal_path, index=False)
    evaluator.to_parquet(evaluator_path, index=False)
    for path in (temporal_path, evaluator_path):
        path.with_name(f"{path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")
    source_frames = {
        "planning_metrics": pd.DataFrame(
            [{"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "planning_artifact_activity_t1": 1, "planning_artifact_activity_t2": 2, "planning_artifact_activity_t3": 4, "pi_line_delta_t1": 1, "pi_line_delta_t2": 2, "pi_line_delta_t3": 4}]
        ),
        "code_churn_metrics": pd.DataFrame(
            [{"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "cc_total_t1": 10, "cc_total_t2": 20, "cc_total_t3": 40, "cc_commit_n_t1": 1, "cc_commit_n_t2": 2, "cc_commit_n_t3": 4}]
        ),
        "technical_degradation_metrics": pd.DataFrame(
            [{"ID_Equipe": "TEAM_1", "Semestre": "2025.2", "technical_complexity_mean_t1": 1, "technical_complexity_mean_t2": 2, "technical_complexity_mean_t3": 4}]
        ),
    }
    for name, frame in source_frames.items():
        source_path = tmp_path / "data" / "analysis" / f"{name}.parquet"
        frame.to_parquet(source_path, index=False)
        source_path.with_name(f"{source_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")
    data_path = tmp_path / "data" / "analysis" / "cross_evidence" / "figure_data" / "temporal_escalation_panel.csv"
    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_temporal_escalation_figure(output_data_path=data_path, figure_root=tmp_path / "assets" / "figures" / "cross_evidence", figure_data_root=data_path.parent)
        second = engine.build_temporal_escalation_figure(output_data_path=data_path, figure_root=tmp_path / "assets" / "figures" / "cross_evidence", figure_data_root=data_path.parent)
    finally:
        os.chdir(old_cwd)
    manifest_path = data_path.with_name(f"{data_path.stem}.manifest.json")
    metadata = json.loads(data_path.with_name(f"{data_path.name}.metadata.json").read_text(encoding="utf-8"))
    assert data_path.exists() and manifest_path.exists()
    assert metadata["status"] == "success"
    assert len(first) == len(second) == 39
    assert (tmp_path / "assets" / "figures" / "cross_evidence" / "prioritarias" / "temporal_escalation_panel.png").exists()
    entry = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert entry["visual_spec_version"] == "cross-evidence-visual-spec-v1"
    assert "relative_to_t1_baseline" in entry["transformations"]


def file_category_churn_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"temporal_marker": "T1", "file_category": "source", "event_n": 2, "churn_lines": 20, "total_event_n": 3, "total_churn_lines": 30, "category_event_share": 2 / 3, "category_churn_share": 2 / 3},
            {"temporal_marker": "T1", "file_category": "planning", "event_n": 1, "churn_lines": 10, "total_event_n": 3, "total_churn_lines": 30, "category_event_share": 1 / 3, "category_churn_share": 1 / 3},
            {"temporal_marker": "T2", "file_category": "source", "event_n": 4, "churn_lines": 80, "total_event_n": 5, "total_churn_lines": 100, "category_event_share": 4 / 5, "category_churn_share": 0.8},
            {"temporal_marker": "T2", "file_category": "generated", "event_n": 1, "churn_lines": 20, "total_event_n": 5, "total_churn_lines": 100, "category_event_share": 0.2, "category_churn_share": 0.2},
            {"temporal_marker": "T3", "file_category": "unknown", "event_n": 1, "churn_lines": 5, "total_event_n": 1, "total_churn_lines": 5, "category_event_share": 1.0, "category_churn_share": 1.0},
        ]
    )


def test_compute_file_category_churn_figure_data_preserves_all_categories_and_zero_fills() -> None:
    engine = load_engine()
    result = engine.compute_file_category_churn_figure_data(file_category_churn_fixture())

    assert len(result) == 24
    assert set(result["file_category"]) == set(engine.FILE_CATEGORY_CHURN_FIGURE_CATEGORIES)
    assert set(result["temporal_marker"]) == {"T1", "T2", "T3"}
    absent = result.loc[(result["temporal_marker"] == "T1") & (result["file_category"] == "unknown")].iloc[0]
    assert absent["event_n"] == 0
    assert absent["churn_lines"] == 0
    assert result.loc[result["temporal_marker"] == "T1", "category_churn_share"].sum() == pytest.approx(1.0)
    assert result["transformation"].eq("category_complete_grid|absolute_log_and_relative_100_percent").all()


def test_build_file_category_churn_figure_exports_and_skips(tmp_path: Path) -> None:
    engine = load_engine()
    source_path = tmp_path / "data" / "analysis" / "cross_evidence" / "datasets" / "file_category_churn_metrics.parquet"
    source_path.parent.mkdir(parents=True)
    file_category_churn_fixture().to_parquet(source_path, index=False)
    source_path.with_name(f"{source_path.name}.metadata.json").write_text(json.dumps({"status": "success"}), encoding="utf-8")
    data_path = tmp_path / "data" / "analysis" / "cross_evidence" / "figure_data" / "file_category_churn_by_cut.csv"
    old_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        first = engine.build_file_category_churn_figure(output_data_path=data_path, figure_root=tmp_path / "assets" / "figures" / "cross_evidence", figure_data_root=data_path.parent)
        second = engine.build_file_category_churn_figure(output_data_path=data_path, figure_root=tmp_path / "assets" / "figures" / "cross_evidence", figure_data_root=data_path.parent)
    finally:
        os.chdir(old_cwd)
    manifest_path = data_path.with_name(f"{data_path.stem}.manifest.json")
    metadata = json.loads(data_path.with_name(f"{data_path.name}.metadata.json").read_text(encoding="utf-8"))
    assert data_path.exists() and manifest_path.exists()
    assert metadata["status"] == "success"
    assert len(first) == len(second) == 24
    assert (tmp_path / "assets" / "figures" / "cross_evidence" / "prioritarias" / "file_category_churn_by_cut.pdf").exists()
    entry = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "relative_100_percent_panel" in entry["transformations"]


def test_cross_evidence_visual_spec_defines_shared_publication_contract() -> None:
    engine = load_engine()

    spec = engine.cross_evidence_visual_spec(
        "scope_vs_late_instability",
        category="prioritarias",
        variables=["scope_applicability_mean_t3", "late_instability_index"],
        required=True,
    )

    assert spec["visual_spec_version"] == "cross-evidence-visual-spec-v1"
    assert spec["theme"] == "plotly_white"
    assert spec["width"] == 1400
    assert spec["height"] == 850
    assert spec["png_scale"] == 2
    assert spec["export_formats"] == ["html", "png", "svg", "pdf"]
    assert spec["palette"]["scope"] == "#2563EB"
    assert spec["anonymization_policy"] == "public_visual_ranked_or_aggregate"


def test_cross_evidence_visual_helpers_choose_scale_and_anonymize_ids(tmp_path: Path) -> None:
    engine = load_engine()
    assert engine.choose_cross_evidence_scale(pd.Series([1, 10, 1000]))["scale"] == "log"
    assert engine.choose_cross_evidence_scale(pd.Series([0, 10, 1000]))["scale"] == "linear"
    assert engine.choose_cross_evidence_scale(pd.Series([1, 2, 50]))["scale"] == "linear"

    visual = engine.anonymize_cross_evidence_visual_data(
        pd.DataFrame({"ID_Equipe": ["raw-b", "raw-a"], "value": [2, 1]})
    )
    assert "ID_Equipe" not in visual.columns
    assert visual["anonymized_team_id"].tolist() == ["TEAM_02", "TEAM_01"]
    paths = engine.cross_evidence_figure_export_paths(
        "scope_vs_late_instability",
        category="prioritarias",
        figure_root=tmp_path / "figures",
        figure_data_root=tmp_path / "figure_data",
    )
    assert paths["data"] == tmp_path / "figure_data" / "scope_vs_late_instability.csv"
    assert paths["pdf"] == tmp_path / "figures" / "prioritarias" / "scope_vs_late_instability.pdf"


def test_build_cross_evidence_figure_manifest_entry_records_visual_contract(tmp_path: Path) -> None:
    engine = load_engine()
    import plotly.graph_objects as plotly_go

    paths = engine.cross_evidence_figure_export_paths(
        "test_figure",
        figure_root=tmp_path / "figures",
        figure_data_root=tmp_path / "figure_data",
    )
    paths["data"].parent.mkdir(parents=True)
    paths["data"].write_text("x,y\n1,2\n", encoding="utf-8")
    paths["png"].parent.mkdir(parents=True)
    paths["png"].write_bytes(b"png")
    entry = engine.build_cross_evidence_figure_manifest_entry(
        plotly_go.Figure(),
        pd.DataFrame({"x": [1], "y": [2]}),
        figure_id="test_figure",
        category="exploratorias",
        source="fixture",
        unit_of_analysis="team_semester",
        variables=["x", "y"],
        transformations=["complete_case_pair"],
        scale_notes=["linear"],
        paths=paths,
    )

    assert entry["visual_spec_version"] == "cross-evidence-visual-spec-v1"
    assert entry["dimensions"] == {"width": 1400, "height": 850, "png_scale": 2}
    assert entry["static_paths"]["png"].endswith("test_figure.png")
    assert "png" in entry["checksums"]
    assert entry["n_valid"] == 1
