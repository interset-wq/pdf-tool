"""Main application window with resizable sidebar and all features."""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

from ui.viewer import PDFViewer
from ui.sidebar import Sidebar
from ui.toolbar import Toolbar
from ui.statusbar import StatusBar
from ui.presentation import PresentationMode
from ui.resizable_panel import ResizablePanel
from core.pdf_operations import (
    PDFMerger, PDFSplitter, PDFRotator, PDFMetadata,
    PDFPageNumber, PDFTextExtractor,
)
from core.pdf_converter import PDFToImage, ImageToPDF
from core.pdf_security import PDFSecurity, PDFWatermark
from core.pdf_compressor import PDFCompressor


class MainWindow:
    """Main application window controller."""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("PDF Tool")
        self.root.geometry("1400x900")
        self.root.minsize(900, 600)

        self.is_dark = True
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.current_file: Path | None = None
        self.sidebar_visible = True

        # Core modules
        self.merger = PDFMerger()
        self.splitter = PDFSplitter()
        self.rotator = PDFRotator()
        self.metadata = PDFMetadata()
        self.page_number = PDFPageNumber()
        self.text_extractor = PDFTextExtractor()
        self.converter = PDFToImage()
        self.image_to_pdf = ImageToPDF()
        self.security = PDFSecurity()
        self.watermark = PDFWatermark()
        self.compressor = PDFCompressor()

        self._setup_ui()
        self._setup_bindings()

    def _setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Toolbar
        commands = {
            "open": self.open_file,
            "save": self.save_file,
            "merge": self.merge_files,
            "split": self.split_file,
            "rotate": self.rotate_file,
            "reorder": self.reorder_file,
            "convert": self.convert_file,
            "extract_text": self.extract_text,
            "encrypt": self.encrypt_file,
            "watermark": self.add_watermark,
            "compress": self.compress_file,
            "toggle_theme": self.toggle_theme,
            "toggle_sidebar": self.toggle_sidebar,
            "present": self.start_presentation,
        }
        self.toolbar = Toolbar(self.root, commands=commands)
        self.toolbar.grid(row=0, column=0, sticky="ew")

        # Main content area with resizable panel
        self.panel = ResizablePanel(
            self.root, min_width=120, max_width=400, on_resize=self._on_panel_resize
        )
        self.panel.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        # Sidebar
        self.sidebar = Sidebar(self.panel, on_page_select=self._on_page_select)
        self.panel.set_left_widget(self.sidebar)

        # Separator
        self.panel.create_separator()

        # PDF Viewer
        self.viewer = PDFViewer(self.panel, on_page_change=self._on_page_change)
        self.panel.set_right_widget(self.viewer)

        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=2, column=0, sticky="ew")
        self.status_bar.set_zoom_callback(self._on_status_zoom)

    def _setup_bindings(self):
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Left>", lambda e: self.viewer.prev_page())
        self.root.bind("<Right>", lambda e: self.viewer.next_page())
        self.root.bind("<Control-plus>", lambda e: self.viewer.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.viewer.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.viewer.zoom_reset())
        self.root.bind("<End>", lambda e: self.viewer.go_to_end())
        self.root.bind("<Home>", lambda e: self.viewer.go_to_start())
        self.root.bind("<F5>", lambda e: self.start_presentation())
        self.root.bind("<Control-b>", lambda e: self.toggle_sidebar())

    # Theme & Sidebar
    def toggle_theme(self):
        self.is_dark = not self.is_dark
        ctk.set_appearance_mode("dark" if self.is_dark else "light")
        self.toolbar.update_theme_button(self.is_dark)
        self.status_bar.set_status(f"Theme: {'Dark' if self.is_dark else 'Light'}")

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_forget()
            self.panel._separator.grid_forget()
            self.status_bar.set_status("Sidebar hidden")
        else:
            self.sidebar.grid(row=0, column=0, sticky="ns")
            self.panel._separator.grid(row=0, column=1, sticky="ns")
            self.status_bar.set_status("Sidebar shown")
        self.sidebar_visible = not self.sidebar_visible
        self.toolbar.update_sidebar_button(self.sidebar_visible)

    def _on_panel_resize(self, width):
        pass

    # Presentation
    def start_presentation(self):
        if not self.current_file:
            messagebox.showinfo("Info", "Open a PDF first")
            return
        PresentationMode(self.root, str(self.current_file), self.viewer.current_page)

    # File operations
    def open_file(self, file_path: str | None = None):
        if file_path is None:
            path = filedialog.askopenfilename(
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
        else:
            path = file_path

        if not path:
            return

        try:
            self.viewer.open_pdf(path)
            self.current_file = Path(path)
            self.sidebar.set_document(self.viewer.reader.document)

            # Auto-adjust sidebar width based on PDF
            optimal_width = self.sidebar.get_optimal_width()
            self.panel.set_width(optimal_width)

            self.sidebar.update_file_info(
                self.current_file.name,
                self.viewer.reader.page_count,
                self._get_file_size(self.current_file),
            )
            self.status_bar.update_page_info(1, self.viewer.reader.page_count)
            self.status_bar.set_status(f"Opened: {self.current_file.name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF:\n{e}")

    def save_file(self):
        if not self.current_file:
            messagebox.showinfo("Info", "No file to save")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=self.current_file.name,
        )
        if path:
            self.status_bar.set_status(f"Saved: {Path(path).name}")

    # Edit operations
    def merge_files(self):
        paths = filedialog.askopenfilenames(
            title="Select PDFs to merge", filetypes=[("PDF files", "*.pdf")]
        )
        if not paths:
            return
        output = filedialog.asksaveasfilename(
            title="Save merged PDF", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")]
        )
        if not output:
            return
        try:
            self.status_bar.set_status("Merging...")
            self.merger.merge(list(paths), output)
            self.status_bar.set_status(f"Merged {len(paths)} files")
            messagebox.showinfo("Success", f"Merged {len(paths)} files")
        except Exception as e:
            self.status_bar.set_status("Merge failed")
            messagebox.showerror("Error", f"Merge failed:\n{e}")

    def split_file(self):
        if not self.current_file:
            messagebox.showinfo("Info", "Open a PDF first")
            return
        output_dir = filedialog.askdirectory(title="Select output directory")
        if not output_dir:
            return
        try:
            self.status_bar.set_status("Splitting...")
            files = self.splitter.split_by_pages(self.current_file, output_dir)
            self.status_bar.set_status(f"Split into {len(files)} files")
            messagebox.showinfo("Success", f"Split into {len(files)} files")
        except Exception as e:
            self.status_bar.set_status("Split failed")
            messagebox.showerror("Error", f"Split failed:\n{e}")

    def rotate_file(self):
        if not self.current_file:
            messagebox.showinfo("Info", "Open a PDF first")
            return
        dialog = ctk.CTkInputDialog(
            text="Enter angle (90, 180, 270) or negative for counter-clockwise:", title="Rotate"
        )
        angle_str = dialog.get_input()
        if not angle_str:
            return
        try:
            angle = int(angle_str)
        except ValueError:
            messagebox.showerror("Error", "Invalid angle")
            return
        output = filedialog.asksaveasfilename(
            title="Save rotated PDF", defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"rotated_{self.current_file.name}",
        )
        if not output:
            return
        try:
            self.rotator.rotate_all(self.current_file, angle, output)
            self.status_bar.set_status(f"Rotated {angle} degrees")
            messagebox.showinfo("Success", f"Rotated {angle} degrees")
        except Exception as e:
            self.status_bar.set_status("Rotate failed")
            messagebox.showerror("Error", f"Rotate failed:\n{e}")

    def reorder_file(self):
        if not self.current_file:
            messagebox.showinfo("Info", "Open a PDF first")
            return
        dialog = ctk.CTkInputDialog(
            text="Enter new page order (e.g., 3,1,2,4):", title="Reorder Pages"
        )
        order_str = dialog.get_input()
        if not order_str:
            return
        try:
            order = [int(x.strip()) - 1 for x in order_str.split(",")]
        except ValueError:
            messagebox.showerror("Error", "Invalid order format")
            return
        output = filedialog.asksaveasfilename(
            title="Save reordered PDF", defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"reordered_{self.current_file.name}",
        )
        if not output:
            return
        try:
            self.splitter.reorder_pages(self.current_file, order, output)
            self.status_bar.set_status("Pages reordered")
            messagebox.showinfo("Success", "Pages reordered")
        except Exception as e:
            self.status_bar.set_status("Reorder failed")
            messagebox.showerror("Error", f"Reorder failed:\n{e}")

    # Convert operations
    def convert_file(self):
        if not self.current_file:
            messagebox.showinfo("Info", "Open a PDF first")
            return
        output_dir = filedialog.askdirectory(title="Select output directory")
        if not output_dir:
            return
        try:
            self.status_bar.set_status("Converting...")
            files = self.converter.to_png(self.current_file, output_dir)
            self.status_bar.set_status(f"Converted {len(files)} pages")
            messagebox.showinfo("Success", f"Converted {len(files)} pages to PNG")
        except Exception as e:
            self.status_bar.set_status("Conversion failed")
            messagebox.showerror("Error", f"Conversion failed:\n{e}")

    def extract_text(self):
        if not self.current_file:
            messagebox.showinfo("Info", "Open a PDF first")
            return
        output = filedialog.asksaveasfilename(
            title="Save text file", defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"{self.current_file.stem}.txt",
        )
        if not output:
            return
        try:
            self.text_extractor.extract_pages(
                self.current_file, [self.viewer.current_page], output
            )
            self.status_bar.set_status(f"Text extracted to {Path(output).name}")
            messagebox.showinfo("Success", "Text extracted")
        except Exception as e:
            self.status_bar.set_status("Extract failed")
            messagebox.showerror("Error", f"Extract failed:\n{e}")

    # Security operations
    def encrypt_file(self):
        if not self.current_file:
            messagebox.showinfo("Info", "Open a PDF first")
            return
        dialog = ctk.CTkInputDialog(text="Enter password:", title="Password")
        password = dialog.get_input()
        if not password:
            return
        output = filedialog.asksaveasfilename(
            title="Save encrypted PDF", defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"encrypted_{self.current_file.name}",
        )
        if not output:
            return
        try:
            self.security.encrypt(self.current_file, output, password)
            self.status_bar.set_status("PDF encrypted")
            messagebox.showinfo("Success", "PDF encrypted")
        except Exception as e:
            self.status_bar.set_status("Encryption failed")
            messagebox.showerror("Error", f"Encryption failed:\n{e}")

    def add_watermark(self):
        if not self.current_file:
            messagebox.showinfo("Info", "Open a PDF first")
            return
        dialog = ctk.CTkInputDialog(text="Enter watermark text:", title="Watermark")
        text = dialog.get_input()
        if not text:
            return
        output = filedialog.asksaveasfilename(
            title="Save watermarked PDF", defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"watermarked_{self.current_file.name}",
        )
        if not output:
            return
        try:
            self.watermark.add_text_watermark(self.current_file, output, text)
            self.status_bar.set_status("Watermark added")
            messagebox.showinfo("Success", "Watermark added")
        except Exception as e:
            self.status_bar.set_status("Watermark failed")
            messagebox.showerror("Error", f"Watermark failed:\n{e}")

    def compress_file(self):
        if not self.current_file:
            messagebox.showinfo("Info", "Open a PDF first")
            return
        output = filedialog.asksaveasfilename(
            title="Save compressed PDF", defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"compressed_{self.current_file.name}",
        )
        if not output:
            return
        try:
            self.status_bar.set_status("Compressing...")
            result = self.compressor.optimize(self.current_file, output)
            self.status_bar.set_status(f"Reduced by {result['reduction']}")
            messagebox.showinfo(
                "Success",
                f"Original: {result['original']}\nNew: {result['compressed']}\nReduction: {result['reduction']}",
            )
        except Exception as e:
            self.status_bar.set_status("Compression failed")
            messagebox.showerror("Error", f"Compression failed:\n{e}")

    # Callbacks
    def _on_page_select(self, page_num: int):
        self.sidebar.highlight_page(page_num)
        self.viewer.go_to_page(page_num)

    def _on_page_change(self, page_num: int):
        self.sidebar.highlight_page(page_num)
        total = self.viewer.reader.page_count
        self.status_bar.update_page_info(page_num + 1, total)

    def _on_status_zoom(self, zoom: float):
        self.viewer.zoom = zoom
        self.viewer.render()

    def _get_file_size(self, path: Path) -> str:
        size = path.stat().st_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def run(self):
        self.root.mainloop()
