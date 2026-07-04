"""PDF conversion utilities."""

from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class PDFToImage:
    """Convert PDF pages to images."""

    def to_png(
        self,
        input_path: str | Path,
        output_dir: str | Path,
        zoom: float = 2.0,
    ) -> list[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = fitz.open(input_path)
        output_files = []

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            out_path = output_dir / f"page_{page_num + 1:03d}.png"
            pix.save(out_path)
            output_files.append(out_path)

        doc.close()
        return output_files

    def to_jpg(
        self,
        input_path: str | Path,
        output_dir: str | Path,
        zoom: float = 2.0,
        quality: int = 95,
    ) -> list[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        doc = fitz.open(input_path)
        output_files = []

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            out_path = output_dir / f"page_{page_num + 1:03d}.jpg"
            img.save(out_path, quality=quality)
            output_files.append(out_path)

        doc.close()
        return output_files

    def page_to_image(
        self,
        input_path: str | Path,
        page_num: int,
        output_path: str | Path,
        zoom: float = 2.0,
    ) -> Path:
        doc = fitz.open(input_path)
        page = doc.load_page(page_num)
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        pix.save(output_path)
        doc.close()
        return Path(output_path)


class ImageToPDF:
    """Convert images to PDF."""

    def images_to_pdf(
        self,
        image_paths: list[str | Path],
        output_path: str | Path,
    ) -> None:
        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4

        for img_path in image_paths:
            img = Image.open(img_path)
            img_width, img_height = img.size

            scale = min(width / img_width, height / img_height)
            new_width = img_width * scale
            new_height = img_height * scale
            x = (width - new_width) / 2
            y = (height - new_height) / 2

            c.drawImage(str(img_path), x, y, new_width, new_height)
            c.showPage()

        c.save()

    def image_to_pdf(
        self,
        image_path: str | Path,
        output_path: str | Path,
    ) -> None:
        self.images_to_pdf([image_path], output_path)


class PDFToText:
    """Extract text from PDF."""

    def extract_text(self, input_path: str | Path) -> str:
        doc = fitz.open(input_path)
        full_text = []

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            full_text.append(page.get_text())

        doc.close()
        return "\n".join(full_text)

    def extract_page_text(self, input_path: str | Path, page_num: int) -> str:
        doc = fitz.open(input_path)
        page = doc.load_page(page_num)
        text = page.get_text()
        doc.close()
        return text
