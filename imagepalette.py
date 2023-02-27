"""Extract color palette from any image."""

import argparse
import logging

from modules.palette_extractor import PaletteExtractor
from modules.position import Position


def main():
    """Run the main function."""
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
        "--print-palette", help="Print the palette in the console", action="store_true"
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
        "--palette-width",
        help="Ratio of the palette to the original image "
        "(valid if used in the incorporated mode). "
        "Default: 0.02",
        type=float,
        default=0.015,
    )
    parser.add_argument(
        "--palette-height",
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
        "--outline-width",
        help="Width of the outline of the palette "
        "(valid if used in the incorporated mode). Default 1",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--no-outline",
        help="Removes the outline of the palette "
        "(valid if used in the incorporated mode).",
        action="store_true",
    )
    parser.add_argument(
        "--seed",
        help="Seed for the random generator in the KMeans algorithm. "
        "Useful to get the same palette every time",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--min-color-distance",
        help="Minimum square distance between colors in the palette. " "Default: 1",
        type=int,
        default=1,
    )

    args = parser.parse_args()

    # some args might not be valid, if so quit the script
    if not args.input:
        parser.error("Specify the input image. Use -h to get a list of commands.")

    if (
        not args.print_palette
        and not args.palette
        and not args.json
        and not args.incorporated
    ):
        parser.error(
            "Specify the type of output (Palette, Printpalette, Incorporated, JSON). "
            "Use -h to get a list of commands."
        )

    if len(args.color) > 3 or max(args.color) > 255 or min(args.color) < 0:
        parser.error(
            "The background color specified is wrong. "
            "Use -h to get a list of commands."
        )

    if len(args.outline) > 3 or max(args.outline) > 255 or min(args.outline) < 0:
        parser.error(
            "The outline specified is wrong. Use -h to get a list of commands."
        )

    if not any(args.position.lower() == p for p in ["l", "r", "t", "b"]):
        parser.error(
            "The position specified is wrong. Use -h to get a list of commands"
        )
        return

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
    p.extractColors(seed=args.seed, min_dist=args.min_color_distance)

    if args.print_palette:
        p.printPalette()
    if args.palette:
        p.generatePalette()
        p.savePaletteImage(folder=output_folder)
    if args.json:
        p.savePaletteJSON()
    if args.incorporated:
        background_color = tuple(args.color)
        if not args.no_outline:
            outline_color = tuple(args.outline)
        else:
            outline_color = None
        p.incorporatePalette(
            output_scl=args.scl,
            palette_width_scl=args.palette_width,
            palette_height_scl=args.palette_height,
            position=Position(args.position),
            background_color=background_color,
            outline_color=outline_color,
            line_width=args.outline_width,
        )
        p.saveIncorporatedPalette(folder=output_folder)


if __name__ == "__main__":
    main()
