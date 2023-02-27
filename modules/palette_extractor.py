"""Palette extractor module."""

import json
import logging
import pathlib

from PIL import Image, ImageDraw

from .color import Color
from .kmeans import KMeans
from .position import Position
from .terminal import format_table, Cell


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

    def extractColors(self, seed: int = None, min_dist: int = 25, max_iter: int = 5):
        """Extract the colors from the image.

        Args:
            seed (int, optional): Seed to initialize the KMeans algorithm. \
                If none is provided, the algorithm will use the current time.
            min_dist (int, optional): Minimum average distance between the centroids \
                and each pixel. Defaults to 25.
            max_iter (int, optional): Maximum number of iterations without change \
                in objective function. Defaults to 5.
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
            KMeans(
                n_clusters=self._palette_size,
                random_seed=seed,
                min_dist=min_dist,
                max_iterations=max_iter,
            )
            .fit(pixels=pixels_list)
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
        color_width_scl: float = 0.9,
        color_height_scl: float = 0.9,
        background_color: Color = None,
        outline_color: Color = None,
        line_width: int = 1,
        position: Position = Position.RIGHT,
    ):
        """Incorporate the palette in the image.

        Args:
            output_scl (float, optional): Relative of the original image \
                in the output image. Defaults to 0.9.
            color_width_scl (float, optional): Width of the color rectangle relative \
                to the size of the palette. Defaults to 0.9.
            color_height_scl (float, optional): Height of the color rectangle relative \
                to the size of the palette. Defaults to 0.9.
            background_color (Color, optional): Background color of the palette. \
                Defaults to Color(220, 220, 220).
            outline_color (Color, optional): Outline color of the palette. \
                If not provided, the outline will be the same as the background color.
            line_width (int, optional): Width of the outline. Defaults to 1.
            position (Position, optional): Position of the palette. \
                 Defaults to Position.RIGHT.
        """

        if background_color is None:
            background_color = Color(220, 220, 220)
        if outline_color is None:
            outline_color = background_color

        logging.info("Incorporating palette in the image")

        # image resized

        if position == Position.RIGHT or position == Position.LEFT:
            # image size
            new_width = int(self._im.width * output_scl)
            new_height = int(self._im.height)
            # bars container size
            container_width = int(self._im.width * (1 - output_scl))
            container_height = int(self._im.height)
            # bars size
            bar_width = int(container_width * color_width_scl)
            bar_height = int(container_height / len(self._colors))
            # bars displacement
            bar_dx = int((container_width - bar_width) / 2)
            bar_dy = 0
            # color size
            color_height = bar_height * color_height_scl
            color_dx = 0
            color_dy = int((bar_height - color_height) / 2)
        else:
            # image size
            new_width = int(self._im.width)
            new_height = int(self._im.height * output_scl)
            # bars container size
            container_width = int(self._im.width)
            container_height = int(self._im.height * (1 - output_scl))
            # bars size
            bar_width = int(container_width / len(self._colors))
            bar_height = int(container_height * color_height_scl)
            # bars displacement
            bar_dx = 0
            bar_dy = int((container_height - bar_height) / 2)
            # color size
            color_width = bar_width * color_width_scl
            color_dx = int((bar_width - color_width) / 2)
            color_dy = 0

        # fill the container
        container = Image.new(
            "RGB",
            (container_width, container_height),
            background_color.rgb,
        )
        draw = ImageDraw.Draw(container)

        if position == Position.LEFT or position == Position.RIGHT:
            for i, c in enumerate(self._colors):
                x_0 = bar_dx + color_dx
                y_0 = bar_dy + color_dy + i * bar_height
                x_1 = x_0 + bar_width
                y_1 = y_0 + color_height

                draw.rectangle(
                    [x_0, y_0, x_1, y_1],
                    fill=c.rgb,
                    outline=outline_color.rgb,
                    width=line_width,
                )

            self._incorporated_palette = Image.new("RGB", (new_width, new_height))
            if position == Position.RIGHT:
                self._incorporated_palette.paste(self._im, (0, 0))
                self._incorporated_palette.paste(
                    container, (new_width - container_width, 0)
                )
            elif position == Position.LEFT:
                self._incorporated_palette.paste(self._im, (container_width, 0))
                self._incorporated_palette.paste(container, (0, 0))
        else:
            for i, c in enumerate(self._colors):
                x_0 = bar_dx + color_dx + i * bar_width
                y_0 = bar_dy + color_dy
                x_1 = x_0 + color_width
                y_1 = y_0 + bar_height

                draw.rectangle(
                    [x_0, y_0, x_1, y_1], fill=c.rgb, outline=outline_color.rgb
                )

            self._incorporated_palette = Image.new("RGB", (new_width, new_height))
            if position == Position.BOTTOM:
                self._incorporated_palette.paste(self._im, (0, 0))
                self._incorporated_palette.paste(
                    container, (0, new_height - container_height)
                )

            elif position == Position.TOP:
                self._incorporated_palette.paste(self._im, (0, container_height))
                self._incorporated_palette.paste(container, (0, 0))

        logging.info("Palette incorporated")

    def loadPaletteJSON(self, path: str):
        """Load a palette from a JSON file.

        Args:
            path (str): Path to the JSON file.
        """
        with open(path, "r") as f:
            data = json.load(f)
        self._colors = [Color(*c) for c in data["rgb"]]

    def printPalette(self):
        """Print the palette in the console.

        The console must support TrueColor.
        """
        # print the palette in the console
        cells = []
        BAR_WIDTH = 16
        for c in self._colors:
            row = []
            row.append(Cell("█" * BAR_WIDTH, fore=c))
            row.append(Cell(c.rgb_formatted))
            row.append(Cell(c.hsv_formatted))
            row.append(Cell(c.hex))
            cells.append(row)

        print(format_table(cells, border_fore=Color(211, 211, 211)))

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
        return self._path.split("/")[-1].split(".")[0]
