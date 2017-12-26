from math import ceil

from PIL import Image, ImageFont, ImageDraw
import numpy as np

# specified constants - MODIFY THESE
INPUT = "sample/input_image.jpg"
TEXT_FILE = "sample/input_text.txt"
OUTPUT_FILE = "sample/output.jpg"
OUTPUT_SCALE = 2
FONT_NAME = "sample/Arial_Bold.ttf"
FONT_SIZE = 10

# derived constants
INPUT_IMAGE = Image.open(INPUT)
INPUT_DIMENSIONS = INPUT_IMAGE.size
OUTPUT_DIMENSIONS = (INPUT_DIMENSIONS[0] * OUTPUT_SCALE, INPUT_DIMENSIONS[1] * OUTPUT_SCALE)
FONT = ImageFont.truetype(FONT_NAME, FONT_SIZE)
with open(TEXT_FILE) as fin:
    TEXT = fin.read().replace("\n", "").replace(" ", "")


def main():
    SPACING_MAX = FONT_SIZE

    input_vals = np.array(Image.open(INPUT).convert('L'))

    # bruteforce currect average density
    img_vals = 255*np.ones((OUTPUT_DIMENSIONS[1], OUTPUT_DIMENSIONS[0]), dtype=np.uint8)
    y = 0
    x = 0
    cnt = 0
    while y < OUTPUT_DIMENSIONS[1] - FONT_SIZE:
        # map current y -> input y
        input_y = int(y/OUTPUT_SCALE)

        # find optimal spacing between min and max bounds
        spacing = []
        for i in range(min(SPACING_MAX, OUTPUT_DIMENSIONS[0] - x)):
            width = FONT.getsize(TEXT[cnt % len(TEXT)])[0] + i
            img = Image.new("L", (width, FONT_SIZE), (255))
            ImageDraw.Draw(img).text((0, 0), TEXT[cnt % len(TEXT)], font=FONT)
            img = img.crop(box=(0, 2, img.width, img.height))

            # calculate brightness
            # Note: I experimented with a few different measures, but this seemed
            #       to always produce the best results
            calc_brightness = (np.mean(np.array(img)) - 128) * 2

            # calculate target brightness
            target_brightness = np.mean(input_vals[
                    input_y: input_y+ceil(img.height/OUTPUT_SCALE),
                    int(x/OUTPUT_SCALE): int(x/OUTPUT_SCALE) + ceil(img.width/OUTPUT_SCALE)])

            spacing.append((abs(target_brightness - calc_brightness), img))

        _, img = min(spacing, key=lambda x: x[0])
        if x + img.size[0] <= OUTPUT_DIMENSIONS[0]:
            img_vals[y:y+img.size[1], x:x+img.size[0]] = np.array(img)

        x += img.size[0]
        cnt += 1

        if x >= OUTPUT_DIMENSIONS[0]:
            x = 0
            y += img.size[1]

    img = Image.fromarray(img_vals, mode='L')
    img.show()
    img.save(OUTPUT_FILE)


if __name__ == '__main__':
    main()
