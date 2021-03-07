from typing import List, Tuple, Dict

from PIL import Image

from segmenter.labeler import label_crops
from utils.types import LabeledCrops, Box
from .connections import get_all_symbols_relations_connections, get_minimum_spanning_tree_symbol_connections
from .utils import RELATIONS


class SymbolTreeNode:
    def __init__(self, label: str, crop: Box, position: int) -> None:
        self.position: int = position
        self.label: str = label
        self.crop: Box = crop
        self.relations: Dict[str, List['SymbolTreeNode']] = {relation_name: [] for relation_name in RELATIONS}
        # add inverse relations
        self.relations.update({f"{relation_name}_inverse": [] for relation_name in RELATIONS})

    def connect_with_relation(self, other: 'SymbolTreeNode', relation: str) -> None:
        assert relation in RELATIONS, f"relation type {relation} is unknown"

        self.relations[relation].append(other)
        other.__connect_with_relation_inverse(self, relation)

    def __connect_with_relation_inverse(self, other: 'SymbolTreeNode', relation: str) -> None:
        assert relation in RELATIONS, f"relation type {relation} is unknown"

        self.relations[f"{relation}_inverse"].append(other)


class SymbolTree:
    def __init__(self, labeled_crops: LabeledCrops, all_relations: List[List[Tuple[int, float, str]]],
                 min_tree: List[Tuple[int, int]]) -> None:
        self.nodes = [
            SymbolTreeNode(label, crop, i)
            for i, (label, crop) in enumerate(labeled_crops)
        ]

        for from_node, to_node in min_tree:
            _j, _distance, relation = SymbolTree.__find_relation(all_relations, from_node, to_node)

            self.nodes[from_node].connect_with_relation(self.nodes[to_node], relation)

    def __str__(self):
        result = ""

        # possible to change the node representation later
        def node_str(n: 'SymbolTreeNode') -> str:
            return n.label

        for node in self.nodes:
            result += node_str(node)
            result += " -> {"

            inner_nodes_list = []
            for relation, inner_nodes in node.relations.items():
                if inner_nodes:
                    for inner_node in inner_nodes:
                        inner_nodes_list.append(f"{relation}: {node_str(inner_node)}")

            result += ', '.join(inner_nodes_list)
            result += "}\n"

        return result

    @classmethod
    def from_image(cls, img: Image) -> 'SymbolTree':
        labeled_crops = label_crops(img)

        return cls.from_labeled_crops(labeled_crops)

    @classmethod
    def from_labeled_crops(cls, labeled_crops: LabeledCrops) -> 'SymbolTree':
        relations = get_all_symbols_relations_connections(labeled_crops)
        min_tree = get_minimum_spanning_tree_symbol_connections(labeled_crops)

        return cls(labeled_crops, relations, min_tree)

    # helper function
    @staticmethod
    def __find_relation(all_relations: List[List[Tuple[int, float, str]]], from_node: int, to_node: int) -> \
            Tuple[int, float, str]:
        inner_list = all_relations[from_node]
        try:
            return next((j, d, r) for j, d, r in inner_list if j == to_node)
        except StopIteration:
            raise ValueError(f"could not find relation from {from_node} to {to_node}")
