from typing import List

from PIL import ImageDraw, ImageFont

from segmenter.symbol_segmenter import segment_image
from segmenter.utils import is_another_in_between
from utils.types import LabeledCrops, LabelCrop, Box
from .classifier import SVMClassifier


def draw_labeled_crops(img, labeled_crops):
    labeled_img = img.copy()
    labeled_img = labeled_img.convert('RGB')
    img_d = ImageDraw.Draw(labeled_img)

    font = ImageFont.truetype('arial.ttf', size=20, layout_engine=ImageFont.LAYOUT_BASIC)

    for i, labeled_crop in enumerate(labeled_crops):
        label, crop = labeled_crop
        l, t, r, d = crop
        l -= 1
        t -= 1
        fw, fh = font.getsize(label)
        img_d.text((l - fw, t - fh), label, font=font, fill=(67, 64, 255))

    return labeled_img


def __sort_labeled_crops(labeled_crops) -> LabeledCrops:
    def sort_key(label_crop: LabelCrop) -> int:
        l, _t, r, _d = label_crop[1]

        return l * 1000 - r

    return sorted(labeled_crops, key=sort_key)


def __other_vertically_between(crop1: Box, crop2: Box, crops: List[Box]) -> bool:
    l1, t1, r1, d1 = crop1
    l2, t2, r2, d2 = crop2

    # crop1 should be on top
    if t2 < t1:
        __other_vertically_between(crop2, crop1, crops)

    for crop in crops:
        if crop == crop1 or crop == crop2:
            continue

        l, t, r, d = crop

        # if its in the middle in terms of height, we check using `line intersect`
        # using the method `is_another_in_between`, as sometimes it might be in the middle in terms of `top` and `down`
        # but its far away in terms of `right` and `left`, and to make checking easier for us, we use this method
        if d < t2 and t > d1 and is_another_in_between(crop1, crop2, [crop]):
            return True

    return False


def __is_frac(frac_crop: Box, crops: List[Box]) -> bool:
    left, top, right, down = frac_crop

    top_found = False
    down_found = False

    for other_crop in crops:
        if top_found and down_found:
            return True

        if other_crop == frac_crop:
            continue

        other_left, other_top, other_right, other_down = other_crop

        if left <= other_left and right >= other_right:
            if other_top > down and not __other_vertically_between(frac_crop, other_crop, crops):
                down_found = True
            elif other_down < top and not __other_vertically_between(other_crop, frac_crop, crops):
                top_found = True

    return top_found and down_found


def __fix_frac_symbols(labeled_crops: LabeledCrops) -> LabeledCrops:
    """
    This function tries to identify if a `-` symbol is actually a `frac` and replace its label
    """

    _labels, crops = list(zip(*labeled_crops))

    for i, (label, crop) in enumerate(labeled_crops):
        if label == '-':
            if __is_frac(crop, crops):
                labeled_crops[i] = ('\\frac', crop)

    return labeled_crops


def get_labeled_crops(img, svm_model: SVMClassifier) -> LabeledCrops:
    crops_images = segment_image(img)
    crops, cropped_images = list(zip(*crops_images))

    predicted_labels: List[str] = []

    for crop, cropped_img in crops_images:
        predicted_labels.append(svm_model.predict_label(cropped_img))

    labeled_crops = __sort_labeled_crops(list(zip(predicted_labels, crops)))

    return __fix_frac_symbols(labeled_crops)
