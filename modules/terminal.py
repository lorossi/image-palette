"""Terminal module."""
from __future__ import annotations

from .color import Color

ESC = "\033["


class Cell:
    """A cell in a table."""

    _content: str

    def __init__(self, content: str, fore: Color = None, back: Color = None) -> Cell:
        """Initialize a Cell object.

        Args:
            content (str): Content of the cell.
            fore (Color, optional): Text color of the cell. Defaults to None.
            back (Color, optional): Background color of the cell. Defaults to None.

        Returns:
            Cell: _description_
        """
        self._content = content
        self._fore = fore
        self._back = back

    def __repr__(self) -> str:
        """Return a string representation of the cell.

        Returns:
            str
        """
        return format_color(self._content, fore=self._fore, back=self._back)

    def __str__(self) -> str:
        """Return a string representation of the cell.

        Returns:
            str
        """
        return self.__repr__()

    def __len__(self) -> int:
        """Return the length of content the cell.

        Returns:
            int
        """
        return len(self._content)


def format_color(text: str, fore: Color = None, back: Color = None) -> str:
    """Format text with foreground and background colors.

    Args:
        text (str): text to format
        fore (Color, optional): foreground color. Defaults to None.
        back (Color, optional): background color. Defaults to None.
    """

    if fore is None:
        front_str = ""
    else:
        front_str = f"{ESC}38;2;{fore.rgb[0]};{fore.rgb[1]};{fore.rgb[2]}m"

    if back is None:
        back_str = ""
    else:
        back_str = f"{ESC}48;2;{back.rgb[0]};{back.rgb[1]};{back.rgb[2]}m"

    return f"{front_str}{back_str}{text}{ESC}0m"


def format_table(cells: list[list[Cell]], border_fore: Color = None) -> str:
    """Format a table.

    Args:
        cells (list[list[Cell]]): List of cells.
        border_fore (Color, optional): Color of the border. Defaults to None.

    Returns:
        str
    """
    if border_fore is None:
        VERTICAL_LINE = "│"
        HORIZONTAL_LINE = "─"
        TOP_LEFT_ANGLE = "┌"
        TOP_RIGHT_ANGLE = "┐"
        BOTTOM_LEFT_ANGLE = "└"
        BOTTOM_RIGHT_ANGLE = "┘"
        TOP_CONNECTOR = "┬"
        BOTTOM_CONNECTOR = "┴"
    else:
        VERTICAL_LINE = format_color("│", fore=border_fore)
        HORIZONTAL_LINE = format_color("─", fore=border_fore)
        TOP_LEFT_ANGLE = format_color("┌", fore=border_fore)
        TOP_RIGHT_ANGLE = format_color("┐", fore=border_fore)
        BOTTOM_LEFT_ANGLE = format_color("└", fore=border_fore)
        BOTTOM_RIGHT_ANGLE = format_color("┘", fore=border_fore)
        TOP_CONNECTOR = format_color("┬", fore=border_fore)
        BOTTOM_CONNECTOR = format_color("┴", fore=border_fore)

    max_col_width = [max(len(cell) + 2 for cell in col) for col in zip(*cells)]

    table = ""
    table += TOP_LEFT_ANGLE

    for w in max_col_width[:-1]:
        table += HORIZONTAL_LINE * w
        table += TOP_CONNECTOR

    table += HORIZONTAL_LINE * max_col_width[-1]
    table += TOP_RIGHT_ANGLE
    table += "\n"

    for row in cells:
        table += VERTICAL_LINE
        for cell, w in zip(row, max_col_width):
            table += " "
            table += str(cell)
            table += " " * (w - len(cell) - 1)
            table += VERTICAL_LINE

        table += "\n"

    table += BOTTOM_LEFT_ANGLE

    for w in max_col_width[:-1]:
        table += HORIZONTAL_LINE * w
        table += BOTTOM_CONNECTOR

    table += HORIZONTAL_LINE * max_col_width[-1]
    table += BOTTOM_RIGHT_ANGLE

    return table
