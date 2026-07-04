"""PDF operations: merge, split, rotate, reorder, metadata, page numbers."""

from pathlib import Path

import pikepdf
import fitz  # PyMuPDF


class PDFMerger:
    """Merge multiple PDF files."""

    def merge(self, input_paths: list[str | Path], output_path: str | Path) -> None:
        output = pikepdf.Pdf.new()
        for path in input_paths:
            src = pikepdf.open(path)
            output.pages.extend(src.pages)
        output.save(output_path)


class PDFSplitter:
    """Split PDF into multiple files."""

    def split_by_pages(
        self, input_path: str | Path, output_dir: str | Path, prefix: str = "split"
    ) -> list[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        src = pikepdf.open(input_path)
        output_files = []

        for i, page in enumerate(src.pages):
            dst = pikepdf.Pdf.new()
            dst.pages.append(page)
            out_path = output_dir / f"{prefix}_{i + 1:03d}.pdf"
            dst.save(out_path)
            output_files.append(out_path)

        return output_files

    def extract_pages(
        self, input_path: str | Path, pages: list[int], output_path: str | Path
    ) -> None:
        src = pikepdf.open(input_path)
        dst = pikepdf.Pdf.new()
        for page_num in pages:
            if 0 <= page_num < len(src.pages):
                dst.pages.append(src.pages[page_num])
        dst.save(output_path)

    def delete_pages(
        self, input_path: str | Path, pages: list[int], output_path: str | Path
    ) -> None:
        src = pikepdf.open(input_path)
        dst = pikepdf.Pdf.new()
        for i, page in enumerate(src.pages):
            if i not in pages:
                dst.pages.append(page)
        dst.save(output_path)

    def reorder_pages(
        self, input_path: str | Path, new_order: list[int], output_path: str | Path
    ) -> None:
        src = pikepdf.open(input_path)
        dst = pikepdf.Pdf.new()
        for idx in new_order:
            if 0 <= idx < len(src.pages):
                dst.pages.append(src.pages[idx])
        dst.save(output_path)


class PDFRotator:
    """Rotate PDF pages."""

    def rotate_page(
        self, input_path: str | Path, page_num: int, angle: int, output_path: str | Path
    ) -> None:
        src = pikepdf.open(input_path)
        page = src.pages[page_num]
        existing = int(page.get("/Rotate", 0))
        page["/Rotate"] = pikepdf.Object.parse(str((existing + angle) % 360))
        src.save(output_path)

    def rotate_all(
        self, input_path: str | Path, angle: int, output_path: str | Path
    ) -> None:
        src = pikepdf.open(input_path)
        for page in src.pages:
            existing = int(page.get("/Rotate", 0))
            page["/Rotate"] = pikepdf.Object.parse(str((existing + angle) % 360))
        src.save(output_path)


class PDFMetadata:
    """Read and write PDF metadata."""

    def get_metadata(self, file_path: str | Path) -> dict:
        doc = fitz.open(file_path)
        meta = doc.metadata or {}
        doc.close()
        return {
            "title": meta.get("title", ""),
            "author": meta.get("author", ""),
            "subject": meta.get("subject", ""),
            "creator": meta.get("creator", ""),
            "producer": meta.get("producer", ""),
            "page_count": doc.page_count if hasattr(doc, "page_count") else 0,
        }

    def set_metadata(
        self,
        input_path: str | Path,
        output_path: str | Path,
        title: str = "",
        author: str = "",
        subject: str = "",
    ) -> None:
        src = pikepdf.open(input_path)
        with src.open_metadata() as meta:
            if title:
                meta["dc:title"] = title
            if author:
                meta["dc:creator"] = [author]
            if subject:
                meta["dc:description"] = subject
        src.save(output_path)


class PDFPageNumber:
    """Add page numbers to PDF."""

    def add_page_numbers(
        self,
        input_path: str | Path,
        output_path: str | Path,
        position: str = "bottom-center",
        font_size: int = 12,
        start: int = 1,
    ) -> None:
        doc = fitz.open(input_path)

        for i, page in enumerate(doc):
            rect = page.rect
            text = str(start + i)

            # Calculate position
            if "bottom" in position:
                y = rect.height - 30
            else:
                y = 40

            if "left" in position:
                x = 50
            elif "right" in position:
                x = rect.width - 50 - len(text) * font_size * 0.5
            else:
                x = rect.width / 2 - len(text) * font_size * 0.25

            page.insert_text(
                fitz.Point(x, y),
                text,
                fontsize=font_size,
                fontname="helv",
                color=(0, 0, 0),
            )

        doc.save(output_path)
        doc.close()


class PDFTextExtractor:
    """Extract text from PDF."""

    def extract_all(self, file_path: str | Path) -> str:
        doc = fitz.open(file_path)
        texts = []
        for page in doc:
            texts.append(page.get_text())
        doc.close()
        return "\n\n".join(texts)

    def extract_page(self, file_path: str | Path, page_num: int) -> str:
        doc = fitz.open(file_path)
        text = doc.load_page(page_num).get_text()
        doc.close()
        return text

    def extract_pages(
        self, file_path: str | Path, pages: list[int], output_path: str | Path
    ) -> None:
        doc = fitz.open(file_path)
        texts = []
        for p in pages:
            if 0 <= p < doc.page_count:
                texts.append(f"--- Page {p + 1} ---\n{doc.load_page(p).get_text()}")
        doc.close()
        Path(output_path).write_text("\n\n".join(texts), encoding="utf-8")
