"""Resizable panel separator."""

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

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def set_left_widget(self, widget):
        self._left_widget = widget
        widget.grid(row=0, column=0, sticky="ns")

    def set_right_widget(self, widget):
        self._right_widget = widget
        widget.grid(row=0, column=2, sticky="nsew")

    def create_separator(self):
        self._separator = ctk.CTkFrame(self, width=6, cursor="hand2",
                                        fg_color=("gray70", "gray35"))
        self._separator.grid(row=0, column=1, sticky="ns")
        self._separator.grid_propagate(False)

        # Drag handle indicator
        handle = ctk.CTkLabel(self._separator, text="|", font=("", 10),
                              text_color=("gray50", "gray55"))
        handle.pack(expand=True)

        # Bindings
        for widget in [self._separator, handle]:
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._on_drag)
            widget.bind("<ButtonRelease-1>", self._end_drag)
            widget.configure(cursor="sb_h_double_arrow")

    def _start_drag(self, event):
        self._dragging = True
        self._start_x = event.x_root
        self._start_width = self._left_widget.winfo_width()

    def _on_drag(self, event):
        if not self._dragging:
            return
        dx = event.x_root - self._start_x
        new_width = self._start_width + dx
        new_width = max(self.min_width, min(self.max_width, new_width))

        self._left_widget.configure(width=new_width)
        if self.on_resize:
            self.on_resize(new_width)

    def _end_drag(self, event):
        self._dragging = False

    def set_width(self, width: int):
        width = max(self.min_width, min(self.max_width, width))
        self._left_widget.configure(width=width)
