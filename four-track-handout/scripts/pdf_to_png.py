#!/usr/bin/env python3
"""Render every page of a PDF to PNG for visual QA (any OS; needs `pip install pymupdf`).
usage: python3 pdf_to_png.py file.pdf OUT_DIR [scale]
"""
import sys
from pathlib import Path

import fitz

if len(sys.argv) < 3:
    sys.exit("usage: python3 pdf_to_png.py file.pdf OUT_DIR [scale]")
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
stem = Path(sys.argv[1]).stem
for i, page in enumerate(fitz.open(sys.argv[1])):
    file = out / f"{stem}-p{i + 1}.png"
    page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).save(file)
    print(file)
