#!/usr/bin/env python3
"""Anonymizer script for redacting PII from CSVs and transcripts.

This script processes evaluation forms and transcripts, replacing identifiable
information with deterministic hashes. It creates a restricted mapping file
for authorized researchers to correlate results.

Usage:
    python 01_anonymizer.py --csv input.csv --transcript feedback.txt \
        --output-dir output/ --mapping-path mapping.json --salt pepper
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
from pathlib import Path

from pipeline_core import (
    anonymize_csv_file,
    anonymize_transcript,
    build_anonymization_mapping,
    input_checksum,
    is_identifier_field,
    is_current_artifact,
    load_project_environment,
    write_artifact_metadata,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def discover_files(directory: Path, suffixes: set[str]) -> list[Path]:
    """Return supported files below an existing directory in stable order."""
    if not directory.exists():
        return []
    return sorted(
        path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in suffixes
    )


def output_path(source_path: Path, source_dir: Path, output_dir: Path) -> Path:
    """Build an output path preserving a source directory's relative layout."""
    try:
        return output_dir / source_path.relative_to(source_dir)
    except ValueError:
        return output_dir / source_path.name


def collect_csv_identifiers(csv_path: Path) -> list[str]:
    """Collect identifiers from CSV fields that will be anonymized."""
    identifiers: set[str] = set()

    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key, value in row.items():
                if not isinstance(value, str) or not value:
                    continue
                if is_identifier_field(key):
                    identifiers.add(value)
                elif "@" in value:
                    identifiers.update(
                        re.findall(r"\b[\w.\-+%]+@[\w.\-]+\.\w+\b", value)
                    )

    return sorted(identifiers)


def main() -> None:
    """Main entry point for anonymizer."""
    load_project_environment()

    parser = argparse.ArgumentParser(
        description="Anonymize CSVs and transcripts by replacing PII with hashes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--csv",
        type=Path,
        action="append",
        default=[],
        help="Path to input CSV file; may be repeated",
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        action="append",
        default=[],
        help="Path to input transcript file; may be repeated",
    )
    parser.add_argument("--forms-dir", type=Path, default=Path("data/raw/forms"))
    parser.add_argument(
        "--transcripts-dir", type=Path, default=Path("data/processed/transcripts")
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/forms"),
        help="Directory to write anonymized files",
    )
    parser.add_argument(
        "--mapping-path",
        type=Path,
        default=Path("data/processed/chave_relacional.json"),
        help="Path to write the anonymization mapping JSON",
    )
    parser.add_argument(
        "--transcripts-output-dir",
        type=Path,
        default=Path("data/processed/transcripts_anon"),
    )
    parser.add_argument(
        "--salt",
        type=str,
        default=None,
        help="Salt to mix into hashes; defaults to ANONYMIZATION_SALT",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate outputs even when their current successful versions exist",
    )

    args = parser.parse_args()

    salt = args.salt or os.environ.get("ANONYMIZATION_SALT")
    if not salt:
        parser.error("--salt or ANONYMIZATION_SALT must be set")

    csv_paths = list(dict.fromkeys([*discover_files(args.forms_dir, {".csv"}), *args.csv]))
    transcript_paths = list(
        dict.fromkeys([*discover_files(args.transcripts_dir, {".txt", ".json"}), *args.transcript])
    )
    csv_outputs = [(path, output_path(path, args.forms_dir, args.output_dir)) for path in csv_paths]
    transcript_outputs = [
        (path, output_path(path, args.transcripts_dir, args.transcripts_output_dir))
        for path in transcript_paths
    ]

    logger.info("Building anonymization mapping...")

    # Build mapping from transcript and CSV
    csv_identifiers = [
        identifier
        for csv_path in csv_paths
        for identifier in collect_csv_identifiers(csv_path)
    ]
    mapping = build_anonymization_mapping(
        [csv_identifiers], transcript_paths, salt=salt
    )

    logger.info(f"Found {len(mapping)} identifiers to anonymize")

    # Anonymize CSV if provided
    for csv_path, output_csv in csv_outputs:
        checksum = input_checksum([csv_path], {"salt": salt})
        if not args.force and is_current_artifact(output_csv, checksum):
            continue
        logger.info(f"Anonymizing CSV: {csv_path}")
        anonymize_csv_file(csv_path, output_csv, mapping, salt=salt)
        write_artifact_metadata(output_csv, checksum)
        logger.info(f"Wrote anonymized CSV to {output_csv}")

    # Anonymize transcript if provided
    for transcript_path, output_transcript in transcript_outputs:
        checksum = input_checksum([transcript_path], {"salt": salt})
        if not args.force and is_current_artifact(output_transcript, checksum):
            continue
        logger.info(f"Anonymizing transcript: {transcript_path}")
        anonymize_transcript(transcript_path, output_transcript, mapping)
        write_artifact_metadata(output_transcript, checksum)
        logger.info(f"Wrote anonymized transcript to {output_transcript}")

    # Write mapping (restricted file)
    logger.info(f"Writing mapping to {args.mapping_path}")
    args.mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_data = {
        "salt": salt,
        "mapping": mapping,
    }
    args.mapping_path.write_text(json.dumps(mapping_data, indent=2), encoding="utf-8")
    write_artifact_metadata(
        args.mapping_path,
        input_checksum([*csv_paths, *transcript_paths], {"salt": salt}),
    )
    logger.info("Anonymization complete")


if __name__ == "__main__":
    main()
