from math import ceil

import attr
import numpy as np
from PIL import Image, ImageFont, ImageDraw


class Config:
    """config constants"""

    INPUT = "sample/input_image.jpg"
    TEXT_FILE = "sample/input_text.txt"
    OUTPUT_FILE = "sample/output.jpg"
    OUTPUT_SCALE = 2
    FONT_NAME = "sample/Arial_Bold.ttf"
    FONT_SIZE = 10


@attr.s
class Vector:
    x = attr.ib(default=0)
    y = attr.ib(default=0)

    def __mul__(self, b):
        assert isinstance(b, (int, float))
        return self.__class__(x=self.x * b, y=self.y * b)

    def __rmul__(self, b):
        return self.__mul__(b)


def transform(file_in=None, file_out=None, source_text=None, font=None):
    # config defaults
    if file_in is None:
        file_in = Config.INPUT
    if file_out is None:
        file_out = Config.OUTPUT_FILE
    if source_text is None:
        with open(Config.TEXT_FILE) as fin:
            source_text = fin.read().replace("\n", "").replace(" ", "")
    if font is None:
        font = ImageFont.truetype(Config.FONT_NAME, Config.FONT_SIZE)

    SPACING_MAX = Config.FONT_SIZE

    input_image = Image.open(file_in)

    output_dimensions = (
        Vector(x=input_image.size[0], y=input_image.size[1]) * Config.OUTPUT_SCALE
    )

    input_vals = np.array(input_image.convert("L"))

    # bruteforce currect average density
    img_vals = 255 * np.ones(
        (output_dimensions.y, output_dimensions.x), dtype=np.uint8
    )
    y = 0
    x = 0
    cnt = 0
    while y < output_dimensions.y - Config.FONT_SIZE:
        # map current y -> input y
        input_y = int(y / Config.OUTPUT_SCALE)

        # find optimal spacing between min and max bounds
        spacing = []
        for i in range(min(SPACING_MAX, output_dimensions.x - x)):
            width = font.getsize(source_text[cnt % len(source_text)])[0] + i
            img = Image.new("L", (width, Config.FONT_SIZE), (255))
            ImageDraw.Draw(img).text((0, 0), source_text[cnt % len(source_text)], font=font)
            img = img.crop(box=(0, 2, img.width, img.height))

            # calculate brightness
            # Note: I experimented with a few different measures, but this
            #       seemed to always produce the best results
            calc_brightness = (np.mean(np.array(img)) - 128) * 2

            # calculate target brightness
            target_brightness = np.mean(
                input_vals[
                    input_y : input_y + ceil(img.height / Config.OUTPUT_SCALE),
                    int(x / Config.OUTPUT_SCALE) : int(x / Config.OUTPUT_SCALE)
                    + ceil(img.width / Config.OUTPUT_SCALE),
                ]
            )

            spacing.append((abs(target_brightness - calc_brightness), img))

        _, img = min(spacing, key=lambda x: x[0])
        if x + img.size[0] <= output_dimensions.x:
            img_vals[y : y + img.size[1], x : x + img.size[0]] = np.array(img)

        x += img.size[0]
        cnt += 1

        if x >= output_dimensions.x:
            x = 0
            y += img.size[1]

    img = Image.fromarray(img_vals, mode="L")
    img.save(file_out, format="PNG")
    file_out.seek(0)
    return file_out


if __name__ == "__main__":
    transform()
