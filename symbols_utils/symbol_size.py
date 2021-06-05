from segmenter.utils import box_size, box_center

# default sizes of symbols
SYMBOLS_DEFAULT_SIZES = {'0': (29, 48), '1': (23, 46), '2': (28, 46), '3': (29, 48), '4': (31, 47), '5': (28, 48),
                         '6': (29, 48), '7': (30, 49),
                         '8': (29, 48), '9': (29, 48), 'a': (31, 32), 'b': (26, 49), 'c': (27, 32), 'd': (32, 49),
                         'e': (27, 32), 'f': (34, 63),
                         'g': (32, 45), 'h': (34, 49), 'i': (18, 47), 'j': (28, 60), 'k': (31, 49), 'l': (15, 49),
                         'm': (56, 32), 'n': (37, 32),
                         'o': (29, 32), 'p': (36, 44), 'q': (28, 44), 'r': (28, 32), 's': (25, 32), 't': (21, 44),
                         'u': (35, 32), 'v': (30, 32),
                         'w': (46, 32), 'x': (34, 32), 'y': (32, 45), 'z': (29, 32), 'A': (47, 49), 'B': (49, 47),
                         'C': (49, 51), 'D': (53, 47),
                         'E': (50, 47), 'F': (49, 47), 'G': (49, 51), 'H': (58, 47), 'I': (32, 47), 'J': (39, 49),
                         'K': (58, 47), 'L': (41, 47),
                         'M': (69, 47), 'N': (58, 47), 'O': (48, 51), 'P': (49, 47), 'Q': (48, 62), 'R': (49, 49),
                         'S': (40, 51), 'T': (47, 47),
                         'U': (47, 49), 'V': (49, 49), 'W': (68, 49), 'X': (57, 47), 'Y': (49, 47), 'Z': (46, 47),
                         '=': (46, 16), '-': (42, 3),
                         '+': (46, 46), '(': (16, 69), ')': (16, 69), '[': (10, 69), ']': (10, 69), ',': (8, 20),
                         '.': (7, 7), '|': (5, 69),
                         '\\sum': (91, 97), '\\pi': (37, 31), '\\int': (61, 153),
                         # it does not matter the size of `frac` since its not always the same
                         '\\frac': (100, 3), }

HAS_BELOW_BASELINE_GROUPS = {'fgjpqyQ,': 12, '()[]|': 15}


def __find_baseline_extra_height(symbol):
    for k, v in HAS_BELOW_BASELINE_GROUPS.items():
        if symbol in k:
            return v
    # special special case
    if symbol == '\\int':
        return 57
    if symbol == '\\sum':
        return 30

    return None


# returns the length from the top of the symbol to get to the baseline
def get_baseline_height(symbol_name, box):
    w, h = box_size(box)

    baseline_extra_height = __find_baseline_extra_height(symbol_name)

    if baseline_extra_height is not None:
        _, default_h = SYMBOLS_DEFAULT_SIZES[symbol_name]
        height_perc = h / default_h

        return h - baseline_extra_height * height_perc
    elif symbol_name == '=':
        return h * 1.5
    elif symbol_name == '-':
        return h * 6
    else:
        return h


def get_baseline_center(symbol_name, box):
    # extract the top position
    _l, t, _r, _d = box
    # get the center in x coordinate (width)
    w, _ = box_center(box)

    # get the baseline height from the top
    baseline_h = get_baseline_height(symbol_name, box)
    # add the baseline offset to the top to get the new height
    new_h = t + baseline_h

    return w, new_h


def percentage_of_default_size(symbol_name, box):
    w, h = box_size(box)

    default_w, default_h = SYMBOLS_DEFAULT_SIZES[symbol_name]

    # special case: because the `-` symbol is small in height, it would mostly stay the same or change only by one pixel
    # and 1/3 is a large change percentage for one pixel, so we only use width of the character as it is more reliable
    if symbol_name == '-':
        return w / default_w
    else:
        return max(w / default_w, h / default_h)
