import unittest

from PIL import Image

from classifier.classifier import SVMClassifier
from .tree import SymbolTree


class ParserTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.model = SVMClassifier()
        self.model.import_from_pickle('./model/svm.pkl')

    def test_multiple_connections_to_frac_up_down(self):
        img = Image.open('./testing_dataset/frac_with_multiple_connections.png')

        tree = SymbolTree.from_image(img, self.model, optimize=False)

        self.assertEqual(self.tree_str(tree),
                         r"\frac -> {up: [x, +], down: [x, -]},"
                         r"x -> {down_inverse: [\frac]},"
                         r"x -> {up_inverse: [\frac]},"
                         r"+ -> {left: [y], up_inverse: [\frac]},"
                         r"- -> {left: [y], down_inverse: [\frac]},"
                         r"y -> {left_inverse: [-]},"
                         r"y -> {left_inverse: [+]},")

        tree.optimize_connections()

        self.assertEqual(self.tree_str(tree),
                         r"\frac -> {up: [x], down: [x]},"
                         r"x -> {left: [-], down_inverse: [\frac]},"
                         r"x -> {left: [+], up_inverse: [\frac]},"
                         r"+ -> {left: [y], left_inverse: [x]},"
                         r"- -> {left: [y], left_inverse: [x]},"
                         r"y -> {left_inverse: [-]},"
                         r"y -> {left_inverse: [+]},")

    def test_frac_connect_to_leftmost_child(self):
        img = Image.open('./testing_dataset/frac_should_connect_to_leftmost.png')

        tree = SymbolTree.from_image(img, self.model, optimize=False)

        self.assertEqual(self.tree_str(tree),
                         r"\frac -> {up: [2], down: [5]},"
                         r"4 -> {left: [5]},"
                         r"1 -> {left: [2]},"
                         r"5 -> {left: [6], left_inverse: [4], down_inverse: [\frac]},"
                         r"2 -> {left: [3], left_inverse: [1], up_inverse: [\frac]},"
                         r"6 -> {left_inverse: [5]},"
                         r"3 -> {left_inverse: [2]},")

        tree.optimize_connections()

        self.assertEqual(self.tree_str(tree),
                         r"\frac -> {up: [1], down: [4]},"
                         r"4 -> {left: [5], down_inverse: [\frac]},"
                         r"1 -> {left: [2], up_inverse: [\frac]},"
                         r"5 -> {left: [6], left_inverse: [4]},"
                         r"2 -> {left: [3], left_inverse: [1]},"
                         r"6 -> {left_inverse: [5]},"
                         r"3 -> {left_inverse: [2]},")

    @staticmethod
    def tree_str(tree):
        return str(tree).replace('\n', ',')


if __name__ == '__main__':
    unittest.main()
