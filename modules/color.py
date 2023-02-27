"""Module containing the Color class."""

from __future__ import annotations
from typing import Any


class Color:
    """Class containing all information about a color."""

    _frozen: bool = False
    # class containing all information about a color
    def __init__(self, r: int, g: int, b: int) -> Color:
        """Initialize a Color object.

        Args:
            r (int): red component (range 0-255)
            g (int): green component (range 0-255)
            b (int): blue component (range 0-255)

        Returns:
            Color
        """
        if not (0 <= r <= 255):
            raise ValueError("Red component must be in range 0-255")

        if not (0 <= g <= 255):
            raise ValueError("Green component must be in range 0-255")

        if not (0 <= b <= 255):
            raise ValueError("Blue component must be in range 0-255")

        self._rgb = (r, g, b)
        self._hsv = self._toHSV(r, g, b)
        self._frozen = True

    def _toHSV(self, R: int, G: int, B: int) -> tuple[int, int, int]:
        r = R / 255
        g = G / 255
        b = B / 255

        c_max = max(r, g, b)
        c_min = min(r, g, b)
        delta = c_max - c_min

        if delta == 0:
            h = 0
        elif c_max == r:
            h = (60 * ((g - b) / delta) + 360) % 360
        elif c_max == g:
            h = (60 * ((b - r) / delta) + 120) % 360
        elif c_max == b:
            h = (60 * ((r - g) / delta) + 240) % 360

        if c_max == 0:
            s = 0
        else:
            s = delta / c_max * 100

        v = c_max * 100

        return (int(h), int(s), int(v))

    def __setattr__(self, __name: str, __value: Any) -> None:
        """Set attribute.

        Args:
            __name (str)
            __value (Any)

        Raises:
            AttributeError: thrown if the object is frozen
        """
        if self._frozen:
            raise AttributeError("Color object is immutable")
        super().__setattr__(__name, __value)

    # getter functions
    @property
    def r(self) -> int:
        """Get the red component of the color.

        Returns:
            int: red component (range 0-255)
        """
        return self._rgb[0]

    def g(self) -> int:
        """Get the green component of the color.

        Returns:
            int: green component (range 0-255)
        """
        return self._rgb[1]

    def b(self) -> int:
        """Get the blue component of the color.

        Returns:
            int: blue component (range 0-255)
        """
        return self._rgb[2]

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Get the RGB components of the color.

        Returns:
            tuple[int, int, int]: RGB components (range 0-255)
        """
        return tuple(self._rgb)

    @property
    def hsv(self) -> tuple[int, int, int]:
        """Get the HSV components of the color.

        Returns:
            tuple[int, int, int]:
        """
        return tuple(self._hsv)

    @property
    def hsv_formatted(self) -> str:
        """Return the HSV components of the color as a formatted string.

        Returns:
            str
        """
        return f"hsv({self._hsv[0]}°, {self._hsv[1]}%, {self._hsv[2]}%)"

    @property
    def rgb_formatted(self) -> str:
        """Return the RGB components of the color as a formatted string.

        Returns:
            str
        """
        return f"rgb({self._rgb[0]}, {self._rgb[1]}, {self._rgb[2]})"

    @property
    def hue(self) -> int:
        """Get the hue component of the color.

        Returns:
            int
        """
        return self._hsv[0]

    @property
    def saturation(self) -> int:
        """Get the saturation component of the color.

        Returns:
            int
        """
        return self._hsv[1]

    @property
    def hex(self) -> str:
        """Get the hex representation of the color.

        Returns:
            str
        """
        return f"#{''.join([hex(x)[2:].zfill(2) for x in self._rgb]).upper()}"
