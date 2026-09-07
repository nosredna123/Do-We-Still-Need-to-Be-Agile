#!/usr/bin/env python3
"""Audio transcriber for converting session recordings to text.

This script processes audio files (.mp3, .wav) from feedback sessions using
OpenAI's Whisper API, generating searchable transcripts for NLP analysis.

Usage:
    python 00_audio_transcriber.py --audio-dir data/raw/audio/ \
        --output-dir data/processed/transcripts/
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def transcribe_audio_file(
    audio_path: Path,
    api_key: Optional[str] = None,
) -> dict[str, Any]:
    """Transcribe a single audio file using Whisper API.

    Args:
        audio_path: Path to audio file (.mp3, .wav)
        api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)

    Returns:
        Dictionary with transcription metadata
    """
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("openai package not installed. Install with: pip install openai")
        return {"error": "openai not installed"}

    client = OpenAI(api_key=api_key)

    try:
        logger.info(f"Transcribing: {audio_path.name}")

        with audio_path.open("rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
            )

        return {
            "filename": audio_path.name,
            "duration": None,
            "text": transcript.text,
            "timestamp": None,
            "status": "success",
        }
    except Exception as e:
        logger.error(f"Failed to transcribe {audio_path}: {e}")
        return {
            "filename": audio_path.name,
            "error": str(e),
            "status": "error",
        }


def main() -> None:
    """Main entry point for audio transcriber."""
    parser = argparse.ArgumentParser(
        description="Transcribe audio files using Whisper API"
    )
    parser.add_argument(
        "--audio-dir",
        type=Path,
        required=True,
        help="Directory containing audio files (.mp3, .wav)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory to write transcription JSON files",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="OpenAI API key (uses OPENAI_API_KEY env var if not provided)",
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)

    audio_extensions = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}
    audio_files = [
        f for f in args.audio_dir.iterdir()
        if f.is_file() and f.suffix.lower() in audio_extensions
    ]

    logger.info(f"Found {len(audio_files)} audio files in {args.audio_dir}")

    for audio_file in audio_files:
        result = transcribe_audio_file(audio_file, api_key=args.api_key)

        output_file = args.output_dir / f"{audio_file.stem}.json"
        output_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
        text_output_file = args.output_dir / f"{audio_file.stem}.txt"
        text_output_file.write_text(str(result.get("text", "")), encoding="utf-8")

        if result.get("status") == "success":
            logger.info(f"Transcribed: {audio_file.name} -> {output_file.name}")
        else:
            logger.warning(f"Failed to transcribe: {audio_file.name}")

    logger.info("Transcription complete")


if __name__ == "__main__":
    main()
