from enum import Enum


class Position(Enum):
    """Position of the color legend. \
    Valid values: l, r, t, b (for left, right, top, bottom)."""

    LEFT = "l"
    RIGHT = "r"
    TOP = "t"
    BOTTOM = "b"
