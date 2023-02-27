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
    def __init__(self):
        self._colours = []
        self._resized_width = 1000

    def loadImage(self, path, selected_colours=5, resize=False):
        self._path = path
        # removes folder and file extension from filename
        self._filename = ".".join(self._path.split("/")[-1].split(".")[:-1])
        self._selected_colours = selected_colours
        try:
            self._im = Image.open(self._path)
        except Exception as e:
            logging.error(f"Cannot open image {self._path}. Error: {e}")
            raise e

        self._working_image = self._im.copy()
        # resize the image if it's too big
        # you might miss some colours but the runtime will be way lower
        if resize and self._im.width > self._resized_width:
            new_width = self._resized_width
            new_height = int(self._im.height / self._im.width * new_width)
            self._working_image = self._working_image.resize(
                (new_width, new_height)
            )

    def extractColours(self):
        # start extracting the colours
        logging.info("Starting colour extractions")
        pixels = self._working_image.load()
        # need to convert to list the list of lists
        pixels_list = [
            pixels[x, y]
            for x in range(self._working_image.width)
            for y in range(self._working_image.height)
        ]
        kmeans = KMeans(n_clusters=self._selected_colours, initial_state=0).fit(
            pixels_list
        )
        # append the fund colours to the private variable
        for k in kmeans.centroids:
            self._colours.append(Color(k))
        # sort by saturation and hue
        self._colours.sort(key=lambda x: x.saturation, reverse=False)
        self._colours.sort(key=lambda x: x.hue, reverse=False)
        logging.info("Colours extracted")

    def generatePalette(self, output_width=1000, output_height=200):
        # generates an image containing the palette
        logging.info("Starting palette image generation")
        bars_width = int(output_width / self._selected_colours)

        self._palette = Image.new("RGB", (output_width, output_height))
        draw = ImageDraw.Draw(self._palette)

        i = 0
        for c in self._colours:
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
        background_colour=(220, 220, 220),
        outline_colour=(127, 127, 127),
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
            slice_height = int(palette_height / self._selected_colours)
            bar_height = int(slice_height * 0.75)
            bar_width = int(palette_width * 0.5)
            # displacement
            bars_dx = int((palette_width - bar_width) / 2)
            bars_dy = int((slice_height - bar_height) / 2)

            logging.info("Starting palette incorporation")
            bars = Image.new(
                "RGB", (palette_width, palette_height), colour=background_colour
            )
            draw = ImageDraw.Draw(bars)
            # draw each bar
            i = 0
            for c in self._colours:
                x_0 = bars_dx
                y_0 = i * slice_height + bars_dy
                x_1 = x_0 + bar_width
                y_1 = y_0 + bar_height
                fill = c.rgb
                draw.rectangle(
                    [x_0, y_0, x_1, y_1],
                    fill=fill,
                    outline=outline_colour,
                    width=line_width,
                )
                i += 1

            # left or right
            self._incorporated_palette = Image.new(
                "RGB", (new_width + palette_width, new_height), colour=background_colour
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
            slice_width = int(palette_width / self._selected_colours)
            bar_width = int(slice_width * 0.75)
            bar_height = int(palette_height * 0.5)

            # displacement
            bars_dx = int((slice_width - bar_width) / 2)
            bars_dy = int((palette_height - bar_height) / 2)

            logging.info("Starting palette incorporation")
            bars = Image.new(
                "RGB", (palette_width, palette_height), colour=background_colour
            )
            draw = ImageDraw.Draw(bars)
            # draw each bar
            i = 0
            for c in self._colours:
                x_0 = i * slice_width + bars_dx
                y_0 = bars_dy
                x_1 = x_0 + bar_width
                y_1 = y_0 + bar_height
                fill = c.rgb
                draw.rectangle(
                    [x_0, y_0, x_1, y_1],
                    fill=fill,
                    outline=outline_colour,
                    width=line_width,
                )
                i += 1

            self._incorporated_palette = Image.new(
                "RGB",
                (new_width, new_height + palette_height),
                colour=background_colour,
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
        max_rgb = max(len(str(c.rgb)) for c in self._colours)
        max_hsv = max(len(str(c.hsv_formatted)) for c in self._colours)
        max_hex = max(len(str(c.hex)) for c in self._colours)

        separator = " | "
        line_width = bar_width + max_rgb + max_hsv + max_hex + len(separator) * 6 + 1
        line_colour = Color([233, 233, 233])  # light gray
        print("\n", format_color("Extracted colour palette:", fore=line_colour), "\n")
        print(" ", format_color("-" * line_width, fore=line_colour), sep="")

        for c in self._colours:
            rgb = c.rgb
            hsv = c.hsv_formatted
            hex = c.hex

            spacing_rgb = max_rgb - len(str(rgb))
            spacing_hsv = max_hsv - len(str(hsv))

            print(format_color(" | ", fore=line_colour), end="")
            print(format_color(" " * bar_width, back=c), sep=" ", end="")
            print(format_color(separator, fore=line_colour), end="")
            print(f"rgb{rgb}{spacing_rgb * ' '}", end="")
            print(format_color(separator, fore=line_colour), end="")
            print(f"hsv{hsv}{spacing_hsv * ' '}", end="")
            print(format_color(separator, fore=line_colour), end="")
            print(f"{hex}", end="")

            print(format_color(" |", fore=line_colour))

        print(" ", format_color("-" * line_width, fore=line_colour), "\n", sep="")

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

    def savePaletteJSON(self, folder="output/"):
        # save the colours in a JSON file
        self.crateFolder(folder)

        json_dict = {"rgb": [], "hsv": [], "hex": []}

        for c in self._colours:
            json_dict["rgb"].append(c.rgb)
            json_dict["hsv"].append(c.hsv)
            json_dict["hex"].append(c.hex)

        path = f"{folder}{self._filename}-json-palette.json"
        with open(path, "w") as json_file:
            json.dump(json_dict, json_file, indent=2)
        logging.info(f"JSON file saved. Path: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract colour palette from any image"
    )
    parser.add_argument("-i", "--input", help="Source image path")
    parser.add_argument(
        "-o", "--output", help="Custom output folder", default="output/"
    )
    parser.add_argument(
        "-c", "--colours", help="Number of extracted colours", type=int, default=5
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
        help="Position of the colour legend. Valid values: l, r, t, b "
        "(for left, right, top, bottom) (valid if used in the incorporated mode). "
        "Default: r",
        type=str,
        default="r",
    )
    parser.add_argument(
        "--colour",
        help="Background colour of the image. Pass 3 integers in range 0-255 "
        "(valid if used in the incorporated mode). Example: 244 34 111. "
        "Default 220 220 220",
        nargs="+",
        type=int,
        default=[220, 220, 220],
    )
    parser.add_argument(
        "--outline",
        help="Outline colour of the palette. Pass 3 integers in range 0-255 "
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

    if len(args.colour) > 3 or max(args.colour) > 255 or min(args.colour) < 0:
        parser.error(
            "The background colour specified is wrong. "
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
    p.loadImage(path=args.input, selected_colours=args.colours, resize=args.resize)
    p.extractColours()

    if args.printpalette:
        p.printPalette()
    if args.palette:
        p.generatePalette()
        p.savePaletteImage(folder=output_folder)
    if args.json:
        p.savePaletteJSON()
    if args.incorporated:
        background_colour = tuple(args.colour)
        if not args.nooutline:
            outline_colour = tuple(args.outline)
        else:
            outline_colour = None
        p.incorporatePalette(
            output_scl=args.scl,
            palette_width_scl=args.palettewidth,
            palette_height_scl=args.paletteheight,
            position=args.position,
            background_colour=background_colour,
            outline_colour=outline_colour,
            line_width=args.outlinewidth,
        )
        p.saveIncorporatedPalette(folder=output_folder)


if __name__ == "__main__":
    main()
