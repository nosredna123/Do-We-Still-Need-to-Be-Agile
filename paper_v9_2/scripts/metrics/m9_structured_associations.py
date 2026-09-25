"""Generate descriptive, stratified M9 associations for RQ3."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

CONTRACT_VERSION = "m9-structured-associations-v1"
TEAM_KEY = ["ID_Equipe", "Semestre"]
PREDICTORS = ["pi_file_count_t1", "planning_scope_log1p_t1"]
M6B_PREDICTORS = ["m6b_planning_evidence_present", "m6b_goals_n", "m6b_architecture_or_design_n", "m6b_task_decomposition_n", "m6b_risk_or_dependency_n", "m6b_evidence_quotes_n"]
OUTCOMES = ["clean_rework_churn_t3", "clean_rework_ratio_t3", "project_progress_mean_t3", "scope_applicability_mean_t3", "technical_complexity_mean_t3", "engagement_participation_mean_t3"]


def _atomic_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def _atomic_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str), encoding="utf-8")
    os.replace(temporary, path)


def _association_table(frame: pd.DataFrame, outcomes: list[str], analysis_id: str, predictors: list[str] = PREDICTORS) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for predictor in predictors:
        for outcome in outcomes:
            pair = frame[[predictor, outcome]].dropna()
            rho = p_value = None
            if len(pair) >= 3 and pair[predictor].nunique() >= 2 and pair[outcome].nunique() >= 2:
                rho, p_value = spearmanr(pair[predictor], pair[outcome])
            rows.append({"analysis_id": analysis_id, "predictor": predictor, "outcome": outcome, "n": int(len(pair)), "spearman_rho": None if rho is None else float(rho), "spearman_p_exploratory": None if p_value is None else float(p_value)})
    return pd.DataFrame(rows)


def _leave_one_out(frame: pd.DataFrame, outcomes: list[str], analysis_id: str) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for predictor in PREDICTORS:
        for outcome in outcomes:
            pair = frame[TEAM_KEY + [predictor, outcome]].dropna()
            for removed in pair[TEAM_KEY].to_dict("records"):
                remaining = pair.loc[~((pair["ID_Equipe"] == removed["ID_Equipe"]) & (pair["Semestre"] == removed["Semestre"]))]
                rho = p_value = None
                if len(remaining) >= 3 and remaining[predictor].nunique() >= 2 and remaining[outcome].nunique() >= 2:
                    rho, p_value = spearmanr(remaining[predictor], remaining[outcome])
                rows.append({"analysis_id": analysis_id, "predictor": predictor, "outcome": outcome, "removed_ID_Equipe": removed["ID_Equipe"], "removed_Semestre": removed["Semestre"], "n_remaining": int(len(remaining)), "spearman_rho": None if rho is None else float(rho), "spearman_p_exploratory": None if p_value is None else float(p_value)})
    return pd.DataFrame(rows)


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir().parent
    metrics = resolve_metrics_dir()
    paths = {
        "m6": metrics / "m6a_structural_planning.csv",
        "m8m": metrics / "m8_rework_magnitude.csv",
        "m8p": metrics / "m8_rework_participation.csv",
        "outcomes": root / "data" / "lake" / "evaluator_team_cuts.parquet",
        "m6b": metrics / "m6b_llm_planning_content.json",
    }
    input_hash = hashlib.sha256("".join(compute_sha256(path) for path in paths.values()).encode()).hexdigest()
    config = {"contract_version": CONTRACT_VERSION, "predictors": PREDICTORS, "outcomes": OUTCOMES, "missingness_policy": "stratify_and_report_no_score_floor_imputation"}
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    names = ["m9_planning_vs_rework_m6a_m8a.csv", "m9_planning_vs_rework_m6a_m8b_eligible_stratum.csv", "m9_planning_vs_outcomes_m6a_t3.csv", "m9_planning_vs_outcomes_m6b_t3_if_approved.csv", "m9_leave_one_out_intervals.csv", "m9_structured_associations.metadata.json"]
    outputs = [metrics / name for name in names]
    if not force and all(path.is_file() for path in outputs):
        metadata = json.loads(outputs[-1].read_text(encoding="utf-8"))
        if metadata.get("input_sha256") == input_hash and metadata.get("config_sha256") == config_hash:
            return {"status": "resumed", "artifacts": [str(path) for path in outputs]}
    m6 = pd.read_csv(paths["m6"], dtype={"Semestre": str})
    m8m = pd.read_csv(paths["m8m"], dtype={"Semestre": str})
    m8p = pd.read_csv(paths["m8p"], dtype={"Semestre": str})
    evaluator = pd.read_parquet(paths["outcomes"])
    t3 = evaluator.loc[evaluator["temporal_marker"].eq("T3"), TEAM_KEY + ["project_progress_mean", "scope_applicability_mean", "technical_complexity_mean", "engagement_participation_mean"]].rename(columns={column: f"{column}_t3" for column in ["project_progress_mean", "scope_applicability_mean", "technical_complexity_mean", "engagement_participation_mean"]})
    m6b_records = json.loads(paths["m6b"].read_text(encoding="utf-8"))
    m6b_rows = []
    for record in m6b_records:
        row = {"ID_Equipe": record["ID_Equipe"], "Semestre": record["Semestre"]}
        if record["status"] == "success":
            parsed = record["parsed_response"]
            row.update({"m6b_planning_evidence_present": parsed["planning_evidence_present"], "m6b_goals_n": len(parsed["goals"]), "m6b_architecture_or_design_n": len(parsed["architecture_or_design"]), "m6b_task_decomposition_n": len(parsed["task_decomposition"]), "m6b_risk_or_dependency_n": len(parsed["risk_or_dependency"]), "m6b_evidence_quotes_n": len(parsed["evidence_quotes"])})
        else:
            row.update({predictor: None for predictor in M6B_PREDICTORS})
        m6b_rows.append(row)
    m6b_frame = pd.DataFrame(m6b_rows)
    frame = m6.merge(m8m[TEAM_KEY + ["clean_rework_churn_t3", "clean_rework_ratio_t3", "baseline_eligible_for_rework_t3"]], on=TEAM_KEY, validate="one_to_one").merge(t3, on=TEAM_KEY, validate="one_to_one").merge(m6b_frame, on=TEAM_KEY, validate="one_to_one")
    if len(frame) != 14:
        raise ValueError(f"Expected 14 M9 team-semesters after joins, got {len(frame)}")
    all_rework = _association_table(frame, ["clean_rework_churn_t3"], "all_team_semesters")
    eligible = frame.loc[frame["baseline_eligible_for_rework_t3"]].copy()
    eligible_rework = _association_table(eligible, ["clean_rework_ratio_t3"], "baseline_eligible_only")
    evaluator_outcomes = ["project_progress_mean_t3", "scope_applicability_mean_t3", "technical_complexity_mean_t3", "engagement_participation_mean_t3"]
    outcomes = _association_table(frame, evaluator_outcomes, "all_team_semesters")
    loo = pd.concat([_leave_one_out(frame, ["clean_rework_churn_t3"], "all_team_semesters"), _leave_one_out(eligible, ["clean_rework_ratio_t3"], "baseline_eligible_only")], ignore_index=True)
    m6b_associations = _association_table(frame.dropna(subset=["m6b_planning_evidence_present"]), ["clean_rework_churn_t3", "project_progress_mean_t3", "scope_applicability_mean_t3", "technical_complexity_mean_t3", "engagement_participation_mean_t3"], "m6b_structured_content", M6B_PREDICTORS)
    metadata = {"status": "success", "gate_status": "pending", "contract_version": CONTRACT_VERSION, "metric_definition_version": CONTRACT_VERSION, "input_sha256": input_hash, "config_sha256": config_hash, "rq": "RQ3", "unit_of_analysis": "team_semester", "predictors": PREDICTORS, "m6b_predictors": M6B_PREDICTORS, "m6b_status": "approved_human_review", "m7_used_as_predictor": False, "inference": "exploratory_descriptive", "coverage": {"team_semesters": 14, "baseline_eligible": int(len(eligible)), "m6b_observed": int(frame["m6b_planning_evidence_present"].notna().sum()), "leave_one_out_rows": int(len(loo))}, "limitations": ["Spearman values are descriptive and not causal", "small denominators and influential cases require leave-one-out review", "M6b predictors are separate structured evidence counts, not a composite score", "M6b unavailable cases remain excluded from pairwise associations", "M7 is excluded as a predictor"], "artifacts": names}
    _atomic_csv(all_rework, outputs[0]); _atomic_csv(eligible_rework, outputs[1]); _atomic_csv(outcomes, outputs[2]); _atomic_csv(m6b_associations, outputs[3]); _atomic_csv(loo, outputs[4]); _atomic_json(metadata, outputs[5])
    if verbose: print(json.dumps(metadata, indent=2, sort_keys=True))
    return {"status": "generated", "artifacts": [str(path) for path in outputs]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate v9 M9 structured associations")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2))


if __name__ == "__main__":
    main()