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

    def test_dot_on_frac(self):
        """
        This tests the segmentation of a dot character `.` on top of a `-` character which can happen
        when dealing with `1.5/x` for example.

        The reason for this test is because I thought this will fool the `i`,`j` simple identifier and would
        make it think that this is a valid `i` or `j` character, but it is identifying it correctly.
        """
        dot_on_frac_img = Image.open('./testing_dataset/dot_on_frac.png')
        image_segments = segment_image(dot_on_frac_img)

        self.assertEqual(len(image_segments), 11)
        self.assertListEqual(image_segments,
                             [(22, 93, 226, 95), (52, 19, 74, 64), (86, 58, 92, 64), (102, 19, 129, 64),
                              (137, 19, 165, 66), (144, 113, 166, 158), (171, 18, 201, 64), (179, 152, 185, 158),
                              (195, 113, 222, 160), (69, 134, 114, 149), (24, 113, 41, 159)])


if __name__ == '__main__':
    unittest.main()
