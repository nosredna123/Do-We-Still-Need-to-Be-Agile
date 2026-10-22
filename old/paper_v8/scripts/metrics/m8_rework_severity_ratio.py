"""M8 -- Rework Severity Ratio (RQ3, destructive-rework operationalization).

Definition
----------
For each team-semester, file-provenance churn at T3 is already split by
`12_paper_signals_extractor.py` into:

    rework_churn_t3     -- lines added+deleted at T3 in files whose earliest
                            appearance was T1 or T2 (i.e. touching pre-existing,
                            previously-committed work: destructive rework)
    deferred_churn_t3   -- lines added+deleted at T3 in files whose earliest
                            appearance is T3 itself (new, deferred development)

This script derives two team-semester ratios from that split:

    total_churn_t3     = rework_churn_t3 + deferred_churn_t3
    rework_ratio_t3    = rework_churn_t3 / total_churn_t3   (undefined if total is 0)

`rework_ratio_t3` isolates *what fraction* of late-cycle churn was destructive
rework rather than raw volume, so it is comparable across teams of very
different absolute churn sizes.

Source artifact (read-only, paper_v4 signals pipeline, frozen)
-----------------------------------------------------------------
    paper_v4/advanced_metrics/outputs/team_level_signals.csv
    (grain: team-semester; produced by `12_paper_signals_extractor.py`)

Output
------
    paper_v8/data/m8_rework_severity_ratio.csv
    columns: ID_Equipe, Semestre, rework_churn_t3, deferred_churn_t3,
             total_churn_t3, rework_ratio_t3
"""

from __future__ import annotations

import pandas as pd
from _paths import PAPER_V4_OUTPUTS_DIR, ensure_output_dir

SOURCE_PATH = PAPER_V4_OUTPUTS_DIR / "team_level_signals.csv"
OUTPUT_PATH = ensure_output_dir() / "m8_rework_severity_ratio.csv"


def build_rework_severity_ratio(frame: pd.DataFrame) -> pd.DataFrame:
    """Derive total churn and rework ratio from the rework/deferred churn split."""
    table = frame[["ID_Equipe", "Semestre", "rework_churn_t3", "deferred_churn_t3"]].copy()
    table["total_churn_t3"] = table["rework_churn_t3"] + table["deferred_churn_t3"]
    table["rework_ratio_t3"] = table["rework_churn_t3"] / table["total_churn_t3"].where(
        table["total_churn_t3"] != 0
    )
    return table


def main() -> None:
    frame = pd.read_csv(SOURCE_PATH, dtype={"Semestre": str})
    table = build_rework_severity_ratio(frame)
    table.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(table)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
