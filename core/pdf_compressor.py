"""PDF compression and optimization."""

from pathlib import Path

import fitz  # PyMuPDF
import pikepdf


class PDFCompressor:
    """Compress and optimize PDF files."""

    def compress(
        self,
        input_path: str | Path,
        output_path: str | Path,
        image_quality: int = 75,
        dpi: int = 150,
    ) -> None:
        """Compress PDF by re-rendering images at lower quality."""
        src = fitz.open(input_path)
        dst = fitz.open()

        for page_num in range(src.page_count):
            page = src.load_page(page_num)
            mat = fitz.Matrix(dpi / 72, dpi / 72)
            pix = page.get_pixmap(matrix=mat)

            img_doc = fitz.open()
            img_page = img_doc.new_page(width=page.rect.width, height=page.rect.height)

            img = fitz.Pixmap(fitz.csRGB, pix)
            img_bytes = img.tobytes("jpeg")
            img_page.insert_image(page.rect, stream=img_bytes)

            dst.insert_pdf(img_doc)
            img_doc.close()

        dst.save(output_path, garbage=4, deflate=True)
        dst.close()
        src.close()

    def get_file_size(self, file_path: str | Path) -> int:
        return Path(file_path).stat().st_size

    def format_size(self, size_bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def optimize(
        self,
        input_path: str | Path,
        output_path: str | Path,
    ) -> dict:
        """Optimize PDF and return size comparison."""
        original_size = self.get_file_size(input_path)

        src = pikepdf.open(input_path)
        src.save(output_path, garbage=4, deflate=True)
        src.close()

        new_size = self.get_file_size(output_path)
        reduction = ((original_size - new_size) / original_size) * 100

        return {
            "original": self.format_size(original_size),
            "compressed": self.format_size(new_size),
            "reduction": f"{reduction:.1f}%",
        }
