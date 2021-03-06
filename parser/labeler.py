from typing import Tuple, List

from PIL import Image, ImageDraw

from classifier.classifier import SVMClassifier
from classifier.labeler import get_labeled_crops, draw_labeled_crops
from parser.connections import get_minimum_spanning_tree_symbol_connections
from segmenter.labeler import label_crops
from segmenter.utils import box_center
from utils.types import Box


def draw_connections(img: Image, crops: List[Box], connections: List[Tuple[int, int]]) -> Image:
    labeld_img = img.copy()
    img_d = ImageDraw.Draw(labeld_img)

    for (i, j) in connections:
        crop1 = crops[i]
        crop2 = crops[j]

        c1 = box_center(crop1)
        c2 = box_center(crop2)

        img_d.line([c1, c2], fill=(255, 100, 100))

    return labeld_img


def label_minimum_spanning_tree_symbols_connections(img: Image, svm_model: SVMClassifier) -> Image:
    labeled_crops = get_labeled_crops(img, svm_model)
    labels, crops = list(zip(*labeled_crops))

    labeld_crops_img = label_crops(img, crops)

    labeled_img = draw_labeled_crops(labeld_crops_img, labeled_crops)

    labeled_img_connections_minimum = draw_connections(labeled_img, crops,
                                                       get_minimum_spanning_tree_symbol_connections(labeled_crops))

    return labeled_img_connections_minimum
