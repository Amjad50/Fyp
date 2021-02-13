import unittest

from PIL import Image

from .symbol_segmenter import segment_image


class SegmenterTestCase(unittest.TestCase):
    def test_multi_part_symbols(self):
        """
        This tests the segmentation of `=`, `:`, `i`, `j` characters with some extra characters as well
        """
        multi_part_symbols_img = Image.open('./testing_dataset/multi_part_symbols.png')
        image_segments = segment_image(multi_part_symbols_img)

        self.assertEqual(len(image_segments), 7)
        self.assertListEqual(image_segments,
                             [(190, 93, 224, 95), (193, 113, 220, 158), (196, 19, 218, 64), (93, 87, 138, 102),
                              (149, 82, 155, 111), (16, 66, 33, 112), (37, 66, 64, 125)])


if __name__ == '__main__':
    unittest.main()
