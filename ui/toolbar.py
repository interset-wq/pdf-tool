"""Ribbon-style toolbar inspired by PowerPoint."""

import customtkinter as ctk
from utils.fonts import FONT_SMALL, FONT_BUTTON


class RibbonSeparator(ctk.CTkFrame):
    """Vertical separator line."""
    def __init__(self, master, **kwargs):
        super().__init__(master, width=1, fg_color=("gray70", "gray40"), **kwargs)
        self.pack_propagate(False)


class RibbonGroup(ctk.CTkFrame):
    """A group of buttons with a label."""

    def __init__(self, master, label: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._setup_ui(label)

    def _setup_ui(self, label: str):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=4)

        self.label = ctk.CTkLabel(self.content, text=label, font=FONT_SMALL(9))
        self.label.pack(side="bottom", pady=(2, 0))

    def add_button(self, text: str, command, width: int = 60, **kwargs) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            self.content,
            text=text,
            width=width,
            height=30,
            font=FONT_BUTTON(10),
            corner_radius=4,
            command=command,
            **kwargs,
        )
        btn.pack(side="left", padx=2, pady=(4, 16))
        return btn


class Toolbar(ctk.CTkFrame):
    """Ribbon-style toolbar."""

    def __init__(self, master, commands: dict | None = None, **kwargs):
        super().__init__(master, height=80, **kwargs)
        self.commands = commands or {}
        self.pack_propagate(False)
        self._setup_ui()

    def _setup_ui(self):
        ribbon = ctk.CTkFrame(self, fg_color="transparent")
        ribbon.pack(fill="both", expand=True, padx=8, pady=4)

        # Sidebar toggle
        self.sidebar_btn = ctk.CTkButton(
            ribbon,
            text="Panel",
            width=45,
            height=50,
            font=FONT_SMALL(9),
            corner_radius=4,
            command=self._cmd("toggle_sidebar"),
        )
        self.sidebar_btn.pack(side="left", padx=(0, 6))

        RibbonSeparator(ribbon, height=55).pack(side="left", padx=4, fill="y")

        # File
        g = RibbonGroup(ribbon, "File")
        g.pack(side="left", padx=4)
        g.add_button("Open", self._cmd("open"), width=50)
        g.add_button("Save", self._cmd("save"), width=50)

        RibbonSeparator(ribbon, height=55).pack(side="left", padx=4, fill="y")

        # Edit
        g = RibbonGroup(ribbon, "Edit")
        g.pack(side="left", padx=4)
        g.add_button("Merge", self._cmd("merge"), width=55)
        g.add_button("Split", self._cmd("split"), width=55)
        g.add_button("Rotate", self._cmd("rotate"), width=55)
        g.add_button("Reorder", self._cmd("reorder"), width=55)

        RibbonSeparator(ribbon, height=55).pack(side="left", padx=4, fill="y")

        # Convert
        g = RibbonGroup(ribbon, "Convert")
        g.pack(side="left", padx=4)
        g.add_button("To PNG", self._cmd("convert"), width=55)
        g.add_button("To Text", self._cmd("extract_text"), width=55)

        RibbonSeparator(ribbon, height=55).pack(side="left", padx=4, fill="y")

        # View
        g = RibbonGroup(ribbon, "View")
        g.pack(side="left", padx=4)
        g.add_button("Present", self._cmd("present"), width=65,
                      fg_color=("green", "#2d8a4e"))

        RibbonSeparator(ribbon, height=55).pack(side="left", padx=4, fill="y")

        # Security
        g = RibbonGroup(ribbon, "Security")
        g.pack(side="left", padx=4)
        g.add_button("Encrypt", self._cmd("encrypt"), width=55)
        g.add_button("Watermark", self._cmd("watermark"), width=60)
        g.add_button("Compress", self._cmd("compress"), width=60)

        # Theme
        self.theme_switch = ctk.CTkSwitch(
            ribbon,
            text="Dark",
            font=FONT_SMALL(9),
            command=self._cmd("toggle_theme"),
            onvalue=True,
            offvalue=False,
        )
        self.theme_switch.pack(side="right", padx=8)
        self.theme_switch.select()

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
