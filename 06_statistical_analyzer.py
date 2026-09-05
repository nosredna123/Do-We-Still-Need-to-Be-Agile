from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_core import (
    correlation_rows,
    hypothesis_rows,
    load_records,
    write_heatmap_svg,
    write_hypothesis_csv,
    write_records,
    write_scatter_svg,
    write_work_style_svg,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera correlações, testes de hipótese e gráficos exportáveis.")
    parser.add_argument("--input", required=True, help="metrics_dataset.parquet")
    parser.add_argument("--correlation-output", default="correlation_results.csv")
    parser.add_argument("--hypothesis-output", default="hypothesis_results.csv")
    parser.add_argument("--figures-dir", default="assets/figures")
    args = parser.parse_args()

    records = load_records(Path(args.input))
    correlations = correlation_rows(records)
    write_records(Path(args.correlation_output), correlations)
    hypotheses = hypothesis_rows(records)
    write_hypothesis_csv(hypotheses, Path(args.hypothesis_output))

    figures_dir = Path(args.figures_dir)
    write_heatmap_svg(correlations, figures_dir / "correlation_heatmap.svg")
    write_scatter_svg(records, figures_dir / "planning_vs_churn.svg")
    write_work_style_svg(records, figures_dir / "work_style_distribution.svg")


if __name__ == "__main__":
    main()
