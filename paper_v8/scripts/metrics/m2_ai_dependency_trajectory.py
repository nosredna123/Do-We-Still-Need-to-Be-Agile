"""M2 -- Self-Reported AI-Dependency Trajectory (perception proxy for RQ1).

Definition
----------
For each Semestre x temporal_marker cohort-cut, the composite AI-Dependency
Score is the unweighted mean, across the six already LLM-coded question
families, of their per-cut mean `ai_dependency_score` (each family scored on
an ordinal 0-4 scale by `04_nlp_qualitative_miner.py`):

    ai_dependency_composite(s, c) = (1/6) * sum_{q in Q} mean_ai_dependency_score(q, s, c)

    where Q = {student_ai_benefit, student_ai_career_impact_5y,
               student_autonomy_tool_dependency, student_career_expectation,
               student_project_challenges, student_project_feeling}

No new LLM calls are issued: this is a deterministic mean-of-means over
already-scored, already-aggregated Phase 2 columns.

Grain constraint
----------------
`data/analysis/textual_cut_signals.parquet` carries `Semestre` and
`temporal_marker` only (no `ID_Equipe`) -- student survey responses are not
team-attributable. This composite is therefore cohort-level, not team-level,
which must be stated explicitly wherever it is used in the paper.

Source artifact (read-only, Phase 2, frozen)
---------------------------------------------
    data/analysis/textual_cut_signals.parquet
    (grain: Semestre x temporal_marker; produced by
    `04_nlp_qualitative_miner.py` aggregation stage)

Output
------
    paper_v8/data/m2_ai_dependency_trajectory.csv
    columns: Semestre, temporal_marker, ai_dependency_composite_mean,
             n_question_families_available
"""

from __future__ import annotations

import pandas as pd
from _paths import ANALYSIS_DIR, ensure_output_dir

SOURCE_PATH = ANALYSIS_DIR / "textual_cut_signals.parquet"
OUTPUT_PATH = ensure_output_dir() / "m2_ai_dependency_trajectory.csv"

QUESTION_FAMILIES = (
    "student_ai_benefit",
    "student_ai_career_impact_5y",
    "student_autonomy_tool_dependency",
    "student_career_expectation",
    "student_project_challenges",
    "student_project_feeling",
)


def build_composite(frame: pd.DataFrame) -> pd.DataFrame:
    """Average the six per-family ai_dependency_score means into one composite per cut."""
    mean_columns = [f"{family}_ai_dependency_score_mean" for family in QUESTION_FAMILIES]
    missing = [column for column in mean_columns if column not in frame.columns]
    if missing:
        raise ValueError(f"textual_cut_signals.parquet is missing expected columns: {missing}")

    result = frame[["Semestre", "temporal_marker"]].copy()
    result["ai_dependency_composite_mean"] = frame[mean_columns].mean(axis=1, skipna=True)
    result["n_question_families_available"] = frame[mean_columns].notna().sum(axis=1)
    return result


def main() -> None:
    frame = pd.read_parquet(SOURCE_PATH)
    composite = build_composite(frame)
    composite.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(composite)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
