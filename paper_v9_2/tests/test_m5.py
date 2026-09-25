from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.metrics.m5_coordination_evidence import generate


def test_m5_real_outputs_are_global_descriptive_evidence() -> None:
    result = generate(force=True)
    assert result["status"] == "generated"
    metrics = Path("paper_v9/data/metrics")
    density = pd.read_csv(metrics / "m5_marker_density.csv")
    composition = pd.read_csv(metrics / "m5_marker_composition.csv")
    coverage = pd.read_csv(metrics / "m5_corpus_coverage.csv")
    audit = pd.read_csv(metrics / "m5_evidence_audit_trail.csv")
    lexicon = json.loads((metrics / "m5_lexicon.json").read_text(encoding="utf-8"))
    metadata = json.loads((metrics / "m5_coordination_evidence.metadata.json").read_text(encoding="utf-8"))

    assert density["temporal_marker"].tolist() == ["T1", "T2", "T3"]
    assert density["transcript_chunk_n"].tolist() == [35, 37, 28]
    assert density["source_session_n"].eq(2).all()
    assert density["token_n"].gt(0).all()
    assert density["friction_marker_n"].ge(0).all()
    assert density["friction_marker_density_per_1k_tokens"].notna().all()
    assert set(composition["friction_subtype"]) == {"alignment", "handoff", "integration", "blocker", "rework"}
    assert composition.groupby("temporal_marker")["marker_n"].sum().equals(
        density.set_index("temporal_marker")["friction_marker_n"]
    )
    assert coverage["observed_semesters"].astype(str).eq("2025.2").all()
    assert len(audit) > 0
    assert lexicon["version"] == "m5-friction-lexicon-pt-v1"
    assert metadata["status"] == "success"
    assert metadata["rq"] == "RQ2"
    assert metadata["llm_calls_required"] is False
    assert metadata["inference"] == "descriptive_only"


def test_m5_resume_reuses_current_outputs() -> None:
    result = generate()
    assert result["status"] == "resumed"