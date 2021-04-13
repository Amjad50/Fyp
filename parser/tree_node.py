from typing import List, Dict, Callable, Optional

from utils.types import Box
from .utils import RELATIONS, optimize_latex_string


class SymbolTreeNode:
    # these will be placed when a bracket should not be optimized
    # for example `\frac{w}{a}` should not be converted to `\fracwa`, but `\frac{w}a` is fine
    # so we try to place these where appropriate, then after all generation, they will be replaced by the correct
    # bracket type
    __NO_OPTIMIZE_OPEN_BRACKET = '\u1234'
    __NO_OPTIMIZE_CLOSE_BRACKET = '\u1235'
    __LABELS_LEFT_CANNOT_OPTIMIZE = ['\\sum', '\\int', '\\pi']

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

    def generate_latex(self, optimize: bool = True) -> str:
        result = self.__generate_latex(optimize=False)

        # optimize in one go
        if optimize:
            result = optimize_latex_string(result)

        result = result.replace(SymbolTreeNode.__NO_OPTIMIZE_OPEN_BRACKET, '{').replace(
            SymbolTreeNode.__NO_OPTIMIZE_CLOSE_BRACKET, '}')

        return result

    def __generate_latex(self, optimize: bool = False) -> str:
        result = self.label

        assert self.normalized(), "some relation/s have more than one node"

        if self.label == '\\frac':
            assert self.relations['up'] and self.relations['down'], "\\frac should have `up` and `down` relations"
            up_node = self.relations['up'][0]
            down_node = self.relations['down'][0]
            result += f"{SymbolTreeNode.__NO_OPTIMIZE_OPEN_BRACKET}{up_node.__generate_latex(optimize)}" \
                      f"{SymbolTreeNode.__NO_OPTIMIZE_CLOSE_BRACKET}{{{down_node.__generate_latex(optimize)}}}"

            for relation_str in ['power', 'sub']:
                assert not self.relations[relation_str], f"\\frac cannot have `{relation_str}` relation"
        elif self.label == '\\sum':
            if up_node := self.relations['up']:
                result += f"^{{{up_node[0].__generate_latex(optimize)}}}"
            if down_node := self.relations['down']:
                result += f"_{{{down_node[0].__generate_latex(optimize)}}}"
        elif self.label == '\\int':
            up_and_power = self.relations['up'] + self.relations['power']
            down_and_sub = self.relations['down'] + self.relations['sub']

            if up_and_power:
                assert len(up_and_power) == 1, "Integral cannot have two up connections"
                result += f"^{{{up_and_power[0].__generate_latex(optimize)}}}"
            if down_and_sub:
                assert len(down_and_sub) == 1, "Integral cannot have two down connections"
                result += f"_{{{down_and_sub[0].__generate_latex(optimize)}}}"
        else:
            if nodes := self.relations['sub']:
                result += f"_{{{nodes[0].__generate_latex(optimize)}}}"

            if nodes := self.relations['power']:
                result += f"^{{{nodes[0].__generate_latex(optimize)}}}"

            for relation_str in ['up', 'down']:
                assert not self.relations[relation_str], f"`{self.label}` cannot have `{relation_str}` relation"

        # in this case, we treat `none` as `left` because there is no other way
        # FIXME: maybe throw exception on `none`?
        for relation_str in ['left', 'none']:
            if self.label in SymbolTreeNode.__LABELS_LEFT_CANNOT_OPTIMIZE:
                prefix = SymbolTreeNode.__NO_OPTIMIZE_OPEN_BRACKET
                suffix = SymbolTreeNode.__NO_OPTIMIZE_CLOSE_BRACKET
            else:
                prefix = ""
                suffix = ""
            if nodes := self.relations[relation_str]:
                result += f'{prefix}{nodes[0].__generate_latex(optimize)}{suffix}'

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
