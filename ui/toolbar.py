"""Ribbon-style toolbar inspired by PowerPoint."""

import customtkinter as ctk
from utils.fonts import FONT_SMALL, FONT_BUTTON


class RibbonGroup(ctk.CTkFrame):
    """A group of buttons with a label."""

    def __init__(self, master, label: str, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._label_text = label
        self._setup_ui()

    def _setup_ui(self):
        # Container with subtle background
        self.container = ctk.CTkFrame(self, fg_color=("gray90", "gray20"), corner_radius=6)
        self.container.pack(fill="both", expand=True, padx=2)

        # Buttons area
        self.content = ctk.CTkFrame(self.container, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=4, pady=(4, 0))

        # Label at bottom
        self.label = ctk.CTkLabel(
            self.container, text=self._label_text, font=FONT_SMALL(9),
            text_color=("gray50", "gray60")
        )
        self.label.pack(side="bottom", pady=(0, 4))

    def add_button(self, text: str, command, width: int = 60, **kwargs) -> ctk.CTkButton:
        btn = ctk.CTkButton(
            self.content,
            text=text,
            width=width,
            height=28,
            font=FONT_BUTTON(10),
            corner_radius=4,
            command=command,
            **kwargs,
        )
        btn.pack(side="left", padx=2, pady=2)
        return btn

    def add_icon_button(self, text: str, command, icon: str = "", width: int = 60) -> ctk.CTkButton:
        display = f"{icon} {text}" if icon else text
        btn = ctk.CTkButton(
            self.content,
            text=display,
            width=width,
            height=40,
            font=FONT_BUTTON(10),
            corner_radius=4,
            command=command,
        )
        btn.pack(side="left", padx=2, pady=2)
        return btn


class Toolbar(ctk.CTkFrame):
    """Ribbon-style toolbar."""

    def __init__(self, master, commands: dict | None = None, **kwargs):
        super().__init__(master, height=76, **kwargs)
        self.commands = commands or {}
        self.pack_propagate(False)
        self._setup_ui()

    def _setup_ui(self):
        ribbon = ctk.CTkFrame(self, fg_color="transparent")
        ribbon.pack(fill="both", expand=True, padx=6, pady=4)

        # Sidebar toggle (standalone)
        self.sidebar_switch = ctk.CTkSwitch(
            ribbon,
            text="Panel",
            font=FONT_SMALL(9),
            command=self._cmd("toggle_sidebar"),
            onvalue=True,
            offvalue=False,
        )
        self.sidebar_switch.pack(side="left", padx=(0, 6))
        self.sidebar_switch.select()

        # File group
        g = RibbonGroup(ribbon, "File")
        g.pack(side="left", padx=3, fill="y")
        g.add_button("Open", self._cmd("open"), width=50)
        g.add_button("Save", self._cmd("save"), width=50)

        # Edit group
        g = RibbonGroup(ribbon, "Edit")
        g.pack(side="left", padx=3, fill="y")
        g.add_button("Merge", self._cmd("merge"), width=50)
        g.add_button("Split", self._cmd("split"), width=50)
        g.add_button("Rotate", self._cmd("rotate"), width=50)
        g.add_button("Reorder", self._cmd("reorder"), width=50)

        # Convert group
        g = RibbonGroup(ribbon, "Convert")
        g.pack(side="left", padx=3, fill="y")
        g.add_button("PNG", self._cmd("convert"), width=45)
        g.add_button("Text", self._cmd("extract_text"), width=45)

        # View group
        g = RibbonGroup(ribbon, "View")
        g.pack(side="left", padx=3, fill="y")
        g.add_button("Present", self._cmd("present"), width=60,
                      fg_color=("green", "#2d8a4e"), hover_color=("darkgreen", "#1e6b3a"))

        # Security group
        g = RibbonGroup(ribbon, "Security")
        g.pack(side="left", padx=3, fill="y")
        g.add_button("Encrypt", self._cmd("encrypt"), width=50)
        g.add_button("Watermark", self._cmd("watermark"), width=60)
        g.add_button("Compress", self._cmd("compress"), width=60)

        # Theme (right side)
        theme_frame = ctk.CTkFrame(ribbon, fg_color="transparent")
        theme_frame.pack(side="right", padx=(8, 0))

        self.theme_switch = ctk.CTkSwitch(
            theme_frame,
            text="Dark",
            font=FONT_SMALL(9),
            command=self._cmd("toggle_theme"),
            onvalue=True,
            offvalue=False,
        )
        self.theme_switch.pack(side="right")
        self.theme_switch.select()

    def update_theme_button(self, is_dark: bool) -> None:
        if is_dark:
            self.theme_switch.select()
            self.theme_switch.configure(text="Dark")
        else:
            self.theme_switch.deselect()
            self.theme_switch.configure(text="Light")

    def update_sidebar_button(self, visible: bool) -> None:
        if visible:
            self.sidebar_switch.select()
        else:
            self.sidebar_switch.deselect()

    def _cmd(self, key: str):
        def handler():
            if key in self.commands:
                self.commands[key]()
        return handler
