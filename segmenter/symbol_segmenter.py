import copy
from itertools import permutations
from typing import Tuple

import cv2
from PIL import Image, ImageOps

from .simple_identifiers import *
from .utils import *


def __segment_char_flood_fill(img: np.ndarray, start: Tuple[int, int]):
    """
    Runs given the image and where it should start,
    it will go recursively from the starting position and remove every
    black pixel until there is no more connected black pixels.

    Returns:
    - the image with the character containing `start` removed.
    - the box boundaries of the character
    """

    assert img.dtype == bool

    img = img.copy()
    result_img_cropped = np.ones_like(img, dtype=bool)
    h, w = img.shape

    left = right = start[0]
    top = down = start[1]

    queue = {start}
    visited = set()

    while queue:
        now = queue.pop()

        # add to visited
        visited.add(now)

        # convert the pixel to white
        # Access in arrays is in `y, x` or `row, col` that's why it is inverted here
        img[now[1], now[0]] = True
        # move the into the result img crop
        result_img_cropped[now[1], now[0]] = False

        if now[0] > right:
            right = now[0]
        if now[0] < left:
            left = now[0]
        if now[1] > down:
            down = now[1]
        if now[1] < top:
            top = now[1]

        # look trough all 8 surrounding pixels
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue

                x = now[0] + i
                y = now[1] + j

                # in bounds
                if 0 <= x < w and 0 <= y < h:
                    # not visited
                    if (x, y) not in visited:
                        # black
                        # Access in arrays is inverted
                        if not img[y, x]:
                            queue.add((x, y))

    # the plus 1 is for the extra space we didn't reach
    return (left, top, right + 1, down + 1), img, result_img_cropped


def __find_possible_equal_merges(crops, _img):
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


def __find_possible_colon_merges(crops, img):
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


def __find_possible_i_j_merges(crops, img):
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


def __merge_cropped_images(cropped_img1, cropped_img2):
    assert cropped_img1.shape == cropped_img2.shape

    return cropped_img1 & cropped_img2


def __merge_segments(crops, cropped_images, possible_merges):
    if len(possible_merges) != 0:
        crops = copy.deepcopy(crops)

    indices_to_remove = set()
    for c1, c2 in possible_merges:
        c1_i = crops.index(c1)
        c2_i = crops.index(c2)

        indices_to_remove.add(c1_i)
        indices_to_remove.add(c2_i)

        crops.append(merge_boxes(c1, c2))

        cropped_images.append(__merge_cropped_images(cropped_images[c1_i], cropped_images[c2_i]))

    for index in sorted(indices_to_remove, reverse=True):
        crops.pop(index)
        cropped_images.pop(index)

    return crops, cropped_images


def __try_merge_segments(crops, cropped_images, img):
    # order is important
    crops, cropped_images = __merge_segments(crops, cropped_images, __find_possible_equal_merges(crops, img))
    crops, cropped_images = __merge_segments(crops, cropped_images, __find_possible_colon_merges(crops, img))
    crops, cropped_images = __merge_segments(crops, cropped_images, __find_possible_i_j_merges(crops, img))

    return crops, cropped_images


def __final_crop_images(crops, cropped_images):
    assert len(crops) == len(cropped_images)

    result = []

    for crop, cropped_image in zip(crops, cropped_images):
        result.append(Image.fromarray(cropped_image).crop(crop))

    return result


def __convert_to_ltrd(bounding_box):
    l, t, w, h = bounding_box

    return l, t, l + w, t + h


def __get_crops_images_opencv(img: Image):
    img_arr = np.asarray(img)
    gray_inverted_img = np.asarray(ImageOps.invert(img.convert('L')))

    components, _ = cv2.findContours(gray_inverted_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    crops = [__convert_to_ltrd(cv2.boundingRect(c)) for c in components]

    cropped_images = [None] * len(crops)
    for i in range(len(components)):
        mask = np.zeros_like(gray_inverted_img)
        cv2.drawContours(mask, components, i, 255, -1)  # Draw filled contour in mask
        out = np.ones_like(img_arr, dtype=bool)
        out[mask == 255] = img_arr[mask == 255]

        cropped_images[i] = out

    return crops, cropped_images


def __get_crops_images_flood_fill(img: Image):
    img_arr = np.array(img)
    h, w = img_arr.shape

    crops = []
    cropped_images = []
    for x in range(w):
        for y in range(h):
            # Access in arrays is inverted because it is in form `row, col` == `y, x`
            if not img_arr[y, x]:
                (crop_box, img_arr, result_for_this_crop) = __segment_char_flood_fill(img_arr, (x, y))
                cropped_images.append(result_for_this_crop)
                crops.append(crop_box)

    return crops, cropped_images


def segment_image(img: Image, use_opencv: bool = True):
    if use_opencv:
        crops, cropped_images = __get_crops_images_opencv(img)
    else:
        crops, cropped_images = __get_crops_images_flood_fill(img)

    # tries to find symbols that are mergable, like `=`, `:`, `i`, `j`... and merge them
    crops, cropped_images = __try_merge_segments(crops, cropped_images, img)
    cropped_images = __final_crop_images(crops, cropped_images)

    def sort_key(crop_image: Tuple) -> int:
        l, _t, r, _d = crop_image[0]

        return l * 1000 - r

    crops_images = list(zip(crops, cropped_images))

    # return sorted segments from left to right
    return sorted(crops_images, key=sort_key)


def segment_image_crops(img: Image, use_opencv: bool = True):
    crops_images = segment_image(img, use_opencv=use_opencv)
    crops, _cropped_images = list(zip(*crops_images))
    return list(crops)
