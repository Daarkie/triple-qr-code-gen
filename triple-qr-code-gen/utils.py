from PIL import Image
from kivy.core.image import Image as CoreImage
from io import BytesIO
import numpy as np

from tqr_gen import make_tqr


def get_color(num):
    nums_and_colors = {
        0: (255, 255, 255, 255),
        1: (255, 255, 0, 0),
        2: (255, 0, 0, 0),
        3: (255, 100, 0, 0),
        4: (0, 0, 255, 0),
        5: (0, 255, 0, 0),
        6: (255, 0, 255, 0),
        7: (0, 0, 0, 0)
    }
    return nums_and_colors[num]


def create_tqr_image(text0, text1, text2):
    def draw_image():
        size = len(tqr_matrix) * 2
        print(tqr_matrix[12])
        tqr_image = Image.new('RGBA', (size, size))
        for x in range(0, size, 2):
            for y in range(0, size, 2):
                print(f"X = {x} and Y = {y}")
                color = get_color(int(np.int64(tqr_matrix[x // 2][y // 2])))
                tqr_image.putpixel((x, y), color)
                tqr_image.putpixel((x + 1, y), color)
                tqr_image.putpixel((x, y + 1), color)
                tqr_image.putpixel((x + 1, y + 1), color)
        return tqr_image

    tqr_matrix = make_tqr(text0, text1, text2)
    buffer = BytesIO()
    draw_image().save(buffer, format='png')
    buffer.seek(0)
    return CoreImage(buffer, ext='png').texture
