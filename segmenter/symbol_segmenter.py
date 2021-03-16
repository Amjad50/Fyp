import copy
from itertools import permutations

import cv2
from PIL import Image, ImageOps

from .simple_identifiers import *
from .utils import *


def find_possible_equal_merges(crops, _img):
    # 1- find all dash symbols
    dash_symbols = list(filter(is_dash_box, crops))

    def can_be_equal_sign(crop1, crop2):
        c1_w, c1_h = box_size(crop1)
        c2_w, c2_h = box_size(crop2)

        if abs(c1_w - c2_w) > 3:
            return False

        c1_left, c1_top, c1_right, c1_down = crop1
        c2_left, c2_top, c2_right, c2_down = crop2

        if c1_down >= c2_top:
            return False

        if abs(c1_left - c2_left) > 3:
            return False

        if is_another_in_between(crop1, crop2, crops):
            return False

        return True

    # 2- search through all of them and find the possible to merge
    return list(filter(lambda x: can_be_equal_sign(x[0], x[1]), permutations(dash_symbols, 2)))


def find_possible_colon_merges(crops, img):
    # 1- find all dot symbols
    dot_symbols = list(filter(lambda crop: is_dot_box(crop, img), crops))

    def can_be_colon(crop1, crop2):
        c1_w, c1_h = box_size(crop1)
        c2_w, c2_h = box_size(crop2)

        if abs(c1_w - c2_w) > 3 or abs(c1_h - c2_h) > 3:
            return False

        c1_left, c1_top, c1_right, c1_down = crop1
        c2_left, c2_top, c2_right, c2_down = crop2

        if c1_down >= c2_top:
            return False

        if abs(c1_left - c2_left) > 3:
            return False

        if is_another_in_between(crop1, crop2, crops):
            return False

        return True

    # 2- search through all of them and find the possible to merge
    return list(filter(lambda x: can_be_colon(x[0], x[1]), permutations(dot_symbols, 2)))


def find_possible_i_j_merges(crops, img):
    # 1- find all dot symbols
    dot_symbols = list(filter(lambda crop: is_dot_box(crop, img), crops))

    possible_combinations = []

    for dot_symbol in dot_symbols:
        for crop in crops:
            if crop not in dot_symbols:
                possible_combinations.append((dot_symbol, crop))

    def can_be_i_j(dot, crop):
        d_l, d_t, d_r, d_d = dot
        c_l, c_t, c_r, c_d = crop

        # dot must be on top
        if d_t > c_d or d_t > c_t:
            return False

        if d_l > c_r or d_r < c_l:
            return False

        if is_dash_box(crop):
            return False

        if is_another_in_between(dot, crop, crops):
            return False

        return True

    # 2- search through all characters with dots to find the merges
    return list(filter(lambda x: can_be_i_j(x[0], x[1]), possible_combinations))


def merge_cropped_images(cropped_img1, cropped_img2):
    assert cropped_img1.shape == cropped_img2.shape

    return cropped_img1 & cropped_img2


def merge_segments(crops, cropped_images, possible_merges):
    if len(possible_merges) != 0:
        crops = copy.deepcopy(crops)

    indices_to_remove = set()
    for c1, c2 in possible_merges:
        c1_i = crops.index(c1)
        c2_i = crops.index(c2)

        indices_to_remove.add(c1_i)
        indices_to_remove.add(c2_i)

        crops.append(merge_boxes(c1, c2))

        cropped_images.append(merge_cropped_images(cropped_images[c1_i], cropped_images[c2_i]))

    for index in sorted(indices_to_remove, reverse=True):
        crops.pop(index)
        cropped_images.pop(index)

    return crops, cropped_images


def try_merge_segments(crops, cropped_images, img):
    # order is important
    crops, cropped_images = merge_segments(crops, cropped_images, find_possible_equal_merges(crops, img))
    crops, cropped_images = merge_segments(crops, cropped_images, find_possible_colon_merges(crops, img))
    crops, cropped_images = merge_segments(crops, cropped_images, find_possible_i_j_merges(crops, img))

    return crops, cropped_images


def final_crop_images(crops, cropped_images):
    assert len(crops) == len(cropped_images)

    result = []

    for crop, cropped_image in zip(crops, cropped_images):
        result.append(Image.fromarray(cropped_image).crop(crop))

    return result


def __convert_to_ltrd(bounding_box):
    l, t, w, h = bounding_box

    return l, t, l + w, t + h


def segment_image(img: Image):
    gray_inverted_img = np.asarray(ImageOps.invert(img.convert('L')))

    components, _ = cv2.findContours(gray_inverted_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    crops = [__convert_to_ltrd(cv2.boundingRect(c)) for c in components]

    cropped_images = [None] * len(crops)
    for i, crop in enumerate(crops):
        img_arr = np.ones_like(gray_inverted_img, dtype=bool)
        l, t, r, d = crop
        img_arr[t:d, l:r] = np.asarray(img.crop(crop))

        cropped_images[i] = img_arr

    # tries to find symbols that are mergable, like `=`, `:`, `i`, `j`... and merge them
    crops, cropped_images = try_merge_segments(crops, cropped_images, img)
    cropped_images = final_crop_images(crops, cropped_images)

    return list(zip(crops, cropped_images))


def segment_image_crops(img: Image):
    crops_images = segment_image(img)
    crops, _cropped_images = list(zip(*crops_images))
    return list(crops)
