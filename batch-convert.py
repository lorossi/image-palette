from pathlib import Path

from PIL import Image

from modules.palette_extractor import PaletteExtractor


def main():
    path = Path(".").glob("*.jpg")
    photos = [str(x) for x in path if x.is_file()]

    print(f"Starting extraction of {len(photos)} photos")
    i = 0
    for photo in photos:
        im = Image.open(photo)
        width, height = im.size

        p = PaletteExtractor()
        p.loadImage(photo, resize=True)
        p.extractColors(min_dist=25, seed=42)

        if width > height:
            # horizontal image
            p.incorporatePalette(
                output_scl=0.9,
                color_height_scl=0.75,
                color_width_scl=0.9,
                position="r",
            )
        else:
            # vertical image
            p.incorporatePalette(
                output_scl=0.9,
                color_height_scl=0.9,
                color_width_scl=0.75,
                position="b",
            )

        p.saveIncorporatedPalette(folder="Edited/")
        print(f"{photo} done. {i+1}/{len(photos)}.")
        i += 1


if __name__ == "__main__":
    main()
