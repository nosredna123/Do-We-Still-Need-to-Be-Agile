#!/usr/bin/env python3
"""Extract person-entity candidates from raw transcripts with OpenAI.

Usage:
    python 01_ner_extractor.py
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

from pipeline_core import (
    file_checksum,
    is_current_artifact,
    load_project_environment,
    write_artifact_metadata,
)
from pipeline_config import MODEL_CONFIG
from pipeline_prompts import NER_PROMPT

logger = logging.getLogger(__name__)


def transcript_text(transcript_path: Path) -> str:
    """Read the text field from a raw transcription JSON artifact."""
    data: dict[str, Any] = json.loads(transcript_path.read_text(encoding="utf-8"))
    text = data.get("text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError(f"Transcript {transcript_path} has no text content")
    return text


def extract_person_entities(text: str, api_key: str | None = None) -> list[str]:
    """Request strictly structured person-name candidates from OpenAI."""
    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError("openai package is not installed") from error

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=str(MODEL_CONFIG["ner"]["model"]),
        messages=[
            {"role": "system", "content": NER_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={"type": str(MODEL_CONFIG["ner"]["response_format"])},
        temperature=float(MODEL_CONFIG["ner"]["temperature"]),
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI NER response has no content")
    payload: dict[str, Any] = json.loads(content)
    entities = payload.get("person_entities")
    if not isinstance(entities, list) or not all(
        isinstance(entity, str) and entity.strip() for entity in entities
    ):
        raise ValueError("OpenAI NER response has invalid person_entities")
    return sorted(set(entity.strip() for entity in entities))


def main() -> None:
    """Extract person candidates for every pending raw transcript."""
    load_project_environment()
    parser = argparse.ArgumentParser(
        description="Extract person candidates from transcripts using OpenAI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--transcripts-dir",
        type=Path,
        default=Path("data/processed/transcripts"),
        help="Directory containing raw transcription JSON files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/ner_candidates"),
        help="Directory for private NER candidate artifacts",
    )
    parser.add_argument("--api-key", default=None, help="OpenAI API key")
    parser.add_argument("--force", action="store_true", help="Regenerate current NER artifacts")
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Maximum number of pending transcripts to process",
    )
    args = parser.parse_args()
    if args.limite is not None and args.limite < 1:
        parser.error("--limite must be greater than zero")
    if not args.transcripts_dir.is_dir():
        raise FileNotFoundError(f"Transcript directory not found: {args.transcripts_dir}")

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    transcript_paths = sorted(
        path
        for path in args.transcripts_dir.rglob("*.json")
        if not path.name.endswith(".metadata.json")
    )
    if not transcript_paths:
        raise FileNotFoundError(f"No transcription JSON files found in {args.transcripts_dir}")

    pending_paths = []
    for source_path in transcript_paths:
        output_path = args.output_dir / source_path.relative_to(args.transcripts_dir)
        output_path = output_path.with_name(f"{output_path.stem}.ner.json")
        checksum = file_checksum(source_path)
        if not args.force and is_current_artifact(output_path, checksum):
            continue
        pending_paths.append(source_path)

    if args.limite is not None:
        pending_paths = pending_paths[:args.limite]
    logger.info(
        "NER queue: total=%d completed=%d pending=%d",
        len(transcript_paths),
        len(transcript_paths) - len(pending_paths),
        len(pending_paths),
    )

    for index, source_path in enumerate(pending_paths, start=1):
        output_path = args.output_dir / source_path.relative_to(args.transcripts_dir)
        output_path = output_path.with_name(f"{output_path.stem}.ner.json")
        checksum = file_checksum(source_path)
        entities = extract_person_entities(transcript_text(source_path), args.api_key)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps({"person_entities": entities}, indent=2), encoding="utf-8"
        )
        write_artifact_metadata(output_path, checksum)
        logger.info(
            "NER progress: completed=%d/%d pending=%d source=%s",
            index,
            len(pending_paths),
            len(pending_paths) - index,
            source_path.name,
        )


if __name__ == "__main__":
    main()