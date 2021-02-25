from PIL import ImageColor, ImageDraw

from .symbol_segmenter import segment_image_crops


def label_crops(img, crops=None):
    if not crops:
        crops = segment_image_crops(img.convert('1'))
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
