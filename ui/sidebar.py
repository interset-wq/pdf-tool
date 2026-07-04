"""Sidebar with page thumbnails."""

import customtkinter as ctk
from PIL import Image
import threading

import fitz  # PyMuPDF
from utils.fonts import FONT_TITLE, FONT_SMALL, FONT_NORMAL


class Sidebar(ctk.CTkFrame):
    """Sidebar with page thumbnails."""

    def __init__(self, master, on_page_select=None, **kwargs):
        super().__init__(master, width=180, **kwargs)
        self.on_page_select = on_page_select
        self.pdf_doc = None
        self._images = []
        self._current_page = -1
        self.pack_propagate(False)
        self._setup_ui()

    def _setup_ui(self):
        self.grid_rowconfigure(2, weight=1)

        # File info
        info_frame = ctk.CTkFrame(self, corner_radius=6)
        info_frame.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 4))

        self.file_name_label = ctk.CTkLabel(
            info_frame, text="No file", font=FONT_TITLE(11), anchor="w"
        )
        self.file_name_label.pack(fill="x", padx=8, pady=(6, 1))

        self.file_info_label = ctk.CTkLabel(
            info_frame, text="", font=FONT_SMALL(9), anchor="w"
        )
        self.file_info_label.pack(fill="x", padx=8, pady=(0, 6))

        # Pages header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=1, column=0, sticky="ew", padx=8, pady=(2, 0))

        ctk.CTkLabel(header, text="Pages", font=FONT_TITLE(10)).pack(side="left")
        self.page_count_label = ctk.CTkLabel(
            header, text="0", font=FONT_SMALL(9)
        )
        self.page_count_label.pack(side="right")

        # Pages list
        self.pages_frame = ctk.CTkScrollableFrame(self, corner_radius=6)
        self.pages_frame.grid(row=2, column=0, sticky="nsew", padx=6, pady=(4, 6))

    def set_document(self, doc: fitz.Document | None) -> None:
        self.pdf_doc = doc
        self._images = []
        self._current_page = -1
        self._render_all()

    def _render_all(self):
        for w in self.pages_frame.winfo_children():
            w.destroy()

        if not self.pdf_doc:
            self.page_count_label.configure(text="0")
            return

        count = self.pdf_doc.page_count
        self.page_count_label.configure(text=str(count))

        self._items = [None] * count

        for i in range(count):
            item = ctk.CTkFrame(self.pages_frame, corner_radius=4, height=70)
            item.pack(fill="x", pady=2)
            item.pack_propagate(False)

            lbl = ctk.CTkLabel(item, text=f"Page {i + 1}", font=FONT_SMALL(9))
            lbl.pack(expand=True)

            item.bind("<Button-1>", lambda e, idx=i: self._on_click(idx))
            lbl.bind("<Button-1>", lambda e, idx=i: self._on_click(idx))
            lbl.configure(cursor="hand2")

            self._items[i] = (item, lbl)

        threading.Thread(target=self._render_thread, daemon=True).start()

    def get_optimal_width(self) -> int:
        """Calculate optimal sidebar width based on PDF aspect ratio."""
        if not self.pdf_doc or self.pdf_doc.page_count == 0:
            return 180

        page = self.pdf_doc.load_page(0)
        rect = page.rect
        aspect = rect.width / rect.height

        # Landscape (slides): wider sidebar
        # Portrait (documents): narrower sidebar
        if aspect > 1.3:  # Landscape
            return 220
        elif aspect < 0.8:  # Tall portrait
            return 150
        else:  # Standard A4/Letter
            return 180

    def _render_thread(self):
        if not self.pdf_doc:
            return

        thumb_w, thumb_h = 100, 50
        count = self.pdf_doc.page_count

        for i in range(count):
            if not self.pdf_doc:
                break
            try:
                page = self.pdf_doc.load_page(i)
                rect = page.rect
                zoom = min(thumb_w / rect.width, thumb_h / rect.height)
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(thumb_w, thumb_h))
                self.after(0, lambda idx=i, ci=ctk_img: self._set_thumb(idx, ci))
            except Exception:
                pass

    def _set_thumb(self, idx: int, ctk_img):
        if not hasattr(self, '_items') or idx >= len(self._items) or not self._items[idx]:
            return

        item, old_lbl = self._items[idx]
        old_lbl.destroy()

        lbl = ctk.CTkLabel(item, image=ctk_img, text="")
        lbl.pack(pady=(6, 0))

        num = ctk.CTkLabel(item, text=str(idx + 1), font=FONT_SMALL(9))
        num.pack()

        self._images.append(ctk_img)

        for w in [item, lbl, num]:
            w.bind("<Button-1>", lambda e, i=idx: self._on_click(i))
            w.configure(cursor="hand2")

    def highlight_page(self, page_num: int) -> None:
        if not hasattr(self, '_items') or not self._items:
            return

        if 0 <= self._current_page < len(self._items) and self._items[self._current_page]:
            item, _ = self._items[self._current_page]
            item.configure(fg_color=("gray92", "gray17"))

        self._current_page = page_num
        if 0 <= page_num < len(self._items) and self._items[page_num]:
            item, _ = self._items[page_num]
            item.configure(fg_color=("gray75", "gray30"))

    def update_file_info(self, name: str, pages: int, size: str) -> None:
        self.file_name_label.configure(text=name)
        self.file_info_label.configure(text=f"{pages} pages | {size}")

    def clear(self) -> None:
        self.pdf_doc = None
        self._images = []
        self._current_page = -1
        for w in self.pages_frame.winfo_children():
            w.destroy()
        self.page_count_label.configure(text="0")
        self.file_name_label.configure(text="No file")
        self.file_info_label.configure(text="")

    def _on_click(self, page_num: int) -> None:
        if self.on_page_select:
            self.on_page_select(page_num)
