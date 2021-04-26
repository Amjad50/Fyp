from PIL import Image


def img_to_binary(img: Image) -> Image:
    return img.convert('L').point(lambda p: p > 100 and 255).convert('1')
