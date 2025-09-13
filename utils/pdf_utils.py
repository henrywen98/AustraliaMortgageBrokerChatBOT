"""Minimal PDF text extractor used by the ingest pipeline.

Provides:
- extract_pdf_text_with_pages(path) -> List[Tuple[int, str]]

Uses PyMuPDF (pymupdf) which is listed in requirements.txt as `pymupdf`.
"""
from typing import List, Tuple
import os


def extract_pdf_text_with_pages(path: str) -> List[Tuple[int, str]]:
    """Extract plain text from each page of a PDF.

    Returns a list of (page_number, text) with page_number starting at 1.
    If extraction fails, raises the underlying exception.
    """
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        raise RuntimeError("PyMuPDF (fitz) is required for PDF extraction") from e

    if not os.path.exists(path):
        raise FileNotFoundError(path)

    doc = fitz.open(path)
    pages = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        text = page.get_text("text")
        pages.append((i + 1, text))
    doc.close()
    return pages
