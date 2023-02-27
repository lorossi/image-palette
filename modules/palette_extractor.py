"""Palette extractor module."""

import json
import logging
import pathlib

from PIL import Image, ImageDraw

from .color import Color
from .kmeans import KMeans
from .position import Position
from .terminal import format_color


class PaletteExtractor:
    """Palette extractor class."""

    _colors: list[Color] = None
    _resized_width: int = 1000

    def __init__(self):
        """Initialize the class."""
        self._colors = []

    def _createFolder(self, path: str):
        """Create a folder if it doesn't exist; if it does, do nothing."""
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def loadImage(self, path: str, palette_size: int = 5, resize: bool = False) -> None:
        """Load an image.

        Args:
            path (str): Path to the image.
            palette_size (int, optional): Numbers of colors to isolate.. Defaults to 5.
            resize (bool, optional): Resize the image to make the computation faster. \
             Defaults to False.
        """
        self._path = path
        self._palette_size = palette_size
        self._im = Image.open(self._path)

        # create a copy of the image to work on
        self._working_image = self._im.copy()
        # resize the image if it's too big
        # you might miss some colors but the runtime will be way lower
        if resize and self._im.width > self._resized_width:
            new_width = self._resized_width
            new_height = int(self._im.height / self._im.width * new_width)
            self._working_image = self._working_image.resize((new_width, new_height))

    def extractColors(self, seed: int = None, min_dist: int = 1):
        """Extract the colors from the image.

        Args:
            seed (int, optional): Seed to initialize the KMeans algorithm. \
                If none is provided, the algorithm will use the current time.
        """
        # start extracting the colors
        logging.info("Starting color extractions")
        pixels = self._working_image.load()
        # need to convert to list the list of lists
        pixels_list = [
            Color(*pixels[x, y])
            for x in range(self._working_image.width)
            for y in range(self._working_image.height)
        ]
        # run the KMeans algorithm
        self._colors = (
            KMeans(n_clusters=self._palette_size, random_seed=seed)
            .fit(pixels=pixels_list, min_dist=min_dist)
            .centroids
        )
        # sort by saturation and hue
        self._colors.sort(key=lambda x: x.saturation, reverse=False)
        self._colors.sort(key=lambda x: x.hue, reverse=False)
        logging.info("Colors extracted")

    def generatePalette(self, output_width: int = 1000, output_height: int = 200):
        """Generate a palette image.

        Args:
            output_width (int, optional): Defaults to 1000.
            output_height (int, optional): Defaults to 200.
        """
        # generates an image containing the palette
        logging.info("Starting palette image generation")
        bars_width = int(output_width / self._palette_size)

        self._palette = Image.new("RGB", (output_width, output_height))
        draw = ImageDraw.Draw(self._palette)

        i = 0
        for c in self._colors:
            x_0 = i * bars_width
            y_0 = 0
            x_1 = (i + 1) * bars_width
            y_1 = output_height
            fill = c.rgb
            draw.rectangle([x_0, y_0, x_1, y_1], fill=fill)
            i += 1
        logging.info("Palette image generated")

    def incorporatePalette(
        self,
        output_scl: float = 0.9,
        palette_width_scl: float = 0.1,
        palette_height_scl: float = 0.9,
        background_color: tuple[int] = (220, 220, 220),
        outline_color: tuple[int] = (127, 127, 127),
        line_width: int = 1,
        position: Position = Position.RIGHT,
    ):
        """Incorporate the palette in the image.

        Args:
            output_scl (float, optional): Scale of the output image. Defaults to 0.9.
            palette_width_scl (float, optional): Width of the palette relative to \
                the size of the image.. Defaults to 0.1.
            palette_height_scl (float, optional): Height of the palette relative to \
                the size of the image.. Defaults to 0.9.
            background_color (tuple[int], optional): Background color of the palette. \
                Defaults to (220, 220, 220).
            outline_color (tuple[int], optional): Outline color of the palette. \
                Defaults to (127, 127, 127).
            line_width (int, optional): Width of the outline. Defaults to 1.
            position (Position, optional): Position of the palette. \
                 Defaults to Position.RIGHT.
        """
        # image resized
        new_width = int(self._im.width / output_scl)
        new_height = int(self._im.height / output_scl)
        # image displacement
        image_dx = int((new_width - self._im.width) / 2)
        image_dy = int((new_height - self._im.height) / 2)

        # TODO refactor this

        if position.value == "l" or position.value == "r":
            # bar sizes calculation
            palette_width = int(new_width * palette_width_scl)
            palette_height = int(new_height * palette_height_scl)
            slice_height = int(palette_height / self._palette_size)
            bar_height = int(slice_height * 0.75)
            bar_width = int(palette_width * 0.5)
            # displacement
            bars_dx = int((palette_width - bar_width) / 2)
            bars_dy = int((slice_height - bar_height) / 2)

            logging.info("Starting palette incorporation")
            bars = Image.new(
                "RGB", (palette_width, palette_height), color=background_color
            )
            draw = ImageDraw.Draw(bars)
            # draw each bar
            i = 0
            for c in self._colors:
                x_0 = bars_dx
                y_0 = i * slice_height + bars_dy
                x_1 = x_0 + bar_width
                y_1 = y_0 + bar_height
                fill = c.rgb
                draw.rectangle(
                    [x_0, y_0, x_1, y_1],
                    fill=fill,
                    outline=outline_color,
                    width=line_width,
                )
                i += 1

            # left or right
            self._incorporated_palette = Image.new(
                "RGB", (new_width + palette_width, new_height), color=background_color
            )
            palette_dy = int((new_height - palette_height) / 2)
            palette_dx = int(0.5 * image_dx)
            if position == "l":
                self._incorporated_palette.paste(
                    self._im, (palette_width + image_dx, image_dy)
                )
                self._incorporated_palette.paste(bars, (palette_dx, palette_dy))
            elif position == "r":
                self._incorporated_palette.paste(self._im, (image_dx, image_dy))
                self._incorporated_palette.paste(
                    bars,
                    (new_width - palette_width + palette_dx + image_dx, palette_dy),
                )

        if position.value == "t" or position.value == "b":
            # bar sizes calculation
            palette_width = int(new_width * palette_width_scl)
            palette_height = int(new_height * palette_height_scl)
            slice_width = int(palette_width / self._palette_size)
            bar_width = int(slice_width * 0.75)
            bar_height = int(palette_height * 0.5)

            # displacement
            bars_dx = int((slice_width - bar_width) / 2)
            bars_dy = int((palette_height - bar_height) / 2)

            logging.info("Starting palette incorporation")
            bars = Image.new(
                "RGB", (palette_width, palette_height), color=background_color
            )
            draw = ImageDraw.Draw(bars)
            # draw each bar
            i = 0
            for c in self._colors:
                x_0 = i * slice_width + bars_dx
                y_0 = bars_dy
                x_1 = x_0 + bar_width
                y_1 = y_0 + bar_height
                fill = c.rgb
                draw.rectangle(
                    [x_0, y_0, x_1, y_1],
                    fill=fill,
                    outline=outline_color,
                    width=line_width,
                )
                i += 1

            self._incorporated_palette = Image.new(
                "RGB",
                (new_width, new_height + palette_height),
                color=background_color,
            )
            palette_dx = int((new_width - palette_width) / 2)
            palette_dy = int(0.5 * image_dy)
            if position.value == "t":
                self._incorporated_palette.paste(
                    self._im, (image_dx, image_dy + palette_height)
                )
                self._incorporated_palette.paste(bars, (palette_dx, palette_dy))
            elif position.value == "b":
                self._incorporated_palette.paste(self._im, (image_dx, image_dy))
                self._incorporated_palette.paste(
                    bars,
                    (palette_dx, new_height - palette_height + image_dy + palette_dy),
                )

        logging.info("Palette incorporated")

    def printPalette(self):
        """Print the palette in the console.

        The console must support TrueColor.
        """
        # print the palette in the console
        BAR_WIDTH = 16
        SEPARATOR = " │ "
        HORIZONTAL_LINE = "─"

        max_rgb = max(len(str(c.rgb)) for c in self._colors)
        max_hsv = max(len(str(c.hsv_formatted)) for c in self._colors)
        max_hex = max(len(str(c.hex)) for c in self._colors)

        line_width = BAR_WIDTH + max_rgb + max_hsv + max_hex + len(SEPARATOR) * 6 + 1
        line_color = Color(233, 233, 233)  # light gray
        print("\n", format_color("Extracted color palette:", fore=line_color), "\n")
        print(" ", format_color(HORIZONTAL_LINE * line_width, fore=line_color), sep="")

        for c in self._colors:
            rgb = c.rgb
            hsv = c.hsv_formatted
            hex = c.hex

            spacing_rgb = max_rgb - len(str(rgb))
            spacing_hsv = max_hsv - len(str(hsv))

            print(format_color(SEPARATOR, fore=line_color), end="")
            print(format_color(" " * BAR_WIDTH, back=c), sep=" ", end="")
            print(format_color(SEPARATOR, fore=line_color), end="")
            print(f"rgb{rgb}{spacing_rgb * ' '}", end="")
            print(format_color(SEPARATOR, fore=line_color), end="")
            print(f"hsv{hsv}{spacing_hsv * ' '}", end="")
            print(format_color(SEPARATOR, fore=line_color), end="")
            print(f"{hex}", end="")

            print(format_color(SEPARATOR, fore=line_color))

        print(
            " ",
            format_color(HORIZONTAL_LINE * line_width, fore=line_color),
            "\n",
            sep="",
        )

    def savePaletteImage(self, folder: str = "output/"):
        """Save the palette image.

        Args:
            folder (str, optional). Defaults to "output/".
        """
        self._createFolder(folder)
        path = f"{folder}{self._filename}-palette.png"
        self._palette.save(path)

        logging.info(f"Palette image saved. Path: {path}")

    def saveIncorporatedPalette(self, folder: str = "output/"):
        """Save the image with the palette incorporated.

        Args:
            folder (str, optional). Defaults to "output/".
        """
        self._createFolder(folder)
        path = f"{folder}{self._filename}-incorporated-palette.png"
        self._incorporated_palette.save(path)

        logging.info(f"Incorporated palette image saved. Path: {path}")

    def savePaletteJSON(self, folder: str = "output/"):
        """Save the palette in a JSON file.

        Args:
            folder (str, optional). Defaults to "output/".
        """
        self._createFolder(folder)
        json_dict = {"rgb": [], "hsv": [], "hex": []}

        for c in self._colors:
            json_dict["rgb"].append(c.rgb)
            json_dict["hsv"].append(c.hsv)
            json_dict["hex"].append(c.hex)

        path = f"{folder}{self._filename}-json-palette.json"
        with open(path, "w") as json_file:
            json.dump(json_dict, json_file, indent=2)

        logging.info(f"JSON file saved. Path: {path}")

    @property
    def _filename(self) -> str:
        return self._path.split("/")[-1].split(".")[0] + ".png"
