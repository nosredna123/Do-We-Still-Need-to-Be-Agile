from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline_core import anonymize_csv_file, anonymize_transcript_file, build_anonymization_mapping, ensure_parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Anonimiza CSVs e transcrições com hashes irreversíveis.")
    parser.add_argument("--csv", dest="csv_paths", action="append", default=[], help="CSV bruto de entrada")
    parser.add_argument("--transcript", dest="transcript_paths", action="append", default=[], help="Transcrição .txt/.json/.jsonl")
    parser.add_argument("--output-dir", required=True, help="Diretório para os arquivos anonimizados")
    parser.add_argument("--mapping-path", default="chave_relacional.json", help="Caminho do mapa restrito")
    parser.add_argument("--salt", default="", help="Sal opcional para o hashing")
    args = parser.parse_args()

    csv_paths = [Path(path) for path in args.csv_paths]
    transcript_paths = [Path(path) for path in args.transcript_paths]
    output_dir = Path(args.output_dir)
    mapping_path = Path(args.mapping_path)

    mapping = build_anonymization_mapping(csv_paths, transcript_paths, salt=args.salt)
    for csv_path in csv_paths:
        anonymize_csv_file(csv_path, output_dir / csv_path.name, mapping, salt=args.salt)
    for transcript_path in transcript_paths:
        anonymize_transcript_file(transcript_path, output_dir / transcript_path.name, mapping)

    ensure_parent(mapping_path)
    mapping_payload = {"mapping": mapping, "generated_from": [path.name for path in [*csv_paths, *transcript_paths]]}
    mapping_path.write_text(json.dumps(mapping_payload, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
