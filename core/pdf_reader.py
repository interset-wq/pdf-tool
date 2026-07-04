"""PDF reader module using PyMuPDF."""

from pathlib import Path

import fitz  # PyMuPDF


class PDFReader:
    """Read and render PDF files."""

    def __init__(self):
        self.document: fitz.Document | None = None
        self.file_path: Path | None = None

    @property
    def page_count(self) -> int:
        return self.document.page_count if self.document else 0

    @property
    def is_open(self) -> bool:
        return self.document is not None

    def open(self, file_path: str | Path) -> None:
        self.file_path = Path(file_path)
        self.document = fitz.open(self.file_path)

    def close(self) -> None:
        if self.document:
            self.document.close()
            self.document = None
            self.file_path = None

    def get_page(self, page_num: int) -> fitz.Page:
        if not self.document:
            raise RuntimeError("No PDF loaded")
        return self.document.load_page(page_num)

    def render_page(self, page_num: int, zoom: float = 1.0) -> bytes:
        """Render a page to PNG bytes."""
        page = self.get_page(page_num)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        return pix.tobytes("png")

    def get_page_text(self, page_num: int) -> str:
        page = self.get_page(page_num)
        return page.get_text()

    def get_metadata(self) -> dict:
        if not self.document:
            return {}
        return self.document.metadata or {}

    def search_text(self, query: str) -> list[dict]:
        """Search for text across all pages."""
        results = []
        for page_num in range(self.page_count):
            page = self.get_page(page_num)
            hits = page.search_for(query)
            for hit in hits:
                results.append({"page": page_num, "rect": hit})
        return results
