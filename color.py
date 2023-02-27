from __future__ import annotations


class Color:
    # class containing all information about a colour
    def __init__(self, rgb: list[int]) -> Color:
        # it's initialized as rgb list
        self._rgb = [int(x) for x in rgb]
        self._hsv = []

        self.RGBtoHSV()

    # rgb to hsv conversion
    def RGBtoHSV(self):
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

        self._hsv = [int(h), int(s), int(v)]

    # getter functions
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
