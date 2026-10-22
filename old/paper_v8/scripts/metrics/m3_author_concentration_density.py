"""M3 -- Pre-Deadline Author-Concentration Density (integration-pressure proxy for RQ2).

Definition
----------
IMPORTANT CORRECTION (2026-09-23): this metric was previously mislabeled
"AI Authorship Density". The underlying `ai_*` columns in
`integration_friction_metrics.parquet` contain NO tool-identity detection --
there is no regex, keyword list, or author-name/email pattern anywhere in the
pipeline that classifies a commit author as "using AI". They are a generic
per-author commit-count concentration signal, computed only over the raw
`ID_Autor_Local` field, restricted to a fixed 72-hour window immediately
before each team's T3 checkpoint. The column-name prefix "ai_" is therefore a
misnomer inherited from the source pipeline; this script (and the paper)
must describe it honestly as an integration-pressure / author-concentration
proxy, not as evidence of AI tool adoption.

For each team-semester and temporal cut c in {T1, T2, T3}, this metric is the
median, across commit authors, of each author's share of commits in the
72-hour window immediately preceding cut c's T3 boundary:

    AuthorConcentration(i, s, c) = median_over_authors_a(
        commits(a, i, s, window_before_c) / total_commits(i, s, window_before_c)
    )

alongside the Gini coefficient of the same per-author commit-count
distribution (standard Gini formula over sorted commit counts), which
summarizes how unevenly commit volume was distributed across teammates right
before the deadline.

Source artifact (read-only, frozen)
---------------------------------------------
    data/analysis/integration_friction_metrics.parquet
    (grain: team-semester; one row per ID_Equipe x Semestre; the underlying
    per-author commit counts/shares/Gini are computed directly from raw
    `ID_Autor_Local` commit counts in data/lake/git_commits.parquet, with no
    AI/human classification applied)

Output
------
    paper_v8/data/m3_author_concentration_density.csv
    columns: ID_Equipe, Semestre, cut, author_share_median,
             commit_n, churn, author_gini
"""

from __future__ import annotations

import pandas as pd
from _paths import ANALYSIS_DIR, ensure_output_dir

SOURCE_PATH = ANALYSIS_DIR / "integration_friction_metrics.parquet"
OUTPUT_PATH = ensure_output_dir() / "m3_author_concentration_density.csv"
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
                    "author_share_median": row.get(f"ai_author_share_median_{cut}"),
                    "commit_n": row.get(f"ai_commit_n_{cut}"),
                    "churn": row.get(f"ai_churn_{cut}"),
                    "author_gini": row.get(f"ai_gini_{cut}"),
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

