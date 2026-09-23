"""M9 -- Planning Quality vs. Rework / Evaluator-Outcome Association (RQ3, primary).

Definition
----------
This metric joins three already-computed signals at team-semester grain:

    t1_planning_score          -- M6 (LLM 1-10 over T1 commit messages)
    rework_churn_t3,
    rework_ratio_t3             -- M8 (file-provenance destructive rework at T3)
    project_progress_mean_t3,
    scope_applicability_mean_t3,
    technical_complexity_mean_t3,
    engagement_participation_mean_t3
                                -- independent, blind-scored evaluator outcomes at T3

and reports two descriptive (non-causal) views, given n<=14 team-semesters:

(a) Spearman rank correlation rho(t1_planning_score, Y) for each outcome
    Y in {rework_churn_t3, rework_ratio_t3, project_progress_mean_t3,
    scope_applicability_mean_t3, technical_complexity_mean_t3,
    engagement_participation_mean_t3}, computed with `scipy.stats.spearmanr`
    over the subset of teams with a non-missing t1_planning_score.

(b) A median-split group contrast: teams with an available t1_planning_score
    are split into "low" (<= median) and "high" (> median) planning-quality
    groups; each outcome Y is summarized per group with
    `pipeline_statistics.summarize_numeric_distribution`. Teams with a missing
    t1_planning_score (see M7) are excluded from this split and are reported
    separately -- they are not assigned to "low" by fabrication.

All statistics here are exploratory/descriptive, consistent with this repo's
own "conditional-go" verdict on primary Phase 2 tests
(`data/analysis/artifact_reports/00_consolidated_audit.md`,
`docs/02a.artifact-narrative-audit.md`): no causal claims are licensed by n<=14.

Source artifacts (read-only, frozen)
-------------------------------------
    paper_v4/advanced_metrics/outputs/team_level_signals.csv
    (grain: team-semester; produced by `12_paper_signals_extractor.py`)
    data/analysis/cross_evidence/datasets/evaluator_outcome_metrics.parquet
    (grain: team-semester; produced by `08_cross_evidence_engine.py`)

Output
------
    paper_v8/data/m9_planning_vs_rework_association.csv
    columns: outcome, n, spearman_rho, spearman_p
    paper_v8/data/m9_planning_vs_rework_association_group_contrast.csv
    columns: planning_group, outcome, n_total, n_valid, n_missing, mean, std,
             median, q1, q3, iqr
"""

from __future__ import annotations

import pandas as pd
from scipy.stats import spearmanr

from _paths import CROSS_EVIDENCE_DATASETS_DIR, PAPER_V4_OUTPUTS_DIR, ensure_output_dir
from m8_rework_severity_ratio import build_rework_severity_ratio
from pipeline_statistics import summarize_numeric_distribution

TEAM_SIGNALS_PATH = PAPER_V4_OUTPUTS_DIR / "team_level_signals.csv"
EVALUATOR_OUTCOME_PATH = CROSS_EVIDENCE_DATASETS_DIR / "evaluator_outcome_metrics.parquet"
CORRELATION_OUTPUT_PATH = ensure_output_dir() / "m9_planning_vs_rework_association.csv"
GROUP_CONTRAST_OUTPUT_PATH = ensure_output_dir() / "m9_planning_vs_rework_association_group_contrast.csv"

OUTCOME_COLUMNS = (
    "rework_churn_t3",
    "rework_ratio_t3",
    "project_progress_mean_t3",
    "scope_applicability_mean_t3",
    "technical_complexity_mean_t3",
    "engagement_participation_mean_t3",
)
SCALE_TYPE = "evaluator_or_churn_outcome"
SCALE_VERSION = "v1"


def build_joined_frame() -> pd.DataFrame:
    """Join M6/M8-derived team signals with T3 evaluator outcome scores."""
    team_signals = pd.read_csv(TEAM_SIGNALS_PATH, dtype={"Semestre": str})
    team_signals = build_rework_severity_ratio(team_signals)
    team_signals = team_signals.merge(
        pd.read_csv(TEAM_SIGNALS_PATH, dtype={"Semestre": str})[["ID_Equipe", "Semestre", "t1_planning_score"]],
        on=["ID_Equipe", "Semestre"],
        how="left",
    )

    evaluator_outcomes = pd.read_parquet(EVALUATOR_OUTCOME_PATH)
    outcome_columns = ["ID_Equipe", "Semestre"] + [
        column for column in OUTCOME_COLUMNS if column in evaluator_outcomes.columns
    ]
    evaluator_outcomes = evaluator_outcomes[outcome_columns]

    return team_signals.merge(evaluator_outcomes, on=["ID_Equipe", "Semestre"], how="left")


def build_correlations(joined: pd.DataFrame) -> pd.DataFrame:
    """Spearman rho(t1_planning_score, outcome) for each outcome, over non-missing pairs."""
    scored = joined.dropna(subset=["t1_planning_score"])
    rows: list[dict[str, object]] = []
    for outcome in OUTCOME_COLUMNS:
        if outcome not in scored.columns:
            continue
        pair = scored[["t1_planning_score", outcome]].dropna()
        n = int(len(pair))
        if n < 3:
            rows.append({"outcome": outcome, "n": n, "spearman_rho": None, "spearman_p": None})
            continue
        rho, p_value = spearmanr(pair["t1_planning_score"], pair[outcome])
        rows.append({"outcome": outcome, "n": n, "spearman_rho": float(rho), "spearman_p": float(p_value)})
    return pd.DataFrame(rows)


def build_group_contrast(joined: pd.DataFrame) -> pd.DataFrame:
    """Median-split low/high planning-quality group contrast per outcome."""
    scored = joined.dropna(subset=["t1_planning_score"]).copy()
    median_score = scored["t1_planning_score"].median()
    scored["planning_group"] = scored["t1_planning_score"].apply(
        lambda value: "low" if value <= median_score else "high"
    )

    rows: list[dict[str, object]] = []
    for group_name, group in scored.groupby("planning_group"):
        for outcome in OUTCOME_COLUMNS:
            if outcome not in group.columns:
                continue
            values = pd.to_numeric(group[outcome], errors="coerce")
            summary = summarize_numeric_distribution(
                values, scale_type=SCALE_TYPE, scale_version=SCALE_VERSION
            )
            rows.append({"planning_group": group_name, "outcome": outcome, **summary})
    return pd.DataFrame(rows)


def main() -> None:
    joined = build_joined_frame()
    correlations = build_correlations(joined)
    group_contrast = build_group_contrast(joined)
    correlations.to_csv(CORRELATION_OUTPUT_PATH, index=False)
    group_contrast.to_csv(GROUP_CONTRAST_OUTPUT_PATH, index=False)
    print(f"Wrote {len(correlations)} rows to {CORRELATION_OUTPUT_PATH}")
    print(f"Wrote {len(group_contrast)} rows to {GROUP_CONTRAST_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
