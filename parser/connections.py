from typing import List, Tuple

from parser.graph import find_minimum_spanning_tree
from parser.utils import compute_modified_distance, get_most_probable_relation, distance_labeled_crops
from segmenter.utils import is_another_in_between
from utils.types import LabeledCrops


def get_all_symbols_connections(labeled_crops: LabeledCrops) -> List[List[Tuple[int, float]]]:
    labels, crops = list(zip(*labeled_crops))

    relations = [[] for _ in range(len(labeled_crops))]
    connections = [[] for _ in range(len(labeled_crops))]

    for b1_i, b1 in enumerate(labeled_crops):
        for b2_i, b2 in enumerate(labeled_crops):
            crop1 = b1[1]
            crop2 = b2[1]
            if crop1 == crop2:
                continue

            if is_another_in_between(crop1, crop2, crops):
                continue

            relation = get_most_probable_relation(b1, b2)

            if relation is None:
                continue

            relations[b1_i].append((b2_i, relation))

    subs_and_powers = [[] for _ in range(len(labeled_crops))]

    for i, symbol_relations in enumerate(relations):
        for j, relation in symbol_relations:
            if relation == 'sub' or relation == 'power':
                subs_and_powers[i].append(j)

    for b1_i, b1 in enumerate(labeled_crops):
        crops_filtered = []

        for crop_i, crop in enumerate(crops):
            if crop_i not in subs_and_powers[b1_i]:
                crops_filtered.append(crop)

        for b2_i, b2 in enumerate(labeled_crops):
            crop1 = b1[1]
            crop2 = b2[1]
            if crop1 == crop2:
                continue

            if is_another_in_between(crop1, crop2, crops_filtered):
                continue

            relation = get_most_probable_relation(b1, b2)

            if relation is None:
                continue

            d = distance_labeled_crops(b1, b2)
            # as `distance_labeled_crops` returns `Optional`, but if `relation` is not `None`, then this must be also
            # not `None`
            assert d is not None
            connections[b1_i].append((b2_i, compute_modified_distance(d, relation)))

    return connections


def get_minimum_spanning_tree_symbol_connections(labeled_crops: LabeledCrops) -> List[Tuple[int, int]]:
    connections = get_all_symbols_connections(labeled_crops)
    return sorted(find_minimum_spanning_tree(connections))
