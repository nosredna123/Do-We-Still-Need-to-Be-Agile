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
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.suffix.lower() in suffixes
        and not path.name.endswith(".metadata.json")
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


def load_person_names(candidates_dir: Path) -> list[str]:
    """Load validated person candidates emitted by the OpenAI NER stage."""
    person_names: set[str] = set()
    for candidate_path in discover_files(candidates_dir, {".json"}):
        data = json.loads(candidate_path.read_text(encoding="utf-8"))
        entities = data.get("person_entities")
        if not isinstance(entities, list) or not all(
            isinstance(entity, str) and entity.strip() for entity in entities
        ):
            raise ValueError(f"Invalid NER candidate artifact: {candidate_path}")
        person_names.update(entity.strip() for entity in entities)
    return sorted(person_names)


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
        "--ner-candidates-dir", type=Path, default=Path("data/processed/ner_candidates")
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
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Maximum number of pending form/transcript files to anonymize",
    )

    args = parser.parse_args()
    if args.limite is not None and args.limite < 1:
        parser.error("--limite must be greater than zero")

    salt = args.salt or os.environ.get("ANONYMIZATION_SALT")
    if not salt:
        parser.error("--salt or ANONYMIZATION_SALT must be set")

    csv_paths = list(dict.fromkeys([*discover_files(args.forms_dir, {".csv"}), *args.csv]))
    transcript_paths = list(
        dict.fromkeys([*discover_files(args.transcripts_dir, {".txt", ".json"}), *args.transcript])
    )
    if not csv_paths and not transcript_paths:
        raise FileNotFoundError("No CSV or transcript artifacts found to anonymize")
    person_names = load_person_names(args.ner_candidates_dir)
    csv_outputs = [(path, output_path(path, args.forms_dir, args.output_dir)) for path in csv_paths]
    transcript_outputs = [
        (path, output_path(path, args.transcripts_dir, args.transcripts_output_dir))
        for path in transcript_paths
    ]

    total_outputs = len(csv_outputs) + len(transcript_outputs)
    pending_outputs = []
    for source_path, target_path in [*csv_outputs, *transcript_outputs]:
        checksum = input_checksum([source_path], {"salt": salt})
        if args.force or not is_current_artifact(target_path, checksum):
            pending_outputs.append((source_path, target_path))
    if args.limite is not None:
        pending_outputs = pending_outputs[:args.limite]
    csv_outputs = [item for item in pending_outputs if item in csv_outputs]
    transcript_outputs = [item for item in pending_outputs if item in transcript_outputs]
    logger.info(
        "Anonymization queue: total=%d completed=%d pending=%d",
        total_outputs,
        total_outputs - len(pending_outputs),
        len(pending_outputs),
    )

    logger.info("Building anonymization mapping...")

    # Build mapping from transcript and CSV
    csv_identifiers = [
        identifier
        for csv_path in csv_paths
        for identifier in collect_csv_identifiers(csv_path)
    ]
    mapping = build_anonymization_mapping(
        [csv_identifiers], transcript_paths, salt=salt, person_names=person_names
    )

    logger.info(f"Found {len(mapping)} identifiers to anonymize")
    processed_count = 0
    total_pending = len(pending_outputs)

    # Anonymize CSV if provided
    for csv_path, output_csv in csv_outputs:
        checksum = input_checksum([csv_path], {"salt": salt})
        if not args.force and is_current_artifact(output_csv, checksum):
            continue
        logger.info(f"Anonymizing CSV: {csv_path}")
        anonymize_csv_file(csv_path, output_csv, mapping, salt=salt)
        write_artifact_metadata(output_csv, checksum)
        logger.info(f"Wrote anonymized CSV to {output_csv}")
        processed_count += 1
        logger.info(
            "Anonymization progress: completed=%d/%d pending=%d source=%s",
            processed_count,
            total_pending,
            total_pending - processed_count,
            csv_path.name,
        )

    # Anonymize transcript if provided
    for transcript_path, output_transcript in transcript_outputs:
        checksum = input_checksum([transcript_path], {"salt": salt})
        if not args.force and is_current_artifact(output_transcript, checksum):
            continue
        logger.info(f"Anonymizing transcript: {transcript_path}")
        anonymize_transcript(transcript_path, output_transcript, mapping)
        write_artifact_metadata(output_transcript, checksum)
        logger.info(f"Wrote anonymized transcript to {output_transcript}")
        processed_count += 1
        logger.info(
            "Anonymization progress: completed=%d/%d pending=%d source=%s",
            processed_count,
            total_pending,
            total_pending - processed_count,
            transcript_path.name,
        )

    # Write mapping (restricted file)
    logger.info(f"Writing mapping to {args.mapping_path}")
    args.mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_data = {"mapping": mapping}
    args.mapping_path.write_text(json.dumps(mapping_data, indent=2), encoding="utf-8")
    write_artifact_metadata(
        args.mapping_path,
        input_checksum([*csv_paths, *transcript_paths], {"salt": salt}),
    )
    logger.info("Anonymization complete")


if __name__ == "__main__":
    main()
