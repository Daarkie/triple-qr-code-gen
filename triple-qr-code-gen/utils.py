from PIL import Image

from tqr_gen import make_tqr


def get_color(num):
    nums_and_colors = {
        0: (255, 255, 255),
        1: (255, 255, 0),
        2: (255, 0, 0),
        3: (255, 100, 0),
        4: (0, 0, 255),
        5: (0, 255, 0),
        6: (255, 0, 255),
        7: (0, 0, 0)
    }
    return nums_and_colors[num]


def create_qr_image(text0, text1, text2):
    def draw_image():
        size = len(tqr_matrix)
        tqr_image = Image.new('RGB', (size, size))
        for x in range(size):
            for y in range(size):
                color = get_color(tqr_matrix[x][y])
                tqr_image.putpixel((x, y), color)
        return tqr_image

    tqr_matrix = make_tqr(text0, text1, text2)
    return draw_image()
