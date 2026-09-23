"""M4 -- Repository Activity Density Trajectory (RQ2, quantitative side).

Definition
----------
For each Semestre (plus an "all" pooled cohort) and each temporal cut
c in {T1, T2, T3}, this metric summarizes the cross-team distribution of two
already-computed team-semester churn signals from `05_metric_engine.py`:

    cc_total_tc      -- total lines added + deleted in cut c
    cc_commit_n_tc   -- total commit count in cut c

    density_summary(s, c, metric) = summarize_numeric_distribution(
        {team_metric_value_tc : team in teams(s)}, scale_type="count", ...
    )

This reuses `pipeline_statistics.summarize_numeric_distribution` to produce a
mean/median/IQR trajectory comparable, cut-for-cut, against M5's qualitative
coordination-friction trajectory (RQ2's core "perception vs. reality" contrast:
repository activity density spikes late at T3, while qualitative friction is
already high at T1).

Source artifact (read-only, Phase 2, frozen)
---------------------------------------------
    data/analysis/code_churn_metrics.parquet
    (grain: team-semester; produced by `05_metric_engine.py`)

Output
------
    paper_v8/data/m4_repo_activity_density.csv
    columns: Semestre, cut, metric, n_total, n_valid, n_missing, mean, std,
             median, q1, q3, iqr
"""

from __future__ import annotations

import pandas as pd
from _paths import ANALYSIS_DIR, ensure_output_dir

from pipeline_statistics import summarize_numeric_distribution

SOURCE_PATH = ANALYSIS_DIR / "code_churn_metrics.parquet"
OUTPUT_PATH = ensure_output_dir() / "m4_repo_activity_density.csv"
CUTS = ("t1", "t2", "t3")
METRICS = ("cc_total", "cc_commit_n")
SCALE_TYPE = "count"
SCALE_VERSION = "v1"


def build_density_trajectory(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize cross-team churn distributions per cut, per Semestre and pooled."""
    rows: list[dict[str, object]] = []
    groups = [(semestre, group) for semestre, group in frame.groupby("Semestre", dropna=False)]
    groups.append(("all", frame))

    for semestre, group in groups:
        for cut in CUTS:
            for metric in METRICS:
                column = f"{metric}_{cut}"
                if column not in group.columns:
                    continue
                values = pd.to_numeric(group[column], errors="coerce")
                summary = summarize_numeric_distribution(
                    values, scale_type=SCALE_TYPE, scale_version=SCALE_VERSION
                )
                rows.append(
                    {"Semestre": semestre, "cut": cut.upper(), "metric": metric, **summary}
                )
    return pd.DataFrame(rows)


def main() -> None:
    frame = pd.read_parquet(SOURCE_PATH)
    trajectory = build_density_trajectory(frame)
    trajectory.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(trajectory)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
