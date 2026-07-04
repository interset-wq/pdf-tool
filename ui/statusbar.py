"""Status bar widget inspired by PowerPoint."""

import customtkinter as ctk
from utils.fonts import FONT_SMALL


class StatusBar(ctk.CTkFrame):
    """Bottom status bar with page info, status, and zoom controls."""

    def __init__(self, master, **kwargs):
        super().__init__(master, height=32, **kwargs)
        self.pack_propagate(False)
        self._setup_ui()

    def _setup_ui(self):
        # Left: Page info
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.pack(side="left", padx=12, pady=6)

        self.page_info = ctk.CTkLabel(
            left_frame, text="Page 0 / 0", font=FONT_SMALL(11)
        )
        self.page_info.pack(side="left")

        # Separator
        ctk.CTkFrame(self, width=1, fg_color=("gray70", "gray40")).pack(
            side="left", fill="y", padx=12, pady=6
        )

        # Status text
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            left_frame, textvariable=self.status_var, font=FONT_SMALL(11)
        )
        self.status_label.pack(side="left", padx=8)

        # Right: Zoom controls
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right", padx=12, pady=6)

        # Zoom out
        self.zoom_out_btn = ctk.CTkButton(
            right_frame, text="-", width=24, height=22, font=FONT_SMALL(10),
            corner_radius=4, command=self._on_zoom_out
        )
        self.zoom_out_btn.pack(side="left")

        # Zoom slider
        self.zoom_slider = ctk.CTkSlider(
            right_frame, from_=25, to=500, number_of_steps=19,
            width=120, height=16, command=self._on_slider_change
        )
        self.zoom_slider.set(150)
        self.zoom_slider.pack(side="left", padx=4)

        # Zoom in
        self.zoom_in_btn = ctk.CTkButton(
            right_frame, text="+", width=24, height=22, font=FONT_SMALL(10),
            corner_radius=4, command=self._on_zoom_in
        )
        self.zoom_in_btn.pack(side="left")

        # Zoom label
        self.zoom_label = ctk.CTkLabel(
            right_frame, text="150%", font=FONT_SMALL(10), width=45
        )
        self.zoom_label.pack(side="left", padx=(8, 0))

        # Callbacks
        self._on_zoom_callback = None

    def set_zoom_callback(self, callback):
        self._on_zoom_callback = callback

    def _on_slider_change(self, value):
        zoom = int(value)
        self.zoom_label.configure(text=f"{zoom}%")
        if self._on_zoom_callback:
            self._on_zoom_callback(zoom / 100)

    def _on_zoom_in(self):
        current = self.zoom_slider.get()
        new_val = min(current + 25, 500)
        self.zoom_slider.set(new_val)
        self._on_slider_change(new_val)

    def _on_zoom_out(self):
        current = self.zoom_slider.get()
        new_val = max(current - 25, 25)
        self.zoom_slider.set(new_val)
        self._on_slider_change(new_val)

    def update_page_info(self, current: int, total: int) -> None:
        self.page_info.configure(text=f"Page {current} / {total}")

    def update_zoom(self, zoom: float) -> None:
        percent = int(zoom * 100)
        self.zoom_slider.set(percent)
        self.zoom_label.configure(text=f"{percent}%")

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def clear(self) -> None:
        self.status_var.set("Ready")
