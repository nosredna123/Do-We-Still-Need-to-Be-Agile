from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parent.parent


def load_miner():
    spec = importlib.util.spec_from_file_location(
        "phase2_catalog_miner", ROOT / "04_nlp_qualitative_miner.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def registry(*, strategy: str = "coalesce_without_conflict") -> dict[str, dict[str, object]]:
    return {
        "project_feeling": {
            "question_id": "project_feeling",
            "construct": "cognitive_load",
            "aliases": ["Feeling", "Feeling.1"],
            "required_scopes": [{"Semestre": "2025.2", "temporal_marker": "T1", "requirement": "required"}],
            "duplicate_strategy": strategy,
            "conflict_strategy": "resolve_automatically" if strategy == "prefer_highest_suffix" else "reject_on_conflict",
            "registry_version": "test-v1",
        }
    }


def base_frame(**values: object) -> pd.DataFrame:
    row = {
        "Semestre": "2025.2",
        "temporal_marker": "T1",
        "source_file": "students.csv",
        "source_type": "student_response",
        **values,
    }
    return pd.DataFrame([row])


def test_catalog_student_prompts_preserves_lineage_and_audit() -> None:
    miner = load_miner()
    result = miner.catalog_student_prompts(
        base_frame(Feeling="  sobrecarregado   hoje "), registry()
    )

    assert result.to_dict("records") == [
        {
            "student_response_id": "students.csv:0",
            "Semestre": "2025.2",
            "temporal_marker": "T1",
            "source_file": "students.csv",
            "question_id": "project_feeling",
            "construct": "cognitive_load",
            "original_column": "Feeling",
            "answer_text": "sobrecarregado   hoje",
            "duplicate_strategy": "coalesce_without_conflict",
            "conflict_resolution": "none",
            "question_registry_version": "test-v1",
        }
    ]
    assert result.attrs["catalog_audit"][0]["aliases_used"] == ["Feeling"]


def test_catalog_accepts_equal_duplicate_aliases_after_light_normalization() -> None:
    miner = load_miner()
    result = miner.catalog_student_prompts(
        base_frame(Feeling="mesma resposta", **{"Feeling.1": "  mesma   resposta "}),
        registry(),
    )

    assert len(result) == 1
    assert result.iloc[0]["original_column"] == "Feeling"
    assert result.attrs["catalog_audit"][0]["conflicts_detected"] == 0


def test_catalog_rejects_conflicting_aliases() -> None:
    miner = load_miner()
    with pytest.raises(ValueError, match="conflicting aliases"):
        miner.catalog_student_prompts(
            base_frame(Feeling="resposta A", **{"Feeling.1": "resposta B"}),
            registry(),
        )


def test_catalog_rejects_required_question_without_alias_or_answer() -> None:
    miner = load_miner()
    with pytest.raises(ValueError, match="required"):
        miner.catalog_student_prompts(base_frame(), registry())

    frame = base_frame(Feeling=None)
    with pytest.raises(ValueError, match="required"):
        miner.catalog_student_prompts(frame, registry())


def test_catalog_rejects_invalid_registry_definition() -> None:
    miner = load_miner()
    invalid = registry()
    del invalid["project_feeling"]["registry_version"]
    with pytest.raises(ValueError, match="registry_version"):
        miner.catalog_student_prompts(base_frame(Feeling="ok"), invalid)


def test_catalog_supports_highest_suffix_strategy_and_records_overwrite() -> None:
    miner = load_miner()
    result = miner.catalog_student_prompts(
        base_frame(Feeling="old", **{"Feeling.1": "new"}),
        registry(strategy="prefer_highest_suffix"),
    )

    assert result.iloc[0]["answer_text"] == "new"
    assert result.iloc[0]["original_column"] == "Feeling.1"
    assert result.attrs["catalog_audit"][0]["overwritten_count"] == 1


def test_write_student_prompt_catalog_is_private_and_resumable(tmp_path: Path) -> None:
    miner = load_miner()
    prompts = miner.catalog_student_prompts(
        base_frame(Feeling="resposta privada"), registry()
    )
    output = tmp_path / ".private" / "student_prompt_catalog.parquet"

    miner.write_student_prompt_catalog(
        prompts,
        output,
        source_checksum="checksum",
        options={"registry_version": "test-v1"},
    )

    assert output.exists()
    assert output.parent.name == ".private"
    assert "resposta privada" in pd.read_parquet(output).loc[0, "answer_text"]
    metadata = json.loads(
        output.with_name(f"{output.name}.metadata.json").read_text(encoding="utf-8")
    )
    assert metadata == {
        "contract_version": "student-prompt-catalog-v1",
        "input_checksum": "checksum",
        "options": {"registry_version": "test-v1"},
        "status": "success",
    }