"""M1 -- AI Authorship Density (behavioral proxy for RQ1).

Definition
----------
For each team-semester and temporal cut c in {T1, T2, T3}, AI Authorship Density
is the *median share of commit authorship attributable to AI-pattern authors*
already computed by Phase 2 (`08_cross_evidence_engine.py` / `05_metric_engine.py`
lineage), i.e. `ai_author_share_median_tc`. This script does not recompute the
share; it re-exposes it as a tidy, cut-indexed trajectory table so it can be
plotted/tabulated against M2 (self-reported AI dependency) and M5 (repository
activity density) on a shared T1->T3 axis.

Formula (already applied upstream, restated here for traceability)
--------------------------------------------------------------
    ai_author_share_median_tc = median_over_authors(
        commits_by_author_in_cut_c / total_commits_in_cut_c
    )
    restricted to authors flagged as AI-pattern authors under
    `pipeline_config`'s AI-author window definition.

Source artifact (read-only, Phase 2, frozen)
---------------------------------------------
    data/analysis/integration_friction_metrics.parquet
    (grain: team-semester; produced by `05_metric_engine.py` /
    `08_cross_evidence_engine.py`, one row per ID_Equipe x Semestre)

Output
------
    paper_v8/data/m1_ai_authorship_density.csv
    columns: ID_Equipe, Semestre, cut, ai_author_share_median,
             ai_commit_n, ai_churn, ai_gini
"""

from __future__ import annotations

import pandas as pd
from _paths import ANALYSIS_DIR, ensure_output_dir

SOURCE_PATH = ANALYSIS_DIR / "integration_friction_metrics.parquet"
OUTPUT_PATH = ensure_output_dir() / "m1_ai_authorship_density.csv"
CUTS = ("t1", "t2", "t3")


def build_trajectory(frame: pd.DataFrame) -> pd.DataFrame:
    """Reshape the wide team-semester frame into a tidy team x cut trajectory."""
    rows = []
    for _, row in frame.iterrows():
        for cut in CUTS:
            rows.append(
                {
                    "ID_Equipe": row["ID_Equipe"],
                    "Semestre": row["Semestre"],
                    "cut": cut.upper(),
                    "ai_author_share_median": row.get(f"ai_author_share_median_{cut}"),
                    "ai_commit_n": row.get(f"ai_commit_n_{cut}"),
                    "ai_churn": row.get(f"ai_churn_{cut}"),
                    "ai_gini": row.get(f"ai_gini_{cut}"),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    frame = pd.read_parquet(SOURCE_PATH)
    trajectory = build_trajectory(frame)
    trajectory.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(trajectory)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
