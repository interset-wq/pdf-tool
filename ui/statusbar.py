"""Status bar widget for displaying app state and feedback."""

import customtkinter as ctk
from utils.fonts import FONT_SMALL


class StatusBar(ctk.CTkFrame):
    """Bottom status bar with status text and info."""

    def __init__(self, master, **kwargs):
        super().__init__(master, height=28, **kwargs)
        self.pack_propagate(False)
        self._setup_ui()

    def _setup_ui(self):
        # Left: status text
        self.status_var = ctk.StringVar(value="Ready")
        self.status_label = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=FONT_SMALL(11),
            anchor="w",
        )
        self.status_label.pack(side="left", padx=12, pady=4)

        # Right: shortcuts hint
        shortcuts_text = "Ctrl+O Open  |  <- -> Navigate  |  +/- Zoom"
        self.shortcuts_label = ctk.CTkLabel(
            self,
            text=shortcuts_text,
            font=FONT_SMALL(10),
            anchor="e",
        )
        self.shortcuts_label.pack(side="right", padx=12, pady=4)

    def set_status(self, text: str) -> None:
        self.status_var.set(text)

    def clear(self) -> None:
        self.status_var.set("Ready")
