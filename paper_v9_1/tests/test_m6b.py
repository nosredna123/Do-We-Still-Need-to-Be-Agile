from __future__ import annotations

import json
from pathlib import Path


def test_m6b_real_outputs_have_validated_coverage_and_provenance() -> None:
    metrics = Path("paper_v9/data/metrics")
    records = json.loads((metrics / "m6b_llm_planning_content.json").read_text(encoding="utf-8"))
    metadata = json.loads((metrics / "m6_llm_planning_content.metadata.json").read_text(encoding="utf-8"))

    assert len(records) == 14
    assert sum(record["status"] == "success" for record in records) == 9
    assert sum(record["status"] == "unavailable_not_measured" for record in records) == 5
    assert metadata["status"] == "success"
    assert metadata["gate_status"] == "approved_human_review"
    assert metadata["llm_calls_required"] is True
    assert metadata["model"] == "gpt-4o-mini"
    assert metadata["temperature"] == 0.0

    for record in records:
        if record["status"] == "unavailable_not_measured":
            assert record["input_subjects"] == []
            assert record["insufficient_evidence"] == [{"category": "all", "reason": "no_t1_commit_subjects"}]
            continue
        parsed = record["parsed_response"]
        assert set(parsed) == {
            "planning_evidence_present", "goals", "architecture_or_design",
            "task_decomposition", "risk_or_dependency", "evidence_quotes",
            "insufficient_evidence",
        }
        subjects = {item["commit_hash"]: item["subject"] for item in record["input_subjects"]}
        quote_ids = {quote["quote_id"] for quote in parsed["evidence_quotes"]}
        assert len(quote_ids) == len(parsed["evidence_quotes"])
        for quote in parsed["evidence_quotes"]:
            assert quote["commit_hash"] in subjects
            assert quote["quote"] in subjects[quote["commit_hash"]]
        for category in ("goals", "architecture_or_design", "task_decomposition", "risk_or_dependency"):
            for item in parsed[category]:
                assert set(item["evidence_quote_ids"]).issubset(quote_ids)


def test_m6b_review_sample_exists_and_gate_is_pending() -> None:
    sample = Path("paper_v9/data/metrics/m6b_llm_planning_sample_for_review.md")
    assert sample.is_file()
    text = sample.read_text(encoding="utf-8")
    assert "human review approved" in text
    assert "Every quote is an exact substring" in text
    assert "M6b fields enter M9 separately" in text
