from pathlib import Path
from PIL import Image
from imagepalette import PaletteExtractor


def main():
    path = Path(".").glob('DSC*jpg')
    photos = [str(x) for x in path if x.is_file()]

    print(f"Starting extraction of {len(photos)} photos")
    i = 0
    for photo in photos:
        im = Image.open(photo)
        width, height = im.size

        p = PaletteExtractor()
        p.loadImage(photo, selected_colors=5, resize=True)
        p.extractColors()

        if width > height:
            # horizontal image
            p.incorporatePalette(output_scl=0.9, palette_height_scl=0.9, palette_width_scl=0.1, position="r", background_color=(220, 220, 220))
        else:
            # vertical image
            p.incorporatePalette(output_scl=0.9, palette_height_scl=0.9, palette_width_scl=0.1, position="b", background_color=(220, 220, 220))

        p.saveIncorporatedPalette()
        print(f"{photo} done. {i+1}/{len(photos)}.")
        i += 1


if __name__ == "__main__":
    main()
