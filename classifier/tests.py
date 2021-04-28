import unittest

from PIL import Image

from .classifier import SVMClassifier
from .labeler import get_labeled_crops


class ClassifierTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.model = SVMClassifier()
        self.model.import_from_pickle('./model/svm.pkl')

    def test_normal_subtract(self):
        """
        This test a normal fraction with no ambiguity
        """
        labeled_crops = self.label_img('./testing_dataset/normal_subtract.png')
        self.assertEqual(len(labeled_crops), 2)

        self.assertListEqual(labeled_crops,
                             [('-', (20, 77, 62, 80)), ('3', (71, 50, 100, 98))])

    def test_normal_frac(self):
        """
        This test a normal fraction with no ambiguity
        """
        labeled_crops = self.label_img('./testing_dataset/normal_fraction.png')
        self.assertEqual(len(labeled_crops), 3)

        self.assertListEqual(labeled_crops,
                             [('\\frac', (22, 93, 57, 96)), ('2', (25, 19, 53, 65)), ('1', (28, 113, 51, 159))])

    def test_wrong_frac_classification(self):
        """
        This tests, make sure that a subtract is not wrongly classified as \frac, and produce error
        because there is only an element below it but not above it
        """
        labeled_crops = self.label_img('./testing_dataset/only_down_no_frac.png')
        self.assertEqual(len(labeled_crops), 5)

        self.assertListEqual(labeled_crops,
                             [('\\int', (18, 35, 79, 188)), ('-', (57, 178, 90, 181)), ('-', (88, 38, 121, 41)),
                              ('3', (99, 159, 121, 193)), ('3', (129, 19, 151, 53))])

    def label_img(self, url):
        img = Image.open(url)

        labeled_crops = get_labeled_crops(img, self.model)

        return labeled_crops


if __name__ == '__main__':
    unittest.main()
