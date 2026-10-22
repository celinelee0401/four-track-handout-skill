#!/usr/bin/env python3
"""Extract text from a PDF page range (any OS; needs `pip install pymupdf`).
usage: python3 pdf_text.py file.pdf FIRST LAST
"""
import sys

import fitz

if len(sys.argv) < 4:
    sys.exit("usage: python3 pdf_text.py file.pdf FIRST LAST")
doc = fitz.open(sys.argv[1])
last = min(int(sys.argv[3]), doc.page_count)
for i in range(int(sys.argv[2]) - 1, last):
    print(f"=== PAGE {i + 1}")
    print(doc[i].get_text())
