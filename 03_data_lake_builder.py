from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_core import build_master_dataset, write_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Consolida CSVs anonimizados e logs Git em master_dataset.parquet.")
    parser.add_argument("--csv", dest="csv_paths", action="append", default=[], help="CSV anonimizado")
    parser.add_argument("--git-log", required=True, help="CSV git_logs_anon.csv")
    parser.add_argument("--output", default="master_dataset.parquet", help="Saída parquet consolidada")
    args = parser.parse_args()

    rows = build_master_dataset([Path(path) for path in args.csv_paths], Path(args.git_log))
    write_records(Path(args.output), rows)


if __name__ == "__main__":
    main()
