#!/bin/bash

# Script to convert Whitepaper.md to PDF with LaTeX formulas

set -e

echo "Converting Whitepaper.md to PDF..."

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
    echo "Error: pandoc is not installed."
    echo "Install it with: brew install pandoc"
    exit 1
fi

# Check if LaTeX is installed
if ! command -v xelatex &> /dev/null; then
    echo "Error: LaTeX is not installed."
    echo "Install it with: brew install --cask mactex-no-gui"
    exit 1
fi

# Convert directly to PDF using XeLaTeX with Latin Modern (default LaTeX font)
echo "Converting to PDF with LaTeX..."
pandoc Whitepaper.md \
    -f markdown \
    -t pdf \
    --pdf-engine=xelatex \
    -V geometry:margin=1in \
    -V fontsize=11pt \
    -V documentclass:article \
    -V classoption:oneside \
    -o Whitepaper.pdf

echo "✓ Generated Whitepaper.pdf"
echo ""
echo "Done! PDF saved as Whitepaper.pdf"
