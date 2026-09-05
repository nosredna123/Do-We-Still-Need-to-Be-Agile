from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline_core import (
    AUDIO_SUFFIXES,
    ensure_parent,
    run_openai_transcription,
    run_txt_sidecar_transcription,
    run_whisper_transcription,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Transcreve áudios de feedback para .txt e .json.")
    parser.add_argument("input_dir", help="Diretório com arquivos .mp3/.wav/.m4a/.flac/.ogg")
    parser.add_argument("output_dir", help="Diretório onde as transcrições serão gravadas")
    parser.add_argument("--backend", choices=["txt-sidecar", "whisper", "openai"], default="txt-sidecar")
    parser.add_argument("--model", default="base", help="Modelo Whisper/OpenAI a ser utilizado")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    transcribers = {
        "txt-sidecar": lambda path: run_txt_sidecar_transcription(path),
        "whisper": lambda path: run_whisper_transcription(path, args.model),
        "openai": lambda path: run_openai_transcription(path, args.model),
    }
    for audio_path in sorted(path for path in input_dir.iterdir() if path.suffix.lower() in AUDIO_SUFFIXES):
        text, payload = transcribers[args.backend](audio_path)
        json_path = output_dir / f"{audio_path.stem}.json"
        txt_path = output_dir / f"{audio_path.stem}.txt"
        ensure_parent(json_path)
        ensure_parent(txt_path)
        json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        txt_path.write_text(text.strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
