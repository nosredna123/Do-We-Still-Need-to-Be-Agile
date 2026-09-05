from __future__ import annotations

import argparse
from pathlib import Path

from pipeline_core import extract_git_history, load_mapping, mirror_repository, write_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Extrai histórico Git anonimizando autorias e espelhando working trees sem .git.")
    parser.add_argument("--repo", dest="repos", action="append", required=True, help="Repositório local a ser minerado")
    parser.add_argument("--output-dir", required=True, help="Diretório para repositórios expurgados")
    parser.add_argument("--csv-output", default="git_logs_anon.csv", help="Caminho do CSV consolidado")
    parser.add_argument("--mapping-path", default="chave_relacional.json", help="Mapa de identidades previamente gerado")
    parser.add_argument("--salt", default="", help="Sal opcional para o hashing")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    mapping = load_mapping(Path(args.mapping_path))
    all_rows = []
    for repo in [Path(path) for path in args.repos]:
        mirror_repository(repo, output_dir)
        all_rows.extend(extract_git_history(repo, mapping, salt=args.salt))
    write_records(Path(args.csv_output), all_rows)


if __name__ == "__main__":
    main()
