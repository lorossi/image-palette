"""Terminal module."""

from .color import Color


def format_color(text: str, fore: Color = None, back: Color = None) -> str:
    """Format text with foreground and background colors.

    Args:
        text (str): text to format
        fore (Color, optional): foreground color. Defaults to None.
        back (Color, optional): background color. Defaults to None.
    """
    ESC = "\033["

    if fore is None:
        front_str = ""
    else:
        front_str = f"{ESC}38;2;{fore.rgb[0]};{fore.rgb[1]};{fore.rgb[2]}m"

    if back is None:
        back_str = ""
    else:
        back_str = f"{ESC}48;2;{back.rgb[0]};{back.rgb[1]};{back.rgb[2]}m"

    return f"{front_str}{back_str}{text}{ESC}0m"
