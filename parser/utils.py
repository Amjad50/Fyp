from typing import Optional

import numpy as np

from segmenter.utils import box_center
from symbols_utils.symbol_size import get_baseline_center, percentage_of_default_size
from utils.geometry import angle_between_points, distance_between_points
from utils.types import LabelCrop

RELATIONS = ["left", "power", "sub", "up", "down", "none"]


def get_most_probable_relation(label_crop1: LabelCrop, label_crop2: LabelCrop) -> Optional[str]:
    label1, box1 = label_crop1
    label2, box2 = label_crop2

    left1, top1, right1, down1 = box1
    left2, top2, right2, down2 = box2

    # the left should be first
    if left1 > left2:
        # TODO: is this the best way? using this to reduce connections
        return None

    center1 = box_center(box1)
    center2 = box_center(box2)

    baseline1 = get_baseline_center(*label_crop1)
    baseline2 = get_baseline_center(*label_crop2)

    perc1 = percentage_of_default_size(label1, box1)
    perc2 = percentage_of_default_size(label2, box2)

    perc_perc = perc2 / perc1

    angle = angle_between_points(baseline1, baseline2)

    if left1 <= left2 and right1 >= right2:
        if angle > 0:
            return 'up'
        else:
            return 'down'

    if perc_perc < 0.8:
        if -8 >= angle >= -30 and label1 != '-':
            return 'sub'
        elif 15 <= angle <= 60 and label1 != '-':
            return 'power'
    if abs(perc_perc - 1) > 0.15:
        # cannot have sub of smaller symbol to a larger symbol
        if -10 >= angle >= -30:
            return 'none'

    if label1 == '-' or label2 == '-':
        angle = angle_between_points(center1, center2)

    if -12 >= angle >= -30 and label1 != '-':
        return 'sub'
    elif 25 <= angle <= 60 and label1 != '-':
        return 'power'
    elif -10 <= angle <= 10:
        return 'left'
    elif 140 >= angle >= 60:
        return 'up'
    elif -60 >= angle >= -130:
        return 'down'

    return 'none'


def distance_labeled_crops(label_crop1: LabelCrop, label_crop2: LabelCrop) -> Optional[float]:
    label1, box1 = label_crop1
    label2, box2 = label_crop2

    # the left should be first
    if box1[0] > box2[0]:
        return None

    p1 = box_center(box1)
    p2 = box_center(box2)

    options = [distance_between_points(p1, p2)]

    if label1 == '-' and percentage_of_default_size(label1, box1) > 1:
        t, l, d, r = box1
        options.append(distance_between_points((t, l), p2))

    if label2 == '-' and percentage_of_default_size(label2, box2) > 1:
        t, l, d, r = box2
        options.append(distance_between_points(p1, (t, r)))

    return np.min(options)


def compute_modified_distance(distance: float, relation: str) -> float:
    additions = {
        'none': 1e6,
        'left': 0,
        'sub': 0,
        'power': 0,
        'up': 0,
        'down': 0,
    }

    assert relation in additions

    return distance + additions[relation]