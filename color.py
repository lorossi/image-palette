from __future__ import annotations
from typing import Any


class Color:
    _frozen: bool = False
    # class containing all information about a color
    def __init__(self, r: int, g: int, b: int) -> Color:
        # it's initialized as rgb list
        self._rgb = (r, g, b)
        self._hsv = self._toHSV()
        self._frozen = True

    # rgb to hsv conversion
    def _toHSV(self) -> tuple[int, int, int]:
        r = self._rgb[0] / 255
        g = self._rgb[1] / 255
        b = self._rgb[2] / 255

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
        if self._frozen:
            raise AttributeError("Color object is immutable")
        super().__setattr__(__name, __value)

    # getter functions
    @property
    def r(self) -> int:
        return self._rgb[0]

    def g(self) -> int:
        return self._rgb[1]

    def b(self) -> int:
        return self._rgb[2]

    @property
    def rgb(self) -> tuple[int, int, int]:
        return tuple(self._rgb)

    @property
    def hsv(self) -> tuple[int, int, int]:
        return tuple(self._hsv)

    @property
    def hsv_formatted(self) -> str:
        return f"({self._hsv[0]}°, {self._hsv[1]}%, {self._hsv[2]}%)"

    @property
    def hue(self) -> int:
        return self._hsv[0]

    @property
    def saturation(self) -> int:
        return self._hsv[1]

    @property
    def hex(self) -> str:
        return f"#{''.join([hex(x)[2:].zfill(2) for x in self._rgb]).upper()}"
