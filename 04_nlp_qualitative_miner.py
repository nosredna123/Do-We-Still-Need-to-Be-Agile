from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_core import enrich_records, load_records, write_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Enriquece o dataset com sinais qualitativos de NLP.")
    parser.add_argument("--input", required=True, help="master_dataset.parquet")
    parser.add_argument("--output", default="nlp_enriched_dataset.parquet", help="Arquivo parquet de saída")
    parser.add_argument("--backend", choices=["heuristic", "openai"], default="heuristic")
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--text-column", dest="text_columns", action="append", default=[])
    args = parser.parse_args()

    records = load_records(Path(args.input))
    enriched = enrich_records(records, backend=args.backend, text_fields=args.text_columns or None, model=args.model)
    write_records(Path(args.output), enriched)


if __name__ == "__main__":
    main()
