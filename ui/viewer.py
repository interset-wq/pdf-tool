"""PDF viewer with lazy loading and caching."""

import customtkinter as ctk
from PIL import Image, ImageTk
import io
import threading
from concurrent.futures import ThreadPoolExecutor

from core.pdf_reader import PDFReader
from utils.fonts import FONT_BUTTON, FONT_SMALL, FONT_NORMAL


class PDFViewer(ctk.CTkFrame):
    """Optimized PDF viewer with lazy rendering and page cache."""

    def __init__(self, master, on_page_change=None, **kwargs):
        super().__init__(master, **kwargs)
        self.reader = PDFReader()
        self.current_page = 0
        self.zoom = 1.5
        self.scroll_mode = True
        self.on_page_change = on_page_change

        # Cache: page_num -> (ImageTk.PhotoImage, width, height)
        self._cache = {}
        self._page_positions = []  # (y_offset, height) for each page
        self._total_height = 0
        self._rendering = False
        self._executor = ThreadPoolExecutor(max_workers=2)

        self._setup_ui()

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Navigation bar
        nav_frame = ctk.CTkFrame(self, corner_radius=6, height=40)
        nav_frame.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 2))
        nav_frame.pack_propagate(False)

        # Left: page navigation
        left_nav = ctk.CTkFrame(nav_frame, fg_color="transparent")
        left_nav.pack(side="left", padx=6, pady=4)

        self.prev_btn = ctk.CTkButton(
            left_nav, text="<", width=28, height=26, font=FONT_BUTTON(11), command=self.prev_page
        )
        self.prev_btn.pack(side="left", padx=2)

        self.page_entry = ctk.CTkEntry(left_nav, width=48, height=26, justify="center", font=FONT_NORMAL(11))
        self.page_entry.pack(side="left", padx=3)
        self.page_entry.bind("<Return>", self._on_page_entry)

        self.page_label = ctk.CTkLabel(left_nav, text="/ 0", font=FONT_NORMAL(11))
        self.page_label.pack(side="left", padx=2)

        self.next_btn = ctk.CTkButton(
            left_nav, text=">", width=28, height=26, font=FONT_BUTTON(11), command=self.next_page
        )
        self.next_btn.pack(side="left", padx=2)

        # Center: mode + zoom
        center_nav = ctk.CTkFrame(nav_frame, fg_color="transparent")
        center_nav.pack(side="left", expand=True)

        self.scroll_mode_btn = ctk.CTkButton(
            center_nav, text="Scroll", width=52, height=26, font=FONT_SMALL(10),
            command=lambda: self.set_mode(True),
        )
        self.scroll_mode_btn.pack(side="left", padx=2)

        self.page_mode_btn = ctk.CTkButton(
            center_nav, text="Page", width=52, height=26, font=FONT_SMALL(10),
            command=lambda: self.set_mode(False),
        )
        self.page_mode_btn.pack(side="left", padx=2)

        self.zoom_out_btn = ctk.CTkButton(
            center_nav, text="-", width=28, height=26, font=FONT_BUTTON(11), command=self.zoom_out
        )
        self.zoom_out_btn.pack(side="left", padx=(8, 2))

        self.zoom_label = ctk.CTkLabel(center_nav, text="150%", width=50, font=FONT_SMALL(10))
        self.zoom_label.pack(side="left", padx=2)

        self.zoom_in_btn = ctk.CTkButton(
            center_nav, text="+", width=28, height=26, font=FONT_BUTTON(11), command=self.zoom_in
        )
        self.zoom_in_btn.pack(side="left", padx=2)

        self.zoom_fit_btn = ctk.CTkButton(
            center_nav, text="Fit", width=40, height=26, font=FONT_SMALL(10), command=self.zoom_fit
        )
        self.zoom_fit_btn.pack(side="left", padx=2)

        # Right: info
        right_nav = ctk.CTkFrame(nav_frame, fg_color="transparent")
        right_nav.pack(side="right", padx=6, pady=4)

        self.info_label = ctk.CTkLabel(right_nav, text="", font=FONT_SMALL(10))
        self.info_label.pack(side="right")

        # Canvas
        self.canvas_frame = ctk.CTkFrame(self, corner_radius=8)
        self.canvas_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.canvas_frame.grid_rowconfigure(0, weight=1)

        self.canvas = ctk.CTkCanvas(self.canvas_frame, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.v_scrollbar = ctk.CTkScrollbar(
            self.canvas_frame, orientation="vertical", command=self.canvas.yview
        )
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar = ctk.CTkScrollbar(
            self.canvas_frame, orientation="horizontal", command=self.canvas.xview
        )
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(
            yscrollcommand=self._on_scroll,
            xscrollcommand=self.h_scrollbar.set,
        )

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        self._update_ui()

    def _on_scroll(self, *args):
        self.v_scrollbar.set(*args)
        self._lazy_render()

    def _on_canvas_resize(self, event):
        if self.scroll_mode and self.reader.is_open:
            self._rebuild_layout()

    def set_mode(self, scroll: bool) -> None:
        if self.scroll_mode == scroll:
            return

        # Save current page before switching
        saved_page = self.current_page

        self.scroll_mode = scroll
        self._cache.clear()
        self._page_positions.clear()

        if self.reader.is_open:
            self._setup_view()

            # Restore page position
            if scroll:
                self._scroll_to_page(saved_page)
            else:
                self.current_page = saved_page
                self._render_single_page()
                self._update_ui()

            if self.on_page_change:
                self.on_page_change(self.current_page)

        self._update_mode_buttons()

    def _setup_view(self):
        self.canvas.delete("all")
        self._page_positions.clear()

        if self.scroll_mode:
            self._calculate_positions()
            self._lazy_render()
        else:
            self._render_single_page()

        self._update_ui()

    def _calculate_positions(self):
        """Pre-calculate page positions without rendering."""
        self._page_positions = []
        y = 0
        gap = 8
        canvas_width = max(self.canvas.winfo_width(), 600)

        for i in range(self.reader.page_count):
            page = self.reader.get_page(i)
            rect = page.rect
            scale = self.zoom
            w = rect.width * scale
            h = rect.height * scale
            self._page_positions.append((y, w, h))
            y += h + gap

        self._total_height = y
        self.canvas.configure(scrollregion=(0, 0, canvas_width, y))

    def _lazy_render(self):
        """Only render visible pages."""
        if not self.scroll_mode or not self.reader.is_open or self._rendering:
            return

        canvas_height = self.canvas.winfo_height()
        scroll_y = self.canvas.yview()[0] * self._total_height

        # Find visible range
        margin = 200  # pre-render margin
        visible_start = scroll_y - margin
        visible_end = scroll_y + canvas_height + margin

        canvas_width = max(self.canvas.winfo_width(), 600)

        for i, (y, w, h) in enumerate(self._page_positions):
            page_bottom = y + h
            if page_bottom < visible_start or y > visible_end:
                continue  # Skip non-visible pages

            if i not in self._cache:
                self._render_page_async(i)

            if i in self._cache:
                photo, pw, ph = self._cache[i]
                x = (canvas_width - pw) // 2
                self.canvas.create_image(x, y, anchor="nw", image=photo, tags=f"page_{i}")

        self._update_current_page()

    def _render_page_async(self, page_num: int):
        """Render a page in background thread."""
        if page_num in self._cache or self._rendering:
            return

        def _do_render():
            try:
                img_bytes = self.reader.render_page(page_num, self.zoom)
                img = Image.open(io.BytesIO(img_bytes))
                photo = ImageTk.PhotoImage(img)

                self.after(0, lambda: self._cache_page(page_num, photo, photo.width(), photo.height()))
            except Exception:
                pass

        self._executor.submit(_do_render)

    def _cache_page(self, page_num: int, photo, w: int, h: int):
        self._cache[page_num] = (photo, w, h)
        self._lazy_render()

    def _render_single_page(self):
        """Render single page for page mode."""
        self.canvas.delete("all")

        if self.current_page in self._cache:
            photo, w, h = self._cache[self.current_page]
        else:
            img_bytes = self.reader.render_page(self.current_page, self.zoom)
            img = Image.open(io.BytesIO(img_bytes))
            photo = ImageTk.PhotoImage(img)
            w, h = photo.width(), photo.height()
            self._cache[self.current_page] = (photo, w, h)

        canvas_width = max(self.canvas.winfo_width(), 600)
        canvas_height = max(self.canvas.winfo_height(), 400)

        x = (canvas_width - w) // 2
        y = (canvas_height - h) // 2

        self.canvas.create_image(x, y, anchor="nw", image=photo)
        self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

    def _rebuild_layout(self):
        """Recalculate positions and re-render on zoom/resize."""
        if not self.scroll_mode:
            return
        self.canvas.delete("all")
        self._cache.clear()
        self._calculate_positions()
        self._lazy_render()

    def _update_current_page(self):
        """Update current_page based on scroll position."""
        scroll_y = self.canvas.yview()[0] * self._total_height
        canvas_height = self.canvas.winfo_height()

        for i, (y, w, h) in enumerate(self._page_positions):
            if y + h > scroll_y:
                if self.current_page != i:
                    self.current_page = i
                    if self.on_page_change:
                        self.on_page_change(i)
                break

        self._update_ui()

    def open_pdf(self, file_path: str) -> None:
        self.reader.open(file_path)
        self.current_page = 0
        self._cache.clear()
        self._page_positions.clear()
        self._setup_view()

    def close_pdf(self) -> None:
        self.reader.close()
        self.canvas.delete("all")
        self._cache.clear()
        self._page_positions.clear()
        self._update_ui()

    def render(self) -> None:
        if not self.reader.is_open:
            return
        self._cache.clear()
        self._setup_view()

    def prev_page(self) -> None:
        if self.current_page > 0:
            self.current_page -= 1
            if self.scroll_mode:
                self._scroll_to_page(self.current_page)
            else:
                self._render_single_page()
                self._update_ui()
            if self.on_page_change:
                self.on_page_change(self.current_page)

    def next_page(self) -> None:
        if self.current_page < self.reader.page_count - 1:
            self.current_page += 1
            if self.scroll_mode:
                self._scroll_to_page(self.current_page)
            else:
                self._render_single_page()
                self._update_ui()
            if self.on_page_change:
                self.on_page_change(self.current_page)

    def go_to_page(self, page_num: int) -> None:
        if 0 <= page_num < self.reader.page_count:
            self.current_page = page_num
            if self.scroll_mode:
                self._scroll_to_page(page_num)
            else:
                self._render_single_page()
                self._update_ui()
            if self.on_page_change:
                self.on_page_change(self.current_page)

    def _scroll_to_page(self, page_num: int) -> None:
        if page_num >= len(self._page_positions):
            return
        y = self._page_positions[page_num][0]
        canvas_height = self.canvas.winfo_height()
        scroll_pos = y / max(self._total_height - canvas_height, 1)
        self.canvas.yview_moveto(scroll_pos)
        self._lazy_render()

    def go_to_start(self) -> None:
        self.go_to_page(0)

    def go_to_end(self) -> None:
        self.go_to_page(self.reader.page_count - 1)

    def zoom_in(self) -> None:
        self.zoom = min(self.zoom + 0.25, 5.0)
        self.render()

    def zoom_out(self) -> None:
        self.zoom = max(self.zoom - 0.25, 0.5)
        self.render()

    def zoom_fit(self) -> None:
        if not self.reader.is_open:
            return
        page = self.reader.get_page(self.current_page)
        canvas_width = max(self.canvas.winfo_width(), 400)
        self.zoom = canvas_width / page.rect.width
        self.render()

    def zoom_reset(self) -> None:
        self.zoom = 1.5
        self.render()

    def _on_page_entry(self, event) -> None:
        try:
            page_num = int(self.page_entry.get()) - 1
            self.go_to_page(page_num)
        except (ValueError, IndexError):
            pass

    def _on_mousewheel(self, event) -> None:
        if self.scroll_mode:
            self.canvas.yview_scroll(-3 if event.delta > 0 else 3, "units")
            self._update_current_page()
        else:
            if event.delta > 0:
                self.prev_page()
            else:
                self.next_page()

    def _update_mode_buttons(self) -> None:
        if self.scroll_mode:
            self.scroll_mode_btn.configure(fg_color=("dodgerblue", "#1f6aa5"))
            self.page_mode_btn.configure(fg_color=("gray75", "gray30"))
        else:
            self.scroll_mode_btn.configure(fg_color=("gray75", "gray30"))
            self.page_mode_btn.configure(fg_color=("dodgerblue", "#1f6aa5"))

    def _update_ui(self) -> None:
        has_pdf = self.reader.is_open
        total = self.reader.page_count if has_pdf else 0

        self.prev_btn.configure(
            state="normal" if has_pdf and self.current_page > 0 else "disabled"
        )
        self.next_btn.configure(
            state="normal" if has_pdf and self.current_page < total - 1 else "disabled"
        )
        self.zoom_in_btn.configure(state="normal" if has_pdf else "disabled")
        self.zoom_out_btn.configure(state="normal" if has_pdf else "disabled")
        self.zoom_fit_btn.configure(state="normal" if has_pdf else "disabled")

        if has_pdf:
            self.page_entry.configure(state="normal")
            self.page_entry.delete(0, "end")
            self.page_entry.insert(0, str(self.current_page + 1))
            self.page_label.configure(text=f"/ {total}")
            self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")

            page = self.reader.get_page(self.current_page)
            w, h = int(page.rect.width), int(page.rect.height)
            self.info_label.configure(text=f"{w} x {h} pt")
        else:
            self.page_entry.configure(state="disabled")
            self.page_entry.delete(0, "end")
            self.page_label.configure(text="/ 0")
            self.zoom_label.configure(text="100%")
            self.info_label.configure(text="")

        self._update_mode_buttons()
