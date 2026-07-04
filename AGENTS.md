# AGENTS.md

## Project Overview

PDF tool built with CustomTkinter UI. Aims to be a comprehensive PDF utility (view, merge, split, convert, encrypt/decrypt, compress).

## Quick Commands

```bash
# Run the app
uv run python main.py

# Add dependencies
uv add <package>

# Sync dependencies
uv sync
```

## Tech Stack

- **Package manager**: uv (not pip)
- **Python**: 3.14 (required)
- **UI**: CustomTkinter 6.x
- **PDF processing**: PyMuPDF (rendering), pikepdf (merge/split/encrypt), reportlab (PDF generation), Pillow (image handling)

## Architecture

Planned structure (not yet implemented):
- `ui/` - CustomTkinter windows, viewer, toolbar, sidebar
- `core/` - PDF operations (reader, merger, splitter, converter, security)
- `utils/` - Helpers

Entry point: `main.py`

## Conventions

- Use `uv` for all package operations, never `pip`
- CustomTkinter widgets use `ctk` import alias
- PyMuPDF is imported as `fitz`
