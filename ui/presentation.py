"""Fullscreen presentation mode for PDF."""

import customtkinter as ctk
from PIL import Image, ImageTk
import io

from core.pdf_reader import PDFReader


class PresentationMode(ctk.CTkToplevel):
    """Fullscreen PDF presentation/slideshow mode."""

    def __init__(self, master, file_path: str, start_page: int = 0):
        super().__init__(master)
        self.reader = PDFReader()
        self.file_path = file_path
        self.current_page = start_page
        self.zoom = 1.0
        self._photo = None

        self.reader.open(file_path)
        self._setup_window()
        self._setup_ui()
        self._render_page()

    def _setup_window(self):
        self.title("Presentation Mode")
        self.overrideredirect(True)  # Remove title bar
        self.configure(bg="black")

        # Get screen size
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # Cover entire screen
        self.geometry(f"{screen_w}x{screen_h}+0+0")
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Canvas for rendering
        self.canvas = ctk.CTkCanvas(self, bg="black", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Controls overlay (auto-hide)
        self.controls = ctk.CTkFrame(self, fg_color="black", height=60)
        self.controls.grid(row=1, column=0, sticky="ew")
        self.controls.grid_propagate(False)

        # Control buttons
        btn_style = {"fg_color": "gray30", "hover_color": "gray50", "height": 36}

        self.prev_btn = ctk.CTkButton(
            self.controls, text="<", width=50, command=self.prev_page, **btn_style
        )
        self.prev_btn.pack(side="left", padx=10, pady=12)

        self.page_label = ctk.CTkLabel(
            self.controls, text="1 / 1", font=("", 14), text_color="white"
        )
        self.page_label.pack(side="left", padx=20)

        self.next_btn = ctk.CTkButton(
            self.controls, text=">", width=50, command=self.next_page, **btn_style
        )
        self.next_btn.pack(side="left", padx=10, pady=12)

        # Zoom controls
        self.zoom_out_btn = ctk.CTkButton(
            self.controls, text="-", width=40, command=self.zoom_out, **btn_style
        )
        self.zoom_out_btn.pack(side="right", padx=10, pady=12)

        self.zoom_label = ctk.CTkLabel(
            self.controls, text="100%", font=("", 12), text_color="white"
        )
        self.zoom_label.pack(side="right", padx=10)

        self.zoom_in_btn = ctk.CTkButton(
            self.controls, text="+", width=40, command=self.zoom_in, **btn_style
        )
        self.zoom_in_btn.pack(side="right", padx=10, pady=12)

        # Exit button
        self.exit_btn = ctk.CTkButton(
            self.controls, text="Exit", width=60, command=self.exit_presentation,
            fg_color="gray50", hover_color="gray70", height=36
        )
        self.exit_btn.pack(side="right", padx=10, pady=12)

        # Bindings
        self.bind("<Escape>", lambda e: self.exit_presentation())
        self.bind("<Left>", lambda e: self.prev_page())
        self.bind("<Right>", lambda e: self.next_page())
        self.bind("<space>", lambda e: self.next_page())
        self.bind("<Up>", lambda e: self.zoom_in())
        self.bind("<Down>", lambda e: self.zoom_out())
        self.bind("<Home>", lambda e: self.go_to_start())
        self.bind("<End>", lambda e: self.go_to_end())
        self.bind("<Motion>", self._show_controls)
        self.bind("<Key>", self._on_key)
        self.bind("<Configure>", self._on_resize)

        # Auto-hide controls
        self._controls_visible = True
        self._hide_after_id = None
        self._schedule_hide()

    def _render_page(self):
        if not self.reader.is_open:
            return

        # Ensure window is fully rendered
        self.update_idletasks()

        # Use actual window size
        win_w = self.winfo_width()
        win_h = self.winfo_height()

        # Fallback to screen size if window not ready
        if win_w <= 1:
            win_w = self.winfo_screenwidth()
        if win_h <= 1:
            win_h = self.winfo_screenheight()

        page = self.reader.get_page(self.current_page)
        page_w = page.rect.width
        page_h = page.rect.height

        # Fit to screen with padding
        padding = 40
        avail_w = win_w - padding * 2
        avail_h = win_h - padding * 2

        scale_w = avail_w / page_w
        scale_h = avail_h / page_h
        self.zoom = min(scale_w, scale_h)

        img_bytes = self.reader.render_page(self.current_page, self.zoom)
        img = Image.open(io.BytesIO(img_bytes))
        self._photo = ImageTk.PhotoImage(img)

        self.canvas.delete("all")
        # Center the image
        x = (win_w - self._photo.width()) // 2
        y = (win_h - self._photo.height()) // 2
        self.canvas.create_image(x, y, anchor="nw", image=self._photo)

        self._update_ui()

    def _update_ui(self):
        total = self.reader.page_count
        self.page_label.configure(text=f"{self.current_page + 1} / {total}")
        self.zoom_label.configure(text=f"{int(self.zoom * 100)}%")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_page()

    def next_page(self):
        if self.current_page < self.reader.page_count - 1:
            self.current_page += 1
            self._render_page()

    def go_to_start(self):
        self.current_page = 0
        self._render_page()

    def go_to_end(self):
        self.current_page = self.reader.page_count - 1
        self._render_page()

    def zoom_in(self):
        self.zoom = min(self.zoom + 0.1, 3.0)
        self._render_page()

    def zoom_out(self):
        self.zoom = max(self.zoom - 0.1, 0.3)
        self._render_page()

    def _on_key(self, event):
        if event.keysym.isdigit():
            pass

    def _on_resize(self, event):
        if event.widget == self:
            self._render_page()

    def _show_controls(self, event=None):
        if not self._controls_visible:
            self.controls.grid(row=1, column=0, sticky="ew")
            self._controls_visible = True
        self._schedule_hide()

    def _schedule_hide(self):
        if self._hide_after_id:
            self.after_cancel(self._hide_after_id)
        self._hide_after_id = self.after(3000, self._hide_controls)

    def _hide_controls(self):
        self.controls.grid_forget()
        self._controls_visible = False

    def exit_presentation(self):
        self.reader.close()
        self.destroy()
