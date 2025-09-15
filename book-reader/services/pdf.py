# services/pdf.py

import fitz
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QSize

def extract_pdf_cover(path: str, size: QSize = QSize(200, 300)) -> QPixmap | None:
    """
    Render the first page as a high-DPI raster thumbnail of the given size.
    """
    doc = fitz.open(path)
    page = doc.load_page(0)
    rect = page.rect
    zoom_x = size.width() / rect.width
    zoom_y = size.height() / rect.height
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat)
    doc.close()

    data = pix.tobytes("png")
    qpix = QPixmap()
    qpix.loadFromData(data)
    return qpix

def extract_pdf_page_image(path: str, page_number: int, size: QSize = QSize(800, 1200)) -> QPixmap | None:
    """
    Render the given page as a high-DPI raster image of the given size.
    """
    doc = fitz.open(path)
    page = doc.load_page(page_number)
    rect = page.rect
    zoom_x = size.width() / rect.width
    zoom_y = size.height() / rect.height
    mat = fitz.Matrix(zoom_x, zoom_y)
    pix = page.get_pixmap(matrix=mat)
    doc.close()

    data = pix.tobytes("png")
    qpix = QPixmap()
    qpix.loadFromData(data)
    return qpix

def extract_pdf_text(path: str) -> str:
    """
    Extract plain text from every page.
    """
    doc = fitz.open(path)
    text = [p.get_text("text") for p in doc]
    doc.close()
    return "\n".join(text)

def extract_pdf_metadata(path: str) -> dict[str,str]:
    """
    Read title/author from PDF metadata.
    """
    doc = fitz.open(path)
    meta = doc.metadata or {}
    doc.close()
    return {
        "title": meta.get("title", ""),
        "author": meta.get("author", "")
    }
import io
import contextlib
import fitz

def extract_pdf_page_text(path: str, page_number: int) -> str:
    """
    Return plain text of a single PDF page, while suppressing MuPDF
    font-lookup warnings that normally go to stderr.
    """
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        doc = fitz.open(path)
        page = doc.load_page(page_number)
        text = page.get_text("text")
        doc.close()
    return text
