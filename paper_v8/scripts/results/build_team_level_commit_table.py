"""Build the team-level repository activity table reported in RQ3.

The output preserves team-semester identity and distinguishes an undefined
planning score from the floor value used only in M9's sensitivity analysis.
"""

from __future__ import annotations

import pandas as pd

from _paths import DATA_DIR, PROJECT_ROOT, ensure_results_output_dir

ACTIVITY_PATH = PROJECT_ROOT / "data" / "analysis" / "code_churn_metrics.parquet"
PLANNING_PATH = DATA_DIR / "m6_t1_planning_quality.csv"
REWORK_PATH = DATA_DIR / "m8_rework_severity_ratio.csv"
OUTPUT_PATH = ensure_results_output_dir() / "team_level_commit_rework.csv"
KEYS = ["ID_Equipe", "Semestre"]
CUTS = ("T1", "T2", "T3")


def first_active_window(row: pd.Series) -> str:
    """Return the first temporal window containing at least one commit."""
    for cut in CUTS:
        if row[f"commits_{cut.lower()}"] > 0:
            return cut
    return "none"


def build_table() -> pd.DataFrame:
    """Join activity, observed planning evidence, and T3 churn by team-semester."""
    activity = pd.read_parquet(ACTIVITY_PATH)
    activity["Semestre"] = activity["Semestre"].astype(str)
    activity = activity[
        KEYS + ["cc_commit_n_t1", "cc_commit_n_t2", "cc_commit_n_t3"]
    ].rename(
        columns={
            "cc_commit_n_t1": "commits_t1",
            "cc_commit_n_t2": "commits_t2",
            "cc_commit_n_t3": "commits_t3",
        }
    )

    planning = pd.read_csv(PLANNING_PATH, dtype={"Semestre": str})
    rework = pd.read_csv(REWORK_PATH, dtype={"Semestre": str})
    table = activity.merge(planning, on=KEYS, how="left", validate="one_to_one")
    table = table.merge(rework, on=KEYS, how="left", validate="one_to_one")
    table["first_active_window"] = table.apply(first_active_window, axis=1)
    table["planning_evidence"] = table["t1_planning_score"].apply(
        lambda value: "omitted" if pd.isna(value) else "observed"
    )
    table["team_semester"] = table["Semestre"] + "/" + table["ID_Equipe"]

    columns = [
        "team_semester",
        "commits_t1",
        "commits_t2",
        "commits_t3",
        "first_active_window",
        "planning_evidence",
        "t1_planning_score",
        "rework_churn_t3",
        "deferred_churn_t3",
        "total_churn_t3",
        "rework_ratio_t3",
    ]
    return table[columns].sort_values("team_semester").reset_index(drop=True)


def main() -> None:
    table = build_table()
    table.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(table)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()