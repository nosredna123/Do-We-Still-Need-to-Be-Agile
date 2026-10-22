"""Generate the non-composite M1 perception panel from the persisted NLP lake."""

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

QUESTION_GROUPS = {
    "ai_benefit": "ai_benefit",
    "autonomy_tool_dependency": "autonomy_tool_balance",
    "ai_career_impact_5y": "career_impact",
    "career_expectation": "project_expectations",
    "project_challenges": "project_expectations",
    "project_feeling": "project_expectations",
}
QUESTION_ORDER = tuple(QUESTION_GROUPS)
CHECKPOINT_ORDER = ("T1", "T2", "T3")
CONTRACT_VERSION = "m1-rq1-perception-panel-v2"
RAW_USAGE_COLUMNS = {
    "general_frequency": "Com que frequência você utiliza ferramentas de IA generativa em seu dia a dia de maneira geral?",
    "software_frequency": "Com que frequência você utiliza ferramentas de IA Generativa especificamente em projetos de engenharia de software?",
    "tasks": "Para quais atividades você costuma utilizar ferramentas de IA generativa? (marque todas as que se aplicam)",
    "tools": "Quais ferramentas de IA generativa você utilizou nos últimos 12 meses em projetos de engenharia de software? (selecione todas que se aplicam)",
    "prior_project_experience": "Você já desenvolveu ou participou de projetos de desenvolvimento de software que usa IA Generativa para realizar alguma(s) funcionalidade(s) ",
    "career_text": "Em 5 anos, como você enxerga o impacto das ferramentas de IA generativa em sua carreira de engenharia de software?",
    "autonomy_balance": "Para você, qual deve ser o equilíbrio ideal entre a autonomia de cada integrante e a dependência de ferramentas de suporte no desenvolvimento do projeto?",
}
FREQUENCY_ORDER = ("Nunca", "Raramente", "Algumas vezes por mês", "Semanalmente", "Diariamente")
CAREER_TOPIC_KEYWORDS = {
    "productivity_and_speed": ("produt", "tempo", "rápid", "efici"),
    "skills_and_learning": ("compet", "aprend", "conhec", "habil", "skill", "formação"),
    "task_or_role_change": ("papel", "função", "processo", "atividade", "tarefa", "cargo"),
    "replacement_or_job_risk": ("substit", "extin", "desempreg", "mercado", "perder", "elimin"),
    "uncertainty_or_condition": ("depende", "talvez", "incert", "risco", "acredito", "pode"),
}


def _atomic_write_csv(frame: pd.DataFrame, path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    frame.to_csv(temporary, index=False)
    os.replace(temporary, path)


def _atomic_write_json(payload: dict[str, Any], path: Path) -> None:
    temporary = path.with_name(f"{path.name}.partial")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, path)


def _validate_input(frame: pd.DataFrame) -> None:
    required = {
        "student_response_id",
        "Semestre",
        "temporal_marker",
        "question_id",
        "ai_dependency_score",
        "status",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"M1 input is missing required columns: {sorted(missing)}")
    observed_questions = set(frame["question_id"].dropna())
    if observed_questions != set(QUESTION_ORDER):
        raise ValueError(
            "M1 input question set differs from the v8 contract: "
            f"{sorted(observed_questions)}"
        )
    if frame["status"].ne("success").any():
        raise ValueError("M1 input contains non-success NLP rows")
    scores = pd.to_numeric(frame["ai_dependency_score"], errors="coerce")
    if scores.isna().any() or not scores.between(0, 4).all():
        raise ValueError("M1 scores must be numeric and within the inclusive range 0..4")
    if scores.mod(1).ne(0).any():
        raise ValueError("M1 scores must be integer-valued")
    duplicate_keys = frame.duplicated(["student_response_id", "question_id"])
    if duplicate_keys.any():
        raise ValueError("M1 input contains duplicate student-response/question rows")
    if frame[["Semestre", "temporal_marker"]].isna().any().any():
        raise ValueError("M1 input contains missing cohort or checkpoint keys")


def _input_path() -> Path:
    return resolve_paper_v9_dir().parent / "data" / "analysis" / "student_nlp.parquet"


def _raw_input_path() -> Path:
    return resolve_paper_v9_dir().parent / "data" / "lake" / "student_responses.parquet"


def _config_hash() -> str:
    encoded = json.dumps(
        {"questions": QUESTION_GROUPS, "contract_version": CONTRACT_VERSION},
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _build_long(frame: pd.DataFrame) -> pd.DataFrame:
    summary = (
        frame.groupby(["Semestre", "temporal_marker", "question_id"], observed=True)[
            "ai_dependency_score"
        ]
        .agg(
            mean="mean",
            std=lambda values: values.std(ddof=1),
            median="median",
            q1=lambda values: values.quantile(0.25),
            q3=lambda values: values.quantile(0.75),
            n="count",
        )
        .reset_index()
    )
    summary["iqr"] = summary["q3"] - summary["q1"]
    counts = frame.groupby(["Semestre", "temporal_marker"], observed=True)[
        "student_response_id"
    ].nunique()
    summary["student_n"] = [
        counts[(row.Semestre, row.temporal_marker)] for row in summary.itertuples()
    ]
    summary["perception_group"] = summary["question_id"].map(QUESTION_GROUPS)
    summary["perception_family"] = summary["question_id"]
    summary["coverage"] = summary["n"] / summary["student_n"]
    summary["measurement_status"] = "available"
    summary = summary.rename(columns={"question_id": "question"})
    columns = [
        "Semestre",
        "temporal_marker",
        "perception_group",
        "perception_family",
        "mean",
        "std",
        "median",
        "q1",
        "q3",
        "iqr",
        "n",
        "student_n",
        "coverage",
        "measurement_status",
    ]
    return summary[columns].sort_values(
        ["Semestre", "temporal_marker", "perception_family"],
        key=lambda values: values.map({item: index for index, item in enumerate(QUESTION_ORDER)})
        if values.name == "perception_family"
        else values,
    ).reset_index(drop=True)


def _build_wide(long: pd.DataFrame) -> pd.DataFrame:
    index = ["Semestre", "temporal_marker"]
    values = ["mean", "std", "median", "q1", "q3", "iqr", "n", "student_n", "coverage", "measurement_status"]
    wide = long.pivot(index=index, columns="perception_family", values=values)
    wide.columns = [f"{question}_{stat}" for stat, question in wide.columns]
    wide = wide.reset_index()
    expected = [f"{question}_{stat}" for question in QUESTION_ORDER for stat in values]
    return wide[index + expected].sort_values(index).reset_index(drop=True)


def _load_v8_comparison(root: Path) -> pd.DataFrame:
    path = root.parent / "paper_v8" / "data" / "m1_ai_dependency_trajectory.csv"
    if not path.is_file():
        raise FileNotFoundError(f"V8 comparison artifact not found: {path}")
    return pd.read_csv(path, dtype={"Semestre": str})


def _validate_raw_input(frame: pd.DataFrame) -> None:
    required = {"Semestre", "temporal_marker", "source_file", *RAW_USAGE_COLUMNS.values()}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Raw M1 input is missing required columns: {sorted(missing)}")
    if frame[["Semestre", "temporal_marker", "source_file"]].isna().any().any():
        raise ValueError("Raw M1 input has missing temporal provenance")
    if set(frame["temporal_marker"].dropna()) != set(CHECKPOINT_ORDER):
        raise ValueError("Raw M1 input must contain exactly T1, T2, and T3")


def _split_multi_select(value: object) -> list[str]:
    if pd.isna(value) or not str(value).strip():
        return []
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _build_usage_counts(raw: pd.DataFrame, column_key: str, output_name: str) -> pd.DataFrame:
    column = RAW_USAGE_COLUMNS[column_key]
    records: list[dict[str, Any]] = []
    for keys, group in raw.groupby(["Semestre", "temporal_marker"], observed=True):
        semester, checkpoint = keys
        values = group[column].map(_split_multi_select).explode().dropna()
        counts = values.value_counts().sort_index()
        denominator = len(group)
        for category, count in counts.items():
            records.append(
                {
                    "Semestre": semester,
                    "temporal_marker": checkpoint,
                    "measure": output_name,
                    "category": category,
                    "count": int(count),
                    "respondent_n": denominator,
                    "share": float(count / denominator),
                }
            )
    result = pd.DataFrame(records)
    if result.empty:
        raise ValueError(f"No usable values found for raw M1 measure: {output_name}")
    return result.sort_values(["Semestre", "temporal_marker", "category"]).reset_index(drop=True)


def _build_usage_frequency(raw: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for measure, column_key in (("general_frequency", "general_frequency"), ("software_frequency", "software_frequency")):
        column = RAW_USAGE_COLUMNS[column_key]
        for keys, group in raw.groupby(["Semestre", "temporal_marker"], observed=True):
            semester, checkpoint = keys
            counts = group[column].value_counts(dropna=False)
            for category in FREQUENCY_ORDER:
                count = int(counts.get(category, 0))
                records.append(
                    {
                        "Semestre": semester,
                        "temporal_marker": checkpoint,
                        "measure": measure,
                        "category": category,
                        "count": count,
                        "respondent_n": len(group),
                        "share": count / len(group),
                    }
                )
    return pd.DataFrame(records)


def _build_binary_experience(raw: pd.DataFrame) -> pd.DataFrame:
    column = RAW_USAGE_COLUMNS["prior_project_experience"]
    result = (
        raw.groupby(["Semestre", "temporal_marker", column], dropna=False, observed=True)
        .size()
        .reset_index(name="count")
        .rename(columns={column: "category"})
    )
    result["measure"] = "prior_ai_project_experience"
    result["respondent_n"] = result.groupby(["Semestre", "temporal_marker"])["count"].transform("sum")
    result["share"] = result["count"] / result["respondent_n"]
    return result


def _build_autonomy_distribution(raw: pd.DataFrame) -> pd.DataFrame:
    column = RAW_USAGE_COLUMNS["autonomy_balance"]
    scores = pd.to_numeric(raw[column], errors="coerce")
    if scores.isna().any() or not scores.between(1, 5).all():
        raise ValueError("Raw autonomy balance responses must be numeric scores from 1 to 5")
    result = (
        raw.assign(autonomy_score=scores)
        .groupby(["Semestre", "temporal_marker", "autonomy_score"], observed=True)
        .size()
        .reset_index(name="count")
        .rename(columns={"autonomy_score": "category"})
    )
    result["measure"] = "autonomy_tool_balance"
    result["respondent_n"] = result.groupby(["Semestre", "temporal_marker"])["count"].transform("sum")
    result["share"] = result["count"] / result["respondent_n"]
    return result


def _build_career_topics(raw: pd.DataFrame) -> pd.DataFrame:
    column = RAW_USAGE_COLUMNS["career_text"]
    records: list[dict[str, Any]] = []
    for row in raw[["Semestre", "temporal_marker", column]].itertuples(index=False):
        text = "" if pd.isna(row[2]) else str(row[2]).lower()
        matched = [topic for topic, keywords in CAREER_TOPIC_KEYWORDS.items() if any(keyword in text for keyword in keywords)]
        if not matched:
            matched = ["other_or_insufficient_evidence"]
        for topic in matched:
            records.append({"Semestre": row[0], "temporal_marker": row[1], "topic": topic})
    result = pd.DataFrame(records)
    counts = result.groupby(["Semestre", "temporal_marker", "topic"], observed=True).size().reset_index(name="count")
    counts["respondent_n"] = counts.groupby(["Semestre", "temporal_marker"])["count"].transform("sum")
    counts["share_of_topic_assignments"] = counts["count"] / counts["respondent_n"]
    counts["coding_status"] = "exploratory_rule_based_unvalidated"
    return counts


def _build_perception_distribution(frame: pd.DataFrame) -> pd.DataFrame:
    result = (
        frame.groupby(["Semestre", "temporal_marker", "question_id", "ai_dependency_score"], observed=True)
        .size()
        .reset_index(name="count")
        .rename(columns={"question_id": "perception_family", "ai_dependency_score": "category"})
    )
    result["respondent_n"] = result.groupby(
        ["Semestre", "temporal_marker", "perception_family"]
    )["count"].transform("sum")
    result["share"] = result["count"] / result["respondent_n"]
    return result


def generate(force: bool = False, verbose: bool = False) -> dict[str, Any]:
    root = resolve_paper_v9_dir()
    metrics_dir = resolve_metrics_dir()
    input_path = _input_path()
    raw_input_path = _raw_input_path()
    input_hash = compute_sha256(input_path)
    raw_input_hash = compute_sha256(raw_input_path)
    config_hash = _config_hash()
    manifest_path = metrics_dir / "m1_rq1_perception_panel.metadata.json"
    long_path = metrics_dir / "m1_rq1_perception_panel_long.csv"
    wide_path = metrics_dir / "m1_rq1_perception_panel_wide.csv"
    if not force and manifest_path.is_file() and long_path.is_file() and wide_path.is_file():
        metadata = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (
            metadata.get("input_sha256") == input_hash
            and metadata.get("raw_input_sha256") == raw_input_hash
            and metadata.get("config_sha256") == config_hash
        ):
            return {"status": "resumed", "artifacts": [str(long_path), str(wide_path)]}

    source = pd.read_parquet(input_path)
    raw_source = pd.read_parquet(raw_input_path)
    _validate_input(source)
    _validate_raw_input(raw_source)
    long = _build_long(source)
    wide = _build_wide(long)
    v8 = _load_v8_comparison(root)
    legacy = v8.set_index(["Semestre", "temporal_marker"])["ai_dependency_composite_mean"]
    recalculated = source.groupby(["Semestre", "temporal_marker"], observed=True).ai_dependency_score.mean()
    comparison = (recalculated - legacy).abs()
    if comparison.isna().any() or not (comparison < 1e-12).all():
        raise AssertionError("M1 v8 comparison does not reproduce the published composite")

    usage_frequency = _build_usage_frequency(raw_source)
    usage_tasks = _build_usage_counts(raw_source, "tasks", "real_ai_use_tasks")
    usage_tools = _build_usage_counts(raw_source, "tools", "real_ai_use_tools")
    prior_experience = _build_binary_experience(raw_source)
    autonomy_distribution = _build_autonomy_distribution(raw_source)
    career_topics = _build_career_topics(raw_source)
    perception_distribution = _build_perception_distribution(source)
    additional_outputs = {
        "m1_rq1_usage_frequency.csv": usage_frequency,
        "m1_rq1_usage_tasks.csv": usage_tasks,
        "m1_rq1_usage_tools.csv": usage_tools,
        "m1_rq1_prior_ai_project_experience.csv": prior_experience,
        "m1_rq1_autonomy_tool_balance.csv": autonomy_distribution,
        "m1_rq1_career_impact_topics_exploratory.csv": career_topics,
        "m1_rq1_perception_distribution.csv": perception_distribution,
    }

    _atomic_write_csv(long, long_path)
    _atomic_write_csv(wide, wide_path)
    for filename, frame in additional_outputs.items():
        _atomic_write_csv(frame, metrics_dir / filename)
    artifact_names = [long_path.name, wide_path.name, *additional_outputs]
    metadata = {
        "status": "success",
        "gate_status": "approved",
        "gate_approved_on": "2026-09-24",
        "gate_scope": "descriptive M1 v2 outputs approved; exploratory career topics and NLP rubric validity remain limitations",
        "contract_version": CONTRACT_VERSION,
        "metric_definition_version": CONTRACT_VERSION,
        "input_path": str(input_path.relative_to(root.parent)),
        "input_sha256": input_hash,
        "raw_input_path": str(raw_input_path.relative_to(root.parent)),
        "raw_input_sha256": raw_input_hash,
        "config_sha256": config_hash,
        "unit_of_analysis": "cohort by semester and temporal checkpoint",
        "keys": ["Semestre", "temporal_marker", "perception_family"],
        "question_groups": QUESTION_GROUPS,
        "coverage": long.groupby(["Semestre", "temporal_marker"], as_index=False).agg(
            families=("perception_family", "nunique"),
            students=("student_n", "first"),
            min_coverage=("coverage", "min"),
            max_coverage=("coverage", "max"),
        ).to_dict(orient="records"),
        "unavailable_not_measured": ["individual_T1_T3_panel", "team_semester"],
        "available_and_extracted": [
            "real_ai_use_frequency",
            "real_ai_use_tasks",
            "real_ai_use_tools",
            "prior_ai_project_experience",
            "autonomy_tool_balance",
        ],
        "exploratory_unvalidated": ["career_impact_topics"],
        "raw_usage_contract": {
            "respondent_rows": int(len(raw_source)),
            "temporal_keys": int(raw_source[["Semestre", "temporal_marker"]].drop_duplicates().shape[0]),
            "career_topic_coding": "keyword rules; requires human validation before confirmatory use",
        },
        "v8_comparison": {"max_absolute_difference": float(comparison.max()), "families": 6},
        "artifacts": artifact_names,
    }
    _atomic_write_json(metadata, manifest_path)
    if verbose:
        print(json.dumps(metadata, indent=2, sort_keys=True))
    return {"status": "generated", "artifacts": [str(metrics_dir / name) for name in artifact_names] + [str(manifest_path)]}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the v9 M1 perception panel")
    parser.add_argument("--force", action="store_true", help="Regenerate existing artifacts")
    parser.add_argument("--verbose", action="store_true", help="Print the generated manifest")
    args = parser.parse_args()
    print(json.dumps(generate(force=args.force, verbose=args.verbose), indent=2))


if __name__ == "__main__":
    main()