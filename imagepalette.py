# Lorenzo Rossi - www.lorenzoros.si - https://github.com/lorossi
# dreaming of better days

import argparse
import json
import logging
import pathlib

from PIL import Image, ImageDraw

from color import Color
from kmeans import KMeans
from terminal import format_color


class PaletteExtractor:
    # extracts the palette
    _colors: list[Color] = None
    _resized_width: int = 1000

    def __init__(self):
        self._colors = []

    def loadImage(self, path: str, palette_size: int = 5, resize: bool = False) -> None:
        self._path = path
        # removes folder and file extension from filename

        self._palette_size = palette_size
        self._im = Image.open(self._path)

        self._working_image = self._im.copy()
        # resize the image if it's too big
        # you might miss some colors but the runtime will be way lower
        if resize and self._im.width > self._resized_width:
            new_width = self._resized_width
            new_height = int(self._im.height / self._im.width * new_width)
            self._working_image = self._working_image.resize((new_width, new_height))

    def extractColors(self, seed: int = None):
        # start extracting the colors
        logging.info("Starting color extractions")
        pixels = self._working_image.load()
        # need to convert to list the list of lists
        pixels_list = [
            Color(*pixels[x, y])
            for x in range(self._working_image.width)
            for y in range(self._working_image.height)
        ]

        kmeans = KMeans(n_clusters=self._palette_size, random_seed=seed).fit(
            pixels=pixels_list
        )
        # append the fund colors to the private variable
        self._colors = kmeans._centroids
        # sort by saturation and hue
        self._colors.sort(key=lambda x: x.saturation, reverse=False)
        self._colors.sort(key=lambda x: x.hue, reverse=False)
        logging.info("Colors extracted")

    def generatePalette(self, output_width=1000, output_height=200):
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
        output_scl=0.9,
        palette_width_scl=0.1,
        palette_height_scl=0.9,
        background_color=(220, 220, 220),
        outline_color=(127, 127, 127),
        line_width=1,
        position="r",
    ):
        # position can be "l" for left, "r" for right, "t" for top,
        # "b" for bottom
        # image resized
        new_width = int(self._im.width / output_scl)
        new_height = int(self._im.height / output_scl)
        image_dx = int((new_width - self._im.width) / 2)
        image_dy = int((new_height - self._im.height) / 2)

        if position == "l" or position == "r":
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

        if position == "t" or position == "b":
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
            if position == "t":
                self._incorporated_palette.paste(
                    self._im, (image_dx, image_dy + palette_height)
                )
                self._incorporated_palette.paste(bars, (palette_dx, palette_dy))
            elif position == "b":
                self._incorporated_palette.paste(self._im, (image_dx, image_dy))
                self._incorporated_palette.paste(
                    bars,
                    (palette_dx, new_height - palette_height + image_dy + palette_dy),
                )

        logging.info("Palette incorporated")

    def printPalette(self):
        # print the palette in the console
        bar_width = 16
        max_rgb = max(len(str(c.rgb)) for c in self._colors)
        max_hsv = max(len(str(c.hsv_formatted)) for c in self._colors)
        max_hex = max(len(str(c.hex)) for c in self._colors)

        separator = " | "
        line_width = bar_width + max_rgb + max_hsv + max_hex + len(separator) * 6 + 1
        line_color = Color(233, 233, 233)  # light gray
        print("\n", format_color("Extracted color palette:", fore=line_color), "\n")
        print(" ", format_color("-" * line_width, fore=line_color), sep="")

        for c in self._colors:
            rgb = c.rgb
            hsv = c.hsv_formatted
            hex = c.hex

            spacing_rgb = max_rgb - len(str(rgb))
            spacing_hsv = max_hsv - len(str(hsv))

            print(format_color(" | ", fore=line_color), end="")
            print(format_color(" " * bar_width, back=c), sep=" ", end="")
            print(format_color(separator, fore=line_color), end="")
            print(f"rgb{rgb}{spacing_rgb * ' '}", end="")
            print(format_color(separator, fore=line_color), end="")
            print(f"hsv{hsv}{spacing_hsv * ' '}", end="")
            print(format_color(separator, fore=line_color), end="")
            print(f"{hex}", end="")

            print(format_color(" |", fore=line_color))

        print(" ", format_color("-" * line_width, fore=line_color), "\n", sep="")

    def crateFolder(self, path):
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def savePaletteImage(self, folder="output/"):
        # save the generated image
        self.crateFolder(folder)
        path = f"{folder}{self._filename}-palette.png"
        self._palette.save(path)
        logging.info(f"Palette image saved. Path: {path}")

    def saveIncorporatedPalette(self, folder="output/"):
        # save the generated image
        self.crateFolder(folder)
        path = f"{folder}{self._filename}-incorporated-palette.png"
        self._incorporated_palette.save(path)
        logging.info(f"Incorporated palette image saved. Path: {path}")

    def savePaletteJSON(self, folder: str = "output/"):
        # save the colors in a JSON file
        self.crateFolder(folder)

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


def main():
    parser = argparse.ArgumentParser(description="Extract color palette from any image")
    parser.add_argument("-i", "--input", help="Source image path")
    parser.add_argument(
        "-o", "--output", help="Custom output folder", default="output/"
    )
    parser.add_argument(
        "-c", "--colors", help="Number of extracted colors", type=int, default=5
    )
    parser.add_argument(
        "-r",
        "--resize",
        help="Resize the image for internal use. "
        "Calculations will be quicker but slightly less accurate",
        action="store_true",
    )
    parser.add_argument("--console", help="Log to console", action="store_true")
    parser.add_argument(
        "--palette", help="Create an image containing the palette", action="store_true"
    )
    parser.add_argument(
        "--printpalette", help="Print the palette in the console", action="store_true"
    )
    parser.add_argument(
        "--json", help="Create a JSON file containing the palette", action="store_true"
    )
    parser.add_argument(
        "--incorporated",
        help="Incorporate the palette inside the original image",
        action="store_true",
    )
    parser.add_argument(
        "--scl",
        help="Original image scale (valid if used in the incorporated mode). "
        "Default: 0.9",
        type=float,
        default=0.9,
    )
    parser.add_argument(
        "--palettewidth",
        help="Ratio of the palette to the original image "
        "(valid if used in the incorporated mode). "
        "Default: 0.02",
        type=float,
        default=0.015,
    )
    parser.add_argument(
        "--paletteheight",
        help="Ratio of the palette to the original image "
        "(valid if used in the incorporated mode). Default: 0.9",
        type=float,
        default=0.9,
    )
    parser.add_argument(
        "--position",
        help="Position of the color legend. Valid values: l, r, t, b "
        "(for left, right, top, bottom) (valid if used in the incorporated mode). "
        "Default: r",
        type=str,
        default="r",
    )
    parser.add_argument(
        "--color",
        help="Background color of the image. Pass 3 integers in range 0-255 "
        "(valid if used in the incorporated mode). Example: 244 34 111. "
        "Default 220 220 220",
        nargs="+",
        type=int,
        default=[220, 220, 220],
    )
    parser.add_argument(
        "--outline",
        help="Outline color of the palette. Pass 3 integers in range 0-255 "
        " (valid if used in the incorporated mode). Example: 244 34 111. "
        "Default 127 127 127",
        nargs="+",
        type=int,
        default=[127, 127, 127],
    )
    parser.add_argument(
        "--outlinewidth",
        help="Width of the outline of the palette "
        "(valid if used in the incorporated mode). Default 1",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--nooutline",
        help="Removes the outline of the palette "
        "(valid if used in the incorporated mode).",
        action="store_true",
    )

    args = parser.parse_args()

    # some args might not be valid, if so quit the script
    if not args.input:
        parser.error("Specify the input image. Use -h to get a list of commands.")
        quit()

    if (
        not args.printpalette
        and not args.palette
        and not args.json
        and not args.incorporated
    ):
        parser.error(
            "Specify the type of output (Palette, Printpalette, Incorporated, JSON). "
            "Use -h to get a list of commands."
        )
        quit()

    if len(args.color) > 3 or max(args.color) > 255 or min(args.color) < 0:
        parser.error(
            "The background color specified is wrong. "
            "Use -h to get a list of commands."
        )
        quit()

    if len(args.outline) > 3 or max(args.outline) > 255 or min(args.outline) < 0:
        parser.error(
            "The outline specified is wrong. Use -h to get a list of commands."
        )
        quit()

    if not any(args.position.lower() == p for p in ["l", "r", "t", "b"]):
        parser.error(
            "The position specified is wrong. Use -h to get a list of commands"
        )
        quit()

    if args.console:
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
        )
    else:
        logfile = __file__.replace(".py", ".log")
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=logging.INFO,
            filename=logfile,
            filemode="w+",
        )
        print(f"Logging in {logfile}. Use --console to view the log directly here")

    # add trailing slash to output folder
    if args.output[-1] != "/":
        output_folder = args.output + "/"
    else:
        output_folder = args.output

    # fire up the extractor and load an image
    p = PaletteExtractor()
    p.loadImage(path=args.input, palette_size=args.colors, resize=args.resize)
    p.extractColors()

    if args.printpalette:
        p.printPalette()
    if args.palette:
        p.generatePalette()
        p.savePaletteImage(folder=output_folder)
    if args.json:
        p.savePaletteJSON()
    if args.incorporated:
        background_color = tuple(args.color)
        if not args.nooutline:
            outline_color = tuple(args.outline)
        else:
            outline_color = None
        p.incorporatePalette(
            output_scl=args.scl,
            palette_width_scl=args.palettewidth,
            palette_height_scl=args.paletteheight,
            position=args.position,
            background_color=background_color,
            outline_color=outline_color,
            line_width=args.outlinewidth,
        )
        p.saveIncorporatedPalette(folder=output_folder)


if __name__ == "__main__":
    main()
