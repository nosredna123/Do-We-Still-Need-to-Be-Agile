from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from paper_v9.scripts.results.generate_nonoverlapping_phase_activity import (
    PHASE_CLEAN_CHURN_SHARE_STEM,
    PHASE_COMMIT_SHARE_STEM,
    PHASE_LABELS,
    PHASE_STEM,
    STEM,
    WEEK_BIN_LABELS,
    WEEKLY_STEM,
    generate,
)


def test_nonoverlapping_phase_activity_generates_expected_bins() -> None:
    result = generate()

    assert result["status"] == "generated"
    assert result["coverage"]["team_semesters"] == 14
    assert result["coverage"]["weekly_rows"] == 14 * len(WEEK_BIN_LABELS)
    assert result["coverage"]["phase_rows"] == 14 * len(PHASE_LABELS)

    figures = Path("paper_v9/figures")
    weekly = pd.read_csv(figures / f"{WEEKLY_STEM}_data.csv", dtype={"Semestre": str})
    phase = pd.read_csv(figures / f"{PHASE_STEM}_data.csv", dtype={"Semestre": str})
    metadata = json.loads((figures / f"{STEM}.metadata.json").read_text(encoding="utf-8"))

    assert weekly[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
    assert phase[["ID_Equipe", "Semestre"]].drop_duplicates().shape[0] == 14
    assert set(weekly["week_bin"]) == set(WEEK_BIN_LABELS)
    assert set(phase["phase"]) == set(PHASE_LABELS)
    assert weekly.groupby(["ID_Equipe", "Semestre"]).size().eq(len(WEEK_BIN_LABELS)).all()
    assert phase.groupby(["ID_Equipe", "Semestre"]).size().eq(len(PHASE_LABELS)).all()
    assert phase[["commit_share_pct", "clean_churn_share_pct"]].apply(
        lambda column: column.between(0, 100).all()
    ).all()
    assert phase.groupby(["ID_Equipe", "Semestre"])["commit_share_pct"].sum().round(6).between(99.999, 100.001).all()

    assert metadata["contract_version"] == "rq2-nonoverlapping-phase-activity-v1"
    assert metadata["inference"] == "descriptive_nonoverlapping_activity_bins_not_causal"
    assert metadata["coverage"]["phase_rows"] == 14 * len(PHASE_LABELS)
    assert metadata["coverage"]["weekly_rows"] == 14 * len(WEEK_BIN_LABELS)
    assert "Repository activity does not observe off-repository work." in metadata["limitations"]

    for stem in (PHASE_COMMIT_SHARE_STEM, PHASE_CLEAN_CHURN_SHARE_STEM):
        assert all((figures / f"{stem}.{extension}").is_file() for extension in ("pdf", "svg", "png"))
