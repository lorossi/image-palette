# Image Palette
Extract the dominant colors from any image and either add the palette to the source image, generate it as a separate file or get it in a json file.

This program uses [k-mean clustering](https://en.wikipedia.org/wiki/K-means_clustering) (provided by scikit) to determine the most prevalent colors. It's quite resources consuming but with a few precautions it can be made faster.

Look down below for sample images or check my [Instagram profile](https://www.instagram.com/lorossi97/) to see more of my work! If you want to replicate this effect in your own photos, make sure to look below for the instructions.

# Output
*Input image*
![starry-night](https://github.com/lorossi/image-palette/blob/master/output/starry-night.jpg?raw=true)

*Generated color palette*
![starry-night-color-palette](https://github.com/lorossi/image-palette/blob/master/output/starry-night-palette.png?raw=true)

*Palette integrated in original image*
![starry-night--with-incorporated-color-palette](https://github.com/lorossi/image-palette/blob/master/output/starry-night-incorporated-palette.png?raw=true)

*Json file with the color palette*

*Filename* `starry-night-json-palette.json`

*Content*

```
{
  "rgb":[
    [165,174,147],
    [107,132,155],
    [25,29,33],
    [66,90,137],
    [47,60,87]
  ],
  "hsv":[
    [79,15,68],
    [208,30,60],
    [210,24,12],
    [219,51,53],
    [220,45,34]
    ]
  }
```


# How to use
- Install Python3 on your PC
- Clone the repository or [download the release](https://github.com/lorossi/image-palette/releases/latest)
- Navigate to the folder containing the script
- Install the required Python modules with the command `python3 -m pip install -r requirements.txt`
- View a list of all the available arguments `python3 imagepalette.py -h`

## Image resizing

By using the command `--resize` (or `-r`) the image will be resized in order to speed up the colors extraction. The output image will not be affected and will be the same size as the original one.

## Arguments
| Command | Description | Optional | Defaults | Type |
|---|---|---|---|---|
| `-i` `--input` | Source image path | ✗ | `none` | `string` |
| `-o` `--output` | Custom output folder | ✓ | `output/` | `string` |
| `-c` `--colors` | Number of extracted colors | ✓ | `5` | `int` |
| `-r` `--resize` | Resize the image for internal use | ✓ | `none` | `none` |
| `--console` | Log to console | ✓ | `False` | `none` |
| `--palette` | Create an image containing the palette | ✓ <sup>but one of this group must be selected</sup> | `none` | `none` |
| `--json` | Create a JSON file containing the palette | ✓ <sup>but one of this group must be selected</sup> | `none` | `none` |
| `--incorporated` | Incorporate the palette inside the original image | ✓ <sup>but one of this group must be selected</sup> | `none` | `none` |
| `--scl` | Original image scale (valid if used in the incorporated mode) | ✓ | `0.9` | `float` |
| `--palettewidth` | Ratio of the palette to the original image (valid if used in the incorporated mode) | ✓ | `0.02` | `float` |
| `--paletteheight` | Ratio of the palette to the original image (valid if used in the incorporated mode) | ✓ | 0.9` | `float` |
| `--position` | Position of the color legend (valid if used in the incorporated mode) | ✓ | `r` | `{l, r, t, b}` |
| `--color` | Backround color of the image (valid if used in the incorporated mode) | ✓ | `220 220 220` | `int int int` |
| `--outline` | Outline color of the palette (valid if used in the incorporated mode) | ✓ | `127 127 127` | `int int int` |
| `--outlinewidth` | Width of the oultine of the palette (valid if used in the incorporated mode) | ✓ | `1` | `int` |
| `--nooutline` | Removes the outline of the palette (valid if used in the incorporated mode) | ✓ | `none` | `none` |

## Examples
- Generate a 4 colors palette of the image "image-1.png" and save it as a new image file: `python3 imagepalette.py -i image-1.png -c 4 --palette`
- Generate a 8 color palette of the image "image-1.png" and save it as a JSON file: `python3 imagepalette.py -i image-1.png -c 8 --json`
- Generate a 5 colors palette of the image "image-1.png" and incorporate it in the source image: `python3 imagepalette.py -i image-1.png -c 5 --incorporated`
    - The arguments `--palettewidth`, `--paletteheight`, `--scl`, `--position`, `--color`, `--outline`, `--nooutline` can be used to further customize the output image
- Generate a 5 colors palette of the image "image-1.png" and incorporate it on the left side the source image with a purple background and a gold outline 5 pixels wide: `python3 -i image-1.png --position l --incorporated --color 128 0 128 --outline 255 215 0 --outlinewidth 5 `

## Batch converting
I have included a script called `batch-convert.py` that will automatically create integrated palettes all the `.jpg` files placed in the same folder.

# License
This project is distributed under Attribution 4.0 International (CC BY 4.0) license.
