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
import re
from pathlib import Path

from pipeline_core import (
    anonymize_csv_file,
    anonymize_transcript,
    build_anonymization_mapping,
    input_checksum,
    is_identifier_field,
    is_current_artifact,
    write_artifact_metadata,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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
    parser = argparse.ArgumentParser(
        description="Anonymize CSVs and transcripts by replacing PII with hashes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--csv", type=Path, help="Path to input CSV file")
    parser.add_argument(
        "--transcript", type=Path, help="Path to input transcript file"
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
        "--salt",
        type=str,
        default="",
        help="Salt to mix into hashes for additional security",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate outputs even when their current successful versions exist",
    )

    args = parser.parse_args()

    input_paths = [path for path in [args.csv, args.transcript] if path]
    checksum = input_checksum(input_paths, {"salt": args.salt})
    output_paths = [args.mapping_path]
    if args.csv:
        output_paths.append(args.output_dir / args.csv.name)
    if args.transcript:
        output_paths.append(args.output_dir / args.transcript.name)

    if not args.force and all(
        is_current_artifact(output_path, checksum) for output_path in output_paths
    ):
        logger.info("Skipping current anonymization outputs")
        return

    logger.info("Building anonymization mapping...")

    # Build mapping from transcript and CSV
    transcript_paths = [args.transcript] if args.transcript else []
    csv_identifiers = collect_csv_identifiers(args.csv) if args.csv else []
    mapping = build_anonymization_mapping(
        [csv_identifiers], transcript_paths, salt=args.salt
    )

    logger.info(f"Found {len(mapping)} identifiers to anonymize")

    # Anonymize CSV if provided
    if args.csv:
        logger.info(f"Anonymizing CSV: {args.csv}")
        output_csv = args.output_dir / args.csv.name
        anonymize_csv_file(args.csv, output_csv, mapping, salt=args.salt)
        logger.info(f"Wrote anonymized CSV to {output_csv}")

    # Anonymize transcript if provided
    if args.transcript:
        logger.info(f"Anonymizing transcript: {args.transcript}")
        output_transcript = args.output_dir / args.transcript.name
        anonymize_transcript(args.transcript, output_transcript, mapping)
        logger.info(f"Wrote anonymized transcript to {output_transcript}")

    # Write mapping (restricted file)
    logger.info(f"Writing mapping to {args.mapping_path}")
    args.mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_data = {
        "salt": args.salt,
        "mapping": mapping,
    }
    args.mapping_path.write_text(json.dumps(mapping_data, indent=2), encoding="utf-8")
    for output_path in output_paths:
        write_artifact_metadata(output_path, checksum)
    logger.info("Anonymization complete")


if __name__ == "__main__":
    main()
