from segmenter.utils import box_size, box_center

# default sizes of symbols
SYMBOLS_DEFAULT_SIZES = {'0': (29, 48), '1': (23, 46), '2': (28, 46), '3': (29, 48), '4': (31, 47), '5': (28, 48),
                         '6': (29, 48), '7': (30, 49), '8': (29, 48), '9': (29, 48), 'a': (31, 32), 'b': (26, 49),
                         'c': (27, 32), 'd': (32, 49), 'e': (27, 32), 'f': (34, 63), 'g': (32, 45), 'h': (34, 49),
                         'i': (18, 47), 'j': (28, 60), 'k': (31, 49), 'l': (15, 49), 'm': (56, 32), 'n': (37, 32),
                         'o': (29, 32), 'p': (36, 44), 'q': (28, 44), 'r': (28, 32), 's': (25, 32), 't': (21, 44),
                         'u': (35, 32), 'v': (30, 32), 'w': (46, 32), 'x': (34, 32), 'y': (32, 45), 'z': (29, 32),
                         'A': (47, 49), 'B': (49, 47), 'C': (49, 51), 'D': (53, 47), 'E': (50, 47), 'F': (49, 47),
                         'G': (49, 51), 'H': (58, 47), 'I': (32, 47), 'J': (39, 49), 'K': (58, 47), 'L': (41, 47),
                         'M': (69, 47), 'N': (58, 47), 'O': (48, 51), 'P': (49, 47), 'Q': (48, 62), 'R': (49, 49),
                         'S': (40, 51), 'T': (47, 47), 'U': (47, 49), 'V': (49, 49), 'W': (68, 49), 'X': (57, 47),
                         'Y': (49, 47), 'Z': (46, 47), '=': (46, 16), '-': (42, 3), '+': (46, 46), '\\Sigma': (42, 47),
                         '\\pi': (37, 31)}

HAS_BELOW_BASELINE = 'fgjpqyQ'
BELOW_BASELINE_HEIGHT = 12


# returns the length from the top of the symbol to get to the baseline
def get_baseline_height(symbol_name, box):
    w, h = box_size(box)

    if symbol_name in HAS_BELOW_BASELINE:
        _, default_h = SYMBOLS_DEFAULT_SIZES[symbol_name]
        height_perc = h / default_h

        return h - BELOW_BASELINE_HEIGHT * height_perc
    elif symbol_name == '=':
        return h * 1.5
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

    return max(w / default_w, h / default_h)
