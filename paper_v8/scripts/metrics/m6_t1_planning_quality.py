"""M6 -- T1 Planning-Quality Score (RQ3, primary predictor).

Definition
----------
For each team-semester, the T1 Planning-Quality Score is an LLM-assigned
integer in [1, 10] reflecting how clear, specific, and coherent the team's
architectural/planning intent was, judged solely from the text of their T1
commit messages (the "planning" prompt in
`paper_v4/advanced_metrics/llm_prompts.py`). A missing score means the team
had zero T1 commits to evaluate (see M7, the Planning-Omission Rate, for the
formal treatment of this case).

    t1_planning_score(team, semester) in {1, ..., 10} union {NaN}

This script performs no re-scoring; it re-exposes the value with an explicit
label for downstream joins (M8, M9).

Source artifact (read-only, paper_v4 signals pipeline, frozen)
-----------------------------------------------------------------
    paper_v4/advanced_metrics/outputs/team_level_signals.csv
    (grain: team-semester; produced by `12_paper_signals_extractor.py`)

Output
------
    paper_v8/data/m6_t1_planning_quality.csv
    columns: ID_Equipe, Semestre, t1_planning_score
"""

from __future__ import annotations

import pandas as pd
from _paths import PAPER_V4_OUTPUTS_DIR, ensure_output_dir

SOURCE_PATH = PAPER_V4_OUTPUTS_DIR / "team_level_signals.csv"
OUTPUT_PATH = ensure_output_dir() / "m6_t1_planning_quality.csv"


def main() -> None:
    frame = pd.read_csv(SOURCE_PATH, dtype={"Semestre": str})
    table = frame[["ID_Equipe", "Semestre", "t1_planning_score"]].copy()
    table.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(table)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
