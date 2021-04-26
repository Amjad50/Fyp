from PIL import ImageColor, ImageDraw

from utils.image import img_to_binary
from .symbol_segmenter import segment_image_crops


def draw_crops_rects(img, crops=None):
    if not crops:
        crops = segment_image_crops(img_to_binary(img), use_opencv=True)
    labeled_img = img.copy()
    labeled_img = labeled_img.convert('RGB')
    img_d = ImageDraw.Draw(labeled_img)

    for i, crop in enumerate(crops):
        l, t, r, d = crop
        l -= 1
        t -= 1

        # goes through all hsl colors, evenly divided by the number of crops
        color = ImageColor.getrgb(f'hsl({i / len(crops) * 360}, 100%, 50%)')
        img_d.rectangle((l, t, r, d), outline=color)

    return labeled_img
