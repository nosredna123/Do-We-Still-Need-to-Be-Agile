"""M7 -- T1 Planning-Omission Rate (RQ3, formalizes the abstract's 55% claim).

Definition
----------
For each cohort (Semestre), the T1 Planning-Omission Rate is the share of
team-semesters whose T1 Planning-Quality Score (M6) is missing -- i.e. the
team made zero commits before the T1 cut, so there was no text for the LLM to
evaluate, and therefore no observable substantive early architectural
alignment:

    planning_omission_rate(s) = |{ team in teams(s) : t1_planning_score(team, s) is NaN }|
                                 / |teams(s)|

This is a deterministic count/percentage over M6's output; no LLM calls are
issued.

Source artifact (read-only, paper_v4 signals pipeline, frozen)
-----------------------------------------------------------------
    paper_v4/advanced_metrics/outputs/team_level_signals.csv
    (grain: team-semester; produced by `12_paper_signals_extractor.py`)

Output
------
    paper_v8/data/m7_planning_omission_rate.csv
    columns: Semestre, n_teams, n_omitted, omission_rate
"""

from __future__ import annotations

import pandas as pd
from _paths import PAPER_V4_OUTPUTS_DIR, ensure_output_dir

SOURCE_PATH = PAPER_V4_OUTPUTS_DIR / "team_level_signals.csv"
OUTPUT_PATH = ensure_output_dir() / "m7_planning_omission_rate.csv"


def build_omission_rate(frame: pd.DataFrame) -> pd.DataFrame:
    """Count and rate T1 planning-score omissions per Semestre, plus a pooled 'all' row."""
    rows: list[dict[str, object]] = []
    groups = [(semestre, group) for semestre, group in frame.groupby("Semestre", dropna=False)]
    groups.append(("all", frame))

    for semestre, group in groups:
        n_teams = int(len(group))
        n_omitted = int(group["t1_planning_score"].isna().sum())
        rows.append(
            {
                "Semestre": semestre,
                "n_teams": n_teams,
                "n_omitted": n_omitted,
                "omission_rate": n_omitted / n_teams if n_teams else None,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    frame = pd.read_csv(SOURCE_PATH, dtype={"Semestre": str})
    table = build_omission_rate(frame)
    table.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(table)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
