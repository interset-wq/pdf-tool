"""Toolbar with grouped actions, theme switch, and sidebar toggle."""

import customtkinter as ctk
from utils.fonts import FONT_SMALL, FONT_BUTTON


class Toolbar(ctk.CTkFrame):
    """Top toolbar with file, edit, convert, security actions."""

    def __init__(self, master, commands: dict | None = None, **kwargs):
        super().__init__(master, height=56, **kwargs)
        self.commands = commands or {}
        self.pack_propagate(False)
        self._setup_ui()

    def _setup_ui(self):
        # Sidebar toggle (leftmost)
        self.sidebar_toggle = ctk.CTkButton(
            self,
            text="Panel",
            width=50,
            height=28,
            font=FONT_BUTTON(),
            command=self._cmd("toggle_sidebar"),
        )
        self.sidebar_toggle.grid(row=0, column=0, padx=(12, 4), pady=14, sticky="w")

        # File group
        file_frame = ctk.CTkFrame(self, fg_color="transparent")
        file_frame.grid(row=0, column=1, padx=4, pady=10, sticky="w")

        ctk.CTkLabel(file_frame, text="File", font=FONT_SMALL()).pack(anchor="w")
        btn_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        self._create_button(btn_frame, "Open", "open")
        self._create_button(btn_frame, "Save", "save")

        # Edit group
        edit_frame = ctk.CTkFrame(self, fg_color="transparent")
        edit_frame.grid(row=0, column=2, padx=4, pady=10, sticky="w")

        ctk.CTkLabel(edit_frame, text="Edit", font=FONT_SMALL()).pack(anchor="w")
        btn_frame = ctk.CTkFrame(edit_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        self._create_button(btn_frame, "Merge", "merge")
        self._create_button(btn_frame, "Split", "split")
        self._create_button(btn_frame, "Rotate", "rotate")
        self._create_button(btn_frame, "Reorder", "reorder")

        # Convert group
        convert_frame = ctk.CTkFrame(self, fg_color="transparent")
        convert_frame.grid(row=0, column=3, padx=4, pady=10, sticky="w")

        ctk.CTkLabel(convert_frame, text="Convert", font=FONT_SMALL()).pack(anchor="w")
        btn_frame = ctk.CTkFrame(convert_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        self._create_button(btn_frame, "To PNG", "convert")
        self._create_button(btn_frame, "To Text", "extract_text")

        # Present group
        present_frame = ctk.CTkFrame(self, fg_color="transparent")
        present_frame.grid(row=0, column=4, padx=4, pady=10, sticky="w")

        ctk.CTkLabel(present_frame, text="View", font=FONT_SMALL()).pack(anchor="w")
        btn_frame = ctk.CTkFrame(present_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        self._create_button(btn_frame, "Present", "present")

        # Security group
        sec_frame = ctk.CTkFrame(self, fg_color="transparent")
        sec_frame.grid(row=0, column=5, padx=4, pady=10, sticky="w")

        ctk.CTkLabel(sec_frame, text="Security", font=FONT_SMALL()).pack(anchor="w")
        btn_frame = ctk.CTkFrame(sec_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        self._create_button(btn_frame, "Encrypt", "encrypt")
        self._create_button(btn_frame, "Watermark", "watermark")
        self._create_button(btn_frame, "Compress", "compress")

        # Theme switch (right side)
        theme_frame = ctk.CTkFrame(self, fg_color="transparent")
        theme_frame.grid(row=0, column=6, padx=12, pady=10, sticky="e")

        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Dark",
            font=FONT_SMALL(),
            command=self._cmd("toggle_theme"),
            onvalue=True,
            offvalue=False,
        )
        self.theme_switch.pack(side="right")
        self.theme_switch.select()

    def _create_button(self, parent, text: str, key: str):
        btn = ctk.CTkButton(
            parent,
            text=text,
            width=70,
            height=28,
            font=FONT_BUTTON(),
            corner_radius=6,
            command=self._cmd(key),
        )
        btn.pack(side="left", padx=2)
        return btn

    def update_theme_button(self, is_dark: bool) -> None:
        if is_dark:
            self.theme_switch.select()
            self.theme_switch.configure(text="Dark")
        else:
            self.theme_switch.deselect()
            self.theme_switch.configure(text="Light")

    def _cmd(self, key: str):
        def handler():
            if key in self.commands:
                self.commands[key]()
        return handler
