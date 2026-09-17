from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


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
