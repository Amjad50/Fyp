from typing import List, Dict, Callable, Optional

from utils.types import Box
from .utils import RELATIONS, optimize_latex_string


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

        relations_list = self.relations[relation]

        already_exist_index = SymbolTreeNode.__find_node_with_condition(relations_list,
                                                                        lambda node: node.position == other.position)
        assert already_exist_index is None, \
            f"connection from {self.position} to {other.position} with relation '{relation}' already exists"

        relations_list.append(other)
        other.__connect_with_relation_inverse(self, relation)

    def __connect_with_relation_inverse(self, other: 'SymbolTreeNode', relation: str) -> None:
        assert relation in RELATIONS, f"relation type {relation} is unknown"

        relations_list = self.relations[f"{relation}_inverse"]

        already_exist_index = SymbolTreeNode.__find_node_with_condition(relations_list,
                                                                        lambda node: node.position == other.position)
        assert already_exist_index is None, \
            f"connection from {self.position} to {other.position} with relation '{relation}_inverse' already exists"

        relations_list.append(other)

    def remove_connection_with_relation(self, relation: str, position: int) -> None:
        assert relation in RELATIONS, f"relation type {relation} is unknown"

        relations_list = self.relations[relation]
        index = SymbolTreeNode.__find_node_with_condition(relations_list,
                                                          lambda node: node.position == position)

        if index is not None:
            other = relations_list.pop(index)

            other.__remove_connection_with_relation_inverse(relation, self.position)
        else:
            raise ValueError(f"node with position {position} could not be found in relation {relation}")

    def __remove_connection_with_relation_inverse(self, relation: str, position: int) -> None:
        assert relation in RELATIONS, f"relation type {relation} is unknown"

        relations_list = self.relations[f"{relation}_inverse"]
        index = SymbolTreeNode.__find_node_with_condition(relations_list,
                                                          lambda node: node.position == position)

        if index is not None:
            relations_list.pop(index)
        else:
            raise ValueError(f"node with position {position} could not be found in relation {relation}_inverse")

    def normalized(self) -> bool:
        for relation_str in RELATIONS:
            if len(self.relations[relation_str]) > 1:
                return False

        return True

    def generate_latex(self, optimize: bool = False) -> str:
        result = self.label

        assert self.normalized(), "some relation/s have more than one node"

        if self.label == '\\frac':
            assert self.relations['up'] and self.relations['down'], "\\frac should have `up` and `down` relations"
            up_node = self.relations['up'][0]
            down_node = self.relations['down'][0]
            result += f"{{{up_node.generate_latex(optimize)}}}{{{down_node.generate_latex(optimize)}}}"

            for relation_str in ['power', 'sub']:
                assert not self.relations[relation_str], f"\\frac cannot have `{relation_str}` relation"
        else:
            if nodes := self.relations['sub']:
                result += f"_{{{nodes[0].generate_latex(optimize)}}}"

            if nodes := self.relations['power']:
                result += f"^{{{nodes[0].generate_latex(optimize)}}}"

            for relation_str in ['up', 'down']:
                assert not self.relations[relation_str], f"`{self.label}` cannot have `{relation_str}` relation"

        # in this case, we treat `none` as `left` because there is no other way
        # FIXME: maybe throw exception on `none`?
        for relation_str in ['left', 'none']:
            if nodes := self.relations[relation_str]:
                result += nodes[0].generate_latex(optimize)

        if optimize:
            return optimize_latex_string(result)
        return result

    @staticmethod
    def __find_node_with_condition(nodes: List['SymbolTreeNode'], condition: Callable[['SymbolTreeNode'], bool]) -> \
            Optional[int]:
        for i, node in enumerate(nodes):
            if condition(node):
                return i

        return None
