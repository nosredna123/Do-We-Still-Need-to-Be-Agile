"""M2 -- Perceived Role-Disruption Risk (raw Likert survey proxy for RQ1).

Definition
----------
For each Semestre x temporal_marker cohort-cut and each SE role r in
{Backend, Frontend, QA, Project Manager, Product Manager, Scrum Master}, this
metric summarizes the raw 5-point Likert item ("this role will be extinct or
severely affected by generative AI tools", 1 = strongly disagree, 5 = strongly
agree) directly from the student survey -- no LLM coding involved, these are
structured numeric responses.

    role_disruption_risk(r, s, c) = summarize_numeric_distribution(
        likert_values(r, s, c), scale_type="likert_1_5", scale_version="v1"
    )

reusing `pipeline_statistics.summarize_numeric_distribution` for a consistent
mean/median/IQR/missingness summary, exactly as Phase 2 does for its own
ordinal scores.

Grain constraint
----------------
`data/lake/student_responses.parquet` carries `Semestre` and `temporal_marker`
only (no `ID_Equipe`) -- same cohort-level constraint as M1.

Source artifact (read-only, Phase 2 lake contract, frozen)
-----------------------------------------------------------
    data/lake/student_responses.parquet
    (validated via `phase2_contracts.load_phase2_inputs`, contract
    "student_responses", produced by `03_data_lake_builder.py`)

Output
------
    paper_v8/data/m2_role_disruption_risk.csv
    columns: Semestre, temporal_marker, role, n_total, n_valid, n_missing,
             mean, std, median, q1, q3, iqr, mode, mode_n, mode_share
"""

from __future__ import annotations

import pandas as pd
from _paths import LAKE_DIR, ensure_output_dir

from phase2_contracts import load_phase2_inputs
from pipeline_statistics import summarize_numeric_distribution

OUTPUT_PATH = ensure_output_dir() / "m2_role_disruption_risk.csv"
SCALE_TYPE = "likert_1_5_role_disruption"
SCALE_VERSION = "v1"

# Exact verbatim survey column names (verified against student_responses.parquet).
ROLE_QUESTION_COLUMNS = {
    "Backend": (
        "A função de backend será extinta ou severamente afetada pelo uso de "
        "ferramentas de IA generativa na engenharia de software. Indique seu "
        "grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente)."
    ),
    "Frontend": (
        "A função de frontend será extinta ou severamente afetada pelo uso de "
        "ferramentas de IA generativa na engenharia de software. Indique seu "
        "grau de concordância de 1 (Discordo totalmente) a 5 (Concordo totalmente)."
    ),
    "QA": (
        "A função de QA (Garantia de Qualidade) será extinta ou severamente "
        "afetada pelo uso de ferramentas de IA generativa na engenharia de "
        "software. Indique seu grau de concordância de 1 (Discordo totalmente) "
        "a 5 (Concordo totalmente)."
    ),
    "Project Manager": (
        "A função de gerente de projeto será extinta ou severamente afetada "
        "pelo uso de ferramentas de IA generativa na engenharia de software. "
        "Indique seu grau de concordância de 1 (Discordo totalmente) a 5 "
        "(Concordo totalmente)."
    ),
    "Product Manager": (
        "A função de Product Manager será extinta ou severamente afetada pelo "
        "uso de ferramentas de IA generativa na engenharia de software. "
        "Indique seu grau de concordância de 1 (Discordo totalmente) a 5 "
        "(Concordo totalmente)."
    ),
    "Scrum Master": (
        "A função de Scrum Master será extinta ou severamente afetada pelo uso "
        "de ferramentas de IA generativa na engenharia de software. Indique "
        "seu grau de concordância de 1 (Discordo totalmente) a 5 (Concordo "
        "totalmente)."
    ),
}


def build_role_disruption_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Summarize each role's Likert distribution per Semestre x temporal_marker cut."""
    missing_columns = [column for column in ROLE_QUESTION_COLUMNS.values() if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"student_responses.parquet is missing expected columns: {missing_columns}")

    rows: list[dict[str, object]] = []
    for (semestre, cut), group in frame.groupby(["Semestre", "temporal_marker"], dropna=False):
        for role, column in ROLE_QUESTION_COLUMNS.items():
            values = pd.to_numeric(group[column], errors="coerce")
            summary = summarize_numeric_distribution(
                values, scale_type=SCALE_TYPE, scale_version=SCALE_VERSION
            )
            rows.append({"Semestre": semestre, "temporal_marker": cut, "role": role, **summary})
    return pd.DataFrame(rows)


def main() -> None:
    inputs = load_phase2_inputs(LAKE_DIR)
    student_responses = inputs["student_responses"]
    table = build_role_disruption_table(student_responses)
    table.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(table)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
