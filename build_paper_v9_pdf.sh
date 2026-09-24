#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LATEX_DIR="$ROOT_DIR/paper_v9/latex"
BUILD_DIR="$LATEX_DIR/build"

cd "$LATEX_DIR"
mkdir -p "$BUILD_DIR"
rm -f "$BUILD_DIR/main.aux" "$BUILD_DIR/main.bbl" "$BUILD_DIR/main.blg" \
  "$BUILD_DIR/main.log" "$BUILD_DIR/main.out" "$BUILD_DIR/main.pdf"

pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory="$BUILD_DIR" main.tex

(cd "$BUILD_DIR" && BIBINPUTS="$LATEX_DIR:$BUILD_DIR:" bibtex main)

pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory="$BUILD_DIR" main.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory="$BUILD_DIR" main.tex

PDF_PATH="$BUILD_DIR/main.pdf"
if [[ ! -s "$PDF_PATH" ]]; then
  echo "PDF was not generated: $PDF_PATH" >&2
  exit 1
fi

echo "Generated: $PDF_PATH"
