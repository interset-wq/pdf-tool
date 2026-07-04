"""PDF security operations: encrypt, decrypt, watermark."""

from pathlib import Path

import fitz  # PyMuPDF
import pikepdf
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class PDFSecurity:
    """PDF encryption and decryption."""

    def encrypt(
        self,
        input_path: str | Path,
        output_path: str | Path,
        user_password: str,
        owner_password: str | None = None,
    ) -> None:
        owner = owner_password or user_password
        src = pikepdf.open(input_path)
        src.save(
            output_path,
            encryption=pikepdf.Encryption(
                user=user_password, owner=owner, R=6
            ),
        )
        src.close()

    def decrypt(
        self,
        input_path: str | Path,
        output_path: str | Path,
        password: str,
    ) -> None:
        src = pikepdf.open(input_path, password=password)
        src.save(output_path)
        src.close()

    def is_encrypted(self, file_path: str | Path) -> bool:
        try:
            pikepdf.open(file_path)
            return False
        except pikepdf.PasswordError:
            return True

    def remove_password(
        self,
        input_path: str | Path,
        output_path: str | Path,
        password: str,
    ) -> None:
        src = pikepdf.open(input_path, password=password)
        src.save(output_path)
        src.close()


class PDFWatermark:
    """Add watermark to PDF."""

    def add_text_watermark(
        self,
        input_path: str | Path,
        output_path: str | Path,
        text: str,
        font_size: int = 60,
        opacity: float = 0.3,
        rotation: float = 45,
    ) -> None:
        doc = fitz.open(input_path)

        for page in doc:
            rect = page.rect
            center_x = rect.width / 2
            center_y = rect.height / 2

            page.insert_text(
                fitz.Point(center_x - len(text) * font_size * 0.3, center_y),
                text,
                fontsize=font_size,
                fontname="helv",
                color=(0.8, 0.8, 0.8),
                rotate=rotation,
                overlay=True,
            )

        doc.save(output_path)
        doc.close()

    def add_image_watermark(
        self,
        input_path: str | Path,
        output_path: str | Path,
        image_path: str | Path,
        opacity: float = 0.3,
        scale: float = 0.3,
    ) -> None:
        doc = fitz.open(input_path)
        img_rect = fitz.Rect(0, 0, 200 * scale, 200 * scale)

        for page in doc:
            rect = page.rect
            x = (rect.width - img_rect.width) / 2
            y = (rect.height - img_rect.height) / 2
            img_rect.move(x, y)
            page.insert_image(img_rect, filename=str(image_path), overlay=True)

        doc.save(output_path)
        doc.close()
