"""Generate M2 role-specific perceived-disruption distributions."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from paper_v9.scripts.common.paths import resolve_metrics_dir, resolve_paper_v9_dir
from paper_v9.scripts.common.provenance import compute_sha256

ROLE_QUESTION_COLUMNS = {
    "Backend": "A função de backend será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).",
    "Frontend": "A função de frontend será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).",
    "QA": "A função de QA (Garantia de Qualidade) será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).",
    "Project Manager": "A função de gerente de projeto será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).",
    "Product Manager": "A função de Product Manager será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).",
    "Scrum Master": "A função de Scrum Master será extinta ou severamente afetada pelo uso de ferramentas de IA generativa na engenharia de software. Indique seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente).",
}
ROLE_ORDER = tuple(ROLE_QUESTION_COLUMNS)
CHECKPOINT_ORDER = ("T1", "T2", "T3")
CONTRACT_VERSION = "m2-role-perception-v1"


def _atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def _atomic_write_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, path)


def _load_input() -> Path:
    return resolve_paper_v9_dir().parent / "data" / "lake" / "student_responses.parquet"


def _validate_input(frame: pd.DataFrame) -> None:
    required = {"Semestre", "temporal_marker", "Email Address", *ROLE_QUESTION_COLUMNS.values()}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"M2 input is missing required columns: {sorted(missing)}")
    if set(frame["temporal_marker"].dropna()) != set(CHECKPOINT_ORDER):
        raise ValueError("M2 input must contain exactly T1, T2, and T3")
    if frame[["Semestre", "temporal_marker", "Email Address"]].isna().any().any():
        raise ValueError("M2 input has missing temporal or respondent identifiers")


def _build_long(frame: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for role, column in ROLE_QUESTION_COLUMNS.items():
        part = frame[["Semestre", "temporal_marker", "Email Address", column]].copy()
        part = part.rename(columns={column: "score"})
        part["role"] = role
        parts.append(part)
    long = pd.concat(parts, ignore_index=True)
    long["score"] = pd.to_numeric(long["score"], errors="coerce")
    if long["score"].isna().any() or not long["score"].between(1, 5).all():
        raise ValueError("M2 role scores must be complete integers from 1 to 5")
    if long["score"].mod(1).ne(0).any():
        raise ValueError("M2 role scores must be integer-valued")
    respondent = long["Email Address"].astype("string").str.strip().str.lower()
    if long.assign(_respondent=respondent).duplicated(
        ["Semestre", "temporal_marker", "_respondent", "role"]
    ).any():
        raise ValueError("M2 contains duplicate respondent-checkpoint-role records")
    long["respondent_key"] = respondent.map(lambda value: hashlib.sha256(value.encode()).hexdigest())
    return long


def _build_distributions(long: pd.DataFrame) -> pd.DataFrame:
    result = (
        long.groupby(["Semestre", "temporal_marker", "role", "score"], observed=True)
        .size()
        .reset_index(name="count")
    )
    result["respondent_n"] = result.groupby(
        ["Semestre", "temporal_marker", "role"]
    )["count"].transform("sum")
    result["share"] = result["count"] / result["respondent_n"]
    return result.sort_values(["Semestre", "temporal_marker", "role", "score"]).reset_index(drop=True)


def _build_summary(long: pd.DataFrame) -> pd.DataFrame:
    enriched = long.assign(
        disagreement=long["score"].isin([1, 2]),
        neutral=long["score"].eq(3),
        agreement=long["score"].isin([4, 5]),
    )
    result = (
        enriched.groupby(["Semestre", "temporal_marker", "role"], as_index=False, observed=True)
        .agg(
            n=("score", "size"),
            mean=("score", "mean"),
            std=("score", lambda values: values.std(ddof=1)),
            median=("score", "median"),
            q1=("score", lambda values: values.quantile(0.25)),
            q3=("score", lambda values: values.quantile(0.75)),
            disagreement_share=("disagreement", "mean"),
            neutral_share=("neutral", "mean"),
            agreement_share=("agreement", "mean"),
        )
    )
    result["iqr"] = result["q3"] - result["q1"]
    return result


def _build_paired(long: pd.DataFrame) -> pd.DataFrame:
    panel = (
        long.pivot_table(
            index=["Semestre", "respondent_key", "role"],
            columns="temporal_marker",
            values="score",
            aggfunc="first",
        )
        .dropna(subset=["T1", "T3"])
        .reset_index()
    )
    panel["change_T3_minus_T1"] = panel["T3"] - panel["T1"]
    result = (
        panel.groupby(["Semestre", "role"], as_index=False)
        .agg(
            pairs=("change_T3_minus_T1", "size"),
            mean_T1=("T1", "mean"),
            mean_T3=("T3", "mean"),
            mean_change=("change_T3_minus_T1", "mean"),
            median_change=("change_T3_minus_T1", "median"),
            increased_share=("change_T3_minus_T1", lambda values: values.gt(0).mean()),
            unchanged_share=("change_T3_minus_T1", lambda values: values.eq(0).mean()),
            decreased_share=("change_T3_minus_T1", lambda values: values.lt(0).mean()),
        )
    )
    return result


def _config_hash() -> str:
    encoded = json.dumps(
        {"roles": ROLE_QUESTION_COLUMNS, "contract_version": CONTRACT_VERSION},
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir()
    metrics_dir = resolve_metrics_dir()
    input_path = _load_input()
    input_hash = compute_sha256(input_path)
    config_hash = _config_hash()
    distributions_path = metrics_dir / "m2_role_perception_distributions.csv"
    summary_path = metrics_dir / "m2_role_perception_by_team_semester.csv"
    paired_path = metrics_dir / "m2_role_perception_paired_t1_t3.csv"
    manifest_path = metrics_dir / "m2_role_perception.metadata.json"
    outputs = [distributions_path, summary_path, paired_path]
    if not force and manifest_path.is_file() and all(path.is_file() for path in outputs):
        metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
        if metadata.get("input_sha256") == input_hash and metadata.get("config_sha256") == config_hash:
            return {"status": "resumed", "artifacts": [str(path) for path in outputs]}

    source = pd.read_parquet(input_path)
    _validate_input(source)
    long = _build_long(source)
    distributions = _build_distributions(long)
    summary = _build_summary(long)
    paired = _build_paired(long)
    _atomic_write_csv(distributions, distributions_path)
    _atomic_write_csv(summary, summary_path)
    _atomic_write_csv(paired, paired_path)
    metadata = {
        "status": "success",
        "gate_status": "approved",
        "gate_approved_on": "2026-09-24",
        "gate_scope": "descriptive perceived-disruption agreement by role, including privacy-preserving paired sensitivity analysis",
        "contract_version": CONTRACT_VERSION,
        "metric_definition_version": CONTRACT_VERSION,
        "input_path": str(input_path.relative_to(root.parent)),
        "input_sha256": input_hash,
        "config_sha256": config_hash,
        "unit_of_analysis": "cohort by semester, temporal checkpoint, and role",
        "keys": ["Semestre", "temporal_marker", "role"],
        "roles": list(ROLE_ORDER),
        "scale": {"min": 1, "max": 5, "type": "Likert agreement"},
        "coverage": summary.groupby(["Semestre", "temporal_marker"], as_index=False).agg(
            roles=("role", "nunique"), students_per_role=("n", "first")
        ).to_dict(orient="records"),
        "paired_t1_t3": {"pairing_key": "hashed anonymized respondent identifier", "pairs": int(paired["pairs"].sum())},
        "interpretation": "perceived role disruption agreement, not objective extinction risk",
        "limitations": [
            "the prompt combines extinction and severe transformation",
            "self-report is not telemetry",
            "paired analysis requires observed respondent identifiers",
        ],
        "artifacts": [path.name for path in outputs],
    }
    _atomic_write_json(metadata, manifest_path)
    if verbose:
        print(json.dumps(metadata, indent=2, sort_keys=True))
    return {"status": "generated", "artifacts": [str(path) for path in outputs] + [str(manifest_path)]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the v9 M2 role perception metric")
    parser.add_argument("--force", action="store_true", help="Regenerate existing artifacts")
    parser.add_argument("--verbose", action="store_true", help="Print the generated manifest")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2))


if __name__ == "__main__":
    main()
