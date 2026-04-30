"""
Load clinical notes / prescriptions from various file formats into plain text.

Supports:
    .txt, .md         — read directly
    .pdf              — pypdf (text-layer PDFs) with OCR fallback
    .png/.jpg/.jpeg/  — Tesseract OCR via pytesseract
    .tiff/.bmp/.webp

Tesseract must be installed at the OS level for image / scanned-PDF support:
    macOS:   brew install tesseract
    Ubuntu:  sudo apt-get install tesseract-ocr
    Windows: https://github.com/UB-Mannheim/tesseract/wiki
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union

SUPPORTED_TEXT = {".txt", ".md"}
SUPPORTED_PDF = {".pdf"}
SUPPORTED_IMAGE = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}
SUPPORTED_ALL = SUPPORTED_TEXT | SUPPORTED_PDF | SUPPORTED_IMAGE


class UnsupportedFileType(Exception):
    """Raised when the uploaded file extension is not handled."""


def _read_text(data: bytes) -> str:
    # Try utf-8 then latin-1 as a fallback (clinical notes from older systems
    # are sometimes in cp1252/latin-1).
    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _read_pdf(data: bytes) -> str:
    """Extract text from a PDF; OCR each page that yields no text."""
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise ImportError("pypdf is required for PDF support: pip install pypdf") from e

    reader = PdfReader(io.BytesIO(data))
    chunks = []
    pages_needing_ocr = []

    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").strip()
        if text:
            chunks.append(text)
        else:
            pages_needing_ocr.append(i)

    if pages_needing_ocr:
        ocr_text = _ocr_pdf_pages(data, pages_needing_ocr)
        if ocr_text:
            chunks.append(ocr_text)

    return "\n\n".join(chunks).strip()


def _ocr_pdf_pages(data: bytes, page_indices: list[int]) -> str:
    """OCR specific pages of a PDF. Silently returns '' if pdf2image/Tesseract
    aren't installed — text-layer PDFs still work without these."""
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
    except ImportError:
        return ""

    try:
        images = convert_from_bytes(data)
    except Exception:
        # poppler not installed or corrupted PDF — skip OCR gracefully
        return ""

    out = []
    for idx in page_indices:
        if idx < len(images):
            try:
                out.append(pytesseract.image_to_string(images[idx]))
            except Exception:
                pass
    return "\n\n".join(t.strip() for t in out if t.strip())


def _read_image(data: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract
    except ImportError as e:
        raise ImportError(
            "Image OCR requires Pillow and pytesseract: "
            "pip install Pillow pytesseract  (and install Tesseract OS-side)"
        ) from e

    image = Image.open(io.BytesIO(data))
    return pytesseract.image_to_string(image).strip()


def load_document(file: Union[str, Path, bytes], filename: str | None = None) -> str:
    """Top-level entry point.

    Args:
        file:     A path to a file, OR raw bytes (e.g. from a Streamlit upload).
        filename: When passing bytes, supply the original filename so we can
                  dispatch on its extension.

    Returns:
        Plain text extracted from the document. May be empty if extraction failed.
    """
    if isinstance(file, (str, Path)):
        path = Path(file)
        data = path.read_bytes()
        suffix = path.suffix.lower()
    else:
        if not filename:
            raise ValueError("filename is required when passing raw bytes")
        data = file
        suffix = Path(filename).suffix.lower()

    if suffix in SUPPORTED_TEXT:
        return _read_text(data)
    if suffix in SUPPORTED_PDF:
        return _read_pdf(data)
    if suffix in SUPPORTED_IMAGE:
        return _read_image(data)

    raise UnsupportedFileType(
        f"Unsupported file type '{suffix}'. Supported: "
        f"{sorted(SUPPORTED_ALL)}"
    )
