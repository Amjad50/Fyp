from .utils import box_size


# dot signs
def is_dot_box(box):
    w, h = box_size(box)
    return abs((w / h) - 1) < 0.2 or abs(w - h) < 2


# equal signs
def is_dash_box(box):
    w, h = box_size(box)
    return w / h > 4
