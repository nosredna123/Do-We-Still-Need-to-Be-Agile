"""Generate leave-one-out influence map for small-n directional robustness."""

from __future__ import annotations

import json
import math
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_figures_dir, resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "rq3-influence-map-v1"
STEM = "rq3_influence_map"
RELATIONSHIP_CONTRACT_STEM = "rq3_influence_relationship_contract"
TEAM_KEY = ["ID_Equipe", "Semestre"]
MIN_N = 4
RELATIONSHIPS = [
    {
        "relationship_id": "planning_scope_to_t3_score",
        "task_4_2_requirement": "planning_t1_to_t3_score",
        "label": "Planning scope → T3 score",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "evaluator_score_t3",
    },
    {
        "relationship_id": "planning_scope_to_score_delta",
        "task_4_2_requirement": "planning_t1_to_delta_score_t3_minus_t1",
        "label": "Planning scope → score delta",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "delta_score_t3_minus_t1",
    },
    {
        "relationship_id": "planning_scope_to_final7_commits",
        "task_4_2_requirement": "planning_t1_to_final7_concentration",
        "label": "Planning scope → final-7 commits",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "final7_commit_share_pct",
    },
    {
        "relationship_id": "planning_scope_to_final7_clean_churn",
        "task_4_2_requirement": "planning_t1_to_final7_concentration",
        "label": "Planning scope → final-7 clean churn",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "final7_clean_churn_share_pct",
    },
    {
        "relationship_id": "final7_commits_to_t3_score",
        "task_4_2_requirement": "final7_concentration_to_t3_score",
        "label": "Final-7 commits → T3 score",
        "predictor": "final7_commit_share_pct",
        "outcome": "evaluator_score_t3",
    },
    {
        "relationship_id": "final7_clean_churn_to_t3_score",
        "task_4_2_requirement": "final7_concentration_to_t3_score",
        "label": "Final-7 clean churn → T3 score",
        "predictor": "final7_clean_churn_share_pct",
        "outcome": "evaluator_score_t3",
    },
    {
        "relationship_id": "final7_commits_to_score_delta",
        "task_4_2_requirement": "final7_concentration_to_delta_score",
        "label": "Final-7 commits → score delta",
        "predictor": "final7_commit_share_pct",
        "outcome": "delta_score_t3_minus_t1",
    },
    {
        "relationship_id": "final7_clean_churn_to_score_delta",
        "task_4_2_requirement": "final7_concentration_to_delta_score",
        "label": "Final-7 clean churn → score delta",
        "predictor": "final7_clean_churn_share_pct",
        "outcome": "delta_score_t3_minus_t1",
    },
    {
        "relationship_id": "regularity_to_score_delta",
        "task_4_2_requirement": "regularity_index_to_delta_score",
        "label": "Regularity index → score delta",
        "predictor": "regularity_index",
        "outcome": "delta_score_t3_minus_t1",
    },
    {
        "relationship_id": "technical_complexity_to_rework_churn",
        "task_4_2_requirement": "technical_complexity_t3_to_clean_churn_or_rework",
        "label": "Technical complexity → rework churn",
        "predictor": "technical_complexity_mean_t3",
        "outcome": "clean_rework_churn_t3",
    },
    {
        "relationship_id": "technical_complexity_to_rework_ratio",
        "task_4_2_requirement": "technical_complexity_t3_to_clean_churn_or_rework",
        "label": "Technical complexity → rework ratio",
        "predictor": "technical_complexity_mean_t3",
        "outcome": "clean_rework_ratio_t3",
        "filter_column": "baseline_eligible_for_rework_t3",
    },
    {
        "relationship_id": "planning_scope_to_rework_churn",
        "task_4_2_requirement": "planning_t1_to_rework_t3",
        "label": "Planning scope → rework churn",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "clean_rework_churn_t3",
    },
    {
        "relationship_id": "planning_scope_to_rework_ratio",
        "task_4_2_requirement": "planning_t1_to_rework_t3",
        "label": "Planning scope → rework ratio",
        "predictor": "planning_scope_log1p_t1",
        "outcome": "clean_rework_ratio_t3",
        "filter_column": "baseline_eligible_for_rework_t3",
    },
]
REQUIRED_BASE_COLUMNS = [
    *TEAM_KEY,
    "evaluator_score_t3",
    "delta_score_t3_minus_t1",
    "planning_scope_log1p_t1",
    "final7_commit_share_pct",
    "final7_clean_churn_share_pct",
]
REQUIRED_REGULARITY_COLUMNS = [*TEAM_KEY, "regularity_index"]
REQUIRED_REWORK_COLUMNS = [
    *TEAM_KEY,
    "clean_rework_churn_t3",
    "clean_rework_ratio_t3",
    "baseline_eligible_for_rework_t3",
]
REQUIRED_EVALUATOR_COLUMNS = [*TEAM_KEY, "temporal_marker", "technical_complexity_mean"]
REQUIRED_M9_COLUMNS = [
    "analysis_id",
    "predictor",
    "outcome",
    "removed_ID_Equipe",
    "removed_Semestre",
    "n_remaining",
    "spearman_rho",
]


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def _atomic_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    os.replace(temporary, path)


def _require_columns(frame: pd.DataFrame, columns: list[str], source: Path) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def _write_figure(figure: go.Figure, stem: str, figures_dir: Path) -> None:
    for extension in ("pdf", "svg", "png"):
        figure.write_image(
            figures_dir / f"{stem}.{extension}",
            scale=2 if extension == "png" else 1,
        )


def _spearman(frame: pd.DataFrame, predictor: str, outcome: str) -> float | None:
    subset = frame[[predictor, outcome]].dropna()
    if len(subset) < MIN_N:
        return None
    if subset[predictor].nunique(dropna=True) < 2 or subset[outcome].nunique(dropna=True) < 2:
        return None
    rho = subset[predictor].corr(subset[outcome], method="spearman")
    if pd.isna(rho):
        return None
    return float(rho)


def _sign(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "unavailable"
    if value > 0:
        return "positive"
    if value < 0:
        return "negative"
    return "zero"


def _load_analysis_frame(paths: dict[str, Path]) -> pd.DataFrame:
    base = pd.read_csv(paths["base"], dtype={"Semestre": str})
    regularity = pd.read_csv(paths["regularity"], dtype={"Semestre": str})
    rework = pd.read_csv(paths["rework"], dtype={"Semestre": str})
    evaluator = pd.read_parquet(paths["evaluator"])

    _require_columns(base, REQUIRED_BASE_COLUMNS, paths["base"])
    _require_columns(regularity, REQUIRED_REGULARITY_COLUMNS, paths["regularity"])
    _require_columns(rework, REQUIRED_REWORK_COLUMNS, paths["rework"])
    _require_columns(evaluator, REQUIRED_EVALUATOR_COLUMNS, paths["evaluator"])

    evaluator_t3 = evaluator.loc[evaluator["temporal_marker"].eq("T3"), [*TEAM_KEY, "technical_complexity_mean"]]
    evaluator_t3 = evaluator_t3.rename(columns={"technical_complexity_mean": "technical_complexity_mean_t3"})
    evaluator_t3["Semestre"] = evaluator_t3["Semestre"].astype(str)

    analysis = (
        base.merge(regularity[[*TEAM_KEY, "regularity_index"]], on=TEAM_KEY, validate="one_to_one")
        .merge(rework[REQUIRED_REWORK_COLUMNS], on=TEAM_KEY, validate="one_to_one")
        .merge(evaluator_t3, on=TEAM_KEY, validate="one_to_one")
        .sort_values(TEAM_KEY)
        .reset_index(drop=True)
    )
    if len(analysis) != 14:
        raise ValueError(f"Expected 14 team-semesters, got {len(analysis)}")
    return analysis


def _relationship_frame(analysis: pd.DataFrame, relation: dict[str, Any]) -> pd.DataFrame:
    frame = analysis.copy()
    filter_column = relation.get("filter_column")
    if filter_column:
        frame = frame.loc[frame[filter_column].astype(bool)].copy()
    return frame


def _influence_rows(analysis: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for relation in RELATIONSHIPS:
        frame = _relationship_frame(analysis, relation)
        full_rho = _spearman(frame, relation["predictor"], relation["outcome"])
        full_sign = _sign(full_rho)
        full_n = int(frame[[relation["predictor"], relation["outcome"]]].dropna().shape[0])
        full_status = "available" if full_rho is not None else "unavailable_n_lt_4_or_constant"
        for removed in analysis[TEAM_KEY].drop_duplicates().itertuples(index=False):
            removed_team = removed.ID_Equipe
            removed_semester = removed.Semestre
            loo = frame.loc[
                ~(frame["ID_Equipe"].eq(removed_team) & frame["Semestre"].eq(removed_semester))
            ].copy()
            loo_rho = _spearman(loo, relation["predictor"], relation["outcome"])
            loo_sign = _sign(loo_rho)
            if full_rho is None or loo_rho is None:
                rho_delta = None
                abs_rho_delta = None
            else:
                rho_delta = loo_rho - full_rho
                abs_rho_delta = abs(rho_delta)
            rows.append(
                {
                    "relationship_id": relation["relationship_id"],
                    "task_4_2_requirement": relation["task_4_2_requirement"],
                    "relationship_label": relation["label"],
                    "predictor": relation["predictor"],
                    "outcome": relation["outcome"],
                    "filter_column": relation.get("filter_column", ""),
                    "removed_ID_Equipe": removed_team,
                    "removed_Semestre": removed_semester,
                    "full_sample_n": full_n,
                    "loo_n": int(loo[[relation["predictor"], relation["outcome"]]].dropna().shape[0]),
                    "full_sample_rho": full_rho,
                    "loo_rho": loo_rho,
                    "rho_delta_from_full": rho_delta,
                    "abs_rho_delta_from_full": abs_rho_delta,
                    "full_sample_sign": full_sign,
                    "loo_sign": loo_sign,
                    "sign_changed": full_sign != loo_sign if full_sign != "unavailable" and loo_sign != "unavailable" else pd.NA,
                    "availability_status": full_status if loo_rho is not None else "loo_unavailable_n_lt_4_or_constant",
                    "inference_note": "descriptive_directional_robustness_not_confirmatory",
                }
            )
    return pd.DataFrame(rows)


def _relationship_contract(influence: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for relation in RELATIONSHIPS:
        subset = influence.loc[influence["relationship_id"].eq(relation["relationship_id"])]
        available = subset.loc[subset["availability_status"].eq("available")]
        full_rho = subset["full_sample_rho"].dropna()
        full_sign = subset["full_sample_sign"].dropna()
        sign_preservation_share = None
        if not available.empty:
            sign_preservation_share = float((available["full_sample_sign"] == available["loo_sign"]).mean())
        rows.append(
            {
                "task_4_2_requirement": relation["task_4_2_requirement"],
                "relationship_id": relation["relationship_id"],
                "relationship_label": relation["label"],
                "predictor": relation["predictor"],
                "outcome": relation["outcome"],
                "filter_column": relation.get("filter_column", ""),
                "full_sample_n": int(subset["full_sample_n"].max()),
                "leave_one_out_rows": int(len(subset)),
                "available_leave_one_out_rows": int(len(available)),
                "full_sample_rho": float(full_rho.iloc[0]) if not full_rho.empty else None,
                "full_sample_sign": full_sign.iloc[0] if not full_sign.empty else "unavailable",
                "loo_min_rho": float(available["loo_rho"].min()) if not available.empty else None,
                "loo_max_rho": float(available["loo_rho"].max()) if not available.empty else None,
                "max_abs_rho_delta_from_full": (
                    float(available["abs_rho_delta_from_full"].max()) if not available.empty else None
                ),
                "sign_preservation_share": sign_preservation_share,
                "availability_status": "available" if len(available) == len(subset) else "partially_or_fully_unavailable",
                "inference_note": "directional_robustness_not_confirmatory",
            }
        )
    return pd.DataFrame(rows)


def _build_influence_map(data: pd.DataFrame) -> go.Figure:
    data = data.copy()
    data["removed_team_semester"] = data["removed_ID_Equipe"].astype(str) + " · " + data["removed_Semestre"].astype(str)
    pivot = data.pivot(
        index="removed_team_semester",
        columns="relationship_label",
        values="rho_delta_from_full",
    )
    ordered_rows = sorted(pivot.index)
    ordered_columns = list(dict.fromkeys(data["relationship_label"].tolist()))
    pivot = pivot.reindex(index=ordered_rows, columns=ordered_columns)

    customdata = []
    lookup = data.set_index(["removed_team_semester", "relationship_label"])
    for row_label in ordered_rows:
        custom_row = []
        for column_label in ordered_columns:
            record = lookup.loc[(row_label, column_label)]
            custom_row.append(
                [
                    record["relationship_id"],
                    record["full_sample_rho"],
                    record["loo_rho"],
                    record["abs_rho_delta_from_full"],
                    record["full_sample_sign"],
                    record["loo_sign"],
                    record["availability_status"],
                ]
            )
        customdata.append(custom_row)

    finite_delta = data["rho_delta_from_full"].dropna().abs()
    max_delta = float(finite_delta.max()) if not finite_delta.empty else 1.0
    zmax = max(0.1, math.ceil(max_delta * 10) / 10)
    figure = go.Figure(
        data=go.Heatmap(
            z=pivot.to_numpy(dtype=float),
            x=[column.replace(" → ", "<br>→ ") for column in ordered_columns],
            y=ordered_rows,
            zmid=0,
            zmin=-zmax,
            zmax=zmax,
            colorscale="RdBu",
            colorbar={"title": "Δ Spearman<br>rho"},
            customdata=customdata,
            hovertemplate=(
                "Removed=%{y}<br>"
                "Relationship=%{x}<br>"
                "Full rho=%{customdata[1]:.3f}<br>"
                "LOO rho=%{customdata[2]:.3f}<br>"
                "|Δrho|=%{customdata[3]:.3f}<br>"
                "Full sign=%{customdata[4]}<br>"
                "LOO sign=%{customdata[5]}<br>"
                "Status=%{customdata[6]}"
                "<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        template="simple_white",
        width=1450,
        height=860,
        margin={"l": 145, "r": 55, "t": 95, "b": 300},
        title={
            "text": "Leave-one-out influence map for directional associations",
            "font": {"size": 22},
        },
        font={"size": 13, "family": "DejaVu Sans, Arial, sans-serif"},
        xaxis={"tickangle": -22, "automargin": True},
        yaxis={"title": "Removed team-semester", "automargin": True},
        annotations=[
            {
                "text": (
                    "Cells show change in descriptive Spearman rho after removing one team-semester. "
                    "Use as directional robustness evidence, not confirmatory significance."
                ),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.42,
                "xanchor": "left",
                "showarrow": False,
                "align": "left",
                "font": {"size": 12, "color": "#52525b"},
            }
        ],
    )
    return figure


def _legacy_m9_coverage(path: Path) -> dict[str, Any]:
    legacy = pd.read_csv(path, dtype={"removed_Semestre": str})
    _require_columns(legacy, REQUIRED_M9_COLUMNS, path)
    return {
        "rows": int(len(legacy)),
        "analysis_ids": sorted(legacy["analysis_id"].dropna().unique().tolist()),
        "relationship_count": int(legacy[["predictor", "outcome"]].drop_duplicates().shape[0]),
    }


def generate() -> dict[str, Any]:
    paper_v9 = resolve_paper_v9_dir()
    repo_root = paper_v9.parent
    figures_dir = resolve_figures_dir()
    metrics_dir = resolve_metrics_dir()
    paths = {
        "base": figures_dir / "rq2_score_trajectory_base_data.csv",
        "regularity": figures_dir / "rq2_operational_regularity_data.csv",
        "rework": metrics_dir / "m8_rework_magnitude.csv",
        "legacy_m9_leave_one_out": metrics_dir / "m9_leave_one_out_intervals.csv",
        "evaluator": repo_root / "data" / "lake" / "evaluator_team_cuts.parquet",
    }

    analysis = _load_analysis_frame(paths)
    influence = _influence_rows(analysis)
    if influence[["removed_ID_Equipe", "removed_Semestre"]].drop_duplicates().shape[0] != 14:
        raise ValueError("Influence map must cover 14 removed team-semesters")

    data_path = figures_dir / f"{STEM}_data.csv"
    relationship_contract_path = figures_dir / f"{RELATIONSHIP_CONTRACT_STEM}.csv"
    metadata_path = figures_dir / f"{STEM}.metadata.json"
    _atomic_csv(influence, data_path)
    relationship_contract = _relationship_contract(influence)
    _atomic_csv(relationship_contract, relationship_contract_path)
    _write_figure(_build_influence_map(influence), STEM, figures_dir)

    task_4_2_requirements = sorted(relationship_contract["task_4_2_requirement"].unique().tolist())
    metadata: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "artifact_id": STEM,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "data_path": str(data_path.relative_to(repo_root)),
        "data_sha256": compute_sha256(data_path),
        "relationship_contract_path": str(relationship_contract_path.relative_to(repo_root)),
        "relationship_contract_sha256": compute_sha256(relationship_contract_path),
        "figure_artifacts": [
            str((figures_dir / f"{STEM}.{extension}").relative_to(repo_root))
            for extension in ("pdf", "svg", "png")
        ],
        "inputs": {name: str(path.relative_to(repo_root)) for name, path in paths.items()},
        "input_sha256": {name: compute_sha256(path) for name, path in paths.items()},
        "legacy_m9_leave_one_out_coverage": _legacy_m9_coverage(paths["legacy_m9_leave_one_out"]),
        "coverage": {
            "removed_team_semesters": int(
                influence[["removed_ID_Equipe", "removed_Semestre"]].drop_duplicates().shape[0]
            ),
            "relationships": int(influence["relationship_id"].nunique()),
            "task_4_2_requirements": len(task_4_2_requirements),
            "rows": int(len(influence)),
        },
        "metric": "Descriptive Spearman rho; influence is leave-one-out rho minus full-sample rho.",
        "task_4_2_relationship_requirements": task_4_2_requirements,
        "task_4_2_relationship_contract": (
            "Each planned Fase 4.2 relationship category is represented by one or more operationalized "
            "relationships in rq3_influence_relationship_contract.csv."
        ),
        "unavailable_rule": f"Relationships or leave-one-out slices with n < {MIN_N} or constant values are marked unavailable.",
        "relationships": RELATIONSHIPS,
        "inference": "descriptive_directional_robustness_not_confirmatory",
        "limitations": [
            "Small-n leave-one-out maps are sensitivity diagnostics, not confirmatory statistical tests.",
            "Spearman direction can change when ties and influential team-semesters are removed.",
            "Rework ratio relationships are restricted to baseline-eligible team-semesters.",
            "Repository and evaluator measures remain observational proxies and do not establish causality.",
        ],
    }
    _atomic_json(metadata, metadata_path)
    return {
        "status": "generated",
        "data_path": str(data_path),
        "relationship_contract_path": str(relationship_contract_path),
        "metadata_path": str(metadata_path),
        "coverage": metadata["coverage"],
    }


def main() -> None:
    result = generate()
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
