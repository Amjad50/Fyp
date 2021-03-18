import numpy as np

from .utils import box_size


def black_ratio(box, img):
    # img must be in binary format ("1"), so we convert to make sure
    img_arr = np.asarray(img.convert("1").crop(box))
    w, h = img_arr.shape
    full_size = w * h
    white_count = img_arr.sum()
    black_count = full_size - white_count

    return black_count / full_size


# dot signs
def is_dot_box(box, img):
    w, h = box_size(box)
    r = black_ratio(box, img)
    return r > 0.6 and (abs((w / h) - 1) < 0.2 or abs(w - h) < 2)


# equal signs
def is_dash_box(box):
    w, h = box_size(box)
    return w / h > 4
