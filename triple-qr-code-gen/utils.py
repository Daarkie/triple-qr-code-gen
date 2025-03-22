from PIL import Image
from enum import Enum

class Color(Enum):
    NONE = 0
    FIRST = 1
    SECOND = 2
    THIRD = 4
    FCOMBOS = 3
    FCOMBOT = 5
    SCOMBOT = 6
    COMBO = 7

def draw(qr, color1, color2, color3):
    qr_image = Image.new('RGBA', (250, 250), "transparent")

def create_qr_image(text0, text1):
