from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_core import compute_metrics, load_records, write_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Calcula métricas quantitativas a partir do dataset enriquecido.")
    parser.add_argument("--input", required=True, help="nlp_enriched_dataset.parquet")
    parser.add_argument("--output", default="metrics_dataset.parquet", help="Arquivo parquet de saída")
    args = parser.parse_args()

    rows = load_records(Path(args.input))
    metrics_rows = compute_metrics(rows)
    write_records(Path(args.output), metrics_rows)


if __name__ == "__main__":
    main()
