"""Font configuration for the application."""

import platform


def get_font(size: int = 12, bold: bool = False) -> tuple[str, int, str]:
    """Get font tuple for the current platform."""
    system = platform.system()

    if system == "Windows":
        font_name = "Microsoft YaHei"
    elif system == "Darwin":  # macOS
        font_name = "PingFang SC"
    else:  # Linux
        font_name = "Noto Sans CJK SC"

    weight = "bold" if bold else "normal"
    return (font_name, size, weight)


# Pre-defined font styles
FONT_TITLE = lambda size=14: get_font(size, bold=True)
FONT_NORMAL = lambda size=12: get_font(size)
FONT_SMALL = lambda size=10: get_font(size)
FONT_BUTTON = lambda size=11: get_font(size)
FONT_HEADER = lambda size=11: get_font(size, bold=True)
