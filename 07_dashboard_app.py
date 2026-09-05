from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_core import load_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Dashboard Streamlit para explorar a relação entre BDUF e Code Churn.")
    parser.add_argument("--input", default="metrics_dataset.parquet", help="Dataset auditado")
    args = parser.parse_args()

    try:
        import streamlit as st  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("O dashboard requer `streamlit` instalado.") from exc

    st.set_page_config(page_title="Do We Still Need to Be Agile?", layout="wide")

    records = load_records(Path(args.input))
    if not records:
        raise RuntimeError("Nenhum dado encontrado no dataset informado.")

    columns = sorted(records[0].keys())
    turma_options = sorted({str(row.get("turma", "não informado")) for row in records})
    experience_options = sorted({str(row.get("experiencia", row.get("experience", "não informado"))) for row in records})

    st.title("Do We Still Need to Be Agile? — Dashboard Analítico")

    selected_turmas = st.sidebar.multiselect("Turma", turma_options, default=turma_options)
    selected_experience = st.sidebar.multiselect("Experiência", experience_options, default=experience_options)

    filtered = [
        row
        for row in records
        if str(row.get("turma", "não informado")) in selected_turmas
        and str(row.get("experiencia", row.get("experience", "não informado"))) in selected_experience
    ]

    st.metric("Registros filtrados", len(filtered))
    st.dataframe(filtered, use_container_width=True)

    st.subheader("Relação entre planejamento e code churn")
    scatter_rows = [
        {
            "planning_index": row.get("planning_index"),
            "code_churn": row.get("code_churn"),
            "work_style": row.get("nlp_work_style"),
        }
        for row in filtered
    ]
    st.dataframe(scatter_rows, use_container_width=True)

    st.subheader("Colunas disponíveis")
    st.write(columns)


if __name__ == "__main__":
    main()
