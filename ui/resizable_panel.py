"""Resizable panel separator - optimized for smooth dragging."""

import customtkinter as ctk


class ResizablePanel(ctk.CTkFrame):
    """A panel with a draggable separator for resizing."""

    def __init__(self, master, min_width=120, max_width=400, on_resize=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.min_width = min_width
        self.max_width = max_width
        self.on_resize = on_resize
        self._dragging = False
        self._start_x = 0
        self._start_width = 0
        self._update_pending = False

        # Use pack layout for smoother resizing
        self.pack_propagate(False)

        # Left widget container with fixed width
        self._left_container = ctk.CTkFrame(self, fg_color="transparent")
        self._left_container.pack(side="left", fill="y")

        # Separator
        self._separator = ctk.CTkFrame(self, width=6, fg_color=("gray70", "gray35"))
        self._separator.pack(side="left", fill="y")
        self._separator.pack_propagate(False)

        # Handle
        handle = ctk.CTkLabel(self._separator, text="|", font=("", 10),
                              text_color=("gray50", "gray55"))
        handle.pack(expand=True)
        handle.configure(cursor="sb_h_double_arrow")

        # Bindings on separator and handle
        for w in [self._separator, handle]:
            w.bind("<ButtonPress-1>", self._start_drag)
            w.bind("<B1-Motion>", self._on_drag)
            w.bind("<ButtonRelease-1>", self._end_drag)
            w.configure(cursor="sb_h_double_arrow")

        # Right widget (viewer) - takes remaining space
        self._right_widget = None

    def set_left_widget(self, widget):
        self._left_widget = widget
        widget.pack(in_=self._left_container, fill="both", expand=True)

    def set_right_widget(self, widget):
        self._right_widget = widget
        widget.pack(side="left", fill="both", expand=True)

    def create_separator(self):
        pass  # Created in __init__

    def _start_drag(self, event):
        self._dragging = True
        self._start_x = event.x_root
        self._start_width = self._left_container.winfo_width()

    def _on_drag(self, event):
        if not self._dragging:
            return

        dx = event.x_root - self._start_x
        new_width = self._start_width + dx
        new_width = max(self.min_width, min(self.max_width, new_width))

        # Update width directly without triggering full re-layout
        self._left_container.configure(width=new_width)

        if self.on_resize and not self._update_pending:
            self._update_pending = True
            self.after(1, lambda: self._do_resize(new_width))

    def _do_resize(self, width):
        self._update_pending = False
        if self.on_resize:
            self.on_resize(width)

    def _end_drag(self, event):
        self._dragging = False

    def set_width(self, width: int):
        width = max(self.min_width, min(self.max_width, width))
        self._left_container.configure(width=width)
