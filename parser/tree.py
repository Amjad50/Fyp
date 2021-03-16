from typing import List, Tuple

from PIL import Image

from classifier.classifier import SVMClassifier
from classifier.labeler import get_labeled_crops
from utils.types import LabeledCrops
from .connections import get_all_symbols_relations_connections, get_minimum_spanning_tree_symbol_connections
from .labeler import draw_connections
from .tree_node import SymbolTreeNode
from .utils import RELATIONS, optimize_latex_string


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

    @classmethod
    def from_image(cls, img: Image, svm_model: SVMClassifier) -> 'SymbolTree':
        labeled_crops = get_labeled_crops(img, svm_model)

        return cls.from_labeled_crops(labeled_crops)

    @classmethod
    def from_labeled_crops(cls, labeled_crops: LabeledCrops) -> 'SymbolTree':
        relations = get_all_symbols_relations_connections(labeled_crops)
        min_tree = get_minimum_spanning_tree_symbol_connections(labeled_crops)

        return cls(labeled_crops, relations, min_tree)

    def add_connection(self, from_node: int, to_node: int, relation: str) -> None:
        self.nodes[from_node].connect_with_relation(self.nodes[to_node], relation)

    def remove_connection(self, from_node: int, to_node: int, relation: str) -> None:
        self.nodes[from_node].remove_connection_with_relation(relation, to_node)

    def draw_min_connections(self, img: Image):
        all_connections = []

        crops = [
            node.crop
            for node in self.nodes
        ]

        for i, node in enumerate(self.nodes):
            for relation, connections in node.relations.items():
                if 'inverse' not in relation and connections:
                    for inner_node in connections:
                        all_connections.append((i, inner_node.position))

        return draw_connections(img, crops, all_connections)

    def optimize_connections(self):
        changed = True

        # loop until there is no more optimizations to do
        while changed:
            changed = False
            for node in self.nodes:
                # 1- optimize similar connections of the same relation and left optimize them
                for relation_str in ['up', 'down', 'power', 'sub']:
                    if SymbolTree.__optimize_multiple_connections_to_left(node, relation_str):
                        changed = True

        changed = True
        # loop until there is no more optimizations to do
        while changed:
            changed = False
            for node in self.nodes:
                # 1- optimize similar connections of the same relation and left optimize them
                for relation_str in ['up', 'down', 'power', 'sub']:
                    if SymbolTree.__optimize_first_parent_connection(node, relation_str):
                        changed = True

    def get_root_node(self) -> 'SymbolTreeNode':
        return self.__get_root_node(self.nodes)

    def get_latex_string(self, optimize: bool = False) -> str:
        # FIXME: producing latex on unoptimized connections might result in very bad results, so maybe call optimize
        #  here? but calling optimize would change the tree, and this method should be `pure` (does not change object
        #  structure)
        leftmost_node = self.get_root_node()

        latex_string = leftmost_node.generate_latex(optimize=False)

        # optimize at the end on one go is better than doing it for each node
        if optimize:
            return optimize_latex_string(latex_string)
        return latex_string

    # helper function
    @staticmethod
    def __find_relation(all_relations: List[List[Tuple[int, float, str]]], from_node: int, to_node: int) -> \
            Tuple[int, float, str]:
        inner_list = all_relations[from_node]
        try:
            return next((j, d, r) for j, d, r in inner_list if j == to_node)
        except StopIteration:
            raise ValueError(f"could not find relation from {from_node} to {to_node}")

    @staticmethod
    def __get_leftmost_node(nodes: List['SymbolTreeNode']) -> 'SymbolTreeNode':
        assert len(nodes) > 0, "cannot find leftmost of an empty list of nodes"

        left_most_node = nodes[0]
        min_left = left_most_node.crop[0]

        for node in nodes:
            if node.crop[0] < min_left:
                left_most_node = node
                min_left = node.crop[0]

        return left_most_node

    @staticmethod
    def __is_root(node: 'SymbolTreeNode') -> bool:
        for relation_str in RELATIONS:
            if node.relations[f'{relation_str}_inverse']:
                return False

        return True

    @staticmethod
    def __get_root_node(nodes: List['SymbolTreeNode']) -> 'SymbolTreeNode':
        assert len(nodes) > 0, "cannot find root node of an empty list of nodes"

        # the most probable scenario is that the leftmost node is the root, can't think of a case where the leftmost
        # is not the root, but nevertheless, we can try to find the root node manually if the leftmost is not it
        leftmost_node = SymbolTree.__get_leftmost_node(nodes)

        if SymbolTree.__is_root(leftmost_node):
            return leftmost_node

        for node in nodes:
            if SymbolTree.__is_root(node):
                return node

        raise Exception('Could not find root node')

    @staticmethod
    def __sort_by_left_most(nodes: List['SymbolTreeNode']) -> List['SymbolTreeNode']:
        return sorted(nodes, key=lambda node: node.crop[0])

    @staticmethod
    def __optimize_multiple_connections_to_left(node: SymbolTreeNode, relation_str: str) -> bool:
        """
        This function finds if there are multiple connections to a single relation, it will connect these connections
        using `left` and finally connect the single left-most node to the parent

        @param node: node to optimize
        @param relation_str: relation to optimize
        @return: True if a change is actually occurred, False otherwise
        """
        connections = node.relations[relation_str]
        if len(connections) <= 1:
            return False
        sorted_connections = SymbolTree.__sort_by_left_most(connections)

        for i in range(len(sorted_connections) - 1):
            node_from = sorted_connections[i]
            node_to = sorted_connections[i + 1]

            node_from.connect_with_relation(node_to, 'left')

        # it is important that we save a copy of the position, as when we remove a connection, it would also
        # modify the reference to `connections`
        positions = [n.position for n in connections]
        for pos in positions:
            node.remove_connection_with_relation(relation_str, pos)

        node.connect_with_relation(sorted_connections[0], relation_str)

        return True

    @staticmethod
    def __optimize_first_parent_connection(node: SymbolTreeNode, relation_str: str) -> bool:
        """
        This function will walk recursively of a connection of a node and reconnect itself will all parents one by one
        until it find the first parent, and will remove all other connections to the children.

        This is helpful as in `frac` sometimes, the middle element will be connected by `up`/`down` only, so this method
        will transfer the relation from this middle element to the first element

        @param node: node to optimize
        @param relation_str: relation to optimize
        @return: True if a change is actually occurred, False otherwise
        """
        connections = node.relations[relation_str]

        if len(connections) == 0:
            return False
        if len(connections) > 1:
            raise ValueError(f"connections of node {node.position} with relation '{relation_str}' must be one")

        connecting_node = connections[0]

        for inner_relation_str in ['power', 'sub', 'left']:
            if relation_str != inner_relation_str:
                inner_connections = connecting_node.relations[f'{inner_relation_str}_inverse']
                if inner_connections:
                    if len(inner_connections) > 1:
                        raise ValueError(
                            f"inner connections of node {node.position} with inner node {connecting_node.position} "
                            f"relation '{relation_str}' must be one")

                    node.remove_connection_with_relation(relation_str, connecting_node.position)
                    node.connect_with_relation(inner_connections[0], relation_str)

                    SymbolTree.__optimize_first_parent_connection(node, relation_str)
                    return True

        return False

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
                    relation_str = f"{relation}: ["
                    relation_inner_nodes = []
                    for inner_node in inner_nodes:
                        relation_inner_nodes.append(f"{node_str(inner_node)}")
                    relation_str += ", ".join(relation_inner_nodes)
                    relation_str += "]"
                    inner_nodes_list.append(relation_str)

            result += ', '.join(inner_nodes_list)
            result += "}\n"

        return result
