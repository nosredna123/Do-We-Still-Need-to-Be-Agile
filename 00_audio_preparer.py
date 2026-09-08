#!/usr/bin/env python3
"""Prepare audio recordings for OpenAI transcription uploads.

Usage:
    python 00_audio_preparer.py
"""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
from pathlib import Path

from pipeline_core import (
    file_checksum,
    is_current_artifact,
    load_project_environment,
    write_artifact_metadata,
)

logger = logging.getLogger(__name__)
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


def compression_command(source_path: Path, output_path: Path) -> list[str]:
    """Build the ffmpeg command that creates a mono transcription audio file."""
    return [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-b:a",
        "48k",
        str(output_path),
    ]


def segment_command(source_path: Path, output_pattern: Path) -> list[str]:
    """Build the ffmpeg command that splits oversized audio into ten-minute parts."""
    return [
        "ffmpeg",
        "-y",
        "-i",
        str(source_path),
        "-f",
        "segment",
        "-segment_time",
        "600",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-b:a",
        "48k",
        str(output_pattern),
    ]


def current_prepared_outputs(output_path: Path, checksum: str) -> bool:
    """Return whether a compressed output or all of its segments are current."""
    if is_current_artifact(output_path, checksum):
        return True
    segments = sorted(output_path.parent.glob(f"{output_path.stem}.part*.mp3"))
    return bool(segments) and all(
        is_current_artifact(segment, checksum) for segment in segments
    )


def main() -> None:
    """Prepare every source audio file for the transcription stage."""
    load_project_environment()
    parser = argparse.ArgumentParser(
        description="Compress and segment audio files for OpenAI transcription",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--audio-dir",
        type=Path,
        default=Path("data/raw/audio"),
        help="Directory containing source recordings",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/audio_chunks"),
        help="Directory for prepared transcription audio",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate prepared audio even when source content is unchanged",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Maximum number of pending source audio files to prepare",
    )
    args = parser.parse_args()
    if args.limite is not None and args.limite < 1:
        parser.error("--limite must be greater than zero")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to prepare audio files")
    if not args.audio_dir.is_dir():
        raise FileNotFoundError(f"Audio source directory not found: {args.audio_dir}")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    audio_paths = sorted(
        path
        for path in args.audio_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS
    )
    if not audio_paths:
        raise FileNotFoundError(f"No supported audio files found in {args.audio_dir}")

    pending_audio_paths = []
    for source_path in audio_paths:
        relative_path = source_path.relative_to(args.audio_dir)
        output_path = args.output_dir / relative_path.with_suffix(".mp3")
        checksum = file_checksum(source_path)
        if not args.force and current_prepared_outputs(output_path, checksum):
            continue
        pending_audio_paths.append(source_path)

    if args.limite is not None:
        pending_audio_paths = pending_audio_paths[:args.limite]
    logger.info("Selected %d pending source audio files", len(pending_audio_paths))

    for source_path in pending_audio_paths:
        relative_path = source_path.relative_to(args.audio_dir)
        output_path = args.output_dir / relative_path.with_suffix(".mp3")
        checksum = file_checksum(source_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.with_name(f"{output_path.name}.metadata.json").unlink(
            missing_ok=True
        )
        for stale_segment in output_path.parent.glob(f"{output_path.stem}.part*.mp3"):
            stale_segment.unlink()
            stale_segment.with_name(f"{stale_segment.name}.metadata.json").unlink(
                missing_ok=True
            )
        subprocess.run(compression_command(source_path, output_path), check=True)
        if output_path.stat().st_size <= MAX_UPLOAD_BYTES:
            write_artifact_metadata(output_path, checksum)
            continue

        output_path.unlink()
        pattern = output_path.with_name(f"{output_path.stem}.part%03d.mp3")
        subprocess.run(segment_command(source_path, pattern), check=True)
        segments = sorted(output_path.parent.glob(f"{output_path.stem}.part*.mp3"))
        if not segments or any(segment.stat().st_size > MAX_UPLOAD_BYTES for segment in segments):
            raise RuntimeError(f"Prepared audio exceeds upload limit: {source_path}")
        for segment in segments:
            write_artifact_metadata(segment, checksum)


if __name__ == "__main__":
    main()